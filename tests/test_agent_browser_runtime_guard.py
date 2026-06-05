from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_GUARD_PATH = ROOT / "scripts" / "agent_browser_runtime_guard.py"


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


def test_inspect_runtime_tracks_orphan_daemon_tree() -> None:
    guard = load_runtime_guard_module()
    processes = [
        guard.ProcessInfo(pid=100, ppid=1, rss_kib=10, command="node /tmp/agent-browser/dist/daemon.js"),
        guard.ProcessInfo(pid=101, ppid=100, rss_kib=20, command="chrome-headless --type=renderer"),
        guard.ProcessInfo(pid=200, ppid=999, rss_kib=10, command="node /tmp/agent-browser/dist/daemon.js"),
    ]

    payload = guard.inspect_runtime(processes)

    assert payload["daemon_count"] == 2
    assert payload["orphan_daemon_count"] == 1
    assert payload["orphan_descendant_count"] == 1
    assert payload["orphan_tree_pids"] == [100, 101]


def test_inspect_runtime_flags_reparented_chromium_residue() -> None:
    # #302: the owning agent-browser daemon already died, but its Chromium got
    # reparented to PID 1. The daemon-rooted orphan scan finds nothing, yet this
    # residue must not be reported clean.
    guard = load_runtime_guard_module()
    processes = [
        guard.ProcessInfo(pid=501, ppid=1, rss_kib=80000, command="/opt/agent-browser/chrome-linux/chrome --headless --type=renderer"),
        guard.ProcessInfo(pid=999, ppid=1, rss_kib=15000, command="dockerd --config-file=/etc/docker/daemon.json"),
    ]

    payload = guard.inspect_runtime(processes)

    assert payload["orphan_daemon_count"] == 0
    assert payload["reparented_residue_count"] == 1
    assert payload["reparented_residue_pids"] == [501]
    # dockerd's daemon.json must not be misread as agent-browser daemon.js residue.
    assert 999 not in payload["reparented_residue_pids"]
    assert guard.runtime_residue_total(payload) == 1


def test_inspect_runtime_ignores_non_headless_desktop_chrome() -> None:
    # #302 follow-up: a developer's desktop Chrome reparented to init is NOT
    # agent-browser gather residue. Bare chrome/chromium only counts when it is a
    # headless/automation process, so the runtime gate is not falsely tripped.
    guard = load_runtime_guard_module()
    processes = [
        guard.ProcessInfo(pid=700, ppid=1, rss_kib=300000, command="/opt/google/chrome/chrome --profile-directory=Default"),
        guard.ProcessInfo(pid=701, ppid=1, rss_kib=90000, command="/usr/bin/chromium --type=renderer --headless"),
    ]

    payload = guard.inspect_runtime(processes)

    # Desktop Chrome (no headless/automation marker) is ignored; the headless one is residue.
    assert payload["reparented_residue_pids"] == [701]
    assert 700 not in payload["reparented_residue_pids"]


def test_inspect_runtime_flags_zombie_browser_residue() -> None:
    # #302: a <defunct> agent-browser/headless-Chromium process the host init has
    # not reaped must keep the runtime from being reported clean. Zombies lose
    # their argv, so detection keys on the agent-browser-specific process names
    # (headless_shell / agent-browser), not a bare `chrome` that could be a
    # transient desktop-Chrome zombie.
    guard = load_runtime_guard_module()
    processes = [
        guard.ProcessInfo(pid=600, ppid=1, rss_kib=0, command="[headless_shell] <defunct>"),
        guard.ProcessInfo(pid=601, ppid=700, rss_kib=0, command="[bash] <defunct>"),
    ]

    payload = guard.inspect_runtime(processes)

    assert payload["zombie_residue_count"] == 1
    assert payload["zombie_residue_pids"] == [600]
    # a non-browser zombie (defunct bash) is not browser residue.
    assert 601 not in payload["zombie_residue_pids"]
    assert guard.runtime_residue_total(payload) == 1


def test_assert_no_orphans_unhealthy_for_reparented_chromium_residue(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_fake_ps(
        bin_dir,
        output="500 1 64000 /opt/agent-browser/chrome-linux/chrome --headless --type=gpu-process",
    )
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
    env.pop("CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS", None)
    result = subprocess.run(
        [sys.executable, str(RUNTIME_GUARD_PATH), "--repo-root", str(ROOT), "--assert-no-orphans", "--json"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1, result.stdout
    payload = json.loads(result.stdout)
    assert payload["healthy"] is False
    assert payload["runtime"]["orphan_daemon_count"] == 0
    assert payload["runtime"]["reparented_residue_pids"] == [500]


def test_runtime_guard_doctor_check_fails_for_orphan_daemons(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_fake_agent_browser(bin_dir)
    make_fake_ps(
        bin_dir,
        output="\n".join(
            [
                "100 1 10 node /tmp/agent-browser/dist/daemon.js",
                "101 100 20 chrome-headless --type=renderer",
            ]
        ),
    )

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
    result = subprocess.run(
        [sys.executable, str(RUNTIME_GUARD_PATH), "--repo-root", str(ROOT), "--doctor-check"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert "--cleanup-orphans --execute" in result.stderr


def test_runtime_guard_assert_no_orphans_inspects_without_helpcheck(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_fake_ps(
        bin_dir,
        output="\n".join(
            [
                "100 1 10 node /tmp/agent-browser/dist/daemon.js",
                "101 100 20 chrome-headless --type=renderer",
            ]
        ),
    )

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
    result = subprocess.run(
        [sys.executable, str(RUNTIME_GUARD_PATH), "--repo-root", str(ROOT), "--assert-no-orphans", "--json"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert "--cleanup-orphans --execute" in result.stderr
    payload = json.loads(result.stdout)
    assert payload["runtime"]["orphan_tree_pids"] == [100, 101]


def test_runtime_guard_cleanup_fails_when_orphan_respawns_after_clean_snapshot(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_fake_ps_sequence(
        bin_dir,
        outputs=[
            "",
            "\n".join(
                [
                    "100 1 10 node /tmp/agent-browser/dist/daemon.js",
                    "101 100 20 chrome-headless --type=renderer",
                ]
            ),
        ],
    )

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
    result = subprocess.run(
        [sys.executable, str(RUNTIME_GUARD_PATH), "--repo-root", str(ROOT), "--cleanup-orphans", "--execute", "--json"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["target_pids"] == []
    assert payload["remaining_pids"] == [100, 101]


def test_doctor_marks_agent_browser_unhealthy_when_runtime_guard_fails(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_fake_agent_browser(bin_dir)
    make_fake_ps(
        bin_dir,
        output="\n".join(
            [
                "100 1 10 node /tmp/agent-browser/dist/daemon.js",
                "101 100 20 chrome-headless --type=renderer",
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
