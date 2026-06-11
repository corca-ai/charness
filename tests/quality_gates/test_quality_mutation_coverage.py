"""Regression checks for mutation sampling coverage collection."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest

from scripts.mutation_sampling_lib import (
    coverage_run_command,
    load_line_contexts,
    run_test_coverage,
    select_test_nodeids,
)


def test_coverage_run_command_wraps_pytest_module_command(tmp_path: Path) -> None:
    command = coverage_run_command("python3 -m pytest -q tests/control_plane", tmp_path / ".coverage")

    assert command[:6] == ["python3", "-m", "coverage", "run", "--data-file", str(tmp_path / ".coverage")]
    assert command[6:] == ["-m", "pytest", "-q", "tests/control_plane"]


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
    stale_shard = coverage_json.with_name(".mutation-coverage.stale")
    stale_shard.write_text("not a coverage sqlite database", encoding="utf-8")

    run_test_coverage(repo, "python3 -m pytest -q tests/test_cli_target.py", coverage_json)

    assert not stale_shard.exists()
