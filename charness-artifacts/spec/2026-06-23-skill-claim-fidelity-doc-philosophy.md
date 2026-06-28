# Spec - Skill Claim-Fidelity And Doc-Philosophy Methodology

Status: locked for implementation after Slice 1 critique folded
Created: 2026-06-23
Goal:
[2026-06-23-skill-claim-fidelity-doc-philosophy.md](../goals/2026-06-23-skill-claim-fidelity-doc-philosophy.md)
Primary pilot: quality skill, issue #397

This is the methodology contract for evaluating whether a Charness skill's
runtime behavior is faithful to its documentation claims without reopening the
settled reference-value question. It is a build contract for the active goal:
classify the quality skill's docs, remediate the execution shape, then begin a
small fan-out to prove the method generalizes.

## Problem

The 2026-06-22 quality claim-fidelity run proved a real execution-shape gap:
`/charness:quality` completed a capable gate-driven review but opened 0 of its
39 declared references. The run therefore failed the skill-task-fidelity claim
and also exceeded the runtime budget.

That result can be misread in two opposite ways:

1. Treat every unread reference as dead weight and reopen the rejected reference
   pruning heuristic.
2. Treat a capable final answer as enough and ignore that the runtime did not
   reach the point where the skill says reference-backed judgment should happen.

Both readings are wrong for this goal. Reference value is already settled by the
2026-06-21 disposition: un-routed is not worthless, and the defect is
discoverability or execution shape rather than bloat. This spec defines the
middle contract: each doc gets an engagement classification, and the claim made
about a run must match that classification.

## Current Slice

Write the methodology and schema contract before editing the quality harness or
skill behavior. The first implementation slice after this spec classifies the
quality skill's 39 declared references and records that classification in
[spec.json](../../evals/cautilus/quality-claim-fidelity/spec.json).

This is a braided contract: the axis is fixed now, while the quality remediation
choice remains a probe answered by the classification.

## Fixed Decisions

1. The per-doc axis has exactly three values for this goal:
   `engage-always`, `on-demand`, and `gate-sufficient`.
2. The axis is per document, not per skill and not per reference directory.
   A single skill can contain all three classes.
3. `engage-always` means a real representative run must consult the document.
   Zero reads are an execution-shape defect.
4. `on-demand` means the document is valuable when the run reaches that
   question. A generic run need not read it, but any claim about not reading it
   must say that it was on-demand rather than dead.
5. `gate-sufficient` means a deterministic gate already yields the conclusion
   the document would otherwise supply for this eval claim. It means
   claim-satisfied-by-gate here, not deletion-candidate.
6. A claim-fidelity run has two separated signals:
   deterministic coverage of required engagement, and Cautilus recommendation
   or runtime-budget scoring. A duration-only reject is not a failed coverage
   fix.
7. For #397, issue closeout is allowed only if the observed packet proves an
   actual runtime consultation/opening of `quality-lenses.md` in the real
   quality run. The coverage summary must rise from 0/39 to at least 1/39 and
   include `quality-lenses.md`, but a matcher-only/spec-only change that does
   not reflect a runtime read is not closeout evidence. Runtime budget is
   reported separately.

## Taxonomy Axis Checkpoint

This spec intentionally adds internal evaluation vocabulary, not a user-facing
CLI or skill mode. The three values live on one conceptual axis: the kind of
runtime engagement a document must receive for a claim-fidelity run to be
honest.

- `engage-always`: required evidence source for the representative run.
- `on-demand`: conditional evidence source for a narrower question.
- `gate-sufficient`: superseded by a deterministic conclusion for this claim.

The values are not remediation strategies. Strategies such as "front-load gate
triage" or "wire references into gate findings" remain downstream choices after
classification.

## Engagement Tag Contract

