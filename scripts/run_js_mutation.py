#!/usr/bin/env python3
"""Run the repo-owned StrykerJS mutation workflow for agent runtime modules."""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = Path("stryker.config.mjs")
DEFAULT_LOG = Path("reports/mutation/stryker-js.log")
DEFAULT_REPORT_JSON = Path("reports/mutation/stryker-js.json")
DEFAULT_TIMEOUT_SECONDS = 900
DEFAULT_MAX_FILES = 1
DEFAULT_MAX_MUTANTS = 120
JS_MUTATION_POOL = ("scripts/agent-runtime/*.mjs",)
JS_MUTATION_MUTANT_WEIGHTS = {
    "scripts/agent-runtime/codex-eval-runtime.mjs": 142,
    "scripts/agent-runtime/contract-versions.mjs": 5,
    "scripts/agent-runtime/extract-skill-experiment-input.mjs": 369,
    "scripts/agent-runtime/instruction-surface-case-suite.mjs": 262,
    "scripts/agent-runtime/instruction-surface-support.mjs": 334,
    "scripts/agent-runtime/run-local-eval-test.mjs": 668,
    "scripts/agent-runtime/skill-test-telemetry.mjs": 86,
}


def resolve(repo_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


def positive_int(value: str | None, default: int) -> int:
    if not value:
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise SystemExit(f"expected integer timeout, got {value!r}") from exc
    if parsed <= 0:
        raise SystemExit(f"expected positive timeout, got {value!r}")
    return parsed


def stryker_bin(repo_root: Path) -> Path:
    binary = repo_root / "node_modules" / ".bin" / ("stryker.cmd" if os.name == "nt" else "stryker")
    if not binary.is_file():
        raise SystemExit(
            "StrykerJS is not installed; run `npm install` before JS mutation testing."
        )
    return binary


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def list_js_targets(repo_root: Path) -> list[str]:
    targets: set[str] = set()
    for pattern in JS_MUTATION_POOL:
        for path in repo_root.glob(pattern):
            if path.is_file():
                targets.add(path.relative_to(repo_root).as_posix())
    return sorted(targets)


def select_js_targets(repo_root: Path, *, mode: str) -> list[str]:
    explicit = (os.environ.get("MUTATION_JS_TARGETS") or "").strip()
    if explicit:
        return explicit.split()
    targets = list_js_targets(repo_root)
    if mode == "dry-run":
        return targets
    max_files = positive_int(os.environ.get("MUTATION_JS_MAX_FILES"), DEFAULT_MAX_FILES)
    max_mutants = positive_int(os.environ.get("MUTATION_JS_MAX_MUTANTS"), DEFAULT_MAX_MUTANTS)
    seed = (os.environ.get("MUTATION_SAMPLE_SEED") or "default-js-mutation-seed").strip()
    selected: list[str] = []
    selected_mutants = 0
    for path in sorted(targets, key=lambda item: stable_hash(f"{seed}:{item}")):
        weight = JS_MUTATION_MUTANT_WEIGHTS.get(path, 0)
        if max_mutants and weight and selected_mutants + weight > max_mutants:
            continue
        selected.append(path)
        selected_mutants += weight
        if len(selected) >= max_files:
            break
    return selected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--mode", choices=("dry-run", "full"), default="dry-run")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=positive_int(os.environ.get("MUTATION_JS_TIMEOUT_SECONDS"), DEFAULT_TIMEOUT_SECONDS),
    )
    return parser.parse_args()


def remove_stale_report(repo_root: Path, report_json: Path) -> Path:
    report_path = resolve(repo_root, report_json)
    if report_path.is_file():
        report_path.unlink()
    return report_path


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    config_path = resolve(repo_root, args.config)
    log_path = resolve(repo_root, args.log)
    report_path = remove_stale_report(repo_root, args.report_json)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    command = [str(stryker_bin(repo_root)), "run", str(config_path)]
    if args.mode == "dry-run":
        command.append("--dryRunOnly")

    targets = select_js_targets(repo_root, mode=args.mode)
    if not targets:
        raise SystemExit("no JS mutation targets selected; adjust MUTATION_JS_MAX_MUTANTS or MUTATION_JS_TARGETS")
    env = {**os.environ, "MUTATION_JS_TARGETS": " ".join(targets)}

    with log_path.open("w", encoding="utf-8") as log:
        log.write("+ " + " ".join(command) + "\n")
        log.write(f"MUTATION_JS_TARGETS={env['MUTATION_JS_TARGETS']}\n")
        log.write(f"STRYKER_JS_REPORT={report_path}\n")
        log.flush()
        try:
            result = subprocess.run(
                command,
                cwd=repo_root,
                check=False,
                text=True,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=args.timeout_seconds,
                env=env,
            )
        except subprocess.TimeoutExpired:
            log.write(f"\nStrykerJS mutation timed out after {args.timeout_seconds}s.\n")
            return 124

    sys.stdout.write(f"StrykerJS {args.mode} log written to {log_path}\n")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
