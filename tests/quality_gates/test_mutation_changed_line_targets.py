"""Exact-line targets for changed-line mutation proof."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import scripts.mutation_changed_files_lib as mutation_changed_files_lib
import scripts.mutation_changed_line_diff as mutation_changed_line_diff
from scripts.mutation_changed_files_lib import changed_line_scope_gap_targets
from scripts.sample_mutation_files import write_manifest


def test_changed_line_scope_gap_targets_include_source_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "scripts" / "demo.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        "def covered():\n    return 1\n\ndef gap():\n    return 2\n", encoding="utf-8"
    )
    monkeypatch.setattr(
        mutation_changed_files_lib,
        "changed_line_numbers",
        lambda repo_root, base, head, path: {4, 5},
    )
    monkeypatch.setattr(
        mutation_changed_files_lib,
        "line_source_text",
        lambda repo_root, path, ref=None: target.read_text(encoding="utf-8").splitlines(),
    )

    targets = changed_line_scope_gap_targets(
        repo_root=tmp_path,
        base_sha="base",
        head_sha="head",
        changed_before_coverage=["scripts/demo.py"],
        statement_lines={"scripts/demo.py": ({1, 2}, {4, 5})},
        coverage_enabled=True,
    )

    assert targets == {
        "scripts/demo.py": [
            {"line": 4, "source": "def gap():"},
            {"line": 5, "source": "return 2"},
        ]
    }


def test_changed_line_numbers_for_paths_batches_normal_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        output = (
            "diff --git a/scripts/foo.py b/scripts/foo.py\n"
            "+++ b/scripts/foo.py\n"
            "@@ -1 +2,2 @@\n"
            "+new\n"
            "diff --git a/scripts/bar.py b/scripts/bar.py\n"
            "+++ b/scripts/bar.py\n"
            "@@ -4 +5 @@\n"
            "+also-new\n"
        )
        return subprocess.CompletedProcess(command, 0, output, "")

    monkeypatch.setattr(mutation_changed_line_diff, "run_process", fake_run)
    changed = mutation_changed_files_lib.changed_line_numbers_for_paths(
        Path("/repo"), "a" * 40, "b" * 40, ["scripts/foo.py", "scripts/bar.py"]
    )

    assert changed == {"scripts/foo.py": {2, 3}, "scripts/bar.py": {5}}
    assert len(calls) == 1


def test_changed_line_numbers_reuses_immutable_range_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(
            command,
            0,
            "+++ b/scripts/foo.py\n@@ -1 +2 @@\n+new\n",
            "",
        )

    monkeypatch.setattr(mutation_changed_files_lib, "run_process", fake_run)
    args = (Path("/repo"), "c" * 40, "d" * 40, "scripts/foo.py")
    assert mutation_changed_files_lib.changed_line_numbers(*args) == {2}
    assert mutation_changed_files_lib.changed_line_numbers(*args) == {2}
    assert len(calls) == 1


def test_manifest_surfaces_changed_line_proof_targets(tmp_path: Path) -> None:
    manifest_json = tmp_path / "sample.json"
    manifest_md = tmp_path / "sample.md"
    manifest = {
        "seed": "fixed-seed",
        "base_sha": "base",
        "head_sha": "head",
        "max_files": 1,
        "eligible_count": 1,
        "all_eligible_count": 1,
        "changed_files_before_coverage": ["scripts/a.py"],
        "changed_files": ["scripts/a.py"],
        "changed_line_uncovered_changed_files": ["scripts/a.py"],
        "changed_line_uncovered_changed_line_targets": {
            "scripts/a.py": [{"line": 12, "source": "return value"}],
        },
        "uncovered_changed_files": [],
        "changed_files_excluded_by_file_coverage": [],
        "changed_files_excluded_by_mutation_line_coverage": [],
        "selection_excluded_changed_files": [],
        "changed_sample": ["scripts/a.py"],
        "fill_sample": [],
        "sample": ["scripts/a.py"],
        "pools": {},
        "test_command": "python3 -m pytest -q tests/test_a.py",
    }

    write_manifest(manifest, manifest_json, manifest_md)

    payload = json.loads(manifest_json.read_text(encoding="utf-8"))
    text = manifest_md.read_text(encoding="utf-8")
    assert payload["changed_line_uncovered_changed_line_targets"] == {
        "scripts/a.py": [{"line": 12, "source": "return value"}],
    }
    assert "- Changed-line proof targets: 1" in text
    assert "## Changed-line proof targets" in text
    assert "- `scripts/a.py:12` `return value`" in text


def test_changed_line_targets_read_source_from_head_not_dirty_worktree(tmp_path: Path) -> None:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True
        ).stdout.strip()

    (tmp_path / "scripts").mkdir()
    git("init", "-q")
    target = tmp_path / "scripts" / "demo.py"
    target.write_text("def value():\n    return 1\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    target.write_text("def value():\n    return 2\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "head")
    head = git("rev-parse", "HEAD")
    target.write_text("def value():\n    return 999\n", encoding="utf-8")

    targets = changed_line_scope_gap_targets(
        repo_root=tmp_path,
        base_sha=base,
        head_sha=head,
        changed_before_coverage=["scripts/demo.py"],
        statement_lines={"scripts/demo.py": ({1}, {2})},
        coverage_enabled=True,
    )

    assert targets["scripts/demo.py"] == [{"line": 2, "source": "return 2"}]
