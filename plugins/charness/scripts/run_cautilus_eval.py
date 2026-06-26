#!/usr/bin/env python3

"""Repo-owned wrapper for `cautilus evaluate fixture/observation/skill-experiment`.

Enforces the planner-consult contract from
`skills/public/quality/references/cautilus-on-demand.md`: every cautilus evaluate
invocation runs `scripts/plan_cautilus_proof.py` first and refuses with exit
code 2 when the planner says the call is not warranted.

Refuses when no `--justification-log` is provided AND the planner returns
either `next_action: "none"` or `must_ask_before_running: true`. The
justification-log path is the operator-supplied override: it must exist as a
file of at least 32 bytes containing a `- source-kind: <kind>` line whose
kind is one of `failing-prompt`, `transcript`, `operator-log`, `issue-log`,
or `regression-log` (mirroring the `## Behavior Source` shape in
`charness-artifacts/cautilus/latest.md`). Otherwise forwards to `cautilus evaluate
<mode>` with any extra args after `--`.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
_plan_module = import_repo_module(__file__, "scripts.plan_cautilus_proof")
plan_cautilus_proof = _plan_module.plan_cautilus_proof
_surfaces_lib = import_repo_module(__file__, "scripts.surfaces_lib")
collect_changed_paths = _surfaces_lib.collect_changed_paths
normalize_repo_path = _surfaces_lib.normalize_repo_path

VALID_MODES = ("fixture", "observation", "skill-experiment")
CANONICAL_REFERENCE_PATH = "skills/public/quality/references/cautilus-on-demand.md"
PLUGIN_REFERENCE_PATH = "skills/quality/references/cautilus-on-demand.md"
JUSTIFICATION_LOG_MIN_BYTES = 32
DEFAULT_CAUTILUS_TIMEOUT_SECONDS = 1800
# Mirrors VALID_BEHAVIOR_SOURCE_KINDS in scripts/validate_cautilus_proof.py so the
# wrapper, the artifact validator, and the cautilus-on-demand reference all share
# one grammar. A trivial file containing the marker token as a substring no
# longer passes — the wrapper requires a `- source-kind: <kind>` line shape.
JUSTIFICATION_LOG_KINDS = (
    "failing-prompt",
    "transcript",
    "operator-log",
    "issue-log",
    "regression-log",
)
SOURCE_KIND_LINE_RE = re.compile(
    r"^\s*-\s*source-kind\s*:\s*`?([a-z0-9_-]+)`?\s*$",
    re.MULTILINE,
)


def _default_timeout_seconds() -> float:
    raw = os.environ.get("CHARNESS_CAUTILUS_TIMEOUT_SECONDS")
    if raw is None:
        return float(DEFAULT_CAUTILUS_TIMEOUT_SECONDS)
    try:
        value = float(raw)
    except ValueError:
        return float(DEFAULT_CAUTILUS_TIMEOUT_SECONDS)
    return value if value > 0 else float(DEFAULT_CAUTILUS_TIMEOUT_SECONDS)


def parse_args(argv: list[str] | None = None) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Repo-owned wrapper for cautilus evaluate fixture/observation/skill-experiment.",
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--mode",
        required=True,
        choices=VALID_MODES,
        help="cautilus evaluate subcommand to invoke",
    )
    parser.add_argument(
        "--justification-log",
        type=Path,
        required=True,
        help="Path to the failing prompt/transcript/operator-log that motivates this run (required to keep cautilus provenance non-empty).",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Explicit repo-relative paths for the planner. Defaults to current git diff.",
    )
    parser.add_argument(
        "--cautilus-bin",
        default="cautilus",
        help="Cautilus binary to invoke. Defaults to `cautilus` on PATH.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the planner gate and print the forwarded command without invoking it.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=_default_timeout_seconds(),
        help="Maximum wall-clock seconds for the forwarded cautilus process.",
    )
    return parser.parse_known_args(argv)


def _reference_path(repo_root: Path) -> str:
    for candidate in (CANONICAL_REFERENCE_PATH, PLUGIN_REFERENCE_PATH):
        if (repo_root / candidate).is_file():
            return candidate
    return CANONICAL_REFERENCE_PATH


def _refuse(message: str, repo_root: Path) -> int:
    print(
        f"refusing: {message} see {_reference_path(repo_root)}",
        file=sys.stderr,
    )
    return 2


def _run_forwarded_cautilus(args: argparse.Namespace, cmd: list[str], repo_root: Path) -> subprocess.CompletedProcess[bytes] | int:
    try:
        return subprocess.run(cmd, check=False, timeout=args.timeout_seconds)
    except FileNotFoundError:
        return _refuse(
            f"cautilus binary `{args.cautilus_bin}` not on PATH; install cautilus "
            "or pass --cautilus-bin <path>.",
            repo_root,
        )
    except subprocess.TimeoutExpired:
        print(
            f"cautilus evaluate timed out after {args.timeout_seconds}s: {' '.join(cmd)}",
            file=sys.stderr,
        )
        return 124


def main(argv: list[str] | None = None) -> int:
    args, remaining = parse_args(argv)
    repo_root = args.repo_root.resolve()
    if args.timeout_seconds <= 0:
        return _refuse("--timeout-seconds must be a positive number.", repo_root)

    if args.paths is not None:
        changed_paths = [normalize_repo_path(path) for path in args.paths]
    else:
        changed_paths = collect_changed_paths(repo_root)
    plan = plan_cautilus_proof(repo_root, changed_paths)
    if plan["next_action"] == "none" or plan["must_ask_before_running"]:
        print(
            f"note: planner reports next_action={plan['next_action']!r}, "
            f"must_ask_before_running={plan['must_ask_before_running']!r}; "
            "proceeding because an explicit --justification-log is supplied.",
            file=sys.stderr,
        )

    log_path = args.justification_log
    if not log_path.is_file():
        return _refuse(
            f"--justification-log path {log_path} is missing.",
            repo_root,
        )
    size = log_path.stat().st_size
    if size == 0:
        return _refuse(
            f"--justification-log path {log_path} is empty.",
            repo_root,
        )
    if size < JUSTIFICATION_LOG_MIN_BYTES:
        return _refuse(
            f"--justification-log path {log_path} is {size} bytes; "
            f"behavior-proof logs must be at least "
            f"{JUSTIFICATION_LOG_MIN_BYTES} bytes (trivial files are not "
            f"behavior proof).",
            repo_root,
        )
    body = log_path.read_text(encoding="utf-8", errors="replace")
    declared_kinds = SOURCE_KIND_LINE_RE.findall(body)
    if not declared_kinds:
        return _refuse(
            f"--justification-log path {log_path} has no `- source-kind: <kind>` line; "
            f"add one so the log is identifiable as a behavior proof, matching the "
            f"`## Behavior Source` shape in charness-artifacts/cautilus/latest.md.",
            repo_root,
        )
    invalid = [kind for kind in declared_kinds if kind not in JUSTIFICATION_LOG_KINDS]
    if invalid or not any(kind in JUSTIFICATION_LOG_KINDS for kind in declared_kinds):
        return _refuse(
            f"--justification-log path {log_path} declares `source-kind: "
            f"{declared_kinds[0]}`; supported kinds are "
            f"{', '.join(JUSTIFICATION_LOG_KINDS)}.",
            repo_root,
        )
    chosen_kind = next(kind for kind in declared_kinds if kind in JUSTIFICATION_LOG_KINDS)

    if remaining and remaining[0] == "--":
        remaining = remaining[1:]
    cmd = [args.cautilus_bin, "evaluate", args.mode, *remaining]

    if args.dry_run:
        print(f"would run: {' '.join(cmd)}")
        return 0

    runs_dir = repo_root / ".cautilus" / "runs"
    runs_before = {entry.name for entry in runs_dir.iterdir()} if runs_dir.is_dir() else set()

    print(f"running: {' '.join(cmd)}", file=sys.stderr)
    completed = _run_forwarded_cautilus(args, cmd, repo_root)
    if isinstance(completed, int):
        return completed

    if completed.returncode == 0 and runs_dir.is_dir():
        new_runs = sorted(
            entry.name for entry in runs_dir.iterdir()
            if entry.is_dir() and entry.name not in runs_before
        )
        if new_runs:
            print(
                "\nRecord cautilus provenance: add the following block under "
                "`## Behavior Source` in charness-artifacts/cautilus/latest.md, "
                "or include it in the commit body that lands this run.",
                file=sys.stderr,
            )
            for run_name in new_runs:
                print(f"- source-ref: .cautilus/runs/{run_name}", file=sys.stderr)
                print(f"- source-kind: {chosen_kind}", file=sys.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
