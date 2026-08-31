from __future__ import annotations

import json
from pathlib import Path

import yaml

from .seeding_support import load_module
from .support import ROOT, run_script, write_executable

SCRIPT = "skills/public/quality/scripts/measure_startup_probes.py"
MEASURE_STARTUP_PROBES = load_module("measure_startup_probes_under_test", ROOT / SCRIPT)


def _seed_repo(
    tmp_path: Path,
    *,
    probe_sleep_seconds: float = 0.0,
    failing: bool = False,
    timeout_seconds: float | None = None,
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


def test_measure_startup_probes_summary_bounds_failures() -> None:
    failures = [{"label": f"probe-{index}"} for index in range(12)]
    payload = MEASURE_STARTUP_PROBES.summarize(
        {
            "adapter_path": None,
            "probe_class": "all",
            "probes_configured": 12,
            "probes_measured": 12,
            "measured": failures,
            "failures": failures,
        }
    )

    assert payload["failures_count"] == 12
    assert len(payload["failures_sample"]) == 10
    assert payload["failures_truncated"] is True


def test_measure_startup_probes_shapes_on_one_tree(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path)
    detail = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--class",
        "standing",
        "--detail",
        "--record-runtime-signals",
    )
    assert detail.returncode == 0, detail.stderr
    payload = yaml.safe_load(detail.stdout)
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
    recorded = json.loads(
        (repo / ".charness" / "quality" / "runtime-signals.json").read_text(encoding="utf-8")
    )
    assert any("demo-version" in profile["commands"] for profile in recorded["profiles"].values())

    summary = run_script(SCRIPT, "--repo-root", str(repo), "--class", "standing", "--summary")
    assert summary.returncode == 0
    assert yaml.safe_load(summary.stdout)["probes_measured"] == 1

    (repo / ".charness" / "quality" / "runtime-signals.json").unlink()
    state_root = tmp_path / "task-result" / "runtime" / "quality"
    external = run_script(
        SCRIPT,
        "--repo-root",
        str(repo),
        "--class",
        "standing",
        "--record-runtime-signals",
        "--state-root",
        str(state_root),
    )
    assert external.returncode == 0, external.stderr
    external_summary = json.loads((state_root / "runtime-signals.json").read_text(encoding="utf-8"))
    assert any("demo-version" in profile["commands"] for profile in external_summary["profiles"].values())
    assert not (repo / ".charness" / "quality" / "runtime-signals.json").exists()

    failing_repo = _seed_repo(tmp_path / "failing", failing=True)
    failed = run_script(SCRIPT, "--repo-root", str(failing_repo), "--class", "standing", "--detail")
    assert failed.returncode == 1
    failed_payload = yaml.safe_load(failed.stdout)
    assert len(failed_payload["failures"]) == 1
    assert failed_payload["failures"][0]["label"] == "demo-version"
    assert failed_payload["failures"][0]["status"] == "command-failed"

    timeout_repo = _seed_repo(tmp_path / "timeout", probe_sleep_seconds=0.2, timeout_seconds=0.05)
    timed_out = run_script(SCRIPT, "--repo-root", str(timeout_repo), "--class", "standing", "--detail")
    assert timed_out.returncode == 1
    timeout_payload = yaml.safe_load(timed_out.stdout)
    assert len(timeout_payload["failures"]) == 1
    assert timeout_payload["failures"][0]["status"] == "command-timeout"
    assert timeout_payload["failures"][0]["timeout_seconds"] == 0.05
    assert timeout_payload["failures"][0]["returncode"] == 124
    human = run_script(SCRIPT, "--repo-root", str(timeout_repo), "--class", "standing")
    assert human.returncode == 1
    assert "COMMAND-TIMEOUT" in human.stdout
    assert "rc 124" in human.stdout


def test_timeout_seconds_uses_default_for_invalid_probe_value() -> None:
    assert MEASURE_STARTUP_PROBES._timeout_seconds({"timeout_seconds": "bad"}) == float(
        MEASURE_STARTUP_PROBES.DEFAULT_PROBE_TIMEOUT_SECONDS
    )
    assert MEASURE_STARTUP_PROBES._timeout_seconds({"timeout_seconds": 0}) == float(
        MEASURE_STARTUP_PROBES.DEFAULT_PROBE_TIMEOUT_SECONDS
    )
