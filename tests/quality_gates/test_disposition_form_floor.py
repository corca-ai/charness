"""Tests for the #329 disposition-form floor (shared grammar + both wirings).

Loads the shared grammar (``scripts/disposition_form.py``), the achieve gate
(``goal_artifact_disposition.py`` + the ``check_complete_evidence`` wrapper), and
the session-retro validator directly so no production re-export line is added.
"""
from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _ROOT / "scripts"
_ACHIEVE = _ROOT / "skills/public/achieve/scripts"


def _load(name: str, base: Path):
    spec = importlib.util.spec_from_file_location(name, base / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


df = _load("disposition_form", _SCRIPTS)
disp = _load("goal_artifact_disposition", _ACHIEVE)
ce = _load("goal_artifact_closeout_evidence", _ACHIEVE)
vra = _load("validate_retro_artifact", _SCRIPTS)


# --- grammar: the three valid forms pass (form only) -----------------------


def test_applied_form_passes_including_vague() -> None:
    for value in ("applied: shipped a gate", "applied: tweak", "applied — folded it", "applied changes above cover all"):
        assert df.evaluate_disposition_form(value)["kind"] == "applied"
    # vague-but-valid passes — proves this is NOT a content classifier
    assert df.evaluate_disposition_form("applied: tweak")["ok"] is True


def test_issue_form_passes_singular_plural_and_markdown() -> None:
    for value in ("issue #329", "issues #295 and #296", "**issue #307** (quality)", "issue -> filed as #331", "#328"):
        verdict = df.evaluate_disposition_form(value)
        assert verdict["kind"] == "issue", value
        assert verdict["ok"] is True


def test_none_form_requires_separator_and_reason() -> None:
    assert df.evaluate_disposition_form("none — nothing actionable surfaced")["kind"] == "none"
    assert df.evaluate_disposition_form("none - hyphen reason")["kind"] == "none"
    assert df.evaluate_disposition_form("none: colon reason")["kind"] == "none"


# --- grammar: the named-invalid prose-only / memory class is rejected -------


def test_bare_memory_and_prose_only_are_rejected() -> None:
    for value in (
        "memory",
        "memory -> recent-lessons digest refreshed this session",
        "memory + ESCALATE-IF-RECUR -> recent-lessons refreshed",
        "memory.",
        "deferred -> handoff Next Session candidate",
        "fix (folded)",
        "complete — three improvements surfaced",
        "candidate issue OR fold, not filed",
    ):
        verdict = df.evaluate_disposition_form(value)
        assert verdict["ok"] is False, value
        assert verdict["kind"] == "invalid", value


def test_degenerate_valid_prefixes_are_rejected() -> None:
    # `none` with no reason, `issue` with no number, empty value: all invalid.
    assert df.evaluate_disposition_form("none")["ok"] is False
    assert df.evaluate_disposition_form("none left as prose-only memory")["ok"] is False  # no separator
    assert df.evaluate_disposition_form("issue")["ok"] is False  # no #N
    assert df.evaluate_disposition_form("issues with the parser")["ok"] is False  # prose, no #N
    assert df.evaluate_disposition_form("   ")["ok"] is False


def test_none_compound_word_is_not_a_valid_none_form() -> None:
    # `none-actionable …` is a compound word, not a `none — <reason>` disposition
    # (fresh-eye Finding 2): the separator must not be a plain hyphen glued to `none`.
    assert df.evaluate_disposition_form("none-actionable items remain unfiled")["ok"] is False
    # whitespace-bearing hyphen / em-dash / colon still pass
    assert df.evaluate_disposition_form("none - real reason")["kind"] == "none"
    assert df.evaluate_disposition_form("none—real reason")["kind"] == "none"


def test_placeholder_values_are_skipped_not_failed() -> None:
    for value in ("TODO — disposition every surfaced improvement", "<reason>", "TBD", "FIXME later"):
        verdict = df.evaluate_disposition_form(value)
        assert verdict["kind"] == "placeholder"
        assert verdict["ok"] is True


# --- scan: marker extraction, fence masking, mid-line markers --------------


def test_scan_finds_both_markers_and_judges_each() -> None:
    body = (
        "- workflow: when a gate... false-negative. Disposition: memory -> recent-lessons\n"
        "- workflow: broaden coverage. Disposition: issue #331\n"
        "Retro dispositions: none — every lesson was captured upstream this run\n"
    )
    scanned = df.scan_dispositions(body)
    kinds = [entry["verdict"]["kind"] for entry in scanned]
    assert kinds == ["invalid", "issue", "none"]
    assert [e["verdict"]["ok"] for e in df.invalid_dispositions(body)] == [False]


def test_scan_masks_fenced_example_disposition_lines() -> None:
    body = "```\nDisposition: memory -> fenced example, not real\n```\nDisposition: applied: real one\n"
    scanned = df.scan_dispositions(body)
    assert len(scanned) == 1
    assert scanned[0]["verdict"]["kind"] == "applied"


def test_retro_dispositions_label_not_split_into_singular_marker() -> None:
    # `Retro dispositions:` must match as one aggregate marker, value judged whole.
    scanned = df.scan_dispositions("Retro dispositions: memory -> kept in head\n")
    assert len(scanned) == 1
    assert scanned[0]["marker"].lower().startswith("retro dispositions")
    assert scanned[0]["verdict"]["ok"] is False


# --- enforce-from-date (grandfathering, fail-closed) -----------------------


def test_is_form_enforced_grandfathers_through_today_and_fails_closed() -> None:
    assert df.is_form_enforced(date(2026, 6, 8)) is True  # rule date inclusive
    assert df.is_form_enforced(date(2026, 6, 9)) is True
    assert df.is_form_enforced(date(2026, 6, 7)) is False  # today: #330/#329/triggering retros grandfathered
    assert df.is_form_enforced(date(2026, 5, 30)) is False
    assert df.is_form_enforced(None) is True  # undatable -> fail-closed (in-scope)


# --- achieve wiring: form floor inside check_complete_evidence -------------

_SLUG = "329-form"


def _seed(tmp_path: Path, rel: str, body: str) -> Path:
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


def _seed_review(tmp_path: Path, created: str) -> str:
    name = f"{created}-{_SLUG}-disposition.md"
    _seed(tmp_path, f"charness-artifacts/critique/{name}", f"# Disposition review for {_SLUG}\n\n- ok\n")
    return f"Disposition review: charness-artifacts/critique/{name}"


def _seed_evidence(tmp_path: Path, created: str) -> None:
    _seed(tmp_path, f"charness-artifacts/retro/{created}-{_SLUG}.md", "# Retro\n\n## Next Improvements\n\n- workflow: do x\n")
    _seed(tmp_path, f"charness-artifacts/probe/{created}-{_SLUG}.json", '{"host":"claude-code"}\n')


def _build_goal(created: str, auto_retro_body: str, review_line: str = "") -> str:
    extra = f"{review_line}\n" if review_line else ""
    return (
        f"# Achieve Goal: T\n\nStatus: active\nCreated: {created}\n"
        f"Activation: `/goal @charness-artifacts/goals/{created}-{_SLUG}.md`\n\n"
        "## Final Verification\n\n"
        f"Retro: charness-artifacts/retro/{created}-{_SLUG}.md\n"
        f"Host log probe: charness-artifacts/probe/{created}-{_SLUG}.json\n{extra}\n"
        f"## Auto-Retro\n\n{auto_retro_body}\n"
    )


def test_achieve_form_floor_rejects_memory_disposition_in_scope(tmp_path: Path) -> None:
    created = "2026-06-08"  # in form scope
    _seed_evidence(tmp_path, created)
    review = _seed_review(tmp_path, created)
    body = "- improvement one. Disposition: memory -> kept in head\nRetro dispositions: applied: shipped the floor\n"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert report["ok"] is False
    assert "disposition_form" in report
    assert any("memory" in entry["value"] for entry in report["disposition_form"]["invalid"])


def test_achieve_form_floor_passes_valid_forms_in_scope(tmp_path: Path) -> None:
    created = "2026-06-08"
    _seed_evidence(tmp_path, created)
    review = _seed_review(tmp_path, created)
    body = "- one. Disposition: applied: shipped a gate\n- two. Disposition: issue #999\nRetro dispositions: none — the rest is non-actionable this run\n"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert "disposition_form" not in report
    assert report["ok"] is True


def test_achieve_form_floor_grandfathers_pre_date_goal(tmp_path: Path) -> None:
    created = "2026-06-07"  # day before the rule date -> grandfathered
    _seed_evidence(tmp_path, created)
    review = _seed_review(tmp_path, created)
    body = "- one. Disposition: memory -> kept in head\n"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert "disposition_form" not in report  # inert for grandfathered goals
    assert report["disposition_form_scope"]["enforced"] is False


def test_achieve_form_floor_ignores_dispositions_outside_auto_retro(tmp_path: Path) -> None:
    # A `Disposition:` line in another section (e.g. Sibling Search) is not judged.
    created = "2026-06-08"
    _seed_evidence(tmp_path, created)
    review = _seed_review(tmp_path, created)
    goal = (
        f"# Achieve Goal: T\n\nStatus: active\nCreated: {created}\n"
        f"Activation: `/goal @charness-artifacts/goals/{created}-{_SLUG}.md`\n\n"
        "## Sibling Search\n\n- axis: x | Disposition: memory -> not an improvement disposition\n\n"
        "## Final Verification\n\n"
        f"Retro: charness-artifacts/retro/{created}-{_SLUG}.md\n"
        f"Host log probe: charness-artifacts/probe/{created}-{_SLUG}.json\n{review}\n\n"
        "## Auto-Retro\n\nRetro dispositions: none — all surfaced lessons applied this run already\n"
    )
    report = ce.check_complete_evidence(tmp_path, goal)
    assert "disposition_form" not in report
    assert report["ok"] is True


def test_achieve_form_floor_skips_untouched_placeholder(tmp_path: Path) -> None:
    # The seeded `Retro dispositions: TODO …` placeholder is not a form violation
    # (block-the-blank rung 1a owns that case); isolate via a non-blank sibling line.
    created = "2026-06-08"
    _seed_evidence(tmp_path, created)
    review = _seed_review(tmp_path, created)
    body = (
        "- one. Disposition: applied: shipped it\n"
        "Retro dispositions: TODO — disposition every surfaced improvement, or record the opt-out\n"
    )
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert "disposition_form" not in report


# --- session-retro wiring --------------------------------------------------


def _retro(date_str: str, dispositions: str) -> str:
    return (
        f"# Retro — t\n\nDate: {date_str}\n\n## Context\n\nx\n\n"
        f"## Next Improvements\n\n{dispositions}\n\n## Persisted\n\nyes\n"
    )


def test_retro_validator_rejects_memory_disposition_in_scope(tmp_path: Path) -> None:
    path = _seed(tmp_path, "r.md", _retro("2026-06-08", "- workflow: do x. Disposition: memory -> kept in head\n"))
    raised = False
    try:
        vra.validate_retro_artifact(path)
    except vra.ValidationError as exc:
        raised = True
        assert "memory" in str(exc) or "form" in str(exc).lower()
    assert raised


def test_retro_validator_passes_valid_forms_in_scope(tmp_path: Path) -> None:
    path = _seed(
        tmp_path, "r.md",
        _retro("2026-06-08", "- a. Disposition: applied: shipped it\n- b. Disposition: issue #42\n"),
    )
    vra.validate_retro_artifact(path)  # no raise


def test_retro_validator_grandfathers_pre_date_retro(tmp_path: Path) -> None:
    path = _seed(tmp_path, "r.md", _retro("2026-06-07", "- a. Disposition: memory -> kept in head\n"))
    vra.validate_retro_artifact(path)  # grandfathered -> no raise


def _dateless_retro(dispositions: str) -> str:
    # No `Date:` header (the convention many frozen historical retros predate).
    return f"# Retro — t\n\n## Context\n\nx\n\n## Next Improvements\n\n{dispositions}\n\n## Persisted\n\nyes\n"


def test_retro_validator_grandfathers_dateless_retro_by_filename(tmp_path: Path) -> None:
    # Fresh-eye Finding 1: a dateless frozen retro is grandfathered by its
    # filename date (not fail-closed into retroactive enforcement).
    path = _seed(tmp_path, "2026-06-07-old-retro.md", _dateless_retro("- a. Disposition: memory -> kept in head\n"))
    vra.validate_retro_artifact(path)  # filename date 2026-06-07 -> grandfathered, no raise


def test_retro_validator_enforces_dateless_in_scope_filename(tmp_path: Path) -> None:
    path = _seed(tmp_path, "2026-06-09-new-retro.md", _dateless_retro("- a. Disposition: memory -> kept in head\n"))
    raised = False
    try:
        vra.validate_retro_artifact(path)
    except vra.ValidationError:
        raised = True
    assert raised  # dateless body but in-scope filename -> enforced (no dodge)