`evals/cautilus/*/spec.json` may add per-reference metadata, but the current
observation builder treats `declaredReferences` as a string list when computing
coverage
([build-skill-execution-observation.mjs](../../scripts/agent-runtime/build-skill-execution-observation.mjs)).
The quality pilot must therefore keep `declaredReferences` unchanged and add
engagement metadata beside it unless the implementation slice deliberately
updates the builder and tests the new shape.

Preferred compatible shape for the quality pilot:

```json
{
  "declaredReferences": ["quality-lenses.md"],
  "referenceEngagement": {
    "quality-lenses.md": {
      "engagement": "engage-always",
      "rationale": "SKILL.md routes lens selection and interpretation here.",
      "claimRole": "required_command_fragment"
    }
  }
}
```

Required fields for each tagged reference:

- reference key: basename or relative reference path already present in
  `declaredReferences`.
- `engagement`: one of `engage-always`, `on-demand`, `gate-sufficient`.
- `rationale`: one sentence explaining the classification in terms of the
  representative run.

Optional fields:

- `claimRole`: `required_command_fragment`, `coverage_only`,
  `gate_replacement`, or another local note used only by the harness.
- `gate`: deterministic gate or script that makes a `gate-sufficient` document
  unnecessary for the claim under test.
- `trigger`: the narrower user question that should lead to an `on-demand`
  document.

Backward compatibility requirement: before committing the quality tags, run the
observation builder against the tagged spec and prove it still parses. A direct
object list inside `declaredReferences` is not compatible with the current
builder and must not be used unless the implementation slice updates the
builder intentionally.

## Classification Rules

Classify one document at a time. The question is not "is this reference useful?"
The question is "what kind of runtime engagement would make the skill's current
claim honest?"

Use `engage-always` when any of these are true:

- The skill's core workflow says to consult this document for the ordinary
  representative run.
- The document contains the governing lens, interpretation rubric, or decision
  frame for the claim being tested.
- A run that skips the document can still produce plausible output, but the
  mechanism claim says the document should shape the judgment.

Use `on-demand` when any of these are true:

- The document answers a narrower condition that may not appear in the
  representative run.
- The document is a route target for a specific gate family, integration, host
  policy, or operator question.
- The correct claim is "not needed for this run", not "unused and therefore
  worthless".

Use `gate-sufficient` only when all of these are true:

- A deterministic gate already emits the same conclusion with a clear source of
  truth.
- The representative run can make the correct decision without reading the
  document.
- The spec can name the gate, and a future reader can verify that the gate
  actually covers the claim.

When uncertain, default to `on-demand` and record the trigger. Do not use
`gate-sufficient` as a parking lot for documents that are merely hard to route.

## Quality Pilot Contract

The quality pilot applies the methodology to all 39 declared references in
[spec.json](../../evals/cautilus/quality-claim-fidelity/spec.json).

The expected discriminator is `quality-lenses.md`: the quality skill's ordinary
posture review should reach the lens/judgment phase, so this document is
expected to be `engage-always`. The 2026-06-22 baseline opened none of the 39
references, including this one, which is the execution-shape defect #397 tracks.
Minimum #397 repair evidence is the runtime consultation of `quality-lenses.md`
in the representative quality run; full 39-reference classification is the
methodology pilot evidence that explains and generalizes the repair.

The quality remediation is intentionally not fixed by this spec. After
classification:

- If most `engage-always` misses happen because the front-loaded gate suite
  consumes the whole run, prefer gate triage or a delayed broad-gate posture.
- If gate findings need reference-backed interpretation at the point of
  classification, prefer wiring reference routes into the gate-driven findings.
- If both are true, combine them only as far as needed to move the primary
  coverage signal.

## Probe Questions

1. Does the parallel `referenceEngagement` object need builder-side validation,
   or is schema/comment-level documentation enough for the first pilot?
   Write-back: this spec's `Engagement Tag Contract` and the quality
   [spec.json](../../evals/cautilus/quality-claim-fidelity/spec.json) change.
