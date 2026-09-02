from __future__ import annotations

import json
import sys
from pathlib import Path

import quality_label_universe

from .support import (
    assert_quality_receipt,
    clone_quality_runner_repo,
    run_shell_script,
    write_executable,
)


def _batch_regime(repo: Path) -> str | None:
    """The regime `run-quality.sh` handed the recorder on ARGV, for per-gate samples."""
    return json.loads((repo / "quality-runtime-regime.json").read_text(encoding="utf-8"))


def _aggregate_regimes(repo: Path) -> dict[str, str]:
    """The ambient regime each single-label recorder call saw, keyed by label.

    Separate from `_batch_regime` because the aggregate is regimed through the
    exported variable rather than a flag; asserting only the argv half would leave
    the aggregate's partition unproven.
    """
    path = repo / "quality-runtime-aggregate-regime.jsonl"
    if not path.is_file():
        return {}
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return {str(record["label"]): str(record["regime"]) for record in records}


def _capture_run_quality_runtime_records(repo: Path) -> Path:
    log_path = repo / "quality-runtime-records.jsonl"
    regime_path = repo / "quality-runtime-regime.json"
    aggregate_regime_path = repo / "quality-runtime-aggregate-regime.jsonl"
    state_root_path = repo / "quality-runtime-state-roots.jsonl"
    real_python = sys.executable
    write_executable(
        repo / "scripts" / "record_quality_runtime.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                # NOT the stub the runner hits. `run-quality.sh` invokes
                # `python3 scripts/record_quality_runtime.py` by RELATIVE path, which
                # the `bin/python3` spy below intercepts; this file is reached only by
                # an absolute-path invocation that falls through to the real
                # interpreter. Regime capture therefore lives in the spy, not here.
                # Assert on `_batch_regime` only for runs that go through the runner.
                "import json",
                "import os",
                "import sys",
                "from pathlib import Path",
                "",
                "args = sys.argv[1:]",
                "if '--batch' in args:",
                f"    with Path({str(log_path)!r}).open('a', encoding='utf-8') as handle:",
                "        handle.write(Path(args[args.index('--batch') + 1]).read_text(encoding='utf-8'))",
                "    raise SystemExit(0)",
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
                '  label="" elapsed_ms="" status="" timestamp="" batch="" regime="" state_root="" saw_regime=0',
                '  while [[ "$#" -gt 0 ]]; do',
                '    case "$1" in',
                "      --batch)",
                '        [[ "$#" -ge 2 ]] || exit 2',
                '        batch="$2"',
                "        shift 2",
                "        ;;",
                # The regime decides WHICH PROFILE these samples land in, so an
                # unrecorded one is the #544 defect passing unnoticed. Captured
                # separately from the per-label JSONL because it is per batch.
                "      --runtime-regime)",
                '        [[ "$#" -ge 2 ]] || exit 2',
                '        regime="$2"',
                "        saw_regime=1",
                "        shift 2",
                "        ;;",
                "      --state-root)",
                '        [[ "$#" -ge 2 ]] || exit 2',
                '        state_root="$2"',
                "        shift 2",
                "        ;;",
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
                '  if [[ -n "$batch" ]]; then',
                # The runner batches per-gate samples into one recorder call; the spy
                # replays them line for line so per-label assertions keep working.
                '    [[ -r "$batch" ]] || exit 2',
                '    cat "$batch" >> ' + repr(str(log_path)),
                "    printf '%s\\n' \"$state_root\" >> " + repr(str(state_root_path)),
                '    if [[ "$saw_regime" == "1" ]]; then',
                '      printf \'"%s"\' "$regime" > ' + repr(str(regime_path)),
                "    else",
                "      printf 'null' > " + repr(str(regime_path)),
                "    fi",
                "    exit 0",
                "  fi",
                '  [[ -n "$label" && -n "$elapsed_ms" && -n "$status" && -n "$timestamp" ]] || exit 2',
                # The AGGREGATE label takes its regime from the EXPORTED variable, not
                # from argv, so capture the environment here. Without this the
                # aggregate half of the partition has no assertion at all, and an
                # unregimed `run-quality-full` sample from a widened run would land
                # against the real bar while its per-gate siblings went elsewhere.
                '  printf \'{"label":"%s","regime":"%s"}\\n\' "$label" "${CHARNESS_RUNTIME_REGIME-<unset>}" >> '
                + repr(str(aggregate_regime_path)),
                "  printf '%s\\n' \"$state_root\" >> " + repr(str(state_root_path)),
                '  [[ "$elapsed_ms" =~ ^-?[0-9]+$ ]] || exit 2',
                '  if [[ "${QUALITY_RUNTIME_FAIL_AGGREGATE:-}" == "1" && "$label" == run-quality-* ]]; then',
                "    exit 73",
                "  fi",
                '  printf \'{"elapsed_ms":%s,"label":"%s","status":"%s","timestamp":"%s"}\\n\' "$elapsed_ms" "$label" "$status" "$timestamp" >> '
                + repr(str(log_path)),
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
                f'exec {real_python!r} "$@"',
                "",
            ]
        ),
    )
    return log_path


