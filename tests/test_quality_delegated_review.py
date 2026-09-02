"""Delegated-review floors for the quality artifact validator.

Split out of `test_quality_artifact.py`, which sits in the length gate's warn band;
the shared repo/artifact fixtures still live there.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module
from tests.test_quality_artifact import seed_repo

_validate_quality_artifact = import_repo_module(__file__, "scripts.gates.validate_quality_artifact")
ValidationError = _validate_quality_artifact.ValidationError


def validate(repo: Path) -> None:
    """Run the validator in-process: the CLI boundary is proven elsewhere.

    `tests/test_quality_artifact_report_all.py` owns the subprocess contract
    (default one-pass vs fail-fast, stderr shape, exit status); spawning it again per
    rule is a redundant delivery-boundary exercise.
    """
    _validate_quality_artifact.validate_quality_artifact(
        repo / "charness-artifacts" / "quality" / "latest.md", repo_root=repo
    )


def artifact_with_delegated_review(*section_lines: str) -> str:
    """A valid artifact whose `## Delegated Review` section is the variable under test."""
    return (
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-20",
                "## Scope",
                "- demo",
                "## Surface Contract Review",
                "- semantic coverage: `observed` — contract packet is covered.",
                "- surface: demo surface",
                "- owner: demo owner",
                "- projections: DOM and command output",
                "- state scope: request",
                "- transitions: success and failure",
                "- proof boundary: focused test",
                "- unexamined axes: none",
                "## Current Gates",
                "- gate",
                "## Runtime Signals",
                "- runtime source: structured metrics from `.charness/quality/runtime-signals.json`"
                " rendered by `render_runtime_summary.py` via `scripts/gates_support/record_quality_runtime.py`.",
                "- runtime hot spots: `pytest` 10s",
                "- coverage gate: none",
                "- evaluator depth: adapter bootstrap only",
                "## Healthy",
                "- healthy",
                "## Weak",
                "- weak",
                "## Missing",
                "- missing",
                "## Deferred",
                "- deferred",
                "## Advisory",
                "- none found by inventory: `inventory_adapter_gate_design.py`.",
                "## Delegated Review",
                *section_lines,
                "## Commands Run",
                "- cmd",
                "## Recommended Next Quality Moves",
                "- active AUTO_CANDIDATE: next",
                "## History",
                "- [archive](history/one.md)",
            ]
        )
        + "\n"
    )


def test_validate_quality_artifact_rejects_unsubstantiated_executed_delegated_review(
    tmp_path: Path,
) -> None:
    """Sweep S11: `executed` alone certified a review that named nothing that ran."""
    repo = seed_repo(tmp_path, artifact_with_delegated_review("- status: executed."))
    with pytest.raises(
        ValidationError, match=re.escape("executed delegated review must name the review channel")
    ):
        validate(repo)


def test_validate_quality_artifact_rejects_executed_backed_only_by_the_lens_bullet(
    tmp_path: Path,
) -> None:
    """The standing slow-gate lens bullet is scaffold boilerplate, not substantiation."""
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review(
            "- Delegated Review: executed.",
            "- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):"
            " not re-delegated.",
        ),
    )
    with pytest.raises(
        ValidationError, match=re.escape("executed delegated review must name the review channel")
    ):
        validate(repo)


def test_validate_quality_artifact_rejects_executed_that_states_no_review_ran(
    tmp_path: Path,
) -> None:
    """The stub the sweep reproduced: `executed` plus a confession that nothing ran."""
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review(
            "- status: executed (no reviewer, no findings, nothing ran)."
        ),
    )
    with pytest.raises(ValidationError, match=re.escape("must not also state that no review ran")):
        validate(repo)


def test_validate_quality_artifact_accepts_substantiated_executed_delegated_review(
    tmp_path: Path,
) -> None:
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review(
            "- Delegated Review: executed — one bounded fresh-eye reviewer returned no blocking"
            " findings; the boundary fingerprint reported no reviewer worktree/index drift.",
        ),
    )
    validate(repo)


def test_validate_quality_artifact_reads_the_declared_delegated_review_status(
    tmp_path: Path,
) -> None:
    """A `not_applicable` section that merely mentions `executed` must not arm the floor.

    The body here would be refused verbatim under `executed`, so passing proves the
    floor keys on the declared status rather than on any status word in the section.
    """
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review(
            "- Delegated Review: not_applicable — no delegated review ran for this typo fix;"
            " TODO record executed with the reviewer verdict when one does.",
        ),
    )
    validate(repo)


def test_validate_quality_artifact_rejects_executed_that_denies_a_reviewer(tmp_path: Path) -> None:
    """S11's stub minus its `nothing ran` clause: the same false green, two words shorter.

    Caught by the substantiation arm rather than the contradiction arm — every marker
    this section names, it also negates.
    """
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review("- status: executed (no reviewer, no findings)."),
    )
    with pytest.raises(
        ValidationError, match=re.escape("executed delegated review must name the review channel")
    ):
        validate(repo)


def test_validate_quality_artifact_keeps_the_boundary_fingerprint_phrasing_legal(
    tmp_path: Path,
) -> None:
    """`no reviewer worktree/index/HEAD drift` is real checked-in text, not a confession."""
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review(
            "- Delegated Review: executed — a bounded reviewer returned two findings; the parent"
            " boundary fingerprint reported no reviewer worktree/index/HEAD drift.",
        ),
    )
    validate(repo)


def test_validate_quality_artifact_ignores_fill_guard_comments_in_delegated_review(
    tmp_path: Path,
) -> None:
    """A template comment is guidance, not the author's claim — on either arm.

    Left readable, the scaffold's guard both trips the contradiction arm (it contains
    "no review ran") and satisfies the substantiation arm (it lists the whole
    vocabulary), so it would turn the floor into a no-op for every scaffolded artifact.
    """
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review(
            "- Delegated Review: executed.",
            "<!-- fill guard: name the reviewer, the critique angle, the counterweight, or the"
            " findings it returned; a section that also states no review ran is refused -->",
        ),
    )
    with pytest.raises(
        ValidationError, match=re.escape("executed delegated review must name the review channel")
    ):
        validate(repo)


def test_validate_quality_artifact_accepts_a_cited_review_record_as_substantiation(
    tmp_path: Path,
) -> None:
    """The language-neutral arm: every vocabulary marker is English, the validator ships.

    A consuming repo whose adapter `language:` is not English substantiates by citing
    the review record instead of writing an English review noun.
    """
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review(
            "- Delegated Review: executed — 검토 결과는"
            " `charness-artifacts/quality/history/2026-04-20-demo.md` 에 기록.",
        ),
    )
    validate(repo)


def test_validate_quality_artifact_rejects_a_modified_reviewer_denial(tmp_path: Path) -> None:
    """`no bounded reviewer ran` is the same denial one adjective wider."""
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review(
            "- status: executed (no bounded reviewer ran, nothing found)."
        ),
    )
    with pytest.raises(ValidationError, match=re.escape("must not also state that no review ran")):
        validate(repo)


def test_validate_quality_artifact_keeps_a_negative_review_result_legal(tmp_path: Path) -> None:
    """A reviewer finding nothing is a RESULT, not a denial that the reviewer ran.

    Both phrasings below are checked-in critique text; refusing them would push authors
    to delete honest scope limits from a section whose whole job is disclosure.
    """
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review(
            "- Delegated Review: executed — the round-1 reviewer returned two findings and no"
            " reviewer identified a functional blocker after the repair; no reviewer saw the"
            " post-fix tree.",
        ),
    )
    validate(repo)


def test_validate_quality_artifact_does_not_count_negated_markers_as_substantiation(
    tmp_path: Path,
) -> None:
    """S11's stub names the whole vocabulary while denying every word of it."""
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review(
            "- Delegated Review: executed — no reviewer was found on this host; findings are mine.",
        ),
    )
    with pytest.raises(ValidationError):
        validate(repo)