2. How many of quality's 39 references are truly `engage-always` for a normal
   `/charness:quality` run?
   Write-back: quality [spec.json](../../evals/cautilus/quality-claim-fidelity/spec.json)
   `referenceEngagement` plus the active goal Slice Log.
3. Does quality remediation need to shorten the gate runway, route references
   from gate findings, or both?
   Write-back: a remediation decision entry in the active goal Slice Log before
   behavior edits, and this spec if the decision changes acceptance.
4. Which one or two additional skills provide the best fan-out sample after the
   quality pilot: one public skill with many references and one support skill,
   or two public skills with different execution shapes?
   Write-back: fan-out classification notes under the active goal Slice Log and
   any later reusable-schema follow-up.

## Deferred Decisions

- Whether the engagement tag vocabulary should become a reusable schema for all
  Cautilus skill claim-fidelity specs. Reopen trigger: after the quality pilot
  and 1-2 fan-out samples use the vocabulary without special pleading.
- Whether `build-skill-execution-observation.mjs` should score engagement tags
  directly instead of only matching command fragments. Reopen trigger: when the
  pilot needs tag-aware scoring that cannot be expressed by command fragments
  and coverage fields.
- Whether any `gate-sufficient` quality references should enter a separate
  retirement review. Reopen trigger: after classification identifies a
  gate-sufficient candidate and a distinct value/routing review is scheduled.
- Whether the full all-skills fan-out should be one goal or a batch of smaller
  skill-family goals. Reopen trigger: after the 1-2 skill fan-out sample records
  whether the method fits both sampled execution shapes. Resolved 2026-06-28 for
  the public tier: a single-pass public fan-out (operator-directed, skipping the
  1-2 skill sample) — see `## Full Public Fan-Out (2026-06-28)`. Support-tier
  batching stays open.

## Non-Goals

- Do not re-litigate the settled 2026-06-22 three-way axis framing.
- Do not re-run the rejected reference reachability/pruning heuristic.
- Do not claim Cautilus `accept` is required for #397 if the only remaining
  failing dimension is runtime budget.
- Do not make `engagement` a user-facing skill mode or CLI option.
- Do not run `cautilus evaluate` outside the repo wrapper and planner contract.

## Deliberately Not Doing

- Not deleting or merging references during the quality pilot. A
  `gate-sufficient` classification is evidence for a later deletion discussion,
  not permission to delete in this goal.
- Not requiring every declared reference to be opened in every run. That would
  erase the `on-demand` class and recreate the reachability heuristic under a
  new name.
- Not using the final natural-language answer as the only proof. A plausible
  quality report can still fail the mechanism claim if it never reaches the
  reference-backed judgment phase.

## Constraints

- Cautilus remains eval-only and ask-before-run. Before the one authorized
  post-remediation rollup, run:

  ```bash
  python3 scripts/plan_cautilus_proof.py --repo-root . --json
  ```

  Then use `python3 scripts/run_cautilus_eval.py`.
- The primary #397 proof is deterministic coverage from the observed packet:
  `0/39 -> >=1/39 including quality-lenses.md`, backed by a runtime tool-call
  read/open event from the captured session tree.
- Prompt-affecting quality skill changes require sync-before-verify, skill
  validation, and fresh-eye critique.
- The capture harness tests the installed Claude slash-command path. Host and
  provider boundaries must be recorded as non-claims, not hidden.
- New artifacts under `charness-artifacts/` must be committed with the goal
  state that explains them.

## Success Criteria

1. A maintainer can classify any skill reference using the three-way axis
   without deciding remediation first.
2. The quality pilot can record per-reference engagement tags beside
   `declaredReferences` without breaking the observation builder.
3. The remediation decision for #397 is driven by the classification, not by a
   preselected strategy.
4. The validation report separates deterministic coverage from Cautilus
   recommendation and runtime-budget scoring.
