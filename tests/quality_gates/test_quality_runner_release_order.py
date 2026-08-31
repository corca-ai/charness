from __future__ import annotations

import os
import shlex
import shutil
import sys
from pathlib import Path

import pytest

from .support import ROOT, clone_quality_runner_repo, run_shell_script, write_executable

_RUNNER_OVERRIDE = "CHARNESS_TEST_RUN_QUALITY_SCRIPT"
_RELEASE_LABEL = "pytest-release"


def _runner_path() -> Path:
    return Path(os.environ.get(_RUNNER_OVERRIDE, ROOT / "scripts" / "run-quality.sh"))


def _append_event_script(event: str) -> str:
    return (
        "#!/usr/bin/env python3\n"
        "import os\n"
        "from pathlib import Path\n"
        "with Path(os.environ['ORDER_LOG']).open('a', encoding='utf-8') as stream:\n"
        f"    stream.write({event!r} + '\\n')\n"
        f"if os.environ.get('QUALITY_FAIL_LABEL') == {event!r}: raise SystemExit(1)\n"
    )


def _release_fixture(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> tuple[Path, dict[str, str], Path]:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    source_runner = _runner_path()
    dest_runner = repo / "scripts" / "run-quality.sh"
    if source_runner.read_bytes() != dest_runner.read_bytes():
        shutil.copy2(source_runner, dest_runner)
        from tests.quality_gates.seeding_support import git

        git(repo, "add", "--", "scripts/run-quality.sh")
        git(repo, "commit", "-q", "-m", "seed")

    event_log = tmp_path / "release-order.log"
    producer_args_log = tmp_path / "release-producer-args.log"
    write_executable(
        repo / "bin" / "python3",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "if [[ \"${1:-}\" == \"-m\" && \"${2:-}\" == \"pytest\" ]]; then\n"
        "  printf '%s\\n' pytest-release >> \"$ORDER_LOG\"\n"
        "  if [[ \"${QUALITY_FAIL_LABEL:-}\" == \"pytest-release\" ]]; then exit 1; fi\n"
        "  exit 0\n"
        f"fi\nexec {shlex.quote(sys.executable)} \"$@\"\n",
    )
    write_executable(repo / "scripts" / "validate_skills.py", _append_event_script("validate-skills"))
    write_executable(
        repo / "skills" / "public" / "quality" / "scripts" / "check_runtime_budget.py",
        _append_event_script("check-runtime-budget"),
    )
    write_executable(
        repo / "scripts" / "release_changed_line_coverage.py",
        "#!/usr/bin/env python3\n"
        "import os\n"
        "import sys\n"
        "from pathlib import Path\n"
        "with Path(os.environ['ORDER_LOG']).open('a', encoding='utf-8') as stream:\n"
        "    stream.write('release-changed-line-coverage\\n')\n"
        "Path(os.environ['PRODUCER_ARGS_LOG']).write_text(' '.join(sys.argv[1:]), encoding='utf-8')\n"
        "if os.environ.get('QUALITY_PARTIAL_CHANGED_LINE') == '1': raise SystemExit(4)\n"
        "if os.environ.get('QUALITY_FAIL_LABEL') == 'release-changed-line-coverage': raise SystemExit(1)\n",
    )
    tmp_root = tmp_path / "tmp"
    tmp_root.mkdir()
    env.update(
        {
            "ORDER_LOG": str(event_log),
            "PRODUCER_ARGS_LOG": str(producer_args_log),
            "CHARNESS_RUNTIME_ROOT": str(tmp_path / "runtime"),
            "PYTHONPYCACHEPREFIX": str(tmp_path / "pycache"),
            "PYTEST_ADDOPTS": f"-o cache_dir={tmp_path / 'pytest-cache'}",
            "TMPDIR": str(tmp_root),
        }
    )
    return repo, env, event_log


def test_release_runs_pytest_before_later_checks(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert event_log.read_text(encoding="utf-8").splitlines() == [
        "pytest-release",
        "validate-skills",
        "check-runtime-budget",
        "release-changed-line-coverage",
    ]
    producer_args_log = tmp_path / "release-producer-args.log"
    producer_args = producer_args_log.read_text(encoding="utf-8").split()
    base_index = producer_args.index("--base-sha")
    coverage_index = producer_args.index("--coverage-json")
    assert len(producer_args[base_index + 1]) == 40
    assert producer_args[coverage_index + 1].startswith(str(tmp_path / "runtime"))
    assert str(repo) not in producer_args[coverage_index + 1]
    assert f"PASS {_RELEASE_LABEL}" in result.stdout
    assert "PASS validate-packaging-committed" in result.stdout
    assert "PASS check-command-docs" in result.stdout
    assert "PASS check-test-production-ratio" in result.stdout


def test_release_pytest_failure_stops_before_later_checks(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)
    env["QUALITY_FAIL_LABEL"] = _RELEASE_LABEL

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env)

    assert result.returncode == 1, result.stderr
    assert event_log.read_text(encoding="utf-8").splitlines() == [_RELEASE_LABEL]
    assert "release pytest failed; stopping before later release checks." in result.stderr


def test_release_predecessor_failure_skips_changed_line_proof(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)
    env["QUALITY_FAIL_LABEL"] = "check-runtime-budget"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env)

    assert result.returncode == 1, result.stderr
    assert event_log.read_text(encoding="utf-8").splitlines() == [
        "pytest-release",
        "validate-skills",
        "check-runtime-budget",
    ]
    assert "release-changed-line-coverage" not in result.stdout


