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
    # issue-form dispositions in-scope must also carry a recurrence-lineage marker
    # (rung 1d); a bare `issue #999` would now block (see the rung-1d tests below).
    body = (
        "- one. Disposition: applied: shipped a gate\n"
        "- two. Disposition: issue #999 (novel: first occurrence of this class)\n"
        "Retro dispositions: none — the rest is non-actionable this run\n"
    )
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert "disposition_form" not in report
    assert "recurrence_lineage" not in report
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


# --- rung 1d: recurrence-lineage floor (de-launder the issue escape) --------


def test_recurrence_lineage_grammar_presence_only() -> None:
    # presence/enum only: a marker + colon + non-empty content; correctness unjudged.
    for value in (
        "issue #335 (novel: first occurrence, searched the lineage)",
        "issue #335 (recurs: #284 -> #308 -> #334)",
        "issue #335 — recurrence: same class as #284",
        "issue #335 lineage: prior #329",
    ):
        assert df.has_recurrence_lineage(value) is True, value
    # a bare issue, or prose "novel" without the colon marker, is NOT lineage.
    for value in ("issue #335", "issue #335 a novel approach to caching", "issue #335 (filed)"):
        assert df.has_recurrence_lineage(value) is False, value
    # vague-but-present passes — proves this is NOT a content classifier.
    assert df.has_recurrence_lineage("issue #1 (novel: x)") is True


def test_achieve_lineage_floor_blocks_bare_issue_in_scope(tmp_path: Path) -> None:
    created = "2026-06-08"  # in lineage scope
    _seed_evidence(tmp_path, created)
    review = _seed_review(tmp_path, created)
    body = "- one. Disposition: issue #335\nRetro dispositions: applied: shipped the floor\n"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert report["ok"] is False
    assert "recurrence_lineage" in report
    assert any("#335" in entry["value"] for entry in report["recurrence_lineage"]["missing"])


def test_achieve_lineage_floor_passes_with_marker(tmp_path: Path) -> None:
    created = "2026-06-08"
    _seed_evidence(tmp_path, created)
    review = _seed_review(tmp_path, created)
    for marker in ("novel: distinct, searched the lineage", "recurs: #284 -> #334"):
        body = f"- one. Disposition: issue #335 ({marker})\nRetro dispositions: applied: shipped it\n"
        report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
        assert "recurrence_lineage" not in report, marker


def test_achieve_lineage_floor_exempts_non_issue_forms(tmp_path: Path) -> None:
    # applied:/none — dispositions never need a lineage marker (only issue does).
    created = "2026-06-08"
    _seed_evidence(tmp_path, created)
    review = _seed_review(tmp_path, created)
    body = "- one. Disposition: applied: shipped a gate\nRetro dispositions: none — nothing else actionable this run\n"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert "recurrence_lineage" not in report
    assert report["ok"] is True


def test_achieve_lineage_floor_grandfathers_pre_date_goal(tmp_path: Path) -> None:
    created = "2026-06-07"  # day before the lineage rule date -> grandfathered
    _seed_evidence(tmp_path, created)
    review = _seed_review(tmp_path, created)
    body = "- one. Disposition: issue #335\nRetro dispositions: applied: shipped it\n"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert "recurrence_lineage" not in report  # inert for grandfathered goals
    assert report["recurrence_lineage_scope"]["enforced"] is False


def test_lineage_floor_does_not_leak_into_retro_validator(tmp_path: Path) -> None:
    # Behavior-preservation: the recurrence-lineage rule is achieve-only. A session
    # retro with a bare `issue #N` disposition (no lineage marker) stays VALID under
    # the retro validator, because it calls only is_form_enforced/invalid_dispositions
    # and never has_recurrence_lineage. The shared-module addition is purely additive.
    path = _seed(tmp_path, "r.md", _retro("2026-06-08", "- a. Disposition: issue #42\n"))
    vra.validate_retro_artifact(path)  # no raise — retro unchanged by the addition


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


# --- standalone-retro recurrence-lineage floor (de-launder extension) -------


def test_retro_lineage_floor_blocks_bare_issue_in_scope(tmp_path: Path) -> None:
    # a retro dated on/after the lineage rule date with an issue-form Next
    # Improvement disposition lacking a lineage marker is blocked.
    path = _seed(tmp_path, "r.md", _retro("2026-06-09", "- workflow: x. Disposition: issue #500\n"))
    raised = False
    try:
        vra.validate_retro_artifact(path)
    except vra.ValidationError as exc:
        raised = True
        assert "lineage" in str(exc).lower() or "recurs" in str(exc).lower()
    assert raised


