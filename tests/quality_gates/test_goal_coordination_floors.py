"""Tests for the gather + release coordination closeout floors.

Loads ``goal_artifact_coordination_floors.py`` (the leaf floor module) and
``goal_artifact_closeout_evidence.py`` (the wrapper that calls it) **directly**,
mirroring ``test_goal_disposition_gate.py``: the achieve lib sits near the
single-file line gate, so the tests must not force a new re-export through it.
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


cf = _load("goal_artifact_coordination_floors")
ce = _load("goal_artifact_closeout_evidence")
gal = _load("goal_artifact_lib")


# --- grandfather-by-Created-date -------------------------------------------


def test_grandfather_inclusive_of_rule_date() -> None:
    assert cf.coordination_floors_apply("Created: 2026-05-31\n") is True  # inclusive
    assert cf.coordination_floors_apply("Created: 2026-06-02\n") is True
    assert cf.coordination_floors_apply("Created: 2026-05-30\n") is False  # same-day, grandfathered
    assert cf.coordination_floors_apply("Created: 2026-05-29\n") is False


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
    assert "coordination_missing" not in report
    assert report["ok"] is True


def test_gather_triggered_without_step_refuses(tmp_path: Path) -> None:
    created = "2026-05-31"
    _seed_other_evidence(tmp_path, created)
    report = ce.check_complete_evidence(
        tmp_path, _full_goal(created=created, context_sources=_URL_SOURCE, coordination="Routing: see find-skills\n")
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
            coordination="Routing: see find-skills\n",
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
            coordination="Routing: see find-skills\n",
            release_work="- bumped via bump_version.py\n",
        ),
    )
    assert {e["floor"] for e in report["coordination_missing"]} == {"gather", "release"}
    assert report["ok"] is False
