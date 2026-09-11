# Spec: Achieve learns before commitment

Date: 2026-09-11
Issue: corca-ai/charness#812

## Problem

Achieve already coordinates `ideation`, `spec`, and later workflow owners, and capable fresh agents can infer a useful reality-first sequence from the current guidance. That behavior is not yet the explicit planning handoff: an agent can list a direction-invalidating assumption, accept internally green evidence, and continue toward a complete Goal Draft without stating which sufficiently real observation should decide whether the direction deserves a spec. The existing reviewed Achieve dogfood case starts at late push/confidence work and cannot expose this miss.

## Capability Contract

When Achieve shapes a consequential objective, it owns orchestration: it detects unresolved uncertainty that could change the direction before the next cheap reversible step and routes that uncertainty to ideation. Ideation owns whether reality contact is needed and what the cheapest sufficiently real probe is. Achieve then sequences the returned probe and enters spec only after the concept-level uncertainty is observed, explicitly accepted, or deferred with a reason that keeps the current step honest. Spec-local mechanism uncertainty remains a `Probe Question` rather than bouncing the whole goal backward.

## Current Slice

Clarify the existing orchestration and learning sequence; update the reviewed Achieve dogfood case and focused contract tests; run the same consequential fresh-agent prompt before and after the change plus one routine contrast. Do not add a new artifact schema, router, validator, or execution engine.

## Fixed Decisions

- Achieve remains the orchestration owner. It decides that unresolved direction-level uncertainty needs an owner before commitment and routes it; it does not independently design the probe. There is no second early-planning router.
- `ideation` owns concept shape, assumption ranking, and whether/how reality contact is needed. `spec` owns fixed/probe/defer classification once the concept is stable enough. Achieve selects and sequences those owners and carries their result into the Goal Draft.
- Do not manufacture a separate probe when the next cheap reversible step itself will produce the needed observation before commitment. Record the uncertainty and the expected observation, take that step, then reconsider the route.
- Extend the shared generative-sequence principle only with the missing learning transition: observe first, separate observation from interpretation, diagnose ownership/derivation/boundary/proof before choosing a structural response. Do not add a shared mutable packet.
- “Sufficiently real” is claim-relative. Fresh-agent, user, provider, or live execution is selected only when that actor or boundary is part of the claim; local deterministic evidence remains valid for local structural claims.
- The checkpoint is judgment-led. Static tests pin the instruction and dogfood contract, not the semantic correctness of every future route.
- The existing Goal Draft, ideation artifact, spec, debug artifact, and proof owners retain durable state. No new cross-phase record is introduced.

## Probe Questions

- Can the shared learning sequence and Achieve coordination wording stay short enough to strengthen judgment without becoming a checklist? Resolve through pre-implementation critique and final reader review.
- Does the candidate preserve the baseline's good route while making its five-part decision trace explicit: direction-invalidating assumption, claim-relative observation, selected owner, observation versus interpretation, and result-dependent next move? Observe after candidate integration; do not infer from static tests.

## Deferred Decisions

- Automated multi-turn model evaluation is deferred. The current dogfood registry explicitly records operator-reviewed evidence and has no full prompt-routing evaluator; this slice will not build one.
- Metrics such as assumption survival time and rework amplification remain retro candidates until repeated use establishes a useful denominator.
- Phase-local changes to `debug`, `impl`, `quality`, `prove`, `hotl`, and `retro` are deferred unless critique finds a concrete missing consumer. Their current contracts already own the relevant local decisions.

## Non-Goals

- Requiring a fresh-agent or live-provider test for every goal.
- Making every uncertainty block planning.
- Duplicating the sequence across nine skill bodies.
- Encoding Ceal CLI vocabulary in Charness.
- Treating a passing scenario review as universal model-behavior proof.

## Deliberately Not Doing

- No reality-learning packet, phase enum, lifecycle state machine, or new gate.
- No replacement of Achieve's current interview, approval, Goal Binding, or issue-provider contracts.
- No incident-specific deterministic test that pretends to prove model judgment.

## Constraints

- Preserve the design north star: judgment for reversible work, principle over rulebook, and distinct evidence at irreversible boundaries.
- Preserve one concept per public skill and one canonical owner per fact.
- Source changes must be synchronized to generated plugin mirrors through the existing exporter.
- The worktree's unrelated `execution-result-consumer` debug interrupt is not slice-affine; the risk planner returned `not-applicable` when passed the #812 paths.

## Success Criteria

