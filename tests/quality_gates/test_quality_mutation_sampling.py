"""Regression checks for repo-owned mutation sampling."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import scripts.mutation_changed_files_lib as mutation_changed_files_lib  # noqa: E402
import scripts.sample_mutation_files as sample_mutation_files  # noqa: E402
from scripts.mutation_changed_files_lib import (  # noqa: E402
    changed_line_numbers,
    classify_changed_file_exclusions,
    classify_changed_line_scope_gap,
)
from scripts.mutation_sampling_lib import (  # noqa: E402
    coverage_run_command,
    filter_eligible_by_coverage,
    filter_eligible_by_mutation_line_coverage,
    load_line_contexts,
    mutation_probe_paths,
    pytest_nodeid_from_coverage_context,
    rewrite_cosmic_ray_targets,
    rewrite_cosmic_ray_test_command,
    run_test_coverage,
    select_budgeted_sample,
    select_test_nodeids,
)
from scripts.sample_mutation_files import (  # noqa: E402
    list_changed,
    list_eligible,
    mutation_pathspecs,
    pool_for_path,
    write_manifest,
)


def test_list_changed_returns_stripped_paths_from_git_diff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def succeed_diff(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        assert command == [
            "git",
            "diff",
            "--name-only",
            "base-sha..HEAD",
            "--",
            *mutation_pathspecs(),
        ]
        return subprocess.CompletedProcess(command, 0, " scripts/a.py \n\nscripts/b.py\n", "")

    monkeypatch.setattr(sample_mutation_files.subprocess, "run", succeed_diff)

    assert list_changed(ROOT, "base-sha", "") == ["scripts/a.py", "scripts/b.py"]


def test_list_changed_skips_git_when_base_sha_is_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("git diff should not run without a base sha")

    monkeypatch.setattr(sample_mutation_files.subprocess, "run", fail_if_called)

    assert list_changed(ROOT, "", "head-sha") == []


def test_list_changed_returns_empty_for_empty_successful_diff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def empty_diff(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, "\n", "")

    monkeypatch.setattr(sample_mutation_files.subprocess, "run", empty_diff)

    assert list_changed(ROOT, "base-sha", "head-sha") == []


def test_list_changed_fails_closed_when_git_diff_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_diff(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.CalledProcessError(
            42,
            command,
            output="partial stdout",
            stderr="forced diff failure",
        )

    monkeypatch.setattr(sample_mutation_files.subprocess, "run", fail_diff)

    with pytest.raises(SystemExit) as exc_info:
        list_changed(ROOT, "base-sha", "head-sha")

    message = str(exc_info.value)
    assert "mutation changed-file diff failed while computing sample candidates" in message
    assert "base_sha: base-sha" in message
    assert "head_sha: head-sha" in message
    assert "command: git diff --name-only base-sha..head-sha --" in message
    assert "exit_code: 42" in message
    assert "partial stdout" in message
    assert "forced diff failure" in message


def test_sample_script_fails_closed_before_writes_when_changed_diff_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    bin_dir = tmp_path / "bin"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    bin_dir.mkdir()
    (scripts_dir / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
    config = repo / "cosmic-ray.toml"
    original_config = dedent(
        """\
        [cosmic-ray]
        module-path = ["scripts/original.py"]
        timeout = 30.0
        test-command = "python3 -m pytest -q tests"
        """
    )
    config.write_text(original_config, encoding="utf-8")
    git = bin_dir / "git"
    git.write_text(
        dedent(
            """\
            #!/usr/bin/env bash
            if [[ "$1" == "diff" && "$2" == "--name-only" ]]; then
              echo "forced changed diff failure" >&2
              exit 42
            fi
            exit 1
            """
        ),
        encoding="utf-8",
    )
    git.chmod(0o755)
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "MUTATION_BASE_SHA": "base-sha",
        "MUTATION_HEAD_SHA": "head-sha",
        "MUTATION_SAMPLE_SEED": "fixed-seed",
    }

    result = subprocess.run(
        ["python3", "scripts/sample_mutation_files.py", "--repo-root", str(repo), "--skip-coverage"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert "mutation changed-file diff failed while computing sample candidates" in result.stderr
    assert "base_sha: base-sha" in result.stderr
    assert "head_sha: head-sha" in result.stderr
    assert "exit_code: 42" in result.stderr
    assert "forced changed diff failure" in result.stderr
    assert config.read_text(encoding="utf-8") == original_config
    assert not (repo / "reports" / "mutation" / "sample.json").exists()
    assert not (repo / "reports" / "mutation" / "sample.md").exists()


def test_sample_rewrites_cosmic_ray_module_path(tmp_path: Path) -> None:
    config = tmp_path / "cosmic-ray.toml"
    config.write_text(
        dedent(
            """\
            [cosmic-ray]
            module-path = ["scripts/control_plane_lib.py"]
            timeout = 30.0
            test-command = "python3 -m pytest -q tests"
            """
        ),
        encoding="utf-8",
    )

    rewrite_cosmic_ray_targets(config, ["scripts/a.py", "scripts/b.py"])

    text = config.read_text(encoding="utf-8")
    assert '    "scripts/a.py",' in text
    assert '    "scripts/b.py",' in text
    assert 'test-command = "python3 -m pytest -q tests"' in text


def test_sample_script_rewrites_config_and_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    for name in ("a.py", "b.py", "c.py"):
        (scripts_dir / name).write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "cosmic-ray.toml").write_text(
        dedent(
            """\
            [cosmic-ray]
            module-path = ["scripts/control_plane_lib.py"]
            timeout = 30.0
            test-command = "python3 -m pytest -q tests"
            """
        ),
        encoding="utf-8",
    )
    env = {
        **os.environ,
        "MUTATION_SAMPLE_MAX_FILES": "2",
        "MUTATION_SAMPLE_CHANGED_QUOTA": "0",
        "MUTATION_SAMPLE_SEED": "fixed-seed",
        "MUTATION_SAMPLE_COVERAGE": "0",
    }
    # Scrub leakage from the parent step env so the nested coverage probe
    # cannot drag real SHAs into a tmp_path repo. See issue #190.
    env.pop("MUTATION_BASE_SHA", None)
    env.pop("MUTATION_HEAD_SHA", None)

    result = subprocess.run(
        ["python3", "scripts/sample_mutation_files.py", "--repo-root", str(repo)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    manifest = json.loads((repo / "reports" / "mutation" / "sample.json").read_text(encoding="utf-8"))
    assert manifest["base_sha"] is None
    assert len(manifest["sample"]) == 2
    text = (repo / "cosmic-ray.toml").read_text(encoding="utf-8")
    assert 'module-path = [\n' in text
    for path in manifest["sample"]:
        assert f'    "{path}",' in text
    assert "scripts/control_plane_lib.py" not in manifest["sample"]


def test_sample_pool_includes_core_and_skill_helper_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    for rel_path in (
        "charness",
        "runtime_bootstrap.py",
        "skill_runtime_bootstrap.py",
        "scripts/a.py",
        "skills/public/quality/scripts/helper.py",
        "skills/support/web-fetch/scripts/helper.py",
        "plugins/charness/scripts/generated.py",
        "tests/test_demo.py",
    ):
        path = repo / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("VALUE = 1\n", encoding="utf-8")

    eligible = list_eligible(repo)

    assert "charness" in eligible
    assert "runtime_bootstrap.py" in eligible
    assert "skill_runtime_bootstrap.py" in eligible
    assert "scripts/a.py" in eligible
    assert "skills/public/quality/scripts/helper.py" in eligible
    assert "skills/support/web-fetch/scripts/helper.py" in eligible
    assert "plugins/charness/scripts/generated.py" not in eligible
    assert "tests/test_demo.py" not in eligible
    assert pool_for_path("charness") == "core-python"
    assert pool_for_path("skills/public/quality/scripts/helper.py") == "public-skill-python"
    assert pool_for_path("skills/support/web-fetch/scripts/helper.py") == "support-skill-python"


def test_changed_sample_pathspecs_cover_all_mutation_pools() -> None:
    pathspecs = mutation_pathspecs()

    assert "charness" in pathspecs
    assert "runtime_bootstrap.py" in pathspecs
    assert "skill_runtime_bootstrap.py" in pathspecs
    assert "scripts" in pathspecs
    assert "skills/public" in pathspecs
    assert "skills/support" in pathspecs


def test_sample_filters_eligible_files_by_statement_coverage() -> None:
    eligible = ["scripts/a.py", "scripts/b.py", "scripts/c.py"]
    covered = {"scripts/a.py": {1}, "scripts/c.py": set()}
    statements = {
        "scripts/a.py": ({1, 2}, set()),
        "scripts/b.py": (set(), {1}),
        "scripts/c.py": (set(), set()),
    }

    assert (
        filter_eligible_by_coverage(
            eligible,
            covered,
            statements,
            min_file_coverage=1.0,
        )
        == ["scripts/a.py"]
    )


def test_sample_excludes_partially_covered_files_when_scope_gaps_are_fatal() -> None:
    eligible = ["scripts/a.py", "scripts/b.py"]
    covered = {"scripts/a.py": {1}, "scripts/b.py": {1, 2}}
    statements = {
        "scripts/a.py": ({1}, {2}),
        "scripts/b.py": ({1, 2}, set()),
    }

    assert (
        filter_eligible_by_coverage(
            eligible,
            covered,
            statements,
            min_file_coverage=1.0,
        )
        == ["scripts/b.py"]
    )


def test_sample_requires_mutation_line_coverage_after_file_coverage() -> None:
    assert filter_eligible_by_mutation_line_coverage(
        ["scripts/a.py", "scripts/b.py", "scripts/c.py"],
        {
            "scripts/a.py": {"mutable": 3, "covered": 3, "uncovered": 0},
            "scripts/b.py": {"mutable": 3, "covered": 2, "uncovered": 1},
            "scripts/c.py": {"mutable": 0, "covered": 0, "uncovered": 0},
        },
    ) == ["scripts/a.py"]


def test_changed_file_exclusions_split_filter_boundaries() -> None:
    assert classify_changed_file_exclusions(
        changed_before_coverage=[
            "scripts/file_floor.py",
            "scripts/mutation_line.py",
            "scripts/selected.py",
        ],
        coverage_eligible=["scripts/mutation_line.py", "scripts/selected.py"],
        eligible=["scripts/selected.py"],
        coverage_enabled=True,
    ) == (
        ["scripts/file_floor.py"],
        ["scripts/mutation_line.py"],
        ["scripts/file_floor.py", "scripts/mutation_line.py"],
    )

    assert classify_changed_file_exclusions(
        changed_before_coverage=["scripts/a.py"],
        coverage_eligible=[],
        eligible=[],
        coverage_enabled=False,
    ) == ([], [], [])


def test_changed_line_scope_gap_blocks_only_uncovered_changed_lines(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    changed = {
        "scripts/covered.py": {10, 11},  # changed lines covered; unrelated line 13 uncovered
        "scripts/uncovered.py": {20},  # changed line itself uncovered
        "scripts/untracked.py": {5},  # file never tracked by the suite
        "scripts/rename_noop.py": set(),  # rename/mode change with no content lines
    }
    monkeypatch.setattr(
        mutation_changed_files_lib,
        "changed_line_numbers",
        lambda repo_root, base, head, path: changed[path],
    )
    statement_lines = {
        "scripts/covered.py": ({10, 11, 12}, {13}),
        "scripts/uncovered.py": ({19}, {20, 21}),
    }

    gaps = classify_changed_line_scope_gap(
        repo_root=ROOT,
        base_sha="base",
        head_sha="head",
        changed_before_coverage=list(changed),
        statement_lines=statement_lines,
        coverage_enabled=True,
    )

    assert gaps == ["scripts/uncovered.py", "scripts/untracked.py"]

    assert (
        classify_changed_line_scope_gap(
            repo_root=ROOT,
            base_sha="base",
            head_sha="head",
            changed_before_coverage=list(changed),
            statement_lines=statement_lines,
            coverage_enabled=False,
        )
        == []
    )
    assert (
        classify_changed_line_scope_gap(
            repo_root=ROOT,
            base_sha=None,
            head_sha="head",
            changed_before_coverage=list(changed),
            statement_lines=statement_lines,
            coverage_enabled=True,
        )
        == []
    )


def test_changed_line_numbers_parses_added_lines_over_range(tmp_path: Path) -> None:
    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True)

    git("init")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    target = tmp_path / "mod.py"
    target.write_text("a = 1\nb = 2\nc = 3\n", encoding="utf-8")
    git("add", "mod.py")
    git("commit", "-m", "base")
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout.strip()
    target.write_text("a = 1\nb = 20\nc = 3\nd = 4\n", encoding="utf-8")
    git("commit", "-am", "head")

    assert changed_line_numbers(tmp_path, base, "HEAD", "mod.py") == {2, 4}
    # Empty base sha returns no changed lines (fail-safe guard).
    assert changed_line_numbers(tmp_path, "", "HEAD", "mod.py") == set()


def test_sample_budget_limits_executable_mutants_and_test_nodeids(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    test_path = repo / "tests" / "test_demo.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text(
        "def test_fast():\n    pass\n\ndef test_slow():\n    pass\n",
        encoding="utf-8",
    )
    chosen, excluded, workload = select_budgeted_sample(
        repo_root=repo,
        candidates=["scripts/huge.py", "scripts/fast.py", "scripts/slow.py"],
        limit=3,
        seed="fixed",
        selected=[],
        selected_workload=0,
        mutation_line_coverage={
            "scripts/huge.py": {"covered": 100, "mutable": 100, "uncovered": 0},
            "scripts/fast.py": {"covered": 5, "mutable": 5, "uncovered": 0},
            "scripts/slow.py": {"covered": 6, "mutable": 6, "uncovered": 0},
        },
        line_contexts={
            "scripts/fast.py": {1: {"tests.test_demo.test_fast"}},
            "scripts/slow.py": {1: {"tests.test_demo.test_fast", "tests.test_demo.test_slow"}},
        },
        coverage_enabled=True,
        max_executable_mutants=10,
        max_executable_mutants_per_file=50,
        max_test_nodeids=1,
    )

    assert chosen == ["scripts/fast.py"]
    assert "scripts/huge.py" in excluded
    assert "scripts/slow.py" in excluded
    assert workload == 5


def test_budgeted_sample_records_candidates_excluded_by_quota(tmp_path: Path) -> None:
    chosen, excluded, workload = select_budgeted_sample(
        repo_root=tmp_path,
        candidates=["scripts/a.py", "scripts/b.py", "scripts/c.py"],
        limit=1,
        seed="fixed",
        selected=[],
        selected_workload=0,
        mutation_line_coverage={
            "scripts/a.py": {"covered": 1},
            "scripts/b.py": {"covered": 1},
            "scripts/c.py": {"covered": 1},
        },
        line_contexts={},
        coverage_enabled=False,
        max_executable_mutants=10,
        max_executable_mutants_per_file=10,
        max_test_nodeids=10,
    )

    assert len(chosen) == 1
    assert sorted(chosen + excluded) == ["scripts/a.py", "scripts/b.py", "scripts/c.py"]
    assert workload == 1


def test_budgeted_sample_requires_each_file_to_have_pytest_nodeids(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    test_path = repo / "tests" / "test_demo.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text("def test_demo():\n    pass\n", encoding="utf-8")

    chosen, excluded, workload = select_budgeted_sample(
        repo_root=repo,
        candidates=["scripts/import_only.py", "scripts/tested.py"],
        limit=2,
        seed="fixed",
        selected=[],
        selected_workload=0,
        mutation_line_coverage={
            "scripts/import_only.py": {"covered": 1, "mutable": 1, "uncovered": 0},
            "scripts/tested.py": {"covered": 2, "mutable": 2, "uncovered": 0},
        },
        line_contexts={"scripts/tested.py": {1: {"tests.test_demo.test_demo"}}},
        coverage_enabled=True,
        max_executable_mutants=10,
        max_executable_mutants_per_file=10,
        max_test_nodeids=10,
    )

    assert chosen == ["scripts/tested.py"]
    assert excluded == ["scripts/import_only.py"]
    assert workload == 2


def test_mutation_line_probe_paths_stay_under_reports(tmp_path: Path) -> None:
    probe_config, probe_session = mutation_probe_paths(tmp_path)

    assert probe_config == tmp_path / "reports" / "mutation" / "cosmic-ray-sample-probe.toml"
    assert probe_session == tmp_path / "reports" / "mutation" / "cosmic-ray-sample-probe.sqlite"


def test_cosmic_ray_accepts_extensionless_charness_target(tmp_path: Path) -> None:
    if shutil.which("cosmic-ray") is None:
        pytest.skip("cosmic-ray unavailable")
    config = tmp_path / "cosmic-ray.toml"
    session = tmp_path / "cosmic-ray.sqlite"
    config.write_text(
        dedent(
            """\
            [cosmic-ray]
            module-path = ["charness"]
            timeout = 30.0
            excluded-modules = []
            test-command = "python3 -m pytest -q tests/quality_gates/test_quality_mutation_sampling.py"

            [cosmic-ray.distributor]
            name = "local"
            """
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        ["cosmic-ray", "init", str(config), str(session)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert session.is_file()


def test_sample_derives_pytest_nodeids_from_coverage_contexts(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    test_path = repo / "tests" / "control_plane" / "test_demo.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text("def test_demo():\n    pass\n", encoding="utf-8")

    assert (
        pytest_nodeid_from_coverage_context(
            repo,
            "tests.control_plane.test_demo.TestCase.test_method",
        )
        == "tests/control_plane/test_demo.py::TestCase::test_method"
    )
    assert select_test_nodeids(
        repo,
        ["scripts/a.py"],
        {"scripts/a.py": {1: {"tests.control_plane.test_demo.test_demo"}}},
    ) == ["tests/control_plane/test_demo.py::test_demo"]


def test_sample_rewrites_cosmic_ray_test_command(tmp_path: Path) -> None:
    config = tmp_path / "cosmic-ray.toml"
    config.write_text(
        dedent(
            """\
            [cosmic-ray]
            module-path = ["scripts/a.py"]
            test-command = "python3 -m pytest -q tests"
            """
        ),
        encoding="utf-8",
    )

    rewrite_cosmic_ray_test_command(
        config,
        "python3 -m pytest -q tests/test_demo.py::test_demo",
    )

    assert 'test-command = "python3 -m pytest -q tests/test_demo.py::test_demo"' in config.read_text(
        encoding="utf-8"
    )


def test_manifest_surfaces_changed_files_excluded_by_coverage(tmp_path: Path) -> None:
    manifest_json = tmp_path / "sample.json"
    manifest_md = tmp_path / "sample.md"
    manifest = {
        "seed": "fixed-seed",
        "base_sha": "base",
        "head_sha": "head",
        "max_files": 2,
        "eligible_count": 1,
        "all_eligible_count": 2,
        "covered_eligible_count": 1,
        "mutation_line_eligible_count": 1,
        "mutation_line_coverage": {"scripts/a.py": {"mutable": 1, "covered": 1, "uncovered": 0}},
        "changed_files_before_coverage": ["scripts/a.py", "scripts/b.py"],
        "changed_files": ["scripts/a.py"],
        "changed_files_excluded_by_file_coverage": ["scripts/file_floor.py"],
        "changed_files_excluded_by_mutation_line_coverage": ["scripts/mutation_line.py"],
        "uncovered_changed_files": ["scripts/b.py"],
        "selection_excluded_changed_files": ["scripts/c.py"],
        "changed_sample": ["scripts/a.py"],
        "fill_sample": [],
        "sample": ["scripts/a.py"],
        "pools": {
            "core-python": {"all_eligible": 2, "eligible": 1, "sample": 1},
        },
        "min_file_coverage": 1.0,
        "test_command": "python3 -m pytest -q tests/control_plane",
    }

    write_manifest(manifest, manifest_json, manifest_md)

    payload = json.loads(manifest_json.read_text(encoding="utf-8"))
    text = manifest_md.read_text(encoding="utf-8")
    assert payload["uncovered_changed_files"] == ["scripts/b.py"]
    assert payload["changed_files_excluded_by_file_coverage"] == ["scripts/file_floor.py"]
    assert payload["changed_files_excluded_by_mutation_line_coverage"] == [
        "scripts/mutation_line.py"
    ]
    assert payload["selection_excluded_changed_files"] == ["scripts/c.py"]
    assert "- Changed pool files: 2" in text
    assert "- Changed files with uncovered changed lines (blocking): 0" in text
    assert "## Changed files with uncovered changed lines (blocking)" in text
    assert "- Changed files excluded by coverage/mutation-line filters (advisory union): 1" in text
    assert "- Changed files excluded by file coverage floor: 1" in text
    assert "- Changed files excluded by mutation-line coverage: 1" in text
    assert "- Changed files excluded by selection budgets: 1" in text
    assert "## Changed files excluded by file coverage" in text
    assert "- `scripts/file_floor.py`" in text
    assert "## Changed files excluded by mutation-line coverage" in text
    assert "- `scripts/mutation_line.py`" in text
    assert "- File coverage floor: 1.0" in text
    assert "- Eligible files after mutation-line filter: 1" in text
    assert "- Mutation pools: core-python 1/1 selected (2 pool)" in text


def test_manifest_pool_counts_include_root_and_skill_helpers(tmp_path: Path) -> None:
    manifest_json = tmp_path / "sample.json"
    manifest_md = tmp_path / "sample.md"
    manifest = {
        "seed": "fixed-seed",
        "base_sha": "base",
        "head_sha": "head",
        "max_files": 3,
        "eligible_count": 3,
        "all_eligible_count": 6,
        "covered_eligible_count": 3,
        "mutation_line_eligible_count": 3,
        "mutation_line_coverage": {},
        "changed_files_before_coverage": [],
        "changed_files": [],
        "uncovered_changed_files": [],
        "selection_excluded_changed_files": [],
        "changed_sample": [],
        "fill_sample": [
            "charness",
            "skills/public/quality/scripts/helper.py",
            "skills/support/web-fetch/scripts/helper.py",
        ],
        "sample": [
            "charness",
            "skills/public/quality/scripts/helper.py",
            "skills/support/web-fetch/scripts/helper.py",
        ],
        "pools": {
            "core-python": {"all_eligible": 3, "eligible": 1, "sample": 1},
            "public-skill-python": {"all_eligible": 2, "eligible": 1, "sample": 1},
            "support-skill-python": {"all_eligible": 1, "eligible": 1, "sample": 1},
        },
        "min_file_coverage": 1.0,
        "test_command": "python3 -m pytest -q tests",
    }

    write_manifest(manifest, manifest_json, manifest_md)

    text = manifest_md.read_text(encoding="utf-8")
    assert "core-python 1/1 selected (3 pool)" in text
    assert "public-skill-python 1/1 selected (2 pool)" in text
    assert "support-skill-python 1/1 selected (1 pool)" in text


def test_coverage_run_command_wraps_pytest_module_command(tmp_path: Path) -> None:
    command = coverage_run_command("python3 -m pytest -q tests/control_plane", tmp_path / ".coverage")

    assert command[:6] == ["python3", "-m", "coverage", "run", "--data-file", str(tmp_path / ".coverage")]
    assert command[6:] == ["-m", "pytest", "-q", "tests/control_plane"]


def test_mutation_coverage_tracks_python_subprocesses(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script = repo / "scripts" / "cli_target.py"
    test_file = repo / "tests" / "test_cli_target.py"
    script.parent.mkdir(parents=True)
    test_file.parent.mkdir(parents=True)
    script.write_text(
        dedent(
            """\
            def main() -> int:
                value = 40 + 2
                print(value)
                return 0


            if __name__ == "__main__":
                raise SystemExit(main())
            """
        ),
        encoding="utf-8",
    )
    test_file.write_text(
        dedent(
            """\
            from __future__ import annotations

            import subprocess
            import sys
            from pathlib import Path


            def test_cli_target_subprocess() -> None:
                repo = Path(__file__).resolve().parents[1]
                result = subprocess.run(
                    [sys.executable, "scripts/cli_target.py"],
                    cwd=repo,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                assert result.stdout.strip() == "42"
            """
        ),
        encoding="utf-8",
    )

    coverage_json = repo / "reports" / "mutation" / "coverage.json"
    run_test_coverage(repo, "python3 -m pytest -q tests/test_cli_target.py", coverage_json)

    payload = json.loads(coverage_json.read_text(encoding="utf-8"))
    assert "scripts/cli_target.py" in payload["files"]
    assert {2, 3, 4} <= set(payload["files"]["scripts/cli_target.py"]["executed_lines"])
    assert select_test_nodeids(
        repo,
        ["scripts/cli_target.py"],
        load_line_contexts(repo, coverage_json),
    ) == ["tests/test_cli_target.py::test_cli_target_subprocess"]


def test_mutation_coverage_drops_stale_parallel_shards(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script = repo / "scripts" / "cli_target.py"
    test_file = repo / "tests" / "test_cli_target.py"
    script.parent.mkdir(parents=True)
    test_file.parent.mkdir(parents=True)
    script.write_text(
        "def main() -> int:\n    print('fresh')\n    return 0\n\nif __name__ == '__main__':\n    raise SystemExit(main())\n",
        encoding="utf-8",
    )
    test_file.write_text(
        "import subprocess, sys\nfrom pathlib import Path\n\n"
        "def test_cli_target_subprocess() -> None:\n"
        "    repo = Path(__file__).resolve().parents[1]\n"
        "    subprocess.run([sys.executable, 'scripts/cli_target.py'], cwd=repo, check=True)\n",
        encoding="utf-8",
    )
    coverage_json = repo / "reports" / "mutation" / "coverage.json"
    coverage_json.parent.mkdir(parents=True)
    stale_shard = coverage_json.with_name(".mutation-coverage.stale")
    stale_shard.write_text("not a coverage sqlite database", encoding="utf-8")

    run_test_coverage(repo, "python3 -m pytest -q tests/test_cli_target.py", coverage_json)

    assert not stale_shard.exists()
