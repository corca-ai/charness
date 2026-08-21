from __future__ import annotations

from pathlib import Path

from .support import clone_quality_runner_repo, run_shell_script, write_executable


def test_quality_runner_isolates_focused_coverage_report_per_run(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    """Concurrent changed-line producers must not share the default report path.

    The producer derives coverage runtime filenames from its report stem.  A
    runner-owned temp report therefore isolates both the JSON and its derived
    runtime files; checking only the command's existence would miss the shared
    writer that caused the no-verdict collision.
    """
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    capture = tmp_path / "focused-coverage-argv.txt"
    write_executable(
        repo / "scripts" / "prepush_focused_changed_line_coverage.py",
        "#!/usr/bin/env python3\n"
        "import os\n"
        "import sys\n"
        "from pathlib import Path\n"
        "Path(os.environ['RUNNER_ARG_CAPTURE']).write_text(\n"
        "    '\\n'.join(sys.argv[1:]), encoding='utf-8'\n"
        ")\n",
    )
    env["CHARNESS_QUALITY_LABELS"] = "check-changed-line-mutation-coverage"
    env["RUNNER_ARG_CAPTURE"] = str(capture)

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    args = capture.read_text(encoding="utf-8").splitlines()
    report = Path(args[args.index("--coverage-json") + 1])
    assert report.name == "prepush-focused-coverage.json"
    assert report.is_absolute()
    assert not report.is_relative_to(repo)
    run_temp_base = Path(env.get("TMPDIR", "/tmp")).resolve()
    assert report.is_relative_to(run_temp_base)
