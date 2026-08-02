"""The analyzed/changed COUNT PAIR every changed-line verdict carries.

`scripts/changed_line_scope_counts.py` owns the scope split and its disclosure;
these tests pin that EVERY verdict-emitting path of
`scripts/check_changed_line_mutation_coverage.py` states how many of how many
pool files it actually read, and that stating it changed no verdict.

The seeding helpers are imported from the gate's own test module rather than
re-declared: a second copy of `_seed_two_changed_pool_files` would be a
clone-family the dup ratchet is right to flag, and a fixture that drifts from
the one the sibling tests use is worse than an import.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from tests.script_loader import load_script_module

from .support import ROOT, run_script
from .test_changed_line_mutation_coverage import (
    _TEETH,
    UNESTABLISHED_EXIT,
    _dirty_pool_file,
    _git,
    _seed_repo_with_changed_pool_file,
    _seed_two_changed_pool_files,
    _write_coverage,
    _write_two_file_coverage,
)

COUNTS_KEY = "changed_pool_file_counts"


def _load_scope_counts():
    return load_script_module(
        "changed_line_scope_counts", ROOT / "scripts" / "changed_line_scope_counts.py"
    )


def _counts(result) -> dict:
    payload = json.loads(result.stdout)
    assert COUNTS_KEY in payload, f"verdict emitted no denominator: {payload}"
    return payload[COUNTS_KEY]


def _run_two_file(repo: Path, base: str, head: str, cov: Path, *limit: str):
    return run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--coverage-json", str(cov),
        *[arg for path in limit for arg in ("--limit-to-file", path)],
    )


def test_a_partial_denominator_states_both_numbers_on_a_passing_run(tmp_path: Path) -> None:
    """The acceptance fixture: a NON-blocking verdict whose scope was partial.

    This payload already listed the file it skipped, but `changed_pool_files` (the
    numerator list) is not on this path at all — so "1 of 2" was not reconstructable
    here by any amount of `len()`-ing. A reader who saw `blocking: []` saw a green
    whose scope they could not recover.
    """
    repo, base, head = _seed_two_changed_pool_files(tmp_path)
    cov = _write_two_file_coverage(repo)

    result = _run_two_file(repo, base, head, cov, "scripts/foo.py")

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["blocking"] == []
    assert _counts(result) == {"analyzed": 1, "changed": 2}
    # Both channels, agreeing. stderr already said "analyzed only 1 of 2"; the
    # machine-readable payload said it nowhere, so a consumer parsing JSON and an
    # operator reading the terminal were getting different amounts of the truth.
    assert "analyzed only 1 of 2" in result.stderr


def test_disclosing_the_denominator_does_not_change_the_verdict(tmp_path: Path) -> None:
    """The control. Lane A discloses; it does not refuse.

    Without this, the fixture above would prove only that a key appeared. A CLEAN
    partial denominator still exits 0, and an uncovered changed line still exits 1
    — whether a partial denominator should refuse is D40's toll question and stays
    the operator's, not this change's.
    """
    repo, base, head = _seed_two_changed_pool_files(tmp_path)
    cov = _write_two_file_coverage(repo)

    partial = _run_two_file(repo, base, head, cov, "scripts/foo.py")
    unlimited = _run_two_file(repo, base, head, cov)

    assert partial.returncode == 0, "a partial denominator must not start refusing"
    assert unlimited.returncode == 1, "a real uncovered changed line must still block"
    assert _counts(partial) == {"analyzed": 1, "changed": 2}
    assert _counts(unlimited) == {"analyzed": 2, "changed": 2}


def test_a_full_denominator_says_so_rather_than_staying_silent(tmp_path: Path) -> None:
    """`analyzed == changed` is the honest "nothing was left out", and it is stated.

    Silence would be the ambiguity this lane exists to remove: a reader cannot tell
    a complete scope from an undisclosed one by the absence of a field.
    """
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2, 5, 6], missing=[])

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--coverage-json", str(cov),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert _counts(result) == {"analyzed": 1, "changed": 1}


def test_a_limit_that_analyzes_nothing_states_zero_of_the_real_denominator(tmp_path: Path) -> None:
    """The strongest disclosure case: `0 of 2`, on the exit-3 path.

    "Analyzed nothing" and "nothing changed" are different facts that used to
    render as the same shape of payload.
    """
    repo, base, head = _seed_two_changed_pool_files(tmp_path)
    cov = _write_two_file_coverage(repo)

    result = _run_two_file(repo, base, head, cov, "scripts/absent.py")

    assert result.returncode == UNESTABLISHED_EXIT, result.stdout + result.stderr
    assert _counts(result) == {"analyzed": 0, "changed": 2}


def test_an_empty_range_states_zero_of_zero(tmp_path: Path) -> None:
    """A range that changed no pool file has a real, earned denominator of zero.

    Distinct from the not-computed paths below: this run DID look.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    _git(repo, "init", "-q")
    (repo / "docs" / "note.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "docs" / "note.md").write_text("base\nmore\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "head")
    head = _git(repo, "rev-parse", "HEAD")

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head, "--reuse-coverage"
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert _counts(result) == {"analyzed": 0, "changed": 0}


