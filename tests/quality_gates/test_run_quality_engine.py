from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT, make_quality_runner_repo, write_executable

ENGINE = load_script_module(
    "tests.quality_gates.support_run_quality_engine",
    ROOT / "scripts" / "run_quality_engine.py",
)
FIXTURE = ROOT / "tests" / "quality_gates" / "fixtures" / "quality-gates-engine.yaml"


def _runtime_recorder_stub() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "import json",
            "import sys",
            "from pathlib import Path",
            "args = sys.argv[1:]",
            "root = Path(args[args.index('--repo-root') + 1])",
            "path = root / '.charness' / 'quality' / 'runtime-signals.json'",
            "payload = json.loads(path.read_text()) if path.exists() else {'commands': {}}",
            "commands = payload.setdefault('commands', {})",
            "if '--batch' in args:",
            "    rows = [json.loads(line) for line in Path(args[args.index('--batch') + 1]).read_text().splitlines() if line]",
            "else:",
            "    rows = [{'label': args[args.index('--label') + 1], 'elapsed_ms': int(args[args.index('--elapsed-ms') + 1]), 'status': args[args.index('--status') + 1], 'timestamp': args[args.index('--timestamp') + 1]}]",
            "for row in rows: commands[row['label']] = {'latest': row}",
            "path.parent.mkdir(parents=True, exist_ok=True)",
            "path.write_text(json.dumps(payload, indent=2) + '\\n')",
            "",
        ]
    )


def _seed(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    repo, env = make_quality_runner_repo(tmp_path)
    (repo / "quality-gates.yaml").write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    fixture_stub = repo / "tests" / "quality_gates" / "fixtures" / "engine_gate.py"
    fixture_stub.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "tests" / "quality_gates" / "fixtures" / "engine_gate.py", fixture_stub)
    write_executable(repo / "scripts" / "record_quality_runtime.py", _runtime_recorder_stub())
    write_executable(
        repo / "bin" / "python3",
        f'#!/usr/bin/env bash\nexec {sys.executable!r} "$@"\n',
    )
    env["CHARNESS_QUALITY_RECEIPT_JSON"] = str(repo / "receipt.json")
    env["CHARNESS_QUALITY_HEARTBEAT_SECONDS"] = "0"
    return repo, env


def _run(repo: Path, env: dict[str, str], *args: str, **extra: str):
    run_env = {**env, **extra}
    return run_loaded_script_main(
        "run_quality_engine.py",
        ENGINE,
        "--repo-root",
        str(repo),
        "--gates",
        str(repo / "quality-gates.yaml"),
        *args,
        env=run_env,
    )


def _labels(stdout: str) -> list[str]:
    return [
        line.split()[1]
        for line in stdout.splitlines()
        if line.startswith(("PASS ", "FAIL ", "UNPROVEN "))
    ]