5. The fan-out sample can reuse this contract and record where it fits poorly
   without reopening the axis.

## Acceptance Checks

- SC1 classification usability: the quality classification table applies one of
  `engage-always`, `on-demand`, or `gate-sufficient` to all 39 declared
  references, and every row includes a rationale tied to the representative run.
- SC2 parser compatibility: this command parses the quality spec shape in the
  implementation slice; the baseline bundle is the known-runnable smoke input:

  ```bash
  node scripts/agent-runtime/build-skill-execution-observation.mjs \
    --session-tree charness-artifacts/cautilus/quality-claim-fidelity-2026-06-22 \
    --spec evals/cautilus/quality-claim-fidelity/spec.json \
    --output /tmp/quality-claim-fidelity-observed-smoke.json
  ```

- A targeted diff or unit assertion confirms `declaredReferences` remains a
  string list unless the builder is deliberately changed.
- SC3 remediation decision: before quality skill behavior edits, the active goal
  Slice Log records the classification distribution and the chosen remediation
  (`gate-triage`, `reference-routing`, or `both`) with rationale.
- SC4 signal separation: the validation report records deterministic coverage
  separately from Cautilus recommendation and runtime-budget findings.
- SC5 fan-out reuse: each fan-out classification note names the sampled skill,
  applies the three-way axis, and includes a `fits poorly:` field with either
  `no` or the concrete mismatch.
- `python3 scripts/check_doc_links.py --repo-root .`
- [check-markdown.sh](../../scripts/check-markdown.sh)
- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
- Fresh-eye critique packet for Slice 1 reviews this contract for overstated
  success, taxonomy confusion, and a hidden deletion path.

## Acceptance Check Coverage

- SC1 -> all-39 classification table with per-row rationale.
- SC2 -> builder smoke command plus `declaredReferences` string-list assertion.
- SC3 -> remediation decision entry before behavior edits.
- SC4 -> validation report field/section separating coverage, recommendation,
  and runtime budget.
- SC5 -> fan-out notes with `fits poorly:` disposition.

## Tripwires

- If classification cannot place a document without arguing whether the
  document has value, stop and restate the runtime-engagement question.
- If a proposed remediation can pass by adding `quality-lenses.md` to the
  matcher but still never uses it in the representative run, reject that as
  matcher theater.
- If a Cautilus rollup still rejects solely on duration after deterministic
  coverage moves, report a runtime-budget residual rather than calling the
  coverage fix failed.
- If the builder shape forces destructive `spec.json` churn, keep
  `declaredReferences` as the stable string list and add metadata beside it.

## Critique

Slice 1 fresh-eye critique ran with parent-delegated subagents on 2026-06-23.
Packet consumed: [2026-06-22-222623-packet.md](../critique/2026-06-22-222623-packet.md).
Reviewer tier requested: high-leverage via
[critique-adapter.yaml](../../.agents/critique-adapter.yaml); host spawn
surface accepted parent-delegated reviewers.

Act Before Ship findings folded:

- Strengthened #397 closeout from coverage count alone to runtime consultation
  of `quality-lenses.md`; matcher-only/spec-only changes are not evidence.
- Reframed `gate-sufficient` as eval-local claim-satisfied-by-gate, not
  deletion-candidate.
- Added probe write-back locations and deferred-decision reopen triggers.
- Replaced the non-runnable builder command with the concrete smoke command
  verified against the checked-in 2026-06-22 baseline bundle.
- Added acceptance-check coverage for all five success criteria, including the
  remediation decision, signal-separation report, and fan-out note shape.

Bundle-anyway findings folded:

- Separated minimum #397 repair evidence from full 39-reference methodology
  pilot evidence.
- Named the critique packet/result fields the closeout should preserve.

Over-worry not folded: requiring Cautilus `accept` as the only success signal;
the proof model remains deterministic coverage first, Cautilus recommendation
and runtime budget second.

