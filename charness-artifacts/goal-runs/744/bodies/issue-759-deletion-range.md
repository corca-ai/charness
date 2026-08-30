## Situation

The file-backed critique path (`skills/public/critique/scripts/run_review.py`) is
the canonical way to obtain a bounded fresh-eye review of a change range. Running
it against a range that DELETES files is impossible: the two ways of declaring the
reviewed input contradict each other, and every combination is refused before a
reviewer starts.

## Observed problem

With `--range BASE..HEAD` the packet requires the declared reviewed paths to match
the changed-ref path set EXACTLY. `git diff --name-only` includes deleted paths, so
the natural manifest contains them — and the packet then refuses:

```
status: refused
reason_code: null-content-hash
error: reviewed path `charness-artifacts/probe/2026-08-19-real-host-proof-version-refusal.md`
```

Excluding deletions (`--diff-filter=d`) removes that refusal and produces the
other one:

```
status: refused
reason_code: changed-ref-path-mismatch
error: declared reviewed paths do not exactly match the changed-ref path set
```

Both refusals are individually correct. A deleted path has no content to hash, and
a declared set that omits part of the range is genuinely not the range. Together
they mean a range containing any deletion has no valid declaration.

## Evidence

- Charness source at `e3d7aeef0`; the reviewed range was ten commits carrying six
  file deletions.
- `--range` + full `git diff --name-only` manifest (98 paths) → `null-content-hash`.
- `--range` + `--diff-filter=d` manifest (92 paths) → `changed-ref-path-mismatch`.
- `--prepared-for` with the same 92-path manifest and NO `--range` → `dry-run-ready`.
  That is the workaround actually used, and it is a different input contract: it
  drops the changed-ref binding entirely rather than reconciling it.

## Impact

A refactor or removal slice — exactly the change class where a fresh-eye review is
most valuable, because it is where something load-bearing is most likely to be
dropped — cannot be reviewed through the range-bound path. The available
workaround silently weakens the evidence: the packet is no longer bound to a
commit range, so the review's reviewed-input identity does not prove which range
was read. A reviewer verdict recorded that way cannot be re-derived from the range
later.

This surfaced while reviewing a release slice, so it also blocks the release
critique boundary for any release that removes a file.

## Expected behavior

A range with deletions is reviewable, with the reviewed-input identity still bound
to the range. The deleted paths need to participate in that identity as deletions
rather than as unhashable content — their pre-image and the fact of removal are
what a reviewer needs, and both are available from the range.

## Non-claims

- Neither refusal is wrong on its own; this is about their intersection.
- This does not claim the `--prepared-for` path is broken. It works; it answers a
  weaker question.
- No fix shape is prescribed. Whether the identity should carry a deletion marker,
  the pre-image hash, or a typed absent-content entry is the owner's call.
- Related but distinct: #731 covers bounded-review friction and partial worker
  progress broadly; this is one specific unreviewable input class.

AI-provenance: agent-authored from a Charness release-review session, at the
operator's direction.

---

<!-- charness-work-item-key: issue-759-deletion-range -->
# Work Item #759 — Keep deletions in bounded-review identity

## Purpose and premise

Re-prove the current deletion-range implementation and its carrier before adding code. A passing published premise produces a no-code closeout; a failed premise stays in this Work Item.

## Acceptance and proof

Added, modified, and deleted ranges remain reviewable and identity-bound. A deliberate deletion omission or stale digest fails. The resolution critique and closeout comment bind the exact behavior.

## Non-claims

No exhaustive consumer Git-topology support and no inference from provider state alone.
