# Proposed Goal Run Child Graph

Status: draft — no GitHub mutation authorized
Goal: [issue-native backlog closeout](../../../../goals/2026-08-26-adversarial-priority-backlog-closeout.md)

## System-Change Children

| Key | Proposed issue disposition | Capability | Depends on |
| --- | --- | --- | --- |
| `goal-binding-v1` | create after approval | [Freeze a full Goal Draft and validate Goal Binding V1](./goal-binding-v1.md) | none |
| `goal-run-provider` | rewrite/reuse #726 | [Provide exact Goal Run graph operations and guarded close](./goal-run-provider.md) | none for provider primitives; consumes V1 contract for integration |
| `achieve-orchestration` | rewrite/reuse #727 | [Orchestrate research through `/goal #N` pickup](./achieve-orchestration.md) | `goal-binding-v1`, `goal-run-provider` |
| `goal-evidence-lineage` | create after approval | [Cut proof/evidence consumers to frozen-draft and Goal Run identity](./goal-consumer-cutover.md) | `goal-binding-v1`, `goal-run-provider`, `achieve-orchestration` |
| `dogfood-724-establishment` | rewrite/reuse #725 | [Bootstrap, then prove #724 as the first Goal Run](./dogfood-724-establishment.md) | bootstrap phase starts after approval; final proof/close depends on all four system capabilities |

The dependency order is architectural, not a requirement to serialize all
work. The already-linked provider child first implements only its minimum graph
primitive slice. The dogfood child then performs the explicitly bounded #724
bootstrap so GitHub can own progress without pretending the full target runtime
already exists. Binding validation and the remainder of provider behavior can
then proceed in parallel with disjoint writers, followed by orchestration and
evidence lineage. Handoff
production belongs to binding; active workflow coordination belongs to
orchestration; proof/retro/closeout lineage belongs to the bounded evidence
child. The dogfood child stays open until all four capabilities are proven and
the new command surface independently re-verifies the same graph.

## Existing Backlog Work Items

The following 26 existing issues remain reuse-identity Work Items, subject to the
full [readiness contract](../existing-work-item-readiness.md) before
establishment:
#723, #722, #721, #717, #715, #710, #708, #706, #704, #703, #701,
#700, #699, #698, #697, #695, #694, #693, #692, #669, #668, #667, #637,
#634, #628, and #546.

Closed issues #721, #694, and #628 remain linked historical completions only
after their closeout comments are verified as behavioral evidence. Every other
issue receives a managed bounded addendum/body and exact readback, then must be
immediately executable/verifiable before it is eligible for selection. It later
closes with its own issue-owned behavioral evidence or moves to a verified
successor parent with reason before #724 can close.

## Graph Completion

After approval, the binding's canonical manifest contains these five system
keys plus all 26 existing issue identities. Reconciliation compares exact
repository/number/parent relationships, all 23 managed-body digests, and the
three closed issues' observed fingerprints/evidence dispositions; relation
count alone cannot pass. Later verified in-scope discoveries and deferrals are
parent-owned graph amendments and do not mutate the binding's initial manifest.

The final graph has no catch-all implementation child. The dogfood child proves
composition and provider establishment but may not absorb unfinished behavior
from the other four system capabilities or the 26 backlog issues.