## Canonical Artifact

This file is the canonical methodology contract for the active goal until a
later slice updates it with implementation-discovered facts.

## First Implementation Slice

Classify the quality skill's 39 declared references, probe the observation
builder's accepted `spec.json` shape, and add the engagement tags in the
least-disruptive compatible form.

## Full Public Fan-Out (2026-06-28)

The deferred "full all-skills fan-out" decision is taken for the public tier at
operator direction: all 19 remaining public skills now ship a claim-fidelity
`spec.json` beside the quality pilot, authored in one pass (a parallel
per-skill classification fan-out) as static assets. No live captures were run —
the eval-only/ask-before-run contract is unchanged, and a single-scenario
sample was deliberately skipped in favor of the full pass.

What shipped:

- `evals/cautilus/<skill>-claim-fidelity/spec.json` for every public skill,
  each with `declaredReferences` mirroring the skill's `references/` dir and a
  full `referenceEngagement` classification on the three-way axis (every
  `on-demand` records a trigger; `gate-sufficient` names a gate).
- `evals/cautilus/claim-fidelity-registry.json` indexing all 20 specs with a
  per-skill `fan_out_fit` note (SC5 fan-out disposition).
- `scripts/claim_fidelity_lib.py` + `scripts/validate_claim_fidelity_specs.py`,
  wired as the `validate-claim-fidelity-specs` standing gate (run-quality.sh +
  `tests/quality_gates/support.py`) and surfaced as `claim-fidelity-specs` in
  `.agents/surfaces.json`, with `tests/quality_gates/test_claim_fidelity_specs.py`.

Scope held to the contract:

- A per-skill spec covers only that skill's OWN `references/` dir. Shared
  references (`skills/shared/references/**`) are out of scope even when
  engage-always for the run (e.g. retro's `bootstrap-resolution.md`): the
  classifier dropped them from `declaredReferences`/`requiredCommandFragments`.
  This is a known limitation, recorded so a later slice can decide whether
  shared-ref coverage deserves its own axis.
- `thresholds` stay unset until a per-skill baseline capture sets a runtime
  budget, exactly as the quality pilot set `max_duration_ms` from a real run.
- `requiredCommandFragments` is the methodology's "if the run never opens this,
  it did not follow its own routing" signal, restricted to engage-always
  references the SKILL.md routes to at the point of need. It is the narrow
  hard-matcher subset, not the whole engage-always set (the quality pilot
  enforces 1 of 9). Where the fan-out initially set RCF to the full engage-always
  set, that is a calibration ceiling, not a floor: each skill's first live
  capture (ask-before-run) is where RCF gets tightened to what the run must
  actually open, exactly as the quality pilot derived its matcher from a run.
  `spec` was tightened during the closeout critique (13 -> 4) as the clearest
  over-claim.

Not done here (still open): live `/charness:<skill>` captures +
`cautilus evaluate observation` scoring per skill (ask-before-run, one at a
time); the quality pilot's own #397 runtime-consultation proof (goal Slice 7);
the support-skill tier.

## Schema Evolution (2026-06-28): Multi-Scenario Fixtures And Objective Prompts

The per-skill fixture review (handoff pinned task) surfaced two calibration
facts the original "one bare-prompt fixture per skill" schema could not express,
so the validator (`scripts/claim_fidelity_lib.py`) evolved:

1. **Objective-carrying prompts.** A bare `/charness:<skill>` only reaches the
   reference-routing phase for skills with a well-defined no-argument default
   action (`quality` reviews this repo; `find-skills` self-activates). A skill
   that needs a subject — an objective, a target file, a source URL — stalls at
   the "what do you want?" interview and opens zero references, failing every
   `requiredCommandFragments` for the wrong reason. The `prompt` field is now
   validated as `startswith /charness:<skill>` at a word boundary, so a
   representative objective can follow. The matcher inspects only file-open
   events, so prompt wording does not affect scoring; the prompt's only job is to
   drive the run into the routing phase.

2. **Multiple scenario fixtures per skill.** A skill whose workflow branches into
   mutually-exclusive flows cannot be honored by one fixture. `setup` detects
   greenfield versus partial/normalize, and `greenfield-flow.md` /
   `normalization-flow.md` are mutually exclusive (SKILL.md steps 1, 68-69), so
   the prior single fixture — which listed `greenfield-flow.md` in RCF — false-
   failed any partial-repo run. The registry now keys uniqueness on
   `(skill_id, scenario_id)`: the default scenario keeps `spec.json` and
   `execution-<skill>-claim-fidelity`; a named branch lives at
   `<scenario>.spec.json` with a matching `scenarioId` field and
   `execution-<skill>-<scenario>-claim-fidelity`. Coverage still requires every
   public skill to register at least one scenario. Splitting is applied only
   where the workflow genuinely branches — first application: `setup` →
   `greenfield` + `normalization`; single-flow skills stay one default fixture.

Capture-context non-claim: some scenarios need a repo STATE the prompt cannot
force (setup's greenfield branch needs a fresh-repo sandbox; a mature repo such
as charness always detects normalize). That constraint is recorded in the
scenario spec's `_comment` as an explicit non-claim, not a new validated field
(Floor-Addition Restraint: no new required schema for a one-off note).

## Per-Skill RCF Calibration Lenses (2026-06-28)

The per-skill review sets each skill's `prompt` and `requiredCommandFragments`
(RCF) by applying these lenses, in order:

1. **Planner as ground truth.** If the skill ships a deterministic planner or
   required-reads script (e.g. debug `plan_debug_run.py`), derive RCF from its
   UNCONDITIONAL required reads, not from prose. debug's prior RCF was inverted:
   it hard-matched the planner's on-demand reads (five-whys/detection-gap/
   sibling-search) and omitted the unconditional `five-steps.md` + `debug-memory.md`.
