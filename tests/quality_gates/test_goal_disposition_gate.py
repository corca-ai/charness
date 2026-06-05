"""Tests for the #253 improvement-disposition closeout gate.

Loads ``goal_artifact_disposition.py`` (the deterministic rung) and
``goal_artifact_closeout_evidence.py`` (the wrapper that calls it) **directly**
so the achieve lib gains zero new re-export lines (it sits at 358/360; a new
re-export would hard-fail the single-file gate — goal Boundary "Home + export
budget").
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


disp = _load("goal_artifact_disposition")
ce = _load("goal_artifact_closeout_evidence")


# --- grandfather-by-Created-date -------------------------------------------


def test_grandfather_inclusive_of_rule_date() -> None:
    assert disp.disposition_gate_applies("Created: 2026-05-30\n") is True  # inclusive
    assert disp.disposition_gate_applies("Created: 2026-06-01\n") is True
    assert disp.disposition_gate_applies("Created: 2026-05-29\n") is False  # pre-rule


def test_grandfather_fails_closed_on_missing_or_malformed_created() -> None:
    assert disp.disposition_gate_applies("no created line here\n") is True
    assert disp.disposition_gate_applies("Created: not-a-date\n") is True
    assert disp.disposition_gate_applies("Created: 2026-13-40\n") is True  # invalid month/day


def test_grandfather_ignores_fenced_created_line() -> None:
    # A fenced example Created: must not be read as the real one; with no real
    # Created line the goal fails closed (in-scope), not parsed from the fence.
    fenced = "Created: 2026-05-29\n"  # real line: pre-rule
    assert disp.disposition_gate_applies(fenced) is False
    only_fenced = "```\nCreated: 2026-05-29\n```\n"  # only inside a fence
    assert disp.disposition_gate_applies(only_fenced) is True  # fail-closed, fence ignored


# --- Auto-Retro blank detection (scoped + fence-safe) ----------------------


def test_auto_retro_blank_variants() -> None:
    assert disp.auto_retro_is_blank("## Auto-Retro\n\n   \n") is True  # whitespace
    assert disp.auto_retro_is_blank("## Goal\n\nx\n") is True  # absent section
    assert disp.auto_retro_is_blank("## Auto-Retro\n\napplied: a gate\n") is False  # content


def test_auto_retro_empty_section_does_not_absorb_next_section() -> None:
    # Regression for the section-scan off-by-one: an empty Auto-Retro followed
    # immediately by another H2 must read as blank, not swallow that H2's body.
    assert disp.auto_retro_is_blank("## Auto-Retro\n## After\nlots of text\n") is True


def test_auto_retro_heading_inside_fence_is_ignored() -> None:
    # A fenced ``## Auto-Retro`` is documentation, not the real section; with no
    # real section present the goal reads as blank (absent).
    fenced = "## Goal\n\n```md\n## Auto-Retro\n\napplied: x\n```\n"
    assert disp.auto_retro_is_blank(fenced) is True


# --- retro Next-Improvements presence (structure only) ---------------------


def test_retro_lists_improvements_counts_list_items_only() -> None:
    assert disp.retro_lists_improvements("## Next Improvements\n\n- do x\n") is True
    assert disp.retro_lists_improvements("## Next Improvements\n\n1. do x\n") is True
    assert disp.retro_lists_improvements("## Next Improvements\n\nprose, no bullet\n") is False
    assert disp.retro_lists_improvements("## Other\n\n- x\n") is False  # renamed -> inert


def test_retro_lists_improvements_ignores_fenced_bullets() -> None:
    fenced = "## Next Improvements\n\n```\n- fake bullet in a fence\n```\n"
    assert disp.retro_lists_improvements(fenced) is False


# --- opt-out (Auto-Retro-scoped, min-length, un-poisoned) ------------------


def test_optout_valid_and_min_length() -> None:
    ok = "## Auto-Retro\n\nRetro dispositions: none — no actionable improvement surfaced this run\n"
    assert disp.find_disposition_optout(ok) == "no actionable improvement surfaced this run"
    short = "## Auto-Retro\n\nRetro dispositions: none — nope\n"
    assert disp.find_disposition_optout(short) is None  # below MIN_OPTOUT_REASON


def test_optout_is_auto_retro_scoped_not_poisoned_by_body_prose() -> None:
    # The round-2 B-2 poisoning shape: the body *describes* the opt-out marker
    # outside the Auto-Retro span. A full-text scan would falsely exempt; the
    # scoped scan must not.
    poisoned = (
        "## Goal\n\nThe opt-out line is `Retro dispositions: none — because there is nothing`.\n\n"
        "## Auto-Retro\n\n   \n"
    )
    assert disp.find_disposition_optout(poisoned) is None
    assert disp.auto_retro_is_blank(poisoned) is True


# --- integration: rung 1a via check_complete_evidence ----------------------

_SLUG = "253-dispo"


def _seed(tmp_path: Path, rel: str, body: str) -> Path:
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


def _build_goal(created: str, auto_retro_body: str, *, slug: str = _SLUG, review_line: str = "") -> str:
    extra = f"{review_line}\n" if review_line else ""
    return (
        f"# Achieve Goal: T\n\nStatus: active\nCreated: {created}\n"
        f"Activation: `/goal @charness-artifacts/goals/{created}-{slug}.md`\n\n"
        "## Final Verification\n\n"
        f"Retro: charness-artifacts/retro/{created}-{slug}.md\n"
        f"Host log probe: charness-artifacts/probe/{created}-{slug}.json\n{extra}\n"
        f"## Auto-Retro\n\n{auto_retro_body}\n"
    )


def _seed_review(tmp_path: Path, created: str, *, slug: str = _SLUG, bind: bool = True) -> str:
    name = f"{created}-{slug}-disposition.md" if bind else f"{created}-unrelated-review.md"
    _seed(
        tmp_path,
        f"charness-artifacts/critique/{name}",
        f"# Disposition review {'for ' + slug if bind else 'of a different goal'}\n\n- improvement 1: applied\n",
    )
    return f"Disposition review: charness-artifacts/critique/{name}"


def _seed_evidence(tmp_path: Path, created: str, *, improvements: bool = True, slug: str = _SLUG) -> None:
    next_improvements = "## Next Improvements\n\n- workflow: do x next time\n" if improvements else "## Next Improvements\n\nnone\n"
    _seed(tmp_path, f"charness-artifacts/retro/{created}-{slug}.md", f"# Retro\n\n{next_improvements}")
    _seed(tmp_path, f"charness-artifacts/probe/{created}-{slug}.json", '{"host":"claude-code"}\n')


def test_block_the_blank_fires_in_scope_blank_with_improving_retro(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, "   "))
    assert report["disposition_scope"]["in_scope"] is True
    assert report["retro_improvements_present"] is True
    assert report["auto_retro_blank"] is True
    assert "disposition_blank" in report
    assert report["ok"] is False


def test_block_the_blank_grandfathered_pre_rule(tmp_path: Path) -> None:
    created = "2026-05-29"  # pre-rule
    _seed_evidence(tmp_path, created)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, "   "))
    assert report["disposition_scope"]["in_scope"] is False
    assert "disposition_blank" not in report  # gate inert for grandfathered goals


def test_block_the_blank_passes_with_filled_auto_retro(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    review_line = _seed_review(tmp_path, created)  # rung 1b satisfied; isolate rung 1a
    report = ce.check_complete_evidence(
        tmp_path,
        _build_goal(created, "applied: shipped a gate this run; issue #999 filed for the rest", review_line=review_line),
    )
    assert "disposition_blank" not in report
    assert report["ok"] is True


def test_block_the_blank_inert_when_retro_lists_no_improvements(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created, improvements=False)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, "   "))
    assert report["retro_improvements_present"] is False
    assert "disposition_blank" not in report  # nothing to disposition -> no block


def test_optout_passes_blank_and_is_surfaced(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    review_line = _seed_review(tmp_path, created)  # rung 1b satisfied; isolate the opt-out path
    optout = "Retro dispositions: none — every surfaced lesson was already captured upstream this run"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, optout, review_line=review_line))
    assert "disposition_blank" not in report
    assert report["disposition_optout"]["reason"].startswith("every surfaced lesson")
    assert report["ok"] is True


# --- integration: rung 1b (disposition_review line) ------------------------

_FILLED = "applied: shipped a gate this run; issue #999 filed for the rest"


def test_disposition_review_line_parsed_and_normalized() -> None:
    parsed = ce.parse_closeout_evidence("Disposition review: charness-artifacts/critique/x.md\n")
    assert parsed["disposition_review"] == {"kind": "evidence", "value": "charness-artifacts/critique/x.md"}
    # the hyphenated label + skip form both normalize/parse (round-3 B1 regex arm)
    skip = ce.parse_closeout_evidence(
        "Disposition-review: skipped: host-blocked-subagent: the host rejected Agent spawn at runtime\n"
    )
    assert skip["disposition_review"]["kind"] == "skip"


def test_disposition_review_prose_in_auto_retro_is_not_evidence() -> None:
    text = (
        "# Achieve Goal: T\n\n"
        "Created: 2026-05-30\n"
        "Activation: `/goal @charness-artifacts/goals/2026-05-30-253-dispo.md`\n\n"
        "## Final Verification\n\n"
        "Retro: charness-artifacts/retro/2026-05-30-253-dispo.md\n"
        "Host log probe: charness-artifacts/probe/2026-05-30-253-dispo.json\n\n"
        "## Auto-Retro\n\n"
        "- Disposition review: this prose notes that the review happened elsewhere\n"
        "Disposition review: this unbulleted prose is still outside Final Verification\n"
    )
    parsed = ce.parse_closeout_evidence(text)
    assert "disposition_review" not in parsed


def test_derive_goal_tokens_keeps_slug_and_numeric_cluster() -> None:
    assert ce.derive_goal_tokens(
        "Activation: `/goal @charness-artifacts/goals/2026-05-31-261-coordination-cues.md`\n"
    ) == ["261-coordination-cues", "261"]
    assert ce.derive_goal_tokens(
        "Activation: `/goal @charness-artifacts/goals/2026-05-31-261.md`\n"
    ) == ["261"]


def test_narration_sections_present_is_exact_and_case_insensitive() -> None:
    retro = "# Retro\n\n## waste\n\nx\n\n## Other\n\nx\n\n## Next Improvements\n\n- x\n"
    assert ce.narration_sections_present(retro) == ["Waste", "Next Improvements"]


def test_in_scope_goal_refused_without_disposition_review_line(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, _FILLED))
    assert report["ok"] is False
    assert "disposition_review" in report["missing"]


def test_in_scope_goal_flips_with_bound_disposition_review(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    review_line = _seed_review(tmp_path, created)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, _FILLED, review_line=review_line))
    assert report["ok"] is True
    assert report["binding_failures"] == []


def test_check_complete_evidence_surfaces_retro_narration_sections(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed(
        tmp_path,
        f"charness-artifacts/retro/{created}-{_SLUG}.md",
        "# Retro\n\n## Waste\n\nnone\n\n## Critical Decisions\n\n- kept the gate\n",
    )
    _seed(tmp_path, f"charness-artifacts/probe/{created}-{_SLUG}.json", '{"host":"claude-code"}\n')
    review_line = _seed_review(tmp_path, created)

    report = ce.check_complete_evidence(
        tmp_path,
        _build_goal(created, _FILLED, review_line=review_line),
    )

    assert report["ok"] is True
    assert report["narration_required_sections"] == ["Waste", "Critical Decisions"]


def test_check_complete_evidence_narration_skips_non_retro_evidence_first(
    tmp_path: Path, monkeypatch
) -> None:
    retro = _seed(
        tmp_path,
        "charness-artifacts/retro/2026-05-29-loop-order.md",
        "# Retro\n\n## Waste\n\nnone\n",
    )
    probe = _seed(tmp_path, "charness-artifacts/probe/2026-05-29-loop-order.json", '{"host":"test"}\n')

    class FakeHelper:
        @staticmethod
        def check(**kwargs):
            return {
                "ok": True,
                "missing": [],
                "missing_evidence_files": [],
                "invalid_skips": [],
                "satisfied": [
                    {"name": "host_log_probe", "via": "evidence", "path": str(probe)},
                    {"name": "retro_artifact", "via": "evidence", "path": str(retro)},
                ],
            }

        @staticmethod
        def evidence_binds_to_context(path, *, tokens):
            return True, "bound for test"

    monkeypatch.setattr(ce, "_load_shared_helper", lambda: FakeHelper)
    text = (
        "# Achieve Goal: T\n\n"
        "Created: 2026-05-29\n"
        "Activation: `/goal @charness-artifacts/goals/2026-05-29-loop-order.md`\n\n"
        "## Final Verification\n\n"
        "Retro: charness-artifacts/retro/2026-05-29-loop-order.md\n"
        "Host log probe: charness-artifacts/probe/2026-05-29-loop-order.json\n"
        "## Auto-Retro\n\nx\n"
    )

    report = ce.check_complete_evidence(tmp_path, text)

    assert report["narration_required_sections"] == ["Waste"]


def test_disposition_review_host_blocked_skip_flips(tmp_path: Path) -> None:
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    skip = "Disposition review: skipped: host-blocked-subagent: this host rejected the Agent spawn at runtime"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, _FILLED, review_line=skip))
    assert report["ok"] is True


def test_grandfathered_goal_does_not_require_disposition_review(tmp_path: Path) -> None:
    created = "2026-05-29"  # pre-rule
    _seed_evidence(tmp_path, created)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, _FILLED))
    assert "disposition_review" not in report["missing"]
    assert report["ok"] is True


def test_disposition_review_must_bind_to_goal(tmp_path: Path) -> None:
    # 1b is presence/binding-only BY DESIGN: a present-but-unrelated review file
    # is refused (cannot satisfy by citing a stranger's artifact).
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    unbound = _seed_review(tmp_path, created, bind=False)
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, _FILLED, review_line=unbound))
    assert "disposition_review" in {e["name"] for e in report["binding_failures"]}
    assert report["ok"] is False


def test_block_the_blank_fires_independently_of_review_skip(tmp_path: Path) -> None:
    # Host portability: a rung-1b skip must NOT disable rung-1a (block-the-blank).
    created = "2026-05-30"
    _seed_evidence(tmp_path, created)
    skip = "Disposition review: skipped: host-blocked-subagent: this host rejected the Agent spawn at runtime"
    report = ce.check_complete_evidence(tmp_path, _build_goal(created, "   ", review_line=skip))
    assert "disposition_blank" in report  # blank caught despite the rung-1b skip
    assert report["ok"] is False


# --- #315: seeded scaffold placeholders must not satisfy the gate ----------


def test_is_placeholder_value_recognizes_literal_markers() -> None:
    for marker in ("TODO", "TODO — fill or skip", "TBD", "<path>", "<retro-path>", "FIXME"):
        assert ce.is_placeholder_value(marker) is True
    # a real bound path never starts with a placeholder marker
    assert ce.is_placeholder_value("charness-artifacts/retro/2026-06-06-g.md") is False
    assert ce.is_placeholder_value("skipped: host-log-not-exposed: detail here") is False


def test_parse_drops_todo_placeholder_evidence_lines() -> None:
    # The template seeds visible `Retro: TODO …` / `Host log probe: TODO …` /
    # `Disposition review: TODO …` lines. An untouched placeholder must NOT be
    # read as satisfied evidence — it is dropped so the name lands in `missing`.
    text = (
        "## Final Verification\n\n"
        "Retro: TODO — create or explicitly skip with an allowed reason before complete\n"
        "Host log probe: TODO — create or explicitly skip with an allowed reason before complete\n"
        "Disposition review: TODO — create or explicitly skip only when policy allows before complete\n"
    )
    parsed = ce.parse_closeout_evidence(text)
    assert parsed == {}  # no placeholder is parsed as evidence or skip


def test_placeholder_only_artifact_cannot_pass_complete_evidence_gate(tmp_path: Path) -> None:
    # An in-scope goal whose Final Verification still carries the untouched
    # `TODO` scaffold placeholders must be refused: every required evidence name
    # falls back to `missing`.
    created = "2026-06-06"
    text = (
        "# Achieve Goal: T\n\nStatus: active\nCreated: " + created + "\n"
        f"Activation: `/goal @charness-artifacts/goals/{created}-{_SLUG}.md`\n\n"
        "## Final Verification\n\n"
        "Retro: TODO — create or explicitly skip with an allowed reason before complete\n"
        "Host log probe: TODO — create or explicitly skip with an allowed reason before complete\n"
        "Disposition review: TODO — create or explicitly skip only when policy allows before complete\n\n"
        "## Auto-Retro\n\n"
        "Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out\n"
    )
    report = ce.check_complete_evidence(tmp_path, text)
    assert report["ok"] is False
    assert set(report["missing"]) == {"retro_artifact", "host_log_probe", "disposition_review"}


def test_auto_retro_placeholder_reads_as_blank_keeping_rung_1a_live() -> None:
    # Seeding the `Retro dispositions: TODO …` placeholder must not silently
    # disable rung 1a: an Auto-Retro carrying only the untouched placeholder
    # still reads as blank-equivalent.
    placeholder = (
        "## Auto-Retro\n\nRetro dispositions: TODO — disposition every surfaced "
        "improvement, or record the explicit no-improvement opt-out\n"
    )
    assert disp.auto_retro_is_blank(placeholder) is True
    # once replaced by a real opt-out or per-improvement record it is non-blank
    optout = "## Auto-Retro\n\nRetro dispositions: none — every lesson was captured upstream this run\n"
    assert disp.auto_retro_is_blank(optout) is False
    assert disp.auto_retro_is_blank("## Auto-Retro\n\napplied: shipped a gate this run\n") is False


def test_block_the_blank_fires_when_auto_retro_holds_only_the_placeholder(tmp_path: Path) -> None:
    # End-to-end: a goal that filled the disposition-review line but left the
    # seeded Auto-Retro TODO placeholder is still block-the-blank refused.
    created = "2026-06-06"
    _seed_evidence(tmp_path, created)
    review_line = _seed_review(tmp_path, created)  # rung 1b satisfied; isolate rung 1a
    placeholder = (
        "Retro dispositions: TODO — disposition every surfaced improvement, or "
        "record the explicit no-improvement opt-out"
    )
    report = ce.check_complete_evidence(
        tmp_path, _build_goal(created, placeholder, review_line=review_line)
    )
    assert report["auto_retro_blank"] is True
    assert "disposition_blank" in report
    assert report["ok"] is False


# --- corpus invariant: grandfather never retroactively refuses -------------


def test_live_corpus_pre_rule_goals_are_never_rung1a_refused() -> None:
    """Stable invariant regardless of how the goal corpus grows: no pre-rule
    (Created < rule date) completed goal is ever block-the-blank refused."""
    runner = _load("audit_disposition_corpus")
    repo_root = Path(__file__).resolve().parents[2]
    rows = [
        runner.audit_goal(repo_root, p)
        for p in sorted((repo_root / "charness-artifacts/goals").glob("*.md"))
    ]
    pre_rule = [r for r in rows if r["status"] == "complete" and r["in_scope"] is False]
    assert pre_rule, "expected at least one pre-rule completed goal in the corpus"
    assert all(r["rung1a_block_the_blank"] is False for r in pre_rule)
