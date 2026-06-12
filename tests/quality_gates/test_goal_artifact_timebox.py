from __future__ import annotations

import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path

_LIB = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts/goal_artifact_lib.py"
_spec = importlib.util.spec_from_file_location("goal_artifact_lib", _LIB)
gal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gal)


def _goal_text(tmp_path: Path, slug: str = "g", date: str = "2026-05-28") -> str:
    path = gal.goal_path(tmp_path, date, slug)
    return path.read_text(encoding="utf-8")


def _append_evidence_lines(text: str, retro_value: str, probe_value: str) -> str:
    return text.replace(
        "## Final Verification\n",
        f"## Final Verification\n\nRetro: {retro_value}\nHost log probe: {probe_value}\n",
        1,
    )


def _fill_auto_retro_first_line(text: str) -> str:
    return text.replace(
        "Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out",
        "Retro dispositions: none — no actionable improvement surfaced during this run",
        1,
    )


def _seed_bound_report(tmp_path: Path, slug: str = "g") -> Path:
    report = tmp_path / "charness-artifacts/goals" / f"2026-05-28-{slug}-early-close-report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        f"# Early Close Report for {slug}\n\n"
        "## Why It Ended Early\n\nRemaining slices require a separate decision boundary.\n\n"
        "## User Decisions Needed\n\n- Choose whether to expand scope or defer the candidate.\n\n"
        "## Waste Retro\n\n- Candidate review must be explicit before closing early.\n",
        encoding="utf-8",
    )
    return report


def _seed_closeout_lines(tmp_path: Path, slug: str = "g") -> str:
    retro = tmp_path / "charness-artifacts/retro" / f"2026-05-28-{slug}.md"
    probe = tmp_path / "charness-artifacts/probe" / f"2026-05-28-{slug}.json"
    retro.parent.mkdir(parents=True, exist_ok=True)
    probe.parent.mkdir(parents=True, exist_ok=True)
    retro.write_text(f"# Retro for {slug}\n\nbody\n", encoding="utf-8")
    probe.write_text(f'{{"goal":"{slug}"}}\n', encoding="utf-8")
    report = _seed_bound_report(tmp_path, slug)
    return (
        f"Retro: {retro.relative_to(tmp_path)}\n"
        f"Host log probe: {probe.relative_to(tmp_path)}\n"
        f"Early close report: {report.relative_to(tmp_path)}\n"
    )


def _early_activation() -> str:
    value = datetime.now(timezone.utc) - timedelta(hours=1)
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def _add_timebox(
    text: str,
    *,
    activation_time: str,
    timebox: str = "3h",
    reserve: str = "20m",
    extra: str = "",
    policy: str = "continue_next_improvement",
) -> str:
    lines = (
        f"Timebox: {timebox}\nActivation time: {activation_time}\n"
        f"Closeout reserve: {reserve}\nDone-early policy: {policy}\n"
    )
    if extra:
        lines += extra.rstrip() + "\n"
    return text.replace("## Active Operating Frame\n", f"## Active Operating Frame\n\n{lines}", 1)


def test_check_timebox_blocks_early_close_without_next_slice_decision() -> None:
    text = _add_timebox(
        "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n## Active Operating Frame\n",
        activation_time="2026-06-05T00:00:00Z",
    )
    report = gal.check_timebox_closeout(
        text,
        now=datetime(2026, 6, 5, 1, 0, tzinfo=timezone.utc),
    )
    assert report["ok"] is False
    assert report["status"] == "early_close_blocked"
    assert report["closeout_window_started"] == "2026-06-05T02:40:00Z"


