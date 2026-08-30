"""The release publish command surface.

Split from `publish_release_cli` when that module reached its length cap: the
argument contract is one concept -- what an operator may ask the publish helper
for, and the constraints argparse can refuse before any code runs -- and it is
what a reader consults to answer "which flags does a resume have to repeat".
Behavioral gates on those values (the sentinel refusal on `--bump-rationale`, the
critique binding) stay with the code that acts on them, in `publish_release_preflight`.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """The parser itself, so a caller can ask what the command surface OFFERS.

    Split from `parse_args` because the only way to test "this flag exists" was a
    substring search over this file's source, which stayed green with the flag
    deleted: `--close-issue` still occurs inside `--close-issue-repo` and in five
    help strings. A question about the command surface is answered by the surface.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root used to resolve the release adapter")
    parser.add_argument("--remote", default="origin", help="Git remote to push to (default: origin)")
    parser.add_argument("--title", help="Release title (defaults to the tag name)")
    parser.add_argument("--notes-file", type=Path, help="Path to a release notes file; omit to generate notes from commits")
    parser.add_argument("--critique-artifact", help="Path to the required release critique artifact (under charness-artifacts/critique/)")
    parser.add_argument("--critique-blocked", help="Host signal (>=20 chars) when the bounded fresh-eye critique was genuinely blocked by the host runtime; mutually exclusive with --critique-artifact")
    parser.add_argument("--close-issue", action="append", type=int, default=[], help="Issue number to close at release time; repeat for multiple")
    parser.add_argument("--close-issue-repo", help="Repository (owner/repo) hosting --close-issue numbers; defaults to current repo")
    parser.add_argument(
        "--close-issue-classification",
        # Keep in step with `issue_verify_closeout.CLASSIFICATIONS`: a value missing
        # here is refused by argparse before any code runs, i.e. unreachable.
        choices=("bug", "feature", "deferred-work", "question", "decision-needed", "consolidated"),
        help="Classification applied to every --close-issue number for the issue-owned draft validator",
    )
    parser.add_argument(
        "--close-issue-carrier-file",
        type=Path,
        help="Path to the closeout ledger validated before release and committed only after observer evidence exists",
    )
    parser.add_argument(
        "--close-issue-behavior", action="append", default=[],
        help='Behavioral-verdict line for a --close-issue, e.g. "Behavior #42: confirmed via fresh checkout install" '
        '(repeat per issue; single-issue shorthand "Behavior: <...>" also matches). Required rung-1 presence floor '
        "before a release closes a linked issue.",
    )
    parser.add_argument(
        "--close-issue-probe-record", action="append", default=[],
        help='Probe record for a --close-issue whose behavioral verdict claims a verification, e.g. '
        '"Probe record #42: charness-artifacts/probe/2026-08-18-x.md" (repeat per issue; single-issue '
        'shorthand "Probe record: <...>" also matches). A typed disposition -- local-only-by-contract, '
        "blocked-needs-operator, no-behavior-change -- satisfies it equally where no probe applies. "
        "Rung-1 floor: the named record must resolve `evaluated`, so a claim cannot outrun its "
        "measurement at a publish.",
    )
    parser.add_argument("--bump-rationale", help=(
        "Why THIS bump level, rendered into the release record's `## Bump Rationale` section. "
        "version-policy.md requires a stated rationale whenever the level is debatable. Repeat it "
        "on --resume: the resume rebuilds the payload from arguments, so omitting it publishes a "
        "record that says no rationale was recorded."))
    parser.add_argument("--execute", action="store_true", help="Execute the publish plan; without it the payload is printed dry-run")
    parser.add_argument("--prep-update-instructions", action="store_true", help="Emit version-agnostic update_instructions guidance + staleness report, then exit. Run this BEFORE the release critique so the adapter guard does not HOLD the publish; does not require a clean worktree or the critique gate.")
    parser.add_argument("--resume", action="store_true", help=(
        "Resume a partial publish (requires --publish-current). For a post-publication issue-closeout "
        "commit, repeat the exact original issue, classification, carrier, behavior, repo, critique, and "
        "--notes-file arguments. Omitting --notes-file on resume is refused when notes for the tag are drafted."))
    parser.add_argument("--claims-review-artifact", help=(
        "Repo-relative charness.release.claims-review.v4 JSON record for a marked prepared release; commit it "
        "with the review narrative it names, then use --resume --publish-current --claims-review-artifact <path>. "
        "A `pass` requires an `observer_distinctness` object naming one of separate-agent-context / separate-host / "
        "separate-operator plus its concrete signal and the review narrative; a host with no distinct observer "
        "records `verdict: unproven` with `kind: unproven` instead of a same-agent reread. Run plan_release_run.py "
        "at a prepared stop for the exact resume invocation."))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--publish-current", action="store_true", help="Publish the current packaging manifest version without bumping")
    group.add_argument("--part", choices=("patch", "minor", "major"), help="Semver component to bump before publishing")
    group.add_argument("--set-version", help="Explicit version string to set before publishing")
    return parser


def parse_args() -> argparse.Namespace:
    return build_parser().parse_args()
