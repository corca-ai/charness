"""In-process pins for `publish_release_narrative_gate.py`, the publish-boundary
wrapper around the narrative audit.

The audit rules themselves are pinned by `test_release_narrative_audit.py`
through the CLI. What had no test at all is the wrapper: three entrypoints whose
whole contribution is WHEN publish is refused and whether the refusal carries the
blockers. Two of them raise `SystemExit` before publish; the post-publish reader
must not, because the release already exists by then.

`run_notes_file_preflight`'s `notes_file is None` early return is the
`--generate-notes` path, where the notes are composed at creation time and there
is no file to inspect beforehand. That branch is a live publish shape, not a
defensive stub, so it is pinned here alongside the refusal it skips.
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


def test_notes_file_preflight_is_a_no_op_on_the_generate_notes_path(tmp_path: Path) -> None:
    # `--generate-notes` passes no notes_file. The pointer rule then has nothing
    # to read before publish, and `audit_notes_text` owns the published body
    # afterwards; the preflight must not invent a refusal here.
    GATE.run_notes_file_preflight(tmp_path, target_tag="v0.1.0", notes_file=None)


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