def _read_runtime_records(log_path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]


def _install_inventory_declaration_phase_probe(repo: Path) -> Path:
    """Make the two labels observable so phase isolation is tested behaviorally."""
    events = repo / "phase-events.jsonl"
    event_literal = repr(str(events))
    write_executable(
        repo / "scripts" / "validate_skills.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import time",
                "from pathlib import Path",
                f"events = Path({event_literal})",
                "with events.open('a', encoding='utf-8') as handle:",
                "    handle.write('first-start\\n')",
                "time.sleep(0.15)",
                "with events.open('a', encoding='utf-8') as handle:",
                "    handle.write('first-end\\n')",
                "",
            ]
        ),
    )
    write_executable(
        repo / "scripts" / "validate_inventory_consumption_declaration.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import os",
                "import sys",
                "from pathlib import Path",
                f"events = Path({event_literal})",
                "with events.open('a', encoding='utf-8') as handle:",
                "    handle.write('declaration-start\\n')",
                "seen = events.read_text(encoding='utf-8').splitlines()",
                "if 'first-end' not in seen:",
                "    print('declaration gate started before the first phase drained')",
                "    raise SystemExit(41)",
                "if os.environ.get('QUALITY_FAIL_LABEL') == 'validate-inventory-consumption-declaration':",
                "    print('quality failure output from validate-inventory-consumption-declaration')",
                "    raise SystemExit(1)",
                "with events.open('a', encoding='utf-8') as handle:",
                "    handle.write('declaration-end\\n')",
                "",
            ]
        ),
    )
    write_executable(
        repo / "skills" / "public" / "quality" / "scripts" / "check_dup_ratchet.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                f"events = Path({event_literal})",
                "seen = events.read_text(encoding='utf-8').splitlines()",
                "if 'declaration-end' not in seen:",
                "    print('next phase started before the isolated declaration gate drained')",
                "    raise SystemExit(42)",
                "with events.open('a', encoding='utf-8') as handle:",
                "    handle.write('next-start\\n')",
                "",
            ]
        ),
    )
    return events


def test_inventory_declaration_gate_runs_after_first_phase_drains(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    events = _install_inventory_declaration_phase_probe(repo)
    runtime_log = _capture_run_quality_runtime_records(repo)
    env["CHARNESS_QUALITY_LABELS"] = (
        "validate-skills,validate-inventory-consumption-declaration,dup-ratchet"
    )

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--read-only", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert events.read_text(encoding="utf-8").splitlines() == [
        "first-start",
        "first-end",
        "declaration-start",
        "declaration-end",
        "next-start",
    ]
    assert [record["label"] for record in _read_runtime_records(runtime_log)] == [
        "validate-skills",
        "validate-inventory-consumption-declaration",
        "dup-ratchet",
    ]
    rows = quality_label_universe.quality_gate_rows(repo) or []
    phases = quality_label_universe._quality_gate_declaration(repo)["phases"]
    declaration_phase = next(
        index
        for index, phase in enumerate(phases)
        if any(
            row["label"] == "validate-inventory-consumption-declaration" for row in phase["gates"]
        )
    )
    post_tree_phase = next(
        index
        for index, phase in enumerate(phases)
        if any(row["label"] == "dup-ratchet" for row in phase["gates"])
    )
    assert rows
    assert phases[declaration_phase]["isolation"] == "alone"
    assert declaration_phase < post_tree_phase


