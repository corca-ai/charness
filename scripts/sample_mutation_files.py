#!/usr/bin/env python3
"""Pick a deterministic stratified sample of Cosmic Ray mutation targets.

The sample rewrites `cosmic-ray.toml`'s `module-path` list so the following
Cosmic Ray init/exec run mutates only the selected files.
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.mutation_manifest_lib import build_manifest_from_state, write_manifest  # noqa: E402
from scripts.mutation_sampling_lib import (  # noqa: E402
    build_mutation_line_coverage,
    filter_eligible_by_coverage,
    filter_eligible_by_mutation_line_coverage,
    load_covered_lines,
    load_file_statement_lines,
    load_line_contexts,
    read_test_command,
    rewrite_cosmic_ray_targets,
    rewrite_cosmic_ray_test_command,
    run_test_coverage,
    select_budgeted_sample,
    select_test_nodeids,
)

MUTATION_POOLS = {
    "core-python": (
        "charness",
        "runtime_bootstrap.py",
        "skill_runtime_bootstrap.py",
        "scripts/*.py",
    ),
    "public-skill-python": ("skills/public/*/scripts/*.py",),
    "support-skill-python": ("skills/support/*/scripts/*.py",),
}
EXCLUDED_NAMES = {"__init__.py"}
DEFAULT_MAX_FILES = 10
DEFAULT_CHANGED_QUOTA = 5
DEFAULT_COVERAGE_JSON = Path("reports/mutation/test-coverage.json")
DEFAULT_MIN_FILE_COVERAGE = 0.85
DEFAULT_MAX_EXECUTABLE_MUTANTS = 120
DEFAULT_MAX_EXECUTABLE_MUTANTS_PER_FILE = 80
DEFAULT_MAX_TEST_NODEIDS = 40


def list_eligible(repo_root: Path) -> list[str]:
    paths: set[str] = set()
    for patterns in MUTATION_POOLS.values():
        for pattern in patterns:
            for path in repo_root.glob(pattern):
                if not path.is_file() or path.name in EXCLUDED_NAMES:
                    continue
                paths.add(path.relative_to(repo_root).as_posix())
    return sorted(paths)


def pool_for_path(path: str) -> str:
    candidate = Path(path)
    parts = candidate.parts
    if path in {"charness", "runtime_bootstrap.py", "skill_runtime_bootstrap.py"}:
        return "core-python"
    if len(parts) == 2 and parts[0] == "scripts" and candidate.suffix == ".py":
        return "core-python"
    if (
        len(parts) == 5
        and parts[0] == "skills"
        and parts[1] == "public"
        and parts[3] == "scripts"
        and candidate.suffix == ".py"
    ):
        return "public-skill-python"
    if (
        len(parts) == 5
        and parts[0] == "skills"
        and parts[1] == "support"
        and parts[3] == "scripts"
        and candidate.suffix == ".py"
    ):
        return "support-skill-python"
    return "unknown"


def mutation_pathspecs() -> list[str]:
    pathspecs: list[str] = []
    for patterns in MUTATION_POOLS.values():
        for pattern in patterns:
            root = pattern.split("*", 1)[0].rstrip("/")
            pathspecs.append(root or pattern)
    return sorted(set(pathspecs))


def list_changed(repo_root: Path, base_sha: str, head_sha: str) -> list[str]:
    if not base_sha:
        return []
    head = head_sha or "HEAD"
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_sha}..{head}", "--", *mutation_pathspecs()],
            cwd=repo_root,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"git diff {base_sha}..{head} failed: {exc.stderr}\n")
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def positive_int(value: str | None, default: int) -> int:
    if value is None or value == "":
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise SystemExit(f"expected non-negative integer, got: {value!r}") from exc
    if parsed < 0:
        raise SystemExit(f"expected non-negative integer, got: {value!r}")
    return parsed


def append_github_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as output:
        output.write(f"{name}={value}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--config", type=Path, default=Path("cosmic-ray.toml"))
    parser.add_argument("--manifest-json", type=Path, default=Path("reports/mutation/sample.json"))
    parser.add_argument("--manifest-md", type=Path, default=Path("reports/mutation/sample.md"))
    parser.add_argument("--coverage-json", type=Path, default=DEFAULT_COVERAGE_JSON)
    parser.add_argument(
        "--skip-coverage",
        action="store_true",
        help="Skip test-command coverage collection. Intended for narrow unit tests only.",
    )
    return parser.parse_args()


def parse_min_file_coverage() -> float:
    try:
        min_file_coverage = float(
            (os.environ.get("MUTATION_SAMPLE_MIN_FILE_COVERAGE") or "").strip()
            or DEFAULT_MIN_FILE_COVERAGE
        )
    except ValueError as exc:
        raise SystemExit("MUTATION_SAMPLE_MIN_FILE_COVERAGE must be a number") from exc
    if min_file_coverage < 0 or min_file_coverage > 1:
        raise SystemExit("MUTATION_SAMPLE_MIN_FILE_COVERAGE must be between 0 and 1")
    return min_file_coverage


def select_eligible_for_mutation(
    *,
    repo_root: Path,
    config_path: Path,
    all_eligible: list[str],
    coverage_enabled: bool,
    coverage_json: Path,
    test_command: str,
    min_file_coverage: float,
) -> tuple[list[str], dict[str, dict[int, set[str]]], dict[str, dict[str, int]]]:
    if not coverage_enabled:
        return all_eligible, {}, {}
    try:
        run_test_coverage(repo_root, test_command, coverage_json)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"test-command coverage probe failed with exit {exc.returncode}: {test_command}"
        ) from exc

    covered_lines = load_covered_lines(repo_root, coverage_json)
    statement_lines = load_file_statement_lines(repo_root, coverage_json)
    line_contexts = load_line_contexts(repo_root, coverage_json)
    coverage_eligible = filter_eligible_by_coverage(
        all_eligible,
        covered_lines,
        statement_lines,
        min_file_coverage=min_file_coverage,
    )
    mutation_line_coverage = build_mutation_line_coverage(
        repo_root,
        config_path,
        coverage_eligible,
        covered_lines,
    )
    return (
        filter_eligible_by_mutation_line_coverage(coverage_eligible, mutation_line_coverage),
        line_contexts,
        mutation_line_coverage,
    )


def mutation_test_command_for_sample(
    repo_root: Path,
    sample: list[str],
    line_contexts: dict[str, dict[int, set[str]]],
    fallback_command: str,
    *,
    coverage_enabled: bool,
) -> str | None:
    if not coverage_enabled:
        return fallback_command
    test_nodeids = select_test_nodeids(repo_root, sample, line_contexts)
    if not test_nodeids:
        return None
    return shlex.join(["python3", "-m", "pytest", "-q", *test_nodeids])


def parse_workload_limits() -> tuple[int, int, int]:
    total = positive_int(os.environ.get("MUTATION_SAMPLE_MAX_EXECUTABLE_MUTANTS"), DEFAULT_MAX_EXECUTABLE_MUTANTS)
    per_file = positive_int(
        os.environ.get("MUTATION_SAMPLE_MAX_EXECUTABLE_MUTANTS_PER_FILE"),
        DEFAULT_MAX_EXECUTABLE_MUTANTS_PER_FILE,
    )
    nodeids = positive_int(os.environ.get("MUTATION_SAMPLE_MAX_TEST_NODEIDS"), DEFAULT_MAX_TEST_NODEIDS)
    return total, per_file, nodeids


def output_paths(args: argparse.Namespace, repo_root: Path) -> tuple[Path, Path]:
    manifest_json = (
        args.manifest_json if args.manifest_json.is_absolute() else repo_root / args.manifest_json
    )
    manifest_md = args.manifest_md if args.manifest_md.is_absolute() else repo_root / args.manifest_md
    return manifest_json, manifest_md


def report_no_eligible(coverage_enabled: bool, test_command: str) -> None:
    if coverage_enabled:
        sys.stderr.write(
            f"no eligible mutation pool files had coverage from {test_command!r}\n"
        )
    else:
        sys.stderr.write("no eligible files matched the configured mutation pools\n")


def select_sample_files(
    *,
    repo_root: Path,
    seed: str,
    max_files: int,
    changed_quota: int,
    changed: list[str],
    eligible: list[str],
    mutation_line_coverage: dict[str, dict[str, int]],
    line_contexts: dict[str, dict[int, set[str]]],
    coverage_enabled: bool,
    max_executable_mutants: int,
    max_executable_mutants_per_file: int,
    max_test_nodeids: int,
) -> tuple[list[str], list[str], list[str], list[str], list[str], int]:
    changed_sample, selection_excluded_changed_files, selected_executable_mutants = (
        select_budgeted_sample(
            repo_root=repo_root,
            candidates=changed,
            limit=changed_quota,
            seed=f"{seed}:changed",
            selected=[],
            selected_workload=0,
            mutation_line_coverage=mutation_line_coverage,
            line_contexts=line_contexts,
            coverage_enabled=coverage_enabled,
            max_executable_mutants=max_executable_mutants,
            max_executable_mutants_per_file=max_executable_mutants_per_file,
            max_test_nodeids=max_test_nodeids,
        )
    )
    fill_pool = [path for path in eligible if path not in set(changed)]
    fill_sample, selection_excluded_fill_files, selected_executable_mutants = (
        select_budgeted_sample(
            repo_root=repo_root,
            candidates=fill_pool,
            limit=max_files - len(changed_sample),
            seed=f"{seed}:fill",
            selected=changed_sample,
            selected_workload=selected_executable_mutants,
            mutation_line_coverage=mutation_line_coverage,
            line_contexts=line_contexts,
            coverage_enabled=coverage_enabled,
            max_executable_mutants=max_executable_mutants,
            max_executable_mutants_per_file=max_executable_mutants_per_file,
            max_test_nodeids=max_test_nodeids,
        )
    )
    sample = changed_sample + fill_sample
    return (
        changed_sample,
        fill_sample,
        sample,
        selection_excluded_changed_files,
        selection_excluded_fill_files,
        selected_executable_mutants,
    )


def publish_sample(
    *,
    args: argparse.Namespace,
    repo_root: Path,
    config_path: Path,
    manifest: dict,
    sample: list[str],
    mutation_test_command: str,
) -> None:
    manifest_json, manifest_md = output_paths(args, repo_root)
    write_manifest(manifest, manifest_json, manifest_md)
    rewrite_cosmic_ray_targets(config_path, sample)
    rewrite_cosmic_ray_test_command(config_path, mutation_test_command)

    sample_arg = " ".join(sample)
    append_github_output("sample_files", sample_arg)
    sys.stdout.write(f"sample ({len(sample)}/{manifest['max_files']}): {sample_arg}\n")


def main() -> int:
    args = parse_args()

    repo_root = args.repo_root.resolve()
    config_path = args.config if args.config.is_absolute() else repo_root / args.config
    max_files = positive_int(os.environ.get("MUTATION_SAMPLE_MAX_FILES"), DEFAULT_MAX_FILES)
    changed_quota = min(
        positive_int(os.environ.get("MUTATION_SAMPLE_CHANGED_QUOTA"), DEFAULT_CHANGED_QUOTA),
        max_files,
    )
    base_sha = (os.environ.get("MUTATION_BASE_SHA") or "").strip()
    head_sha = (os.environ.get("MUTATION_HEAD_SHA") or "").strip()
    seed = (os.environ.get("MUTATION_SAMPLE_SEED") or "").strip() or str(int(time.time()))
    min_file_coverage = parse_min_file_coverage()
    workload_limits = parse_workload_limits()
    max_executable_mutants, max_executable_mutants_per_file, max_test_nodeids = workload_limits

    coverage_json = args.coverage_json if args.coverage_json.is_absolute() else repo_root / args.coverage_json
    test_command = read_test_command(config_path)
    coverage_enabled = (
        not args.skip_coverage and (os.environ.get("MUTATION_SAMPLE_COVERAGE") or "1") != "0"
    )

    all_eligible = list_eligible(repo_root)
    eligible, line_contexts, mutation_line_coverage = select_eligible_for_mutation(
        repo_root=repo_root,
        config_path=config_path,
        all_eligible=all_eligible,
        coverage_enabled=coverage_enabled,
        coverage_json=coverage_json,
        test_command=test_command,
        min_file_coverage=min_file_coverage,
    )

    if not eligible:
        report_no_eligible(coverage_enabled, test_command)
        return 1
    all_eligible_set = set(all_eligible)
    eligible_set = set(eligible)
    changed_before_coverage = [
        path for path in list_changed(repo_root, base_sha, head_sha) if path in all_eligible_set
    ]
    changed = [path for path in changed_before_coverage if path in eligible_set]
    uncovered_changed_files = [
        path for path in changed_before_coverage if coverage_enabled and path not in eligible_set
    ]

    (
        changed_sample,
        fill_sample,
        sample,
        selection_excluded_changed_files,
        selection_excluded_fill_files,
        selected_executable_mutants,
    ) = select_sample_files(
        repo_root=repo_root,
        seed=seed,
        max_files=max_files,
        changed_quota=changed_quota,
        changed=changed,
        eligible=eligible,
        mutation_line_coverage=mutation_line_coverage,
        line_contexts=line_contexts,
        coverage_enabled=coverage_enabled,
        max_executable_mutants=max_executable_mutants,
        max_executable_mutants_per_file=max_executable_mutants_per_file,
        max_test_nodeids=max_test_nodeids,
    )
    if not sample:
        sys.stderr.write("no mutation sample files were selected\n")
        return 1

    mutation_test_command = mutation_test_command_for_sample(
        repo_root,
        sample,
        line_contexts,
        test_command,
        coverage_enabled=coverage_enabled,
    )
    if mutation_test_command is None:
        sys.stderr.write("no pytest test nodeids were observed for the selected mutation sample\n")
        return 1

    publish_sample(
        args=args,
        repo_root=repo_root,
        config_path=config_path,
        manifest=build_manifest_from_state({**locals(), "pool_for_path": pool_for_path}),
        sample=sample,
        mutation_test_command=mutation_test_command,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