def test_release_changed_line_failure_fails_release_and_is_last_once(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)
    env["QUALITY_FAIL_LABEL"] = "release-changed-line-coverage"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env)

    assert result.returncode == 1, result.stderr
    events = event_log.read_text(encoding="utf-8").splitlines()
    assert events[-1] == "release-changed-line-coverage"
    assert events.count("release-changed-line-coverage") == 1
    assert "FAIL release-changed-line-coverage" in result.stdout


def test_release_partial_changed_line_fails_the_release(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)
    env["QUALITY_PARTIAL_CHANGED_LINE"] = "1"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env)

    assert result.returncode == 4, result.stderr
    assert event_log.read_text(encoding="utf-8").splitlines()[-1] == "release-changed-line-coverage"
    assert "FAIL release-changed-line-coverage" in result.stdout
    assert "PASS release-changed-line-coverage" not in result.stdout


def test_release_explicit_non_claim_omits_only_changed_line_proof(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)

    result = run_shell_script(
        repo / "scripts" / "run-quality.sh",
        "--release",
        "--non-claim=release-changed-line-coverage",
        cwd=repo,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert event_log.read_text(encoding="utf-8").splitlines() == [
        "pytest-release",
        "validate-skills",
        "check-runtime-budget",
    ]
    assert "PASS release-changed-line-coverage" not in result.stdout
    assert "FAIL release-changed-line-coverage" not in result.stdout
    assert (
        "NON-CLAIM: release-changed-line-coverage was not run by explicit release policy; "
        "no changed-line verdict exists"
    ) in result.stderr


def test_changed_line_non_claim_requires_release(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, _event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)

    result = run_shell_script(
        repo / "scripts" / "run-quality.sh",
        "--non-claim=release-changed-line-coverage",
        cwd=repo,
        env=env,
    )

    assert result.returncode == 2
    assert "requires --release" in result.stderr


def test_release_refuses_unknown_non_claim_label(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, _event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)

    result = run_shell_script(
        repo / "scripts" / "run-quality.sh",
        "--release",
        "--non-claim=mutation",
        cwd=repo,
        env=env,
    )

    assert result.returncode == 2
    assert "unsupported --non-claim label mutation" in result.stderr


def test_release_refuses_a_label_filter(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, _event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = "pytest-release"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env)

    assert result.returncode == 2
    assert "one indivisible lane" in result.stderr


@pytest.mark.parametrize("runner_args", [(), ("--full",)])
def test_non_release_lanes_never_run_changed_line_proof(
    runner_args: tuple[str, ...], tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)

    result = run_shell_script(repo / "scripts" / "run-quality.sh", *runner_args, cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert "release-changed-line-coverage" not in event_log.read_text(encoding="utf-8")
    assert "release-changed-line-coverage" not in result.stdout


def test_explicit_release_pytest_label_runs_only_release_pytest(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)
    env["CHARNESS_QUALITY_LABELS"] = _RELEASE_LABEL

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert event_log.read_text(encoding="utf-8").splitlines() == [_RELEASE_LABEL]
    assert f"PASS {_RELEASE_LABEL}" in result.stdout
    assert "PASS validate-skills" not in result.stdout
