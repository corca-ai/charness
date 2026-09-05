"""Cheap owners of staged files still run when Slice-reopen skips the release receipt."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.hooks import check_staged_cheap_owners as owners

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.boundary_contract(
    reason="observe the cheap-owner child commands (docs-length, tokei, seam-index)"
)


def _labels(paths: list[str], existing: list[str] | None = None) -> list[str]:
    present = existing if existing is not None else [path for path in paths if (ROOT / path).is_file()]
    return [gate.label for gate in owners.cheap_owner_gates(ROOT, paths, present)]


def test_a_docs_path_selects_docs_length() -> None:
    assert "check-docs-length (staged)" in _labels(["docs/artifact-policy.md"])
    assert "check-python-lengths (staged)" not in _labels(["docs/artifact-policy.md"])


def test_a_python_path_selects_tokei_caps() -> None:
    path = "scripts/hooks/check_staged_cheap_owners.py"
    assert "check-python-lengths (staged)" in _labels([path])
    assert "check-docs-length (staged)" not in _labels([path])


def test_a_debug_path_selects_the_seam_index() -> None:
    path = "charness-artifacts/debug/latest.md"
    assert "validate-debug-seam-index (staged)" in _labels([path])


def test_a_schema_path_selects_enum_axis() -> None:
    path = "integrations/tools/manifest.schema.json"
    assert "check-schema-enum-axis (staged)" in _labels([path])
    assert "check-docs-length (staged)" not in _labels([path])


def test_an_unrelated_path_selects_no_cheap_owner() -> None:
    assert _labels(["README.md"]) == []


def test_a_failing_child_refuses_the_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        owners,
        "run_process",
        lambda *_a, **_k: SimpleNamespace(returncode=1, stderr="over budget\n", stdout=""),
    )
    code, text = owners.run_cheap_owners(ROOT, ["docs/artifact-policy.md"])
    assert code == 2
    assert "check-docs-length (staged)" in text
    assert "over budget" in text


def test_live_docs_length_on_this_tree_passes() -> None:
    code, text = owners.run_cheap_owners(ROOT, ["docs/development.md"])
    assert code == 0
    assert text == ""


def test_pre_commit_hook_invokes_the_cheap_owners() -> None:
    hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    assert "scripts/hooks/check_staged_cheap_owners.py" in hook
