"""#367: ingest a repo-declared command-timing log as a runtime sample source.

Covers both the portable library (`runtime_timing_log_lib`) and the integration
through the runtime helpers (`render_runtime_summary.py`, `check_runtime_budget.py`)
so a repo's existing structured timing log lights up gate hot spots without a
hand-rolled log->runtime-signals.json bridge.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

from .support import ROOT, run_script

SKILL_SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))
timing_log_lib = importlib.import_module("runtime_timing_log_lib")

RENDER_SCRIPT = "skills/public/quality/scripts/render_runtime_summary.py"
BUDGET_SCRIPT = "skills/public/quality/scripts/check_runtime_budget.py"
LOG_REL = ".charness/quality/command-timing.jsonl"


# --- library unit tests -------------------------------------------------------


def test_inert_when_command_timing_log_absent(tmp_path: Path) -> None:
    result = timing_log_lib.evaluate_timing_log(tmp_path, {}, "default")
    assert result["configured"] is False
    assert result["errors"] == []
    assert result["commands"] == {}


def test_inert_when_command_timing_log_empty_mapping(tmp_path: Path) -> None:
    result = timing_log_lib.evaluate_timing_log(tmp_path, {"command_timing_log": {}}, "default")
    assert result["configured"] is False
    assert result["commands"] == {}


def _write_jsonl(repo: Path, rows: list[dict[str, object]]) -> None:
    log_path = repo / LOG_REL
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _adapter_data(**overrides: object) -> dict[str, object]:
    config = {
        "path": LOG_REL,
        "format": "jsonl",
        "field_map": {"label": "command", "elapsed": "elapsed_ms"},
        "elapsed_unit": "ms",
    }
    config.update(overrides)
    return {"command_timing_log": config}


def test_jsonl_aggregates_latest_median_and_max(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path,
        [
            {"command": "pytest", "elapsed_ms": 100},
            {"command": "pytest", "elapsed_ms": 300},
            {"command": "pytest", "elapsed_ms": 200},
            {"command": "ruff", "elapsed_ms": 50},
        ],
    )
    result = timing_log_lib.evaluate_timing_log(tmp_path, _adapter_data(), "default")
    assert result["errors"] == []
    assert result["file_present"] is True
    assert result["samples_total"] == 4
    pytest_entry = result["commands"]["pytest"]
    assert pytest_entry["latest"] == {"elapsed_ms": 200}  # last in file order
    assert pytest_entry["median_recent_elapsed_ms"] == 200  # median(100,300,200)
    assert pytest_entry["max_recent_elapsed_ms"] == 300
    assert pytest_entry["samples"] == 3
    assert result["commands"]["ruff"]["latest"] == {"elapsed_ms": 50}


def test_recent_window_limits_median_and_max(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path,
        [{"command": "pytest", "elapsed_ms": ms} for ms in (9000, 9000, 100, 200, 300)],
    )
    result = timing_log_lib.evaluate_timing_log(tmp_path, _adapter_data(recent_window=3), "default")
    entry = result["commands"]["pytest"]
    # Only the last 3 samples (100, 200, 300) feed median/max; the early spikes drop out.
    assert entry["median_recent_elapsed_ms"] == 200
    assert entry["max_recent_elapsed_ms"] == 300
    assert entry["latest"] == {"elapsed_ms": 300}
    assert entry["samples"] == 5  # total sample count is preserved


def test_elapsed_unit_seconds_converts_to_milliseconds(tmp_path: Path) -> None:
    _write_jsonl(tmp_path, [{"command": "build", "duration_s": 1.5}])
    data = _adapter_data(field_map={"label": "command", "elapsed": "duration_s"}, elapsed_unit="s")
    result = timing_log_lib.evaluate_timing_log(tmp_path, data, "default")
    assert result["commands"]["build"]["latest"] == {"elapsed_ms": 1500}


def test_profile_field_filters_to_selected_profile(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path,
        [
            {"command": "pytest", "elapsed_ms": 100, "runner": "ci"},
            {"command": "pytest", "elapsed_ms": 999, "runner": "laptop"},
        ],
    )
    data = _adapter_data(field_map={"label": "command", "elapsed": "elapsed_ms", "profile": "runner"})
    ci = timing_log_lib.evaluate_timing_log(tmp_path, data, "ci")
    assert ci["commands"]["pytest"]["latest"] == {"elapsed_ms": 100}
    assert ci["samples_total"] == 1
    # The literal machine-auto "default" profile is not a stored value, so it
    # matches every entry rather than filtering them all out.
    default = timing_log_lib.evaluate_timing_log(tmp_path, data, "default")
    assert default["samples_total"] == 2


def test_missing_log_file_is_soft(tmp_path: Path) -> None:
    result = timing_log_lib.evaluate_timing_log(tmp_path, _adapter_data(), "default")
    assert result["configured"] is True
    assert result["file_present"] is False
    assert result["errors"] == []
    assert result["commands"] == {}


def test_json_array_format(tmp_path: Path) -> None:
    log_path = tmp_path / LOG_REL
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        json.dumps([{"command": "pytest", "elapsed_ms": 100}, {"command": "pytest", "elapsed_ms": 300}]),
        encoding="utf-8",
    )
    result = timing_log_lib.evaluate_timing_log(tmp_path, _adapter_data(format="json"), "default")
    assert result["commands"]["pytest"]["max_recent_elapsed_ms"] == 300


def test_malformed_jsonl_lines_are_skipped(tmp_path: Path) -> None:
    log_path = tmp_path / LOG_REL
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        '{"command": "pytest", "elapsed_ms": 100}\nnot json\n\n{"command": "pytest", "elapsed_ms": 200}\n',
        encoding="utf-8",
    )
    result = timing_log_lib.evaluate_timing_log(tmp_path, _adapter_data(), "default")
    assert result["samples_total"] == 2
    assert result["commands"]["pytest"]["latest"] == {"elapsed_ms": 200}


def test_config_errors_when_field_map_incomplete(tmp_path: Path) -> None:
    _write_jsonl(tmp_path, [{"command": "pytest", "elapsed_ms": 100}])
    data = {"command_timing_log": {"path": LOG_REL, "field_map": {"label": "command"}}}
    result = timing_log_lib.evaluate_timing_log(tmp_path, data, "default")
    assert result["commands"] == {}
    assert any("elapsed" in err for err in result["errors"])


def test_config_error_when_not_a_mapping(tmp_path: Path) -> None:
    result = timing_log_lib.evaluate_timing_log(tmp_path, {"command_timing_log": "oops"}, "default")
    assert result["errors"] == ["command_timing_log must be a mapping"]


def test_config_error_when_field_map_not_a_mapping(tmp_path: Path) -> None:
    _write_jsonl(tmp_path, [{"command": "pytest", "elapsed_ms": 100}])
    data = {"command_timing_log": {"path": LOG_REL, "field_map": "label,elapsed"}}
    result = timing_log_lib.evaluate_timing_log(tmp_path, data, "default")
    assert result["commands"] == {}
    assert any("field_map" in err for err in result["errors"])


def test_json_whole_file_malformed_is_soft(tmp_path: Path) -> None:
    # data-shape problems (unparseable file / non-list payload) are soft: no
    # samples, no config error — only config-shape problems fail loud.
    log_path = tmp_path / LOG_REL
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text('{"command": "pytest", "elapsed_ms": 100}', encoding="utf-8")  # object, not array
    result = timing_log_lib.evaluate_timing_log(tmp_path, _adapter_data(format="json"), "default")
    assert result["file_present"] is True
    assert result["samples_total"] == 0
    assert result["errors"] == []
    assert result["commands"] == {}

    log_path.write_text("definitely not json", encoding="utf-8")
    corrupt = timing_log_lib.evaluate_timing_log(tmp_path, _adapter_data(format="json"), "default")
    assert corrupt["samples_total"] == 0
    assert corrupt["errors"] == []


def test_recent_window_surfaced_in_report(tmp_path: Path) -> None:
    _write_jsonl(tmp_path, [{"command": "pytest", "elapsed_ms": 100}])
    result = timing_log_lib.evaluate_timing_log(tmp_path, _adapter_data(recent_window=7), "default")
    assert result["recent_window"] == 7


def test_negative_and_nonnumeric_elapsed_skipped(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path,
        [
            {"command": "pytest", "elapsed_ms": -5},
            {"command": "pytest", "elapsed_ms": "slow"},
            {"command": "pytest", "elapsed_ms": 120},
        ],
    )
    result = timing_log_lib.evaluate_timing_log(tmp_path, _adapter_data(), "default")
    assert result["commands"]["pytest"]["samples"] == 1
    assert result["commands"]["pytest"]["latest"] == {"elapsed_ms": 120}


# --- integration through the runtime helpers ----------------------------------


def _seed_repo(
    tmp_path: Path,
    *,
    adapter_lines: list[str],
    log_rows: list[dict[str, object]] | None = None,
    signals: dict | None = None,
) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".charness" / "quality").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")
    if log_rows is not None:
        (repo / LOG_REL).write_text("\n".join(json.dumps(r) for r in log_rows) + "\n", encoding="utf-8")
    if signals is not None:
        (repo / ".charness" / "quality" / "runtime-signals.json").write_text(json.dumps(signals), encoding="utf-8")
    return repo


_TIMING_ADAPTER = [
    "version: 1",
    "repo: testrepo",
    "output_dir: charness-artifacts/quality",
    "command_timing_log:",
    f"  path: {LOG_REL}",
    "  format: jsonl",
    "  field_map:",
    "    label: command",
    "    elapsed: elapsed_ms",
    "  elapsed_unit: ms",
]


def test_render_runtime_summary_ingests_command_timing_log(tmp_path: Path) -> None:
    repo = _seed_repo(
        tmp_path,
        adapter_lines=_TIMING_ADAPTER,
        log_rows=[
            {"command": "pytest", "elapsed_ms": 60000},
            {"command": "specdown", "elapsed_ms": 12000},
        ],
    )
    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["commands_source"] == "command_timing_log"
    assert payload["timing_log"]["source_used"] is True
    assert payload["timing_log"]["samples_total"] == 2
    labels = {hot["label"] for hot in payload["runtime_hotspots"]}
    assert {"pytest", "specdown"} <= labels
    assert any("command_timing_log" in line for line in payload["markdown_lines"])


def test_runtime_signals_take_precedence_over_timing_log(tmp_path: Path) -> None:
    repo = _seed_repo(
        tmp_path,
        adapter_lines=_TIMING_ADAPTER,
        log_rows=[{"command": "pytest", "elapsed_ms": 60000}],
        signals={"commands": {"pytest": {"latest": {"elapsed_ms": 5}, "median_recent_elapsed_ms": 5}}},
    )
    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["commands_source"] == "runtime_signals"
    assert payload["timing_log"]["source_used"] is False
    pytest_hot = next(h for h in payload["runtime_hotspots"] if h["label"] == "pytest")
    assert pytest_hot["latest_elapsed_ms"] == 5  # from signals, not the 60000 log sample


def test_check_runtime_budget_violation_from_timing_log(tmp_path: Path) -> None:
    repo = _seed_repo(
        tmp_path,
        adapter_lines=[*_TIMING_ADAPTER, "runtime_budgets:", "  pytest: 1000"],
        log_rows=[{"command": "pytest", "elapsed_ms": 60000}],
    )
    result = run_script(BUDGET_SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 1, result.stdout
    payload = json.loads(result.stdout)
    assert payload["commands_source"] == "command_timing_log"
    assert [v["label"] for v in payload["violations"]] == ["pytest"]


def test_check_runtime_budget_fails_loud_on_misconfigured_timing_log(tmp_path: Path) -> None:
    bad_adapter = [
        "version: 1",
        "repo: testrepo",
        "output_dir: charness-artifacts/quality",
        "command_timing_log:",
        f"  path: {LOG_REL}",
        "  field_map:",
        "    label: command",  # elapsed deliberately omitted
    ]
    repo = _seed_repo(tmp_path, adapter_lines=bad_adapter, log_rows=[{"command": "pytest", "elapsed_ms": 100}])
    result = run_script(BUDGET_SCRIPT, "--repo-root", str(repo), "--json", "--runtime-profile", "default")
    assert result.returncode == 1, result.stdout
    payload = json.loads(result.stdout)
    assert any("command_timing_log" in err for err in payload["profile_config_errors"])
