# Release Critique — Charness v6.5.0 follow-up

Date: 2026-08-26

## Decision Under Review

Whether to publish Charness `6.4.1` → `6.5.0` with the reduction-first
verification contract, explicit retry identities, live release-state binding,
and honest rendering of unproven public-release claims. The intended behavior
is less-is-more: first question whether the requested verification scope is
necessary, then question the verifier when its contract, trust boundary, or
result is suspect.

## Four-Round Review Result

- Round 1 challenged the initial reduction-first wording and made the scope
  decision explicit at the critique/quality/release entry points.
- Round 2 challenged retry semantics and narrowed them to a one-shot,
  content-addressed decision. A new receipt or renamed output is not a new
  reason to rerun; the helper is deliberately not a global retry ledger.
- Round 3 read the release consumer rather than trusting the helper's shape.
  It found two live-path defects: the retry/release reconciler was absent from
  the CLI execution context, and an inconclusive same-proxy guard could remain
  `verified`. Both were repaired and covered by focused tests.
- Round 4 read the repaired live/state surfaces. Runtime wiring had no further
  blocker; the state/rendering review found a false sentence claiming that an
  unconfirmed probe had established a distinct channel. That renderer defect
  was repaired and covered by focused tests. The separate reduction reviewer
  timed out twice and delivered no finding; that is recorded as a non-claim,
  not as approval.

The final renderer repair was made after the last bounded review. Under the
repository's two-round cap for a verdict-logic slice, it is accepted-unreviewed
under the round cap and supported by local tests and precommit evidence. No
claim that “no more fixes are possible” is made.

## Meta-Analysis: Why Each Round Found Something

The sequence is not evidence that critique should continue indefinitely. Each
round changed the effective review surface after the previous one exposed a
different boundary: prose and scope, retry identity, live dependency wiring,
then state-to-renderer truthfulness. Early tests also used a fake CLI context,
so a unit-level success could hide a production export defect. The lesson is
to review the consumer and the verifier's blind class after a repair, not to
repeat the whole subject suite.

The stop rule now makes the distinction explicit: a retry needs a changed
subject, verifier, input, or stable failure identity; otherwise it is
`stop-no-progress`. A broad final gate is retained only for the irreversible
release consumer closure. A global attempt counter or universal host matrix
would add another broad verifier without a demonstrated escape, so neither is
part of this slice.

## Verification Scope Decision

- Claim under test: the `6.5.0` release path preserves typed verification state and does not render an unproven public-release observation as verified.
- Changed surfaces: critique scope/retry helpers and their generated plugin mirrors; release verification state, CLI execution context, renderer, release tests, and the final release artifact; consumers are the release record, publish gate, public readback, and operator update path.
- Minimum sufficient proof: verify the current prepare packet; validate the critique artifact; run the focused release observer/state/publish tests; run precommit and mirror checks; let the release helper perform its target-specific pre-publish and post-publish consumer checks.
- Deliberately omitted checks: Cautilus, live Ceal/Claude/provider behavior, a universal host matrix, and cumulative `origin/main` changed-line coverage. They are not required consumers for this target and would not prove the repaired boundaries; public readback and install readback remain required release claims.
- Verifier contract: `critique_verification_scope.py` validates typed scope fields and identity coupling; `verification_retry.py` makes one retry decision from content-addressed identities; release verification state/reconciliation owns the public-readback claim. These are not truth oracles and do not maintain a cross-consumer retry ledger.
- Failure classification: none
- Negative control: command `python3 -m pytest -q tests/quality_gates/test_release_observer.py tests/quality_gates/test_release_distinct_channel.py`; expected refusal `inconclusive or same-proxy evidence must not establish verified distinctness`; observed `the guard-aware state and honest renderer paths pass`; receipt `70 passed`.
- Subject identity: sha256:78a5f6caa67a34ff28014ad6c99f254607cb6d4e28a714682c6cbe983fa72bf3
- Verifier identity: sha256:8fb989b4a49cffebf5445d1992d8405126e5ccb9a56444606826642d14f39586
- Input identity: sha256:e4a7c75dfcbed3fabc18452e1a22fb4d7699c18a4f46377ee2e3a200490dd83c
- Failure identity: stable:none
- Evidence identity: sha256:63724c281e0fce4e91d685f1a98634abc60942a5446a8e261c797e5aa31fab76
- Retry disposition: first-attempt
- Retry key: sha256:31eae0a8c9293b0ed4ec7cd6647285824583b92dd1bf953e33560fb75a7eefb3

## Failure Angles

- Scope creep: a changed receipt or a document-only replacement could trigger a whole-repo rerun. The contract now requires a smallest claim, final consumers, omitted checks, and a changed identity before retry.
- Verifier defect: a passing shape check could be mistaken for semantic truth. The review explicitly challenged helper limits, live export wiring, guard state, and renderer wording; the remaining helper preimage/automatic-consumer-wiring limitations are non-claims, not hidden approvals.
- Subject defect: the release path could still publish a false public verification state. The live-context and renderer defects found in R3/R4 were fixed and locally tested.
- Review delivery: the R4 reduction lens did not deliver after one retry. Its absence is retained as a delivery non-claim, not converted into a same-agent approval.

## Counterweight Pass

