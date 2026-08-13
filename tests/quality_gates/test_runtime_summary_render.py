"""Acceptance checks for `render_runtime_summary.py`.

Split out of `test_runtime_budget_gate.py`: that module proves the budget *gate*
(pass/fail, violations, profile selection), while this one proves the *renderer*
that turns the same runtime signals into the operator-facing markdown/JSON
summary. Two scripts, two contracts — they share only the seeded repo helper.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

from .support import ROOT, run_script, seed_runtime_budget_repo

RENDER_SCRIPT = "skills/public/quality/scripts/render_runtime_summary.py"
QUALITY_SCRIPTS_DIR = ROOT / "skills" / "public" / "quality" / "scripts"
if str(QUALITY_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(QUALITY_SCRIPTS_DIR))
RENDER_RUNTIME_SUMMARY = QUALITY_SCRIPTS_DIR / "render_runtime_summary.py"
_render_spec = importlib.util.spec_from_file_location(
    "render_runtime_summary_under_test", RENDER_RUNTIME_SUMMARY
)
assert _render_spec is not None and _render_spec.loader is not None
render_runtime_summary = importlib.util.module_from_spec(_render_spec)
_render_spec.loader.exec_module(render_runtime_summary)


def test_render_runtime_summary_uses_structured_runtime_signals(tmp_path: Path) -> None:
    signals = {
        "commands": {
            "pytest": {
                "latest": {"elapsed_ms": 15000, "status": "pass"},
                "median_recent_elapsed_ms": 14000,
            }
        }
    }
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)

    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["signals_present"] is True
    assert payload["markdown_lines"][:3] == [
        "- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `default`.",
        "- runtime hot spots: `pytest` 15.0s latest / 14.0s median, budget 22.0s.",
        "- runtime visibility: weak due to `runtime_visibility_missing_startup_probes`; Add at least one standing startup probe for agent-facing CLI or adapter startup.",
    ]
    # Advisory-interpretation contract rollout (#322): the hot-spot ranking is
    # inference-layer, so a 4th interpretation bullet rides the lines and the JSON.
    assert payload["markdown_lines"][3].startswith("- runtime interpretation (inference-layer trend, not a verdict):")
    interpretation = payload["interpretation"]
    assert set(interpretation) == {"measures", "proxy_for", "blind_spots", "interpretation_question"}
    assert all(interpretation[field].strip() for field in interpretation)
    assert "transient" in interpretation["blind_spots"]  # the load-bearing blind spot


def test_render_runtime_summary_yaml_summary_is_structured(tmp_path: Path) -> None:
    signals = {
        "commands": {"pytest": {"latest": {"elapsed_ms": 15000, "status": "pass"}}}
    }
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)
    args = ("--repo-root", str(repo), "--runtime-profile", "default", "--summary")
    yaml_result = run_script(RENDER_SCRIPT, *args)
    assert yaml_result.returncode == 0
    assert yaml.safe_load(yaml_result.stdout)["runtime_hotspot_count"] == 1


def test_render_runtime_summary_bounds_diagnostic_lists() -> None:
    payload = render_runtime_summary.summarize(
        {
            "runtime_profile": "default",
            "signals_path": "signals.json",
            "signals_present": True,
            "commands_source": "signals",
            "runtime_hotspots": [],
            "stale_runtime_hotspots": [],
            "runtime_visibility_findings": list(range(7)),
            "missing_samples": list(range(7)),
        },
        sample_limit=5,
    )

    assert payload["runtime_visibility_finding_count"] == 7
    assert len(payload["runtime_visibility_findings_sample"]) == 5
    assert payload["runtime_visibility_findings_truncated"] is True
    assert payload["missing_sample_count"] == 7
    assert len(payload["missing_samples_sample"]) == 5
    assert payload["missing_samples_truncated"] is True


def test_render_runtime_summary_names_excluded_stale_hotspots(tmp_path: Path) -> None:
    signals = {
        "updated_at": "2026-06-26T00:00:00Z",
        "commands": {
            "pytest": {
                "latest": {
                    "timestamp": "2026-06-26T00:00:00Z",
                    "elapsed_ms": 15000,
                    "status": "pass",
                },
                "median_recent_elapsed_ms": 14000,
            },
            "check-duplicates": {
                "latest": {
                    "timestamp": "2026-06-04T12:11:36Z",
                    "elapsed_ms": 9995,
                    "status": "pass",
                },
                "median_recent_elapsed_ms": 11877,
            },
        },
    }
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)

    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert [item["label"] for item in payload["runtime_hotspots"]] == ["pytest"]
    assert [item["label"] for item in payload["stale_runtime_hotspots"]] == ["check-duplicates"]
    assert any("stale runtime hot spots excluded" in line for line in payload["markdown_lines"])


def test_render_runtime_summary_names_excluded_stale_hotspots_without_fresh_hotspots(tmp_path: Path) -> None:
    signals = {
        "updated_at": "2026-06-26T00:00:00Z",
        "commands": {
            "retired-check": {
                "latest": {
                    "timestamp": "2026-06-04T12:11:36Z",
                    "elapsed_ms": 9995,
                    "status": "pass",
                },
                "median_recent_elapsed_ms": 11877,
            },
        },
    }
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=signals)

    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["runtime_hotspots"] == []
    assert [item["label"] for item in payload["stale_runtime_hotspots"]] == ["retired-check"]
    assert payload["markdown_lines"][:3] == [
        "- runtime source: structured metrics file `.charness/quality/runtime-signals.json` has no fresh samples for profile `default`.",
        "- stale runtime hot spots excluded: `retired-check` latest sample 2026-06-04T12:11:36Z, 21d old.",
        "- runtime hot spots: unavailable until structured runtime metrics have samples.",
    ]
    assert "interpretation" not in payload


def test_render_runtime_summary_handles_command_timing_log_without_stale_hotspots(tmp_path: Path) -> None:
    lines = render_runtime_summary.render_markdown_lines(
        {
            "runtime_profile": "default",
            "runtime_hotspots": [],
            "stale_runtime_hotspots": [],
            "runtime_visibility_findings": [],
            "timing_log": {"configured": True, "file_present": True, "path": "reports/timing.jsonl"},
        },
        repo_root=tmp_path,
        signals_present=False,
    )

    assert lines[:2] == [
        "- runtime source: command-timing log `reports/timing.jsonl` has no usable samples for profile `default`.",
        "- runtime hot spots: unavailable until structured runtime metrics have samples.",
    ]


def test_render_runtime_summary_handles_command_timing_log_with_only_stale_hotspots(tmp_path: Path) -> None:
    lines = render_runtime_summary.render_markdown_lines(
        {
            "runtime_profile": "default",
            "runtime_hotspots": [],
            "stale_runtime_hotspots": [
                {
                    "label": "retired-check",
                    "latest_timestamp": "2026-06-04T00:00:00Z",
                    "stale_days": 22,
                }
            ],
            "runtime_visibility_findings": [],
            "timing_log": {"configured": True, "file_present": True, "path": "reports/timing.jsonl"},
        },
        repo_root=tmp_path,
        signals_present=False,
    )

    assert lines[:3] == [
        "- runtime source: command-timing log `reports/timing.jsonl` has no fresh usable samples for profile `default`.",
        "- stale runtime hot spots excluded: `retired-check` latest sample 2026-06-04T00:00:00Z, 22d old.",
        "- runtime hot spots: unavailable until structured runtime metrics have samples.",
    ]


def test_render_runtime_summary_normalizes_unexpected_stale_hotspot_shape(tmp_path: Path) -> None:
    lines = render_runtime_summary.render_markdown_lines(
        {
            "runtime_profile": "default",
            "runtime_hotspots": [],
            "stale_runtime_hotspots": {"label": "bad-shape"},
            "runtime_visibility_findings": [],
            "timing_log": {},
        },
        repo_root=tmp_path,
        signals_present=True,
    )

    assert lines[0] == (
        "- runtime source: structured metrics file "
        "`.charness/quality/runtime-signals.json` has no samples for profile `default`."
    )
    assert not any("stale runtime hot spots excluded" in line for line in lines)


def test_render_runtime_summary_omits_interpretation_without_hotspots(tmp_path: Path) -> None:
    # Cardinal-error guard: no hot spots -> no inference-layer declaration (it must
    # never attach to an empty report; only a produced ranking is re-interpreted).
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=None)
    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["runtime_hotspots"] == []
    assert "interpretation" not in payload
    assert not any("runtime interpretation" in line for line in payload["markdown_lines"])

    reference = (
        ROOT
        / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")
    assert "render_runtime_summary.py" in reference


def test_render_runtime_summary_reports_missing_structured_signals(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(tmp_path, budgets={"pytest": 22000}, signals=None)

    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    assert (
        "- runtime source: not configured; add structured timing capture "
        "(or a `command_timing_log` adapter key) before reporting timing trends."
        in result.stdout
    )
    assert "runtime_visibility_missing_startup_probes" in result.stdout
    assert "10s" not in result.stdout


def test_render_runtime_summary_escalates_empty_runtime_visibility(tmp_path: Path) -> None:
    repo = seed_runtime_budget_repo(tmp_path, budgets=None, signals=None)

    result = run_script(RENDER_SCRIPT, "--repo-root", str(repo), "--detail", "--runtime-profile", "default")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert [finding["type"] for finding in payload["runtime_visibility_findings"]] == [
        "runtime_visibility_missing_budgets",
        "runtime_visibility_missing_startup_probes",
    ]
    assert payload["markdown_lines"][2].startswith(
        "- runtime visibility: weak due to `runtime_visibility_missing_budgets`, "
        "`runtime_visibility_missing_startup_probes`;"
    )
