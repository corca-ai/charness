"""Closeout producer for the changed-line mutation-coverage release gate.

Lever A+B (decided 2026-06-07): instead of a dedicated slow `dynamic_context`
probe, closeout can either instrument the broad pytest run itself or instrument
an explicit focused pytest command while broad pytest stays on the normal
proof/cache path. The producer exports small coverage JSON and stamps a freshness
fingerprint. The release consumer
(`check_changed_line_mutation_coverage.py --require-fresh-coverage`) trusts that
coverage when its producer-qualified `.changed-line.fingerprint` marker matches
the current changed-pool content.

Spec: charness-artifacts/spec/mutation-changed-line-premerge-gate.md (Slice 2).
This wiring is charness-host-local (closeout-specific); the transferable doctrine
lives in skills/public/quality/references/mutation-testing.md.
"""
from __future__ import annotations

import shlex
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Callable

import yaml

from runtime_bootstrap import import_repo_module

_sampling = import_repo_module(__file__, "scripts.mutation_sampling_lib")
_changed_files = import_repo_module(__file__, "scripts.mutation_changed_files_lib")
_consumer = import_repo_module(__file__, "scripts.check_changed_line_mutation_coverage")

#: Read from the consumer rather than transcribed: a local `2` here that drifted
#: from the consumer's own contract would silently re-collapse the two states.
CONSUMER_REFUSED_EXIT = _consumer.REFUSED_EXIT
#: Same discipline, for the same reason. Unreachable on today's producer path (it
#: never passes `--limit-to-file`, so `unanalyzed` is always empty), but named so
#: the mapping below is a DECISION rather than a fallthrough the day that changes.
CONSUMER_PARTIAL_EXIT = _consumer.PARTIAL_EXIT

DEFAULT_COVERAGE_JSON = Path("reports/mutation/test-coverage.json")
_COVERAGE_ENV_KEYS = ("COVERAGE_PROCESS_START", "COVERAGE_RCFILE", "PYTHONPATH")
#: Re-export, NOT a second definition (SC18). The instrumentation policy is owned
#: by `mutation_sampling_lib.classify_instrumentable_command` so this module and
#: the changed-line gate cannot drift back into opposite answers. Only names this
#: module's body or an external caller actually reads are bound here -- an unread
#: alias is a live trap (`run_standing_pytest.py`'s own re-export block records
#: why), and a first draft of this slice kept a helper-flag alias whose ONLY
#: reader was the test asserting it existed.
classify_instrumentable_command = _sampling.classify_instrumentable_command
is_standing_pytest_runner_command = _sampling.is_standing_pytest_runner_command
is_instrumentable_pytest_command = _sampling.is_instrumentable_pytest_command
PRODUCE_REQUIRES_LOCK_ERROR = (
    "--produce-mutation-coverage requires --verification-lock and is incompatible "
    "with --skip-broad-pytest (the locked closeout proof anchors the coverage marker)"
)
FOCUSED_REQUIRES_PRODUCE_ERROR = (
    "--mutation-coverage-command requires --produce-mutation-coverage"
)
FOCUSED_REQUIRES_PYTEST_ERROR = (
    "--mutation-coverage-command must start with 'pytest ', 'python3 -m pytest ', "
    "or the standing pytest runner"
)
EXTRA_TARGETS_REQUIRES_PRODUCE_ERROR = (
    "--mutation-coverage-extra-pytest-target requires --produce-mutation-coverage"
)
EXTRA_TARGETS_FOCUSED_CONFLICT_ERROR = (
    "--mutation-coverage-extra-pytest-target composes with the broad coverage producer; "
    "when using --mutation-coverage-command, put the target in that explicit command instead"
)


