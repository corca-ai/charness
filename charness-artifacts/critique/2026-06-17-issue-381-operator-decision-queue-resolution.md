# Issue #381 Operator Decision Queue Resolution Critique

Date: 2026-06-17
Target: https://github.com/corca-ai/charness/issues/381
Packet consumed: `charness-artifacts/critique/2026-06-16-222946-packet.md`
Fresh-Eye Satisfaction: parent-delegated

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `requested_fields_sent`
- **Application state**: `fields accepted by spawn call; provider application not independently confirmed`

## Change

Adds a portable `## Operator Decision Queue` surface for `achieve` goal
artifacts and connects HOTL operator-needed dispositions to it. Fresh `achieve`
and handoff-generated draft goals include the queue. Complete-state evidence for
goals created on or after 2026-06-17 now requires the queue to carry either
`none — <reason>` or a `Decision:` item.

Out of scope: repo-specific side-effect policies, live proof commands,
machine-readable HOTL ledger schema changes, and #371 lifecycle proof.

## Angle Findings

- First-use reviewer: the initial handoff auto-draft only exposed the heading,
  not the queue item schema. Fixed by adding the same queue guidance and item
  form to `skills/public/handoff/scripts/chunked_routing_auto_draft.py`.
- Validator reviewer: making the queue a global required section would break
  historical goal artifacts, and the initial scaffold text did not force a real
  closeout disposition. Fixed by removing the global required-section change and
  adding a Created-gated complete-state floor in
  `skills/public/achieve/scripts/goal_artifact_operator_queue.py`.
- Cascade reviewer: dogfood/lifecycle/SKILL wording initially overstated or
  under-specified the final report contract. Fixed by aligning dogfood wording,
  `achieve` output shape, and `references/lifecycle.md`.

## Counterweight Triage

Act Before Ship:
- Done — dogfood now says fresh artifacts include the queue and complete-state
  evidence requires new goals to disposition it.
- Done — new helper files are part of the working tree and plugin mirror sync.

Bundle Anyway:
- Keep handoff auto-draft queue schema; it closes the first-use gap without
  expanding runtime enforcement.
- Keep HOTL pointer guidance; it does not alter the seven-status vocabulary or
  proof-command contract.
- Keep the Created-gated floor; it prevents new closeout disappearance without
  migrating historical artifacts.

Over-Worry:
- Do not add historical goal migration.
- Do not add a transcript hard gate requiring every final answer to literally
  contain a queue line.
- Do not require full field parsing for every `Decision:` item in this slice.

Valid but Defer:
- A future validator could check full queue item fields when a `Decision:` item
  exists, but #381 only needs an obvious durable queue and empty/non-empty
  disposition at closeout.

## Floor-Addition Restraint

Call: keep. This is a new blocking floor, but it is Created-date gated,
complete-state only, and narrower than the rejected global required-section
migration. Advisory/prose alone is insufficient for #381 because the reported
failure mode is decision-needed items disappearing into residual-risk prose.

## Next Move

Ship after deterministic validation, direct-commit closeout carrier validation,
and GitHub closeout verification for #381. Leave #371 open unless controlled
agent-browser lifecycle proof covers normal completion, cancellation, provider
failure, and timeout.
