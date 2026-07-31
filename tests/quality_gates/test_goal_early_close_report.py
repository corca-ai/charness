"""Tests for the achieve early-close report evidence floor."""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts"
_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ce = _load("goal_artifact_closeout_evidence")


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    """Assert each fragment belongs to its option block, not only usage text."""
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_early_close_report_help_describes_options() -> None:
    result = subprocess.run(
        [sys.executable, str(_SCRIPTS / "goal_artifact_early_close_report.py"), "--help"],
        cwd=_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    _assert_help_pairs(
        result.stdout,
        {
            "--repo-root": "Repo root accepted for the preflight scaffold contract.",
            "--slug": "Goal slug used in the report heading.",
        },
    )


def _seed_required_evidence(tmp_path: Path, slug: str) -> str:
    retro = tmp_path / "charness-artifacts/retro" / f"2026-05-28-{slug}.md"
    probe = tmp_path / "charness-artifacts/probe" / f"2026-05-28-{slug}.json"
    retro.parent.mkdir(parents=True, exist_ok=True)
    probe.parent.mkdir(parents=True, exist_ok=True)
    # Non-degenerate on purpose. A 12-byte `{"goal":"g"}` probe is a STUB by
    # any measure, and the closeout gate now refuses one: real host-log probes
    # in this repo floor at 923 bytes / 530 residual characters, and real
    # markdown artifacts at 337, so fixture minimalism was standing in for
    # evidence minimalism. The assertions below are unchanged.
    retro.write_text(
        f"# Retro for {slug}\n\n"
        "## What Happened\n\nThe slice landed and its proof ran to green.\n\n"
        "## What To Change\n\nNothing outstanding for this fixture.\n",
        encoding="utf-8",
    )
    probe.write_text(
        '{"goal": "' + slug + '", "host": "claude-code", "surface": "session-log",'
        ' "observed": ["slice-start", "slice-end"], "verdict": "probed"}\n',
        encoding="utf-8",
    )
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


cga = _load("check_goal_artifact")


def test_hollow_report_names_the_section_in_cli_message(tmp_path: Path) -> None:
    # The complete-flip refusal for a hollow early-close report must NAME the hollow
    # section in the human-facing CLI tail. Before the reader fix, `apply_report_shape`
    # set ok=False but `_evidence_missing_bits` had no branch for it, so a hollow
    # report as the sole failure printed a dangling "…evidence not satisfied — " with
    # no reason and forced the author to reverse-engineer it from raw JSON.
    report_path = tmp_path / "charness-artifacts/goals" / "2026-05-28-g-early-close-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    # The realistic false-green case: all three headings present (looks well-formed),
    # but one section body is terse (`None.`) -> `required section body is hollow`.
    report_path.write_text(
        "# Early Close Report — g\n\n"
        "## Why early closeout was chosen\n\nNo safe next slice remained; only unsafe work was left.\n\n"
        "## What user decisions are needed\n\nWhether to push or defer the carrier commit.\n\n"
        "## Waste and retro\n\nNone.\n",
        encoding="utf-8",
    )
    report = ce.check_complete_evidence(
        tmp_path,
        _goal(
            tmp_path,
            include_report=False,
            report_line=f"Early close report: {report_path.relative_to(tmp_path)}\n",
        ),
    )
    assert report["ok"] is False
    joined = "; ".join(cga._evidence_missing_bits(report))
    assert "early-close report shape" in joined and "waste_retro" in joined and "hollow" in joined
    assert joined.strip()  # never a dangling em-dash tail
