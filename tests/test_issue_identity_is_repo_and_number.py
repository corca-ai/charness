"""The issue provider has one canonical identity rule."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REPO = "corca-ai/charness"
OTHER = "someone-else/charness"


def _module(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


IDENTITY = _module("skills/public/issue/scripts/issue_identity.py", "issue_identity_under_test")
BACKEND = _module("skills/public/issue/scripts/issue_backend.py", "issue_backend_under_test")
RESOLVE = _module("skills/public/issue/scripts/resolve_adapter.py", "issue_resolve_under_test")


def _parsed_backend(**fields: object) -> tuple[dict, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    backend = RESOLVE._parse_backend(fields, errors, warnings)
    return backend, errors, warnings


def test_answer_repo_accepts_qualified_shapes_and_rejects_half_identity() -> None:
    assert IDENTITY.answer_repo({"repository": {"nameWithOwner": REPO}}) == REPO
    assert IDENTITY.answer_repo({"repository": {"owner": {"login": "corca-ai"}, "name": "charness"}}) == REPO
    assert IDENTITY.answer_repo({"url": f"https://github.com/{REPO}/issues/1"}) == REPO
    assert IDENTITY.answer_repo({"repository": "charness"}) is None
    assert IDENTITY.answer_repo({"url": "https://github.com/corca-ai/charness/issues"}) is None


def test_identity_mismatch_reports_both_wrong_fields() -> None:
    mismatches = IDENTITY.issue_identity_mismatches(
        {"number": 7, "url": f"https://github.com/{OTHER}/issues/7"},
        expected_repo=REPO,
        expected_number=42,
    )

    assert {item["field"] for item in mismatches} == {"number", "repository"}


def test_repo_scoped_backend_is_explicit_and_only_waives_repo() -> None:
    backend, errors, warnings = _parsed_backend(
        id="acme",
        binary="acme",
        repo_scoped=REPO,
        commands={"view": ["view", "{number}" ]},
    )
    assert errors == []
    assert warnings == []
    assert backend["repo_scoped"] == REPO

    argv = BACKEND.resolve_op(
        backend,
        "view",
        ["view", "{repo}", "{number}"],
        frozenset({"repo", "number"}),
        required=frozenset({"repo", "number"}),
        waivable=frozenset({"repo"}),
        repo=REPO,
        number="42",
    )
    assert argv == ["acme", "view", "42"]


def test_issue_number_can_never_be_waived() -> None:
    backend, errors, _ = _parsed_backend(
        id="acme",
        binary="acme",
        repo_scoped=REPO,
        commands={"view": ["view"]},
    )
    assert errors == []
    with pytest.raises(RuntimeError, match="missing required placeholders.*number"):
        BACKEND.resolve_op(
            backend,
            "view",
            ["view", "{repo}", "{number}"],
            frozenset({"repo", "number"}),
            required=frozenset({"repo", "number"}),
            waivable=frozenset({"repo"}),
            repo=REPO,
            number="42",
        )
