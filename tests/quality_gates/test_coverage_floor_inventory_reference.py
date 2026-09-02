"""The reference inventory's gate discovery must honor the anchor its policy declares.

`gate_script_pattern` was resolved with a single hardcoded anchor (`scripts/`), so a
repo whose stop gate is `.githooks/pre-commit` could not name it: the spelling
resolved to `scripts/.githooks/pre-commit` and matched nothing, and the policy could
describe the repo or be resolvable but not both.

The meta-check half is pinned here too, because it is the half that fails quietly.
Two shapes of quiet failure are covered:

* it counted `foreign` references with a hardcoded `scripts/` + `.sh` pair, so on a
  repo that moved either, a gate referenced by lefthook and NOT discovered by the
  pattern -- the drift the meta-check exists to catch -- reported clean;
* a repo with no lefthook and no CI workflows has no operational side to reconcile
  against, and reporting every discovered gate as `orphaned` there renders "compared
  nothing" as "found drift". That repo shape is the one the sub-key-absence half of
  this work exists to support, so the two halves have to be proven TOGETHER: the
  end-to-end case below is the adapter body the policy document tells a consumer to
  write, run through this gate.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from scripts.adapters.quality_adapter_lib import load_quality_adapter_permissive

from .git_fixture_support import init_git_repo
from .quality_bootstrap_support import seed_quality_repo
from .seeding_support import write_quality_adapter
from .support import ROOT

REFERENCE = ROOT / "skills" / "public" / "quality" / "references" / "coverage_floor_inventory.py"


def _load(repo_root: Path, policy: dict[str, object], *, replace: bool = False):
    spec = importlib.util.spec_from_file_location("coverage_floor_inventory_under_test", REFERENCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO_ROOT = repo_root
    module.POLICY = dict(policy) if replace else {**module.POLICY, **policy}
    return module


def _write(repo: Path, relative: str, text: str = "") -> Path:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _repo(tmp_path: Path, name: str = "repo") -> Path:
    """A git repo, because the reference now takes its file source from `git ls-files`.

    A filesystem walk sees build output and anything else `.gitignore` excludes, and a
    coverage-floor gate that discovers an ignored file reports on something the repo
    does not own. Fixtures therefore have to be the shape the gate reads.
    """
    repo = tmp_path / name
    repo.mkdir()
    init_git_repo(repo)
    return repo


def test_gate_discovery_honors_the_anchor_the_pattern_declares(tmp_path: Path) -> None:
    from tests.quality_gates.seeding_support import git

    repo = _repo(tmp_path)
    cases = (
        ("*-quality-gate.sh", "scripts/repo-quality-gate.sh", "scripts/*-quality-gate.sh"),
        (".githooks/pre-commit", ".githooks/pre-commit", ".githooks/pre-commit"),
        ("tools/check_coverage.py", "tools/check_coverage.py", "tools/check_coverage.py"),
        ("scripts/*/gate.sh", "scripts/ci/gate.sh", "scripts/*/gate.sh"),
        ("**/*-quality-gate.sh", "tools/nested/repo-quality-gate.sh", "**/*-quality-gate.sh"),
    )
    for _pattern, gate_relative, _anchored in cases:
        _write(repo, gate_relative)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "gates")
    for pattern, gate_relative, anchored in cases:
        module = _load(repo, {"gate_script_pattern": pattern})
        assert module.anchored_gate_pattern() == anchored, pattern
        discovered = [path.relative_to(repo).as_posix() for path in module.discover_gate_scripts()]
        assert gate_relative in discovered, pattern
        if "*" not in pattern:
            assert discovered == [gate_relative], pattern


def test_an_absolute_pattern_fails_rather_than_raising(tmp_path: Path) -> None:
    """`Path.glob` raises on an absolute pattern; every other bad input gets `FAIL:`."""
    module = _load(_repo(tmp_path), {"gate_script_pattern": "/etc/gate.sh"})

    with pytest.raises(SystemExit) as excinfo:
        module.discover_gate_scripts()
    assert "must be repo-relative" in str(excinfo.value)


def test_meta_check_counts_foreign_refs_under_the_declared_anchor(tmp_path: Path) -> None:
    """A referenced-but-undiscovered gate is drift wherever the anchor points."""
    repo = _repo(tmp_path)
    discovered = _write(repo, ".githooks/pre-commit")
    _write(repo, "lefthook.yml", "pre-commit:\n  run: .githooks/pre-commit\n")
    module = _load(repo, {"gate_script_pattern": ".githooks/pre-commit"})

    module.meta_check_gate_scripts([discovered])

    # Referenced and NOT discovered: the case the hardcoded `scripts/` prefix could
    # never report for a `.githooks` repo.
    _write(repo, "lefthook.yml", "pre-commit:\n  run: .githooks/pre-push\n")
    _write(repo, ".githooks/pre-push")
    module = _load(repo, {"gate_script_pattern": ".githooks/*"})
    with pytest.raises(SystemExit) as excinfo:
        module.meta_check_gate_scripts([discovered])
    assert ".githooks/pre-push" in str(excinfo.value)


def test_a_metacharacter_pattern_does_not_empty_the_foreign_half(tmp_path: Path) -> None:
    """The decomposition bug: a `(prefix, suffix)` pair is wrong for `**/` and `.*`.

    `Path(pattern).parent` gave the literal prefix `**/`, which no real path starts
    with, so `foreign` was structurally empty while `orphaned` fired on everything --
    a false red whose only remedy was to stop naming the pattern correctly.
    """
    repo = _repo(tmp_path)
    discovered = _write(repo, "tools/a-quality-gate.sh")
    _write(
        repo,
        "lefthook.yml",
        "pre-commit:\n  run: tools/a-quality-gate.sh\n  also: tools/a-quality-gate.sh\n",
    )
    module = _load(repo, {"gate_script_pattern": "tools/*-quality-gate.sh"})

    # Discovered AND referenced: neither half fires.
    module.meta_check_gate_scripts([discovered])

    # A second referenced gate the pattern claims but discovery did not return.
    _write(repo, "lefthook.yml", "pre-commit:\n  run: tools/b-quality-gate.sh\n")
    _write(repo, "tools/b-quality-gate.sh")
    with pytest.raises(SystemExit) as excinfo:
        module.meta_check_gate_scripts([discovered])
    message = str(excinfo.value)
    assert "Operational refs not matched by gate_script_pattern:" in message
    assert "tools/b-quality-gate.sh" in message


def test_a_repo_with_no_lefthook_and_no_ci_is_unmeasured_not_drifted(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The end-to-end case the two halves of this work have to satisfy together.

    This is the resolved policy the coverage-floor-policy document tells a consumer
    with no lefthook and no CI to declare: three sub-keys absent, and a `.githooks`
    stop gate. Discovery finding the gate is not enough -- before this, the very next
    step reported every discovered gate as orphaned, so following the documentation
    produced a hard red on a correctly-configured repo.
    """
    repo = _repo(tmp_path)
    gate = _write(repo, ".githooks/pre-commit", "#!/usr/bin/env bash\n")
    module = _load(
        repo,
        {
            "min_statements_threshold": 30,
            "fail_below_pct": 80.0,
            "warn_ceiling_pct": 95.0,
            "floor_drift_lock_pp": 1.0,
            "gate_script_pattern": ".githooks/pre-commit",
        },
        replace=True,
    )

    assert module.discover_gate_scripts() == [gate]
    # No KeyError: the three declared-absent sub-keys are simply not there.
    assert module.operational_ref_sources() == []
    assert module.collect_exemptions() == set()
    module.meta_check_gate_scripts([gate])

    assert (
        "SKIP: coverage_floor_policy declares no lefthook or CI surface" in capsys.readouterr().err
    )


def test_the_reported_consumer_shape_resolves_with_the_deleted_sub_keys_still_gone(
    tmp_path: Path,
) -> None:
    """The reported repro, migrated to the dotted vocabulary and proven end to end.

    A TypeScript/Workers repo with no lefthook, no CI workflows and no exemption list
    deleted those three sub-keys and got all three back from the merge, so the adapter
    described three files the repo does not have while appearing corrected. Deletion is
    still not a declaration; the DECLARATION is, and this pins that the resolved policy
    a consumer reads carries neither the deleted keys nor a phantom-path warning about
    them -- there is no phantom left to warn about.

    `gate_script_pattern` is the fourth key from the same report: a repo whose stop gate
    is `.githooks/pre-commit` had no way to say so, because the reference inventory
    anchored every pattern under `scripts/`. It survives resolution verbatim here, and
    `tests/quality_gates/test_coverage_floor_inventory_reference.py` proves the
    inventory now discovers it.
    """
    repo = seed_quality_repo(tmp_path)
    write_quality_adapter(
        repo,
        [
            "deliberately_absent:",
            "  coverage_floor_policy.lefthook_path: this repo has no lefthook",
            "  coverage_floor_policy.ci_workflow_glob: this repo runs no CI workflows",
            "  coverage_floor_policy.exemption_list_path: no exemption list exists here",
            "coverage_floor_policy:",
            "  min_statements_threshold: 30",
            "  fail_below_pct: 80.0",
            "  warn_ceiling_pct: 95.0",
            "  floor_drift_lock_pp: 1.0",
            "  gate_script_pattern: .githooks/pre-commit",
        ],
    )

    resolved = load_quality_adapter_permissive(repo)
    policy = resolved["data"]["coverage_floor_policy"]

    assert set(policy) == {
        "min_statements_threshold",
        "fail_below_pct",
        "warn_ceiling_pct",
        "floor_drift_lock_pp",
        "gate_script_pattern",
    }, policy
    assert policy["gate_script_pattern"] == ".githooks/pre-commit"
    assert "deliberately_absent_unasserted_paths" not in resolved["data"]
    assert not any("do not go looking" in warning for warning in resolved["warnings"])


def test_main_reuses_one_repo_file_snapshot_for_both_populations(
    tmp_path: Path, monkeypatch
) -> None:
    """`discover_gate_scripts` and `operational_ref_sources` used to each build
    their own unbound `RepoFileSnapshot` inside one `main()` run -- two
    `git ls-files` processes over the identical stable tree. `main` now threads
    one `RepoFileSnapshot` through both; this pins the count so it cannot
    silently double again.
    """
    repo = _repo(tmp_path)
    _write(repo, ".githooks/pre-commit", "#!/usr/bin/env bash\n")
    _write(repo, "coverage.json", '{"files": {}}\n')
    module = _load(
        repo,
        {
            "min_statements_threshold": 30,
            "fail_below_pct": 80.0,
            "warn_ceiling_pct": 95.0,
            "gate_script_pattern": ".githooks/pre-commit",
        },
        replace=True,
    )

    listing = sys.modules[module.RepoFileSnapshot.list_files.__module__]

    real_run = listing.run_process
    calls: list[list[str]] = []

    def counting_run(args, **kwargs):
        calls.append(list(args))
        return real_run(args, **kwargs)

    monkeypatch.setattr(listing, "run_process", counting_run)

    assert module.main() == 0
    ls_files_calls = [call for call in calls if call[:2] == ["git", "ls-files"]]
    assert len(ls_files_calls) == 1, ls_files_calls


