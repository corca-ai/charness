"""The Rust changed-line floor: what it judges, and what it refuses to judge.

Python changed lines have had a blocking floor since D40; Rust had none while the
ratio gate counted `native/*/src/**/*.rs` as production. These cases pin the two
halves that make the lane safe to arm later: the diff parse that decides WHICH
lines are judged, and the three-way classification that decides what a judgement
means. Coverage itself comes from `cargo llvm-cov`, which is not re-implemented
here and not run by these tests.
"""
from __future__ import annotations

from pathlib import Path

from .repo_shapes import install_two_commit_repo
from .seeding_support import load_module
from .support import ROOT

MODULE = load_module("rust_changed_line_coverage", ROOT / "scripts/rust_changed_line_coverage.py")


_LIB_SEED = "fn a() {}\nfn b() {}\nfn c() {}\n"


def test_only_added_and_modified_lines_are_judged(tmp_path: Path) -> None:
    """The diff decides the scope. A file's untouched lines are not this lane's
    business -- judging them would make every Rust change carry the whole crate."""

    repo, base, _head = install_two_commit_repo(
        tmp_path / "repo",
        {"native/demo/src/lib.rs": _LIB_SEED},
        {"native/demo/src/lib.rs": "fn a() {}\nfn b2() {}\nfn c() {}\nfn d() {}\n"},
        first_message="seed",
        second_message="change",
    )

    changed = MODULE.changed_rust_lines(repo, base)

    assert changed == {"native/demo/src/lib.rs": {2, 4}}


def test_a_pure_deletion_contributes_no_judged_lines(tmp_path: Path) -> None:
    """A hunk that only removes lines has `+N,0`. Read as one added line at N it
    would judge a line this diff did not write."""

    repo, base, _head = install_two_commit_repo(
        tmp_path / "repo",
        {"native/demo/src/lib.rs": _LIB_SEED},
        {"native/demo/src/lib.rs": "fn a() {}\nfn c() {}\n"},
        first_message="seed",
        second_message="delete",
    )

    assert MODULE.changed_rust_lines(repo, base) == {}


def test_a_line_with_no_coverage_record_is_not_executable_never_uncovered(monkeypatch) -> None:
    """The direction-of-error argument, as an assertion.

    A changed line llvm-cov emitted no `DA:` record for is a comment, a blank, a
    `use`, or a declaration folded away -- not an untested line. Calling it uncovered
    would make the floor block on formatting; calling an untested line covered would
    make it worthless. Only the second is unsafe, so the lane is built to under-report.
    """

    monkeypatch.setattr(MODULE, "changed_rust_lines", lambda *_a, **_k: {"native/demo/src/lib.rs": {1, 2, 3}})
    monkeypatch.setattr(MODULE, "discover_crates", lambda *_a, **_k: [Path("native/demo")])
    monkeypatch.setattr(
        MODULE, "crate_line_counts",
        lambda *_a, **_k: {"native/demo/src/lib.rs": {2: 0, 3: 7}},
    )
    monkeypatch.setattr(MODULE, "_relative", lambda _root, name: name)

    report = MODULE.build_report(Path("/repo"), base_sha="deadbeef")

    assert report["not_executable"] == 1               # line 1: no record
    assert [u["line"] for u in report["uncovered"]] == [2]  # record, zero hits
    assert report["covered"] == 1                      # line 3: record, hits
    assert report["status"] == "established"


def test_a_changed_file_no_crate_measured_is_reported_not_absorbed(monkeypatch) -> None:
    """An unmeasured file must not disappear into `not_executable`, which is the
    bucket that reads as 'fine'. It gets its own list."""

    monkeypatch.setattr(MODULE, "changed_rust_lines", lambda *_a, **_k: {"other/tree/x.rs": {1}})
    monkeypatch.setattr(MODULE, "discover_crates", lambda *_a, **_k: [])
    monkeypatch.setattr(MODULE, "crate_line_counts", lambda *_a, **_k: {})

    report = MODULE.build_report(Path("/repo"), base_sha="deadbeef")

    assert report["unmeasured_files"] == ["other/tree/x.rs"]
    assert report["not_executable"] == 0
    assert report["uncovered"] == []


def test_a_diff_that_touched_no_rust_says_empty_scope(tmp_path: Path) -> None:
    """A discovered empty set stays a cheap pass -- and says so, rather than
    reporting a clean floor over a comparison that never happened."""

    repo, base, _head = install_two_commit_repo(
        tmp_path / "repo",
        {"README.md": "# demo\n"},
        {"README.md": "# demo\n\nmore\n"},
        first_message="seed",
        second_message="docs only",
    )

    report = MODULE.build_report(repo, base_sha=base)

    assert report["status"] == "empty-scope"
    assert report["changed_lines"] == 0
    assert report["uncovered"] == []


def test_the_floor_is_opt_in(monkeypatch, capsys) -> None:
    """Reporting and refusing are different runs of the same lane.

    Arming this at the release boundary is its own decision with its own evidence;
    the 2026-08-29 ratio-cap entry is this repo's record of promoting a measurement
    to blocking a day after building it.
    """

    monkeypatch.setattr(
        MODULE, "build_report",
        lambda *_a, **_k: {"schema": "x", "status": "established", "uncovered": [{"path": "a.rs", "line": 1}]},
    )
    monkeypatch.setattr(MODULE._producer, "default_mutation_base_sha", lambda _root: "deadbeef")

    assert MODULE.main(["--repo-root", str(ROOT)]) == 0
    assert MODULE.main(["--repo-root", str(ROOT), "--refuse-uncovered"]) == 1
    assert "1 changed Rust line(s)" in capsys.readouterr().err


def test_an_unestablished_run_is_neither_a_pass_nor_a_violation(monkeypatch, capsys) -> None:
    """Exit 3, distinct from 0 and 1: a lane that could not measure has not found a
    clean floor, and has not found a breach either."""

    monkeypatch.setattr(MODULE._producer, "default_mutation_base_sha", lambda _root: "")

    assert MODULE.main(["--repo-root", str(ROOT)]) == 3
    assert "no base sha" in capsys.readouterr().out
