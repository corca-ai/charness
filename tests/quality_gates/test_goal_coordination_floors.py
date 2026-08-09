"""Tests for the gather + release coordination closeout floors.

Loads ``goal_artifact_coordination_floors.py`` (the leaf floor module) and
``goal_artifact_closeout_evidence.py`` (the wrapper that calls it) **directly**,
mirroring ``test_goal_disposition_gate.py``: the achieve lib sits near the
single-file line gate, so the tests must not force a new re-export through it.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/achieve/scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cf = _load("goal_artifact_coordination_floors")
pr = _load("goal_artifact_phase_routing")
ce = _load("goal_artifact_closeout_evidence")
gal = _load("goal_artifact_lib")
cga = _load("check_goal_artifact")
md = _load("goal_artifact_markdown")


# --- grandfather-by-Created-date -------------------------------------------


def test_grandfather_inclusive_of_rule_date() -> None:
    assert cf.coordination_floors_apply("Created: 2026-05-31\n") is True  # inclusive
    assert cf.coordination_floors_apply("Created: 2026-06-02\n") is True
    assert cf.coordination_floors_apply("Created: 2026-05-30\n") is False  # same-day, grandfathered
    assert cf.coordination_floors_apply("Created: 2026-05-29\n") is False
    assert cf.issue_closeout_floor_applies("Created: 2026-06-02\n") is True
    assert cf.issue_closeout_floor_applies("Created: 2026-06-01\n") is False


def test_grandfather_fails_closed_on_missing_or_malformed_created() -> None:
    assert cf.coordination_floors_apply("no created line here\n") is True
    assert cf.coordination_floors_apply("Created: not-a-date\n") is True
    assert cf.coordination_floors_apply("Created: 2026-13-40\n") is True


def test_grandfather_ignores_fenced_created_line() -> None:
    only_fenced = "```\nCreated: 2026-05-30\n```\n"  # only inside a fence -> no real Created
    assert cf.coordination_floors_apply(only_fenced) is True  # fail-closed, fence ignored


# --- gather trigger (external URL, scoped to Context Sources) ---------------


def test_gather_triggered_on_external_url_in_context_sources() -> None:
    text = "## Context Sources\n\n- https://example.com/thread some external doc\n"
    assert cf.gather_triggered(text) is True


def test_gather_inert_on_local_paths_and_issue_numbers() -> None:
    text = (
        "## Context Sources\n\n- `skills/public/gather/SKILL.md` local path\n"
        "- corca-ai/charness#247 a bare issue ref, not a URL\n"
    )
    assert cf.gather_triggered(text) is False


def test_gather_trigger_is_scoped_to_context_sources() -> None:
    # A URL elsewhere in the body (not in Context Sources) does not trigger the
    # gather floor — only externally-sourced *context* must be gathered.
    text = "## Goal\n\nSee https://example.com for background.\n\n## Context Sources\n\n- local only\n"
    assert cf.gather_triggered(text) is False


def test_gather_inert_when_context_sources_section_is_absent() -> None:
    assert cf.gather_triggered("## Goal\n\nNo context-source section here.\n") is False


def test_gather_trigger_ignores_fenced_url() -> None:
    text = "## Context Sources\n\n```\nhttps://example.com/in-a-fence\n```\n- local path only\n"
    assert cf.gather_triggered(text) is False


# --- release trigger (precise tokens, Coordination Cues excluded) ----------


def test_release_triggered_on_version_bump_token() -> None:
    assert cf.release_triggered("## Slice Log\n\n- What changed: ran bump_version.py --part minor\n") is True
    assert cf.release_triggered("## Slice Log\n\n- touched .claude-plugin/marketplace.json\n") is True
    assert cf.release_triggered("## Slice Log\n\n- updated charness-artifacts/release/latest.md\n") is True


def test_release_inert_on_mere_release_skill_mention() -> None:
    # The bare word "release" / the release skill *directory* is not a token, so a
    # goal that merely references release tooling as context does not self-trip.
    text = (
        "## Context Sources\n\n- `skills/public/release/SKILL.md` and `skills/public/gather/`\n"
        "## Boundaries\n\n- sync the `plugins/` mirror before validators\n"
    )
    assert cf.release_triggered(text) is False


def test_release_trigger_excludes_coordination_cues_section() -> None:
    # A `Release:` reference value that names a release artifact must NOT itself
    # re-trigger the floor (else a satisfied release step would reopen the gate).
    text = (
        "## Coordination Cues\n\nRelease: charness-artifacts/release/2026-05-31-x.md\n\n"
        "## Slice Log\n\n- ordinary work, no release token\n"
    )
    assert cf.release_triggered(text) is False


def test_release_trigger_ignores_fenced_token() -> None:
    assert cf.release_triggered("## Slice Log\n\n```\nbump_version.py\n```\n") is False


def test_issue_closeout_triggered_by_tracked_issue_context_source() -> None:
    text = "## Context Sources\n\n- GitHub issue #277: closeout binding regression\n"
    assert cf.issue_closeout_triggered(text) is True


def test_issue_closeout_triggered_by_github_issue_url_context_source() -> None:
    text = "## Context Sources\n\n- https://github.com/corca-ai/charness/issues/277\n"
    assert cf.issue_closeout_triggered(text) is True


def test_issue_closeout_triggered_by_repo_qualified_issue_context_source() -> None:
    text = "## Context Sources\n\n- corca-ai/charness#277\n"
    assert cf.issue_closeout_triggered(text) is True


def test_issue_closeout_triggered_by_close_keyword_in_recorded_work() -> None:
    text = "## Slice Log\n\n- Commit body carries Close #277 after verifier proof.\n"
    assert cf.issue_closeout_triggered(text) is True


def test_issue_closeout_triggered_by_repo_qualified_close_keyword() -> None:
    text = "## Slice Log\n\n- Commit body carries Close corca-ai/charness#277.\n"
    assert cf.issue_closeout_triggered(text) is True


def test_issue_closeout_triggered_by_close_keyword_in_final_verification() -> None:
    text = "## Final Verification\n\n- GitHub auto-close proof saw Close #277 on origin/main.\n"
    assert cf.issue_closeout_triggered(text) is True


def test_issue_closeout_ignores_planning_close_keywords() -> None:
    text = (
        "## Non-Goals\n\n- Do not close #276 until push and remote verification.\n\n"
        "## Slice Plan\n\n| 1 | Close #276 only after carrier proof | planned |\n"
    )
    assert cf.issue_closeout_triggered(text) is False


def test_issue_closeout_inert_on_generic_issue_and_auto_retro_disposition() -> None:
    text = (
        "## Context Sources\n\n- `docs/handoff.md` local source\n\n"
        "## Slice Log\n\n- ordinary issue discussion with no tracked issue number\n\n"
        "## Auto-Retro\n\napplied: shipped fix; issue #999 tracks the rest\n"
    )
    assert cf.issue_closeout_triggered(text) is False


def test_issue_closeout_trigger_excludes_coordination_cues_and_fences() -> None:
    text = (
        "## Coordination Cues\n\n"
        "Issue closeout: charness-artifacts/issue/2026-06-02-277.md\n\n"
        "## Slice Log\n\n```\nClose #277.\n```\n"
    )
    assert cf.issue_closeout_triggered(text) is False


def test_section_span_keeps_child_headings_inside_parent_body() -> None:
    masked = cf._mask_fences("## Parent\nbody\n### Child\nchild body\n## Next\noutside\n")
    start, end = cf._section_span(masked, "Parent")
    assert masked[start:end] == "body\n### Child\nchild body\n"


# --- step-line parsing (presence-only, line-anchored, opt-out min length) ---


def _coord(body: str):
    return cf._section_body(cf._mask_fences(body), "Coordination Cues")


def test_parse_step_reference_and_optout_forms() -> None:
    ref = _coord("## Coordination Cues\n\nGather: charness-artifacts/gather/x.md\n")
    assert cf._parse_step(ref, cf._GATHER_REF) == ("ref", "charness-artifacts/gather/x.md")
    ok_optout = _coord("## Coordination Cues\n\nRelease: n/a — no release surface was touched this run\n")
    kind, reason = cf._parse_step(ok_optout, cf._RELEASE_REF)
    assert kind == "optout" and reason.startswith("no release surface")
    short = _coord("## Coordination Cues\n\nRelease: n/a — nope\n")
    assert cf._parse_step(short, cf._RELEASE_REF)[0] == "optout_short"  # below MIN_OPTOUT_REASON


def test_parse_step_prefers_satisfying_line_over_earlier_short_optout() -> None:
    # N1 regression: a stray non-satisfying step line ABOVE a real reference must
    # not shadow it into a false refusal — the first *satisfying* line wins.
    body = _coord(
        "## Coordination Cues\n\n"
        "Gather: n/a — short\n"
        "Gather: charness-artifacts/gather/2026-05-31-real.md\n"
    )
    assert cf._parse_step(body, cf._GATHER_REF) == ("ref", "charness-artifacts/gather/2026-05-31-real.md")
    # symmetric for release, and a valid opt-out below a bad one is also found
    rbody = _coord(
        "## Coordination Cues\n\n"
        "Release: n/a — no\n"
        "Release: n/a — edited the release script but cut no version this run\n"
    )
    assert cf._parse_step(rbody, cf._RELEASE_REF)[0] == "optout"


def test_parse_step_ignores_mid_line_inline_example() -> None:
    # The poisoning shape: prose that merely *describes* a step line inside
    # backticks / parens must not be read as a real reference (line-anchored).
    body = _coord(
        "## Coordination Cues\n\n"
        "- **Gather step** — add a `Gather: <path>` line here, or `Gather: n/a — <reason>`.\n"
    )
    assert cf._parse_step(body, cf._GATHER_REF) == (None, None)


# --- #261 Slice 3: bounded mutation-survivor hardening ----------------------
# Targeted kills for the live, NON-equivalent survivors confirmed by per-mutant
# ground-truthing of the coordination-cues trio. Each test was verified to fail
# (kill) under its mutant and pass on clean code. The remaining ~survivors are
# equivalent-by-construction (named below) or deferred to the follow-up triage.


def test_section_span_body_starts_at_first_content_char() -> None:
    """`body_start += 1` lands exactly on the first body char (just past the
    heading line's newline). An off-by-one — `+= 2` drops the first char, `-= 1`
    keeps the heading's newline — corrupts every downstream section-body scan."""
    masked = cf._mask_fences("## H\nXfirst\nmore\n## Next\n")
    start, end = cf._section_span(masked, "H")
    assert masked[start:end] == "Xfirst\nmore\n"


def test_classify_step_optout_floor_is_exactly_thirty_chars() -> None:
    """The opt-out floor is exactly 30 visible chars (`MIN_OPTOUT_REASON`): a
    30-char reason satisfies (`optout`), 29 does not (`optout_short`). Pinning the
    literal kills both the `>=`→`>` operator mutant and the `30`→`31` constant
    mutant (the latter via the explicit constant assertion)."""
    assert cf.MIN_OPTOUT_REASON == 30  # the contract the kills below pin
    at_floor = cf._classify_step("n/a — " + "x" * 30)
    below_floor = cf._classify_step("n/a — " + "y" * 29)
    assert at_floor == ("optout", "x" * 30)
    assert below_floor[0] == "optout_short"


def test_classify_step_optout_length_ignores_trailing_whitespace() -> None:
    """The opt-out reason is stripped before its length is measured, so trailing
    padding cannot smuggle a too-short reason past the floor. Dropping `.strip()`
    would let the padded length (>= the floor) wrongly pass as `optout`."""
    visible = "y" * (cf.MIN_OPTOUT_REASON - 1)  # one below the floor when stripped
    kind, value = cf._classify_step(f"n/a — {visible}      ")
    assert kind == "optout_short"
    assert value == visible  # stored reason is the stripped form


# --- template seed is inert (no false trigger / no false satisfy) -----------


def test_template_seed_coordination_cues_is_inert(tmp_path: Path) -> None:
    gal.upsert_goal(tmp_path, date="2026-05-31", slug="seed", title="T")
    text = gal.goal_path(tmp_path, "2026-05-31", "seed").read_text(encoding="utf-8")
    # the scaffold carries a Coordination Cues heading...
    assert "## Coordination Cues" in text
    # ...but the seed prose neither triggers a floor nor parses as a real step
    assert cf.gather_triggered(text) is False
    assert cf.release_triggered(text) is False
    seed = _coord(text)
    assert cf._parse_step(seed, cf._GATHER_REF) == (None, None)
    assert cf._parse_step(seed, cf._RELEASE_REF) == (None, None)
    assert cf._parse_step(seed, cf._ISSUE_CLOSEOUT_REF) == (None, None)
    # and check_goal still passes on the fresh scaffold
    assert gal.check_goal(text)["ok"] is True


# --- integration via check_complete_evidence -------------------------------

_SLUG = "coord-floor"


def _seed(tmp_path: Path, rel: str, body: str) -> None:
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")


def _seed_other_evidence(tmp_path: Path, created: str) -> None:
    # Satisfy every OTHER closeout gate (retro/probe/disposition) so the only
    # variable under test is the coordination floor. Retro lists no improvements
    # -> block-the-blank inert; Auto-Retro is non-blank anyway.
    _seed(tmp_path, f"charness-artifacts/retro/{created}-{_SLUG}.md", "# Retro\n\n## Next Improvements\n\nnone\n")
    _seed(tmp_path, f"charness-artifacts/probe/{created}-{_SLUG}.json", '{"host":"claude-code"}\n')
    _seed(
        tmp_path,
        f"charness-artifacts/critique/{created}-{_SLUG}-disposition.md",
        f"# Disposition review for {_SLUG}\n\n- improvement 1: applied\n",
    )


def _full_goal(*, created: str, context_sources: str, coordination: str, release_work: str = "") -> str:
    return (
        f"# Achieve Goal: T\n\nStatus: active\nCreated: {created}\n"
        f"Activation: `/goal @charness-artifacts/goals/{created}-{_SLUG}.md`\n\n"
        f"## Context Sources\n\n{context_sources}\n\n"
        f"## Coordination Cues\n\n{coordination}\n\n"
        f"## Slice Log\n\n{release_work}\n\n"
        "## Final Verification\n\n"
        f"Retro: charness-artifacts/retro/{created}-{_SLUG}.md\n"
        f"Host log probe: charness-artifacts/probe/{created}-{_SLUG}.json\n"
        f"Disposition review: charness-artifacts/critique/{created}-{_SLUG}-disposition.md\n\n"
        "## Auto-Retro\n\napplied: shipped a gate this run; issue #999 filed for the rest\n"
    )


_URL_SOURCE = "- https://example.com/spec the external design source\n"
_LOCAL_SOURCE = "- `charness-artifacts/retro/x.md` local only\n"


def test_clean_goal_no_floors_no_friction(tmp_path: Path) -> None:
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path, _full_goal(created=created, context_sources=_LOCAL_SOURCE, coordination="_unused_")
    )
    assert report["coordination_scope"]["in_scope"] is True
    assert report["gather_floor"]["triggered"] is False
    assert report["release_floor"]["triggered"] is False
    assert report["issue_closeout_floor"]["triggered"] is False
    assert "coordination_missing" not in report
    assert report["ok"] is True


