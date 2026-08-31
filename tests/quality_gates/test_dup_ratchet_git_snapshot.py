"""GitSnapshot's one-coherent-snapshot and lazy changed-path contract tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.git_status_snapshot import status_args as git_status_args

from .dup_ratchet_test_support import git as _git
from .repo_shapes import replace_with_committed_repo
from .seeding_support import load_module
from .test_dup_ratchet import (
    _code_family,
    _consumer_repo,
    _doc_inventory,
    _run_inproc,
    _write_json,
)

SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "public" / "quality" / "scripts"
gitmod = load_module("dup_ratchet_git_snapshot_inproc", SCRIPTS / "dup_ratchet_git.py")
scan = load_module("dup_ratchet_scan_snapshot_inproc", SCRIPTS / "dup_ratchet_scan.py")


def test_git_seams_anchor_stagnation_and_reset(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    overlay = repo / "q" / "dup-review.json"
    overlay.parent.mkdir(parents=True)
    overlay.write_text("{}\n", encoding="utf-8")
    replace_with_committed_repo(repo, message="seed overlay")
    anchor = _git(repo, "rev-parse", "HEAD").stdout.strip()

    for index in range(3):
        _git(repo, "commit", "--allow-empty", "-m", f"work {index}")

    assert gitmod.resolve_anchor(repo, "q/dup-review.json") == anchor
    assert gitmod.anchor_is_ancestor(repo, anchor) is True
    assert gitmod.stagnation_commits(repo, anchor) == 3

    overlay.write_text('{"reviewed": 1}\n', encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "lower the ceiling")
    new_anchor = _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert gitmod.resolve_anchor(repo, "q/dup-review.json") == new_anchor
    assert gitmod.stagnation_commits(repo, new_anchor) == 0


def test_git_seams_orphan_and_missing(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    (repo / "f.txt").write_text("x\n", encoding="utf-8")
    replace_with_committed_repo(repo, message="init")
    assert gitmod.anchor_is_ancestor(repo, "0" * 40) is False
    assert gitmod.stagnation_commits(repo, "0" * 40) is None
    assert gitmod.anchor_is_ancestor(repo, None) is False
    assert gitmod.resolve_anchor(repo, "q/never.json") is None


def test_git_snapshot_batches_gate_facts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    overlay = repo / "q" / "dup-review.json"
    overlay.parent.mkdir(parents=True)
    overlay.write_text("{}\n", encoding="utf-8")
    tracked = repo / "tracked.py"
    tracked.write_text("seed\n", encoding="utf-8")
    replace_with_committed_repo(repo, message="seed overlay")
    anchor = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "commit", "--allow-empty", "-m", "work")
    tracked.write_text("changed\n", encoding="utf-8")
    (repo / "untracked.py").write_text("new\n", encoding="utf-8")

    calls: list[list[str]] = []
    original = gitmod._git_output

    def recording_git_output(root: Path, args: list[str]) -> tuple[int, str]:
        calls.append(args)
        return original(root, args)

    monkeypatch.setattr(gitmod, "_git_output", recording_git_output)
    facts = gitmod.snapshot(repo, "q/dup-review.json")

    assert facts.anchor == anchor
    assert facts.anchor_is_ancestor is True
    assert facts.stagnation == 1
    assert "tracked.py" in facts.tracked_paths
    assert facts.changed_paths == frozenset({"tracked.py", "untracked.py"})
    assert calls == [
        ["log", "-1", "--format=%H", "HEAD", "--", "q/dup-review.json"],
        ["rev-list", "--left-right", "--count", f"{anchor}...HEAD"],
        ["ls-files"],
        list(git_status_args()),
    ]


def _located_family(fingerprint: str, locations: list[dict]) -> dict:
    return {
        "family_fingerprint": fingerprint,
        "family_member_hashes": [fingerprint],
        "locations": locations,
    }


def test_inproc_hard_block_names_member_paths_and_diff_status(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    (repo / "untouched.py").write_text("a = 1\n", encoding="utf-8")
    replace_with_committed_repo(repo)
    (repo / "touched.py").write_text("b = 2\n", encoding="utf-8")
    code_json = _write_json(
        tmp_path / "code.json",
        {
            "status": "findings",
            "families": [
                _code_family("known1", ["known1"]),
                _located_family(
                    "NEWFAM",
                    [
                        {"file": "untouched.py", "start": 1, "end": 1},
                        {"file": "touched.py", "start": 1, "end": 1},
                    ],
                ),
            ],
        },
    )
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(doc_json))
    assert report["status"] == "hard-block"
    assert report["new_code_family_members"] == {
        "NEWFAM": [
            {"file": "untouched.py", "start": 1, "end": 1, "in_current_diff": False},
            {"file": "touched.py", "start": 1, "end": 1, "in_current_diff": True},
        ]
    }
    member_lines = [m for m in report["messages"] if m.startswith("new family NEWFAM")]
    assert member_lines == [
        "new family NEWFAM: members untouched.py:1-1 (untouched), touched.py:1-1 (in current diff)"
    ]


def test_inproc_hard_block_member_evidence_without_git_is_unknown(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    code_json = _write_json(
        tmp_path / "code.json",
        {
            "status": "findings",
            "families": [
                _code_family("known1", ["known1"]),
                _located_family("LOCFAM", [{"file": "x.py", "start": 3, "end": 9}]),
                _code_family("BAREFAM", ["BAREFAM"]),
            ],
        },
    )
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(doc_json))
    assert report["status"] == "hard-block"
    assert report["new_code_family_members"]["LOCFAM"][0]["in_current_diff"] is None
    assert report["new_code_family_members"]["BAREFAM"] == []
    assert any("x.py:3-9 (diff status unknown)" in m for m in report["messages"])
    assert any(
        m == "new family BAREFAM: member spans unavailable from this scan"
        for m in report["messages"]
    )


def test_family_member_spans_drops_malformed_and_no_git_changed_paths_is_none(
    tmp_path: Path,
) -> None:
    fam = {
        "locations": [
            {"file": "a.py", "start": 1, "end": 2},
            {"file": "", "start": 1, "end": 2},
            {"file": "b.py", "start": True, "end": 2},
            "not-a-dict",
            {"file": "c.py", "start": 1},
        ]
    }
    assert scan.family_member_spans(fam) == [{"file": "a.py", "start": 1, "end": 2}]
    assert gitmod.changed_worktree_paths(tmp_path) is None


def test_git_seams_do_not_launch_git_on_a_plain_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "plain"
    repo.mkdir()
    (repo / "f.txt").write_text("x\n", encoding="utf-8")
    launches: list[tuple[str, ...]] = []
    original = subprocess.run

    def wrapped(argv, *args, **kwargs):
        if isinstance(argv, (list, tuple)) and argv and Path(str(argv[0])).name == "git":
            launches.append(tuple(str(part) for part in argv[1:]))
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", wrapped)
    assert gitmod.tracked_files(repo) is None
    assert gitmod.changed_worktree_paths(repo) is None
    assert gitmod.resolve_anchor(repo, "q/dup-review.json") is None
    assert launches == []


def test_tracked_files_lists_a_real_checkout(tmp_path: Path) -> None:
    from .git_fixture_support import init_git_repo

    repo = tmp_path / "r"
    repo.mkdir()
    (repo / "f.txt").write_text("x\n", encoding="utf-8")
    init_git_repo(repo, "f.txt")
    assert gitmod.tracked_files(repo) == {"f.txt"}