def test_retro_lineage_floor_passes_with_marker_and_exempts_non_issue(tmp_path: Path) -> None:
    for disp in (
        "issue #500 (novel: first occurrence, searched the lineage)",
        "issue #500 (recurs: #284 -> #334)",
        "applied: shipped it",
        "none — nothing else actionable this run",
    ):
        path = _seed(tmp_path, "r.md", _retro("2026-06-09", f"- workflow: x. Disposition: {disp}\n"))
        vra.validate_retro_artifact(path)  # no raise


def test_retro_lineage_floor_grandfathers_pre_date_retro(tmp_path: Path) -> None:
    # all existing retros are dated on/before the landing day -> grandfathered, so
    # a bare issue disposition on a 2026-06-08 retro stays valid (broad-gate-safe).
    path = _seed(tmp_path, "r.md", _retro("2026-06-08", "- workflow: x. Disposition: issue #500\n"))
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


# --- #337: structural-follow-up destination floor (rung 1e) -----------------
# Grammar: the four destination forms, including `repo-local guard: <path>`.


def test_destination_form_accepts_the_four_forms_including_repo_local_guard() -> None:
    assert df.evaluate_destination_form("applied: shipped a validator")["kind"] == "applied"
    assert df.evaluate_destination_form("issue #337 (novel: first occurrence)")["kind"] == "issue"
    assert df.evaluate_destination_form("none — no structural follow-up; lesson is one-off")["kind"] == "none"
    for value in ("repo-local guard: skills/x/AGENTS.md", "repo-local guard - .agents/issue-adapter.yaml"):
        verdict = df.evaluate_destination_form(value)
        assert verdict["kind"] == "repo-local-guard", value
        assert verdict["ok"] is True
    # vague-but-valid passes — proves this is NOT a content classifier
    assert df.evaluate_destination_form("applied: tweak")["ok"] is True


def test_destination_form_rejects_memory_and_skips_placeholder() -> None:
    for value in ("memory -> recent-lessons digest refreshed", "recorded in recent-lessons", "repo-local guard"):
        assert df.evaluate_destination_form(value)["ok"] is False, value
    assert df.evaluate_destination_form("TODO — classify the destination")["kind"] == "placeholder"
    assert df.evaluate_destination_form("   ")["ok"] is False


def test_scan_destinations_finds_marker_variants_and_masks_fences() -> None:
    body = (
        "Structural follow-up: applied: shipped the floor this run\n"
        "Structural followup: issue #337 (recurs: #329 -> #330)\n"
        "```\nStructural follow-up: memory -> fenced example, not real\n```\n"
    )
    scanned = df.scan_destinations(body)
    assert [e["verdict"]["kind"] for e in scanned] == ["applied", "issue"]  # fenced line inert


# Trigger detection: a transferable-waste `## Sibling Search` vs the n/a short-circuit.


def test_names_transferable_waste_true_only_for_real_decision_bullets() -> None:
    transferable = (
        "# Retro\n\n## Sibling Search\n\n"
        "- same layer: scripts/x.py | decision: same waste, fix now | proof: grep\n"
    )
    assert df.names_transferable_waste(transferable) is True
    short_circuit = "# Retro\n\n## Sibling Search\n\n- n/a — trivial fix; no plausible siblings\n"
    assert df.names_transferable_waste(short_circuit) is False
    assert df.names_transferable_waste("# Retro\n\n## Next Improvements\n\n- do x\n") is False  # absent
    fenced = "# Retro\n\n```\n## Sibling Search\n\n- a | decision: x\n```\n"
    assert df.names_transferable_waste(fenced) is False  # fenced section inert


def test_evaluate_structural_followup_problem_states() -> None:
    assert df.evaluate_structural_followup("Retro dispositions: applied: x\n")["problem"] == "missing"
    assert df.evaluate_structural_followup("Structural follow-up: memory -> kept in head\n")["problem"] == "invalid"
    assert df.evaluate_structural_followup("Structural follow-up: none — one-off, no owner\n")["problem"] is None


def test_structural_followup_rule_date_grandfathers_landing_day() -> None:
    assert df.STRUCTURAL_FOLLOWUP_RULE_DATE == date(2026, 6, 9)