def test_gather_triggered_without_step_refuses(tmp_path: Path) -> None:
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path, _full_goal(created=created, context_sources=_URL_SOURCE, coordination="Routing: impl — selected from installed metadata\n")
    )
    assert report["gather_floor"]["triggered"] is True
    assert report["gather_floor"]["satisfied"] is False
    assert {e["floor"] for e in report["coordination_missing"]} == {"gather"}
    assert report["ok"] is False


def test_gather_satisfied_by_reference(tmp_path: Path) -> None:
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_URL_SOURCE,
            coordination="Gather: charness-artifacts/gather/2026-05-31-spec.md\n",
        ),
    )
    assert report["gather_floor"]["satisfied"] is True
    assert "coordination_missing" not in report
    assert report["ok"] is True


def test_gather_satisfied_by_optout(tmp_path: Path) -> None:
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_URL_SOURCE,
            coordination="Gather: n/a — the URL is a tracked GitHub issue handled via issue, not gather\n",
        ),
    )
    assert report["gather_floor"]["satisfied"] is True
    assert report["ok"] is True


def test_gather_short_optout_still_refuses(tmp_path: Path) -> None:
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(created=created, context_sources=_URL_SOURCE, coordination="Gather: n/a — nope\n"),
    )
    assert report["gather_floor"]["satisfied"] is False
    assert report["ok"] is False


