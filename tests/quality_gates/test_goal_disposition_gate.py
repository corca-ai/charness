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