1. An Achieve agent is explicitly told to choose the next learning move before commitment, not merely enumerate risks.
2. The handoff distinguishes direction-invalidating concept uncertainty from bounded implementation uncertainty.
3. A failure observation leads through ownership/derivation/boundary/proof diagnosis before a mechanism is selected.
4. Evidence claims remain proportional: structural evidence does not satisfy actor/live effectiveness, and live proof is not imposed on local-only claims.
5. Routine reversible goals retain a direct path without a new packet or mandatory probe.
6. The reviewed Achieve dogfood prompt exercises early under-shaped planning without naming `ideation`, `spec`, assumptions, or probes.

## Acceptance Checks

- `manual`: preserve the two baseline fresh-agent observations. Both current agents chose a reality-first probe, establishing that the change should clarify and stabilize an existing good judgment rather than invent a new capability.
- `manual`: run this actor-effect prompt through a fresh agent: “Use Achieve to take this long-running objective from concept to an approved build plan: make generated task artifacts sufficient for a fresh agent to execute the right path without extra operator explanation.” It must identify fresh-agent sufficiency as direction-invalidating, route the uncertainty to ideation, select an actor-observing probe before spec/approval, separate the eventual observation from interpretation, and state different next moves for pass and fail. Fail if it completes or seeks approval for a Goal Draft without that observation/disposition, or responds only with the new vocabulary.
- `manual`: run this paired local-structure prompt through a fresh agent: “Use Achieve to take this long-running objective from concept to an approved build plan: make generated task artifacts preserve their declared schema and byte-stable regeneration across source and plugin mirrors.” It should use repository inspection and deterministic regeneration evidence, and should not require a fresh-agent/user/provider probe unless inspection exposes a separate actor-facing claim. The paired routes must differ because the claim boundary differs, not because one prompt is labeled routine.
- `manual`: preserve the exact prompts and a structured observation of both results against the five-part decision trace. Raw model prose remains session evidence rather than a new canonical contract. These two observations are bounded cases, not a general model-improvement claim.
- `manual`: confirm that the decisive basis survives in existing Goal Draft surfaces: evidence identity in `Context Sources`, the interpretation and chosen direction in `Interview Decisions`, and any remaining claim/evidence gap in `Agent Verification Plan`. A later spec-planning reader must recover why the concept was settled or dispositioned without hidden transcript reasoning.
- `unit`: focused Achieve before-activation tests pin orchestration ownership, the learning-before-commitment transition, the concept-vs-mechanism discriminator, and the no-universal-probe escape.
- `unit`: public-skill dogfood tests prove the registry carries and exposes the new Achieve acceptance evidence.
- `integration`: public skill validation, dogfood validation, documentation checks, and source/plugin export comparison pass on the integrated tree.

## Boundary Ownership

- Producer: Achieve produces the planning sequence and Goal Draft; ideation produces concept/risk/probe judgment; spec produces the implementation contract; actor/provider probes produce external observations.
- Consumer: the operator approves the exact briefing; spec and later Work Items consume the settled/dispositioned concept; future agents consume the frozen Goal Draft.
- Owning surface: Achieve coordination owns selection and handoff; shared generative sequence owns only reusable ordering; public dogfood owns reviewed consumer expectation.
- Verdict: owned-correctly, provided the change does not add shared state or make the shared reference Achieve-specific.

## Critique

Round 1 used two file-backed read-only workers over packet `charness-artifacts/critique/2026-09-11-110557-packet.json`; both delivered blocking findings.

- Act Before Ship: define an outcome-sensitive behavioral rubric and paired claim-boundary prompts; route ownership was ambiguous between Achieve and ideation; the cheap-reversible-step escape and durable Goal Draft consumer trace were missing. All are repaired in this revision.
- Bundle Anyway: keep raw before/after outputs and explicit fail conditions with the manual dogfood evidence.
- Over-Worry: the baseline already behaving well does not make clarification valueless, and no automated evaluator or new schema is required.
- Valid but Defer: general model-behavior improvement, automated multi-turn evaluation, and rework metrics retain their existing deferred/non-claim status.

Fresh-Eye Satisfaction: worker-delivered, blocking round consumed; follow-up review required before implementation.

Follow-up review: `issue-812-spec-followup` delivered `pass` and was approval-eligible after reading the repaired whole. Packet `charness-artifacts/critique/2026-09-11-110758-packet.json`; reviewed-input identity `69a0bba4b6eb213413d4fd0f031ff64ae82157bed0801c5fa6610f7e36fc8328`; findings identity `3bc620c3261602f808f77f521afb5ac55c92bb54e7d025482be4e24359828f54`; durable worker report `charness-artifacts/critique/workers/issue-812-spec-followup/worker-report.yaml`. Implementation is allowed against this revised contract.

