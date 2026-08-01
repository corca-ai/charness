"""Floors on the goal artifact's own closeout record.

Both floors here were built because a checked-in closeout-claims review found the
defects in a real goal's `## Final Verification`, not because they were imagined.
Each is form/identity only: neither decides whether a citation is honest or
whether a review was independent, because neither question is decidable from a
checked-in file, and a validator that pretended otherwise would ship as the
Goodhart proxy this repo refuses.
"""
from __future__ import annotations

import importlib.util
from datetime import date, timedelta

from .support import ROOT

SCRIPT_DIR = ROOT / "skills" / "public" / "achieve" / "scripts"
IN_SCOPE = "2026-08-01"
GRANDFATHERED = "2026-07-01"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _artifact(created: str, final_verification: str) -> str:
    return (
        f"# Goal\n\nCreated: {created}\nStatus: complete\n\n"
        f"## Final Verification\n\n{final_verification}\n"
    )


# --- figure form ------------------------------------------------------------


def _figure_check(created: str, body: str) -> dict:
    return _load("goal_artifact_figure_form").check(_artifact(created, body))


def test_a_bare_figure_is_refused() -> None:
    """The defect itself: a number a later session plans against, with no source."""
    result = _figure_check(IN_SCOPE, "- Mutation score was 94.9% across the suite.")

    assert result["applies"] is True
    assert result["ok"] is False
    assert result["figure_lines"] == 1
    assert "no ` — ` separator" in result["offenders"][0]["reason"]


def test_a_sourced_figure_passes() -> None:
    result = _figure_check(
        IN_SCOPE,
        "- Mutation score 94.9% — `cosmic-ray dump reports/mutation/session.sqlite`",
    )

    assert result["ok"] is True
    assert result["figure_lines"] == 1


def test_an_explicitly_unbacked_figure_passes_with_a_reason() -> None:
    """The escape hatch is the point: an honest closeout can state an unmeasured
    number, as long as it says so. Without this arm the floor would push authors
    to delete inconvenient figures rather than label them."""
    result = _figure_check(
        IN_SCOPE, "- Roughly 40 sessions affected — unbacked: no host log retains that window"
    )

    assert result["ok"] is True


def test_a_bare_unbacked_marker_is_refused() -> None:
    """`unbacked:` with no reason is the floor satisfied by a magic word."""
    result = _figure_check(IN_SCOPE, "- Roughly 40 sessions affected — unbacked: n/a")

    assert result["ok"] is False


def test_prose_after_the_separator_is_not_a_source() -> None:
    result = _figure_check(IN_SCOPE, "- Mutation score 94.9% — this was verified carefully")

    assert result["ok"] is False
    assert "prose with no path, command, or URL" in result["offenders"][0]["reason"]


def test_tokens_that_are_digits_without_being_figures_do_not_trigger() -> None:
    """The false-refusal direction is the dangerous one: a gate that fires on
    dates, versions, issue refs, and paths would make an ordinary closeout
    unrecordable and train people to pad text until it passes."""
    body = "\n".join(
        [
            "- Landed on 2026-08-01 with no rollback.",
            "- Released as v3.0.1 to the plugin surface.",
            "- Tracked in #467 and closed there.",
            "- Wrote scripts/check_doc_links.py and its test.",
            "- Gate took 40.7s on this machine.",
        ]
    )
    result = _figure_check(IN_SCOPE, body)

    assert result["figure_lines"] == 0, result.get("offenders")
    assert result["ok"] is True


def test_a_figure_inside_a_code_fence_is_the_author_showing_a_shape() -> None:
    text = (
        f"# Goal\n\nCreated: {IN_SCOPE}\nStatus: complete\n\n"
        "## Final Verification\n\n"
        "```\n- Mutation score 94.9%\n```\n"
    )
    result = _load("goal_artifact_figure_form").check(text)

    assert result["figure_lines"] == 0
    assert result["ok"] is True


def test_evidence_lines_are_left_to_their_own_floor() -> None:
    """A retro path can contain digits; reading it as a figure would double-refuse
    one defect and hide which floor to fix."""
    result = _figure_check(
        IN_SCOPE, "Retro: charness-artifacts/retro/2026-08-01-v3-0-1-retro.md"
    )

    assert result["figure_lines"] == 0
    assert result["ok"] is True


def test_figure_floor_grandfathers_a_prior_goal() -> None:
    """Without this, a floor landing today is in scope for every prior goal, and
    the only way to green those is to edit frozen artifacts."""
    result = _figure_check(GRANDFATHERED, "- Mutation score was 94.9% across the suite.")

    assert result["applies"] is False
    assert result["ok"] is True
    assert result["evaluated"] is False
    assert result["rule_date"] == "2026-08-01"
    # The scope verdict rests on a line the author wrote, with no corroborating
    # channel, and the reason has to say so rather than read as established fact.
    assert "self-declared" in result["reason"]