2. **Bare vs pin.** A bare `/charness:<skill>` reaches the reference-routing phase
   only for self-activators whose no-argument default action IS the claim worth
   testing (quality reviews this repo; critique autonomous-triggers). A skill
   whose no-arg default does NOT exercise its central claim (find-skills' default
   is a script-resolved inventory dump that reaches no doc-routing floor — lens 7)
   or that needs a subject gets a representative objective pinned into the prompt
   (the matcher inspects only file-open events, so wording cannot affect scoring).
   Pinning a representative SHAPE also makes shape-conditional RCF refs
   unconditional (create-cli multi-command CLI; create-skill external-tool skill).
3. **Script-resolved contract doc.** A reference that only EXPLAINS a contract the
   runtime resolves via a script (adapter-contract.md, resolved by
   resolve_adapter.py) stays engage-always but is demoted from RCF — the run reads
   the resolved output, not the explainer doc.
4. **Conditional / mutually-exclusive flows split into multiple fixtures.** setup
   (greenfield/normalization), critique (autonomous/decision): each branch is its
   own scenario fixture with its own RCF.
5. **Capture-context non-claim.** A scenario needing a repo STATE the prompt
   cannot fabricate (setup greenfield needs a fresh repo; debug needs a real
   reproducible bug) records that in the spec `_comment`; it is not faithfully
   runnable against a clean charness repo.
6. **Two-signal split for self-activators.** When an autonomous run's inferred
   target is non-deterministic (critique default), deterministic RCF proves only
   that the path was followed; inference QUALITY is the Cautilus-recommendation
   signal, not a hard matcher.
