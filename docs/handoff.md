# Charness Handoff

## Workflow Trigger

- **Read [recent lessons](../charness-artifacts/retro/recent-lessons.md) BEFORE acting.** A
  headless run proved this line works, and that the digest's 4 trap slots dropped the two
  sharpest lessons — THIS file and the spec artifact are the channel that carries.
- No goal is running. Unpushed commits: `git log --oneline origin/main..HEAD` (16). The
  operator was asked for a push grant several times last session and steered elsewhere
  each time — state the count, do not open with the ask. Then `## Next Session`.

## Current State

- **24 open issues; closing GENERATES issues** (Aug 7-10: created 60, closed 42).
- **`#572` CLOSED as `consolidated` into `#590`.** The `ed90c1f3` green cron is NOT
  recovery; it predates `#590`'s diagnostic `739a2a3e`.
- **`#582`-`#585` CARRY their own status** (per-member outcome + disposition in each
  body). **CLASS REMAINS, 4/4.** Do not close them.
- **Gate 90/0, 0 UNPROVEN at `a24b0155`.** A handoff "gate green" line goes stale the
  moment a later commit adds an unowned path: `2c95898b` committed a `.patch` with no
  owning surface and blocked BOTH bundle-readiness gates for four commits while this file
  advertised 89/0. Re-take the baseline; do not inherit the claim.
- Filed `#596` (probe-pin tax; `#536` closed COMPLETED), `#597`
  (`check_quality_tool_fixtures` passes on an empty set, unwired), `#598` (word-preference
  gate + a five-week-unactioned audit), `#599` (no "what reads this?").
- **D53's reopen trigger is NOT in-repo observable** ([deferred](./deferred-decisions.md)).

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **The recorded sweep as a DYNAMIC WORKFLOW** (operator-directed), one agent per
   candidate, each REQUIRED to emit its consumer grep before proposing. **No counterweight
   ran on it — triage first.** Two of its five items are RE-keys, not deletions.
2. **`state-selection.md` is waived by `classTag` for a gap the allowlist now owns.**
   Forced only by `judge_from_user_request`, covered by no scenario — the twin of the
   `workflow-trigger.md` case `a24b0155` moved. Pre-existing; touches a Slice-8 record.
3. **`#546` phase 2 — the adapter `conditional:` marker.**
4. **`#587` — edit, do not close.** The mapper is
   `suggest_mutation_coverage_command.tests_referencing_paths:85-87`.
5. **Waves 2-3.** `#539` `#581` `#588` `#528` `#589` `#542`, then `#586` `#590`
   `#593`-`#599` `#550` `#527`. Umbrellas wait on their own work.

## Discuss

- **Does a pattern-match decide what someone MEANT?** A declared route replaces it, as
  `--intent` replaced `should_fire_chunker`. Suspects: `setup_skill_routing_lib`'s
  semantic-completeness regex (ships to consumers), `chunked_routing_parser`,
  `classify_push_diff_lib`. Form validators are NOT in this class.
- **The harness-improvement thesis has no artifact.** Narrowed to two items: the lessons
  digest's slot policy, and the autonomy permission posture. Decide whether it gets a home.

## Continuation Capability

- **A removal proposal without its consumer grep is malformed.** Seven wrong proposals in
  one session, each refuted by one grep. Put the grep and its result IN the proposal.
- **Budget hit? Rule #1: delete the unnecessary sentences, then send prose to a link.** Not
  compress the wording. A link line says what it CONTAINS (awiki `link_only_lines`), never
  why to open it. Never argue for an untaxed section — it becomes a dumping ground.
- **The round that reads the REPAIRS is the one that catches you.** `a24b0155`'s round-1
  fix removed a waiver channel and left three sentences describing it; round 2 found the
  contradiction its own repair created. Reviewers unprompted; round 2 is not optional.
- **Autonomy needs `--dangerously-skip-permissions`, which the operator already uses.**
  Under `acceptEdits` a headless run cannot reach its own stop gate — the contract demands
  gates, the mode blocks `python3`. A precondition, NOT a harness defect; do not file it.
- **Six of six deletions were refuted — then one refutation was itself refuted.** Proving
  the proposer's REASON wrong is not proving the surface load-bearing; only the second
  blocks a deletion. Name the consumer grep in both directions.
- **Closing an issue can delete a ruling — or rot its pointer.** `#536` closed COMPLETED
  while the cost it tracked survived. A green ratchet can likewise be the record of paying
  its own tax ([dup-review.json](../charness-artifacts/quality/dup-review.json)).

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Deferred decisions](./deferred-decisions.md) — D53, D54, D55 landed this session.
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
- [Closeout floor matrix spec](../charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md)
- [2026-08-11 session retro](../charness-artifacts/retro/2026-08-11-session-retro.md) — this session's waste, critical decisions, north-star alignment, sibling scan, and the Engelbart/Klein counterfactuals.
- [Umbrella class disposition plan](../charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md) — per-member dispositions for `#582`-`#585`, the deletable-surfaces sweep with its consumer greps, the pickup-deletion ruling and its scope, and the `# Observation run 2026-08-11` measurement.
