#!/usr/bin/env python3

"""Repo-owned wrapper for `cautilus eval test/evaluate`.

Enforces the planner-consult contract from
`skills/public/quality/references/cautilus-on-demand.md`: every cautilus eval
invocation runs `scripts/plan_cautilus_proof.py` first and refuses with exit
code 2 when the planner says the call is not warranted.

Refuses when no `--justification-log` is provided AND the planner returns
either `next_action: "none"` or `must_ask_before_running: true`. The
justification-log path is the operator-supplied override: it must exist as a
file of at least 32 bytes containing one of the behavior-source markers
(`failing-prompt`, `transcript`, `operator-log`, `issue-log`, `regression-log`)
that match the `## Behavior Source` shape in
`charness-artifacts/cautilus/latest.md`. Otherwise forwards to `cautilus eval
<mode>` with any extra args after `--`.
"""

from __future__ import annotations

import argparse
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

VALID_MODES = ("test", "evaluate")
CANONICAL_REFERENCE_PATH = "skills/public/quality/references/cautilus-on-demand.md"
PLUGIN_REFERENCE_PATH = "skills/quality/references/cautilus-on-demand.md"
JUSTIFICATION_LOG_MIN_BYTES = 32
JUSTIFICATION_LOG_MARKERS = (
    "failing-prompt",
    "transcript",
    "operator-log",
    "issue-log",
    "regression-log",
)


def parse_args(argv: list[str] | None = None) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Repo-owned wrapper for cautilus eval test/evaluate.",
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--mode",
        required=True,
        choices=VALID_MODES,
        help="cautilus eval subcommand to invoke",
    )
    parser.add_argument(
        "--justification-log",
        type=Path,
        default=None,
        help="Path to the failing prompt/transcript/operator-log that motivates this run",
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


def main(argv: list[str] | None = None) -> int:
    args, remaining = parse_args(argv)
    repo_root = args.repo_root.resolve()

    if args.paths is not None:
        changed_paths = [normalize_repo_path(path) for path in args.paths]
    else:
        changed_paths = collect_changed_paths(repo_root)
    plan = plan_cautilus_proof(repo_root, changed_paths)

    if args.justification_log is None:
        if plan["next_action"] == "none":
            return _refuse(
                f"planner returned next_action=\"none\" "
                f"(status={plan['status']}, run_mode={plan['run_mode']}); "
                "deterministic gates own this closeout. To override with an "
                "explicit log-backed behavior proof request, pass "
                "--justification-log <path-to-failing-log>.",
                repo_root,
            )
        if plan["must_ask_before_running"]:
            return _refuse(
                "planner reports must_ask_before_running=true and no "
                "--justification-log was provided; pass --justification-log "
                "<path-to-failing-log>.",
                repo_root,
            )
    else:
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
        body = log_path.read_text(encoding="utf-8", errors="replace").lower()
        if not any(marker in body for marker in JUSTIFICATION_LOG_MARKERS):
            return _refuse(
                f"--justification-log path {log_path} does not contain any of "
                f"the behavior-source markers ({', '.join(JUSTIFICATION_LOG_MARKERS)}); "
                f"add one (e.g. `source-kind: failing-prompt`) so the log is "
                f"identifiable as a behavior proof, matching the "
                f"`## Behavior Source` shape in charness-artifacts/cautilus/latest.md.",
                repo_root,
            )

    if remaining and remaining[0] == "--":
        remaining = remaining[1:]
    cmd = [args.cautilus_bin, "eval", args.mode, *remaining]

    if args.dry_run:
        print(f"would run: {' '.join(cmd)}")
        return 0

    print(f"running: {' '.join(cmd)}", file=sys.stderr)
    try:
        completed = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        return _refuse(
            f"cautilus binary `{args.cautilus_bin}` not on PATH; install cautilus "
            "or pass --cautilus-bin <path>.",
            repo_root,
        )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
