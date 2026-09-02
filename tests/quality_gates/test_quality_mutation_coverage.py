"""Regression checks for mutation sampling coverage collection."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest

from scripts.mutation.mutation_sampling_lib import (
    coverage_run_command,
    coverage_runtime_paths,
    load_line_contexts,
    run_test_coverage,
    select_test_nodeids,
)


def test_coverage_runtime_files_are_namespaced_by_report(tmp_path: Path) -> None:
    broad = tmp_path / "reports" / "mutation" / "test-coverage.json"
    sample = tmp_path / "reports" / "mutation" / "sample-coverage.json"
    focused = tmp_path / "reports" / "mutation" / "release-changed-line-coverage.json"

    broad_paths = coverage_runtime_paths(broad, repo_root=tmp_path)
    sample_paths = coverage_runtime_paths(sample, repo_root=tmp_path)
    focused_paths = coverage_runtime_paths(focused, repo_root=tmp_path)

    assert set(broad_paths).isdisjoint(sample_paths)
    assert set(broad_paths).isdisjoint(focused_paths)
    assert set(sample_paths).isdisjoint(focused_paths)
    assert broad_paths[0].name == ".test-coverage.mutation-coverage"
    assert sample_paths[0].name == ".sample-coverage.mutation-coverage"
    assert focused_paths[0].name == ".release-changed-line-coverage.mutation-coverage"


def test_coverage_run_command_wraps_pytest_module_command(tmp_path: Path) -> None:
    command = coverage_run_command(
        "python3 -m pytest -q tests/control_plane", tmp_path / ".coverage"
    )

    assert command[:6] == [
        "python3",
        "-m",
        "coverage",
        "run",
        "--data-file",
        str(tmp_path / ".coverage"),
    ]
    assert command[6:] == ["-m", "pytest", "-q", "tests/control_plane"]


@pytest.mark.boundary_contract(
    reason="prove coverage crosses the repository test's real Python child-process boundary"
)
def test_mutation_coverage_tracks_python_subprocesses(tmp_path: Path) -> None:
    pytest.importorskip("coverage", reason="coverage package required for mutation coverage probe")
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
    pytest.importorskip("coverage", reason="coverage package required for mutation coverage probe")
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
    data_file, _, _ = coverage_runtime_paths(coverage_json, repo_root=repo)
    stale_shard = data_file.with_name(data_file.name + ".stale")
    stale_shard.write_text("not a coverage sqlite database", encoding="utf-8")

    run_test_coverage(repo, "python3 -m pytest -q tests/test_cli_target.py", coverage_json)

    assert not stale_shard.exists()