def test_check_timebox_rejects_one_line_early_close_without_candidate_ledger() -> None:
    text = (
        _add_timebox(
            "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n"
            "## Active Operating Frame\n\n## Final Verification\n",
            activation_time="2026-06-05T00:00:00Z",
        )
        + "No safe next slice: only unsafe release work remains and user confirmation is required first.\n"
    )
    report = gal.check_timebox_closeout(
        text,
        now=datetime(2026, 6, 5, 1, 0, tzinfo=timezone.utc),
    )
    assert report["ok"] is False
    assert report["status"] == "early_close_blocked"
    assert "Next slice candidate" in report["issues"][0]


def test_check_timebox_allows_early_close_with_candidate_ledger_and_sufficiency_check() -> None:
    text = (
        _add_timebox(
            "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n"
            "## Active Operating Frame\n\n## Final Verification\n",
            activation_time="2026-06-05T00:00:00Z",
        )
        + "Early close rationale: remaining candidates need user confirmation or a separate design boundary.\n"
        + (
            "Next slice candidate: release push | decision: user-decision | reason: "
            "external publish approval is explicitly outside the current local timebox.\n"
        )
        + (
            "Next slice candidate: resolver commonization | decision: defer | reason: "
            "public skill export safety needs a separate design slice before mutation.\n"
        )
        + (
            "Outcome sufficiency check: accepted-low-yield: current run landed the safe "
            "local slices, and the remaining work is intentionally deferred.\n"
        )
    )
    report = gal.check_timebox_closeout(
        text,
        now=datetime(2026, 6, 5, 1, 0, tzinfo=timezone.utc),
    )
    assert report["ok"] is True
    assert report["status"] == "early_close_with_evidence"
    assert report["evidence"] == "early_close_rationale"
    assert report["early_close_readiness"]["candidate_ledger"]["count"] == 2
    assert report["early_close_readiness"]["outcome_sufficiency"]["status"] == "accepted-low-yield"


def test_check_timebox_rejects_duplicate_candidate_names() -> None:
    text = (
        _add_timebox(
            "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n"
            "## Active Operating Frame\n\n## Final Verification\n",
            activation_time="2026-06-05T00:00:00Z",
        )
        + "Early close rationale: remaining candidates need user confirmation or a separate design boundary.\n"
        + (
            "Next slice candidate: resolver commonization | decision: defer | reason: "
            "public skill export safety needs a separate design slice before mutation.\n"
        )
        + (
            "Next slice candidate: Resolver   Commonization | decision: defer | reason: "
            "the same candidate repeated with spacing cannot prove a second reviewed option.\n"
        )
        + (
            "Outcome sufficiency check: accepted-low-yield: current run landed the safe "
            "local slices, and the remaining work is intentionally deferred.\n"
        )
    )
    report = gal.check_timebox_closeout(
        text,
        now=datetime(2026, 6, 5, 1, 0, tzinfo=timezone.utc),
    )
    assert report["ok"] is False
    assert report["early_close_readiness"]["candidate_ledger"]["distinct_count"] == 1
    assert "distinct `Next slice candidate:`" in report["issues"][0]


def test_check_timebox_ignores_planned_stop_condition_outside_final_verification() -> None:
    text = _add_timebox(
        "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n## Active Operating Frame\n",
        activation_time="2026-06-05T00:00:00Z",
        extra="Stop condition: blocked - only unsafe release work remains and user confirmation is required first.",
    )
    report = gal.check_timebox_closeout(
        text,
        now=datetime(2026, 6, 5, 1, 0, tzinfo=timezone.utc),
    )
    assert report["ok"] is False
    assert report["status"] == "early_close_blocked"


def test_check_timebox_allows_closeout_window() -> None:
    text = _add_timebox(
        "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n## Active Operating Frame\n",
        activation_time="2026-06-05T00:00:00Z",
    )
    report = gal.check_timebox_closeout(
        text,
        now=datetime(2026, 6, 5, 2, 45, tzinfo=timezone.utc),
    )
    assert report["ok"] is True
    assert report["status"] == "ready"


