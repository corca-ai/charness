"""The claims floor's refusals, driven IN-PROCESS in the lane that judges coverage.

Every seeded-repo test of these refusals is `release_only`, and the producer behind the
changed-line/mutation gate runs `-m 'not release_only'`. So the refusals were proven by
tests that gate never executes, which to that gate is indistinguishable from no test at
all -- and it blocked on exactly these lines. The same is true of the CLI guard reached
only through a spawned binary: a subprocess is invisible to in-process coverage.

This file holds the driver each one needs and nothing else. It does NOT replace the
seeded-repo tests in `test_release_claims_review.py`: those prove the topology against
real commits and real git, which a scripted `run` cannot.
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from .release_script_loading import load_release_script

CLAIMS_REVIEW = load_release_script("publish_release_claims_review", suffix="in_process")
CLI = load_release_script("publish_release_cli", suffix="in_process")
_RECORD = "charness-artifacts/release/latest.md"


def _scripted_run(answers: dict[tuple[str, ...], str]):
    """A `run` that answers only the git reads a test declares, and fails on any other.

    Unanswered commands raise rather than returning an empty success: a stub that
    silently answers everything lets a refusal pass for the wrong reason, and the
    AssertionError names the command so the miss is legible.
    """
    def run(command, *, cwd=None, check=False):  # noqa: ARG001 - mirrors the real signature
        key = tuple(str(part) for part in command)
        if key not in answers:
            raise AssertionError(f"unscripted git read: {list(key)}")
        return SimpleNamespace(returncode=0, stdout=answers[key], stderr="")

    return run


def _unreachable_run(*_args, **_kwargs):
    raise AssertionError("the missing-artifact refusal must precede every git read")


def test_the_same_refusal_fires_in_process_where_coverage_can_see_it(monkeypatch, tmp_path: Path) -> None:
    """`test_release_claims_review.py::test_publish_cli_refuses_claims_artifact_without_resume`
    spawns the real binary and proves the OPERATOR-visible behaviour, and nothing else.

    A refusal reached only through a spawned binary is invisible to in-process coverage,
    so the mutation lane drops the line and the guard reads as unproven -- which is what
    it did. Same guard, driven in-process: the refusal precedes every adapter read and
    every git call in `main`, so it needs no repo at all.
    """
    monkeypatch.setattr(sys, "argv", [
        "publish_release.py", "--repo-root", str(tmp_path), "--part", "patch",
        "--claims-review-artifact", "charness-artifacts/release-review/review.json",
    ])

    with pytest.raises(SystemExit, match="only valid with --resume --publish-current"):
        CLI.main()


def test_validate_claims_review_refuses_a_prepared_stop_with_no_artifact(tmp_path: Path) -> None:
    """The prepared stop's own precondition, and the first thing the floor checks.

    Without it the resume reaches a claims phase carrying no record, and every later
    binding check has nothing to bind against -- the floor would pass by having nothing
    to refuse, which is the fall-through shape this whole module exists to close.
    """
    with pytest.raises(SystemExit, match="prepared claims-review state requires --claims-review-artifact"):
        CLAIMS_REVIEW.validate_claims_review(
            tmp_path, prepared={"commit": "abc", "path": _RECORD, "sha256": "0" * 64},
            evidence_commit="def", artifact_path=None, target_version="1.2.3",
            tag_name="v1.2.3", run=_unreachable_run,
        )


def test_validate_claims_review_refuses_evidence_that_is_not_the_direct_child(tmp_path: Path) -> None:
    """The topology this module is named for, driven without a real repo.

    A seeded-repo test proves it too, but every one of those is `release_only`, so the
    lane that judges changed-line coverage never runs them and the refusal read as
    unproven. Parenthood is the only thing under test here, so a scripted `run` is the
    honest driver: it fixes the one fact the assertion depends on and cannot pass by
    accidentally reproducing some other part of the flow.
    """
    with pytest.raises(SystemExit, match="must be the direct child of the prepared release record"):
        CLAIMS_REVIEW.validate_claims_review(
            tmp_path, prepared={"commit": "prepared", "path": _RECORD, "sha256": "0" * 64},
            evidence_commit="evidence",
            artifact_path="charness-artifacts/release-review/review.json",
            target_version="1.2.3", tag_name="v1.2.3",
            run=_scripted_run({("git", "show", "-s", "--format=%P", "evidence"): "someone-else"}),
        )


def test_a_merge_cannot_be_the_prepared_record_even_when_it_carries_the_marker() -> None:
    """A one-parent P boundary, and a merge is not one.

    A merge can RETAIN the marker from a non-first parent while appearing to introduce it
    against its first parent, which is exactly the reclassification `prepared_record`
    narrows against -- accept it and the review boundary shifts onto a commit no reviewer
    read. Refused before the parent record is ever fetched, so the scripted `run` refuses
    to answer that question at all.
    """
    marker_text = f"# release\n{CLAIMS_REVIEW.MARKER}\n"
    run = _scripted_run({
        ("git", "show", f"merge:{_RECORD}"): marker_text,
        ("git", "show", "-s", "--format=%P", "merge"): "parent-a parent-b",
    })

    assert CLAIMS_REVIEW.prepared_record(
        Path("."), commit="merge", record_path=_RECORD, run=run
    ) is None