# --- achieve wiring: rung 1e inside check_complete_evidence -----------------


def _seed_transferable(tmp_path: Path, created: str) -> None:
    # A retro that names a transferable waste item (real `## Sibling Search` bullet).
    _seed(
        tmp_path,
        f"charness-artifacts/retro/{created}-{_SLUG}.md",
        "# Retro\n\n## Next Improvements\n\n- workflow: do x\n\n## Sibling Search\n\n"
        "- same layer: skills/y.py | decision: valid follow-up outside the slice "
        "| proof: grep\n  follow-up: deferred docs/handoff.md\n",
    )
    _seed(tmp_path, f"charness-artifacts/probe/{created}-{_SLUG}.json", '{"host":"claude-code"}\n')


def test_rung1e_blocks_transferable_waste_without_destination(tmp_path: Path) -> None:
    created = "2026-06-09"  # in structural-follow-up scope
    _seed_transferable(tmp_path, created)
    review = _seed_review(tmp_path, created)
    body = "Retro dispositions: applied: shipped the destination floor this run\n"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert report["structural_followup_scope"]["transferable_waste_named"] is True
    assert report["structural_followup"]["problem"] == "missing"
    assert report["ok"] is False


def test_rung1e_blocks_invalid_destination_form(tmp_path: Path) -> None:
    created = "2026-06-09"
    _seed_transferable(tmp_path, created)
    review = _seed_review(tmp_path, created)
    body = (
        "Retro dispositions: applied: shipped the destination floor this run\n"
        "Structural follow-up: memory -> recorded in recent-lessons\n"
    )
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert report["structural_followup"]["problem"] == "invalid"
    assert report["ok"] is False


def test_rung1e_passes_with_valid_destination(tmp_path: Path) -> None:
    created = "2026-06-09"
    _seed_transferable(tmp_path, created)
    review = _seed_review(tmp_path, created)
    for destination in (
        "applied: shipped the destination floor this run",
        "issue #337 (recurs: #329 -> #330)",
        "repo-local guard: skills/x/AGENTS.md",
        "none — one-off waste this run, no structural owner",
    ):
        body = (
            "Retro dispositions: applied: shipped the destination floor this run\n"
            f"Structural follow-up: {destination}\n"
        )
        report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
        assert "structural_followup" not in report, destination
        assert report["ok"] is True, destination


def test_rung1e_grandfathers_pre_rule_goal(tmp_path: Path) -> None:
    created = "2026-06-08"  # day before the rule date -> grandfathered
    _seed_transferable(tmp_path, created)
    review = _seed_review(tmp_path, created)
    body = "Retro dispositions: applied: shipped it; the transferable waste has no destination line\n"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert report["structural_followup_scope"]["enforced"] is False
    assert "structural_followup" not in report  # inert for grandfathered goals


def test_rung1e_does_not_over_fire_without_transferable_waste(tmp_path: Path) -> None:
    # In scope, but the retro names no transferable waste (no `## Sibling Search`):
    # the floor must NOT force a destination line.
    created = "2026-06-09"
    _seed_evidence(tmp_path, created)  # retro has Next Improvements but no Sibling Search
    review = _seed_review(tmp_path, created)
    body = "Retro dispositions: applied: shipped the destination floor this run\n"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, body, review))
    assert report["structural_followup_scope"]["transferable_waste_named"] is False
    assert "structural_followup" not in report
    assert report["ok"] is True


def test_rung1e_does_not_leak_into_retro_validator(tmp_path: Path) -> None:
    # Behavior-preservation: the destination floor is achieve-only. A session retro
    # that names transferable waste but records no `Structural follow-up:` line stays
    # VALID under the retro validator (it never calls the new destination helpers).
    body = (
        "# Retro — t\n\nDate: 2026-06-09\n\n## Context\n\nx\n\n## Next Improvements\n\n"
        "- workflow: do x. Disposition: applied: shipped it\n\n## Sibling Search\n\n"
        "- same layer: skills/y.py | decision: valid follow-up outside the slice | proof: grep\n"
        "  follow-up: deferred docs/handoff.md\n\n## Persisted\n\nyes\n"
    )
    path = _seed(tmp_path, "2026-06-09-r.md", body)
    vra.validate_retro_artifact(path)  # no raise — retro unchanged by the addition