def test_gather_grandfathered_pre_rule_is_inert(tmp_path: Path) -> None:
    created = "2026-05-30"  # same-day, grandfathered
    _seed(tmp_path, f"charness-artifacts/retro/{created}-{_SLUG}.md", "# Retro\n\n## Next Improvements\n\nnone\n")
    _seed(tmp_path, f"charness-artifacts/probe/{created}-{_SLUG}.json", '{"host":"claude-code"}\n')
    # pre-2026-05-30 disposition rule date is inclusive, so this date still needs
    # the disposition_review line; seed + cite it so only coordination scope varies.
    _seed(
        tmp_path,
        f"charness-artifacts/critique/{created}-{_SLUG}-disposition.md",
        f"# Disposition review for {_SLUG}\n\n- improvement 1: applied\n",
    )
    report = ce.check_complete_evidence(
        tmp_path, _full_goal(created=created, context_sources=_URL_SOURCE, coordination="no step here\n")
    )
    assert report["coordination_scope"]["in_scope"] is False
    assert "coordination_missing" not in report
    assert report["ok"] is True


def test_release_triggered_without_step_refuses(tmp_path: Path) -> None:
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_LOCAL_SOURCE,
            coordination="Routing: impl — selected from installed metadata\n",
            release_work="- What changed: ran bump_version.py --part patch\n",
        ),
    )
    assert report["release_floor"]["triggered"] is True
    assert report["release_floor"]["satisfied"] is False
    assert {e["floor"] for e in report["coordination_missing"]} == {"release"}
    assert report["ok"] is False


