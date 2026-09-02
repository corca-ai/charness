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
import re
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

_pointer_writes = import_repo_module(__file__, "tools.check_current_pointer_writes")


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
            {"commands": {"source_capture": ["gh", "api", "{repo}", "{number}"]}},
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


# --- close verification refuses an answer about something else ---------------

_issue_close = _load_skill_module(
    "skills/public/issue/scripts/issue_close.py", "issue_close_under_test"
)


class _Result:
    def __init__(self, stdout: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = ""


def _close_with(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, *, answered_repo: str, payload: dict
) -> None:
    """Drive `close_with_comment` to its readback check.

    The comment and close commands succeed and the view command returns
    `payload`, so the only thing under test is whether the readback is about the
    issue that was asked about.
    """
    import json as _json

    payload = dict(payload)
    payload["repository"] = {"nameWithOwner": answered_repo}
    monkeypatch.setattr(
        _issue_close, "_run_backend", lambda argv: _Result(stdout=_json.dumps(payload))
    )
    body = tmp_path / "close-body.md"
    # Scaffolding: this test is about the post-close identity readback, not the
    # rung-1 body floor, which now applies to every classification.
    body.write_text(
        "closes the issue" + chr(10) * 2 + "AI-provenance: authored by an agent session." + chr(10),
        encoding="utf-8",
    )
    _issue_close.close_with_comment(
        "owner/repo", 42, body, repo_root=ROOT, classification="chore",
    )


def _verified(**overrides: object) -> dict[str, object]:
    payload = {"number": 42, "state": "CLOSED", "repository": {"nameWithOwner": "owner/repo"}}
    payload.update(overrides)
    return payload


def test_close_verification_refuses_an_answer_about_another_repository(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The readback must be about the issue that was asked about. A wrong-repo
    answer carries the right number and the expected state, so without this it
    reads as a successful close."""
    with pytest.raises(RuntimeError, match="different repository"):
        _close_with(monkeypatch, tmp_path, answered_repo="someone-else/repo", payload=_verified())


def test_close_verification_refuses_an_answer_about_another_issue(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    with pytest.raises(RuntimeError, match="different issue"):
        _close_with(monkeypatch, tmp_path, answered_repo="owner/repo", payload=_verified(number=7))


def test_close_verification_accepts_the_issue_it_asked_about(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Control: the two refusals above must not be satisfiable by a check that
    refuses everything."""
    _close_with(monkeypatch, tmp_path, answered_repo="owner/repo", payload=_verified())


def test_a_typed_refusal_from_the_source_capture_op_passes_through() -> None:
    """The same re-raise as `backend_binary`, on the other call path.

    `build_page_argv` resolves the op through the owner too, and that second
    `except CaptureRefusal: raise` is what keeps an already-typed refusal from
    being relabelled `invalid_capture_command` by the RuntimeError arm below it.
    """

    class _Owner:
        PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")

        def backend_binary(self, _backend):
            return "gh"

        def resolve_op(self, *_args, **_kwargs):
            raise _capture.CaptureRefusal("missing_backend_module", "partial install")

    with pytest.raises(_capture.CaptureRefusal) as excinfo:
        _with_owner(_Owner())

    assert excinfo.value.code == "missing_backend_module"


def test_a_runtime_error_from_the_source_capture_op_becomes_a_config_refusal() -> None:
    class _Owner:
        PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")

        def backend_binary(self, _backend):
            return "gh"

        def resolve_op(self, *_args, **_kwargs):
            raise RuntimeError("template is missing a required placeholder")

    with pytest.raises(_capture.CaptureRefusal) as excinfo:
        _with_owner(_Owner())

    assert excinfo.value.code == "invalid_capture_command"