def test_validate_quality_artifact_rejects_slash_filler_as_a_cited_record(tmp_path: Path) -> None:
    """The language-neutral arm needs a path shape; `n/a` is not a review record."""
    repo = seed_repo(tmp_path, artifact_with_delegated_review("- status: executed `n/a`."))
    with pytest.raises(
        ValidationError, match=re.escape("executed delegated review must name the review channel")
    ):
        validate(repo)


def test_validate_quality_artifact_strips_a_fill_guard_wrapped_across_lines(tmp_path: Path) -> None:
    """Comment stripping must survive a reflowed guard, or both defects come back.

    Line-by-line stripping leaves a wrapped guard fully readable: half of it is free
    substantiation and the other half trips the contradiction arm on boilerplate.
    """
    repo = seed_repo(
        tmp_path,
        artifact_with_delegated_review(
            "- Delegated Review: executed.",
            "<!-- fill guard: name the reviewer, the counterweight,",
            "or the findings it returned; a section that also says no reviewer ran is refused -->",
        ),
    )
    with pytest.raises(
        ValidationError, match=re.escape("executed delegated review must name the review channel")
    ):
        validate(repo)


def test_declared_delegated_review_status_is_none_without_a_status_line() -> None:
    """The helper reports absence rather than guessing; the section rule owns the refusal."""
    assert (
        _validate_quality_artifact.declared_delegated_review_status(
            ["- the reviewer read the diff.", "- lenses: fixture-economics."]
        )
        is None
    )
