from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_GUARD_PATH = ROOT / "scripts" / "agent_browser_runtime_guard.py"

# Ownership scoping (#365) keys on the process working directory. The pure
# inspect_runtime tests pass simulated cwd values so no real process is needed;
# OWNED resolves under REPO_ROOT, FOREIGN is a neighbor checkout.
REPO_ROOT = Path("/repo/checkout")
OWNED = "/repo/checkout"
OWNED_SUBDIR = "/repo/checkout/sub"
FOREIGN = "/other/neighbor"


def load_runtime_guard_module():
    spec = importlib.util.spec_from_file_location("agent_browser_runtime_guard", RUNTIME_GUARD_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_fake_agent_browser(bin_dir: Path) -> None:
    script = bin_dir / "agent-browser"
    script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ \"${1:-}\" == \"--version\" ]]; then',
                '  echo \"agent-browser 0.25.3\"',
                'elif [[ \"${1:-}\" == \"--help\" ]]; then',
                '  echo \"agent-browser\"',
                "else",
                "  exit 1",
                "fi",
                "",
            ]
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)


def make_fake_ps(bin_dir: Path, *, output: str) -> None:
    script = bin_dir / "ps"
    script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                "cat <<'EOF'",
                output.rstrip("\n"),
                "EOF",
                "",
            ]
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)


def make_fake_ps_sequence(bin_dir: Path, *, outputs: list[str]) -> None:
    state = bin_dir / "ps-count"
    cases = "\n".join(f"{index}) cat <<'EOF'\n{output.rstrip()}\nEOF\n;;" for index, output in enumerate(outputs, start=1))
    script = bin_dir / "ps"
    script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                f"state={str(state)!r}",
                'count="$(cat "$state" 2>/dev/null || echo 0)"',
                'count="$((count + 1))"',
                'printf "%s" "$count" > "$state"',
                "case \"$count\" in",
                cases,
                "*) cat <<'EOF'",
                outputs[-1].rstrip(),
                "EOF",
                ";;",
                "esac",
                "",
            ]
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)


class MarkerProcesses:
    """Spawn real, harmless long-lived processes so the guard can read a real
    ``/proc/<pid>/cwd`` for ownership scoping (#365). The fake ``ps`` labels these
    PIDs with daemon/chrome command strings; the guard's own ``--cleanup-orphans
    --execute`` may signal an OWNED marker (that is the point), so every marker is
    reaped in teardown. Never targets a real machine daemon."""

    def __init__(self) -> None:
        self._procs: list[subprocess.Popen] = []

    def spawn(self, cwd: Path) -> int:
        proc = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(120)"],
            cwd=str(cwd),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._procs.append(proc)
        return proc.pid

    def alive(self, pid: int) -> bool:
        for proc in self._procs:
            if proc.pid == pid:
                return proc.poll() is None
        raise AssertionError(f"unknown marker pid {pid}")

    def close(self) -> None:
        for proc in self._procs:
            proc.kill()
            proc.wait()