def instrument_broad_command(
    command: str,
    data_file: Path,
    *,
    extra_pytest_targets: list[str] | tuple[str, ...] = (),
) -> str:
    """Rewrite an instrumentable pytest command to run under plain `coverage run`,
    preserving the remaining arguments VERBATIM (the `tests/test_*.py` glob must
    stay unquoted so bash still expands it -- which is why this builder does
    string surgery on the raw remainder rather than re-joining argv).

    Accepts exactly what `mutation_sampling_lib.classify_instrumentable_command`
    accepts; only the rendering is local. See that function for why the split is
    at the classifier rather than at a boolean."""
    classified = classify_instrumentable_command(command)
    if classified is None:
        raise ValueError(f"not an instrumentable pytest command: {command!r}")
    kind, interpreter, remainder = classified
    data_file_arg = shlex.quote(str(data_file))
    # The caller's own interpreter spelling, falling back to the SAME default the
    # argv builder uses. Previously this hardcoded `python3` while the argv builder
    # recovered the caller's `/usr/bin/python3` and otherwise used `sys.executable`,
    # so the two builders measured the same accepted command under two different
    # interpreters -- measured by a round-2 reviewer, invisible to a test that
    # compares every token except the first.
    driver = shlex.quote(interpreter or sys.executable)
    prefix = f"{driver} -m coverage run --data-file {data_file_arg}"
    if kind == _sampling.PYTEST_KIND:
        extra_suffix = (" " + shlex.join(list(extra_pytest_targets))) if extra_pytest_targets else ""
        return f"{prefix} -m pytest" + remainder + extra_suffix
    extra_suffix = "".join(
        f" --extra-pytest-target {shlex.quote(target)}" for target in extra_pytest_targets
    )
    return f"{prefix} " + remainder + extra_suffix


def _with_coverage_env(env: dict[str, str], command: str) -> str:
    exports = "; ".join(f"export {key}={shlex.quote(env[key])}" for key in _COVERAGE_ENV_KEYS)
    return f"{exports}; {command}"


def consumer_command_for_produced_coverage(repo_root: Path, *, base_sha: str, coverage_json: Path) -> str:
    """Return the copyable post-commit consumer command for this producer run."""
    consumer_script = Path(__file__).resolve().with_name("check_changed_line_mutation_coverage.py")
    return (
        f"python3 {shlex.quote(str(consumer_script))} "
        f"--repo-root {shlex.quote(str(repo_root))} "
        f"--base-sha {shlex.quote(base_sha)} --head-sha HEAD "
        f"--coverage-json {shlex.quote(str(coverage_json))} "
        "--reuse-coverage --require-fresh-coverage"
    )


def produce_command_coverage(
    repo_root: Path,
    command: str,
    *,
    base_sha: str,
    coverage_json: Path,
    run_command: Callable[[Path, str, str], dict[str, object]],
    phase: str = "verify",
    extra_pytest_targets: list[str] | tuple[str, ...] = (),
    include_paths: Sequence[str] | None = None,
) -> dict[str, object]:
    """Run a pytest command under plain coverage and stamp the freshness marker."""
    data_file, rcfile, env = _sampling.prepare_plain_coverage(repo_root, coverage_json)
    instrumented = _with_coverage_env(
        env,
        instrument_broad_command(command, data_file, extra_pytest_targets=extra_pytest_targets),
    )
    result = dict(run_command(repo_root, instrumented, phase))
    result["command"] = command
    result["instrumented_command"] = instrumented
    if extra_pytest_targets:
        result["mutation_coverage_extra_pytest_targets"] = list(extra_pytest_targets)
    result["produced_mutation_coverage"] = False
    if result.get("returncode") == 0:
        combine_kwargs = {"show_contexts": False}
        if include_paths:
            combine_kwargs["include_paths"] = list(include_paths)
        _sampling.combine_and_export_coverage(
            repo_root, rcfile, data_file, coverage_json, env, **combine_kwargs
        )
        fingerprint = _changed_files.write_coverage_fingerprint_marker(
            repo_root, coverage_json, base_sha
        )
        result["produced_mutation_coverage"] = True
        result["mutation_coverage_base_sha"] = base_sha
        result["mutation_coverage_json"] = str(coverage_json)
        result["mutation_coverage_fingerprint"] = fingerprint
        result["mutation_coverage_consumer_command"] = consumer_command_for_produced_coverage(
            repo_root,
            base_sha=base_sha,
            coverage_json=coverage_json,
        )
    return result


