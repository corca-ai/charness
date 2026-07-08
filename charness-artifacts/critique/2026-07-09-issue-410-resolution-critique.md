# Resolution Critique — issue #410 (reference-compaction Slice 7 sweep, remaining queue)

- **Target**: pre-close resolution critique for the final #410 queue execution
  (handoff pickup MOVE, hotl MIXED lift, setup/greenfield capture-proven KEEP,
  spill-targets FINAL keep).
- **Execution**: 1 bounded fresh-eye batch reviewer (file-reported), findings
  triaged by the resolving agent; reviewer ran the validators itself.
- **Fresh-Eye Satisfaction**: parent-delegated (repo `Subagent Delegation` contract).
- **Packet Consumed**: /tmp/slice9-critique-report.md (reviewer output; verbatim
  findings mirrored below).

## Change

Close #410 by exhausting the slice7-census-reconciliation capture-gated queue:

- **Slice 9 (handoff pickup)**: planner stops forcing `workflow-trigger.md` for
  pickup (`e4f3626d`); pickup RCF `[]` on a NEW dir-scoped substance judge
  (`outcome-assertions.json`); pickup-ambiguous RCF `[continuation-sequence.md]`
  (clean-MOVE). Fresh capture: flipped spec PASS, old spec FAILED the same run,
  judge 4/4, mention-only probe fails.
- **Slice 9b (hotl)**: `verified_against.*` / `disposition.*` / ODQ five-field
  tokens lifted into SKILL.md step 5 (`8bdf9fda`); doc-open floor unchanged and
  re-proven by a confirming capture (2/2 DEPTH).
- **Slice 9c (setup greenfield)**: `capture-skill-run.sh --run-cwd` (fresh
  non-charness sandbox); two captures prove the RCF floor genuinely load-bearing
  → capture-PROVEN KEEP, census MOVE refuted per-condition; observed RSF tokens
  pinned; ideation-carrying prompt fixed the unfixturable dead end.
- **spill-targets.md**: FINAL keep-DEPTH disposition recorded (routing table
  absent from SKILL.md; capture-proven genuine open).

## Capability at Stake

Every evaluator-required public skill's claim-fidelity floor must be honest
(observed, falsifiable, matcher never softened) after the RCF→RSF/substance
compaction — a wrong floor either false-fails faithful runs or silently
green-lights the guarded failure mode (mention-only pickup, boilerplate
scaffolding, proxy-only verification).

## Angles + Findings

1. **Over-relaxation (pickup RCF=[])** — reviewer verdict: largely unfounded.
   The judge assertion is compound (identify trigger AND verify live state via
   an independent channel AND start-or-name-boundary); the planner structure
   stays deterministically pinned in `tests/test_handoff_plan.py`; advisory
   substance floors match repo precedent (debug/gather/setup).
2. **Evidence gap (falsifiability probe)** — the finding.md claimed a judged
   mention-only probe the bundle did not contain. Fixed before close: probe
   re-executed and saved as `falsifiability-probe.json` (verdict: fail) in the
   bundle; finding.md now cites it and discloses the first run was
   transcript-only.
3. **Capture blinding leak** — the captured agent can read its own eval
   identity from the out-dir path (observed in the pickup transcript). Real
   harness integrity gap, predates this slice, passes independently grounded →
   filed as #423, not blocking.
4. **hotl** — lifted tokens verbatim-match the reference; anti-proxy DEPTH
   correctly un-lifted; capture genuine (`cat` of the reference, heavy faithful
   proof loop). Stale `max_duration_ms` (observed 835,853 ms vs pinned 510,000)
   fixed before close: re-baselined to 1,700,000.
5. **Greenfield fixture honesty** — synthetic 'logtrim' ideation is legitimate
   fixture INPUT (names no floor doc, games no matcher); RSF tokens verbatim in
   the transcript (observed-not-assumed); KEEP-vs-census reasoning matches the
   reconciliation doc's own METHOD CORRECTION.
6. **Harness `--run-cwd`** — default path provably unchanged, mirror
   byte-identical, live-proven twice; static pin test added before close.
7. **Validators re-run by the reviewer** — claim-fidelity specs, scenario
   conditional reads, handoff planner tests, outcome-assertion schema: all green.

## Structured Findings

<!-- bins: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer -->
- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/cautilus/handoff-pickup-slice9-2026-07-09/falsifiability-probe.json | action: fix | note: the one load-bearing counter-evidence claim was unbacked in the bundle; probe re-executed and persisted, finding.md now cites it honestly.
- F2 | bin: act-before-ship | evidence: strong | ref: evals/cautilus/hotl-claim-fidelity/spec.json | action: fix | note: max_duration_ms 510000 was already exceeded ~64% by the just-proven representative run; re-baselined to 1700000 (~2x observed).
- F3 | bin: bundle-anyway | evidence: moderate | ref: tests/test_skill_efficiency_ab.py | action: fix | note: static pin for --run-cwd default fallback + missing-dir refusal, mirroring the existing capture-script recurrence guards.
- F4 | bin: valid-but-defer | evidence: strong | ref: scripts/agent-runtime/capture-skill-run.sh | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/423 | note: eval-identity leak into the captured run's view (out-dir name, justification.md) — filed; passes stand because behavior was independently grounded.
- F5 | bin: over-worry | evidence: weak | ref: evals/cautilus/handoff-claim-fidelity/outcome-assertions.json | action: defer | note: "boundary-naming arm is a lazy-run loophole" — refuted by the compound assertion clauses plus the deterministic planner tests; the probe proves the lazy shape fails.

## Counterweight Triage

- **Act Before Ship**: F1 (probe artifact), F2 (hotl threshold) — both executed
  before the close commit.
- **Bundle Anyway (this commit)**: F3 (harness pin test).
- **Over-Worry (ignored)**: F5 (loophole concern — disproven by the probe and
  the compound clause structure).
- **Valid but Defer**: F4 (capture blinding → #423 with the transcript evidence).

## Deliberately Not Doing

- No re-flip of the setup/greenfield or spill-targets doc-open floors (both are
  now capture-proven load-bearing; retiring them would be the over-relaxation
  the guardrail names).
- No matcher change (#415 class stays closed; floor MISSes were treated as
  fixture/skill-shape signals throughout).
- No pinned-task pickup scenario in this slice (the boundary-naming arm is
  proven and mention-only is red; a startable-task fixture is a scenario
  candidate, recorded in the bundle finding, not #410 debt).

## Boundary Ownership

- Owning surface: each mutation landed in its producer surface — pickup routing
  in the handoff planner (`plan_handoff_run.py`), floors in the owning
  `evals/cautilus/*` specs + registry, harness capability in
  `scripts/agent-runtime/capture-skill-run.sh` (mirrored), the queue record in
  `charness-artifacts/reference-compaction/`, and the leaked-identity gap in a
  new issue (#423) because its owner is the harness, not this resolution.
- Verdict: owned-correctly

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied -->
- Requested tier: high-leverage
- Requested spawn fields: model=sonnet
- Host exposure state: requested_fields_sent
- Application state: model=sonnet requested via the Agent tool's model option, not host-confirmed; file-reported to survive the session's unreliable subagent return channel

## Next Move

Commit the flip set with close keywords + behavioral verdict, push, verify
GitHub CLOSED state, refresh the handoff.

Fresh-Eye Satisfaction: parent-delegated
