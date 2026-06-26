#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import runpy
import signal
import sys
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_subprocess_guard = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process
HELP_TIMEOUT_SECONDS = 10
PS_TIMEOUT_SECONDS = 10
DEFAULT_TERM_GRACE_SECONDS = 2.0
CLEANUP_COMMAND = "python3 scripts/agent_browser_runtime_guard.py --repo-root . --cleanup-orphans --execute"
# Guidance for residue the cleanup command cannot fix: reparented (PPID=1, owning
# daemon already gone) or zombie (<defunct>) browser processes are not part of any
# orphan-daemon tree, so `--cleanup-orphans` targets nothing and the operator who
# keeps running it is stuck in a no-exit loop (#309). Reaping these is the
# container init's job.
INIT_REAP_GUIDANCE = (
    "Only reparented (PPID=1) or zombie (<defunct>) agent-browser residue remains; "
    "`--cleanup-orphans` targets orphan daemon trees and cannot reap it. The container "
    "init must reap these PIDs — restart the container (or wait for init to reap them) "
    "to clear the runtime."
)
# Markers that identify an agent-browser session's process tree (the agent-browser
# daemon and the headless Chromium it drives). Used to detect reparented (PPID=1)
# and zombie (<defunct>) browser residue that survives a daemon's death — residue
# the daemon-rooted orphan scan alone misses and would otherwise report clean (#302).
# `daemon.js` is intentionally NOT a marker: reparented agent-browser daemons carry
# `agent-browser` in their command and are already counted by the orphan-daemon scan,
# and bare `daemon.js` collides with unrelated commands (e.g. dockerd's `daemon.json`).
AGENT_BROWSER_RESIDUE_MARKERS = ("agent-browser", "headless_shell")
# Bare Chrome/Chromium is only agent-browser residue when it is clearly a
# headless/automation process; otherwise a developer's desktop Chrome reparented
# to init would be misclassified as gather residue and fail the runtime gate.
CHROMIUM_MARKERS = ("chromium", "chrome")
HEADLESS_INDICATORS = ("--headless", "headless_shell")
DEFUNCT_MARKERS = ("<defunct>", "(defunct)")


@dataclass(frozen=True)
class ProcessInfo:
    pid: int
    ppid: int
    rss_kib: int
    command: str
    # Working directory of the process (the daemon's launching checkout), read
    # from /proc by list_processes. None when unreadable (non-Linux, permission
    # denied, a process that released its cwd) -> fail-closed ownership (#365).
    cwd: str | None = None


def parse_ps_output(text: str) -> list[ProcessInfo]:
    processes: list[ProcessInfo] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = raw_line.split(None, 3)
        if len(parts) != 4:
            continue
        pid_text, ppid_text, rss_text, command = parts
        if not (pid_text.isdigit() and ppid_text.isdigit() and rss_text.isdigit()):
            continue
        processes.append(ProcessInfo(pid=int(pid_text), ppid=int(ppid_text), rss_kib=int(rss_text), command=command))
    return processes


def read_process_cwd(pid: int) -> str | None:
    """The process working directory via ``/proc`` (Linux). ``None`` when it cannot
    be read — non-Linux, permission denied (another user's process), or a process
    that released its cwd (e.g. a ``<defunct>`` zombie). An unreadable cwd is the
    fail-closed input to ``is_checkout_owned`` (#365): the guard never kills or
    flags a process it cannot prove belongs to this checkout."""
    try:
        return os.readlink(f"/proc/{pid}/cwd")
    except OSError:
        return None


def list_processes(repo_root: Path) -> list[ProcessInfo]:
    completed = run_process(["ps", "-eo", "pid=,ppid=,rss=,command="], cwd=repo_root, timeout_seconds=PS_TIMEOUT_SECONDS)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "ps failed"
        raise RuntimeError(detail)
    return [replace(process, cwd=read_process_cwd(process.pid)) for process in parse_ps_output(completed.stdout)]