def test_release_satisfied_by_reference(tmp_path: Path) -> None:
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_LOCAL_SOURCE,
            coordination="Release: charness-artifacts/release/2026-05-31-v0.13.0.md\n",
            release_work="- What changed: ran bump_version.py --part minor\n",
        ),
    )
    assert report["release_floor"]["satisfied"] is True
    assert report["ok"] is True


def test_release_satisfied_by_optout(tmp_path: Path) -> None:
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_LOCAL_SOURCE,
            coordination="Release: n/a — edited the release script but cut no version this run\n",
            release_work="- What changed: refactored publish_release.py internals only\n",
        ),
    )
    assert report["release_floor"]["satisfied"] is True
    assert report["ok"] is True


def test_both_floors_can_refuse_together(tmp_path: Path) -> None:
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_URL_SOURCE,
            coordination="Routing: impl — selected from installed metadata\n",
            release_work="- bumped via bump_version.py\n",
        ),
    )
    assert {e["floor"] for e in report["coordination_missing"]} == {"gather", "release"}
    assert report["ok"] is False


def test_issue_closeout_triggered_without_step_refuses(tmp_path: Path) -> None:
    created = "2026-06-02"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources="- GitHub issue #277: closeout binding regression\n",
            coordination="Routing: impl — selected from installed metadata\n",
        ),
    )
    assert report["issue_closeout_floor"]["triggered"] is True
    assert report["issue_closeout_floor"]["satisfied"] is False
    assert {e["floor"] for e in report["coordination_missing"]} == {"issue_closeout"}
    assert report["ok"] is False


def test_issue_closeout_satisfied_by_reference(tmp_path: Path) -> None:
    created = "2026-06-02"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources="- GitHub issue #277: closeout binding regression\n",
            coordination="Issue closeout: charness-artifacts/issue/2026-06-02-277.md\n",
        ),
    )
    assert report["issue_closeout_floor"]["satisfied"] is True
    assert "coordination_missing" not in report
    assert report["ok"] is True


def test_issue_closeout_satisfied_by_optout(tmp_path: Path) -> None:
    created = "2026-06-02"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources="- GitHub issue #277: closeout binding regression\n",
            coordination="Issue closeout: n/a — issue was context only and no tracked issue closes in this goal\n",
        ),
    )
    assert report["issue_closeout_floor"]["satisfied"] is True
    assert report["ok"] is True


def test_issue_closeout_short_optout_refuses(tmp_path: Path) -> None:
    created = "2026-06-02"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources="- GitHub issue #277: closeout binding regression\n",
            coordination="Issue closeout: n/a — too short\n",
        ),
    )
    assert report["issue_closeout_floor"]["triggered"] is True
    assert report["issue_closeout_floor"]["evidence"] == "optout_short"
    assert {e["floor"] for e in report["coordination_missing"]} == {"issue_closeout"}
    assert report["ok"] is False


