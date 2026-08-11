# Charness Handoff

## Workflow Trigger

- **Invoke `charness:handoff`.** Read [recent lessons](../charness-artifacts/retro/recent-lessons.md)
  BEFORE acting, then `## Next Session`, then route each item through its owning skill.
- No goal is running. State the unpushed count from `git log --oneline origin/main..HEAD | wc -l`
  in your first reply. A push grant has been declined for several sessions — do not ask.

## Continuation Capability

- [Rulings retro](../charness-artifacts/retro/2026-08-11-six-rulings-and-the-declared-where-derivable-class.md)
  — the record behind the bullets below; read it before changing a proof surface.
- [Operating contract](./conventions/operating-contract.md) — Critique Discipline: a proof surface
  owes a second review round reading the REPAIRS.
- [Implementation discipline](./conventions/implementation-discipline.md#declared-where-derivable)
  — derive a fact before pinning it; regenerate a ratchet baseline, never hand-edit it.
- [Fresh-eye subagent review](../skills/shared/references/fresh-eye-subagent-review.md) — this repo
  contract IS the delegation request; a conditional "unless the user asked" is already satisfied.
- Run the REPO's own script, never `~/.agents/src/charness` — a second checkout with its own
  git, adapters, and artifacts.

## Current State

- [Six operator rulings](../charness-artifacts/spec/2026-08-11-six-operator-rulings.md) — status per
  ruling; ruling 1 (#598) is executed, both halves.
- #598 is not closable until the `issue` closeout floor runs; it sits inside the range in item 5.
- Two release-note lines owed at the next bump, a MAJOR: `check_title_slug_drift`, and the
  `domain_language_contract` removal — three parts, per [the gate](../scripts/check_documented_subcommands.py).
- New: [#604](https://github.com/corca-ai/charness/issues/604) (shipped parity defaults miss the
  bare scaffolded form) and [#605](https://github.com/corca-ai/charness/issues/605) (a trim-back
  loop whose guardian tests no longer reach it; unproven, deliberately not deleted).
- #582-#585 carry their own status and the class remains — do not close them.
- [Deferred decisions](./deferred-decisions.md) — D53's reopen trigger has three clauses; only the
  middle one is in-repo observable, with nothing watching for it.
- Re-take gate and issue counts, do not inherit them:
  [quality posture](../charness-artifacts/quality/latest.md), `gh issue list --state open`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **Write the recent-lessons selection spec** — the operator's design is in this session's
   discussion and has NO artifact yet; that absence is why
   [the thesis](../charness-artifacts/spec/2026-08-11-harness-improvement-thesis.md) is the wrong
   pointer for it. Scored ledger, blinded slots, two exits (archive down, graduate up).
2. **Round-2 review of the handoff ownership gate** —
   [round-1 findings](../charness-artifacts/critique/2026-08-12-handoff-bullet-ownership-critique.md);
   the repaired surface has not been read by a fresh context.
3. [Rulings 2, 3, 5, 6](../charness-artifacts/spec/2026-08-11-six-operator-rulings.md) — do not
   re-litigate; treat their sizing as estimates. Ruling 6 is the only schema change and the largest.
4. **#587 — edit, do not close.** Mapper is `tests_referencing_paths` in
   [suggest_mutation_coverage_command.py](../scripts/suggest_mutation_coverage_command.py); read the
   issue body first.
5. **Waves 2-3.** #539 #581 #588 #528 #589 #542, then #586 #590 #593-#597 #599 #550 #527 #546.

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
