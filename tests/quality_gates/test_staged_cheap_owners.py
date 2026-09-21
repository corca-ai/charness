"""Cheap owners of staged files still run when Slice-reopen skips the release receipt."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.hooks import check_staged_cheap_owners as owners

from .git_fixture_support import init_git_repo

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.boundary_contract(
    reason="observe the cheap-owner child commands (docs-length, tokei, eviction-form, seam-index)"
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


def test_outside_universe_python_does_not_dispatch_length_owner(tmp_path: Path) -> None:
    artifact = tmp_path / "charness-artifacts/probe/example.py"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("value = 1\n", encoding="utf-8")
    owner = tmp_path / "scripts/gates/check_code_lengths.py"
    owner.parent.mkdir(parents=True)
    owner.write_text("", encoding="utf-8")
    code, text = owners.run_cheap_owners(tmp_path, [artifact.relative_to(tmp_path).as_posix()])
    assert (code, text) == (0, "")


def test_mixed_python_set_passes_only_owner_selected_paths(tmp_path: Path) -> None:
    paths = ["scripts/gates/check_code_lengths.py", "charness-artifacts/probe/example.py"]
    for relative in paths:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("value = 1\n", encoding="utf-8")
    gates = owners.cheap_owner_gates(tmp_path, paths)
    assert len(gates) == 1
    assert gates[0].argv[-2:] == ("--paths", paths[0])


def test_custom_python_universe_is_owned_by_length_selector(tmp_path: Path) -> None:
    paths = ["scripts/gates/check_code_lengths.py", "custom/example.py"]
    for relative in paths:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("value = 1\n", encoding="utf-8")
    adapter = tmp_path / ".agents/quality-adapter.yaml"
    adapter.parent.mkdir()
    adapter.write_text("version: 1\nrepo: sample\nuniverses:\n  python_sources:\n    - custom/*.py\n", encoding="utf-8")
    gates = owners.cheap_owner_gates(tmp_path, paths)
    assert len(gates) == 1
    assert gates[0].argv[-2:] == ("--paths", paths[1])


def test_a_debug_path_selects_the_seam_index() -> None:
    path = "charness-artifacts/debug/latest.md"
    assert "validate-debug-seam-index (staged)" in _labels([path])


def test_invalid_length_owner_configuration_refuses_cleanly(tmp_path: Path, capsys) -> None:
    owner = tmp_path / "scripts/gates/check_code_lengths.py"
    owner.parent.mkdir(parents=True)
    owner.write_text("", encoding="utf-8")
    adapter = tmp_path / ".agents/quality-adapter.yaml"
    adapter.parent.mkdir()
    adapter.write_text("version: [\n", encoding="utf-8")
    code = owners.main(["--repo-root", str(tmp_path), "--paths", owner.relative_to(tmp_path).as_posix()])
    assert code == 2
    assert "cheap owners unavailable" in capsys.readouterr().err


def test_a_schema_path_selects_enum_axis() -> None:
    path = "integrations/tools/manifest.schema.json"
    assert "check-schema-enum-axis (staged)" in _labels([path])
    assert "check-docs-length (staged)" not in _labels([path])


def test_an_unrelated_path_selects_no_cheap_owner() -> None:
    assert _labels(["README.md"]) == []


def test_a_staged_test_file_selects_the_eviction_owner() -> None:
    path = "tests/quality_gates/test_module_eviction_form_gate.py"
    assert "check-module-eviction-form (staged)" in _labels([path])


def test_a_non_test_python_path_does_not_select_the_eviction_owner() -> None:
    path = "scripts/hooks/check_staged_cheap_owners.py"
    assert "check-python-lengths (staged)" in _labels([path])
    assert "check-module-eviction-form (staged)" not in _labels([path])


@pytest.mark.parametrize("path, label", [
    ("docs/artifact-policy.md", "check-docs-length (staged)"),
    ("scripts/hooks/check_staged_cheap_owners.py", "check-python-lengths (staged)"),
])
def test_a_failing_child_refuses_the_commit(monkeypatch: pytest.MonkeyPatch, path: str, label: str) -> None:
    monkeypatch.setattr(
        owners,
        "run_process",
        lambda *_a, **_k: SimpleNamespace(returncode=1, stderr="over budget\n", stdout=""),
    )
    code, text = owners.run_cheap_owners(ROOT, [path])
    assert code == 2
    assert label in text
    assert "over budget" in text


def test_live_docs_length_on_this_tree_passes() -> None:
    code, text = owners.run_cheap_owners(ROOT, ["docs/development.md"])
    assert code == 0
    assert text == ""


def test_pre_commit_hook_invokes_the_cheap_owners() -> None:
    hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    assert "scripts/hooks/check_staged_cheap_owners.py" in hook


def test_staged_file_with_unstaged_edits_refuses_before_any_owner(tmp_path: Path) -> None:
    """Owners read worktree bytes while the commit takes index bytes: a staged
    file edited again afterwards is refused so staged unsafe content cannot
    pass behind worktree-clean bytes."""
    repo = tmp_path / "repo"
    target = repo / "docs" / "n.md"
    target.parent.mkdir(parents=True)
    target.write_text("staged\n", encoding="utf-8")
    init_git_repo(repo, "docs/n.md")
    target.write_text("worktree cleaned\n", encoding="utf-8")

    code, text = owners.run_cheap_owners(repo)

    assert code == 2
    assert "differ from the worktree" in text
    assert "docs/n.md" in text
    assert "restage" in text


def test_stable_staged_file_passes_the_worktree_guard(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    target = repo / "docs" / "n.md"
    target.parent.mkdir(parents=True)
    target.write_text("staged\n", encoding="utf-8")
    init_git_repo(repo, "docs/n.md")

    code, text = owners.run_cheap_owners(repo)

    assert (code, text) == (0, "")
