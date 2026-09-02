"""Argument surface for the changed-line mutation-coverage gate.

Split out of `check_changed_line_mutation_coverage.py` when that file crossed its
length cap (S6b-1). The CLI is a cohesive unit: every flag here is an operator
choice about SCOPE or TRUST -- which range, which coverage source, how much to
believe it -- and the parse-time refusal of an uninstrumentable `--test-command`
belongs beside the flag it refuses, not in the verdict logic. The gate re-exports
`parse_args`, so callers and tests keep binding it at the old address.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.mutation.mutation_sampling_lib import (  # noqa: E402
    INSTRUMENTABLE_COMMAND_REFUSAL,
    is_instrumentable_pytest_command,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reproduce the mutation gate's blocking changed-line signal locally.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--base-sha", default=None, help="Base SHA; defaults to $MUTATION_BASE_SHA.")
    parser.add_argument("--head-sha", default=None, help="Head SHA; defaults to $MUTATION_HEAD_SHA, else HEAD.")
    parser.add_argument("--config", type=Path, default=Path("cosmic-ray.toml"))
    parser.add_argument("--coverage-json", type=Path, default=Path("reports/mutation/test-coverage.json"))
    parser.add_argument(
        "--test-command",
        default=None,
        help=(
            "Command to instrument under coverage for the probe, replacing the "
            "`test-command` literal in --config. Where that literal is bare serial "
            "pytest, a standing xdist runner run through this flag proves the same "
            "scope far cheaper; pass the runner by the path it has in THIS repo "
            "(charness ships one as `run_standing_pytest.py` beside this script). "
            "Accepted shapes are decided by "
            "`mutation_sampling_lib.classify_instrumentable_command`, the single "
            "policy both coverage builders read. Does NOT change what cosmic-ray "
            "runs per mutant -- that still reads --config."
        ),
    )
    parser.add_argument(
        "--reuse-coverage",
        action="store_true",
        help="Reuse an existing coverage JSON instead of running the (slow) gate probe.",
    )
    parser.add_argument(
        "--skip-if-no-coverage",
        action="store_true",
        help=(
            "When no coverage JSON exists, skip non-blocking (exit 3: ran, established nothing) instead of "
            "running the slow probe. The release wiring uses this so the "
            "teeth stay cheap; the coverage source is produced by the full/closeout run "
            "and reused here."
        ),
    )
    parser.add_argument(
        "--require-fresh-coverage",
        action="store_true",
        help=(
            "Only trust a coverage JSON whose sibling marker "
            "`<coverage-json>.changed-line.fingerprint` identifies the changed-line "
            "producer and matches the current changed-pool content fingerprint; otherwise skip "
            "non-blocking. The release wiring sets this so a STALE or foreign coverage source "
            "(produced before the changed lines existed) cannot raise false 'uncovered "
            "changed line' positives. The closeout producer writes the marker when it "
            "refreshes coverage."
        ),
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help=(
            "Escape hatch: proceed even when mutation-pool files have uncommitted "
            "worktree/index changes that base..HEAD cannot see. The run then costs the "
            "full probe and its verdict is ADVISORY ONLY — the payload records "
            "`dirty_pool_unverified: true` plus the offending files, so a clean result "
            "cannot be cited as changed-line proof for them."
        ),
    )
    parser.add_argument(
        "--limit-to-file",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "Repo-relative mutation-pool path to analyze; repeatable. Narrows the "
            "BLOCKING set to these files only. The incremental release producer sets "
            "this because its coverage was collected from a focused test subset: focused "
            "coverage is a SUBSET of full coverage, so an unmapped file's changed lines "
            "would read as uncovered when the full suite covers them. Every changed pool "
            "file outside the limit is reported as `unanalyzed_changed_pool_files` and "
            "named on stderr, so a clean verdict here can never be read as covering them."
        ),
    )
    parser.add_argument(
        "--write-fresh-marker",
        action="store_true",
        help=(
            "Producer mode: after coverage exists for the analyzed range, write the "
            "sibling `<coverage-json>.changed-line.fingerprint` marker recording the "
            "changed-line producer and changed-pool content fingerprint so the release consumer "
            "(`--require-fresh-coverage`) "
            "can trust the coverage."
        ),
    )
    parser.add_argument(
        "--collect-test-contexts",
        action="store_true",
        help=(
            "Collect per-test `dynamic_context` data in the probe and export it into "
            "the coverage JSON. OFF by default, and this gate never reads it: the "
            "changed-line verdict consumes `executed_lines`/`missing_lines` only, via "
            "`load_file_statement_lines`. The single reader of the `contexts` block is "
            "`load_line_contexts`, used by the cosmic-ray sampler "
            "(`scripts/mutation/sample_mutation_files.py`), which builds its own corpus and does "
            "not depend on this flag. Pass it only to hand-build a context-bearing "
            "corpus for that sampler. Measured cost of leaving it on (#696): the same "
            "coverage data exported to 8.22 GB instead of 12.26 MB (671x), taking 36.5s "
            "and 20.44 GiB of peak RSS to load instead of 0.13s and 0.06 GiB."
        ),
    )
    args = parser.parse_args()
    if args.test_command is not None and not is_instrumentable_pytest_command(args.test_command):
        # Refused HERE rather than inside the probe: an unusable --test-command
        # discovered after coverage setup costs a partial run and reads as a
        # coverage failure instead of an argument error.
        parser.error(
            f"--test-command is not an instrumentable pytest command: "
            f"{args.test_command!r}; {INSTRUMENTABLE_COMMAND_REFUSAL}"
        )
    return args
