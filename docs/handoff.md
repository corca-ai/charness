# Charness Handoff

## Workflow Trigger

- No goal is running. The release is published and read back; do not re-run any
  release phase. Start from `## Next Session` item 0.
- Two commits are UNPUSHED (`93b2e1dc`, `739a2a3e`). Push needs its own grant.

## Current State

- 20 open issues. `#514`/`#515`/`#518` closed `NOT_PLANNED` on 2026-08-10 after the
  evidence-boundary crosswalk instance was RETIRED by operator ruling — see
  [the retirement record](../charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md);
  do not rebuild that matrix.
- Filed 2026-08-10: `#588` and `#589` (the carved-out residuals of those closes),
  and `#590` (the mutation workflow reported a JS symptom for a Python failure).
- `#572` is the one open red. `#590` diagnosed it and REPAIRED THE REPORTING at
  `739a2a3e`; the failure itself is untouched, so the lane is still red.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

0. **Read the newest `#572` comment, then fix the leaf cause.** Cheapest item,
   highest payoff: `test_mutating_a_source_file_drops_its_stale_bytecode` fails on
   the runner and passes locally, exiting the cosmic-ray baseline and redding the
   lane. WHY is unknown — no bytecode-suppressing setting exists in the workflows,
   the pytest config, the shared conftest, the cosmic-ray config, or the runner
   script; all five were checked. `739a2a3e`
   makes the test report the child's exit code, env, and directory contents, so the
   next cron run (`17 */12 * * *`) names it. Read that, then fix.
1. **Build the closeout floor x classification matrix** — decided, spec ready at
   [the spec](../charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md).
   All three mechanizable `#586` guards measured ~0 findings; this one starts from a
   live one (`consolidated` skips four of six close floors and only a non-blocking
   advisory says so). The validator MUST be behavioral, not grep — that constraint
   IS the slice. Two bounded rounds owed.
2. **`#590` left a gap, recorded on the issue:** the workflow's inline script body
   has ZERO automated coverage — how a temporal-dead-zone error survived round 1.
   Worth its own slice; item 0's cron run is the only current check on it.
3. `#546` has a refuted option, not a fix — built, reviewed HOLD, measured
   defective, reverted; its comment carries the alternative.

## Discuss

- `#576` has no chosen direction; a comment records why it is honest silence.
- `#587` and `#580` were measured on 2026-08-10 and both had a false premise; both
  are retitled with the measurement on the issue. `#580` no longer blocks anything.
  `#587` now asks ONE thing — what its iteration-#2 false blocker actually was —
  answerable only from the original session's record, not this tree.
- The `Premise-residue:` seam reads markers and nothing writes them; exactly one
  exists. If records do not start writing them the record channel stays empty.

## Continuation Capability

- **Read the source, not the summary.** Burned twice on 2026-08-10: an issue body
  read without its latest comment (the signal had already moved), and a REST API
  `conclusion: success` for a step that exited 1 (`continue-on-error` masks it; only
  `outcome` carries the truth, and only inside the workflow).
- **The round that reads the REPAIRS finds a different class.** Six for six. On
  2026-08-10 round 2 caught a blocker the repair itself introduced, whose failure
  mode was worse than the defect being fixed.
- **Run the module that exercises the changed function**, not the ones that sound
  related. Five tests began spawning a real external binary and the run that would
  have shown it was skipped by assumption.
- **The cheapest disconfirming probe, BEFORE building.** It ran on time three times
  on 2026-08-10 and refuted three planned builds — a guard with no findings, a
  remedy for a defect that did not exist, and a blocker that no longer blocked.
- **Let the floors refuse your own work.** Several fired on this session's own
  mutations, including a gate that rejected a code comment for containing the word
  `closed`. The gate was right.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
