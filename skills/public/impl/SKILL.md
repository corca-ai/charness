---
name: impl
description: "Use when work should move into code, config, tests, or operator-facing artifacts. Read the current contract, make the smallest useful change (including deleting obsolete code or tests), run proportionate focused verification, and leave a concise evidence record."
---
# Impl

Use this when work should move from an agreed intent into code, configuration,
tests, or an operator-facing artifact. `impl` is an execution skill, not a
ceremony runner: its job is to make the intended change and establish enough
evidence that the next decision does not require rework.

## Start

1. Read `AGENTS.md`, then `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path --> and only the pages that own the
   current surface. If an active `/goal #N` exists, read the parent body and
   the selected child only; do not rescan the whole issue graph on routine
   pickup.
2. Read the current implementation contract. If none exists, write a small
   working contract in the task context: intended behavior, acceptance check,
   and explicit non-claims.
3. Inspect the exact target paths and current diff. Preserve unrelated parent
   worktree changes. When using an implementation worktree, it must be clean at
   entry and its runtime/cache paths must be outside the worktree.

Achieve owns active goal navigation; the parent issue is the resume state.

## Continuation

When the user requests autonomous continuation, carry on across local
checkpoints and take the next locally decidable slice. Pause only for a real
product/policy decision, an irreversible external side effect (the boundary
definition is owned by `<authoring-repo>/docs/design-north-star.md`), unavailable
stronger proof, or conflicting evidence.

## Change

- Implement the smallest coherent user-visible change. Deleting an obsolete
  wrapper, gate, mirror, or test is a valid implementation when it removes a
  real source of friction and its remaining consumers are understood.
- Keep source-of-truth and generated export changes together. Use the canonical
  exporter for mirrors; do not hand-edit a generated copy.
- Keep provider selection explicit and resolve it once per operation. Do not add
  a second capability probe when the mutation already performs target
  readback.
- Update the goal parent only when a child transition or externally visible
  decision actually changes.
- Fix the class, not the instance. Before the change closes, read the diff once
  against these six signals; they overlap, and every one that matches is repaired:
  - a value hardcoded with no stated basis
  - a second copy of a source of truth
  - coupling tighter than the seam needs, or a domain boundary the change blurs
  - verification or a gate that costs more than it catches
  - code or a test that exists only for one past moment or incident
  - token, disk, memory, or CPU cost, here and for the consumer who installs it

  The slice's seam is every surface it edits — code, config, test, or
  artifact — with that surface's direct consumers, readers, and generated
  derivatives. Repair inside the seam; name a match outside it as a follow-up,
  not a wider slice.

## Verify

Run the narrowest evidence that answers the changed behavior:

- focused tests for the changed module or user flow;
- the default `<repo-root>/scripts/run-quality.sh` core lane when the change is broad;
- `<repo-root>/scripts/run-quality.sh --full --read-only` only for an explicit broad,
  pre-push, or review check; use `--release` for release-only checks.

When the same failure returns after a fix aimed at it, or a result contradicts
what the contract claims, the test for the next move is whether a falsifiable
cause can be stated — one that predicts an observation able to disprove it. If
it can, make that one correction. If it cannot, another
patch is a guess: stop and enter `../debug/SKILL.md`, whose hypothesis
guardrail, pattern ladder, and detection-gap walk own the repair, and return to
`impl` with its artifact intact. A new, narrower failure after a partial fix is
progress, not this case.

Use external cache and temporary roots supplied by the repo runtime wrapper.
Never treat an ignored cache as proof that the worktree stayed clean; inspect
tracked, untracked, and ignored populations separately when worktree hygiene is
part of the claim.

For authoring a prescribed path or a source-bound record, use the focused
guidance in `../../shared/references/prescribed-path-self-test.md` and
`../../shared/references/source-bound-records.md`; these are design aids, not
additional universal gates.

Additional proof is conditional. A change to verdict logic, a proof surface,
an irreversible external mutation as the north star defines it, a release
surface, or a deletion with
uncertain consumers needs that surface's owner and readback. Ordinary
reversible local work does not require a fresh-eye review, changed-line proof,
or a separate closeout ledger.

## Finish

Report the changed behavior, the focused commands that passed, and the
remaining non-claims. If the active goal needs a provider transition, Achieve
or `issue` updates the parent/child state through the existing provider command.
Do not invent a second coordination channel. Commit only after the relevant
verification has passed; do not push, release, tag, or mutate an installed host
without its explicit authorization.

## References

- `references/adapter-contract.md`
- `references/contract-consumption.md`
- `references/design-lenses.md`
- `references/sequence-discipline.md`
- `references/external-api-contract.md` (only for an external API seam)
- `../../shared/references/prescribed-path-self-test.md` (only for a prescribed path)
- `../../shared/references/source-bound-records.md` (only for a multi-source or durable record)
- `../prove/SKILL.md` (only when its evidence format is explicitly needed)
