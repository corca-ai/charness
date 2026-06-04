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
from dataclasses import asdict, dataclass
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
TERM_GRACE_SECONDS = 2.0
CLEANUP_COMMAND = "python3 scripts/agent_browser_runtime_guard.py --repo-root . --cleanup-orphans --execute"


@dataclass(frozen=True)
class ProcessInfo:
    pid: int
    ppid: int
    rss_kib: int
    command: str


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


def list_processes(repo_root: Path) -> list[ProcessInfo]:
    completed = run_process(["ps", "-eo", "pid=,ppid=,rss=,command="], cwd=repo_root, timeout_seconds=PS_TIMEOUT_SECONDS)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "ps failed"
        raise RuntimeError(detail)
    return parse_ps_output(completed.stdout)


def is_agent_browser_daemon(process: ProcessInfo) -> bool:
    return "agent-browser" in process.command and "daemon.js" in process.command


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


def inspect_runtime(processes: list[ProcessInfo]) -> dict[str, object]:
    daemons = [process for process in processes if is_agent_browser_daemon(process)]
    orphan_daemons = [process for process in daemons if process.ppid == 1]
    orphan_root_pids = {process.pid for process in orphan_daemons}
    orphan_tree_pids = collect_descendant_pids(processes, orphan_root_pids) if orphan_root_pids else set()
    orphan_descendants = [
        process for process in processes if process.pid in orphan_tree_pids and process.pid not in orphan_root_pids
    ]
    return {
        "daemon_count": len(daemons),
        "orphan_daemon_count": len(orphan_daemons),
        "orphan_descendant_count": len(orphan_descendants),
        "daemon_pids": [process.pid for process in daemons],
        "orphan_daemon_pids": sorted(orphan_root_pids),
        "orphan_tree_pids": sorted(orphan_tree_pids),
        "sample_orphan_daemons": [asdict(process) for process in orphan_daemons[:5]],
        "sample_orphan_descendants": [asdict(process) for process in orphan_descendants[:10]],
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


def cleanup_orphans(repo_root: Path, *, execute: bool) -> dict[str, object]:
    processes = list_processes(repo_root)
    runtime = inspect_runtime(processes)
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
    time.sleep(TERM_GRACE_SECONDS)
    remaining_processes = list_processes(repo_root)
    remaining = sorted(process.pid for process in remaining_processes if process.pid in set(target_pids))
    forced = kill_pids(remaining, signal.SIGKILL)
    final_processes = list_processes(repo_root)
    final_runtime = inspect_runtime(final_processes)
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
    return {"runtime": inspect_runtime(processes)}


def assert_no_orphans_payload(repo_root: Path) -> dict[str, object]:
    runtime = inspect_runtime(list_processes(repo_root))
    ignore_orphans = os.environ.get("CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS") == "1"
    healthy = ignore_orphans or runtime["orphan_daemon_count"] == 0
    return {
        "healthy": healthy,
        "runtime": runtime,
        "ignored_orphans": ignore_orphans,
        "next_step": None if healthy else CLEANUP_COMMAND,
    }


def doctor_payload(repo_root: Path) -> dict[str, object]:
    helpcheck = run_help_check(repo_root)
    runtime = inspect_runtime(list_processes(repo_root))
    ignore_orphans = os.environ.get("CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS") == "1"
    healthy = helpcheck["ok"] and (ignore_orphans or runtime["orphan_daemon_count"] == 0)
    return {
        "healthy": healthy,
        "helpcheck": helpcheck,
        "runtime": runtime,
        "ignored_orphans": ignore_orphans,
        "next_step": None if healthy else CLEANUP_COMMAND,
    }


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
        next_step = payload.get("next_step")
        if isinstance(next_step, str):
            print(f"Run `{next_step}` to remove orphan agent-browser daemon trees.", file=sys.stderr)
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
        next_step = payload.get("next_step")
        if isinstance(next_step, str):
            print(f"Run `{next_step}` to remove orphan agent-browser daemon trees.", file=sys.stderr)
        return 1

    print_payload(inspect_payload(repo_root), as_json=args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
