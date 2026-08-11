# Charness Handoff

## Workflow Trigger

- **Invoke `charness:handoff`.** Read [recent lessons](../charness-artifacts/retro/recent-lessons.md)
  BEFORE acting, then `## Next Session`, then route each item through its owning skill.
- No goal is running. State the unpushed count from `git log --oneline origin/main..HEAD | wc -l`
  in your first reply. A push grant has been declined for several sessions — do not ask.

## Continuation Capability

- [Operating contract](./conventions/operating-contract.md) — Critique Discipline: a proof surface
  owes a second review round reading the REPAIRS.
- [Removal and baseline discipline](./conventions/implementation-discipline.md#removal-and-baseline-discipline)
  — regenerate a ratchet baseline; a removal grep must cover every consumer AND every spelling.
- [Declared where derivable](./conventions/implementation-discipline.md#declared-where-derivable)
  — derive a fact before pinning it. Form validators are NOT in this class.
- [Fresh-eye subagent review](../skills/shared/references/fresh-eye-subagent-review.md) — rung 1:
  this repo's delegation contract means spawn immediately for the named reviewer scopes.
- Run the REPO's own script, never `~/.agents/src/charness` — a second checkout with its own
  git, adapters, and artifacts. Incident record:
  [rulings retro](../charness-artifacts/retro/2026-08-11-six-rulings-and-the-declared-where-derivable-class.md).

## Current State

- [Six operator rulings](../charness-artifacts/spec/2026-08-11-six-operator-rulings.md) — six rulings
  with an execution status line each; ruling 1 is #598 and reads executed.
- [Issue #598](https://github.com/corca-ai/charness/issues/598) — ruling 1's issue; the `issue`
  closeout floor has not run on it, and no entry below schedules it.
- [check_documented_subcommands](../scripts/check_documented_subcommands.py) — the gate whose
  docstring holds the three limits on the word "replaces" that a release note must carry.
- [Issue #604](https://github.com/corca-ai/charness/issues/604) — shipped parity defaults against the
  bare scaffolded runner form; fails red to green.
- [Issue #605](https://github.com/corca-ai/charness/issues/605) — a trim-back loop its guardian tests
  no longer reach; unproven and deliberately undeleted.
- [Umbrella disposition plan](../charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md)
  — per-section execution status for #582-#585, each carrying its own class verdict.
- [Deferred decisions](./deferred-decisions.md) — D53's reopen trigger and its three clauses, one of
  them in-repo observable with nothing watching for it.
- [Quality posture](../charness-artifacts/quality/latest.md) — the last recorded gate run. Issue
  counts come from `gh issue list --state open`; the block below is a frozen capture whose
  `issue_scope` predates the issues above.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. [Harness-improvement thesis](../charness-artifacts/spec/2026-08-11-harness-improvement-thesis.md)
   — the digest's slot-policy defect and two unimplemented proposals. The operator's selection
   design is NOT in it; that design has no artifact yet.
2. [Ownership gate critique](../charness-artifacts/critique/2026-08-12-handoff-bullet-ownership-critique.md)
   — three review rounds on the handoff ownership gate and each disposition. The narrowing those
   rounds motivated is itself unreviewed.
3. [Six operator rulings](../charness-artifacts/spec/2026-08-11-six-operator-rulings.md) — rulings
   2, 3, 5, and 6 carry `not executed`; ruling 6 is the only schema change.
4. [suggest_mutation_coverage_command](../scripts/suggest_mutation_coverage_command.py) — holds
   `tests_referencing_paths`, the mapper [#587](https://github.com/corca-ai/charness/issues/587)
   describes; that issue's body governs over any in-repo mention.
5. [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md) — a read of the
   open backlog: #539 #581 #588 #528 #589 #542, then #586 #590 #593-#597 #599 #550 #527 #546.

## Discuss

- **Does a pattern-match decide what someone MEANT?** `--intent` replaced `should_fire_chunker`;
  the same shape survives in `setup_skill_routing_lib`'s semantic-completeness regex (ships to
  consumers), `chunked_routing_parser`, `classify_push_diff_lib`. Form validators are NOT in this class.
- **Should a consumer-facing capability be deletable without a portable replacement?** Ruling 1
  removed one that shipped in the quality package. Is a release note the standing answer?

## References

- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Design north star](./design-north-star.md)
- [Umbrella class disposition plan](../charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md)
- [Validator timing layers](./conventions/validator-timing-layers.md)
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
