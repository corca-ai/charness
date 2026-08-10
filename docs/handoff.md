# Charness Handoff

## Workflow Trigger

- No goal is running. The release is published and read back; do not re-run any
  release phase. Start from `## Next Session` Wave 1.
- **Push is held by operator decision until the backlog is closed.** Nine commits are
  unpushed; `git log --oneline origin/main..HEAD` lists them. One decision is owed
  before that plan can finish — see the `#572` circularity below.

## Current State

- 23 open issues. `#591` is FIXED this session and needs only its closeout floor;
  `#592`-`#594` were filed by the matrix slice and the review of its fix.
- **`#572` cannot close without a push, and push is held until issues close.** Its
  diagnostic is in unpushed `739a2a3e`, the cron runs on main, and the test passes
  locally so it cannot be reproduced here. Break the loop by choosing: push early for
  this one, close everything else and push with `#572` open, or redefine it as the
  rolling ticket its own newest comment proposes.
- The evidence-boundary crosswalk instance was RETIRED by operator ruling — see
  [the retirement record](../charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md);
  do not rebuild that matrix.
- `dup-ratchet` and `check-changed-line-mutation-coverage` are red and BOTH predate
  this session, whose own files are clear: the dup families sit in untouched files and
  were already red at `ba899083`, and the blocked mutation-pool files are owned by
  `739a2a3e`. Recount with `bash scripts/run-quality.sh`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

Three waves, in this order. Ordered by cost per close, not by topic: the expense is
the closeout floor per issue, so batch by classification and close several through one
carrier wherever the ledger allows.

1. **Wave 1 — closes needing no code change.** `#591` (fixed; floor only), then
   `#576`, `#580`, `#587`, `#546`, plus `#592` if its no-build decision holds. Every
   one already carries its measurement in an issue comment, so there is nothing new to
   investigate. This wave is also the first real exercise of the floors `#591` widened:
   past carriers were measured compliant, but no close has happened since the change.
2. **Wave 2 — small concrete bugs, 2-3 per carrier.** `#539`, `#581`, `#588`, `#528`,
   `#589`, `#542`. Real code plus the fresh-eye review each classification owes.
3. **Wave 3 — the rest.** Umbrellas `#582`-`#585` and their instances, plus `#586`,
   `#590`, `#593`, `#594`, `#550`, `#527`. An umbrella closes when its instances
   resolve or when a ruling retires it; making that call is the wave's first task.

`#586` is closable earlier than Wave 3 if wanted: all three of its candidate guards
were measured, the live one is built and gated, and its own remaining option is "rely
on bounded review", which is what the repo already does. The measurements are in the
[matrix spec](../charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md).

## Discuss

- `#576` has no chosen direction; a comment records why it is honest silence.
- The `Premise-residue:` seam reads markers and nothing writes them. If records do not
  start writing them the record channel stays empty.
- The matrix's `not_measured` names six gaps; two are worth a slice (the `commit-msg`
  sub-paths, and the `_missing_ledger_fields` asymmetry on `close-with-comment`).

## Continuation Capability

- **Read the exit code of the thing you ran, not the pipeline's.** `pytest …; echo $?;
  tail` reported green twice off `tail`'s exit; the real run had 19 failures.
- **The round that reads the REPAIRS finds a different class.** Eight for eight, twice
  more today — each time a round-1 repair had bought a smaller copy of its own defect.
- **When a floor widens, the surfaces that TELL authors what it wants are where the
  blockers are.** Both rounds of the `#591` fix found them there, not in the floors.
- **Measure the blast radius before widening a floor.** `#591` looked like an
  irreversible-boundary risk and measured 0 refusals across 87 historical carriers.
- **Adding a gate to the quality runner is four registrations:** the seeded harness
  stub, a timing verdict in
  [validator-timing-layers](./conventions/validator-timing-layers.md), `release_only`
  on any repo-copy test, and the surfaces entry. The suite names each one.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
- [Closeout floor matrix spec](../charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md)
