"""Explicit review inputs never require discovering unrelated artifact files."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.adapters import quality_universe_selection as selection
from tests.quality_gates.repo_shapes import install_committed_repo


def _files(root: Path, *names: str) -> list[Path]:
    paths = [root / name for name in names]
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("evidence\n", encoding="utf-8")
    return paths


def _universe(pattern: str):
    return selection._universes.Universe((pattern,), True, "adapter")


@pytest.mark.parametrize("pattern", ["src", "src/**/*.md", "src/*", "src/*/*.md", "src/**/deep"])
def test_selected_glob_and_directory_parity(tmp_path: Path, monkeypatch, pattern: str) -> None:
    candidates = _files(
        tmp_path, "src/top.md", "src/nested/item.md", "src/nested/deep/proof.txt", "outside.md"
    )
    universe = _universe(pattern)
    expected = selection._universes.matching_files(tmp_path, universe, git_listing=False)
    calls = []

    def scoped_listing(root, *, selected_paths):
        calls.append((root, selected_paths))
        return set(selected_paths)

    def no_discovery(*_args, **_kwargs):
        pytest.fail("selection must not discover a repository corpus")

    monkeypatch.setattr(selection._universes, "_git_listing", scoped_listing)
    monkeypatch.setattr(selection._universes, "_raw_glob", no_discovery)
    monkeypatch.setattr(Path, "glob", no_discovery)
    monkeypatch.setattr(Path, "rglob", no_discovery)
    result = selection.matching_selected_files(tmp_path, {"spec": universe}, candidates)
    assert result == {"spec": expected}
    assert calls == [(tmp_path, sorted(candidates))]


def test_one_query_across_families_and_no_empty_universe_claim(tmp_path: Path, monkeypatch) -> None:
    candidates = _files(tmp_path, "spec/proof.md", "outside.md")
    calls = []

    def listed(_root, *, selected_paths):
        calls.append(selected_paths)
        return set(selected_paths)

    monkeypatch.setattr(selection._universes, "_git_listing", listed)
    result = selection.matching_selected_files(
        tmp_path,
        {"spec": _universe("spec"), "critique": _universe("does-not-exist")},
        candidates,
    )
    assert result == {"spec": [candidates[0]], "critique": []}
    assert calls == [sorted(candidates)]
    assert (
        selection._universes.refuse_if_declared_and_empty(
            _universe("does-not-exist"), [], "full-gate"
        )
        == "full-gate: refusing empty declared universe (patterns: does-not-exist)."
    )


@pytest.mark.boundary_contract(
    reason="observe real Git visibility and literal selected-file pathspecs"
)
def test_git_visibility_and_literal_paths(tmp_path: Path, monkeypatch) -> None:
    root = install_committed_repo(tmp_path / "repo", {"proof/tracked.md": "tracked\n"})
    (root / ".gitignore").write_text("proof/tracked.md\nproof/ignored.md\n", encoding="utf-8")
    visible, ignored, literal, unsupplied = _files(
        root, "proof/visible.md", "proof/ignored.md", "proof/[a]*?.md", "proof/aZZ.md"
    )
    tracked = root / "proof/tracked.md"
    original = selection._universes.run_process
    commands = []

    def observed(command, **kwargs):
        commands.append(command)
        return original(command, **kwargs)

    monkeypatch.setattr(selection._universes, "run_process", observed)
    result = selection.matching_selected_files(
        root, {"spec": _universe("proof")}, [tracked, visible, ignored, literal]
    )
    assert result == {"spec": sorted([tracked, visible, literal])}
    assert unsupplied not in result["spec"]
    assert commands == [
        [
            "git",
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            *[
                f":(literal){path.relative_to(root).as_posix()}"
                for path in sorted([tracked, visible, ignored, literal])
            ],
        ]
    ]


def test_file_eligibility_and_lexical_symlink_identity(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    (target,) = _files(root, "proof/target.md")
    alias = root / "proof/alias.md"
    alias.symlink_to("target.md")
    (outside,) = _files(tmp_path, "outside.md")
    monkeypatch.setattr(selection._universes, "_git_listing", lambda _root, **_kwargs: None)
    result = selection.matching_selected_files(
        root,
        {"spec": _universe("proof")},
        [alias, Path("proof/./target.md"), root / "missing.md", root / "proof", outside],
    )
    assert result == {"spec": [alias, target]}
    with pytest.raises(RuntimeError, match="selected-file listing failed"):
        selection.matching_selected_files(
            root, {"spec": _universe("proof")}, [alias], require_git=True
        )


def test_empty_selection_does_not_start_git(tmp_path: Path, monkeypatch) -> None:
    def no_process(*_args, **_kwargs):
        pytest.fail("empty selection must not start Git")

    monkeypatch.setattr(selection._universes, "run_process", no_process)
    assert selection.matching_selected_files(tmp_path, {"spec": _universe("proof")}, []) == {
        "spec": []
    }


def test_git_unavailability_keeps_selected_fallback(tmp_path: Path, monkeypatch) -> None:
    (candidate,) = _files(tmp_path, "proof.md")
    monkeypatch.setattr(
        selection._universes,
        "run_process",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=128, stdout="", stderr="not a repository"
        ),
    )
    assert selection.matching_selected_files(
        tmp_path, {"spec": _universe("*.md")}, [candidate]
    ) == {"spec": [candidate]}
