# Achieve Goal: START HERE — skill claim-fidelity + doc-philosophy across ALL skills (public + support)

Status: active
Created: 2026-06-23
Activation: `/goal @charness-artifacts/goals/2026-06-23-skill-claim-fidelity-doc-philosophy.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: active; Slices 1-2 are complete and logged.
- Current slice: Slice 3 — choose the #397 remediation from the quality reference classification.
- Current slice intent: use the 9 engage-always / 27 on-demand / 3 gate-sufficient distribution, with `quality-lenses.md` as the required engage-always discriminator, to choose gate triage, reference routing, or both before behavior edits.
- Next action: record the remediation decision and rationale in this goal before editing the quality skill flow or harness wiring.
- Verification cadence: cheap deterministic checks (markdown/link gates, `run_slice_closeout.py --skip-broad-pytest`, observed-packet parse) at commit boundaries; fresh-eye critique + a real `claude -p` capture at slice boundaries; ONE operator-gated cautilus rollup at the validation boundary.
- Slice review packet: before fresh-eye slice critique, hand the reviewer intent, changed files + owning/generated surfaces, expected invariants, tests/proof, non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`, and `## Auto-Retro`.

## Goal

START HERE — skill claim-fidelity + doc-philosophy across ALL skills (public + support)

**Source handoff entry #1: START HERE — skill claim-fidelity + doc-philosophy across ALL skills (public + support)**

