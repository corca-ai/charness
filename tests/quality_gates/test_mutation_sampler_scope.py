"""Sampler scope: rotating budgeted slice, not whole-suite context coverage."""

from __future__ import annotations

from pathlib import Path

from scripts.mutation.mutation_sample_scope import (
    SECONDS_PER_MUTANT,
    _load_repo_runtime_bootstrap,
    cap_mutants_to_remaining_job,
    focused_statement_lines_for_changed_files,
    mapped_test_targets,
    mutation_test_command_for_sample,
    standing_pytest_command,
)
from scripts.mutation.sample_mutation_files import select_eligible_for_mutation

ROOT = Path(__file__).resolve().parents[2]


def test_select_eligible_does_not_run_whole_suite_coverage(tmp_path: Path) -> None:
    coverage_json = tmp_path / "coverage.json"
    eligible, coverage_eligible, contexts, workload = select_eligible_for_mutation(
        repo_root=tmp_path,
        config_path=tmp_path / "cosmic-ray.toml",
        all_eligible=["scripts/a.py", "scripts/b.py"],
        coverage_enabled=True,
        coverage_json=coverage_json,
        test_command="python3 -m pytest -q tests",
        min_file_coverage=0.85,
        baseline_abort_marker_path=tmp_path / "abort.json",
    )
    assert not coverage_json.exists()
    assert eligible == ["scripts/a.py", "scripts/b.py"]
    assert coverage_eligible == eligible
    assert contexts == {}
    assert workload == {}


def test_mutation_test_command_uses_mapped_targets_not_the_suite(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        "scripts.mutation.mutation_sample_scope.tests_referencing_paths",
        lambda repo_root, paths: {paths[0]: ["tests/quality_gates/test_demo.py"]},
    )
    command = mutation_test_command_for_sample(
        tmp_path,
        ["scripts/demo.py"],
        {},
        "env CHARNESS_ALLOW_BARE_PYTEST=1 python3 -m pytest -q tests",
        coverage_enabled=True,
        max_test_nodeids=40,
    )
    assert command is not None
    assert "run_standing_pytest.py" in command
    assert "--pytest-target" in command
    assert "tests/quality_gates/test_demo.py" in command
    assert "-q tests" not in command


def test_mutation_test_command_refuses_the_whole_suite_when_nothing_maps(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        "scripts.mutation.mutation_sample_scope.tests_referencing_paths",
        lambda repo_root, paths: {},
    )
    command = mutation_test_command_for_sample(
        tmp_path,
        ["scripts/demo.py"],
        {},
        "python3 -m pytest -q tests",
        coverage_enabled=True,
    )
    assert command is None


def test_mapped_test_targets_honor_the_nodeid_budget(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.mutation.mutation_sample_scope.tests_referencing_paths",
        lambda repo_root, paths: {
            "scripts/a.py": ["tests/test_a.py", "tests/test_b.py", "tests/test_c.py"]
        },
    )
    assert mapped_test_targets(tmp_path, ["scripts/a.py"], limit=2) == [
        "tests/test_a.py",
        "tests/test_b.py",
    ]


def test_standing_pytest_command_passes_each_target() -> None:
    command = standing_pytest_command(["tests/a.py", "tests/b.py"])
    assert command.count("--pytest-target") == 2


def test_public_sample_contract_forbids_whole_suite_probes() -> None:
    text = (
        ROOT / "skills" / "public" / "quality" / "references" / "mutation-testing.md"
    ).read_text(encoding="utf-8")
    assert "Do not run the full test suite" in text
    assert "per-test coverage contexts" in text
    assert "run_test_coverage` defaults to statement coverage" in text
    assert "mutant sampler must not" in text


def test_cap_mutants_shrinks_to_remaining_job_budget(monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.mutation.mutation_sample_scope.job_budget_from_env",
        lambda: (1_000_000, 10_800),
    )
    monkeypatch.setattr(
        "scripts.mutation.mutation_sample_scope.resolve_exec_timeout_seconds",
        lambda requested, **_kwargs: (900, None),
    )
    assert cap_mutants_to_remaining_job(120) == 900 // SECONDS_PER_MUTANT


def test_cap_mutants_falls_back_to_one_when_budget_is_gone(monkeypatch) -> None:
    from scripts.mutation.mutation_outer_budget import InnerTimeoutExceedsOuterBudget

    monkeypatch.setattr(
        "scripts.mutation.mutation_sample_scope.job_budget_from_env",
        lambda: (1_000_000, 10_800),
    )

    def _raise(requested, **_kwargs):
        raise InnerTimeoutExceedsOuterBudget("gone")

    monkeypatch.setattr(
        "scripts.mutation.mutation_sample_scope.resolve_exec_timeout_seconds", _raise
    )
    assert cap_mutants_to_remaining_job(120) == 1


def test_focused_statement_lines_skips_empty_changed_paths(tmp_path: Path) -> None:
    assert (
        focused_statement_lines_for_changed_files(
            repo_root=tmp_path,
            changed_paths=[],
            coverage_json=tmp_path / "coverage.json",
            baseline_abort_marker_path=tmp_path / "abort.json",
            max_test_nodeids=40,
        )
        == {}
    )


def test_focused_statement_lines_skips_when_nothing_maps(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        "scripts.mutation.mutation_sample_scope.tests_referencing_paths",
        lambda repo_root, paths: {},
    )
    assert (
        focused_statement_lines_for_changed_files(
            repo_root=tmp_path,
            changed_paths=["scripts/a.py"],
            coverage_json=tmp_path / "coverage.json",
            baseline_abort_marker_path=tmp_path / "abort.json",
            max_test_nodeids=40,
        )
        == {}
    )


def test_mapped_test_targets_dedupes_shared_targets(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.mutation.mutation_sample_scope.tests_referencing_paths",
        lambda repo_root, paths: {
            "scripts/a.py": ["tests/test_shared.py"],
            "scripts/b.py": ["tests/test_shared.py"],
        },
    )
    assert mapped_test_targets(
        tmp_path, ["scripts/a.py", "scripts/b.py"], limit=40
    ) == ["tests/test_shared.py"]


def test_bootstrap_reinserts_repo_root_when_missing(monkeypatch) -> None:
    import sys

    kept = [p for p in sys.path if p not in (str(ROOT), "")]
    monkeypatch.setattr(sys, "path", kept)
    assert str(ROOT) not in sys.path
    _load_repo_runtime_bootstrap()
    assert str(ROOT) in sys.path