def test_the_unverified_skip_states_what_it_skipped_over(tmp_path: Path) -> None:
    """The pre-push lane's most common verdict, and the #335 recurrence driver.

    A skip already said coverage was unavailable; it did not say how large the set
    it went silent about was. `1 of 1` is the difference between "one file went
    unverified" and an unbounded green.
    """
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    absent = repo / "reports" / "mutation" / "test-coverage.json"  # never written

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--skip-if-no-coverage", "--coverage-json", str(absent),
    )

    assert result.returncode == UNESTABLISHED_EXIT, result.stdout + result.stderr
    assert _counts(result) == {"analyzed": 1, "changed": 1}


def test_the_pair_is_the_ranges_population_and_says_so_beside_the_dirty_keys(tmp_path: Path) -> None:
    """The honest limit of this pair, pinned rather than left to the docstring.

    `--allow-dirty` derives its set from `base..head`, which cannot see uncommitted
    pool edits — so an equal pair here means "all of what this range could see",
    not "all of what changed". The claim that the pair is complete is NOT made; the
    payload carries `dirty_pool_unverified` and the offending files beside it, and
    a reader who takes the pair alone is the failure this test exists to document.
    """
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2, 5, 6], missing=[])
    _dirty_pool_file(repo)  # uncommitted: invisible to base..head

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--coverage-json", str(cov), "--allow-dirty",
    )

    payload = json.loads(result.stdout)
    assert _counts(result) == {"analyzed": 1, "changed": 1}
    assert payload["dirty_pool_unverified"] is True
    assert payload["uncommitted_pool_files"] == ["scripts/foo.py"]


def test_a_run_with_no_base_sha_reports_the_pair_as_not_computed(tmp_path: Path) -> None:
    """Nulls, not zeros. This run derived no changed set at all, so `0 of 0` would
    assert an empty scope it never earned — indistinguishable from the honest
    empty range above."""
    repo, _base, _head = _seed_repo_with_changed_pool_file(tmp_path)

    result = run_script(_TEETH, "--repo-root", str(repo), "--base-sha", "", "--reuse-coverage")

    assert result.returncode == 0, result.stdout + result.stderr
    counts = _counts(result)
    assert counts["analyzed"] is None and counts["changed"] is None
    assert "no base_sha" in counts["not_computed"]


def test_a_startup_refusal_reports_the_pair_as_not_computed(tmp_path: Path) -> None:
    """The refusal paths fire before the changed set exists, and say so.

    A refusal is already "no verdict", but it still emits a payload — and a payload
    with no scope field is the gap this lane closes everywhere else.
    """
    repo, base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    _dirty_pool_file(repo)

    result = run_script(_TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD")

    assert result.returncode == 2, result.stdout + result.stderr
    counts = _counts(result)
    assert counts["analyzed"] is None and counts["changed"] is None
    assert "startup refusal" in counts["not_computed"]


def test_an_absent_limit_analyzes_everything(tmp_path: Path) -> None:
    """`--limit-to-file` is absent on every pre-existing caller, so an empty list
    must mean "analyze all", never "analyze none". Pinned here too because the
    split moved modules: the gate's own copy of this test proves the re-export
    still resolves, this one proves the moved implementation still behaves."""
    counts_module = _load_scope_counts()

    analyzed, unanalyzed = counts_module.apply_file_limit(
        SimpleNamespace(limit_to_file=[]), ["scripts/foo.py", "scripts/bar.py"]
    )

    assert analyzed == ["scripts/foo.py", "scripts/bar.py"]
    assert unanalyzed == []


def test_the_pair_counts_the_whole_changed_set_not_just_the_analyzed_one() -> None:
    """Direct unit pin on the arithmetic the payload tests observe indirectly."""
    counts_module = _load_scope_counts()

    assert counts_module.scope_counts(["a", "b"], ["c"]) == {
        COUNTS_KEY: {"analyzed": 2, "changed": 3}
    }
    assert counts_module.scope_counts([], []) == {COUNTS_KEY: {"analyzed": 0, "changed": 0}}


def test_a_not_computed_pair_carries_its_reason_instead_of_a_number() -> None:
    counts_module = _load_scope_counts()

    assert counts_module.scope_counts_not_computed("because") == {
        COUNTS_KEY: {"analyzed": None, "changed": None, "not_computed": "because"}
    }
