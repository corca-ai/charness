# Release Critique — charness v8.13.0 (minor)

- **Kind**: `charness.release-critique` (v1)
- **Prepared for**: v8.13.0-release
- **Scope**: `8885601c3..5c1a1b06e` — #870 train metrics, #871 goal re-inject
  hook, #872 status report template, #873 root CLI split, #874 import-env
  fix + entry coverage E1-E5, release-battery hardening; umbrellas #843/#859.
- **Reviewers**: one fresh-eye reviewer (read-only shared checkout, no repo
  mutation), delegated by the parent; verdict below is the reviewer's own.
- **Lane evidence**: release lane green, 89 passed, 0 failed
  (`./scripts/run-quality.sh --full --read-only --release`), plus a second
  89/0 from the pre-push hook on the same HEAD.

Fresh-eye satisfaction: parent-delegated angle reviewer, findings received.

## Verdict

GO, conditional on standard pre-publish gates (both now met: battery green
on the release HEAD; stray `charness,cover` annotate artifact confirmed
derived-only and removed, worktree clean).

## Bump Honesty

Minor is correct. Real new operator-facing capabilities, all additive:
`train --stats/--window`, `task report`, `task wait` plus
`task run --detach/--rules-file/--grant-writable`, `hooks status`, the goal
re-inject SessionStart hook, and command-time guards via registry. No
breaking invocation change: the diff adds subcommands/flags only. Closest
refinements are exit-code granularity (train land/land-prefix/refused/requeue
codes) and a `CharnessError` replacing an argparse-arity error for bare
`train`. Not patch (feat-heavy), not major (no migration, no renames).

## Safety / Contract Risks (reviewed, none blocking)

- Split root CLI blast radius: the entry is a thin shim delegating to
  `scripts/cli/*`, with verbatim fallback copies byte-checked by the sync
  test. Mitigated by the sync test plus the entry-bootstrap seam.
- `repo_root_from_script` no longer configures the runtime on package
  import (intentional #874 fix); fail-safe toward historic configure.
  Covered by the package-import regression test.
- Dry-run premise refusals (`premise-blocked` instead of always `planned`)
  are the documented fix; callers assuming dry-run always plans should note it.
- New hooks default disabled with override-reason, friction log, and
  fail-open local extensions.
- Data/migration: none required. Train stats append fail-open; missing
  files read as empty. New receipt keys are additive.

## Reason Not To Release

None on contract. Pre-publish hygiene items from the reviewer are both
closed above.
