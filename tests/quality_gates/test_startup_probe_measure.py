from __future__ import annotations

import json
from pathlib import Path

from .support import run_script, write_executable

SCRIPT = "skills/public/quality/scripts/measure_startup_probes.py"


def _seed_repo(
    tmp_path: Path,
    *,
    probe_sleep_seconds: float = 0.0,
    failing: bool = False,
    timeout_seconds: int | None = None,
) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    write_executable(
        repo / "scripts" / "probe.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "import time",
                f"time.sleep({probe_sleep_seconds})",
                f"raise SystemExit({1 if failing else 0})",
            ]
        ),
    )
    timeout_lines = [] if timeout_seconds is None else [f"    timeout_seconds: {timeout_seconds}"]
    lines = [
        "version: 1",
        "repo: demo",
        "language: en",
        "output_dir: charness-artifacts/quality",
        "runtime_budgets:",
        "  demo-version: 500",
        "startup_probes:",
        "  - label: demo-version",
        "    command:",
        "      - python3",
        "      - scripts/probe.py",
        "    class: standing",
        "    startup_mode: warm",
        "    surface: direct",
        "    samples: 2",
        *timeout_lines,
        "  - label: demo-release",
        "    command:",
        "      - python3",
        "      - scripts/probe.py",
        "    class: release",
        "    startup_mode: first-launch",
        "    surface: install-like",
        "    samples: 1",
    ]
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return repo


def test_measure_startup_probes_filters_by_class_and_reports_timings(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--class", "standing", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["probes_configured"] == 2
    assert payload["probes_measured"] == 1
    assert payload["failures"] == []
    measured = payload["measured"][0]
    assert measured["label"] == "demo-version"
    assert measured["class"] == "standing"
    assert measured["startup_mode"] == "warm"
    assert measured["surface"] == "direct"
    assert measured["samples_requested"] == 2
    assert measured["samples_ran"] == 2
    assert measured["status"] == "ok"


def test_measure_startup_probes_can_record_runtime_signals(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    result = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--class",
        "standing",
        "--record-runtime-signals",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    summary = json.loads((repo / ".charness" / "quality" / "runtime-signals.json").read_text(encoding="utf-8"))
    assert any("demo-version" in profile["commands"] for profile in summary["profiles"].values())


def test_measure_startup_probes_fails_when_command_fails(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, failing=True)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--class", "standing", "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert len(payload["failures"]) == 1
    assert payload["failures"][0]["label"] == "demo-version"
    assert payload["failures"][0]["status"] == "command-failed"


def test_measure_startup_probes_times_out_hanging_command(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, probe_sleep_seconds=2.0, timeout_seconds=1)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--class", "standing", "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert len(payload["failures"]) == 1
    assert payload["failures"][0]["status"] == "command-timeout"
    assert payload["failures"][0]["timeout_seconds"] == 1
    assert payload["failures"][0]["returncode"] == 124


def test_measure_startup_probes_human_output_reports_timeout(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, probe_sleep_seconds=2.0, timeout_seconds=1)
    result = run_script(SCRIPT, "--repo-root", str(repo), "--class", "standing")

    assert result.returncode == 1
    assert "COMMAND-TIMEOUT" in result.stdout
    assert "rc 124" in result.stdout