7. **Script-briefs-judge dissolves doc-RCF floors (sharper than lens 3).** When a
   skill's deterministic surface actively BRIEFS the judge — find-skills'
   `list_capabilities.py` emits a `next_step` that hands the agent the
   ranking-interpretation question and routes it to the doc — even a judgment doc
   becomes skippable, so a surviving RCF entry must be a doc whose UNIQUE content
   the script and SKILL.md body do NOT inline (discovery-order.md's tie-break
   rules), AND the prompt must force that content's use. find-skills' single
   `discovery-order.md` floor holds only because the pinned cross-layer tie
   (public `spec` vs synced-support `specdown`) needs the doc-only tie-break; the
   `_comment` records that prompt↔RCF coupling so a softened prompt cannot
   silently turn the floor into a false-fail.
8. **Executable subject, not just a shape (sharpens lens 2).** A pinned objective
   must carry a CONCRETE subject the run can act on — a real target file, URL,
   goal, decision, or applied behavior — not merely the SHAPE of the desired run.
   "implement a small code slice" (no slice named), "close out an applied
   behavior" (no behavior named), and "shape a new workflow concept" (no seed)
   each describe a run's shape while giving the agent nothing to begin on, so a
   representative run stalls at "what?" or invents its own subject — and the RCF
   floor then rests on a run that never actually occurs. Read the prompt as a
   literal first user turn and ask: can the agent act on a specific subject
   without asking me what I mean? If not, it is a shape, not a probe. Pin a real,
   repo-honest subject (hitl's `docs/operator-acceptance.md` is the model; impl on
   a named real slice; hotl on a real repo guard/behavior; ideation on a concrete
   seed). The live capture runs in the Cautilus sandbox, so a concrete subject
   with side effects (impl mutating code, hotl probing a real behavior) is safe to
   name — abstracting the subject to dodge side effects is a false economy that
   silently breaks executability. This lens caught impl/hotl/ideation prompts that
   passed an RCF-logic critique but were not executable (the critique brief had not
   asked the executability question — now loop step 6 requires it).
9. **Planner-absent is a shape to test, not a fixed input (the live-capture
   lesson).** Lens 1 derives RCF from a planner "if the skill ships one," and the
   loop's step 1 lets a planner-absent skill derive RCF from "the SKILL.md workflow
   + script-resolution analysis." That silently calibrates against a SHAPE GAP:
   when a skill's central claim routes to a doc through a PASSIVE prose pointer
   (not a deterministic brief), a capable run skips the doc and the static fixture
   freezes the miss as passing. Before accepting a planner-absent skill's shape as
   ground truth, ask the also-ask-better-shape question: should this skill HAVE a
   planner? If its central claim is a point-of-need doc route, yes — give it one
   (matching the planner family), anchor RCF to the planner's UNCONDITIONAL
   required_reads (lens 1), and the floor becomes real instead of frozen-gap.
   retro is the worked example: its `expert-lens.md` floor FAILED the first live
   capture (the prose pointer was skipped, the Engelbart lens missed); extracting
   `plan_retro_run.py` flipped it failed→proven (see
   `## Live-Capture Lesson — retro (2026-06-29)`).

## Per-Skill Review Protocol (2026-06-28)

A per-skill review is not fixture-only. Apply all three, every skill:

- **Fix the skill's own defect too — but do not manufacture one.** The fixture
  review surfaces real skill defects (find-skills routed on a ranking without
  surfacing the interpretation question; handoff's `/charness:handoff` bypassing
  its own chunker); fix those in the same pass, carried through `impl`. When the
  skill is genuinely sound (gather, hitl), say so plainly and ship fixture-only —
  the protocol is fix-the-defect, not invent-a-change.
- **North star over prose teeth.** Prefer making a deterministic surface brief the
  judge (a script that suggests the next move / answers-before-routing) over a
  SKILL.md sentence that hopes the agent remembers — the script briefing is
  stronger and unskippable at runtime. Teeth only where a wrong answer escapes.
- **Less but better.** Run a subtraction pass — delete now-redundant code/prose
  (the static SKILL.md pointer the script's `next_step` made redundant; the
  `recommendation_interpretation` artifact leak the critique caught; gather's dead
  `urlparse` host fallback). One source of truth per fact.

The per-skill loop (the cadence to resume in the same key):

1. Read the fixture + SKILL.md + the deterministic planner/scripts as ground truth
   (`plan_<skill>_run.py` / `*_lib.py`); a skill with no planner FIRST applies
   lens 9 (is planner-absence a shape defect to fix?) before deriving RCF from the
   SKILL.md workflow + script-resolution analysis.
2. Apply the lenses; derive RCF from the planner's UNCONDITIONAL, non-script-resolved
   reads only (the worst outcome is a false-fail).
3. Present findings + a recommendation to the operator; on a material fork
   (multi-fixture split, production-behavior skill fix) confirm scope before editing.
4. Edit the fixture + ship the skill fix if a real defect exists; sync the plugin
   mirror (`sync_root_plugin_manifests.py`); run the subtraction pass.
5. Verify: `validate_claim_fidelity_specs.py` + the skill's own tests + dup-ratchet
   / skill-ergonomics gates.
6. Fresh-eye `critique` in a different agent context; the brief MUST include the
   executable-subject check (lens 8: read the prompt as a literal first user turn —
   can a real run begin on a concrete subject, or does it stall/invent?) alongside
   the RCF-logic and matcher-gaming checks. Fold in only concrete fixes.
   Exception, by design: a scenario lens 5 marks as needing a repo STATE the
   prompt cannot fabricate (debug needs a real reproducible bug) is a recorded
   non-claim, not an executability defect — its `_comment` carries the non-claim.
7. Commit source + mirror + fixture + tests together; bump the handoff pointer.

## Live-Capture Lesson — retro (2026-06-29)

The first live capture of the shipped sweep (retro, the cleanest single-floor
skill) FAILED its static floor: a real `/charness:retro` filled the mandatory
counterfactual from inlined prose and never opened `expert-lens.md`, missing the
Engelbart system-improving lens that was the on-the-nose fit for self-improvement
work. Root cause: retro was left planner-absent by the 6/23-24 planner-first
sweep, so its routing was a passive pointer; the static calibration (loop step 1,
"SKILL.md workflow + script-resolution") froze that gap into the fixture as
passing. Two methodology changes (incremental):

1. **also-ask-better-shape (lens 9).** Calibration measured fidelity-to-current-
   shape and never asked whether the skill should have a better shape. A planner-
   absent skill whose central claim is a doc route is a shape defect to FIX (give
   it a planner, anchor RCF to its required_reads), not a fixed input to calibrate
   against.

2. **live-capture-before-assert.** A statically-calibrated behavioral RCF floor is
   a HYPOTHESIS, not a verified floor, until one live capture (ask-before-run, one
   at a time) proves the representative run actually opens it. The 19 remaining
   un-captured floors are provisional; a miss is a skill-shape signal (re-pin /
   re-classify / give-it-a-planner), never a matcher to soften.

Proof: `charness-artifacts/cautilus/retro-claim-fidelity-2026-06-29-recapture/`
(candidate `passed` vs baseline `failed`, A/B via comparison prepare); fix in
`167cad5c`.

Next: continue live captures on the provisional floors. Only 6 of 20 public
skills ship a `plan_*.py` planner (debug/gather/handoff/issue/quality/release);
the other 14 derive RCF via script-resolution, several with planner-EQUIVALENT
briefing scripts (find-skills' `list_capabilities.py`, hitl's
`check_review_state.py`). So lens 9 applies PER-SKILL only where a live capture
reveals the passive-pointer shape — NOT a blanket "planner-ize every
planner-absent skill." `hitl` is a flagged candidate (script-resolution-derived
RCF `43d066a9`; named by the re-capture's Sibling Search), but because it already
ships briefing scripts, confirm its shape by capture before assuming the retro
defect repeats. Rollout deferred to its own session.