def test_github_issue_url_context_triggers_gather_and_issue_floors(tmp_path: Path) -> None:
    created = "2026-06-02"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources="- https://github.com/corca-ai/charness/issues/277\n",
            coordination="Routing: impl — selected from installed metadata\n",
        ),
    )
    assert report["gather_floor"]["triggered"] is True
    assert report["issue_closeout_floor"]["triggered"] is True
    assert {e["floor"] for e in report["coordination_missing"]} == {"gather", "issue_closeout"}
    assert report["ok"] is False


def test_issue_closeout_grandfathers_pre_rule_goal(tmp_path: Path) -> None:
    created = "2026-06-01"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources="- GitHub issue #277: closeout binding regression\n",
            coordination="Routing: impl — selected from installed metadata\n",
        ),
    )
    assert report["issue_closeout_floor"]["in_scope"] is False
    assert report["issue_closeout_floor"]["triggered"] is False
    assert "coordination_missing" not in report
    assert report["ok"] is True


def test_phase_route_triggers_are_recorded_work_only() -> None:
    planned = (
        "## Slice Plan\n\n| 1 | implementation and debug RCA later | now | proof | planned |\n\n"
        "## Slice Log\n\n- Objective: inspect only\n"
    )
    assert pr.phase_route_triggers(planned) == {
        "impl": False,
        "debug": False,
        "quality": False,
        "issue": False,
    }


def test_phase_routing_selected_owner_skill_with_basis_satisfies(tmp_path: Path) -> None:
    created = "2026-06-04"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_LOCAL_SOURCE,
            coordination="Routing: impl — selected from installed metadata\n",
            release_work="- What changed: updated goal helper behavior\n",
        ),
    )
    assert report["phase_routing_floor"]["triggered"] is True
    assert report["phase_routing_floor"]["required"] == ["impl"]
    assert report["phase_routing_floor"]["evidence"] == {"impl": "ref"}
    assert not any(e["floor"] == "phase_routing" for e in report.get("coordination_missing", []))


def test_phase_routing_satisfied_by_selected_owner_skill_reference(tmp_path: Path) -> None:
    created = "2026-06-04"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_LOCAL_SOURCE,
            coordination=(
                "Phases: quality\n"
                "Routing: impl and quality selected from installed metadata for this slice\n"
            ),
            release_work=(
                "- What changed: updated goal helper behavior\n"
                "- Targeted verification: pytest -q tests/quality_gates/test_goal_coordination_floors.py\n"
            ),
        ),
    )
    assert report["phase_routing_floor"]["required"] == ["impl", "quality"]
    assert report["phase_routing_floor"]["evidence"] == {"impl": "ref", "quality": "ref"}
    assert "coordination_missing" not in report
    assert report["ok"] is True


# --- #406 wrapped-line robustness: join soft-wraps before matching ----------


def test_join_soft_wraps_joins_continuation_but_not_adjacent_field() -> None:
    joined = md.join_soft_wraps(
        "Routing: impl selected from installed metadata\nquality here\nGather: n/a — x\n"
    )
    # the bare continuation line merges into the Routing value...
    assert "Routing: impl selected from installed metadata quality here" in joined
    # ...but the following `Gather:` field line stays its own line (no over-join).
    assert "\nGather: n/a — x" in joined


def test_phase_routing_satisfied_when_routed_skill_wraps_to_continuation(tmp_path: Path) -> None:
    # #406: a correct Routing value whose routed skill name wrapped onto the next
    # physical line was false-rejected (the regex read only the first line).
    created = "2026-06-04"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_LOCAL_SOURCE,
            coordination=(
                "Phases: quality\n"
                "Routing: impl selected from installed metadata\nquality for this slice\n"
            ),
            release_work=(
                "- What changed: updated goal helper behavior\n"
                "- Targeted verification: pytest -q tests/quality_gates/test_goal_coordination_floors.py\n"
            ),
        ),
    )
    assert report["phase_routing_floor"]["required"] == ["impl", "quality"]
    assert report["phase_routing_floor"]["evidence"] == {"impl": "ref", "quality": "ref"}
    assert "coordination_missing" not in report
    assert report["ok"] is True


def test_gather_optout_satisfied_when_reason_wraps_to_continuation(tmp_path: Path) -> None:
    # #406 sibling floor: a >=30-char opt-out reason wrapped across two physical
    # lines was under-counted (only the first physical line was measured).
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_URL_SOURCE,
            coordination="Gather: n/a — handled via\nthe issue skill instead of gather this run\n",
        ),
    )
    assert report["gather_floor"]["triggered"] is True
    assert report["gather_floor"]["satisfied"] is True
    assert "coordination_missing" not in report
    assert report["ok"] is True


def test_phase_routing_satisfied_by_optout(tmp_path: Path) -> None:
    created = "2026-06-04"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_LOCAL_SOURCE,
            coordination=(
                "Routing: n/a — restoring a generated fixture only, no owner skill boundary "
                "was crossed in this goal\n"
            ),
            release_work="- What changed: restored a generated fixture snapshot\n",
        ),
    )
    assert report["phase_routing_floor"]["triggered"] is True
    assert report["phase_routing_floor"]["evidence"] == {"impl": "optout"}
    assert report["ok"] is True