def test_a_root_level_gate_is_not_lost_by_a_recursive_pattern(tmp_path: Path) -> None:
    """`fnmatch` and `Path.glob` disagree about `**/`, and the loss lands in DISCOVERY.

    `fnmatch("repo-quality-gate.sh", "**/*-quality-gate.sh")` is False because fnmatch
    demands the literal separator, while the glob a consumer reads the pattern AS
    matches zero directories. A gate silently dropped from the population is worse than
    a wrong `foreign` count: its declared floors are never read, so every file floored
    only there is reported unfloored.
    """
    repo = _repo(tmp_path)
    _write(repo, "repo-quality-gate.sh")
    _write(repo, "tools/nested/other-quality-gate.sh")
    module = _load(repo, {"gate_script_pattern": "**/*-quality-gate.sh"})

    discovered = [path.relative_to(repo).as_posix() for path in module.discover_gate_scripts()]
    assert discovered == ["repo-quality-gate.sh", "tools/nested/other-quality-gate.sh"]


def test_a_single_star_does_not_cross_a_directory_separator(tmp_path: Path) -> None:
    """The opposite direction of the same engine mismatch, on the DEFAULT pattern.

    `fnmatch`'s `*` crosses `/`, so a retired `scripts/archive/old-quality-gate.sh`
    was discovered under `scripts/*-quality-gate.sh` and then reported as drift --
    a hard red the operator could only clear by deleting a correct pattern.
    """
    repo = _repo(tmp_path)
    _write(repo, "scripts/repo-quality-gate.sh")
    _write(repo, "scripts/archive/old-quality-gate.sh")
    module = _load(repo, {"gate_script_pattern": "*-quality-gate.sh"})

    discovered = [path.relative_to(repo).as_posix() for path in module.discover_gate_scripts()]
    assert discovered == ["scripts/repo-quality-gate.sh"]
    assert not module.matches_gate_pattern("scripts/archive/old-quality-gate.sh")


def test_a_declared_surface_that_resolves_to_nothing_fails_rather_than_skipping(
    tmp_path: Path,
) -> None:
    """SKIP must mean DECLARED ABSENT, never "configured and wrong".

    A repo whose lefthook is `lefthook.yaml` keeps the default `lefthook.yml` in
    policy, nothing resolves, and an unconditional SKIP would render an unmeasured
    meta-check as a pass -- strictly worse than the loud wrong red it replaced.
    """
    repo = _repo(tmp_path)
    gate = _write(repo, "scripts/repo-quality-gate.sh")
    _write(repo, "lefthook.yaml", "pre-commit:\n  run: scripts/repo-quality-gate.sh\n")
    module = _load(repo, {"gate_script_pattern": "*-quality-gate.sh"})

    with pytest.raises(SystemExit) as excinfo:
        module.meta_check_gate_scripts([gate])
    message = str(excinfo.value)
    assert "still declares" in message
    assert "lefthook_path" in message
    assert "deliberately_absent" in message


def test_an_untracked_lefthook_is_not_a_source(tmp_path: Path) -> None:
    """One population for both halves.

    Resolving lefthook with `is_file()` while resolving workflows from the git listing
    made a gitignored lefthook count and a gitignored workflow not -- two readers over
    two populations inside the one function whose comment claims otherwise.
    """
    repo = _repo(tmp_path)
    _write(repo, ".gitignore", "lefthook.yml\n")
    _write(repo, "lefthook.yml", "pre-commit:\n  run: scripts/repo-quality-gate.sh\n")
    module = _load(repo, {"gate_script_pattern": "*-quality-gate.sh"})

    assert module.operational_ref_sources() == []


def test_a_missing_git_binary_fails_rather_than_raising(tmp_path: Path, monkeypatch) -> None:
    """The population is now git-derived, so git's absence is a stated precondition.

    A bare `FileNotFoundError` traceback is the one shape an operator cannot act on --
    the same defect the absolute-pattern branch exists to prevent.
    """
    module = _load(_repo(tmp_path), {})
    listing = sys.modules[module.RepoFileSnapshot.list_files.__module__]

    monkeypatch.setattr(
        listing,
        "run_process",
        lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("git")),
    )

    with pytest.raises(SystemExit) as excinfo:
        module.tracked_repo_files()
    assert "git is required to establish the scanned population" in str(excinfo.value)
