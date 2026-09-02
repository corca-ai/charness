"""The analyzed/changed COUNT PAIR every changed-line verdict carries.

`scripts/gates_support/changed_line_scope_counts.py` owns the scope split and its disclosure;
these tests pin that EVERY verdict-emitting path of
`scripts/mutation/check_changed_line_mutation_coverage.py` states how many of how many
pool files it actually read, and that stating it changed no verdict.

The shared history fixture lives in `seeding_support` so the sibling changed-line
tests all exercise the same synthetic repository.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import yaml

from tests.quality_gates.repo_shapes import install_two_commit_repo
from tests.script_loader import load_script_module

from .seeding_support import seed_two_changed_pool_files
from .support import ROOT, run_script
from .test_changed_line_mutation_coverage import (
    _TEETH,
    UNESTABLISHED_EXIT,
    _dirty_pool_file,
    _seed_repo_with_changed_pool_file,
    _write_coverage,
    _write_two_file_coverage,
)

COUNTS_KEY = "changed_pool_file_counts"


def _load_scope_counts():
    return load_script_module(
        "changed_line_scope_counts", ROOT / "scripts" / "gates_support" / "changed_line_scope_counts.py"
    )


def _counts(result) -> dict:
    payload = yaml.safe_load(result.stdout)
    assert COUNTS_KEY in payload, f"verdict emitted no denominator: {payload}"
    return payload[COUNTS_KEY]


def _run_two_file(repo: Path, base: str, head: str, cov: Path, *limit: str):
    return run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--coverage-json", str(cov),
        *[arg for path in limit for arg in ("--limit-to-file", path)],
    )


def test_two_file_denominator_shapes_on_one_checkout(tmp_path: Path) -> None:
    repo, base, head = seed_two_changed_pool_files(tmp_path)
    cov = _write_two_file_coverage(repo)

    partial = _run_two_file(repo, base, head, cov, "scripts/foo.py")
    assert partial.returncode == 4, partial.stdout + partial.stderr
    payload = yaml.safe_load(partial.stdout)
    assert payload["blocking"] == []
    assert payload["changed_line_proof"] == "partial"
    assert _counts(partial) == {"analyzed": 1, "changed": 2}
    assert "analyzed only 1 of 2" in partial.stderr

    unlimited = _run_two_file(repo, base, head, cov)
    assert unlimited.returncode == 1, "a real uncovered changed line must still block"
    assert _counts(unlimited) == {"analyzed": 2, "changed": 2}

    nothing = _run_two_file(repo, base, head, cov, "scripts/absent.py")
    assert nothing.returncode == UNESTABLISHED_EXIT, nothing.stdout + nothing.stderr
    assert _counts(nothing) == {"analyzed": 0, "changed": 2}


def test_an_empty_range_states_zero_of_zero(tmp_path: Path) -> None:
    """A range that changed no pool file has a real, earned denominator of zero.

    Distinct from the not-computed paths below: this run DID look.
    """
    repo, base, head = install_two_commit_repo(
        tmp_path / "repo",
        {"docs/note.md": "base\n"},
        {"docs/note.md": "base\nmore\n"},
        first_message="base",
        second_message="head",
    )

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head, "--reuse-coverage"
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert _counts(result) == {"analyzed": 0, "changed": 0}


def test_one_file_denominator_shapes_on_one_checkout(tmp_path: Path) -> None:
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)

    no_base = run_script(_TEETH, "--repo-root", str(repo), "--base-sha", "", "--reuse-coverage")
    assert no_base.returncode == 0, no_base.stdout + no_base.stderr
    counts = _counts(no_base)
    assert counts["analyzed"] is None and counts["changed"] is None
    assert "no base_sha" in counts["not_computed"]

    cov = _write_coverage(repo, executed=[1, 2, 5, 6], missing=[])
    full = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--coverage-json", str(cov),
    )
    assert full.returncode == 0, full.stdout + full.stderr
    assert _counts(full) == {"analyzed": 1, "changed": 1}

    absent = repo / "reports" / "mutation" / "test-coverage.json"
    skip = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--skip-if-no-coverage", "--coverage-json", str(absent),
    )
    assert skip.returncode == UNESTABLISHED_EXIT, skip.stdout + skip.stderr
    assert _counts(skip) == {"analyzed": 1, "changed": 1}

    _dirty_pool_file(repo)
    dirty = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--coverage-json", str(cov), "--allow-dirty",
    )
    payload = yaml.safe_load(dirty.stdout)
    assert _counts(dirty) == {"analyzed": 1, "changed": 1}
    assert payload["dirty_pool_unverified"] is True
    assert payload["uncommitted_pool_files"] == ["scripts/foo.py"]

    refused = run_script(_TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD")
    assert refused.returncode == 2, refused.stdout + refused.stderr
    refused_counts = _counts(refused)
    assert refused_counts["analyzed"] is None and refused_counts["changed"] is None
    assert "startup refusal" in refused_counts["not_computed"]


def test_scope_count_helpers_are_pure_arithmetic() -> None:
    counts_module = _load_scope_counts()
    analyzed, unanalyzed = counts_module.apply_file_limit(
        SimpleNamespace(limit_to_file=[]), ["scripts/foo.py", "scripts/bar.py"]
    )
    assert analyzed == ["scripts/foo.py", "scripts/bar.py"]
    assert unanalyzed == []
    assert counts_module.scope_counts(["a", "b"], ["c"]) == {
        COUNTS_KEY: {"analyzed": 2, "changed": 3}
    }
    assert counts_module.scope_counts([], []) == {COUNTS_KEY: {"analyzed": 0, "changed": 0}}
    assert counts_module.scope_counts_not_computed("because") == {
        COUNTS_KEY: {"analyzed": None, "changed": None, "not_computed": "because"}
    }
