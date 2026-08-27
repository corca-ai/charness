from __future__ import annotations

import os
import re
import shlex
import shutil
import sys
from pathlib import Path

from .support import ROOT, clone_quality_runner_repo, run_shell_script, write_executable

_RUNNER_OVERRIDE = "CHARNESS_TEST_RUN_QUALITY_SCRIPT"
_RELEASE_LABEL = "pytest-release"
_MUTATION_LABEL = "check-changed-line-mutation-coverage"


def _runner_path() -> Path:
    return Path(os.environ.get(_RUNNER_OVERRIDE, ROOT / "scripts" / "run-quality.sh"))


def _append_event_script(event: str) -> str:
    return (
        "#!/usr/bin/env python3\n"
        "import os\n"
        "from pathlib import Path\n"
        "with Path(os.environ['ORDER_LOG']).open('a', encoding='utf-8') as stream:\n"
        f"    stream.write({event!r} + '\\n')\n"
    )


def _release_fixture(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> tuple[Path, dict[str, str], Path]:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    shutil.copy2(_runner_path(), repo / "scripts" / "run-quality.sh")

    event_log = tmp_path / "release-order.log"
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
        repo / "scripts" / "prepush_focused_changed_line_coverage.py",
        _append_event_script("mutation"),
    )

    tmp_root = tmp_path / "tmp"
    tmp_root.mkdir()
    env.update(
        {
            "ORDER_LOG": str(event_log),
            "CHARNESS_RUNTIME_ROOT": str(tmp_path / "runtime"),
            "PYTHONPYCACHEPREFIX": str(tmp_path / "pycache"),
            "PYTEST_ADDOPTS": f"-o cache_dir={tmp_path / 'pytest-cache'}",
            "TMPDIR": str(tmp_root),
        }
    )
    return repo, env, event_log


def test_normal_release_runs_pytest_before_later_checks_and_mutation(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert event_log.read_text(encoding="utf-8").splitlines() == [
        "pytest-release",
        "validate-skills",
        "check-runtime-budget",
        "mutation",
    ]
    assert f"PASS {_RELEASE_LABEL}" in result.stdout
    assert f"PASS {_MUTATION_LABEL}" in result.stdout


def test_release_pytest_failure_stops_before_later_checks_and_mutation(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env, event_log = _release_fixture(tmp_path, seeded_quality_runner_repo)
    env["QUALITY_FAIL_LABEL"] = _RELEASE_LABEL

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env)

    assert result.returncode == 1, result.stderr
    assert event_log.read_text(encoding="utf-8").splitlines() == [_RELEASE_LABEL]
    assert "release pytest failed; stopping before later release checks." in result.stderr
    assert f"PASS {_MUTATION_LABEL}" not in result.stdout


def test_release_mutation_is_last_queued_gate_and_flushes_immediately() -> None:
    source_lines = []
    for number, raw_line in enumerate(_runner_path().read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if line and not line.startswith("#"):
            source_lines.append((number, line))

    start = next(
        index
        for index, (_, line) in enumerate(source_lines)
        if line == 'if agent_browser_runtime_gate_enabled "agent-browser-runtime-baseline"; then'
    )
    end = next(
        index
        for index, (_, line) in enumerate(source_lines[start:], start)
        if line == 'if [[ -n "$RUN_QUALITY_LABELS" && "$RUN_QUALITY_SELECTED_LABEL_MATCHES" -eq 0 ]]; then'
    )
    release_lines = source_lines[start:end]

    queue_calls = [
        (number, line)
        for number, line in release_lines
        if re.match(r"^(queue_selected|queue_timed|queue_agent_browser_runtime_gate)\s+", line)
    ]
    mutation_number, _mutation_line = next(
        (number, line)
        for number, line in queue_calls
        if f'"{_MUTATION_LABEL}"' in line
    )

    assert mutation_number == max(number for number, _ in queue_calls)
    mutation_index = next(index for index, (number, _) in enumerate(release_lines) if number == mutation_number)
    assert release_lines[mutation_index + 1][1] == "flush_phase || OVERALL_RC=$?"

    preceding_flushes = [
        number
        for number, line in release_lines
        if number < mutation_number and line.startswith("flush_phase")
    ]
    assert preceding_flushes
    assert max(preceding_flushes) < mutation_number

    mutation_guard = [line for _, line in release_lines[mutation_index - 5 : mutation_index]]
    assert 'if [[ "$OVERALL_RC" != "0" ]]; then' in mutation_guard
    assert 'exit "$OVERALL_RC"' in mutation_guard