def is_agent_browser_daemon(process: ProcessInfo) -> bool:
    return "agent-browser" in process.command and "daemon.js" in process.command


def is_checkout_owned(process: ProcessInfo, repo_root: Path) -> bool:
    """Whether ``process`` belongs to this checkout, by its working directory.

    Fail-closed (#365): returns True only when the process cwd resolves inside
    ``repo_root`` (already resolved by the caller). An unknown cwd — unreadable
    ``/proc``, non-Linux, or a zombie that released its cwd — is treated as NOT
    owned, so the guard can never kill or flag a neighbor checkout's live daemon.
    cwd is an ownership heuristic, not cryptographic proof; ``resolve()`` collapses
    symlinks so a symlinked checkout path still matches."""
    if not process.cwd:
        return False
    try:
        cwd = Path(process.cwd).resolve()
    except (OSError, RuntimeError, ValueError):
        return False
    return cwd == repo_root or repo_root in cwd.parents


def is_browser_residue_command(command: str) -> bool:
    lowered = command.lower()
    if any(marker in lowered for marker in AGENT_BROWSER_RESIDUE_MARKERS):
        return True
    if any(marker in lowered for marker in CHROMIUM_MARKERS):
        return any(indicator in lowered for indicator in HEADLESS_INDICATORS)
    return False


def is_defunct_command(command: str) -> bool:
    lowered = command.lower()
    return any(marker in lowered for marker in DEFUNCT_MARKERS)


def collect_descendant_pids(processes: list[ProcessInfo], root_pids: set[int]) -> set[int]:
    children_by_parent: dict[int, list[int]] = defaultdict(list)
    for process in processes:
        children_by_parent[process.ppid].append(process.pid)
    queue = deque(root_pids)
    descendants = set(root_pids)
    while queue:
        current = queue.popleft()
        for child in children_by_parent.get(current, []):
            if child in descendants:
                continue
            descendants.add(child)
            queue.append(child)
    return descendants


def inspect_runtime(processes: list[ProcessInfo], repo_root: Path) -> dict[str, object]:
    # #365: scope every daemon/residue classification to THIS checkout, by the
    # process cwd resolved under repo_root. agent-browser daemons are detached by
    # design (PPID=1 from birth), so a machine-wide PPID-only scan matched — and
    # --cleanup-orphans killed — a concurrent neighbor checkout's LIVE daemon.
    # Ownership-scoping (fail-closed) keeps the cleanup useful for this checkout's
    # own orphans while leaving a neighbor's daemon untouched. The descendant walk
    # stays over ALL processes: a child of an owned orphan daemon belongs to the
    # owned tree even if the child's own cwd differs.
    repo_root = Path(repo_root).resolve()
    daemons = [
        process for process in processes
        if is_agent_browser_daemon(process) and is_checkout_owned(process, repo_root)
    ]
    orphan_daemons = [process for process in daemons if process.ppid == 1]
    orphan_root_pids = {process.pid for process in orphan_daemons}
    orphan_tree_pids = collect_descendant_pids(processes, orphan_root_pids) if orphan_root_pids else set()
    orphan_descendants = [
        process for process in processes if process.pid in orphan_tree_pids and process.pid not in orphan_root_pids
    ]
    # Reparented browser residue: PPID=1 browser processes whose owning daemon is
    # already gone, so they are not part of any orphan-daemon tree. Zombie residue:
    # <defunct> browser processes the host init has not reaped. Neither is reaped
    # here (that is the container init's job), but both must keep the runtime from
    # being reported clean (#302). Both are ownership-scoped (#365): a neighbor's
    # residue is not this checkout's concern. A zombie has usually released its cwd,
    # so an unattributable zombie is conservatively not flagged (fail-closed) —
    # acceptable because the guard never reaps residue, only reports it.
    reparented_residue = [
        process
        for process in processes
        if process.ppid == 1
        and process.pid not in orphan_root_pids
        and is_browser_residue_command(process.command)
        and not is_defunct_command(process.command)
        and is_checkout_owned(process, repo_root)
    ]
    zombie_residue = [
        process for process in processes
        if is_defunct_command(process.command)
        and is_browser_residue_command(process.command)
        and is_checkout_owned(process, repo_root)
    ]
    return {
        "daemon_count": len(daemons),
        "orphan_daemon_count": len(orphan_daemons),
        "orphan_descendant_count": len(orphan_descendants),
        "daemon_pids": [process.pid for process in daemons],
        "orphan_daemon_pids": sorted(orphan_root_pids),
        "orphan_tree_pids": sorted(orphan_tree_pids),
        "reparented_residue_count": len(reparented_residue),
        "reparented_residue_pids": sorted(process.pid for process in reparented_residue),
        "zombie_residue_count": len(zombie_residue),
        "zombie_residue_pids": sorted(process.pid for process in zombie_residue),
        "sample_orphan_daemons": [asdict(process) for process in orphan_daemons[:5]],
        "sample_orphan_descendants": [asdict(process) for process in orphan_descendants[:10]],
        "sample_reparented_residue": [asdict(process) for process in reparented_residue[:5]],
        "sample_zombie_residue": [asdict(process) for process in zombie_residue[:5]],
    }


