# Achieve Goal: Reference-compaction Slice-7 per-condition claim-fidelity floor redesign for setup then handoff (the pinned Next Session #1 front of the sweep).

Status: active
Created: 2026-07-02
Activation: `/goal @charness-artifacts/goals/2026-07-02-issue-410-411-412-413-reference-compaction-slice-7-per-condition-claim-fidelity-fl.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: ACTIVE — scope locked to setup + handoff only, open-ended
  (no timebox). Activated 2026-07-02.
- Current slice: Slices 1–4 DONE. setup (#413) fully redesigned+captured; handoff
  (#412) planner conditionalized (Slice 3) AND both pickup conditions now have
  falsifiable fixtures — clear (`pickup.spec.json`, re-graded from Slice-7) +
  ambiguous (`pickup-ambiguous.spec.json`, fresh capture, both docs opened). Slice 4
  fresh-eye critique pending.
- Next action: Slice 5 closeout — stage #412/#413 issue closeout via `issue`
  (external write, operator-confirm), check #410 setup+handoff rows, refresh
  `docs/handoff.md`, run `retro`, flip goal to complete.
- Verification cadence: cheap deterministic gates + unit tests at commit
  boundaries; fresh-eye subagent critique at each slice boundary; ask-before-run
  Cautilus capture as the live floor proof at the setup and handoff bundle
  boundaries.
- Slice review packet: intent, changed files (spec/eval + planner surfaces),
  expected invariants (floor stays honest, no matcher softening), tests/proof,
  non-claims (token OBSERVED not assumed), out-of-scope (gather, greenfield,
  broader #410), and reviewer questions.
- Discuss before activation: Resolved — the two Cautilus captures are
  ask-before-run live proof and #412/#413 closeout is an external write; operator
  approves each capture at its boundary (confirmed), and issue closeout runs in
  the After phase via the `issue` skill. No unresolved consequential activation
  item.
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Operator Decision Queue`,
  `## Final Verification`, and `## Auto-Retro`.

## Goal