def test_inventory_declaration_failure_remains_a_quality_failure(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _install_inventory_declaration_phase_probe(repo)
    receipt_path = repo / "receipt.json"
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills,validate-inventory-consumption-declaration"
    env["QUALITY_FAIL_LABEL"] = "validate-inventory-consumption-declaration"
    env["CHARNESS_QUALITY_RECEIPT_JSON"] = str(receipt_path)

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--read-only", cwd=repo, env=env)

    assert result.returncode == 1
    assert "FAIL validate-inventory-consumption-declaration" in result.stdout
    assert_quality_receipt(
        repo,
        result,
        status="fail",
        passed=1,
        failed=1,
        adverse_subjects=["validate-inventory-consumption-declaration"],
    )


def test_run_quality_records_full_aggregate_runtime_status(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    log_path = _capture_run_quality_runtime_records(repo)
    env["QUALITY_FAIL_LABEL"] = "check-docs"

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
    assert result.stdout.splitlines()[-1].startswith("Quality summary:"), result.stdout
    assert "warning: failed to record aggregate runtime for run-quality-read-only" in result.stderr


def test_run_quality_preserves_gate_failure_when_aggregate_runtime_recording_fails(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _capture_run_quality_runtime_records(repo)
    env["QUALITY_RUNTIME_FAIL_AGGREGATE"] = "1"
    env["QUALITY_FAIL_LABEL"] = "check-docs"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", "--full", cwd=repo, env=env)

    assert result.returncode == 1
    assert "Quality summary:" in result.stdout
    assert result.stdout.splitlines()[-1].startswith("Quality summary:"), result.stdout
    assert "warning: failed to record aggregate runtime for run-quality-full" in result.stderr


def test_a_label_filtered_run_scopes_its_samples_out_of_the_enforced_window(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    """#544. A filtered run measures the same gate against different competition.

    The aggregate label has refused to record under a filter since it was added,
    for exactly this reason. The per-gate samples had no such protection: they
    were written into the same profile the full-queue budgets are enforced
    against, so a subset run moved the enforcement median without any change to
    the code the gate checks. They are re-keyed rather than dropped, so the
    subset regime stays measurable in its own right.
    """
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    log_path = _capture_run_quality_runtime_records(repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    # Still recorded -- the evidence is preserved, only its profile changes.
    assert "validate-skills" in [record["label"] for record in _read_runtime_records(log_path)]
    assert _batch_regime(repo) == "filtered"


def test_a_named_regime_beats_the_generic_filtered_bucket(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    # A RECURRING subset (the docs-only pre-push branch) is a real regime whose
    # samples are comparable to each other; an ad hoc filter is not. Pooling the
    # two would rebuild the mixture one level down.
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _capture_run_quality_runtime_records(repo)
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills"
    env["CHARNESS_RUNTIME_REGIME"] = "docs-only"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert _batch_regime(repo) == "docs-only"


def test_an_unfiltered_run_records_into_the_enforced_profile_even_if_a_regime_is_exported(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    """The full queue IS the regime every committed budget was sized for.

    Letting an ambient env var re-key an unfiltered run would send its samples to
    a profile that declares no budgets, and every bar in the adapter would then be
    enforced against a window that never fills -- a gate with no teeth and no
    failure to announce it. The structural fact (was this run filtered) wins over
    the caller's label.
    """
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _capture_run_quality_runtime_records(repo)
    env["CHARNESS_RUNTIME_REGIME"] = "docs-only"
    env.pop("CHARNESS_QUALITY_LABELS", None)

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert _batch_regime(repo) == ""


def test_the_regime_reaches_gates_that_record_their_own_samples(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    """`measure_startup_probes.py --record-runtime-signals` calls the recorder itself.

    It never sees `run-quality.sh`'s locals, so without the export its samples
    would land unregimed while every sibling in the same filtered run was scoped
    -- the same contamination, one call site over. This constructs a gate that
    reads the ambient value and shows it arriving, rather than trusting that an
    `export` line implies a reader.

    The regime here is DERIVED, not inherited: the caller passes no
    `CHARNESS_RUNTIME_REGIME`. An earlier version of this test set the variable
    itself, so the child inherited it from the caller and the assertion held with
    the `export` deleted -- it proved nothing about the line it was written for.
    """
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _capture_run_quality_runtime_records(repo)
    observed = repo / "gate-seen-regime.txt"
    write_executable(
        repo / "scripts" / "validate_skills.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import os",
                "from pathlib import Path",
                f"Path({str(observed)!r}).write_text(",
                "    os.environ.get('CHARNESS_RUNTIME_REGIME', '<unset>'), encoding='utf-8'",
                ")",
                "",
            ]
        ),
    )
    env["CHARNESS_QUALITY_LABELS"] = "validate-skills"
    env.pop("CHARNESS_RUNTIME_REGIME", None)

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert observed.read_text(encoding="utf-8") == "filtered"


def test_explicit_runtime_root_is_threaded_to_all_quality_state_consumers(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _capture_run_quality_runtime_records(repo)
    execution_root = tmp_path / "task-result" / "runtime"
    quality_root = execution_root / "quality"
    startup_args = repo / "startup-probe-args.txt"
    budget_args = repo / "runtime-budget-args.txt"
    write_executable(
        repo / "skills" / "public" / "quality" / "scripts" / "measure_startup_probes.py",
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"from pathlib import Path\nPath({str(startup_args)!r}).write_text(' '.join(sys.argv[1:]), encoding='utf-8')\n",
    )
    write_executable(
        repo / "skills" / "public" / "quality" / "scripts" / "check_runtime_budget.py",
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"from pathlib import Path\nPath({str(budget_args)!r}).write_text(' '.join(sys.argv[1:]), encoding='utf-8')\n",
    )
    env["CHARNESS_RUNTIME_ROOT"] = str(execution_root)

    result = run_shell_script(
        repo / "scripts" / "run-quality.sh", "--full", "--read-only", cwd=repo, env=env
    )

    assert result.returncode == 0, result.stderr
    assert startup_args.read_text(encoding="utf-8").split()[-2:] == [
        "--state-root",
        str(quality_root),
    ]
    budget_argv = budget_args.read_text(encoding="utf-8").split()
    assert budget_argv[budget_argv.index("--state-root") + 1] == str(quality_root)
    state_roots = {
        line
        for line in (repo / "quality-runtime-state-roots.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line
    }
    assert state_roots == {str(quality_root)}
    assert not (repo / ".charness" / "quality" / "runtime-signals.json").exists()


def test_an_opt_in_extra_gate_also_leaves_the_enforced_window(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    """A gate set can widen as well as narrow, and both change the competition.

    `CHARNESS_QUALITY_DEAD_CODE=1` queues two full vulture passes into the same
    concurrent phase with NO label filter, so every sibling's sample was taken
    under heavier load and landed in the enforced window anyway. Handling only
    the narrowing case would leave the class open in the one direction that
    still reaches the bars.

    The aggregate is asserted alongside the per-gate batch because it is regimed
    through a different mechanism (the exported variable, not a flag). This is
    the arm where the two could silently disagree.
    """
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _capture_run_quality_runtime_records(repo)
    env.pop("CHARNESS_QUALITY_LABELS", None)
    env.pop("CHARNESS_RUNTIME_REGIME", None)
    env["CHARNESS_QUALITY_DEAD_CODE"] = "1"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert _batch_regime(repo) == "plus-dead-code"
    aggregate = _aggregate_regimes(repo)
    assert aggregate.get("run-quality-full") == "plus-dead-code", aggregate


def test_every_main_phase_opt_in_widens_the_regime_not_just_the_first_one(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    """`CHARNESS_SUPPLY_CHAIN_ONLINE` has the same shape as the dead-code opt-in.

    Naming only the opt-in that happened to be found first is how the second one
    keeps contaminating the enforced window, so the tokens are enumerated and
    composed. Both together must produce one regime that names both, not the
    first one that matched.
    """
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    _capture_run_quality_runtime_records(repo)
    env.pop("CHARNESS_QUALITY_LABELS", None)
    env.pop("CHARNESS_RUNTIME_REGIME", None)
    env["CHARNESS_SUPPLY_CHAIN_ONLINE"] = "1"

    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert _batch_regime(repo) == "plus-supply-chain"

    repo2, env2 = clone_quality_runner_repo(tmp_path / "both", seeded_quality_runner_repo)
    _capture_run_quality_runtime_records(repo2)
    env2.pop("CHARNESS_QUALITY_LABELS", None)
    env2.pop("CHARNESS_RUNTIME_REGIME", None)
    env2["CHARNESS_SUPPLY_CHAIN_ONLINE"] = "1"
    env2["CHARNESS_QUALITY_DEAD_CODE"] = "1"

    result2 = run_shell_script(repo2 / "scripts" / "run-quality.sh", cwd=repo2, env=env2)
    assert result2.returncode == 0, result2.stderr
    assert _batch_regime(repo2) == "plus-dead-code-supply-chain"
