"""Focused failure-path proof for create and deferred create verification."""
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
CREATE = runpy.run_path(str(ROOT / "skills/public/issue/scripts/issue_create.py"))
VERIFY = runpy.run_path(str(ROOT / "skills/public/issue/scripts/issue_create_verify.py"))
CREATE_GLOBALS = CREATE["create_issue"].__globals__
VERIFY_GLOBALS = VERIFY["verify_created_issue"].__globals__


def test_create_number_parser_and_readback_failure_are_typed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="positive integer"):
        CREATE["_positive_issue_number"]("not-a-number")

    body = tmp_path / "body.md"
    body.write_text("body\n", encoding="utf-8")
    monkeypatch.setitem(CREATE_GLOBALS, "run_backend", lambda _argv: SimpleNamespace(returncode=0, stdout="17\n", stderr=""))
    monkeypatch.setitem(CREATE_GLOBALS, "verify_created_issue", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("readback down")))

    payload = CREATE["create_issue"]("owner/repo", "real title", body)

    assert payload["number"] == 17
    assert payload["verify_error"] == "readback down"


def test_verify_create_command_reports_adapter_and_readback_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    emitted: list[dict] = []
    args = SimpleNamespace(repo_root=Path("."), repo="owner/repo", number=17, body_file=None)
    monkeypatch.setitem(CREATE_GLOBALS, "_emit", emitted.append)
    monkeypatch.setitem(CREATE_GLOBALS, "_resolve_backend", lambda _root, _repo: {"adapter_ok": False, "adapter": {"error": "bad"}, "backend": {}})
    assert CREATE["command_verify_create"](args) == 1
    assert emitted[-1] == {"ok": False, "adapter": {"error": "bad"}}

    backend = {"id": "fake"}
    monkeypatch.setitem(CREATE_GLOBALS, "_resolve_backend", lambda _root, _repo: {"adapter_ok": True, "adapter": {}, "backend": backend})
    monkeypatch.setitem(CREATE_GLOBALS, "verify_created_issue", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("readback down")))
    assert CREATE["command_verify_create"](args) == 2
    assert emitted[-1] == {"ok": False, "error": "readback down", "selected_backend": backend}


def test_verify_helper_rejects_unreadable_or_malformed_backend_results(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert VERIFY["_http_url"](object()) is None
    with pytest.raises(RuntimeError, match="body file not found"):
        VERIFY["verify_created_issue"]("owner/repo", 17, body_file=tmp_path / "missing.md")

    backend = {"id": "fake", "binary": "fake", "commands": None}
    monkeypatch.setitem(VERIFY_GLOBALS, "resolve_op", lambda *_args, **_kwargs: ["fake", "view"])
    monkeypatch.setitem(VERIFY_GLOBALS, "run_backend", lambda _argv: SimpleNamespace(returncode=1, stdout="", stderr="down"))
    with pytest.raises(RuntimeError, match="failed: exit=1"):
        VERIFY["verify_created_issue"]("owner/repo", 17, backend=backend)

    monkeypatch.setitem(VERIFY_GLOBALS, "run_backend", lambda _argv: SimpleNamespace(returncode=0, stdout="{", stderr=""))
    with pytest.raises(RuntimeError, match="invalid JSON"):
        VERIFY["verify_created_issue"]("owner/repo", 17, backend=backend)

    monkeypatch.setitem(VERIFY_GLOBALS, "run_backend", lambda _argv: SimpleNamespace(returncode=0, stdout=json.dumps([]), stderr=""))
    with pytest.raises(RuntimeError, match="non-object"):
        VERIFY["verify_created_issue"]("owner/repo", 17, backend=backend)
