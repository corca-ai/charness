"""Tests for the achieve early-close report evidence floor."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ce = _load("goal_artifact_closeout_evidence")


def _seed_required_evidence(tmp_path: Path, slug: str) -> str:
    retro = tmp_path / "charness-artifacts/retro" / f"2026-05-28-{slug}.md"
    probe = tmp_path / "charness-artifacts/probe" / f"2026-05-28-{slug}.json"
    retro.parent.mkdir(parents=True, exist_ok=True)
    probe.parent.mkdir(parents=True, exist_ok=True)
    retro.write_text(f"# Retro for {slug}\n\nbody\n", encoding="utf-8")
    probe.write_text(f'{{"goal":"{slug}"}}\n', encoding="utf-8")
    return (
        f"Retro: {retro.relative_to(tmp_path)}\n"
        f"Host log probe: {probe.relative_to(tmp_path)}\n"
    )


def _goal(
    tmp_path: Path,
    *,
    include_report: bool,
    reason: str | None = None,
    report_line: str | None = None,
) -> str:
    slug = "g"
    evidence_line = ""
    if include_report:
        report = tmp_path / "charness-artifacts/goals" / "2026-05-28-g-early-close-report.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            "# Early Close Report for g\n\n"
            "## Why It Ended Early\n\nNo safe next slice remained for the goal.\n\n"
            "## User Decisions Needed\n\n- Push or defer the carrier commit.\n\n"
            "## Waste Retro\n\n- Late report transport was the gap.\n",
            encoding="utf-8",
        )
        evidence_line = f"Early close report: {report.relative_to(tmp_path)}\n"
    if report_line is not None:
        evidence_line = report_line
    reason_line = reason or "No safe next slice: only unsafe release work remains and user confirmation is required first."
    return (
        "# Achieve Goal: T\n\n"
        "Status: active\nCreated: 2026-05-28\n"
        "Activation: `/goal @charness-artifacts/goals/2026-05-28-g.md`\n\n"
        "## Final Verification\n\n"
        f"{reason_line}\n"
        f"{_seed_required_evidence(tmp_path, slug)}"
        f"{evidence_line}"
        "\n## Auto-Retro\n\napplied: no deferred report gap remains\n"
    )


def test_early_close_reason_requires_bound_report(tmp_path: Path) -> None:
    report = ce.check_complete_evidence(tmp_path, _goal(tmp_path, include_report=False))
    assert report["ok"] is False
    assert "early_close_report" in report["missing"]


def test_bound_early_close_report_satisfies_floor(tmp_path: Path) -> None:
    report = ce.check_complete_evidence(tmp_path, _goal(tmp_path, include_report=True))
    assert report["ok"] is True
    assert any(entry["name"] == "early_close_report" for entry in report["satisfied"])
    assert report["invalid_early_close_reports"] == []


def test_hollow_early_close_report_is_invalid(tmp_path: Path) -> None:
    report_path = tmp_path / "charness-artifacts/goals" / "2026-05-28-g-early-close-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# Early Close Report for g\n\none line only\n", encoding="utf-8")

    report = ce.check_complete_evidence(
        tmp_path,
        _goal(
            tmp_path,
            include_report=False,
            report_line=f"Early close report: {report_path.relative_to(tmp_path)}\n",
        ),
    )

    assert report["ok"] is False
    assert report["invalid_early_close_reports"]


def test_early_close_report_skip_is_invalid(tmp_path: Path) -> None:
    report = ce.check_complete_evidence(
        tmp_path,
        _goal(
            tmp_path,
            include_report=False,
            report_line="Early close report: skipped: host-log-not-exposed: report writing is still possible\n",
        ),
    )
    assert report["ok"] is False
    assert any(entry["name"] == "early_close_report" for entry in report["invalid_skips"])


def test_supported_stop_condition_requires_early_close_report(tmp_path: Path) -> None:
    report = ce.check_complete_evidence(
        tmp_path,
        _goal(
            tmp_path,
            include_report=False,
            reason="Stop condition: blocked - only unsafe release work remains and user confirmation is required first.",
        ),
    )
    assert report["ok"] is False
    assert "early_close_report" in report["missing"]


# #335: the author-time stub the preflight surfaces must satisfy this floor's own
# validator by construction, so an author starting from it cannot fail the flip on
# shape. Round-trip: report_stub() -> validate_report_shape() == [].
ecr = _load("goal_artifact_early_close_report")


def test_report_stub_round_trips_validate_report_shape(tmp_path: Path) -> None:
    report = tmp_path / "early-close.md"
    report.write_text(ecr.report_stub("demo-goal"), encoding="utf-8")
    assert ecr.validate_report_shape(report) == []
    text = report.read_text(encoding="utf-8")
    assert "# Early Close Report — demo-goal" in text
    assert "## Why early closeout was chosen" in text
    assert "## What user decisions are needed" in text
    assert "## Waste and retro" in text


def test_report_stub_cli_prints_stub(capsys, monkeypatch) -> None:
    import sys

    monkeypatch.setattr(sys, "argv", ["x", "--repo-root", ".", "--slug", "cli-goal"])
    assert ecr.main() == 0
    out = capsys.readouterr().out
    assert "# Early Close Report — cli-goal" in out
    assert "## Waste and retro" in out
