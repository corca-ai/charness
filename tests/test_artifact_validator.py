from __future__ import annotations

import sys
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
_artifact_validator = import_repo_module(
    ROOT / "scripts" / "artifacts" / "artifact_validator.py",
    "scripts.artifacts.artifact_validator",
)


def test_validate_max_words_reports_actual_count_and_overage() -> None:
    # An over-budget artifact must name the actual line count and the overage so a
    # run trims in one pass instead of a manual wc-l loop against an unseen ceiling.
    with pytest.raises(_artifact_validator.ValidationError) as excinfo:
        _artifact_validator.validate_max_words(["x"] * 205, max_words=180, artifact_label="debug artifact")
    message = str(excinfo.value)
    assert "should stay concise" in message  # substring other gates match on
    assert "205 words" in message
    assert "under 180" in message
    assert "cut ~25" in message


def test_validate_max_words_accepts_within_budget() -> None:
    _artifact_validator.validate_max_words(["x"] * 180, max_words=180, artifact_label="debug artifact")

def test_scaffold_hint_names_the_owning_scaffold_command() -> None:
    # A violation report that names only WHAT is wrong makes the author rediscover
    # the shape one failed run at a time; the hint names the command that emits it.
    for artifact_type, scaffold in (
        ("debug", "skills/public/debug/scripts/scaffold_debug_artifact.py"),
        ("critique", "skills/public/critique/scripts/scaffold_critique_artifact.py"),
        ("retro", "skills/public/retro/scripts/scaffold_retro_artifact.py"),
        ("ideation", "skills/public/ideation/scripts/scaffold_ideation_artifact.py"),
    ):
        hint = _artifact_validator.scaffold_hint(artifact_type)
        assert hint is not None
        assert f"python3 {scaffold} --repo-root ." in hint


def test_scaffold_hint_also_names_the_skill_that_holds_the_discipline() -> None:
    """The scaffold and the skill teach different halves.

    A session hand-authored an artifact and hit three refusals in a row -- what the
    size budget charges for, that an owner must sit ON its entry, and that
    paraphrasing a second artifact beside an owner still fills the budget. All
    three were already in the skill body. The hint pointed only at the scaffold,
    which emits shape, so following it faithfully still would not have taught
    them.
    """
    for artifact_type, skill in (
        ("retro", "charness:retro"),
        ("quality", "charness:quality"),
    ):
        hint = _artifact_validator.scaffold_hint(artifact_type)
        assert hint is not None
        assert f"`{skill}` skill" in hint, hint


def test_the_named_skill_is_derived_from_the_scaffold_path_not_a_second_map() -> None:
    """A parallel artifact-type -> skill mapping would rot against the one it
    duplicates, so the owner is read off the declared scaffold path."""
    for artifact_type in ("retro", "quality"):
        scaffold = _artifact_validator._scaffold_rel(artifact_type)
        skill = _artifact_validator._skill_id(artifact_type)
        assert skill == f"charness:{Path(scaffold).parts[2]}"

    # A registered type whose scaffold is not a public skill names no skill
    # rather than guessing one.
    assert _artifact_validator._skill_id("goal-closeout") is None


def test_scaffold_hint_is_absent_for_an_unregistered_type() -> None:
    assert _artifact_validator.scaffold_hint("not-a-registered-artifact-type") is None
    assert _artifact_validator._skill_id("not-a-registered-artifact-type") is None


def test_report_validation_failure_emits_the_hint_once(capsys) -> None:
    code = _artifact_validator.report_validation_failure(
        "2 debug artifact rule violation(s):\n- a\n- b", artifact_type="debug"
    )
    err = capsys.readouterr().err
    assert code == 1  # hint only; the verdict and exit code are unchanged
    assert err.count("hint: start from the owning scaffold") == 1


def test_validate_max_words_points_at_the_scaffold_budget() -> None:
    with pytest.raises(_artifact_validator.ValidationError) as excinfo:
        _artifact_validator.validate_max_words(
            ["x"] * 240, max_words=180, artifact_label="debug artifact", artifact_type="debug"
        )
    assert "`size_budget.max_words`" in str(excinfo.value)


def _run_shared_runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, **kwargs: object) -> int:
    # The shared runner IS the whole main() of every changed-path validator, so
    # it reads sys.argv rather than taking an argv list; a new artifact family
    # inherits these two resolution edges without writing a line of its own.
    monkeypatch.setattr(sys, "argv", ["validator", "--repo-root", str(tmp_path)])
    return _artifact_validator.run_changed_artifact_validator(
        default_repo_root=tmp_path,
        all_help="all",
        artifact_label="demo artifact",
        validate_factory=lambda run: (lambda artifact: None),
        fail_fast_help="stop at the first violation",
        **kwargs,
    )


def test_shared_runner_refuses_a_validator_that_resolves_no_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Neither resolver hook wired is an authoring mistake in the CALLER, not a
    # run with nothing in scope: without this the validator would report
    # `Validated 0 demo artifact(s).` and pass forever over an empty set.
    with pytest.raises(TypeError) as excinfo:
        _run_shared_runner(tmp_path, monkeypatch)
    assert "candidate_paths_fn or artifacts_fn" in str(excinfo.value)


def test_shared_runner_reports_nothing_in_scope_as_a_named_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # `artifacts_fn` returning None means "nothing in scope" — a success for the
    # common commit that touches no artifact of this family. The message must be
    # the caller's own so the operator learns WHICH family was empty.
    code = _run_shared_runner(
        tmp_path,
        monkeypatch,
        artifacts_fn=lambda run: None,
        no_scope_message="No demo artifact directory here.",
    )
    assert code == 0
    assert "No demo artifact directory here." in capsys.readouterr().out


def test_shared_runner_falls_back_to_the_labelled_no_scope_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    code = _run_shared_runner(tmp_path, monkeypatch, artifacts_fn=lambda run: None)
    assert code == 0
    assert "No demo artifacts in scope." in capsys.readouterr().out