> Framing is **SETTLED** (operator 2026-06-22): the
>   **per-doc 3-way axis** — **engage-always** (a real run must read it; 0 reads =
>   execution-shape defect), **on-demand** (read only when sought; claim must say
>   so), **gate-sufficient** (a deterministic gate already yields its conclusion →
>   **deletable**, but ONLY via this axis, NOT the rejected reachability heuristic;
>   ref-value stays settled). **First move: write the methodology `spec` encoding
>   the axis** — do NOT re-litigate the framing — then **pilot quality (#397)**:
>   classify its 39 docs, add per-ref engagement tags to `spec.json` (the
>   gates-green-but-lens discriminator), pick remediation (front-load gate triage /
>   wire refs into gate findings), then fan out. Each run = expensive `claude -p`
>   capture + gated `cautilus evaluate observation` (cautilus 0.17.1, re-verified).

**Shaped scope (this goal):** write the methodology spec → fully pilot it on
quality (#397) → **begin** fan-out (1–2 more skills) to prove the methodology
generalizes. The full all-skills fan-out remains an explicit follow-up.

## Non-Goals

- Not re-litigating the per-doc 3-way axis framing (SETTLED 2026-06-22) or the 2026-06-21 reference-value disposition (delete 0; "discoverability gap, not bloat").
- Not pruning/deleting references via the rejected reachability heuristic; deletion is reachable only through the gate-sufficient axis and is not itself a goal of this run.
- Not a release: no plugin version bump expected.
- Not the full fan-out across ALL skills — only begin with 1–2 to validate generalization.
- Not solving the #397 sub-gap (no canonical home for a diagnostic `reject`) unless it blocks the single validation run; file as off-goal otherwise.

## Boundaries

- In scope: the methodology spec contract doc (location per the `spec` skill, likely a `docs/` convention surface); per-ref engagement tags on `evals/cautilus/quality-claim-fidelity/spec.json`; the quality skill remediation; claim-fidelity harness wiring; 1–2 additional skills' doc classification.
- Portable per implementation-discipline: no host-specific assumption baked into the methodology. Honest residual — the capture harness is claude-runtime-specific by design (it tests the claude-installed `/charness:quality` via `claude -p`); that is a known boundary, recorded as a non-claim, not a portability defect to fix here.
- Cautilus is eval-only / ask-before-run: consult `python3 scripts/plan_cautilus_proof.py --repo-root . --json`, use the `scripts/run_cautilus_eval.py` wrapper, never bare `cautilus evaluate`. Exactly ONE run authorized for this goal (operator).
- Editing the quality skill is a behavior-affecting public-skill prompt change: recent-lessons read (done); sync exports/mirrors before validators; fresh-eye critique required at the remediation slice.
- spec.json shape change is verified against `build-skill-execution-observation.mjs` *before* relying on the tagged file (read-the-schema-before-persisting lesson).
- New files (spec doc, harness additions) may need a `.agents/surfaces.json` entry (surfaces-coverage lesson).
- Stop conditions: name on first discovery; do not guess. Escalate (do not re-litigate solo) if classification reveals the axis genuinely does not fit a skill; ask the operator if one cautilus run turns out insufficient to call the verdict.

## User Acceptance

What the user can do to verify completion directly:

- Read the methodology spec doc and confirm it encodes the 3-way axis (engage-always / on-demand / gate-sufficient) and the per-ref engagement-tag contract — without re-litigating the framing.
- Open `evals/cautilus/quality-claim-fidelity/spec.json` and see a per-ref engagement classification across quality's 39 references, with `build-skill-execution-observation.mjs` still parsing it.
- Read the recorded remediation decision + rationale (chosen after classification).
- **(Primary, locally verifiable)** See the deterministic coverage shift `0/39 → ≥1/39 including quality-lenses.md` from `observed.json` (README steps 1–2, no gate), backed by an actual runtime read/open of `quality-lenses.md` in the captured session tree. This number is the host-side matcher's output, not cautilus's judgment, and it is the success signal; matcher-only/spec-only changes are not closeout evidence.
- **(Secondary, operator-gated)** See the single post-remediation cautilus rollup verdict compared to the 2026-06-22 `reject` baseline at `5a9d6fa8`. Note: cautilus may still report `reject` on the `runtime_budget_respect` dimension alone (duration) even when coverage is fixed; a still-slow run is NOT a coverage-fix failure.
- Read the fan-out classification notes for the 1–2 additional skills and the generalization finding.

## Agent Verification Plan

### Low-Cost Checks

- Markdown + link gates on the new spec doc; `run_slice_closeout.py --skip-broad-pytest` at pre-lock commit boundaries.
- `node scripts/agent-runtime/build-skill-execution-observation.mjs` parses the tagged `spec.json` without error (deterministic shape check).
- `validate_skills` when the quality skill surface is edited; mirror-drift gate on exported surfaces.

### High-Confidence Checks

- A real isolated `claude -p "/charness:quality"` capture at the remediated ref via `capture-skill-run.sh`, scored into an observed packet → deterministic coverage shift vs the 0/39 baseline (the observed packet already carries the deterministic claim/coverage verdict).
- Fresh-eye slice critique on the remediation (behavior-affecting public-skill change) and on the methodology spec.

### External Or Live Proof

- ONE operator-gated `cautilus evaluate observation` rollup on the post-remediation arm, run through the `run_cautilus_eval.py` wrapper after `plan_cautilus_proof.py` clears it. Compared to the 2026-06-22 `reject` baseline. No provider/live claims beyond this single rollup; the baseline is the "before", the single run is the "after".
- **Signal separation (folded from plan critique).** The baseline failed BOTH `skill_task_fidelity` (0/39) and `runtime_budget_respect` (755169ms > 600000ms). The **primary** success signal is the deterministic coverage shift from the observed packet, backed by a real runtime consultation of `quality-lenses.md`; the cautilus recommendation and the `runtime_budget_respect` dimension are **secondary** and reported separately. A coverage-fixing remediation that stays slow will still draw a cautilus `reject` on duration alone — that is not a coverage-fix failure and does not by itself block #397 closeout.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Author the methodology spec encoding the 3-way axis + per-ref engagement-tag contract + classify/remediate/prove methodology | The axis is settled; everything downstream applies one written contract uniformly | Committed spec/contract doc; passes link + markdown gates | planned |
| 2 | Classify quality's 39 refs against the axis; add per-ref engagement tags to the eval `spec.json` (verify matcher tolerance first) | The engage-always set is the gates-green-but-lens discriminator that picks remediation | Tagged `spec.json` + per-ref rationale; observation builder still parses | planned |
| 3 | Choose the #397 remediation from the classification (front-load gate triage / wire-refs-into-findings / both) | Decided-after-classification per operator; classification is the input | Recorded remediation decision + rationale in this artifact | planned |
| 4 | Implement the chosen remediation on the quality skill flow + harness wiring; fresh-eye slice critique | The fix is the point of #397; behavior-affecting change needs critique | Edited skill surface, synced exports/mirrors, slice critique findings | planned |
| 5 | Validate: capture remediated `/charness:quality`, build observed packet (PRIMARY = deterministic coverage shift from runtime consultation), then ONE operator-gated cautilus rollup (SECONDARY, may degrade on duration alone) | The single operator-authorized validation; baseline reject already on record | observed.json coverage `0/39 → ≥1/39 incl. quality-lenses.md` backed by a captured read/open event (primary) + one cautilus summary (secondary) vs `5a9d6fa8` baseline | planned |
| 6 | Begin fan-out: classify 1–2 more skills' docs against the axis; record whether the same execution-shape gap appears | Operator chose to begin fan-out; validates the spec beyond quality | Per-skill classification notes + a generalization finding | planned |

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

Seeded:

- Decision: confirm the single cautilus run at the Slice 5 boundary (eval-only / ask-before-run)
- Owner: operator
- Why deferred: pre-authorized in shaping ("코틸러스 런 하나만"); local Slices 1–4 proceed safely first
- Unblock action: operator confirms when `plan_cautilus_proof.py` names the post-remediation observed packet as the failing/target log
- Revisit trigger: reaching Slice 5 with a remediated capture in hand

## Coordination Cues

Defer *which* skill owns each phase to `find-skills`
(`--recommend-for-task` / `--recommendation-role`), recorded as the run reaches
each boundary — not a baked-in phase→skill map.

- Slice 1 (methodology spec) → query find-skills for the upstream contract owner (`spec`).
- Slice 4 (remediation) → query find-skills for the skill-edit owner (`impl`); validation-shaped closeout → `quality` before HITL/manual.
- Slice 5 (validation) → cautilus eval-only contract; off-goal findings → `issue`.
- #397 closeout → staged through `issue` (`Close #397` on the remediation carrier) **only if the closeout predicate holds**: the captured run actually reads/opens `quality-lenses.md`, and observed coverage rises `0/39 → ≥1/39 including quality-lenses.md`. Duration / `runtime_budget_respect` is reported but is NOT a close-blocker — #397's stated defect is the 0/39 mechanism gap, not the time budget. If runtime consultation does not move, leave #397 open with the evidence recorded.
- Gather: n/a — sources are repo-internal; cautilus is an integration tool, not an external URL source.
- Release: n/a — no version bump or install-manifest edit expected.

## Discuss before activation:

RESOLVED — all three items below were discussed with the operator during shaping
(2026-06-23) and confirmed. Three consequential items, all resolved in shaping:

1. **Operator-gated cautilus run (cost + eval-only boundary).** Resolved: operator pre-authorized exactly ONE run for the post-remediation arm; baseline `reject` (0/39, `5a9d6fa8`) is the "before". Still routed through `plan_cautilus_proof.py` + `run_cautilus_eval.py`, with a confirm at the Slice 5 boundary (Operator Decision Queue).
2. **Behavior-affecting public-skill prompt change.** Resolved: in-scope and intended (the #397 remediation edits the quality skill flow); guarded by sync-before-verify, `validate_skills`, and mandatory fresh-eye critique.
3. **Broad scope (begin fan-out).** Resolved: scope is bounded to 1–2 additional skills to validate generalization; full all-skills fan-out is an explicit follow-up, not this goal.

## Slice Log

### Slice 1: Methodology spec

- Objective: Author the skill claim-fidelity/doc-philosophy methodology spec encoding the three-way engagement axis, tag contract, and proof boundaries.
- Why this approach: Slice 1 is the dependency for quality classification and remediation; the operator settled the axis, so implementation needed a written contract.
- Commits:
- What changed: Added charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md; added charness-artifacts/critique/2026-06-23-skill-claim-fidelity-doc-philosophy-spec-critique.md; flipped the goal artifact to active.
- Alternatives rejected: Rejected treating coverage count alone as #397 closeout; rejected gate-sufficient as deletion-candidate wording; rejected an object list inside declaredReferences because the current builder treats it as a string list.
- Targeted verification: check_goal_artifact.py --pursue-ready passed before activation; charness worktree doctor passed; check_doc_authoring_preflight passed for the spec; check-markdown.sh passed; check_doc_links.py passed; build-skill-execution-observation.mjs smoke command over the checked-in 2026-06-22 baseline bundle reproduced coverage=0/39; validate_critique_artifacts.py passed for the critique artifact; run_slice_closeout.py --skip-broad-pytest passed.
- Test duplication pressure: none — documentation/spec slice only; no tests added or expanded.
- Critique: Fresh-eye spec critique completed with 3 angle reviewers + 1 counterweight reviewer; Act Before Ship findings folded into the spec; critique artifact: charness-artifacts/critique/2026-06-23-skill-claim-fidelity-doc-philosophy-spec-critique.md.
- Off-goal findings: none.
- Lessons carried forward: Next slice starts from referenceEngagement beside declaredReferences; #397 proof must show runtime consultation of quality-lenses.md, not matcher theater; remediation decision must be recorded before behavior edits.
- Metrics: Host token/tool metrics not available; reviewer agents completed and were closed.

### Slice 2: Quality reference classification

- Objective: Classify all 39 quality skill declared references against the three-way engagement axis and add compatible metadata to the quality claim-fidelity eval spec.
- Why this approach: The classification is the gates-green-but-lens discriminator for choosing #397 remediation.
- Commits:
- What changed: Updated evals/cautilus/quality-claim-fidelity/spec.json with referenceEngagement metadata for all 39 declared references; aligned the methodology spec wording with the keyed metadata shape; added classification critique evidence.
- Alternatives rejected: Kept declaredReferences as a string list rather than an object list; deferred tag-aware builder scoring; rejected promoting useful on-demand references to engage-always unless the representative run must consult them.
- Targeted verification: python3 -m json.tool parsed spec.json; build-skill-execution-observation.mjs parsed the tagged spec over the checked-in 2026-06-22 baseline bundle and reproduced coverage=0/39; node shape assertion confirmed declaredReferences string[] plus 39/39 metadata coverage; validate_cautilus_proof.py passed with no proof artifact changed; run_slice_closeout.py --skip-broad-pytest passed.
- Test duplication pressure: none — metadata/spec artifact slice only; no tests added or expanded.
- Critique: Fresh-eye classification critique completed with 2 angle reviewers + 1 counterweight reviewer; no Act Before Ship findings; critique artifact: charness-artifacts/critique/2026-06-23-quality-reference-engagement-classification.md.
- Off-goal findings: none.
- Lessons carried forward: Next slice can choose remediation from 9 engage-always, 27 on-demand, 3 gate-sufficient; quality-lenses.md is engage-always and remains the required command fragment; tag-aware scoring is valid but deferred.
- Metrics: Host token/tool metrics not available; reviewer agents completed and were closed.

## Context Sources

- Source: handoff entry #1 (START HERE — skill claim-fidelity + doc-philosophy across ALL skills (public + support)) — see [docs/handoff.md](../../docs/handoff.md).
- Cited issue: #397 — quality skill bypasses its own 39-ref corpus (cautilus reject, 0/39).
- Finding bundle: `charness-artifacts/cautilus/quality-claim-fidelity-2026-06-22/finding.md` (baseline `reject`).
- Harness: `evals/cautilus/quality-claim-fidelity/README.md` + `spec.json`.
- Settled framing: 2026-06-22 per-doc 3-way axis (operator); 2026-06-21 quality-reference disposition (delete 0).
- Cautilus contract: `skills/public/quality/references/cautilus-on-demand.md` (eval-only / ask-before-run).
- Recent traps: `charness-artifacts/retro/recent-lessons.md` (529-overload, read-schema-before-persist, surfaces-coverage).

## Interview Decisions

- **Scope** (family: spec-only / spec+pilot / spec+pilot+begin-fan-out): chose **spec+pilot+begin-fan-out**. Rejected spec-only (leaves methodology unproven) and spec+pilot (operator wants generalization evidence now). axis: single-point — this goal's scope decision.
- **Proof depth** (family: deterministic-before/after / full-double-cautilus / design-only-defer / one-run): operator chose **one cautilus run** ("코틸러스 런 하나만 해서 잘 하는지 보면 됨"). The 2026-06-22 reject/0-of-39 baseline is the "before"; the single run is the post-remediation "after". Rejected double-cautilus (cost) and design-only-defer (no behavioral proof). axis: single-point — operator cost-bounded one validation run.
- **Remediation direction** (family: front-load-gate-triage / wire-refs-into-findings / decide-after-classification): chose **decide-after-classification** — the engage-always/on-demand split is the discriminator. Rejected pre-committing a direction before the classification data exists.
- **Capture model** (family: provider/tier axis — sonnet / haiku / opus): not locked globally. axis: provider/tier — the 529-overload lesson shows sonnet thrashed and haiku captured clean; pick a non-thrashing tier at the capture slice rather than a global default.
- **Cautilus version**: 0.17.1 (re-verified). axis: tool version (integration manifest).

## Plan Critique Findings

Reviewer: bounded fresh-eye subagent (claude), 2026-06-23, read-only over the
goal + #397 + harness README/spec.json + baseline finding.

**Blockers folded (all one root: the baseline failed BOTH dimensions, so a coverage-fix that stays slow misreads as a failed validation):**

- (B) Duration confound → folded into Agent Verification Plan (signal separation) + User Acceptance (primary/secondary split): primary = deterministic coverage shift; cautilus `reject`-on-duration is secondary and not a coverage-fix failure.
- (C) #397 closeout predicate under-specified → folded into Coordination Cues during shaping, then strengthened in Slice 1 critique: closeout iff the captured run actually reads/opens `quality-lenses.md` and observed coverage rises `0/39 → ≥1/39 incl. quality-lenses.md`; duration not a close-blocker.
- (E) Acceptance bullet asserted a verdict local checks can't fully produce → folded into User Acceptance: split locally-verifiable coverage from operator-gated cautilus rollup.

**Over-worry raised, not folded (confirmed sound as written):**

- (A) Slice 1 (methodology spec) is the right first move; no hidden dependency; slice order sound. Slice 2's parser guard is now concrete: keep `declaredReferences` as a string list and add engagement metadata beside it unless the builder is deliberately changed.
- (B) The single after-run vs the existing baseline IS a valid before/after — both are deterministic coverage numbers computed host-side, not stochastic judge calls.
- (C) Fan-out scope is crisply bounded (1–2 skills, classification-only, full fan-out excluded in Non-Goals).
- (D) No over-anchoring: capture model left unlocked (529-overload lesson), cautilus 0.17.1 pinned via manifest, `max_duration_ms` is a deliberate harness threshold not a host-varying value.

Overall reviewer verdict: sound to activate after the one root fix (signal separation), now folded.

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro
