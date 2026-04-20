from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_GUARD_PATH = ROOT / "skills" / "support" / "agent-browser" / "scripts" / "runtime_guard.py"


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