def produce_broad_coverage(
    repo_root: Path,
    command: str,
    *,
    base_sha: str,
    coverage_json: Path,
    run_command: Callable[[Path, str, str], dict[str, object]],
    phase: str = "verify",
    extra_pytest_targets: list[str] | tuple[str, ...] = (),
) -> dict[str, object]:
    """Run the broad pytest command under plain coverage and, on success, export
    a small coverage JSON plus the freshness fingerprint marker the consumer
    trusts. Returns a ``run_command``-shaped result dict (the original command is
    preserved so the broad-pytest proof cache keys still match)."""
    return produce_command_coverage(
        repo_root,
        command,
        base_sha=base_sha,
        coverage_json=coverage_json,
        run_command=run_command,
        phase=phase,
        extra_pytest_targets=extra_pytest_targets,
    )


def default_mutation_base_sha(repo_root: Path) -> str:
    """The merge-base with origin/main — the same base the release consumer uses
    so the producer's freshness fingerprint matches the consumer's recomputation."""
    result = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "origin/main", "HEAD"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def make_closeout_producer(
    repo_root: Path,
    run_command: Callable[[Path, str, str], dict[str, object]],
    *,
    extra_pytest_targets: list[str] | tuple[str, ...] = (),
    base_sha: str | None = None,
    base_sha_resolver: Callable[[Path], str] = default_mutation_base_sha,
) -> Callable[[Path, str, str], dict[str, object]]:
    """A ``(repo_root, command, phase) -> result`` producer bound to the current
    base SHA and the default coverage-json path, for the closeout executor."""
    # An explicit closeout campaign base is resolved by the caller and bound
    # here.  Keep the historical origin/main resolver for the default/auto
    # path, and retain the callback shape consumed by the command executor.
    resolved_base_sha = base_sha if base_sha is not None else base_sha_resolver(repo_root)
    coverage_json = repo_root / DEFAULT_COVERAGE_JSON

    def producer(rr: Path, command: str, phase: str) -> dict[str, object]:
        return produce_broad_coverage(
            rr, command, base_sha=resolved_base_sha, coverage_json=coverage_json,
            run_command=run_command, phase=phase,
            extra_pytest_targets=extra_pytest_targets,
        )

    return producer


def closeout_producer_validation_error(args: object) -> str | None:
    focused_command = getattr(args, "mutation_coverage_command", None)
    extra_targets = list(getattr(args, "mutation_coverage_extra_pytest_target", []) or [])
    if extra_targets and not getattr(args, "produce_mutation_coverage", False):
        return EXTRA_TARGETS_REQUIRES_PRODUCE_ERROR
    if extra_targets and focused_command:
        return EXTRA_TARGETS_FOCUSED_CONFLICT_ERROR
    if focused_command and not getattr(args, "produce_mutation_coverage", False):
        return FOCUSED_REQUIRES_PRODUCE_ERROR
    if focused_command and not is_instrumentable_pytest_command(focused_command):
        return FOCUSED_REQUIRES_PYTEST_ERROR
    if not getattr(args, "produce_mutation_coverage", False):
        return None
    if not getattr(args, "verification_lock", False) or getattr(args, "skip_broad_pytest", False):
        return PRODUCE_REQUIRES_LOCK_ERROR
    return None


def run_focused_closeout_coverage(
    args: object,
    repo_root: Path,
    payload: dict[str, object],
    run_command: Callable[[Path, str, str], dict[str, object]],
    *,
    base_sha: str | None = None,
) -> bool:
    """Run an explicit narrow pytest coverage producer after closeout commands.

    The broad pytest proof remains owned by the normal closeout command plan and
    cache. This focused producer only refreshes the changed-line mutation coverage
    JSON/fingerprint when the operator supplied a command that covers the changed
    pool lines.
    """
    command = getattr(args, "mutation_coverage_command", None)
    if not getattr(args, "produce_mutation_coverage", False) or not command:
        return False
    result = produce_command_coverage(
        repo_root,
        command,
        base_sha=base_sha if base_sha is not None else default_mutation_base_sha(repo_root),
        coverage_json=repo_root / DEFAULT_COVERAGE_JSON,
        run_command=run_command,
        phase="verify",
    )
    payload["executed_commands"].append(result)
    if result["returncode"] != 0:
        payload["status"] = "failed"
        return True
    return False