def run_help_check(repo_root: Path) -> dict[str, object]:
    # `agent-browser --help` warms a background daemon as a side effect, which
    # leaks PPID=1 orphans across runs. `--version` verifies the binary works
    # without spawning a daemon, which is what the doctor healthcheck needs.
    completed = run_process(["agent-browser", "--version"], cwd=repo_root, timeout_seconds=HELP_TIMEOUT_SECONDS)
    ok = completed.returncode == 0 and "agent-browser" in completed.stdout
    return {
        "ok": ok,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def kill_pids(pids: list[int], sig: int) -> list[int]:
    sent: list[int] = []
    for pid in pids:
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            continue
        sent.append(pid)
    return sent


def term_grace_seconds() -> float:
    raw = os.environ.get("CHARNESS_AGENT_BROWSER_TERM_GRACE_SECONDS")
    if raw is None:
        return DEFAULT_TERM_GRACE_SECONDS
    try:
        return max(0.0, float(raw))
    except ValueError:
        return DEFAULT_TERM_GRACE_SECONDS


def cleanup_orphans(repo_root: Path, *, execute: bool) -> dict[str, object]:
    processes = list_processes(repo_root)
    runtime = inspect_runtime(processes, repo_root)
    target_pids = list(runtime["orphan_tree_pids"])
    if not execute:
        return {
            "preview_only": True,
            "target_pids": target_pids,
            "terminated_pids": [],
            "forced_pids": [],
            "remaining_pids": target_pids,
        }

    terminated = kill_pids(target_pids, signal.SIGTERM)
    if target_pids:
        time.sleep(term_grace_seconds())
    remaining_processes = list_processes(repo_root)
    remaining = sorted(process.pid for process in remaining_processes if process.pid in set(target_pids))
    forced = kill_pids(remaining, signal.SIGKILL)
    final_processes = list_processes(repo_root)
    final_runtime = inspect_runtime(final_processes, repo_root)
    return {
        "preview_only": False,
        "target_pids": target_pids,
        "terminated_pids": terminated,
        "forced_pids": forced,
        "remaining_pids": list(final_runtime["orphan_tree_pids"]),
        "runtime": final_runtime,
    }


def inspect_payload(repo_root: Path) -> dict[str, object]:
    processes = list_processes(repo_root)
    return {"runtime": inspect_runtime(processes, repo_root)}


def runtime_residue_total(runtime: dict[str, object]) -> int:
    return (
        int(runtime["orphan_daemon_count"])
        + int(runtime["reparented_residue_count"])
        + int(runtime["zombie_residue_count"])
    )


def runtime_next_step(runtime: dict[str, object]) -> tuple[str | None, str | None]:
    """Return ``(next_step, next_step_kind)`` for a runtime, or ``(None, None)``
    when there is no residue.

    A reap-able orphan daemon tree (``orphan_tree_pids``) is exactly what
    ``--cleanup-orphans --execute`` targets, so recommend it (kind
    ``cleanup_command``). When the only residue is reparented or zombie
    processes — no orphan daemon tree to reap — the cleanup command clears
    nothing (#309); return init-reap guidance (kind ``init_reap``) so the
    operator is not stuck running a no-op command in a loop.
    """
    if runtime_residue_total(runtime) == 0:
        return None, None
    if runtime["orphan_tree_pids"]:
        return CLEANUP_COMMAND, "cleanup_command"
    return INIT_REAP_GUIDANCE, "init_reap"


def assert_no_orphans_payload(repo_root: Path) -> dict[str, object]:
    runtime = inspect_runtime(list_processes(repo_root), repo_root)
    ignore_orphans = os.environ.get("CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS") == "1"
    healthy = ignore_orphans or runtime_residue_total(runtime) == 0
    next_step, next_step_kind = (None, None) if healthy else runtime_next_step(runtime)
    return {
        "healthy": healthy,
        "runtime": runtime,
        "ignored_orphans": ignore_orphans,
        "next_step": next_step,
        "next_step_kind": next_step_kind,
    }


def doctor_payload(repo_root: Path) -> dict[str, object]:
    helpcheck = run_help_check(repo_root)
    runtime = inspect_runtime(list_processes(repo_root), repo_root)
    ignore_orphans = os.environ.get("CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS") == "1"
    healthy = helpcheck["ok"] and (ignore_orphans or runtime_residue_total(runtime) == 0)
    next_step, next_step_kind = (None, None) if healthy else runtime_next_step(runtime)
    return {
        "healthy": healthy,
        "helpcheck": helpcheck,
        "runtime": runtime,
        "ignored_orphans": ignore_orphans,
        "next_step": next_step,
        "next_step_kind": next_step_kind,
    }


def print_next_step_guidance(payload: dict[str, object]) -> None:
    next_step = payload.get("next_step")
    if not isinstance(next_step, str):
        return
    if payload.get("next_step_kind") == "init_reap":
        # Prose guidance, not a runnable command — print it verbatim so the
        # operator is not told to "Run" reparented/zombie-residue advice (#309).
        print(next_step, file=sys.stderr)
    else:
        print(f"Run `{next_step}` to remove orphan agent-browser daemon trees.", file=sys.stderr)


def print_payload(payload: dict[str, object], *, as_json: bool) -> None:
    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        return
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--doctor-check", action="store_true")
    parser.add_argument("--cleanup-orphans", action="store_true")
    parser.add_argument("--assert-no-orphans", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()

    if args.cleanup_orphans:
        payload = cleanup_orphans(repo_root, execute=args.execute)
        print_payload(payload, as_json=args.json)
        return 0 if not payload["remaining_pids"] else 1

    if args.doctor_check:
        payload = doctor_payload(repo_root)
        if payload["healthy"]:
            if payload.get("ignored_orphans") and payload["runtime"]["orphan_daemon_count"]:
                print("agent-browser runtime healthy; orphan check waived by CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS=1")
            else:
                print("agent-browser runtime healthy")
            return 0
        print_payload(payload, as_json=args.json)
        print_next_step_guidance(payload)
        return 1

    if args.assert_no_orphans:
        payload = assert_no_orphans_payload(repo_root)
        if payload["healthy"]:
            if payload.get("ignored_orphans") and payload["runtime"]["orphan_daemon_count"]:
                print("agent-browser runtime orphan check waived by CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS=1")
            else:
                print("agent-browser runtime has no orphan daemon trees")
            return 0
        print_payload(payload, as_json=args.json)
        print_next_step_guidance(payload)
        return 1

    print_payload(inspect_payload(repo_root), as_json=args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
