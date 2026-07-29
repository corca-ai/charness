"""In-process pins for `publish_release_narrative_gate.py`, the publish-boundary
wrapper around the narrative audit.

The audit rules themselves are pinned by `test_release_narrative_audit.py`
through the CLI. What had no test at all is the wrapper: three entrypoints whose
whole contribution is WHEN publish is refused and whether the refusal carries the
blockers. Two of them raise `SystemExit` before publish; the post-publish reader
must not, because the release already exists by then.

`run_notes_file_preflight` has no `notes_file is None` early return any more: the
drafted-notes arm runs on BOTH branches, because handing over the wrong file
satisfies its premise exactly as `--generate-notes` did. The `--generate-notes`
path is still a live publish shape and is still pinned here — but only as
"silent when this repo drafts no notes for the tag", which is a different claim
than the early return used to make.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tests.script_loader import load_script_module

from .support import ROOT

GATE = load_script_module(
    "publish_release_narrative_gate_under_test",
    ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_narrative_gate.py",
)


def test_notes_file_preflight_refuses_a_mutable_pointer_before_publish(tmp_path: Path) -> None:
    notes = tmp_path / "notes.md"
    notes.write_text("See https://github.com/o/r/blob/main/docs/x.md\n", encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        GATE.run_notes_file_preflight(tmp_path, target_tag="v0.1.0", notes_file=notes)

    message = str(excinfo.value)
    assert "public release notes preflight blocked publish" in message
    assert "docs/x.md" in message


def test_notes_file_preflight_names_a_notes_file_that_is_not_there(tmp_path: Path) -> None:
    # A `--notes-file` the publish cannot read is not "no pointers found": the
    # pointer rule never ran, and publish must stop rather than pass by absence.
    missing = tmp_path / "gone.md"

    with pytest.raises(SystemExit) as excinfo:
        GATE.run_notes_file_preflight(tmp_path, target_tag="v0.1.0", notes_file=missing)

    assert f"public release notes file missing: {missing}" in str(excinfo.value)


def test_notes_file_preflight_passes_a_pinned_notes_file(tmp_path: Path) -> None:
    notes = tmp_path / "notes.md"
    notes.write_text("See https://github.com/o/r/blob/v0.1.0/docs/x.md\n", encoding="utf-8")

    GATE.run_notes_file_preflight(tmp_path, target_tag="v0.1.0", notes_file=notes)


def _seed_release_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/release\n", encoding="utf-8"
    )
    return repo


def test_notes_file_preflight_is_a_no_op_on_the_generate_notes_path(tmp_path: Path) -> None:
    # `--generate-notes` passes no notes_file. With no notes drafted for the tag
    # the preflight must not invent a refusal.
    #
    # Seeded with a REAL adapter and a REAL (empty) output_dir: with a bare
    # `tmp_path` the drafted-notes arm returns early on the absent directory, so
    # this passed without ever reaching the branch it is named for.
    repo = _seed_release_repo(tmp_path)
    (repo / "charness-artifacts" / "release" / "2026-05-13-v0.9.9-notes.md").write_text(
        "Another release's notes.\n", encoding="utf-8"
    )

    GATE.run_notes_file_preflight(repo, target_tag="v0.1.0", notes_file=None)


def test_notes_file_preflight_refuses_generate_notes_over_a_drafted_note(tmp_path: Path) -> None:
    """The v2.11.0 defect, at the cheap site.

    `run_narrative_audit` refuses this too, but only after the bump and the
    pre-push quality gates; this call site is what makes it a millisecond
    refusal. It had no test at all, so deleting it from the preflight would not
    have failed anything."""
    repo = _seed_release_repo(tmp_path)
    drafted = repo / "charness-artifacts" / "release" / "2026-05-13-v0.1.0-notes.md"
    drafted.write_text("The operator's notes.\n", encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        GATE.run_notes_file_preflight(repo, target_tag="v0.1.0", notes_file=None)

    message = str(excinfo.value)
    assert "public release notes preflight blocked publish" in message
    assert "2026-05-13-v0.1.0-notes.md" in message

    # Handing the draft over is the whole remedy.
    GATE.run_notes_file_preflight(repo, target_tag="v0.1.0", notes_file=drafted)


def test_notes_file_preflight_names_a_missing_path_before_the_drafted_arm(tmp_path: Path) -> None:
    """A mistyped `--notes-file` must be told it does not exist.

    With the drafted arm running first, the typo produced only "which is none of
    them" — true, and silent about the actual mistake."""
    repo = _seed_release_repo(tmp_path)
    (repo / "charness-artifacts" / "release" / "v0.1.0-notes.md").write_text("notes", encoding="utf-8")
    typo = repo / "charness-artifacts" / "release" / "v0.1.0-note.md"

    with pytest.raises(SystemExit) as excinfo:
        GATE.run_notes_file_preflight(repo, target_tag="v0.1.0", notes_file=typo)

    assert "notes file missing" in str(excinfo.value)


def test_drafted_notes_lookup_defers_to_build_payload_on_an_invalid_adapter(tmp_path: Path) -> None:
    """An unreadable adapter is `build_payload`'s blocker, with its own message.
    The preflight must not pre-empt it with a listing failure."""
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "release-adapter.yaml").write_text("not: a valid adapter\n", encoding="utf-8")

    assert GATE._drafted_notes_for(repo, target_tag="v0.1.0") == []
    GATE.run_notes_file_preflight(repo, target_tag="v0.1.0", notes_file=None)


def test_narrative_audit_refusal_carries_every_blocker(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        GATE,
        "build_narrative_audit_payload",
        lambda repo_root, **kwargs: {"status": "blocked", "blockers": ["first blocker", "second blocker"]},
    )

    with pytest.raises(SystemExit) as excinfo:
        GATE.run_narrative_audit(tmp_path, target_tag="v0.1.0")

    message = str(excinfo.value)
    assert "public release narrative audit blocked publish" in message
    assert "- first blocker" in message
    assert "- second blocker" in message


def test_narrative_audit_is_silent_when_the_artifact_supports_the_publish(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        GATE,
        "build_narrative_audit_payload",
        lambda repo_root, **kwargs: {"status": "passed", "blockers": []},
    )

    GATE.run_narrative_audit(tmp_path, target_tag="v0.1.0")


def test_bootstrap_resolution_refuses_a_copy_with_no_runtime_bootstrap(monkeypatch) -> None:
    # The module resolves its shared runtime by walking ancestors for
    # `skill_runtime_bootstrap.py`. A copy vendored without it cannot load the
    # audit rules at all, so import must fail loudly rather than leave the gate
    # bound to a half-resolved namespace.
    #
    # The module-local `Path` name is replaced rather than `pathlib.Path.is_file`
    # itself: patching the real method would make every `is_file()` call in the
    # worker process — including pytest's own path machinery — return False.
    class NoParentPath:
        def __init__(self, _value: str) -> None:
            pass

        def resolve(self):
            return self

        @property
        def parents(self) -> list[Path]:
            return []

    monkeypatch.setattr(GATE, "Path", NoParentPath)

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        GATE._load_skill_runtime_bootstrap()