The integrated-code review over packet `charness-artifacts/critique/2026-09-11-111723-packet.json` delivered two block verdicts. Act Before Ship findings were: the dogfood registry accidentally described evidence preservation as an Achieve behavior contract; pass/fail routes were not explicit in the Achieve handoff; tests recopied whole prose/contracts; and detailed ownership appeared in too many surfaces. The repair keeps the shared sequence as the reusable owner, keeps Achieve-specific routing and Goal Draft destinations in Achieve, shortens the coordination table, requires contrasting-result routes, and reduces static tests to structural/load-bearing anchors. The request for every Achieve run to preserve raw prompt/result is rejected as misplaced ownership; this spec records the bounded dogfood observation instead.

## Candidate Dogfood Observation

Candidate source: working tree after the integrated-code review repairs to commit `bd1272ac8`.

### Actor-effect case

Exact prompt: “Use Achieve to take this long-running objective from concept to an approved build plan: make generated task artifacts sufficient for a fresh agent to execute the right path without extra operator explanation.”

- Direction-changing uncertainty: whether the artifact is insufficient for an unbriefed agent, or whether the missing owner is upstream briefing/pickup/documentation.
- Selected owner: `ideation` decides whether/how to run reality contact; task-result, task-launch, or pickup ownership follows the observation rather than being assumed.
- Evidence boundary: a fresh agent must select and safely execute the prescribed action from real contrasting task states; schema/unit evidence is explicitly a non-claim for comprehension.
- Observation versus interpretation: emitted fields and deterministic tests were recorded as observations; their usability was kept as an unproven interpretation pending the actor probe.
- Contrasting-result routes: success avoids schema expansion; missing actionable data enters a task-result spec; missing upstream intent moves ownership to launch/Work Item; state-dependent results narrow and repeat the smallest probe.
- Disposition: meets the five-part trace and does not proceed to spec or approval before the observation or honest disposition.

### Local-structure case

Exact prompt: “Use Achieve to take this long-running objective from concept to an approved build plan: make generated task artifacts preserve their declared schema and byte-stable regeneration across source and plugin mirrors.”

- Direction-changing uncertainty: whether byte stability applies to purely derived outputs or incorrectly includes volatile receipts containing timestamps, PIDs, paths, and logs.
- Selected owner: repository source/export/schema owners; one operator scope decision remains before spec.
- Evidence boundary: local classification, canonical fixtures, source/plugin regeneration, byte comparison for purely derived artifacts, and negative schema cases.
- Observation versus interpretation: producer/schema/mirror facts must be inventoried before interpreting a parity gap as a product defect.
- Contrasting-result routes: accept deterministic parity for derived outputs; preserve runtime evidence and use schema/validation rather than byte identity for volatile receipts.
- Disposition: explicitly refuses fresh-agent and provider probes because neither actor is part of the claim. Local deterministic observation is sufficient before spec/approval.

Paired verdict: the routes differ on the evidence-owner axis while keeping the prompt form and planning consequence similar. This is bounded evidence that the candidate supports claim-relative routing; it is not a general model-behavior improvement claim.

Consumer boundary check: `Ceal` and `Daily Scrum` are absent from the changed public skill, shared reference, dogfood registry, and focused tests. The originating consumer episode remains only in issue/spec provenance; shipped behavior is expressed through generic actor, artifact, claim, and owner concepts.

## Implementation Evidence

- Isolated task candidate `db9c6058c` changed only the six declared source/test paths; task receipt was approval-eligible and changed-line status was `noop` because no mutation-pool files changed.
- Parent integrated the candidate as `bd1272ac8`, ran the canonical plugin exporter, and byte-compared the three generated Achieve/shared mirrors.
- Focused tests: `9 passed`.
- `python3 -m tools.validate_public_skill_dogfood --repo-root .`: 19 cases and 19 required skills validated.
- `python3 -m tools.validate_skills --repo-root .`: 21 skill packages validated.

## Canonical Artifact

This spec is the implementation contract. The issue brief remains the pre-mutation discussion record; actual implementation observations and review dispositions will be appended here.

## First Implementation Slice

After critique, edit the shared sequence and Achieve coordination/body together, then update the existing Achieve dogfood case and focused tests. Synchronize generated plugin mirrors once after source edits and run focused validation before broader applicable checks.