The live-context omission, inconclusive-guard state, and false renderer sentence
were real act-before-ship findings because they could change an irreversible
release claim. They were repaired in commits `06517a7a7` and `e500c4611` and
covered by focused tests. The request to add a global retry ledger, an attempt
counter, or a universal host proof is over-worry for this slice: no concrete
escape requires those controls, and they would recreate the broad verifier
that the reduction-first rule is meant to question. The absence of a delivered
R4 reduction finding stays valid-but-unproven rather than being silently
collapsed into a green verdict.

## Review Packet Evidence

- R1 packet: `charness-artifacts/critique/2026-08-26-reduction-first-verification-packet.json`; packet SHA `f6e6f5c460fbe300e12d434a60d64bf25aa7d15346470a45adcfd98d7c8cd23a`; input identity `2022b6abbdc99400a47ab6427b6a54054f219d1f745c87a4e030af03cb80e8b7`.
- R2 packet: `charness-artifacts/critique/2026-08-26-reduction-first-verification-r2-packet.json`; packet SHA `f7c9c8f0e7089bb34f11ab092226ed2e098cdd88a12708f2233a1f69e55e4526`; input identity `4aad3ee91ec49f2000196bdb46d6d730a3913e6dd4585a6db6747b2d2725d09d`.
- R3 packet: `charness-artifacts/critique/reduction-first-verification-r3-packet.json`; packet SHA `e4d9fe43aa8a031e3a070245d7e1abb968b1a468bd74aa299ec937897347bb91`; input identity `8c455f03055dfa3799da13693c7a80dd0e7c8ef50e6c8ad85dec8d3e05741c07`.
- R4 packet: `charness-artifacts/critique/reduction-first-verification-r4-packet.json`; packet SHA `d87932669f7186943e0200c25c5b65302ab0e18a025b9321ae3ee3f0e23352c8`; input identity `bc6c57d507735be8e7ada01d7d64035b6e47b1a82deba3e53eec0663b0aa32c9`.
- Final post-R4 prepare packet: `charness-artifacts/critique/reduction-first-verification-final-packet.json`; deterministic packet SHA `63724c281e0fce4e91d685f1a98634abc60942a5446a8e261c797e5aa31fab76`; input identity `e4a7c75dfcbed3fabc18452e1a22fb4d7699c18a4f46377ee2e3a200490dd83c`; packet verification is current and shape-only, not release approval.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer
- Requested spawn fields: unnamed one-shot; inherited host defaults; no model override
- Host exposure state: host-defaulted
- Application state: metadata-hidden — no provider-side tier metadata was exposed; findings were delivered from separate parent-delegated reviewer contexts
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — R3 and R4 findings were received from separate unnamed
read-only reviewer contexts; the R4 reduction lens timed out after one retry
and remains a non-claim; the post-R4 renderer repair is
accepted-unreviewed-under-round-cap.

## Boundary Ownership

- Producer: critique scope/retry validators, release state reconciler, renderer, generated mirror sync, focused tests, precommit, and the release helper each produce their own evidence.
- Consumer: the durable release record, claims-review gate, tag/public release, and operator update path consume those typed results.
- Owning surface: the release verification state and rendering boundary owns the public-readback verdict; the critique helper owns only the retry decision contract.
- Verdict: owned-correctly

## Release Scope

- Current version/tag: `6.4.1` / `v6.4.1`.
- Target version/tag: `6.5.0` / `v6.5.0`.
- Follow-up slice: `7eaa46939` through `e500c4611`, based on the prior release review carrier at `4961093d061123d5cd54343b1fa7b5752d861b79`.
- Bump rationale: minor is the lightest honest level because this is an additive maintained verification/release capability; existing callers retain their invocation and payload shapes.

## Evidence Executed

- Current final prepare packet verification: passed with `status: current` and `shape validation ok`.
- Focused release observer/state tests: 70 passed.
- Focused release publish tests: 17 passed, 5 deselected.
- Precommit: all declared checks passed; Python length notices were advisory.
- Source/plugin mirror synchronization and drift checks: passed during the final repair sequence.
- The full release gate, target claims review, publication, distinct-channel public readback, and install refresh are intentionally pending and belong to the release helper sequence below.

## Deliberately Not Claiming

- No `v6.5.0` tag, push, hosted release, public readback, or installed `charness update/version/doctor` readback exists yet.
- No live Ceal/Claude/provider, Windows-race, Cautilus, or universal-host proof is claimed.
- The retry helper does not prove that a caller's digest matches a preimage and is not automatically wired into every consumer's resume history; no global loop-prevention guarantee is claimed.
- The R4 reduction reviewer delivered no result after retry; the final renderer repair has no fresh-eye approval and is accepted-unreviewed-under-round-cap.
- The final prepare packet proves deterministic shape/currentness only, not release readiness or public truth.
- This record does not claim that future review can never find another defect; it claims only that the bounded review and stop rule have been applied honestly to this release boundary.

## Operator Action Required

Run the repo-owned release helper for the minor bump with this artifact and the
explicit rationale. Stop at the prepared claims-review boundary, bind a
distinct claims review to the prepared record, then resume with the exact
original arguments. After publication, require distinct-channel public readback
and run the adapter-declared `charness update`, `charness version`, and
`charness doctor` readbacks before calling the release verified.

## Upgrade Path

```text
charness update
charness version
charness doctor
```
