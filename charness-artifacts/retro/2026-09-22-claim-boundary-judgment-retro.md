# Claim Boundary Judgment Retro

Date: 2026-09-22

## Context

Goal #862 repeatedly needed the operator to challenge plausible-looking mechanisms and proofs: a redundant `--json` choice despite an always-structured output contract, a synthetic activation marker with no product reader, stale premises carried into implementation, and lower-level fixtures promoted into release or product evidence. Two earlier Charness commits improved isolated `require-change` task lanes, but this review asks why native subagents and direct implementation or proof work could still repeat the class.

## Evidence Summary

- Charness commits `33f5709f2` and `11bae815d` add premise, consumer, product-state, owner, and lower-level-proof judgment to `build_lane_prompt`; source inspection showed that carrier runs only for isolated `require-change` task lanes.
- `skills/public/impl/SKILL.md` previously accepted the implementation contract without challenging the requested mechanism's premise, consumer, owner, or proof level; `skills/public/prove/SKILL.md` identified a claim but did not require a boundary-capable observer or falsifier.
- The current Ceal operating contract already teaches concept-before-mechanism and the verification ladder, so another Ceal-local checklist would duplicate standing policy rather than improve portable agent routing.
- Focused verification after the repair: 90 selected tests passed; `python3 -m tools.check_skill_contracts --repo-root .` passed; 21 skill packages validated; plugin export contained the new shared reference and both consuming skill routes.

## Waste

The prior repair changed one carrier rather than the complete population of agents that make the decision. It improved isolated task execution but left direct `impl`, direct `prove`, and native subagent routes dependent on whether a consuming repository happened to restate the same principles. That made the operator the only reliable cross-route observer. The second waste was accepting a test or fixture by shape before naming the evidence level it could actually observe, which let local green become an implicit higher-level claim.

## Critical Decisions

- One four-axis judgment frame now owns concept/premise, named consumer and distinct state, canonical behavior owner, and evidence level with observer/falsifier. `impl`, `prove`, and task-run transport it at their distinct decision points rather than each inventing a checklist.
- No new gate, receipt, schema, planner, or mandatory artifact was added. These are semantic judgments on reversible work; deterministic enforcement would encode examples and still miss the next smell.
- Fixtures and simulations remain valid evidence at an honestly labelled lower level. The frame blocks promotion and substitution, not useful component testing.
- An out-of-scope product owner produces the existing typed premise/scope escalation before editing; scope constrains writes, not judgment. A missing higher-level observer may instead narrow the claim within user intent and retain the higher non-claim.

## North Star Alignment

P1 and P3 govern the repair: equip the capable judge with one compact frame instead of adding a gate or enumerating every bad flag, marker, or fixture. P2 holds because the frame is one concept with one shared owner and the public skills only route to it. P4/P5 apply when a lower-level result is about to become release, live, provider, or other escaping evidence; the observer must operate at that boundary, while ordinary local work stays judgment-led. The prior task-run-only repair was not wrong, but it mistook one carrier for the full consumer population.

## Expert Counterfactuals

- Gary Klein pre-mortem on the claim: before coding, assume the requested mechanism is redundant or the success sentence is false and ask which real consumer would notice. For `--json`, no alternate output state exists; for the activation marker, no product consumer reads it; for a fixture-only proof, the release observer cannot see it. This one move would have stopped all three before diff production.

## Sibling Search

- same layer: `scripts/task_run/task_run_lane_runner.py` | decision: same waste, fixed now | proof: the carrier now transports all four axes and preserves typed escalation plus honest lower-level evidence.
- specialization down: `skills/public/impl/SKILL.md` and `skills/public/prove/SKILL.md` | decision: same waste, fixed now | proof: native/direct skill routes consume the shared owner before editing or claiming success.
- abstraction up: Ceal `docs/core-operating-principles.md` and `docs/agent-operating-rules.md` | decision: intentional boundary | proof: they own repo policy; the shared Charness frame operationalizes the decision across consuming repositories without copying Ceal product policy.
- mental-model sibling: `skills/public/spec/SKILL.md` | decision: intentional boundary | proof: spec already names actor, capability delta, acceptance checks, and boundary ownership; forcing the implementation/proof frame there would duplicate its concept-shaping job.

## Next Improvements

- workflow: start requested mechanism changes by applying the four axes before accepting the request's shape; if they do not align, escalate before editing.
- capability: retain `skills/shared/references/claim-boundary-frame.md` as the single owner consumed by `impl`, `prove`, and the isolated task carrier; add no second evaluator until observed rework shows judgment still fails after the frame is read.
- memory: preserve this retro and `charness-artifacts/create-skill/2026-09-22-claim-boundary-frame-brief.md` as the evidence and capability contract; do not add a duplicate lesson-ledger rule.

## Portable Candidate

- Abstract pattern: validate concept, consumer/state, behavior owner, and evidence level/observer before mechanism edits or success claims.
- Triggering evidence: three distinct Goal #862 corrections crossed redundant interface, synthetic state, and proof-level promotion while sharing the same missing judgment.
- Intended consumer/repo shape: any agentic implementation repository using public `impl` or `prove` workflows or isolated implementation lanes.
- Destination: `create-skill`, implemented in the shared reference and two public skill routes.
- First-prompt acceptance claim: a request for a redundant output option or synthetic release proof is challenged before editing, while a labelled unit simulation remains permitted as unit evidence.

## Packet Consumed

`charness-artifacts/retro/2026-09-22-010716-packet.md` reported the adapter's two deterministic sections. The rework-issue section confirmed `impl` is the most frequently attributed public skill in the current window; the changed-files section described only an unrelated usage-episode file and did not inform the repair.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-09-22-claim-boundary-judgment-retro.md
Seeding: none pending