def test_figure_floor_rule_date_is_not_in_the_future() -> None:
    """A rule date after today would silently grandfather every goal forever."""
    module = _load("goal_artifact_figure_form")

    assert module.FIGURE_FORM_RULE_DATE <= date.today() + timedelta(days=1)


# --- evidence distinctness --------------------------------------------------


def _distinctness_check(created: str, retro: str, review: str) -> dict:
    report = {
        "satisfied": [
            {"name": "retro_artifact", "via": "evidence", "path": retro},
            {"name": "disposition_review", "via": "evidence", "path": review},
        ]
    }
    return _load("goal_artifact_evidence_distinctness").check(report, _artifact(created, "x"))


def test_one_file_cannot_be_both_the_record_and_its_own_review() -> None:
    same = "charness-artifacts/retro/2026-08-01-a-retro.md"
    result = _distinctness_check(IN_SCOPE, same, same)

    assert result["applies"] is True
    assert result["ok"] is False
    assert "resolve to the same file" in result["reason"]


def test_two_distinct_paths_pass() -> None:
    result = _distinctness_check(
        IN_SCOPE,
        "charness-artifacts/retro/2026-08-01-a-retro.md",
        "charness-artifacts/critique/2026-08-01-a-claims-review.md",
    )

    assert result["ok"] is True


def test_the_same_file_reached_by_two_spellings_is_still_one_file() -> None:
    """Path identity, not string identity: `./x.md` and `x.md` are one artifact."""
    result = _distinctness_check(
        IN_SCOPE,
        "charness-artifacts/retro/2026-08-01-a-retro.md",
        "./charness-artifacts/retro/2026-08-01-a-retro.md",
    )

    assert result["ok"] is False


def test_a_skipped_review_does_not_collide_with_the_retro() -> None:
    """A host-blocked subagent recorded as `skipped:` has no path. Refusing it
    would punish the documented degradation instead of the defect."""
    report = {
        "satisfied": [
            {"name": "retro_artifact", "via": "evidence", "path": "a/retro.md"},
            {"name": "disposition_review", "via": "skip", "reason": "host-blocked-subagent"},
        ]
    }
    result = _load("goal_artifact_evidence_distinctness").check(
        report, _artifact(IN_SCOPE, "x")
    )

    assert result["ok"] is True
    assert "nothing to compare" in result["reason"]


def test_distinctness_floor_grandfathers_a_prior_goal() -> None:
    same = "charness-artifacts/retro/2026-07-01-a-retro.md"
    result = _distinctness_check(GRANDFATHERED, same, same)

    assert result["applies"] is False
    assert result["ok"] is True


def test_distinctness_floor_does_not_claim_to_check_authorship() -> None:
    """Pinned as a NON-claim, deliberately: the stronger rule ("a different
    author reviewed this") is unbuildable, and the docstring must keep saying so
    rather than letting a reader assume path-distinctness proves independence."""
    source = (SCRIPT_DIR / "goal_artifact_evidence_distinctness.py").read_text(encoding="utf-8")

    assert "does not check that the two files have different AUTHORS" in source
    assert "authorship PROXY" in source


def test_the_figure_floor_is_a_captured_observable_not_a_refusal() -> None:
    """Pinned so nobody arms it without redoing the measurement.

    Armed, it refuses frozen same-day goal artifacts, and the only way to green
    those is to edit finished records to satisfy a rule written after them. The
    non-blocking posture is a decision with a reason, not an oversight, so the
    test asserts the wiring rather than trusting the comment.
    """
    module = _load("goal_artifact_figure_form")
    report = {"ok": True}
    module.apply_figure_form_floor(report, _artifact(IN_SCOPE, "- Score was 94.9% overall."))

    fragment = report["final_verification_figure_form"]
    assert fragment["ok"] is False, "the form question still gets a real answer"
    assert fragment["blocking"] is False
    assert fragment["figure_lines"] == 1, "publishes its own denominator"
    assert report["ok"] is True, "must not flip the caller's verdict"


def test_the_armed_figure_floor_would_refuse_frozen_artifacts() -> None:
    """The measurement the deferral rests on, executed rather than asserted.

    If a later change makes the corpus clean, this test fails and the deferral
    should be revisited — which is the point of pinning a premise instead of a
    conclusion.
    """
    module = _load("goal_artifact_figure_form")
    goals = sorted((ROOT / "charness-artifacts" / "goals").glob("*.md"))
    refused = []
    for path in goals:
        result = module.check(path.read_text(encoding="utf-8"))
        if result["applies"] and not result["ok"]:
            refused.append(path.name)

    assert refused, (
        "the armed floor no longer refuses any checked-in goal; the deferral in "
        "apply_figure_form_floor rests on that refusal and should be revisited"
    )