def _run_guard(args: list[str], bin_dir: Path, repo_root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
    env.setdefault("CHARNESS_AGENT_BROWSER_TERM_GRACE_SECONDS", "0.01")
    env.pop("CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS", None)
    return subprocess.run(
        [sys.executable, str(RUNTIME_GUARD_PATH), "--repo-root", str(repo_root), *args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


# --- pure inspect_runtime ownership logic (#365): simulated cwd, no real kills ---


def test_inspect_runtime_tracks_orphan_daemon_tree() -> None:
    guard = load_runtime_guard_module()
    processes = [
        guard.ProcessInfo(pid=100, ppid=1, rss_kib=10, command="node /tmp/agent-browser/dist/daemon.js", cwd=OWNED),
        # a descendant's own cwd is irrelevant; it belongs to the owned orphan tree.
        guard.ProcessInfo(pid=101, ppid=100, rss_kib=20, command="chrome-headless --type=renderer", cwd=FOREIGN),
        # owned daemon but not an orphan (ppid != 1).
        guard.ProcessInfo(pid=200, ppid=999, rss_kib=10, command="node /tmp/agent-browser/dist/daemon.js", cwd=OWNED),
    ]

    payload = guard.inspect_runtime(processes, REPO_ROOT)

    assert payload["daemon_count"] == 2
    assert payload["orphan_daemon_count"] == 1
    assert payload["orphan_descendant_count"] == 1
    assert payload["orphan_tree_pids"] == [100, 101]


def test_inspect_runtime_excludes_foreign_and_unknown_cwd_daemons() -> None:
    # #365 core: a neighbor checkout's live daemon (cwd outside repo_root) and a
    # daemon whose cwd is unreadable (fail-closed) are never flagged or targeted;
    # only the this-checkout orphan is.
    guard = load_runtime_guard_module()
    processes = [
        guard.ProcessInfo(pid=100, ppid=1, rss_kib=10, command="node /tmp/agent-browser/dist/daemon.js", cwd=OWNED),
        guard.ProcessInfo(pid=300, ppid=1, rss_kib=10, command="node /tmp/agent-browser/dist/daemon.js", cwd=FOREIGN),
        guard.ProcessInfo(pid=400, ppid=1, rss_kib=10, command="node /tmp/agent-browser/dist/daemon.js", cwd=None),
    ]

    payload = guard.inspect_runtime(processes, REPO_ROOT)

    assert payload["daemon_count"] == 1
    assert payload["orphan_daemon_pids"] == [100]
    assert payload["orphan_tree_pids"] == [100]
    # neighbor daemon and unknown-cwd daemon are spared.
    assert 300 not in payload["orphan_tree_pids"]
    assert 400 not in payload["orphan_tree_pids"]


def test_inspect_runtime_owns_daemon_in_repo_subdirectory() -> None:
    # A daemon launched from a subdirectory of the checkout is still this-checkout.
    guard = load_runtime_guard_module()
    processes = [
        guard.ProcessInfo(pid=100, ppid=1, rss_kib=10, command="node /tmp/agent-browser/dist/daemon.js", cwd=OWNED_SUBDIR),
    ]

    payload = guard.inspect_runtime(processes, REPO_ROOT)

    assert payload["orphan_tree_pids"] == [100]


def test_inspect_runtime_flags_reparented_chromium_residue() -> None:
    # #302: the owning agent-browser daemon already died, but its Chromium got
    # reparented to PID 1. #365: only when the residue is owned by this checkout.
    guard = load_runtime_guard_module()
    processes = [
        guard.ProcessInfo(pid=501, ppid=1, rss_kib=80000, command="/opt/agent-browser/chrome-linux/chrome --headless --type=renderer", cwd=OWNED),
        guard.ProcessInfo(pid=999, ppid=1, rss_kib=15000, command="dockerd --config-file=/etc/docker/daemon.json", cwd=OWNED),
    ]

    payload = guard.inspect_runtime(processes, REPO_ROOT)

    assert payload["orphan_daemon_count"] == 0
    assert payload["reparented_residue_count"] == 1
    assert payload["reparented_residue_pids"] == [501]
    # dockerd's daemon.json must not be misread as agent-browser daemon.js residue.
    assert 999 not in payload["reparented_residue_pids"]
    assert guard.runtime_residue_total(payload) == 1


def test_inspect_runtime_excludes_foreign_reparented_residue() -> None:
    # #365: a neighbor checkout's reparented Chromium residue must not fail this
    # checkout's runtime gate.
    guard = load_runtime_guard_module()
    processes = [
        guard.ProcessInfo(pid=501, ppid=1, rss_kib=80000, command="/opt/agent-browser/chrome-linux/chrome --headless --type=renderer", cwd=OWNED),
        guard.ProcessInfo(pid=502, ppid=1, rss_kib=80000, command="/opt/agent-browser/chrome-linux/chrome --headless --type=renderer", cwd=FOREIGN),
    ]

    payload = guard.inspect_runtime(processes, REPO_ROOT)

    assert payload["reparented_residue_pids"] == [501]
    assert 502 not in payload["reparented_residue_pids"]


def test_inspect_runtime_ignores_non_headless_desktop_chrome() -> None:
    # #302 follow-up: a developer's desktop Chrome is NOT agent-browser residue.
    guard = load_runtime_guard_module()
    processes = [
        guard.ProcessInfo(pid=700, ppid=1, rss_kib=300000, command="/opt/google/chrome/chrome --profile-directory=Default", cwd=OWNED),
        guard.ProcessInfo(pid=701, ppid=1, rss_kib=90000, command="/usr/bin/chromium --type=renderer --headless", cwd=OWNED),
    ]

    payload = guard.inspect_runtime(processes, REPO_ROOT)

    # Desktop Chrome (no headless/automation marker) is ignored; the headless one is residue.
    assert payload["reparented_residue_pids"] == [701]
    assert 700 not in payload["reparented_residue_pids"]


def test_inspect_runtime_zombie_residue_requires_ownership() -> None:
    # #302: a <defunct> agent-browser/headless-Chromium process must keep the
    # runtime from being reported clean. #365: only when proven owned by this
    # checkout. A zombie usually releases its cwd, so an unattributable zombie is
    # conservatively NOT flagged (fail-closed); the guard never reaps it anyway.
    guard = load_runtime_guard_module()
    processes = [
        guard.ProcessInfo(pid=600, ppid=1, rss_kib=0, command="[headless_shell] <defunct>", cwd=OWNED),
        guard.ProcessInfo(pid=602, ppid=1, rss_kib=0, command="[headless_shell] <defunct>", cwd=FOREIGN),
        guard.ProcessInfo(pid=603, ppid=1, rss_kib=0, command="[headless_shell] <defunct>", cwd=None),
        guard.ProcessInfo(pid=601, ppid=700, rss_kib=0, command="[bash] <defunct>", cwd=OWNED),
    ]

    payload = guard.inspect_runtime(processes, REPO_ROOT)

    assert payload["zombie_residue_count"] == 1
    assert payload["zombie_residue_pids"] == [600]
    # foreign zombie, unknown-cwd zombie, and a non-browser zombie are not flagged.
    assert 602 not in payload["zombie_residue_pids"]
    assert 603 not in payload["zombie_residue_pids"]
    assert 601 not in payload["zombie_residue_pids"]
    assert guard.runtime_residue_total(payload) == 1


def test_runtime_next_step_distinguishes_residue_class() -> None:
    # #309: a reap-able orphan daemon tree gets the cleanup command, but residue
    # that is purely reparented/zombie cannot be reaped by --cleanup-orphans.
    guard = load_runtime_guard_module()

    clean = guard.inspect_runtime([], REPO_ROOT)
    assert guard.runtime_next_step(clean) == (None, None)

    orphan = guard.inspect_runtime(
        [guard.ProcessInfo(pid=100, ppid=1, rss_kib=10, command="node /tmp/agent-browser/dist/daemon.js", cwd=OWNED)],
        REPO_ROOT,
    )
    command, kind = guard.runtime_next_step(orphan)
    assert kind == "cleanup_command"
    assert "--cleanup-orphans --execute" in command

    reparented = guard.inspect_runtime(
        [guard.ProcessInfo(pid=501, ppid=1, rss_kib=80000, command="/opt/agent-browser/chrome-linux/chrome --headless --type=renderer", cwd=OWNED)],
        REPO_ROOT,
    )
    guidance, kind = guard.runtime_next_step(reparented)
    assert kind == "init_reap"
    lowered = guidance.lower()
    assert "init" in lowered or "container" in lowered


def test_is_checkout_owned_fails_closed_on_unknown_cwd() -> None:
    guard = load_runtime_guard_module()
    owned = guard.ProcessInfo(pid=1, ppid=1, rss_kib=0, command="x", cwd=OWNED)
    foreign = guard.ProcessInfo(pid=2, ppid=1, rss_kib=0, command="x", cwd=FOREIGN)
    unknown = guard.ProcessInfo(pid=3, ppid=1, rss_kib=0, command="x", cwd=None)
    # A sibling path that merely shares the repo_root string prefix is NOT owned:
    # ownership is component-wise (repo_root in cwd.parents), not str.startswith.
    prefix_sibling = guard.ProcessInfo(pid=4, ppid=1, rss_kib=0, command="x", cwd="/repo/checkout-2")
    resolved_root = REPO_ROOT.resolve()
    assert guard.is_checkout_owned(owned, resolved_root) is True
    assert guard.is_checkout_owned(foreign, resolved_root) is False
    assert guard.is_checkout_owned(unknown, resolved_root) is False
    assert guard.is_checkout_owned(prefix_sibling, resolved_root) is False


# --- real-process CLI tests: prove the /proc cwd wiring + neighbor safety (#365) ---


def test_assert_no_orphans_healthy_with_only_foreign_daemon(tmp_path: Path) -> None:
    # Acceptance: a neighbor task's live daemon (different checkout) alive on the
    # host must NOT fail this checkout's runtime probe.
    owned_root = tmp_path / "checkout"
    owned_root.mkdir()
    foreign_root = tmp_path / "neighbor"
    foreign_root.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    markers = MarkerProcesses()
    try:
        foreign_pid = markers.spawn(foreign_root)
        make_fake_ps(bin_dir, output=f"{foreign_pid} 1 10 node /tmp/agent-browser/dist/daemon.js")
        result = _run_guard(["--assert-no-orphans", "--json"], bin_dir, owned_root)
        assert result.returncode == 0, result.stdout + result.stderr
        assert markers.alive(foreign_pid)
    finally:
        markers.close()


def test_cleanup_preview_excludes_foreign_daemon(tmp_path: Path) -> None:
    # Preview (no --execute): the kill set targets only the this-checkout daemon.
    owned_root = tmp_path / "checkout"
    owned_root.mkdir()
    foreign_root = tmp_path / "neighbor"
    foreign_root.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    markers = MarkerProcesses()
    try:
        owned_pid = markers.spawn(owned_root)
        foreign_pid = markers.spawn(foreign_root)
        make_fake_ps(
            bin_dir,
            output="\n".join(
                [
                    f"{owned_pid} 1 10 node /tmp/agent-browser/dist/daemon.js",
                    f"{foreign_pid} 1 10 node /tmp/agent-browser/dist/daemon.js",
                ]
            ),
        )
        result = _run_guard(["--cleanup-orphans", "--json"], bin_dir, owned_root)
        payload = json.loads(result.stdout)
        assert payload["target_pids"] == [owned_pid]
        assert foreign_pid not in payload["target_pids"]
        assert markers.alive(owned_pid)
        assert markers.alive(foreign_pid)
    finally:
        markers.close()


def test_cleanup_execute_targets_owned_and_spares_foreign(tmp_path: Path) -> None:
    # Acceptance, end-to-end: --execute reaps the this-checkout orphan and leaves
    # the neighbor checkout's live daemon running.
    owned_root = tmp_path / "checkout"
    owned_root.mkdir()
    foreign_root = tmp_path / "neighbor"
    foreign_root.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    markers = MarkerProcesses()
    try:
        owned_pid = markers.spawn(owned_root)
        foreign_pid = markers.spawn(foreign_root)
        owned_line = f"{owned_pid} 1 10 node /tmp/agent-browser/dist/daemon.js"
        foreign_line = f"{foreign_pid} 1 10 node /tmp/agent-browser/dist/daemon.js"
        # snapshot 1: both present; later snapshots: owned reaped, neighbor remains.
        make_fake_ps_sequence(bin_dir, outputs=["\n".join([owned_line, foreign_line]), foreign_line])
        result = _run_guard(["--cleanup-orphans", "--execute", "--json"], bin_dir, owned_root)
        payload = json.loads(result.stdout)
        assert payload["target_pids"] == [owned_pid]
        assert foreign_pid not in payload["target_pids"]
        assert payload["remaining_pids"] == []
        assert result.returncode == 0
        # the guard never signalled the neighbor's real process.
        assert markers.alive(foreign_pid)
    finally:
        markers.close()


def test_runtime_guard_doctor_check_fails_for_owned_orphan_daemons(tmp_path: Path) -> None:
    owned_root = tmp_path / "checkout"
    owned_root.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_fake_agent_browser(bin_dir)
    markers = MarkerProcesses()
    try:
        daemon_pid = markers.spawn(owned_root)
        child_pid = markers.spawn(owned_root)
        make_fake_ps(
            bin_dir,
            output="\n".join(
                [
                    f"{daemon_pid} 1 10 node /tmp/agent-browser/dist/daemon.js",
                    f"{child_pid} {daemon_pid} 20 chrome-headless --type=renderer",
                ]
            ),
        )
        result = _run_guard(["--doctor-check"], bin_dir, owned_root)
        assert result.returncode == 1
        assert "--cleanup-orphans --execute" in result.stderr
    finally:
        markers.close()


def test_runtime_guard_assert_no_orphans_inspects_without_helpcheck(tmp_path: Path) -> None:
    owned_root = tmp_path / "checkout"
    owned_root.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    markers = MarkerProcesses()
    try:
        daemon_pid = markers.spawn(owned_root)
        child_pid = markers.spawn(owned_root)
        make_fake_ps(
            bin_dir,
            output="\n".join(
                [
                    f"{daemon_pid} 1 10 node /tmp/agent-browser/dist/daemon.js",
                    f"{child_pid} {daemon_pid} 20 chrome-headless --type=renderer",
                ]
            ),
        )
        result = _run_guard(["--assert-no-orphans", "--json"], bin_dir, owned_root)
        assert result.returncode == 1
        assert "--cleanup-orphans --execute" in result.stderr
        payload = json.loads(result.stdout)
        assert payload["runtime"]["orphan_tree_pids"] == sorted([daemon_pid, child_pid])
    finally:
        markers.close()


def test_assert_no_orphans_unhealthy_for_owned_reparented_chromium_residue(tmp_path: Path) -> None:
    owned_root = tmp_path / "checkout"
    owned_root.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    markers = MarkerProcesses()
    try:
        residue_pid = markers.spawn(owned_root)
        make_fake_ps(
            bin_dir,
            output=f"{residue_pid} 1 64000 /opt/agent-browser/chrome-linux/chrome --headless --type=gpu-process",
        )
        result = _run_guard(["--assert-no-orphans", "--json"], bin_dir, owned_root)
        assert result.returncode == 1, result.stdout
        payload = json.loads(result.stdout)
        assert payload["healthy"] is False
        assert payload["runtime"]["orphan_daemon_count"] == 0
        assert payload["runtime"]["reparented_residue_pids"] == [residue_pid]
    finally:
        markers.close()


def test_assert_no_orphans_init_reap_guidance_for_reparented_only(tmp_path: Path) -> None:
    # #309: with only reparented residue and no reap-able orphan tree, next_step is
    # init-reap guidance, not the dead-end cleanup command.
    owned_root = tmp_path / "checkout"
    owned_root.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    markers = MarkerProcesses()
    try:
        residue_pid = markers.spawn(owned_root)
        make_fake_ps(
            bin_dir,
            output=f"{residue_pid} 1 64000 /opt/agent-browser/chrome-linux/chrome --headless --type=gpu-process",
        )
        result = _run_guard(["--assert-no-orphans", "--json"], bin_dir, owned_root)
        assert result.returncode == 1, result.stdout
        payload = json.loads(result.stdout)
        assert payload["healthy"] is False
        assert payload["runtime"]["orphan_tree_pids"] == []
        assert payload["next_step_kind"] == "init_reap"
        assert "Run `" not in result.stderr
        assert "container" in result.stderr.lower()
    finally:
        markers.close()


def test_runtime_guard_cleanup_fails_when_orphan_respawns_after_clean_snapshot(tmp_path: Path) -> None:
    owned_root = tmp_path / "checkout"
    owned_root.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    markers = MarkerProcesses()
    try:
        daemon_pid = markers.spawn(owned_root)
        child_pid = markers.spawn(owned_root)
        # snapshot 1: clean; snapshot 2+: an owned orphan tree reappears.
        make_fake_ps_sequence(
            bin_dir,
            outputs=[
                "",
                "\n".join(
                    [
                        f"{daemon_pid} 1 10 node /tmp/agent-browser/dist/daemon.js",
                        f"{child_pid} {daemon_pid} 20 chrome-headless --type=renderer",
                    ]
                ),
            ],
        )
        result = _run_guard(["--cleanup-orphans", "--execute", "--json"], bin_dir, owned_root)
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        assert payload["target_pids"] == []
        assert payload["remaining_pids"] == sorted([daemon_pid, child_pid])
    finally:
        markers.close()


def test_cleanup_execute_skips_grace_sleep_when_no_targets() -> None:
    module = load_runtime_guard_module()
    calls = {"sleep": 0}
    original_list_processes = module.list_processes
    original_sleep = module.time.sleep

    def fake_list_processes(_repo_root: Path):
        return []

    def fail_sleep(_seconds: float) -> None:
        calls["sleep"] += 1
        raise AssertionError("cleanup with no target pids must not wait")

    try:
        module.list_processes = fake_list_processes
        module.time.sleep = fail_sleep
        payload = module.cleanup_orphans(Path("/repo/checkout"), execute=True)
    finally:
        module.list_processes = original_list_processes
        module.time.sleep = original_sleep

    assert calls["sleep"] == 0
    assert payload["target_pids"] == []
    assert payload["remaining_pids"] == []


def test_doctor_marks_agent_browser_unhealthy_when_runtime_guard_fails(tmp_path: Path) -> None:
    owned_root = ROOT  # doctor.py resolves the runtime guard relative to repo_root
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_fake_agent_browser(bin_dir)
    markers = MarkerProcesses()
    try:
        daemon_pid = markers.spawn(owned_root)
        child_pid = markers.spawn(owned_root)
        make_fake_ps(
            bin_dir,
            output="\n".join(
                [
                    f"{daemon_pid} 1 10 node /tmp/agent-browser/dist/daemon.js",
                    f"{child_pid} {daemon_pid} 20 chrome-headless --type=renderer",
                ]
            ),
        )
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
        result = subprocess.run(
            [sys.executable, "scripts/doctor.py", "--repo-root", str(ROOT), "--json", "--tool-id", "agent-browser"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        assert payload[0]["doctor_status"] == "unhealthy"
        assert payload[0]["healthcheck"]["failure_hint"]
    finally:
        markers.close()
