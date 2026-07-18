# Gajae-Code Adoption Plan Critique
Date: 2026-07-19

## Decision Under Review

Lock the evidence-backed adoption sequence in
`charness-artifacts/spec/2026-07-19-gajae-code-adoption-plan.md` without copying
Gajae-Code's host runtime or adding speculative reversible-work gates.

## Execution

- Execution: executed with two bounded spec angles followed by a separate
  counterweight.
- Packet consumed:
  `charness-artifacts/critique/2026-07-18-152736-packet.md`.
- Target: `spec-critique`.

## Failure Angles

- Problem/owner angle: checked whether the proposed gap already had a Charness
  owner, whether Slice 1 was a real current failure, and whether later slices
  created duplicate state or evidence systems.
- Structure/acceptance angle: checked Fixed/Probe/Defer coherence, public
  YAML/internal JSON boundaries, and the mapping from each success criterion to
  a runnable check.
- Counterweight: pushed back on generic RPC machinery, new public enums,
  notification-count policy, pipe-buffer choreography, and unconditional index
  lifecycle work.

## Fixed/Probe/Defer Coherence Result

- Fixed: pass after correction. Slice 1 is one request-scoped absolute-deadline
  and response-ID seam, not a generic transaction framework.
- Probe: pass after correction. CI, goal receipts, real-host protocol, and local
  session-index questions now name owners, writeback, and promotion thresholds.
- Deferred: pass after correction. Goal/task state and child-cache changes now
  have concrete reopen triggers rather than a bare “later.”

## Acceptance Check Coverage Result

- SC1/SC2: fake app-server negative matrix plus YAML integration shape.
- SC3: declared-input tamper and unrelated-path non-staleness fixtures.
- SC4: release observer verified/unavailable/malformed schema fixtures.
- SC5/SC6: A/B comparability refusal and outcome-adjacency report fixtures.
- The unconditional index criterion and the global manual negative assertion
  were removed; indexing is a measured probe exit instead.

## Counterweight Pass

- Act Before Ship: bind durable critique verdicts at the critique artifact, not
  only the prepare packet; make release observer generation derive from the
  existing distinct-channel verdict so two success records cannot diverge.
- Bundle Anyway: narrow Slice 1 to current helper seams, define the A/B
  comparability predicate, add one compact probe governance table, and remove
  the non-local SC8 assertion.
- Over-Worry: do not add a message-count cap, generic JSON-RPC client, mandatory
  two-line pipe-buffer fixture, or new public failure taxonomy without evidence.
- Valid but Defer: a disposable incremental audit prototype may run only after
  measuring current scan cost; it becomes production only if its exit evidence
  justifies lifecycle complexity.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/critique_packet_lib.py:117 | action: fix | note: store reviewed_input_identity beside the durable verdict and define declared-input staleness
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_post_create.py:173 | action: fix | note: derive the observer record from the existing distinct-channel verification instead of creating a parallel verdict
- F3 | bin: bundle-anyway | evidence: strong | ref: charness:1630 | action: fix | note: narrow Slice 1 to per-request absolute deadline plus response-ID waiting and preserve the public envelope
- F4 | bin: bundle-anyway | evidence: moderate | ref: scripts/skill_efficiency_report.py:50 | action: fix | note: define a local A/B comparability predicate and reuse current outcome fields
- F5 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/spec/2026-07-19-gajae-code-adoption-plan.md#probe-questions-and-governance | action: fix | note: record probe owner, writeback, and promotion trigger in one table
- F6 | bin: over-worry | evidence: weak | ref: charness:1630 | action: document | note: a count cap and new public error enum solve unobserved policies beyond the deadline-reset bug
- F7 | bin: valid-but-defer | evidence: moderate | ref: scripts/codex_session_audit_lib.py:1 | action: defer | note: incremental indexing needs a measured-cost probe exit before production adoption
- F8 | bin: over-worry | evidence: weak | ref: tests/charness_cli/test_codex_cache_refresh.py | action: document | note: assert observable deadline behavior rather than mandating pipe-buffer choreography

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.6-terra`,
  `reasoning_effort=medium`, `service_tier=priority`, `fork_turns=none`.
- Host exposure state: requested_fields_sent
- Application state: the spawn surface accepted the requested fields and
  returned completed reviewer payloads; provider-side application metadata was
  not independently exposed.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: prepare packet and parent orchestration produce reviewed input and
  isolation evidence; release helper produces distinct-channel/install facts;
  A/B runner produces efficiency facts.
- Consumer: critique artifact consumes verdict identity; release artifact
  consumes observer evidence; quality report consumes comparable efficiency
  runs.
- Owning surface: `critique`, `release`, and `quality` respectively; root CLI
  owns the app-server protocol helper.
- Verdict: owned-correctly

## Deliberately Not Doing

- No tmux/team runtime, universal consensus workflow, hard default-reduction
  gate, npm tarball machinery, or TUI/process-hook import.
- No Cautilus evaluation: this plan changes no prompt/skill behavior and the
  ask-before-run planner was not triggered for source inspection/spec authoring.

## Next Move

The corrected spec is ready for `impl` Slice 1 only. Later slices remain
independently stoppable; probes do not silently promote themselves into build
work.
