"""Keep scheduled mutation inside the job: mapped tests, no whole-suite contexts."""

from __future__ import annotations

import shlex
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.mutation.mutation_baseline_abort_lib import (  # noqa: E402
    STAGE_SAMPLER_COVERAGE,
    log_tail_lines,
    parse_failed_nodeids,
    write_baseline_abort_marker,
)
from scripts.mutation.mutation_changed_files_lib import (  # noqa: E402
    invalidate_changed_line_coverage_marker,
)
from scripts.mutation.mutation_outer_budget import (  # noqa: E402
    InnerTimeoutExceedsOuterBudget,
    job_budget_from_env,
    resolve_exec_timeout_seconds,
)
from scripts.mutation.mutation_sampling_lib import (  # noqa: E402
    CoverageCommandError,
    load_file_statement_lines,
    run_test_coverage,
)
from scripts.mutation.suggest_mutation_coverage_command import (  # noqa: E402
    tests_referencing_paths,
)

DEFAULT_MAX_TEST_NODEIDS = 40
SECONDS_PER_MUTANT = 45


def mapped_test_targets(repo_root: Path, paths: list[str], *, limit: int) -> list[str]:
    matches = tests_referencing_paths(repo_root, paths)
    ordered: list[str] = []
    seen: set[str] = set()
    for path in paths:
        for target in matches.get(path, []):
            if target in seen:
                continue
            seen.add(target)
            ordered.append(target)
            if limit and len(ordered) >= limit:
                return ordered
    return ordered


def standing_pytest_command(targets: list[str]) -> str:
    argv = [
        "python3",
        "scripts/gates_support/run_standing_pytest.py",
        "--repo-root",
        ".",
        "--mode",
        "read-only",
    ]
    for target in targets:
        argv.extend(["--pytest-target", target])
    return shlex.join(argv)


def focused_statement_lines_for_changed_files(
    *,
    repo_root: Path,
    changed_paths: list[str],
    coverage_json: Path,
    baseline_abort_marker_path: Path,
    max_test_nodeids: int,
) -> dict[str, tuple[set[int], set[int]]]:
    """Statement coverage of tests mapped to changed files only. No contexts."""
    if not changed_paths:
        return {}
    invalidate_changed_line_coverage_marker(coverage_json)
    targets = mapped_test_targets(repo_root, changed_paths, limit=max_test_nodeids)
    if not targets:
        return {}
    command = standing_pytest_command(targets)
    try:
        run_test_coverage(repo_root, command, coverage_json, dynamic_context=False)
    except CoverageCommandError as exc:
        combined_output = f"{exc.output or ''}{exc.stderr or ''}"
        failing_nodeids = parse_failed_nodeids(combined_output)
        write_baseline_abort_marker(
            baseline_abort_marker_path,
            exit_code=exc.returncode,
            test_command=command,
            failing_nodeids=failing_nodeids,
            log_tail=[] if failing_nodeids else log_tail_lines(combined_output),
            stage=STAGE_SAMPLER_COVERAGE,
        )
        message = f"focused coverage probe failed with exit {exc.returncode}: {command}"
        if failing_nodeids:
            message += "\nfailing nodeids:\n" + "\n".join(
                f"  - {nodeid}" for nodeid in failing_nodeids
            )
        raise SystemExit(message) from exc
    return load_file_statement_lines(repo_root, coverage_json)


def cap_mutants_to_remaining_job(configured: int) -> int:
    start, timeout = job_budget_from_env()
    if start is None or timeout is None:
        return configured
    try:
        remaining, _reason = resolve_exec_timeout_seconds(
            configured * SECONDS_PER_MUTANT,
            job_start_epoch=start,
            job_timeout_seconds=timeout,
        )
    except InnerTimeoutExceedsOuterBudget:
        return 1
    return max(1, min(configured, remaining // SECONDS_PER_MUTANT))


def mutation_test_command_for_sample(
    repo_root: Path,
    sample: list[str],
    line_contexts: dict[str, dict[int, set[str]]],
    fallback_command: str,
    *,
    coverage_enabled: bool,
    max_test_nodeids: int = DEFAULT_MAX_TEST_NODEIDS,
) -> str | None:
    del line_contexts
    targets = mapped_test_targets(repo_root, sample, limit=max_test_nodeids)
    if targets:
        return standing_pytest_command(targets)
    if not coverage_enabled:
        return fallback_command
    return None
