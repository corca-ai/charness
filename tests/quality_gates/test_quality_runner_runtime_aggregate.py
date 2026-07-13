from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .support import clone_quality_runner_repo, run_shell_script, write_executable


def _capture_run_quality_runtime_records(repo: Path) -> Path:
    log_path = repo / "quality-runtime-records.jsonl"
    real_python = subprocess.run(
        ["python3", "-c", "import sys; print(sys.executable)"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    write_executable(
        repo / "scripts" / "record_quality_runtime.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import os",
                "import sys",
                "from pathlib import Path",
                "",
                "args = sys.argv[1:]",
                "record = {",
                "    'label': args[args.index('--label') + 1],",
                "    'elapsed_ms': int(args[args.index('--elapsed-ms') + 1]),",
                "    'status': args[args.index('--status') + 1],",
                "    'timestamp': args[args.index('--timestamp') + 1],",
                "}",
                "if (",
                "    os.environ.get('QUALITY_RUNTIME_FAIL_AGGREGATE') == '1'",
                "    and record['label'].startswith('run-quality-')",
                "):",
                "    raise SystemExit(73)",
                f"with Path({str(log_path)!r}).open('a', encoding='utf-8') as handle:",
                "    handle.write(json.dumps(record, sort_keys=True) + '\\n')",
                "",
            ]
        ),
    )
    write_executable(
        repo / "bin" / "python3",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                "# Call spy keeps this aggregate test fast; direct-recorder tests cover real behavior elsewhere.",
                'if [[ "${1:-}" == "scripts/record_quality_runtime.py" ]]; then',
                "  shift",
                '  label="" elapsed_ms="" status="" timestamp=""',
                "  while [[ \"$#\" -gt 0 ]]; do",
                "    case \"$1\" in",
                "      --label|--elapsed-ms|--status|--timestamp)",
                '        [[ "$#" -ge 2 ]] || exit 2',
                '        case "$1" in',
                '          --label) label="$2" ;;',
                '          --elapsed-ms) elapsed_ms="$2" ;;',
                '          --status) status="$2" ;;',
                '          --timestamp) timestamp="$2" ;;',
                "        esac",
                "        shift 2",
                "        ;;",
                "      *) shift ;;",
                "    esac",
                "  done",
                '  [[ -n "$label" && -n "$elapsed_ms" && -n "$status" && -n "$timestamp" ]] || exit 2',
                '  [[ "$elapsed_ms" =~ ^-?[0-9]+$ ]] || exit 2',
                '  if [[ "${QUALITY_RUNTIME_FAIL_AGGREGATE:-}" == "1" && "$label" == run-quality-* ]]; then',
                "    exit 73",
                "  fi",
                '  printf \'{"elapsed_ms":%s,"label":"%s","status":"%s","timestamp":"%s"}\\n\' "$elapsed_ms" "$label" "$status" "$timestamp" >> ' + repr(str(log_path)),
                "  exit 0",
                "fi",
                'if [[ "${1:-}" == "-m" && "${2:-}" == "pytest" ]]; then',
                "  shift 2",
                '  if [[ "${1:-}" == "--version" ]]; then echo "pytest 9.0.2"; exit 0; fi',
                '  if [[ "${1:-}" == "--help" ]]; then echo "  -n numprocesses, --numprocesses=numprocesses"; exit 0; fi',
                '  if [[ "${QUALITY_FAIL_LABEL:-}" == "pytest" ]]; then',
                '    echo "quality failure output from pytest"',
                "    exit 1",
                "  fi",
                '  echo "quality success output from pytest"',
                "  exit 0",
                "fi",
                f"exec {real_python!r} \"$@\"",
                "",
            ]
        ),
    )
    return log_path


def _read_runtime_records(log_path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]


def test_run_quality_records_full_aggregate_runtime_status(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    log_path = _capture_run_quality_runtime_records(repo)
    env["QUALITY_FAIL_LABEL"] = "check-markdown"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--full", cwd=repo, env=env)

    assert result.returncode == 1
    records = _read_runtime_records(log_path)
    aggregate = [record for record in records if record["label"] == "run-quality-full"]
    assert len(aggregate) == 1
    assert aggregate[0]["status"] == "fail"
    assert isinstance(aggregate[0]["elapsed_ms"], int)


def test_run_quality_records_read_only_aggregate_runtime(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    log_path = _capture_run_quality_runtime_records(repo)

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--read-only", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    records = _read_runtime_records(log_path)
    aggregate = [record for record in records if record["label"] == "run-quality-read-only"]
    assert len(aggregate) == 1
    assert aggregate[0]["status"] == "pass"


def test_run_quality_records_release_aggregate_runtime_suffix(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    log_path = _capture_run_quality_runtime_records(repo)

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--release", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    labels = [record["label"] for record in _read_runtime_records(log_path)]
    assert labels.count("run-quality-full-release") == 1
    assert "run-quality-full" not in labels


def test_run_quality_does_not_record_filtered_aggregate_runtime(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    log_path = _capture_run_quality_runtime_records(repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    labels = [record["label"] for record in _read_runtime_records(log_path)]
    assert "validate-skills" in labels
    assert not any(str(label).startswith("run-quality-") for label in labels)


def test_run_quality_preserves_success_when_aggregate_runtime_recording_fails(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _capture_run_quality_runtime_records(repo)
    env["QUALITY_RUNTIME_FAIL_AGGREGATE"] = "1"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--read-only", cwd=repo, env=env)

    assert result.returncode == 0
    assert "Quality summary:" in result.stdout
    assert "warning: failed to record aggregate runtime for run-quality-read-only" in result.stderr


def test_run_quality_preserves_gate_failure_when_aggregate_runtime_recording_fails(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _capture_run_quality_runtime_records(repo)
    env["QUALITY_RUNTIME_FAIL_AGGREGATE"] = "1"
    env["QUALITY_FAIL_LABEL"] = "check-markdown"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--full", cwd=repo, env=env)

    assert result.returncode == 1
    assert "Quality summary:" in result.stdout
    assert "warning: failed to record aggregate runtime for run-quality-full" in result.stderr
