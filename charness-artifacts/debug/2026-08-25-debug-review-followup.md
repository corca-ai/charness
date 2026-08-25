# Repeated Review Failure Debug Review
Date: 2026-08-25

## Problem

The first implementation/review pass repeatedly appears green, then a fresh-eye
or adversarial pass finds another failure in an adjacent boundary. The user
experiences this as “why does it keep failing?” rather than as isolated bugs.

## Correct Behavior

When a slice claims success, the final consumer must receive one bound identity
and an established evidence state for every required producer, transport,
package, and artifact surface. Missing, skipped, degraded, stale, or
unavailable evidence must remain a typed non-proof.

## Observed Facts

- The 2026-08-25 adversarial review found four false-green classes: degraded
  duplicate inputs, skipped/xfail proof nodes, helper mutations outside commit
  triggers, and missing packaged anchors.
- The preceding review found the same shape in worker fences, optional joins,
  malformed manifests, and duplicate readiness.
- The Node TAP incident crossed wrapper and run boundaries because counts and
  diagnostics did not share one selected-run owner.
- The broad standing run reached 11,178 passes but had seven source/plugin-drift
  failures; a focused 49-test rerun passed after synchronization. The latest
  quality receipt explicitly claims no full changed-line mutation verdict.
- `docs/agent-task-envelope.md` says task is not a scheduler/worktree/reviewer;
  `skills/public/critique/SKILL.md` still requires multi-angle workers and a
  separate counterweight by default.

## Reproduction

Delete a required duplicate-lineage input, convert a provenance test to skip,
remove a packaged consumer anchor, or remove one worker-to-consumer binding.
The old local-success paths can still look green unless the final consumer
checks the typed evidence state and dependency closure.

## Candidate Causes

- A transient tool or flaky test.
- An incomplete adversarial fixture set.
- Source/plugin/installed or producer/consumer identity drift.
- Distributed contracts that let each local boolean stand in for final proof.
- A workflow mismatch: task records state while critique/host lanes still own
  execution and spawning.

## Hypothesis

The repeated failures are one boundary-contract class, not independent flakes:
local producers emit plausible values, but no single executable contract binds
identity, evidence state, dependency closure, and final-consumer ownership.
Disconfirmer: a negative fixture that removes any required join must make the
owning final consumer refuse approval before a reviewer is needed.

## Verification

The hypothesis is confirmed by the repeated findings in the three debug
artifacts above and by independent reproductions recorded there. Current local
source/plugin fingerprints are aligned; live consumer-host, Windows, network,
and provider adoption remain unproven.

## Root Cause

The repository optimizes for local gate success while the real capability is a
cross-surface claim. Evidence states collapse (`missing -> empty`, `skipped ->
passed`, `degraded -> ready`), producer identity is dropped, and generated or
installed consumers are checked later or separately. Each repair therefore fixes
the observed path and leaves sibling omission paths available.

### Five Whys

1. Why are failures found after review? Reviews add adversarial inputs absent
   from the first regression matrix.
2. Why were those inputs absent? Tests assert successful return codes and local
   helpers, not typed negative states at the final consumer.
3. Why? Required joins, dependency closure, and ownership are split across
   registries, prose, source mirrors, and artifact validators.
4. Why does that split survive? No single boundary contract is the mandatory
   owner of producer identity plus refusal semantics.
5. Why is the contract missing? The architecture grew by issue-local repairs;
   the current task envelope records work but does not compose execution,
   critique, package, and consumer proof into one lifecycle.

## Invariant Proof

- Invariant: when any producer emits evidence, the final approval consumer must
  surface its identity and refuse unless all required evidence is established.
- Producer Proof: the negative fixtures and issue-linked debug artifacts above.
- Final-Consumer Proof: duplicate, provenance, package-anchor, reviewer-delivery,
  and TAP reporter tests; the repaired slice additionally refuses malformed
  duplicate overlays, unknown/skewed lineage identity, omitted dependency
  triggers, and reports that drop `producer_run_id`. These prove local
  consumers, not live hosts.
- Interface-Shape Sibling Scan: `check_dup_ratchet.py`,
  `check_provenance_contract.py`, `reviewer_worker_report.py`,
  `scripts/staged_commit_gate_plan.py`, and `NodeTestReporter` share the same
  producer-to-verdict shape; decision: same class, diagnostic-only here; proof:
  focused fixtures and artifact readback.
- Non-Claims: no live Ceal/Claude roundtrip, Windows race, online link check,
  installed-session refresh, GitHub, push, release, or Cautilus proof.

## Detection Gap

- Focused tests covered known success paths; add one negative fixture per
  registry row at the final consumer.
- Source/plugin parity did not prove package anchors; the repaired registry now
  triggers on the declared runtime dependency closure, while packaged anchors
  remain a separate shape-only proof.
- Task tests prove CAS/state transitions, not task-to-execution/critique
  ownership; add a lane replay that forbids nested spawning.
- Quality receipt is fast and green for its slice, but broad/changed-line proof
  is not the same gate; publish distinct scope and identity in every receipt.

## Sibling Search

- Mental model: a partial/local signal is mistaken for an established verdict.
- Same layer: reviewer delivery, lesson finalization, capability selection,
  duplicate lineage, provenance, and TAP parsing — decision: same class,
  diagnostic-only for this slice; proof: prior focused fixtures.
- Abstraction up: producer -> transport/mirror -> final consumer — decision:
  same class, diagnostic-only for this slice; proof: repeated debug artifacts.
- cross-file: `docs/agent-task-envelope.md` and `skills/public/critique/SKILL.md`
  show execution/review ownership split; decision: valid follow-up outside the
  slice; proof: static contract read; follow-up: deferred docs/handoff.md
  `## Next Session` item 2.

## Seam Risk

- Interrupt ID: repeated-consumer-boundary-failure-2026-08-25
- Risk Class: repeated-symptom, external-seam
- Seam: producer evidence -> task/host transport -> packaged consumer -> verdict
- Disproving Observation: deleting a required join still yields an eligible
  approval with no typed refusal.
- What Local Reasoning Cannot Prove: live host/provider behavior and adoption.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Review Note: the spec was implemented. The second bounded review delivered
  four blockers (malformed overlay, unknown/skewed lineage identity, incomplete
  trigger closure, and dropped producer identity); focused repair and consumer
  proof now pass. Repairs made after the second round are accepted-unreviewed
  under the two-round cap. Broad changed-line/release/host proof remains a
  separate non-claim until executed.
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-25-consumer-boundary-invariants.md

## Prevention

Make the boundary invariant executable and consumer-owned: one typed registry
for required joins, identity, terminal outcomes, refusal codes, dependency
closure, and negative fixtures. Then define a task execution adapter that binds
one task to one host run/result carrier and explicitly disables nested critique
spawns; dogfood it through one long goal with real phase specs before broadening
the contract.