def _consumer_report(result: dict[str, object]) -> dict[str, object] | None:
    """Read the consumer's structured verdict without inventing a second policy."""
    try:
        report = yaml.safe_load(str(result.get("stdout", "")))
    except (TypeError, ValueError, yaml.YAMLError):
        return None
    return report if isinstance(report, dict) else None


def _consumer_range(command: str) -> tuple[str, str] | None:
    """Read the base/head range from the generated authoritative command."""
    try:
        tokens = shlex.split(command)
        return (
            tokens[tokens.index("--base-sha") + 1],
            tokens[tokens.index("--head-sha") + 1],
        )
    except (ValueError, IndexError):
        return None


def _consumer_pass_validation_error(
    report: dict[str, object],
    *,
    command: str,
    producer_base_sha: str,
) -> str | None:
    """Validate the consumer's own minimal clean-verdict contract."""
    consumer_range = _consumer_range(command)
    if consumer_range is None or consumer_range[0] != producer_base_sha:
        return "consumer command range does not match producer metadata"
    if report.get("ok") is not True:
        return "consumer verdict did not report ok=true"
    if not isinstance(report.get("blocking"), list) or report["blocking"]:
        return "consumer verdict did not report an empty blocking list"
    if report.get("base_sha") != consumer_range[0] or report.get("head_sha") != consumer_range[1]:
        return "consumer verdict range does not match its generated command"
    return None


def consumer_status(returncode: object) -> str:
    """Map a consumer exit code to a producer status.

    The consumer separates "I judged and it failed" (1) from "I refused to judge"
    (2) deliberately. Collapsing every nonzero to `blocked` threw that away and
    told the operator there are uncovered changed lines when the truth was that
    the gate could not look — a refusal narrated as a verdict, on a proof surface.

    Exit 3 (ran, established nothing) still maps to `blocked`, and that is
    PRESERVED behavior rather than a considered one: the producer runs under
    `--verification-lock` where coverage was just produced, so an unestablished
    result there is a real closeout gap, and softening it would weaken the
    closeout in a slice that was not scoped to decide that. Named here so the
    next reader sees a decision instead of an accident.
    """
    if returncode == 0:
        return "passed"
    if returncode == CONSUMER_REFUSED_EXIT:
        return "refused"
    if returncode == CONSUMER_PARTIAL_EXIT:
        # `blocked` HERE, deliberately, and for the same reason exit 3 is: this
        # producer runs under `--verification-lock`, where the coverage was just
        # produced over the whole changed set, so a scope that came back short is a
        # real closeout gap rather than the mapper's blind spot. A bounded
        # diagnostic invocation can answer the same byte with a non-blocking
        # `partial`, because its scope is limited BY DESIGN. Two contexts, two
        # right answers -- which is exactly why this needs a branch and not a
        # fallthrough.
        return "blocked"
    return "blocked"


