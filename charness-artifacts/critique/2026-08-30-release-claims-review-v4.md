# v8 claims-review authoring and closed-schema design

Date: 2026-08-30

## Decision Under Review

Replace hand-authored release claims-review bindings with a read-only-by-default
scaffold that derives repository facts from the prepared commit, and replace the
open-ended claims-review record with the closed `charness.release.claims-review.v4`
schema before publishing v8.0.0.

## Verification Scope Decision

- Claim under test: a prepared v8 release can produce a claims-review record whose
  repository-derived bindings are exact and whose removed fields cannot survive as
  silent transport or rendering residue.
- Changed surfaces: release claims-review schema, scope validator, scaffold,
  planner packets, resume consumer, artifact renderer, authoring documentation,
  fixtures, and their focused tests.
- Minimum sufficient proof: the focused release claims-review/planner/publish tests,
  including a real prepared fixture accepted by the production resume validator and
  negative controls for unknown removed fields, incomplete history, scope mismatch,
  dirty state, and read-only preview behavior.
- Deliberately omitted checks: mutation execution and empirical consumer-speed
  measurement; neither is a claim of this release or needed to establish this
  authoring/schema contract.
- Verifier contract: the production claims-review/resume validators plus their
  focused tests; the verifier changed intentionally because the schema itself moved
  from open-ended residue tolerance to closed-world v4 validation.
- Failure classification: verifier-defect
- Negative control: command: inject removed `scope_completeness` | expected refusal: unknown field | observed result: production validator refused | receipt: focused pytest output.
- Subject identity: sha256:b1875e0a01b2904c8569cb46380914fdeae8cf21d1cfdd50e4bcc8b03a796739
- Verifier identity: sha256:86d1bb626ee2f5605eb9b5f9dceedda81ce1e3ff85027b73cca11d11642668ff
- Input identity: sha256:c1884f44dca3811e89c3138895dbc1323e70a4b7aa07cb862ddd6bff17b2ed6e
- Failure identity: stable:state-contraction-residue
- Evidence identity: sha256:c1884f44dca3811e89c3138895dbc1323e70a4b7aa07cb862ddd6bff17b2ed6e
- Retry disposition: first-attempt
- Retry key: sha256:d2258d9311b3fff7ec818dc975484a8c091b3ca1213dc32ea762d4bdd67d20af

## Failure Angles

- A human could copy a prepared commit, record hash, base tag, target, or scope
  digest incorrectly while still producing syntactically valid JSON.
- A removed field could remain in a resume transport or renderer after its producer
  disappears, preserving dead code until an unrelated size gate happens to expose it.
- A shallow clone, non-ancestor base, colliding tag, target mismatch, stale narrative,
  or unrelated dirty file could make derived evidence look authoritative when it is
  incomplete or bound to the wrong release state.
- A scaffold could accidentally claim reviewer independence merely because it emits
  a record for a separate reviewer to fill.

## Counterweight Pass

- The first three angles are release blockers. They are addressed by deriving every
  repository-owned fact from the prepared state, validating the exact full delta,
  refusing ambiguous history/state, and rejecting unknown fields recursively.
- The scaffold does not and should not prove reviewer independence. It only records
  the operator-supplied observer context and signal; the distinct reviewer and the
  final consumer validator remain separate evidence boundaries.
- A generic framework for every possible release record would add abstraction
  without another consumer. The cohesive v4 schema owner is the smallest structural
  boundary that closes this observed class.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/scaffold_claims_review.py | action: fix | note: manual copying of prepared-state bindings was release friction and an integrity risk; the scaffold now derives and validates them before writing only the JSON record.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/claims_review_schema.py | action: fix | note: producer-only state contraction left dead transport/rendering residue; closed v4 shape validation and removed-field injection tests now make that class refuse generically.
- F3 | bin: over-worry | evidence: moderate | ref: skills/public/release/references/critique-boundary.md | action: document | note: scaffold generation is not evidence of a distinct observer; reviewer context and final resume validation remain explicit separate boundaries.

## Reviewer Tier Evidence

- Requested tier: gpt-5.6-luna fresh-eye design reviewer.
- Requested spawn fields: model=gpt-5.6-luna, bounded read-only review of the claims-review scaffold and closed-schema design, with refusal-path and boundary-ownership checks.
- Host exposure state: applied
- Application state: host-confirmed: the `release_known_friction` Luna subagent returned SHIP with explicit acceptance conditions covering prepared-state derivation, exact delta binding, refusal cases, read-only preview, and observer-boundary non-claims.
- Delivery state: findings-received
- Execution mode: typed-subagent
- Worker report: n/a
- Worker report identity: n/a
- Worker report approval: n/a
- Worker report delivery: n/a
- Worker report packet identity: n/a
- Worker report input identity: n/a
- Worker report parent receipt identity: n/a
- Worker report findings identity: n/a

## Fresh-Eye Satisfaction

parent-delegated — `release_known_friction` returned SHIP with acceptance
conditions; F1 and F2 were implemented, and F3 remains an explicit non-claim at
the correct reviewer boundary.

## Reviewed Input Identity

<!-- No prepared packet was consumed; the reviewer inspected the bounded design and
implementation surfaces directly in a separate Luna agent context. -->

## Boundary Ownership

- Producer: `scaffold_claims_review.py` derives prepared-state facts and combines
  them with explicit reviewer inputs.
- Consumer: `validate_claims_review` and resume-publish consume the record; the
  release artifact renderer consumes only the validated final state.
- Owning surface: release claims-review schema and authoring capability.
- Verdict: moved-to-owner

The old shape distributed release-state knowledge across a human author, resume
transport, and renderer. The v4 schema and scaffold move derivation and shape
ownership into one release capability while leaving observer truth with the actual
reviewer.
