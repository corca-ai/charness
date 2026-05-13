#!/usr/bin/env python3

"""Fail when a `.cautilus/runs/` directory has no paired failing-log citation
in `charness-artifacts/cautilus/latest.md` or in the recent git log.

Post-hoc layer of the script-silence layer-3 structural guard: even if the
operator bypasses `scripts/run_cautilus_eval.py` and invokes `cautilus eval`
directly, the resulting run directory must leave a structured provenance
trail. The validator accepts either:

- a `- source-ref: <path>` line in the proof artifact whose value names the
  run id or run-relative path, or
- a commit message that contains both the run id (or run-relative path) and
  a `source-kind: <kind>` token whose kind is one of failing-prompt,
  transcript, operator-log, issue-log, or regression-log.

Bare run-id mentions in prose do not satisfy the contract: the artifact-side
match requires the structured `- source-ref:` line shape, and the commit-side
match requires a paired `source-kind:` token in the same commit body.

Run ids are parsed from directory names matching `YYYYMMDDTHHMMSSmmmZ-*`
(the layout cautilus produces). Runs dated before ENFORCED_FROM_DATE are
grandfathered.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

DEFAULT_RUNS_DIR = ".cautilus/runs"
DEFAULT_ARTIFACT = "charness-artifacts/cautilus/latest.md"
ENFORCED_FROM_DATE = date(2026, 5, 13)
GIT_LOG_DEPTH = 50
RUN_ID_DATE_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})T\d{6}")
SOURCE_REF_LINE_RE = re.compile(r"(?mi)^\s*-\s*source-ref\s*:\s*`?([^`\s]+)`?\s*$")
SOURCE_KIND_TOKEN_RE = re.compile(
    r"(?i)source-kind\s*:\s*`?(?:failing-prompt|transcript|operator-log|issue-log|regression-log)`?\b"
)
COMMIT_SEPARATOR = "\x00"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, default=None)
    parser.add_argument("--artifact", type=Path, default=None)
    parser.add_argument("--git-log-depth", type=int, default=GIT_LOG_DEPTH)
    return parser.parse_args()


def _run_date(run_name: str) -> date | None:
    match = RUN_ID_DATE_RE.match(run_name)
    if not match:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def _recent_log_messages(repo_root: Path, depth: int) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-n", str(depth), "--format=%B%x00"],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    runs_dir = (args.runs_dir or (repo_root / DEFAULT_RUNS_DIR)).resolve()
    artifact = (args.artifact or (repo_root / DEFAULT_ARTIFACT)).resolve()

    if not runs_dir.is_dir():
        print("No .cautilus/runs/ directory; nothing to check.")
        return 0

    run_dirs = sorted([p for p in runs_dir.iterdir() if p.is_dir()])
    if not run_dirs:
        print(f"{runs_dir.relative_to(repo_root)}/ has no run directories; nothing to check.")
        return 0

    artifact_text = artifact.read_text(encoding="utf-8") if artifact.is_file() else ""
    artifact_source_refs = SOURCE_REF_LINE_RE.findall(artifact_text)
    log_text = _recent_log_messages(repo_root, args.git_log_depth)
    commit_bodies = [body for body in log_text.split(COMMIT_SEPARATOR) if body.strip()]

    failures: list[str] = []
    validated: list[str] = []
    grandfathered: list[str] = []
    for run_dir in run_dirs:
        run_id = run_dir.name
        run_date = _run_date(run_id)
        if run_date is not None and run_date < ENFORCED_FROM_DATE:
            grandfathered.append(run_id)
            continue
        run_rel = run_dir.relative_to(repo_root).as_posix()
        artifact_cited = any(
            run_id in ref or run_rel in ref for ref in artifact_source_refs
        )
        commit_cited = any(
            (run_id in body or run_rel in body) and SOURCE_KIND_TOKEN_RE.search(body)
            for body in commit_bodies
        )
        if artifact_cited or commit_cited:
            validated.append(run_id)
            continue
        failures.append(
            f"cautilus run `{run_rel}` lacks a structured provenance citation. Add a "
            f"`- source-ref:` line referencing the run path under "
            f"`{artifact.relative_to(repo_root)}` `## Behavior Source`, or include both the "
            f"run id and a `source-kind: <kind>` token in a commit message (last "
            f"{args.git_log_depth} commits searched). Alternatively, invoke cautilus via "
            f"scripts/run_cautilus_eval.py with --justification-log <path>."
        )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    summary_parts = []
    if validated:
        summary_parts.append(f"{len(validated)} cited")
    if grandfathered:
        summary_parts.append(f"{len(grandfathered)} grandfathered (pre-{ENFORCED_FROM_DATE.isoformat()})")
    if summary_parts:
        print(f"Validated cautilus call provenance: {', '.join(summary_parts)}.")
    else:
        print("No cautilus runs to validate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
