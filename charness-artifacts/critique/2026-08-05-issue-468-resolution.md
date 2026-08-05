# Critique — corca-ai/charness#468 resolution

- **Execution**: executed (bounded fresh-eye reviewer)
- **Fresh-eye Satisfaction**: parent-delegated
- **Reviewer tier**: high-leverage; requested `gpt-5.6-terra` with medium reasoning effort
- **Boundary fingerprint**: `issue-468-resolution-20260805` — clean
- **Target**: deferred-work resolution contract / documentation surface

## Reviewer Tier Evidence

- requested tier: high-leverage
- requested spawn fields: model `gpt-5.6-terra`, reasoning_effort `medium`; no service-tier override was requested
- host exposure state: requested_fields_sent
- application state: spawn accepted reviewer `019fd049-4833-7560-bcca-1ee2c0bf1275`; provider-side model application was not independently exposed
- Delivery state: findings-received

## Boundary Ownership

- Producer: `docs/deferred-decisions.md` produces the deferred-remedy premise record and its evidence fields.
- Consumer: future resolvers, issue-resolution briefs, and bounded reviewers consume the record before remedy design.
- Owning surface: `docs/deferred-decisions.md`; this issue-local documentation contract owns the convention and does not delegate it to a generic validator.
- Verdict: owned-correctly

## Change

Resolve #468 by adding a repo-local `Named Remedy Premise Contract` to
`docs/deferred-decisions.md` and applying it to D45, D47, and D48. The contract
requires the current premise, evidence channel, observation, downstream
decision delta, and an explicit status before implementation begins. It remains
a review convention; it does not add a blocking semantic validator.

## Reporter JTBD

A future resolver must not treat a prose remedy as an implementation plan
without rechecking the current owner/first reader and the premise's evidence
channel.

## Findings (deduped)

- **Act Before Ship**: D47 initially called the evidence channel “the five cited
  consumer artifacts,” but the measured result is five refused citations across
  four artifacts. Corrected before closeout so the record preserves its units.
- **Over-Worry**: the contract is operational enough for its stated
  review-convention boundary. It requires checking the current owner/first
  reader, recording a concrete evidence channel and observation, and makes
  `not-run` explicitly non-authorizing without presenting the convention as a
  blocking gate.
- **Over-Worry**: D45's `falsified` status matches the reader signature and
  adapter contract; its delta reshapes a rewire into a new seam and precedence
  decision.
- **Over-Worry**: D48's `withdrawn` status matches the sync-output and release
  vocabulary reads; retaining explicit uncorroborated publish refusal is
  correctly scoped.
- **Valid but Defer**: D47's replacement contract remains unspecified; the
  named remedy is withdrawn without silently implementing a successor.

## Deliberately Not Doing

- No universal semantic validator for prose premises.
- No implementation of the withdrawn D47/D48 remedies.
- No rewrite of unrelated deferred-decision history or plugin export.

## Next Move

Run the issue closeout shape/validator against the exact direct-commit carrier,
then publish and read back #468 through the GitHub adapter. The distinct
behavior verdict must come from reading the changed documentation contract and
its three normalized examples, not from the GitHub state or carrier body.