# --- error / fail-open branches (the #260 changed-line-coverage gap) --------
#
# The coordination-cues trio shipped (commit f55be70) with these specific
# error / fail-open branches test-uncovered. `classify_changed_line_scope_gap`
# blocks on ANY uncovered changed statement line, so they kept the whole trio
# out of the mutation sample (#260 blocking signal). The tests below pin them.


def test_mask_fences_unbalanced_fence_fails_open() -> None:
    # An odd number of fence markers leaves `_mask_fences` in an open-fence state
    # at EOF; it fails OPEN (returns the raw text untouched) rather than masking
    # the unterminated tail. Covers goal_artifact_coordination_floors.py:110.
    unbalanced = "## Coordination Cues\n\n```\nGather: charness-artifacts/gather/x.md\n"
    assert cf._mask_fences(unbalanced) == unbalanced


@pytest.mark.parametrize("module", [cf, ce], ids=["floors", "closeout"])
def test_mask_fences_blanks_fenced_chars_and_preserves_structure(module) -> None:
    # `_mask_fences` is a duplicated leaf helper in both the floors and closeout
    # modules. Pin its exact masking so the fence-toggle, the per-char
    # newline-vs-space decision (incl. a tab, ord 9 < ord '\n' 10), the
    # `continue`, and the closing `if in_fence` are all mutation-killed:
    #   - non-fenced lines pass through untouched
    #   - a fence marker line and the fenced body collapse to spaces (newline kept)
    #   - a tab (ord 9 < ord '\n' 10) — in BOTH the fence marker line and the
    #     fenced body — becomes a space, not a kept newline, so `==` cannot be
    #     mutated to `<=` / `<` without breaking the output
    text = "keep\n```\t\nab\tc\n```\nkeep2\n"
    lines = module._mask_fences(text).split("\n")
    assert lines[0] == "keep"      # non-fenced line untouched
    assert lines[1] == "    "      # "```\t" fence marker (tab included) -> 4 spaces
    assert lines[2] == "    "      # "ab\tc" fenced body (tab included) -> 4 spaces
    assert lines[3] == "   "       # closing ``` -> 3 spaces
    assert lines[4] == "keep2"     # trailing non-fenced line untouched


def test_section_span_heading_at_eof_collapses_to_empty_span() -> None:
    # A watched heading as the final line with no trailing newline makes
    # `masked.find("\\n", ...)` return -1, so the body span collapses to
    # (len, len). Covers goal_artifact_coordination_floors.py:129.
    masked = "## Coordination Cues"  # no trailing newline, heading is the last char
    assert cf._section_span(masked, "Coordination Cues") == (len(masked), len(masked))
    # and a downstream body read on that span is empty, never raising
    assert cf._section_body(masked, "Coordination Cues") == ""


def test_load_sibling_coordination_floors_raises_when_spec_missing(monkeypatch) -> None:
    # The leaf-module loader fails closed with ImportError when the spec cannot be
    # built (the sibling file is missing). Covers
    # goal_artifact_closeout_evidence.py:202 (the raise branch), which only runs
    # when spec_from_file_location returns None.
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)
    with pytest.raises(ImportError, match="goal_artifact_coordination_floors.py not found"):
        ce._load_sibling_coordination_floors()


def test_skill_runtime_bootstrap_loader_fails_closed_when_bootstrap_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(cga.Path, "is_file", lambda self: False)

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        cga._load_skill_runtime_bootstrap()


def test_sibling_loaders_fail_closed_when_spec_loader_is_missing(monkeypatch) -> None:
    class SpecWithoutLoader:
        loader = None

    spec_without_loader = SpecWithoutLoader()
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: spec_without_loader)

    with pytest.raises(ImportError, match="scripts/check_prescribed_skill_executed_lib.py not found"):
        ce._load_shared_helper()
    with pytest.raises(ImportError, match="goal_artifact_disposition.py not found"):
        ce._load_sibling_disposition()


# --- check_goal_artifact CLI surfaces an unsatisfied coordination floor -----
#
# `check_goal_artifact.py` is otherwise only ever run as a subprocess, so the
# coverage probe reads it as 0% (NOT TRACKED -> whole-file block, the #260
# signal for that file). This in-process test exercises `main()` so its changed
# lines (the coordination-floors missing-bits formatting, L100-107) are covered,
# and pins the real behavior: a complete goal whose gather floor is unsatisfied
# is refused with a "coordination floors: gather step missing" issue.

_CLI_SECTIONS = (
    "Non-Goals",
    "Boundaries",
    "User Acceptance",
    "Agent Verification Plan",
    "Slice Plan",
    "Slice Log",
    "Off-Goal Findings",
    "User Verification Instructions",
)


def _complete_goal_missing_gather(created: str, slug: str) -> str:
    sections = "".join(f"## {name}\n\nx\n\n" for name in _CLI_SECTIONS)
    return (
        f"# Achieve Goal: T\n\nStatus: complete\nCreated: {created}\n"
        f"Activation: `/goal @charness-artifacts/goals/{created}-{slug}.md`\n\n"
        "## Goal\n\nx\n\n"
        f"## Context Sources\n\n- https://example.com/spec the external design source\n\n"
        "## Coordination Cues\n\nRouting: impl — selected from installed metadata (no Gather step recorded)\n\n"
        f"{sections}"
        "## Final Verification\n\n"
        f"Retro: charness-artifacts/retro/{created}-{slug}.md\n"
        f"Host log probe: charness-artifacts/probe/{created}-{slug}.json\n"
        f"Disposition review: charness-artifacts/critique/{created}-{slug}-disposition.md\n\n"
        "## Auto-Retro\n\napplied: shipped a gate this run\n"
    )