def run_produced_coverage_consumer(
    repo_root: Path,
    payload: dict[str, object],
    run_command: Callable[[Path, str, str], dict[str, object]],
) -> bool:
    """Run the authoritative changed-line consumer for successful producers.

    Coverage production alone is not changed-line proof.  The consumer owns the
    classification, so this only executes its already-recorded command and
    carries its structured verdict into the closeout payload.  Before commit,
    though, ``base..HEAD`` excludes dirty eligible files; record that limitation
    as a non-claim instead of manufacturing a green consumer run for the parent
    commit.
    """
    for producer_result in payload.get("executed_commands", []):
        if not isinstance(producer_result, dict) or not producer_result.get("produced_mutation_coverage"):
            continue
        if "mutation_coverage_consumer" in producer_result:
            continue
        command = producer_result.get("mutation_coverage_consumer_command")
        base_sha = producer_result.get("mutation_coverage_base_sha")
        if not isinstance(command, str) or not isinstance(base_sha, str) or not base_sha:
            producer_result["mutation_coverage_consumer"] = {
                "status": "failed",
                "reason": "producer did not provide a usable changed-line consumer range",
            }
            payload["mutation_coverage_changed_line_proof"] = {
                "status": "failed",
                "reason": "producer metadata was incomplete; changed-line coverage was not verified",
            }
            payload["status"] = "failed"
            payload["error"] = "mutation-coverage producer omitted the authoritative consumer range"
            return True

        eligible = set(_consumer.list_eligible(repo_root))
        uncommitted = _consumer.uncommitted_pool_changes(repo_root, eligible)
        if uncommitted:
            consumer_record = {
                "status": "not_checked",
                "command": command,
                "reason": (
                    "eligible mutation-pool worktree changes are excluded from "
                    "base..HEAD; no changed-line claim was made"
                ),
                "uncommitted_eligible_files": uncommitted,
            }
            producer_result["mutation_coverage_consumer"] = consumer_record
            payload["mutation_coverage_changed_line_proof"] = consumer_record
            continue

        result = dict(run_command(repo_root, command, "verify"))
        result["mutation_coverage_consumer"] = True
        report = _consumer_report(result)
        status = consumer_status(result.get("returncode"))
        if report and report.get("coverage_not_verified"):
            status = "not_checked"
        validation_error = None
        if status == "passed":
            validation_error = (
                "consumer emitted no readable object verdict"
                if report is None
                else _consumer_pass_validation_error(
                    report, command=command, producer_base_sha=base_sha
                )
            )
            if validation_error is not None:
                status = "failed"
        consumer_record: dict[str, object] = {"status": status, "command": command}
        if report is not None:
            consumer_record["report"] = report
        if validation_error is not None:
            consumer_record["reason"] = validation_error
        producer_result["mutation_coverage_consumer"] = consumer_record
        payload["mutation_coverage_changed_line_proof"] = consumer_record
        payload["executed_commands"].append(result)

        if status == "refused":
            payload["status"] = "failed"
            payload["error"] = (
                "changed-line mutation-coverage consumer REFUSED to judge (no verdict): "
                f"{(report or {}).get('reason') or 'contaminated inputs or an untrusted run'}. "
                "This is not a report of uncovered changed lines."
            )
            return True
        if status == "blocked":
            payload["status"] = "failed"
            payload["error"] = "changed-line mutation-coverage consumer blocked the produced coverage"
            return True
        if status == "failed":
            payload["status"] = "failed"
            payload["error"] = (
                "changed-line mutation-coverage consumer emitted an invalid or mismatched verdict"
            )
            return True
        if status == "not_checked":
            payload["status"] = "failed"
            payload["error"] = "changed-line mutation coverage was not verified; no changed-line claim can be made"
            return True
    return False


def closeout_producer_or_error(
    args: object,
    repo_root: Path,
    run_command: Callable[[Path, str, str], dict[str, object]],
    *,
    base_sha: str | None = None,
) -> tuple[Callable[[Path, str, str], dict[str, object]] | None, str | None]:
    """Resolve the closeout broad-pytest producer from parsed args.

    Returns ``(producer, None)`` when producing is requested and valid,
    ``(None, error)`` on misuse (produce without the verification lock, or with
    --skip-broad-pytest so there is no broad run to instrument), and
    ``(None, None)`` when producing is not requested.
    """
    validation_error = closeout_producer_validation_error(args)
    if validation_error:
        return None, validation_error
    if not getattr(args, "produce_mutation_coverage", False):
        return None, None
    focused_command = getattr(args, "mutation_coverage_command", None)
    if focused_command:
        return None, None
    producer_kwargs = {
        "extra_pytest_targets": list(getattr(args, "mutation_coverage_extra_pytest_target", []) or []),
    }
    if base_sha is not None:
        producer_kwargs["base_sha"] = base_sha
    return make_closeout_producer(repo_root, run_command, **producer_kwargs), None