def test_default_selects_core_and_writes_receipt_and_runtime(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    result = _run(repo, env)

    assert result.returncode == 0, result.stderr
    assert _labels(result.stdout) == ["core"]
    assert "Quality summary: 1 passed, 0 failed" in result.stdout
    receipt = json.loads((repo / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["measured_scope"] == ["core"]
    signals = json.loads((repo / ".charness" / "quality" / "runtime-signals.json").read_text())
    assert set(signals["commands"]) == {"core", "run-quality-full"}
    assert signals["commands"]["core"]["latest"]["status"] == "pass"
    assert "run-quality: START mode=full release=0 requested_scope=core" in result.stderr


def test_full_selects_standard_but_not_release_or_label_only(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    result = _run(repo, env, "--full")

    assert result.returncode == 0, result.stderr
    labels = _labels(result.stdout)
    assert "core" in labels and "standard" in labels and "pytest" in labels
    assert "pytest-release" not in labels
    assert "label-only" not in labels and "opt-in" not in labels
    assert "checker-fallback" in labels and "checker" not in labels


def test_release_prefers_release_variant_and_runs_release_only(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    result = _run(repo, env, "--release")

    assert result.returncode == 0, result.stderr
    labels = _labels(result.stdout)
    assert "pytest-release" in labels and "pytest" not in labels
    assert "standard" in labels
    assert "release-changed-line-coverage" in labels


def test_release_non_claim_suppresses_changed_line_gate(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    result = _run(repo, env, "--release", "--non-claim=release-changed-line-coverage")

    assert result.returncode == 0, result.stderr
    assert "release-changed-line-coverage" not in _labels(result.stdout)
    assert "NON-CLAIM: release-changed-line-coverage was not run" in result.stderr


def test_explicit_and_env_opt_in_selection(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    explicit = _run(repo, env, "--labels", "label-only")
    assert explicit.returncode == 0, explicit.stderr
    assert _labels(explicit.stdout) == ["label-only"]

    opted_in = _run(repo, env, "--full", QUALITY_OPT_IN="1")
    assert "PASS opt-in" in opted_in.stdout
    not_opted_in = _run(repo, env, "--full")
    assert "PASS opt-in" not in not_opted_in.stdout

    explicit_without_condition = _run(repo, env, "--labels", "opt-in")
    assert explicit_without_condition.returncode == 0
    assert _labels(explicit_without_condition.stdout) == ["opt-in"]


def test_concurrent_completion_and_heartbeat_are_observable(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    started = time.monotonic()
    result = _run(repo, env, "--labels", "slow,fast", CHARNESS_QUALITY_HEARTBEAT_SECONDS="1")

    assert result.returncode == 0, result.stderr
    assert time.monotonic() - started >= 1
    assert "run-quality: BATCH_START checks=2" in result.stderr
    assert "run-quality: HEARTBEAT remaining=1" in result.stderr
    assert result.stdout.index("PASS fast") < result.stdout.index("PASS slow")


def test_attention_output_is_replayed_for_a_passing_gate(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    result = _run(repo, env, "--labels", "warning,core")

    assert result.returncode == 0, result.stderr
    assert "--- warning output ---" in result.stdout
    assert "advisory: WARN: inspect this passing gate" in result.stdout
    assert "--- core output ---" not in result.stdout


def test_fail_fast_stops_later_phases_with_phase_message(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    result = _run(repo, env, "--full", QUALITY_FAIL_LABEL="core")

    assert result.returncode == 1
    assert "FAIL core" in result.stdout
    assert "PASS standard" not in result.stdout
    assert "standing prerequisite failed; stopping before later quality checks." in result.stderr


def test_unproven_exit_codes_are_label_scoped(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    result = _run(repo, env, "--labels", "unproven,partial,ordinary-exit-three")

    assert result.returncode == 3
    assert "UNPROVEN unproven" in result.stdout
    assert "UNPROVEN partial" in result.stdout
    assert "FAIL ordinary-exit-three" in result.stdout
    receipt = json.loads((repo / "receipt.json").read_text(encoding="utf-8"))
    assert set(receipt["unproven_subjects"]) == {"unproven", "partial"}
    assert [item["subject"] for item in receipt["adverse_subjects"]] == ["ordinary-exit-three"]


def test_native_preflight_runs_before_an_explicit_native_gate(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    write_executable(
        repo / "scripts" / "native_gate_lib.py",
        "from pathlib import Path\nPath('native-preflight-ran').write_text('yes')\n",
    )

    result = _run(repo, env, "--labels", "native")

    assert result.returncode == 0, result.stderr
    assert "PASS native" in result.stdout
    assert (repo / "native-preflight-ran").read_text(encoding="utf-8") == "yes"


def test_plugin_preamble_runs_for_writable_full_mode_and_skips_read_only(
    tmp_path: Path,
) -> None:
    repo, env = _seed(tmp_path)
    (repo / "packaging").mkdir(exist_ok=True)
    (repo / "packaging" / "charness.json").write_text(
        json.dumps(
            {"codex": {"repo_marketplace": {"materialized_source_path": "./plugins/charness"}}}
        ),
        encoding="utf-8",
    )
    (repo / ".gitignore").write_text("/plugins/\n", encoding="utf-8")
    write_executable(
        repo / "scripts" / "sync_root_plugin_manifests.py",
        "from pathlib import Path\nPath('preamble-ran').write_text('yes')\n",
    )

    writable = _run(repo, env, "--full")
    assert writable.returncode == 0, writable.stderr
    assert (repo / "preamble-ran").read_text(encoding="utf-8") == "yes"

    (repo / "preamble-ran").unlink()
    read_only = _run(repo, env, "--read-only")
    assert read_only.returncode == 0, read_only.stderr
    assert not (repo / "preamble-ran").exists()


@pytest.mark.parametrize(
    ("args", "extra_env", "message"),
    [
        (("--release", "--labels", "core"), {}, "--release is one indivisible lane"),
        (("--non-claim=release-changed-line-coverage",), {}, "requires --release"),
        (
            (),
            {"CHARNESS_QUALITY_HEARTBEAT_SECONDS": "nope"},
            "CHARNESS_QUALITY_HEARTBEAT_SECONDS must be",
        ),
    ],
)
def test_cli_refusals_return_exit_two(
    tmp_path: Path,
    args: tuple[str, ...],
    extra_env: dict[str, str],
    message: str,
) -> None:
    repo, env = _seed(tmp_path)
    result = _run(repo, env, *args, **extra_env)

    assert result.returncode == 2
    assert message in result.stderr


@pytest.mark.boundary_contract(reason="prove the engine's documented CLI refusal exit code")
def test_cli_unknown_argument_returns_exit_two(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_quality_engine.py"),
            "--repo-root",
            str(repo),
            "--gates",
            str(repo / "quality-gates.yaml"),
            "--unknown",
        ],
        cwd=repo,
        env={**env, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
