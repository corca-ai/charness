"""The refusal branches the changed-line mutation gate named before the 4.0.0 push.

Every branch here is an UNHAPPY path: a wrong-repo answer, a broken install, a
malformed artifact, a path that escapes its root. They shipped uncovered across
the unpushed range, which the changed-line coverage gate refuses at push time --
correctly, because an untested refusal is exactly the shape that quietly stops
refusing.

Grouped by that property rather than by module: each test pins the branch's
CONTRACT (what it refuses and how it says so), not merely that the line runs.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]


def _load_skill_module(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# --- a path outside every known root is returned as-is -----------------------

_pointer_writes = import_repo_module(__file__, "scripts.check_current_pointer_writes")


def test_a_path_outside_repo_and_support_is_returned_unchanged(tmp_path: Path) -> None:
    """Both `relative_to` attempts fail for a path in neither tree. The fallback
    returns the resolved path rather than raising, so a stray location is
    REPORTED rather than crashing the writer scan."""
    outside = tmp_path / "elsewhere" / "pointer.md"
    outside.parent.mkdir(parents=True)
    outside.write_text("x\n", encoding="utf-8")

    resolved = _pointer_writes._display_path(ROOT, outside)

    assert Path(resolved).is_absolute()
    assert "elsewhere" in str(resolved)


# --- a typed capture refusal is not re-wrapped as a config error -------------

_capture = import_repo_module(__file__, "scripts.issue_source_capture_lib")


def _with_owner(owner: object) -> list[str]:
    """Drive `build_page_argv` with a stubbed backend owner."""
    import unittest.mock

    with unittest.mock.patch.object(_capture, "_issue_backend_owner", lambda: owner):
        return _capture.build_page_argv(
            {"commands": {"source_capture": "gh api {repo} {number}"}},
            "owner/repo", 42, 50, None,
        )


def test_a_plain_runtime_error_becomes_an_invalid_capture_command_refusal() -> None:
    """A RuntimeError from the loader is a broken adapter command, and it is
    typed as such so the operator is sent to the adapter."""

    class _Owner:
        def backend_binary(self, _backend):
            raise RuntimeError("adapter command is not runnable")

    with pytest.raises(_capture.CaptureRefusal) as excinfo:
        _with_owner(_Owner())

    assert excinfo.value.code == "invalid_capture_command"
    assert "not runnable" in str(excinfo.value)


def test_an_existing_capture_refusal_passes_through_untouched() -> None:
    """`CaptureRefusal` subclasses RuntimeError, so a broad `except RuntimeError`
    silently re-wrapped an already-correct refusal and sent the operator to the
    adapter for what was a broken INSTALL. The re-raise is what keeps the
    original code."""

    class _Owner:
        def backend_binary(self, _backend):
            raise _capture.CaptureRefusal("missing_backend_module", "partial install")

    with pytest.raises(_capture.CaptureRefusal) as excinfo:
        _with_owner(_Owner())

    assert excinfo.value.code == "missing_backend_module"


# --- an unavailable backend owner is UNKNOWN, never an answer ----------------

_backend = _load_skill_module(
    "skills/public/handoff/scripts/chunked_routing_issue_backend.py",
    "chunked_routing_issue_backend_under_test",
)


def test_an_unavailable_backend_owner_answers_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing or partial install must read as UNKNOWN rather than as a
    wrong-repo answer -- the caller refuses on a mismatch, so returning anything
    but None here would turn an install problem into a false mismatch."""

    def _unavailable():
        raise ImportError("owner module is not installed")

    monkeypatch.setattr(_backend, "_issue_backend_owner", _unavailable)
    assert _backend.answer_repo({"repository": {"nameWithOwner": "owner/repo"}}) is None


# --- close verification refuses an answer about something else ---------------

_issue_close = _load_skill_module(
    "skills/public/issue/scripts/issue_close.py", "issue_close_under_test"
)


class _Result:
    def __init__(self, stdout: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = ""


def _close_with(monkeypatch: pytest.MonkeyPatch, *, answered_repo: str, payload: dict) -> None:
    """Drive `close_with_comment` to its readback check.

    The comment and close commands succeed and the view command returns
    `payload`, so the only thing under test is whether the readback is about the
    issue that was asked about.
    """
    import json as _json

    monkeypatch.setattr(_issue_close, "answer_repo", lambda _payload: answered_repo)
    monkeypatch.setattr(
        _issue_close, "_run_backend", lambda argv: _Result(stdout=_json.dumps(payload))
    )
    body = ROOT / "tests" / "fixtures" / "close-body.md"
    body.write_text("closes the issue" + chr(10), encoding="utf-8")
    try:
        _issue_close.close_with_comment(
            "owner/repo", 42, body, repo_root=ROOT, classification="chore",
        )
    finally:
        body.unlink(missing_ok=True)


def _verified(**overrides: object) -> dict[str, object]:
    payload = {"number": 42, "state": "CLOSED", "repository": {"nameWithOwner": "owner/repo"}}
    payload.update(overrides)
    return payload


def test_close_verification_refuses_an_answer_about_another_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The readback must be about the issue that was asked about. A wrong-repo
    answer carries the right number and the expected state, so without this it
    reads as a successful close."""
    with pytest.raises(RuntimeError, match="different repository"):
        _close_with(monkeypatch, answered_repo="someone-else/repo", payload=_verified())


def test_close_verification_refuses_an_answer_about_another_issue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(RuntimeError, match="different issue"):
        _close_with(monkeypatch, answered_repo="owner/repo", payload=_verified(number=7))


def test_close_verification_accepts_the_issue_it_asked_about(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Control: the two refusals above must not be satisfiable by a check that
    refuses everything."""
    _close_with(monkeypatch, answered_repo="owner/repo", payload=_verified())


# --- a goal artifact with no Slice Log cannot take a slice --------------------

_goal_lib = _load_skill_module(
    "skills/public/achieve/scripts/goal_artifact_lib.py", "goal_artifact_lib_under_test"
)


def test_appending_a_slice_to_an_artifact_without_a_slice_log_is_refused() -> None:
    """Silently appending at the end would put the slice outside the section the
    closeout floors read, so the record would exist and count for nothing."""
    with pytest.raises(ValueError, match="no `## Slice Log` section"):
        _goal_lib.append_slice("# Goal\n\n## Boundaries\n\n- none\n", "- Objective: x\n")


# --- a reviewer-tier map that is not a map is not evidence -------------------

_critique_inspection = import_repo_module(__file__, "scripts.setup_critique_adapter_inspection")


def test_a_non_mapping_reviewer_tier_block_is_not_adoption_evidence() -> None:
    """Adoption is evidenced by the model field inside a mapping. A scalar or a
    list is a malformed adapter, and reading it as adoption would credit a repo
    with a profile it never declared."""
    for malformed in (None, "codex", ["codex"], 3):
        assert _critique_inspection._declares_codex_reviewer_profile(malformed) is False