Reference-compaction Slice-7 per-condition claim-fidelity floor redesign for setup then handoff (the pinned Next Session #1 front of the sweep).

**Source handoff entry #1: Continue the per-condition fixture work**

> (see the reconciliation doc's METHOD CORRECTION):
>    **setup** then **handoff** — trace each ref to its trigger, design a scenario per genuinely-DEPTH
>    condition, retire only truly-inlined docs; then gather's public-URL output-floor + hotl/ledger
>    token-lift. Mechanics: `capture-skill-run.sh` needs an ABSOLUTE `--out-dir` OUTSIDE the repo (its
>    `config/settings.json` pollutes `check_doc_links`); grade with
>    `build-skill-execution-observation.mjs --spec <spec> --stream <out>/stream.jsonl`; broad pytest
>    BEFORE the critique (grep misses path-built consumers).

---

**Source handoff entry #7: #413: setup claim-fidelity floor needs a redesign (RCF hypothesis refuted; default-surfaces.md not forced)**

> ## Context
>
> reference-compaction Slice 7 (#410) scoped setup normalization as an RCF→RSF move, keeping
> `default-surfaces.md` RCF-pinned as "a faithful multi-surface proxy." The first live
> normalization capture (commit forthcoming; bundle
> `charness-artifacts/cautilus/setup-normalization-claim-fidelity-slice7-2026-07-01/`) **refutes
> that floor.** Same class as #411 (gather).
>
> ## Observed problem
>
> A representative in-repo `/charness:setup` full normalization (mode NORMALIZE) scores
> **outcome=FAILED, coverage 0/9**: it opens **zero** reference docs, including all 3 RCF floors
> (`normalization-flow.md`, `agent-docs-policy.md`, `default-surfaces.md`). setup has no planner;
> its 14 Reads were all TARGET SURFACES (README.md, AGENTS.md, docs/operator-acceptance.md,
> operating-contract.md, recent-lessons.md), never a `setup/references/*.md`. The normalization
> discipline is driven by the SKILL.md workflow + the real surfaces, so `default-surfaces.md` (the
> proxy) is never forced — the multi-surface-proxy reasoning was a hypothesis the run refutes.
>
> ## Proposed fix
>
> Redesign setup's normalization claim-fidelity floor as an artifact/substance instrument:
>
> - add `evals/cautilus/setup-claim-fidelity/outcome-assertions.json` grading whether the run
>   actually touched + honestly normalized the real operating surfaces (README/AGENTS/roadmap/
>   operator-acceptance) and left an honest closeout, rather than whether it opened a reference doc;
> - reclassify the reference docs (normalization-flow.md / agent-docs-policy.md / default-surfaces.md)
>   as INLINE/DEPTH per their real role once the artifact floor exists.
>
> Do NOT pin a trivial token to force a green; the RCF is kept as a known-refuted hypothesis until
> the redesign. `greenfield.spec.json` stays untested (needs a fresh-sandbox capture, not in-repo
> capturable — already deferred by #410).
>
> This is the same claim-fidelity FLOOR-MODEL gap as #411 (gather): a SKILL/script-driven skill has
> no honest deterministic doc-routing floor and needs an artifact/substance instrument.
>
> ## References
>
> - Finding: `charness-artifacts/cautilus/setup-normalization-claim-fidelity-slice7-2026-07-01/finding.md`
> - Sibling (same class): #411 · Parent sweep: #410

---

**Source handoff entry #8: #412: handoff planner over-requires continuation-sequence.md for unambiguous pickups**

> ## Context
>
> reference-compaction Slice 7 captured all three handoff claim-fidelity scenarios live
> (commit forthcoming; bundle `charness-artifacts/cautilus/handoff-claim-fidelity-slice7-2026-07-01/`).
> The pickup scenario surfaced a planner over-requirement.
>
> ## Observed problem
>
> `plan_handoff_run.py` emits `references/continuation-sequence.md` as a pickup-intent
> `_required_read` **unconditionally** (verified: `plan_handoff_run.py --intent pickup --json`
> lists it). But the skill's own guidance scopes that doc to *"when several plausible pickups
> exist"* (SKILL.md continuation-sequence reference). The live pickup capture — an unambiguous
> pickup with one clear pinned task — correctly resumed the task WITHOUT opening
> continuation-sequence.md (coverage 1/7, opened only workflow-trigger.md), so the claim-fidelity
> floor `[workflow-trigger.md, continuation-sequence.md]` grades outcome=FAILED even though the
> run behaved faithfully.
>
> ## Why the spec was NOT changed
>
> The pickup spec RCF faithfully mirrors the planner's `_required_reads`, and the eval correctly
> flags the gap. Softening the spec (dropping continuation-sequence.md while the planner still
> emits it) would desync the spec from the planner. The honest fix is at the PLANNER.
>
> ## Proposed fix
>
> Make `plan_handoff_run.py` emit `continuation-sequence.md` as a pickup `_required_read`
> **conditionally** — only when the pickup is ambiguous (several plausible pickups / multiple
> live handoff entries or open issues without one clearly-pinned next task), aligning the planner
> with the skill's own "when several plausible pickups exist" scope. Then re-baseline the pickup
> claim-fidelity floor with a fresh capture (ambiguous-pickup fixture forces the doc; clear-pickup
> fixture does not).
>
> Until then, the pickup scenario's floor legitimately fails on a clear-pickup capture; that is
> recorded, not softened.
>
> ## References
>
> - Finding: `charness-artifacts/cautilus/handoff-claim-fidelity-slice7-2026-07-01/finding.md`
> - Parent sweep: #410

---

**Source handoff entry #10: #410: reference-compaction Slice 7: per-skill RCF→RSF floor sweep (each needs a fresh ask-before-run capture)**

> ## Context
>
> reference-compaction Slices 1–6 are DONE. Slice 1 landed the keystone (RCF-or-RSF
> floor guard, headroom-exempt `## Closeout Vocabulary` H2, advisory `classTag`
> DUP/INLINE/DEPTH + DEPTH-only coverage denominator). **Slice 5 proved the pattern
> on `impl`**: lifting the closeout vocabulary into always-loaded core and moving the
> eval floor from the re-read proxy (`requiredCommandFragments=[<doc>.md]`) to an
> emitted-token floor (`requiredSummaryFragments`) — verified by a live ask-before-run
> Cautilus capture (FLOOR PASS + substance 5/5; bundle at
> `charness-artifacts/cautilus/impl-claim-fidelity-slice5-2026-07-01/`).
>
> ## Observed problem this tracks
>
> Several other evaluator-required public skills still pin their closeout/artifact
> vocabulary behind a `requiredCommandFragments` *doc-open* proxy, which forces a
> representative run to re-read a doc whose intent it already has — the exact
> wasteful re-read Move C relieves. Each is a validator-enforced floor, so it cannot
> be batch-flipped: **each needs its own fresh ask-before-run Cautilus capture to
> re-baseline an HONEST RSF token — the token must be OBSERVED, not assumed.**
>
> > Slice 5 evidence for why capture-before-pin is load-bearing: the plan *assumed*
> > `unverified-future`; the live run never emitted it (it categorized `test-only`),
> > so only the capture-forced `ran-pass` was pinned. Assuming would have shipped a
> > false floor.
>
> ## Scope — per-skill RCF→RSF sweep (each its own gate-clean slice)
>
> Land each AFTER a fresh capture, as a separate reviewable slice with a fresh-eye
> critique:
>
> - [ ] **critique** — lift Structured Findings / Reviewer Tier enums to `## Closeout Vocabulary`; drop `counterweight-triage.md` from RCF in BOTH `spec.json` and `decision.spec.json`; watch the ~195 ceiling (trim the repeated no-same-agent rule).
> - [ ] **hitl** — lift the disposition verb enum + `verified_against.*`/`disposition.*` field tokens; drop `chunk-contract.md` from RCF → RSF (impl's closest twin).
> - [ ] **gather** — lift the Access Modes enum; drop `capability-contract.md` from RCF → RSF (KEEP `source-priority.md` as a floor).
> - [ ] **hotl** — lift ledger `verified_against`/`disposition` field tokens; RCF-drop `proof-rules.md` + `ledger-and-dispositions.md` (must keep RCF non-empty → needs the relaxed guard AND a captured RSF).
> - [ ] **handoff** — RCF-drop continuation-sequence/workflow-trigger (pickup) + state-selection/spill-targets (refresh) → RSF; delete `document-seams.md` (all 3 specs).
> - [ ] **setup** — `normalization.spec.json` RCF→RSF (in-repo capturable); greenfield DEFERRED to a fresh-sandbox capture (NOT in-repo capturable) — keep `greenfield-flow.md` in RCF until then.
> - [ ] **create-cli** — drop `command-conventions.md` from RCF → RSF (RCF stays 3-entry non-empty, independently shippable); do NOT inline the cross-skill `verification-ladder.md` Lint Gate enum. Also fix the prose nit surfaced by the Slice-5 critique: `references/quality-gates.md:47-50` says the Lint Gate enum is "defined in" `verification-ladder.md` "Lint Gate Closeout Shape" — after Slice 5 that section forwards to `impl/SKILL.md ## Closeout Vocabulary`, so reword to "forwards to".
> - [ ] **achieve** — `goal-artifact.md`/`lifecycle.md` RCF→RSF ONLY if a capture confirms the shaping prompt forces a goal-artifact token; else KEEP in RCF and record the finding.
>
> ## Guardrails (do NOT over-relax)
>
> - **`greenfield-flow.md` (setup) and `default-surfaces.md` (setup) STAY RCF-pinned** — one is not in-repo capturable, one is a faithful multi-surface proxy. Applying Move C blindly there would over-relax a healthy floor.
> - **`issue` and `markdown-preview` need NO change** (no stranded token, no actionable surface).
> - Every capture is ask-before-run: consult `python3 scripts/plan_cautilus_proof.py --repo-root . --json`, refuse on `next_action: none`, run through `python3 scripts/run_cautilus_eval.py` / the capture harness with an operator-log justification.
> - A floor MISS is a skill-shape signal (re-pin / re-classify / planner), NEVER a reason to soften the matcher.
>
> ## References
>
> - Contract: `charness-artifacts/reference-compaction/contract.md` (Slice 7)
> - Per-skill detail: `charness-artifacts/reference-compaction/plan.json` (`execution.slices[6]`, `per_skill_plans`)
> - Proven pattern: commit `3c5c8657` (Slice 5) + `charness-artifacts/cautilus/impl-claim-fidelity-slice5-2026-07-01/finding.md`

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not absorb adjacent handoff entries beyond the selected chunk.

## Boundaries

- In scope: `charness-artifacts/cautilus/handoff-claim-fidelity-slice7-2026-07-01/`, `charness-artifacts/cautilus/handoff-claim-fidelity-slice7-2026-07-01/finding.md`, `charness-artifacts/cautilus/impl-claim-fidelity-slice5-2026-07-01/`, `charness-artifacts/cautilus/impl-claim-fidelity-slice5-2026-07-01/finding.md`, `charness-artifacts/cautilus/setup-normalization-claim-fidelity-slice7-2026-07-01/`, `charness-artifacts/cautilus/setup-normalization-claim-fidelity-slice7-2026-07-01/finding.md`, `charness-artifacts/reference-compaction/contract.md`, `charness-artifacts/reference-compaction/plan.json`, `config/settings.json`, `docs/operator-acceptance.md`, `evals/cautilus/setup-claim-fidelity/outcome-assertions.json`, `references/continuation-sequence.md`, `references/quality-gates.md`, `scripts/plan_cautilus_proof.py`, `scripts/run_cautilus_eval.py`, `setup/references/`
- Portable per implementation-discipline: no host-specific assumption.
- Stop conditions: name on first discovery; do not guess.

## User Acceptance

You can verify completion directly by:

- `evals/cautilus/setup-claim-fidelity/outcome-assertions.json` exists and grades
  whether a `/charness:setup` normalization run actually touched + honestly
  normalized the REAL operating surfaces (README/AGENTS/roadmap/operator-acceptance)
  and left an honest closeout — not whether it opened a reference doc — and its
  fresh ask-before-run capture bundle shows a FLOOR PASS + substance-judge pass.
- The three refuted setup RCF docs (`normalization-flow.md`, `agent-docs-policy.md`,
  `default-surfaces.md`) are reclassified (INLINE/DEPTH) per their real role, while
  `greenfield-flow.md` stays RCF-pinned (greenfield deferred, not in-repo capturable).
- `python3 plugins/charness/skills/handoff/scripts/plan_handoff_run.py --intent pickup --json`
  on a clearly-pinned pickup no longer lists `continuation-sequence.md` as a
  required read, while an ambiguous pickup still does; the handoff pickup
  claim-fidelity floor re-baselines green on a clear-pickup capture with RCF
  `[workflow-trigger.md]` (continuation-sequence.md dropped, workflow-trigger.md kept).
- #413 and #412 are resolvable from what landed, and #410's setup + handoff
  checklist rows are checked — each skill landed as its OWN gate-clean,
  fresh-eye-reviewed commit (never batch-flipped).
- Broad pytest is green and no matcher was softened to force a floor pass.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/run_slice_closeout.py --skip-broad-pytest` (or the repo's
  commit-boundary gate set) on each slice commit.
- Unit tests for the planner change (`tests/test_handoff_plan.py` and the handoff
  planner suite) proving conditional `continuation-sequence.md` emission.
- Schema/contract validation of the new `outcome-assertions.json` via
  `scripts/grade_skill_outcome.py` and of the spec edits via
  `claim_fidelity_lib.validate_spec` + the claim-fidelity registry (runs at the
  Slice-2 and Slice-4 commit boundaries when RCF/classTag change, not only pytest).
- `check_doc_links` / doc-authoring preflight on any edited docs.
- Broad `pytest` BEFORE each slice critique (grep misses path-built consumers).

### High-Confidence Checks

- Fresh-eye subagent critique at each slice boundary (setup design, setup land,
  handoff planner, handoff re-baseline) handed the bounded slice review packet.
- `scripts/agent-runtime/build-skill-execution-observation.mjs --spec <spec>
  --stream <out>/stream.jsonl` grading of each capture stream against the floor.

### External Or Live Proof

- Ask-before-run Cautilus captures — one representative `/charness:setup`
  normalization run; one clear-pickup and one ambiguous-pickup `/charness:handoff`
  run — each gated through `python3 scripts/plan_cautilus_proof.py --repo-root .
  --json` (REFUSE on `next_action: none`) → `python3 scripts/run_cautilus_eval.py`
  with an operator-log justification. `capture-skill-run.sh` uses an ABSOLUTE
  `--out-dir` OUTSIDE the repo (its `config/settings.json` pollutes
  `check_doc_links`). The emitted floor token is OBSERVED from the capture, never
  assumed. Operator approves each capture at its boundary.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Design setup's substance floor: add `evals/cautilus/setup-claim-fidelity/outcome-assertions.json` grading the EDITED operating-surface set + honest-closeout summary tokens (`summary_contains`/`transcript_contains`/judge-kind — normalization edits, it does not create a file), mirroring impl's Slice-5 judge; scope its `_comment` to the normalization product (the sibling set also resolves for greenfield — keep greenfield grading deferred); plan the INLINE/DEPTH reclassification of the 3 refuted RCF docs | setup's RCF is a known-refuted hypothesis (in-repo capture 0/9, `Edit=2`); the substance judge must exist before the capture-gated MOVE | `outcome-assertions.json` validates against `grade_skill_outcome.py`; harness confirmed to preserve edited files into `outputs/` before any `output_*` check; reclassification plan matches the census-reconciled verdicts | planned |
| 2 | Capture + land setup MOVE: ask-before-run Cautilus capture of a representative normalization run; observe the emitted token; flip classTag/RCF (the flip rides the capture per `claim_fidelity_lib`); fresh-eye critique; commit | `claim_fidelity_lib` forbids INLINE-tagging a live RCF floor, so the flip must ride a fresh capture; token must be OBSERVED not assumed | capture bundle FLOOR PASS + substance-judge pass; #413 resolvable; standalone reviewed commit | planned |
| 3 | Conditionalize the handoff planner: make `plan_handoff_run.py` emit `continuation-sequence.md` for pickup only when the pickup is ambiguous; add/adjust unit tests | #412 — the planner over-requires it unconditionally; deterministic code change lands before its re-baseline capture | `--intent pickup` clear-case omits the doc, ambiguous case keeps it; unit tests + broad pytest green | planned |
| 4 | Re-baseline handoff pickup floor: ask-before-run clear + ambiguous captures; drop `continuation-sequence.md` from pickup RCF (keep `workflow-trigger.md`, proven load-bearing); re-run `claim_fidelity_lib.validate_spec` + registry, not just pytest; fresh-eye critique; commit | the floor must re-baseline on a fresh capture once the planner is conditional | clear-pickup capture passes floor `[workflow-trigger.md]`; ambiguous forces `continuation-sequence.md` via a GENUINE Read (not a subagent-prompt name-mention — #415 hollow-pass guard); spec validator green (RCF non-empty, no RSF needed); #412 resolvable; standalone reviewed commit | planned |
| 5 | Closeout: check #410 setup + handoff rows, stage #412/#413 issue closeout via the `issue` skill, refresh `docs/handoff.md`, run `retro` | After-phase proof + baton pass | #410 rows checked; #412/#413 resolvable; handoff refreshed; retro dispositions recorded | planned |

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

Active queue items:

- Decision: approve each ask-before-run Cautilus capture (setup normalization;
  handoff clear + ambiguous pickup) | Owner: operator | Why deferred: does not
  block Slice 1/3 non-capture design + code work | Unblock action: approve at the
  capture boundary after `plan_cautilus_proof.py` reports a runnable next_action
  | Revisit trigger: reaching each capture boundary.
- Decision: close/stage #412, #413 and check #410 setup+handoff rows | Owner:
  operator | Why deferred: closeout is an After-phase external write, not a
  blocker for the impl slices | Unblock action: confirm closeout after the fixes
  land and captures pass | Revisit trigger: After phase.

## Coordination Cues

Phase routing defers to `find-skills` (no inline phase→skill map). Expected
closeout floors for this goal:

- Routing: `find-skills` was invoked at session start and drove the pickup →
  handoff chunker → this goal.
- Issue closeout: #412 and #413 close via the `issue` skill after the fixes land
  and captures pass; #410 setup+handoff rows are checked.
- Gather: n/a — no external source ingestion in scope.
- Release: n/a — no plugin version bump expected (Non-Goals).

## Slice Log

### Slice 1: Design setup substance floor (outcome-assertions.json)

- Objective: Add the advisory substance instrument for setup normalization (#413 step 1): grade real-surface touch (README/AGENTS/roadmap/operator-acceptance) + honest per-surface closeout + no-greenfield-overreach, NOT doc-opens. RCF/RSF floor flip deferred to the Slice-2 capture (token OBSERVED, not assumed).
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: validate_assertion_set: 0 errors; validate_outcome_assertions.py: OK (6 sets); ran-setup deterministic floor matches observed summary 'Execution of /setup'; broad pytest 3976 passed; fresh-eye Slice-1 critique SOUND (no blockers). Deferred refinement (carry to the #410-deferred greenfield capture, out of this goal's scope): add a machine-enforced scenarioId/wiring guard so the sibling set is not applied to a future greenfield bundle.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: setup floor flip — capture-gated RCF->RSF (Slice 2)

- Objective: Add setup ## Closeout Vocabulary (74c639cf), run operator-authorized ask-before-run capture, OBSERVE emitted tokens, flip normalization.spec.json RCF=[] -> RSF=[Repo mode:, Normalization non-claims:], reclassify 3 refuted docs classTag INLINE. Resolves #413.
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Old RCF floor grades outcome=FAILED (1/9); flipped RSF floor grades outcome=PASSED (both tokens OBSERVED in closeout). validate_spec + registry (26 specs) OK. grade_skill_outcome selftest PASSED, ran-setup deterministic PASS. Fresh-eye Slice-2b critique: HONEST + LOAD-BEARING, no #410 softening, no blockers. Evidence: charness-artifacts/cautilus/setup-normalization-claim-fidelity-slice2b-2026-07-02/.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 3: handoff planner conditional continuation-sequence.md (Slice 3)

- Objective: Make plan_handoff_run.py emit continuation-sequence.md for pickup ONLY when ambiguous (no clearly-pinned task AND >=2 plausible pickups). Adds _invocation_pins_single_task (issue-id/word-boundary 'pinned' with negation guard/file-path) + _pickup_needs_continuation_sequence + next_session_entry_count. Aligns planner with the skill's 'when several plausible pickups exist' scope. Progresses #412 (RCF drop rides Slice 4 capture).
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: 15 handoff-plan unit tests pass (clear/ambiguous/single/pinned/issue/unpinned); heuristic edge-cases verified; source+mirror synced identical; broad pytest 3980 passed; fresh-eye Slice-3 critique SOUND, no blockers (folded \bpinned\b negation guard + unpinned test).
- Test duplication pressure: added 5 planner tests (pickup ambiguity); no duplicate-coverage pressure — new discriminating cases, not overlap.
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 4: handoff pickup floor re-baseline — per-condition falsifiable fixtures (Slice 4, resolves #412)

- Objective: Split the pickup floor into two falsifiable per-condition fixtures matching the conditionalized planner: CLEAR (pickup.spec.json, RCF=[workflow-trigger.md], re-graded from the existing Slice-7 capture) + NEW AMBIGUOUS (pickup-ambiguous.spec.json, RCF=[workflow-trigger.md, continuation-sequence.md], fresh operator-authorized capture). continuation-sequence.md reclassified on-demand DEPTH (planner change refutes the census INLINE — it IS load-bearing when several plausible pickups exist). Registered pickup-ambiguous in claim-fidelity-registry.json.
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Clear arm: Slice-7 capture's only RCF failure was continuation-sequence.md -> passes RCF=[workflow-trigger.md]. Ambiguous arm: fresh capture at c1a66f4d resolved intent=pickup and OPENED both docs -> outcome=passed (coverage 2/6); falsifiable (skipping continuation-sequence.md fails). validate_spec both specs OK; registry validation 47 passed. Evidence: charness-artifacts/cautilus/handoff-pickup-ambiguous-slice4-2026-07-02/.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Context Sources

- Source: handoff entry #1 (Continue the per-condition fixture work) — see [docs/handoff.md](../../docs/handoff.md).
- Source: handoff entry #7 (#413: setup claim-fidelity floor needs a redesign (RCF hypothesis refuted; default-surfaces.md not forced)) — see [docs/handoff.md](../../docs/handoff.md).
- Source: handoff entry #8 (#412: handoff planner over-requires continuation-sequence.md for unambiguous pickups) — see [docs/handoff.md](../../docs/handoff.md).
- Source: handoff entry #10 (#410: reference-compaction Slice 7: per-skill RCF→RSF floor sweep (each needs a fresh ask-before-run capture)) — see [docs/handoff.md](../../docs/handoff.md).
- Cited path: `charness-artifacts/cautilus/handoff-claim-fidelity-slice7-2026-07-01/`
- Cited path: `charness-artifacts/cautilus/handoff-claim-fidelity-slice7-2026-07-01/finding.md`
- Cited path: `charness-artifacts/cautilus/impl-claim-fidelity-slice5-2026-07-01/`
- Cited path: `charness-artifacts/cautilus/impl-claim-fidelity-slice5-2026-07-01/finding.md`
- Cited path: `charness-artifacts/cautilus/setup-normalization-claim-fidelity-slice7-2026-07-01/`
- Cited path: `charness-artifacts/cautilus/setup-normalization-claim-fidelity-slice7-2026-07-01/finding.md`
- Cited path: `charness-artifacts/reference-compaction/contract.md`
- Cited path: `charness-artifacts/reference-compaction/plan.json`
- Cited path: `config/settings.json`
- Cited path: `docs/operator-acceptance.md`
- Cited path: `evals/cautilus/setup-claim-fidelity/outcome-assertions.json`
- Cited path: `references/continuation-sequence.md`
- Cited path: `references/quality-gates.md`
- Cited path: `scripts/plan_cautilus_proof.py`
- Cited path: `scripts/run_cautilus_eval.py`
- Cited path: `setup/references/`
- Cited issue: #410
- Cited issue: #411
- Cited issue: #412
- Cited issue: #413

## Interview Decisions

- Scope. Family: {setup+handoff only, +gather public-URL tail, broader #410
  sweep}. Chosen: **setup + handoff only** (the selected chunk ①). Rejected:
  +gather (the chunker split it into chunk ②; #410 mandates "each its own
  gate-clean slice", so keep the goal to two skills); broader #410 (several more
  ask-before-run captures — better as separate goals per skill).
- Run budget. Family: {open-ended no-timebox, fixed timebox}. Chosen:
  **open-ended, no timebox**. Rejected: fixed timebox — the work is capture-gated
  ask-before-run, so wall-clock autonomy is already bounded by operator approval;
  a timebox would add early-close bookkeeping without buying pace.
- Capture approval cadence (implicit, per CLAUDE.md eval-only ask-before-run
  contract). Chosen: **operator approves each Cautilus capture at its boundary**
  via `plan_cautilus_proof.py` → `run_cautilus_eval.py`; not a pre-authorized
  batch. Rejected: pre-authorizing all captures up front (violates the
  eval-only/ask-before-run surface).

## Plan Critique Findings

Reviewer: fresh-eye subagent (general-purpose, different context), read-only plan
review against the specs, `plan_handoff_run.py`, `claim_fidelity_lib.py`,
`grade_skill_outcome.py`, `skill_outcome_wiring.py`, and the two committed
captures. Verdict: **no blockers; activation-ready.**

Blockers folded: none (none found).

Refinements folded:

- **Setup deterministic assertions grade EDITS, not a new file.** A normalization
  run edits README/AGENTS (finding shows `Edit=2`), it does not create an
  artifact like impl's `test_*.py`. Slice 1 targets the EDITED operating-surface
  set + honest-closeout summary tokens via `summary_contains` /
  `transcript_contains` / judge-kind assertions, and CONFIRMS the capture harness
  preserves edited (not only created) files into the bundle `outputs/` before
  pinning any `output_*` check.
- **One `outcome-assertions.json` covers both setup specs** (sibling resolution:
  `spec_path.parent / outcome-assertions.json` applies to normalization AND
  greenfield). Slice 1 scopes the assertions to the normalization product and its
  `_comment` states greenfield grading stays deferred with the greenfield RCF, so
  a future greenfield capture is not silently mis-graded.
- **#415 residual on the KEPT `workflow-trigger.md` floor is clean here, and the
  ambiguous fixture needs a genuine-Read check.** The pickup capture spawned NO
  subagent and opened `workflow-trigger.md` genuinely, so the name-mention path is
  not implicated. Slice 4 records this non-claim AND, for the new ambiguous-pickup
  fixture, confirms `continuation-sequence.md` is forced by a real Read rather
  than a subagent-prompt name-mention (else the ambiguous floor is a #415 hollow
  pass).
- **Slice 4 re-runs the spec/registry validator, not only pytest.** The pickup RCF
  drops 2→1; `claim_fidelity_lib.validate_spec` re-checks engage-always +
  non-DUP/INLINE + RCF-or-RSF-non-empty. RCF stays non-empty `[workflow-trigger.md]`
  so no RSF is required (cleaner than impl's RCF→RSF flip). Added to Low-Cost Checks.

Over-worry raised but NOT folded (with why):

- "The flip rides the capture" — VERIFIED true (`claim_fidelity_lib.py:187-192`
  forbids DUP/INLINE on an RCF ref; `:177-181` requires RCF-or-RSF non-empty), not
  a worry.
- "Also drop `workflow-trigger.md` per #410's census `MOVE` row" — declined; the
  live capture PROVED it load-bearing and the METHOD CORRECTION supersedes the
  coarse census row.
- "Handle greenfield now" / "fold in gather or broader #410" — declined; out of
  the locked scope, greenfield not in-repo capturable, gather is chunk ②.
- Irreversible-write timing — no activation risk; issue closeout + #410 row-checks
  are After-phase via the `issue` skill and every capture is ask-before-run.

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro
