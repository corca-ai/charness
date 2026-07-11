# Round 3 Slices A/B Code Critique

Execution: bounded fresh-eye code critique over the Slice A/B working-tree diff.
Fresh-Eye Satisfaction: parent-delegated. Parent spawned a separate reviewer
context and verified worktree/index integrity with
`skills/shared/scripts/reviewer_boundary_fingerprint.py`.
Packet Consumed: `charness-artifacts/critique/2026-07-12-round3-slices-a-b-packet.md`.
Target: `references/code-critique.md`.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: packet requested `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`; live spawn used host-default reviewer fields.
- Host exposure state: host-defaulted
- Application state: host applied a separate default reviewer context; no provider-level model-field confirmation exposed.

## Boundary Ownership

- Verdict: owned-correctly.

Producer ownership stays in `scripts/mutation_coverage_producer.py`: it records
the exact coverage source facts it produced. Consumer behavior stays in
`scripts/check_changed_line_mutation_coverage.py`: the emitted command invokes
that consumer with the producer facts instead of duplicating changed-line
classification logic.

## Change

Slice A moves the SLOC inventory refresh command on `quality-inventory-artifacts`
from `verify_commands` to `sync_commands`, so tracked inventory output is
discovered before verification. Slice B adds exact producer payload fields and a
copyable consumer command for changed-line mutation coverage.

## Capability At Stake

Operators need the lock boundary to fail before expensive verification when a
tracked sync writer changes the tree, and they need a post-commit coverage
consumer command that reuses the exact producer coverage source instead of
recollecting or guessing a base.

## Findings

1. SLOC reclassification is correct for the narrow claim and should not be
   described as an exhaustive all-writer fix.
2. The first consumer command shape had a copy/paste ambiguity. The command now
   uses the producer/consumer install-root script path while `--repo-root` remains
   the target repo, so it is copyable from any current directory and can inspect
   a separate target checkout.
3. The no-recollection proof was strengthened after review: the roundtrip records
   coverage JSON bytes and `st_mtime_ns` before subprocess execution and asserts
   both unchanged after the consumer succeeds.
4. Wrong/stale marker rejection is not duplicated here; the changed-line
   consumer suite already owns
   `test_require_fresh_coverage_skips_when_marker_mismatched`.

## Counterweight Triage

- Act Before Ship: resolved — cwd-proof command model and direct no-recollection
  proof were added before commit.
- Bundle Anyway: SLOC sync reclassification, producer payload fields,
  exact-base/coverage command parsing, and plugin mirror sync.
- Over-Worry: adding a generic all-writer detector or claiming #436 closure.
- Valid but Defer: exhaustive tracked-writer audit remains part of #436 follow-up,
  not this patch release claim.

## Deliberately Not Doing

This slice does not close #436, does not audit every tracked writer, and does not
add a new blocking floor or public sync-only CLI.

## Next Move

Commit Slice A/B with the proof artifacts, then continue to full-bundle quality
and release critique before publishing v0.66.4.
