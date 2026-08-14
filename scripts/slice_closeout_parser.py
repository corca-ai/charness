#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def build_parser(*, repo_root: Path, surfaces_path: Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument("--surfaces-path", type=Path, default=surfaces_path)
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to current git diff.")
    parser.add_argument(
        "--base",
        nargs="?",
        const="auto",
        default=None,
        help=(
            "Collect changed paths from the committed merge-base(<ref>, HEAD)..HEAD range "
            "in addition to the working-tree diff, so a post-commit closeout covers the "
            "bundle without a manual --paths list. Bare --base auto-detects origin/main — "
            "the same range anchor the changed-line mutation gate uses. Mutually exclusive "
            "with --paths; without --base the working-tree default is unchanged. Note: "
            "--produce-mutation-coverage always stamps its freshness fingerprint over the "
            "resolved campaign base, including an explicit non-origin/main ref."
        ),
    )
    parser.add_argument("--plan-only", action="store_true", help="Print obligations without executing commands.")
    parser.add_argument("--skip-sync", action="store_true")
    parser.add_argument("--skip-verify", action="store_true")
    parser.add_argument("--skip-broad-pytest", action="store_true", help="Run deterministic checks but skip broad pytest for pre-lock rehearsal.")
    parser.add_argument("--verification-lock", action="store_true", help="Acknowledge that the mutation set is locked before broad pytest runs.")
    parser.add_argument(
        "--refresh-broad-pytest-proof",
        action="store_true",
        help="Rerun broad pytest even when a cached verification-lock proof exists or was invalidated.",
    )
    parser.add_argument(
        "--produce-mutation-coverage",
        action="store_true",
        help=(
            "Emit reports/mutation/test-coverage.json plus a freshness fingerprint "
            "marker for the pre-push changed-line gate. By default this instruments "
            "the verification-lock broad pytest. With --mutation-coverage-command, "
            "the broad pytest proof stays on the normal closeout/cache path and the "
            "explicit command is instrumented separately. Requires --verification-lock."
        ),
    )
    parser.add_argument(
        "--mutation-coverage-command",
        help=(
            "Explicit pytest command to instrument for the changed-line mutation "
            "coverage producer, e.g. a focused test file or nodeid set. Requires "
            "--produce-mutation-coverage and --verification-lock."
        ),
    )
    parser.add_argument(
        "--mutation-coverage-extra-pytest-target",
        action="append",
        default=[],
        help=(
            "Additional pytest path or nodeid appended to the broad coverage producer "
            "without shell-chaining commands. Requires --produce-mutation-coverage and "
            "cannot be combined with --mutation-coverage-command."
        ),
    )
    parser.add_argument(
        "--ack-cautilus-skill-review",
        action="store_true",
        help=(
            "Acknowledge that public-skill dogfood/scenario review follow-ups from the Cautilus planner "
            "were inspected and the scenario-registry decision was recorded."
        ),
    )
    parser.add_argument(
        "--allow-unmatched",
        action="store_true",
        help="Proceed even when changed files are not covered by the surfaces manifest.",
    )
    parser.add_argument(
        "--predict-commit",
        action="store_true",
        help="Run the same staged-path pre-commit command plan consumed by .githooks/pre-commit.",
    )
    return parser
