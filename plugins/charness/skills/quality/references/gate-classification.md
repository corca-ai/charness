# Gate Classification

The four closeout states (`healthy` / `weak` / `missing` / `deferred`) and the
non-obvious rule that a green, non-shallow gate is still `weak` when a cheaper,
more-direct proof now covers the same seam are single-sourced in the planner
`brief` (`gate_classification.closeout_states`). This doc holds the deeper
discipline the brief summarizes; open it when a classification is contested.

Classify after enforcement triage (`AUTO_EXISTING` / `AUTO_CANDIDATE` /
`NON_AUTOMATABLE`, defined in the brief's `automation_promotion`). When
recommending how often a gate should run, pace targeted vs broad proof by the
meaningful-unit cadence in
[meaningful-slice-cadence](../../../shared/references/meaningful-slice-cadence.md):
broad standing gates and pre-push proof default to the bundle/final boundary,
not the inner loop.

## `weak` versus `missing`

This boundary decides which required artifact section a finding lands in. `weak`
is present-but-inadequate: gameable, too shallow for the claimed confidence,
duplicated by a better existing gate, or still paying standing runtime after a
cheaper and more direct proof exists. `missing` is absent-or-only-implied for a
risk the current surface carries. `defer` is useful-later but not the next
highest-leverage move now.

## Recommended Next Quality Moves

Every recommended next quality move carries an execution posture tag —
`active` (install or change now as the next bounded proof move) or `passive`
(monitor, wait, or defer with an explicit reason).

The ordering of `Recommended Next Quality Moves` is an **inference-layer**
ranking, not a verdict, so it falls under
[advisory-interpretation-contract.md](../../../shared/references/advisory-interpretation-contract.md).
It measures *your* judged leverage of each candidate move against the current
risk surface; it proxies for "the single highest-value next quality move"; it is
blind to maintenance burden you have not yet weighed and to risks no inventory
surfaced. Before presenting the ranking, answer its interpretation question
first, in your own words against this repo: does the top-ranked move genuinely
fit THIS repo's current state and burden tolerance, or is it a generic default
the ranking cannot contextualize? Verified gate *results* (a green/red gate, an
exact count) stay trusted — only the recommendation ordering is re-interpreted.

Move types include cleanup/delete, merge or split ownership, helper extraction,
interface narrowing, dogfood or evidence packets, advisory/describe-first
guidance, existing-gate reuse, candidate floor, defer/watch, and no-gate (the
planner packet enumerates the canonical `QUALITY_MOVE_TYPES`). `candidate-floor`
is exceptional and needs explicit north-star plus floor-addition-restraint
provenance before it becomes executable.