def test_check_goal_artifact_cli_refuses_complete_goal_with_unsatisfied_gather(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    created = "2026-05-31"
    slug = "cli-coord"
    # bind every OTHER closeout gate so the gather floor is the only failure
    _seed(tmp_path, f"charness-artifacts/retro/{created}-{slug}.md", "# Retro\n\n## Next Improvements\n\nnone\n")
    _seed(tmp_path, f"charness-artifacts/probe/{created}-{slug}.json", '{"host":"claude-code"}\n')
    _seed(
        tmp_path,
        f"charness-artifacts/critique/{created}-{slug}-disposition.md",
        f"# Disposition review for {slug}\n\n- improvement 1: applied\n",
    )
    goal_path = tmp_path / f"charness-artifacts/goals/{created}-{slug}.md"
    goal_path.parent.mkdir(parents=True, exist_ok=True)
    goal_path.write_text(_complete_goal_missing_gather(created, slug), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["check_goal_artifact.py", "--repo-root", str(tmp_path), "--goal-path", str(goal_path)],
    )
    rc = cga.main()
    out = capsys.readouterr().out

    assert rc == 1
    assert "coordination floors: gather step missing" in out


def test_coordination_floors_missing_created_fails_closed_and_runs() -> None:
    report = {"ok": True}
    cf.apply_coordination_floors(
        report,
        "## Context Sources\n\n- https://example.com/spec\n\n"
        "## Coordination Cues\n\nRouting: impl — selected from installed metadata\n",
    )

    assert report["coordination_scope"]["in_scope"] is True
    assert report["coordination_scope"]["created"] is None
    assert "fail-closed" in report["coordination_scope"]["reason"]
    assert report["coordination_missing"][0]["floor"] == "gather"
    assert report["ok"] is False


def test_evidence_missing_bits_surfaces_every_rung_reason() -> None:
    # #335: _evidence_missing_bits builds the human-facing CLI reasons. The
    # `missing`, disposition-blank, disposition-form, recurrence-lineage, and
    # closeout-delegation arms (check_goal_artifact.py:60/76/81/83/90) were never
    # exercised, so the changed lines shipped uncovered. Trip every arm at once.
    report = {
        "missing": ["Goal"],
        "missing_evidence_files": [],
        "invalid_skips": [],
        "binding_failures": [],
        "disposition_blank": True,
        "disposition_form": {"reason": "prose-only disposition rejected"},
        "recurrence_lineage": {"reason": "no recurs:/follow-up: lineage marker"},
        "coordination_missing": [],
        "closeout_delegation": {"failures": ["quality not routed before HITL"]},
    }
    bits = cga._evidence_missing_bits(report)
    joined = "\n".join(bits)
    assert "missing: Goal" in joined
    assert "improvement-disposition gate:" in joined
    assert "disposition form: prose-only disposition rejected" in joined
    assert "recurrence-lineage floor: no recurs:/follow-up: lineage marker" in joined
    assert "closeout delegation: quality not routed before HITL" in joined


# --- S14/S17: the Created-scope parse must not be steerable by quoted or ------
# --- fenced text (audit 2026-07-28 rows S14 class h, S17 class g) -------------


def test_created_scope_prefers_the_goals_own_line_over_a_quoted_one() -> None:
    """S14: a body that blockquotes another artifact's date line above its own.

    First-match-wins read the quoted 2025-01-02 and grandfathered every
    Created-gated floor at once. The plain line is the goal's own field, so it
    wins; the quoted one is inert.
    """
    text = "# Goal\n\n> Created: 2025-01-02\n\nCreated: 2026-07-01\nStatus: complete\n"

    assert cf.goal_created_date(text).isoformat() == "2026-07-01"
    assert cf.coordination_floors_apply(text) is True
    assert pr.phase_routing_floor_applies(text) is True


def test_created_scope_fails_closed_on_conflicting_unquoted_dates() -> None:
    """Two plain `Created:` lines disagree: nothing says which is the artifact's
    own, so the scope verdict is refused (None -> fail closed -> floors run)."""
    text = "Created: 2025-01-02\nCreated: 2026-07-01\n"

    assert cf.goal_created_date(text) is None
    assert cf.coordination_floors_apply(text) is True


def test_created_scope_control_quoted_only_line_still_grandfathers() -> None:
    """Control (false-refusal guard): the tested relaxation that reads a
    prefixed/quoted `Created:` when it is the ONLY one is preserved, including a
    repeated identical value."""
    assert cf.goal_created_date("> Created: 2026-01-01\n").isoformat() == "2026-01-01"
    assert cf.coordination_floors_apply("- created: 2026-01-01\n") is False
    assert cf.coordination_floors_apply("Created: 2026-01-01\n> Created: 2026-01-01\n") is False
    assert cf.coordination_floors_apply("Created: 2026-07-01\n") is True


def test_an_unbalanced_fence_is_reported_rather_than_guessed_at() -> None:
    """S17, after the repair that the repair needed.

    The first cut masked every balanced region and returned only the unclosed tail
    raw. Measured wrong: fences pair left to right, so ONE stray marker early
    re-pairs every later fence and masks the real sections between them — a
    malformed-markdown goal became a false "missing sections" refusal. With odd
    parity nothing in the text says which marker is the stray one, so `mask_fences`
    keeps failing open and the FACT of imbalance becomes readable instead.
    """
    text = (
        "```\nCreated: 2020-01-01\n```\n\nCreated: 2026-07-20\n\n"
        "## Notes\n\n```\nstill open at EOF\n"
    )

    assert md.fences_balanced(text) is False
    assert md.mask_fences(text) == text  # fails open, unchanged
    assert md.fences_balanced("```\nx\n```\n") is True
    assert "x" not in md.mask_fences("```\nx\n```\n")

    # ...and the stray-marker shape the first cut broke: real sections stay visible.
    stray = "```\n\n## Slice Log\n\n- What changed: real work\n\n```\nexample\n```\n"
    assert "## Slice Log" in md.mask_fences(stray)


def test_phase_routing_scope_survives_a_fenced_template_plus_unclosed_fence() -> None:
    """S17 end to end: in-scope work stayed unproven because a fenced example
    date won. Now the floor runs and refuses the unrouted impl work."""
    text = (
        "```\nCreated: 2020-01-01\n```\n\nCreated: 2026-07-20\nStatus: complete\n\n"
        "## Slice Log\n\n- What changed: rewrote the parser\n\n"
        "## Coordination Cues\n\n(none)\n\n```\nunclosed example\n"
    )
    report = {"ok": True}
    pr.apply_phase_routing_floor(report, text)

    # The date is UNESTABLISHED, not 2026-07-20: with the fence unbalanced the
    # masked body is the raw body, so the fenced 2020-01-01 and the real date are
    # indistinguishable. Failing closed runs the floor, which is the whole point —
    # the pre-fix behavior let the fenced date silently take it out of scope.
    assert pr.goal_created_date(text) is None
    assert report["phase_routing_floor"]["in_scope"] is True
    assert report["phase_routing_floor"]["required"] == ["impl"]
    assert report["ok"] is False


def test_phase_routing_control_routed_work_still_passes_with_fences() -> None:
    """Control: the same in-scope goal with a real `Routing:` line — and both a
    closed and an unclosed fence — is still accepted."""
    text = (
        "```\nCreated: 2020-01-01\n```\n\nCreated: 2026-07-20\nStatus: complete\n\n"
        "## Slice Log\n\n- What changed: rewrote the parser\n\n"
        "## Coordination Cues\n\nRouting: impl — routed per installed skill metadata\n\n"
        "```\nunclosed example\n"
    )
    report = {"ok": True}
    pr.apply_phase_routing_floor(report, text)

    assert report["phase_routing_floor"]["satisfied"] is True
    assert report["ok"] is True


# --- successor-goal floor (unconditional at completion) ---------------------


def _cues(body: str, created: str = "2026-08-07") -> dict:
    report: dict = {}
    cf.apply_coordination_floors(
        report, f"# Goal\nCreated: {created}\n\n## Coordination Cues\n\n{body}\n"
    )
    return report["successor_goal_floor"]


def test_the_successor_goal_floor_triggers_on_every_in_scope_goal() -> None:
    """Unlike gather/release/issue-closeout, the trigger is not a boundary the
    goal happened to touch. Every completing goal has learned something, so the
    only question is whether the next goal gets it."""
    floor = _cues("- Routing: impl owns the slices")

    assert floor["triggered"] is True
    assert floor["satisfied"] is False
    assert "designing its successor" in floor["reason"]


def test_a_named_successor_satisfies_the_floor() -> None:
    floor = _cues(
        "- Routing: impl\n"
        "- Successor goal: charness-artifacts/goals/2026-08-08-repair-the-root.md"
    )

    assert floor["satisfied"] is True
    assert floor["evidence"] == "ref"


def test_only_a_substantive_opt_out_can_decline_a_successor() -> None:
    """The opt-out is where "do not design one" gets said out loud. A one-word
    bypass would let the floor be discharged by typing `n/a`, which is how a
    standing operator instruction quietly stops applying."""
    assert _cues("- Successor goal: n/a — nope")["satisfied"] is False
    assert (
        _cues("- Successor goal: n/a — operator asked for no successor this cycle")[
            "satisfied"
        ]
        is True
    )


def test_the_successor_floor_grandfathers_goals_created_before_it() -> None:
    assert cf.successor_goal_floor_applies("Created: 2026-08-07\n") is True  # inclusive
    assert cf.successor_goal_floor_applies("Created: 2026-08-06\n") is False
    assert _cues("- Routing: impl", created="2026-08-06")["triggered"] is False


def test_optout_census_is_produced_by_the_real_closeout_path(tmp_path: Path) -> None:
    """Wiring, not unit behavior: the census tests drive the three appliers
    directly, so deleting the `apply_coordination_optout_aggregate` call in
    `goal_artifact_closeout_evidence.py` would leave every one of them green.
    This is the test that fails if the census is never actually computed.
    """
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path,
        _full_goal(
            created=created,
            context_sources=_URL_SOURCE,
            coordination=(
                "Routing: impl — selected from installed metadata\n"
                "Gather: n/a — the external link is background context, never routed\n"
            ),
        ),
    )
    agg = report["coordination_optout_aggregate"]
    assert "gather" in agg["opted_out_obligations"]
    assert agg["reason"].startswith("this goal opted out of 1 of its")

