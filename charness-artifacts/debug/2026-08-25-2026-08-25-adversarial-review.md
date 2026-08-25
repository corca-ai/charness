# Adversarial Consumer Boundary Debug Review
Date: 2026-08-25

## Problem

The second approval review found real false-green paths after the first
producer-to-consumer repair: degraded duplicate inputs could become lineage
approval, skipped/xfail pytest nodes could count as executable proof, helper
edits could miss the commit trigger, exported consumers were not anchor-checked,
and the spec repeated a stale standing-test count.

## Correct Behavior

Missing, unavailable, skipped, xfailed, unestablished, or stale evidence must
remain typed non-proof at the final consumer and at the operator-facing
artifact. Only an established consumer verdict may support approval.

## Observed Facts

- `check_dup_ratchet.py` previously set `lineage_approval_eligible` from
  `readiness.status` alone; missing overlay/baseline collapsed to empty input.
- `check_provenance_contract.py` previously used only pytest's zero return code;
  parameterized, skipped, and xpass outcomes were not classified.
- `scripts/staged_commit_gate_plan.py` named entrypoints but not delivery/lineage
  helpers, so a transitive mutation could bypass the contract gate.
- Plugin validation skipped both fixtures and consumer-anchor checks. The
  standing count in the spec was 11,409 while the current canonical run was
  11,416.

## Reproduction

- Delete `q/dup-review.json` or `q/dup-ratchet-baseline.json` in the consumer
  fixture and run `check_dup_ratchet.py --detail`: the old path reported
  `status: degraded` and `lineage_readiness: ready` with approval eligible.
- Replace a contract pytest node with a skipped or xpassed node: the old checker
  returned zero and marked it passed.
- Stage `skills/shared/scripts/reviewer_delivery_fields.py` or
  `skills/public/quality/scripts/dup_family_lineage.py`: the old plan omitted
  `check-provenance-contract`.
- Remove `plugins/charness/shared/scripts/reviewer_worker_report.py`: the old
  plugin checker still returned `ok: true`.

## Candidate Causes

- A local success signal was treated as final evidence.
- The registry named obligations but did not own dependency closure or proof
  status semantics.
- Commit and package boundaries checked only the obvious entrypoint, while
  closeout prose copied counts manually.

## Hypothesis

The recurring class is an evidence-state collapse at a boundary. If final
consumers require both established inputs and a typed passing proof result, and
the commit/package gates cover dependency and anchor surfaces, the four
transitions `missing -> empty`, `unavailable -> ready`, `skipped -> passed`,
and `not-packaged -> exit 0` become observable refusals. Disconfirmer: delete a
lineage input, skip a fixture, remove an anchor, or mutate a helper and obtain a
green approval without a refusal.

## Verification

The reproductions were run by two independent read-only reviewers. The repair
now gates lineage eligibility on `not degraded`, reads JUnit testcase outcomes,
adds helper/fixture triggers, validates plugin consumer anchors, adds a narrow
checker self-test channel, and refuses missing provenance proof at pre-push.
Focused boundary tests (`python3 -m pytest -q
tests/test_provenance_contract.py tests/quality_gates/test_dup_ratchet.py
tests/quality_gates/test_reviewer_delivery_state_machine.py`): 106 passed in
the final repair slice; source checker: four executable fixtures passed; plugin
checker: `shape+consumer-anchors` with an explicit fixture non-claim.
Canonical standing runner at HEAD `a28c7f741`: `11419 passed in 99.01s`.

## Root Cause

The structural cause is not any one malformed input: final verdicts were
assembled from local booleans without one evidence-state machine that preserved
the distinction between absent, empty, unavailable, and proven. The same gap
recurred one layer up in proof artifacts and package boundaries.

### Five Whys

1. Why did review find failures? Normal success and process exit paths were
   tested, not degraded, skipped, helper-mutation, and package-removal paths.
2. Why were those paths omitted? “Evidence arrived” and “evidence is approval-
   eligible” were not represented as separate required states everywhere.
3. Why did the distinction disappear? The registry was an index, while domain
   consumers, gate triggers, and artifact prose each held part of the rule.
4. Why did existing gates not catch it? They watched final entrypoints and
   return codes, not dependency closure, structured test outcomes, or anchors.
5. Why is that structural? No single contract bound each claim to its minimum
   evidence set and refusal state across producer, checker, package, and
   closeout surfaces. Prevention is the typed registry plus independent proof
   channel and fresh count/identity binding.

## Invariant Proof

- Invariant: when a producer emits identity, readiness, or proof, the final
  consumer must surface it and refuse approval unless the evidence is established.
- Producer Proof: duplicate scan inputs, pytest JUnit results, plugin exports,
  and canonical standing-pytest receipt.
- Final-Consumer Proof: duplicate verdict, provenance checker, staged gate,
  plugin anchor checker, and focused tests.
- Interface-Shape Sibling Scan: same evidence collapse appears in reviewer
  delivery, lesson finalization, capability selection, duplicate lineage, and
  proof artifacts; decision: same class, fix now; proof: focused tests and
  independent reviewer reproductions.
- Non-Claims: the registry remains an audit index for `required_fields` and
  `refusal_code`, not independent runtime enforcement of every metadata row;
  installed Ceal/Claude hosts, provider roundtrips, GitHub state, push/release,
  and Cautilus remain unproven.

## Detection Gap

- duplicate consumer | readiness ignored degraded state | eligibility requires
  `not degraded`.
- provenance checker | return code hid skip/xfail/zero tests | JUnit result parser
  plus self-test channel.
- commit/package boundary | entrypoint-only trigger and no plugin anchor check |
  dependency trigger set and mapped anchor validation.
- closeout artifact | hand-copied test count | record the canonical run identity
  and count before claiming approval.

## Sibling Search

- Mental model: a partial signal is mistaken for an established verdict.
- Same layer: reviewer, lesson, capability, duplicate consumers | decision:
  same class, fix now | proof: registry fixtures.
- Abstraction up: proof gate -> package -> artifact claim | decision: same class,
  fix now | proof: plugin mutation and stale-count readback.
- cross-file: `scripts/run-quality.sh` and
  `charness-artifacts/spec/2026-08-25-consumer-boundary-invariants.md` | decision:
  same class, fix now | proof: fallback and count inspection.

## Seam Risk

- Interrupt ID: consumer-boundary-adversarial-review-2026-08-25
- Risk Class: repeated-symptom, external-seam
- Seam: producer evidence -> checker -> package/export -> operator claim
- Disproving Observation: a removed input or anchor still yields an eligible
  verdict with no typed non-claim.
- What Local Reasoning Cannot Prove: live host/provider behavior and public
  release readback.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Review Note: second fresh-eye verdict-surface review is required after this repair.
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-25-consumer-boundary-invariants.md

## Prevention

Keep boundary contracts typed and consumer-owned, but make every final approval
require an established evidence state. Execute exact fixtures with structured
outcome parsing, trigger the gate on dependency closure and test changes,
validate exported anchors, and make missing pre-push proof refuse rather than
look green. Bind closeout counts to a fresh canonical receipt instead of prose.