def test_check_timebox_rejects_reserve_not_shorter_than_timebox() -> None:
    text = _add_timebox(
        "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n## Active Operating Frame\n",
        activation_time="2026-06-05T00:00:00Z",
        timebox="15m",
        reserve="20m",
    )
    report = gal.check_timebox_closeout(
        text,
        now=datetime(2026, 6, 5, 0, 1, tzinfo=timezone.utc),
    )
    assert report["ok"] is False
    assert any("`Closeout reserve:` must be shorter" in issue for issue in report["issues"])


def test_check_timebox_rejects_annotated_duration() -> None:
    text = _add_timebox(
        "# Achieve Goal: T\n\nStatus: active\nActivation: `/goal @x`\n\n## Active Operating Frame\n",
        activation_time="2026-06-05T00:00:00Z",
        timebox="3h (180m)",
    )
    report = gal.check_timebox_closeout(text)
    assert report["ok"] is False
    assert "invalid `Timebox:` duration" in report["issues"]


def test_upsert_refuses_timebox_complete_before_closeout_window(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug="g", title="T")
    text = _goal_text(tmp_path)
    text = _add_timebox(text, activation_time=_early_activation())
    text = text.replace(
        "## Final Verification\n",
        "## Final Verification\n\n"
        "No safe next slice: only unsafe release work remains and user confirmation is required first.\n"
        f"{_seed_closeout_lines(tmp_path)}",
        1,
    )
    text = _fill_auto_retro_first_line(text)
    gal.goal_path(tmp_path, "2026-05-28", "g").write_text(text, encoding="utf-8")
    refusal = gal.upsert_goal(
        tmp_path, date="2026-05-28", slug="g", title="T", status="complete"
    )
    assert refusal["action"] == "refused"
    assert refusal["timebox_report"]["ok"] is False
    assert refusal["evidence_report"]["ok"] is True
    assert "Next slice candidate" in refusal["timebox_report"]["issues"][0]
    assert "Status: complete" not in _goal_text(tmp_path)


def test_upsert_allows_timebox_complete_before_closeout_window_with_full_ledger(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug="g", title="T")
    text = _goal_text(tmp_path)
    text = _add_timebox(text, activation_time=_early_activation())
    text = text.replace(
        "## Final Verification\n",
        "## Final Verification\n\n"
        "Early close rationale: remaining candidates need user confirmation or a separate design boundary.\n"
        "Next slice candidate: release push | decision: user-decision | reason: external publish approval is explicitly outside the current local timebox.\n"
        "Next slice candidate: resolver commonization | decision: defer | reason: public skill export safety needs a separate design slice before mutation.\n"
        "Outcome sufficiency check: accepted-low-yield: current run landed the safe local slices, and the remaining work is intentionally deferred.\n"
        f"{_seed_closeout_lines(tmp_path)}",
        1,
    )
    text = _fill_auto_retro_first_line(text)
    gal.goal_path(tmp_path, "2026-05-28", "g").write_text(text, encoding="utf-8")

    result = gal.upsert_goal(
        tmp_path, date="2026-05-28", slug="g", title="T", status="complete"
    )

    assert result["action"] in ("updated", "unchanged")
    assert result["status"] == "complete"
    assert "Status: complete" in _goal_text(tmp_path)


def test_upsert_allows_timebox_complete_after_deadline(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-28", slug="g", title="T")
    skip_line = "skipped: host-log-not-exposed: claude jsonl path missing on this host"
    text = _goal_text(tmp_path)
    text = _append_evidence_lines(text, retro_value=skip_line, probe_value=skip_line)
    text = _add_timebox(text, activation_time="2000-01-01T00:00:00Z")
    text = _fill_auto_retro_first_line(text)
    gal.goal_path(tmp_path, "2026-05-28", "g").write_text(text, encoding="utf-8")
    result = gal.upsert_goal(
        tmp_path, date="2026-05-28", slug="g", title="T", status="complete"
    )
    assert result["action"] in ("updated", "unchanged")
    assert result["status"] == "complete"
