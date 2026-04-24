# Spec: Issues #65 and #66 - decision frames and enum-axis checkpoints

Source:

- https://github.com/corca-ai/charness/issues/65
- https://github.com/corca-ai/charness/issues/66

This spec covers one prompt-surface slice across `ideation`, `spec`, and
`find-skills`.

## Problem

Charness has two adjacent reasoning gaps:

1. Decision-shaped prompts such as "what do we need to decide?", "what are the
   issues?", "뭘 결정해야 하죠?", and "쟁점은?" can route to a plausible skill
   without giving the operator the decision frame they asked for.
2. When a workflow proposes a new mode, kind, strategy, profile, target, or
   similar enum value, the public skills do not consistently challenge whether
   the values belong to one conceptual axis.

Both gaps create the same failure mode: extra user-facing choice appears before
the agent has clarified the actual decision.

## Current Slice

Add two small reusable references and wire them into the public workflow skills
that need them:

- `skills/public/ideation/references/decision-question-response.md`
- `skills/public/spec/references/taxonomy-axis-checkpoint.md`

Then connect them from:

- `skills/public/ideation/SKILL.md`
- `skills/public/spec/SKILL.md`
- `skills/public/find-skills/SKILL.md`

## Fixed Decisions

- **One implementation slice handles both issues.** The issues share a
  "decision before choice surface" invariant, and splitting them would duplicate
  routing language.
- **No new public skill.** These are behavior-shaping checkpoints for existing
  workflows, not a new user-facing workflow concept.
- **`ideation` owns decision-question response shape.** It already carries
  `Decision Candidates`, `Recommended Current Decision`, and `Alternatives and
  Tradeoffs`.
- **`spec` owns enum-axis checkpoints before contract lock.** Spec is where
  user-facing API/CLI/config vocabulary hardens into implementation contracts.
- **`find-skills` gets only a routing guardrail.** It should not become the
  answer style for ordinary decision questions.
- **Guidance stays in references.** Public `SKILL.md` files should stay as
  trigger contracts and decision skeletons, with examples and edge cases below
  the core.

## Probe Questions

- Q1. Should `taxonomy-axis-checkpoint.md` live under `ideation` or `spec`?
  - Current default: `spec`, because API/CLI/config enum vocabulary is a
    contract-locking concern.
  - Mitigation: `ideation/SKILL.md` still references the checkpoint when a
    concept introduces a new mode/kind before spec.
- Q2. Should `find-skills` mention Korean trigger examples?
  - Current default: yes, but only as examples of ordinary decision language
    that should usually route to `ideation` or `spec`, not capability search.
- Q3. Do we need executable evaluator scenarios now?
  - Current default: not in this slice. This change touches prompt behavior, so
    cautilus proof and short scenario-review notes are required, but maintained
    scenario registry mutation is deferred unless proof shows a miss.

## Deferred Decisions

- Whether to promote decision-question response shape into a shared reference
  outside `ideation`.
- Whether to add a deterministic validator for enum-axis wording after this
  pattern repeats in more public skills.
- Whether to add maintained cautilus scenarios for #65/#66 after this first
  prompt-surface repair has been dogfooded.

## Non-Goals

- No new CLI flags, modes, schema fields, or adapter configuration.
- No change to the actual Cautilus optimizer taxonomy.
- No broad rewrite of `ideation`, `spec`, or `find-skills`.
- No generic instruction that every question must stop for confirmation before
  implementation.

## Deliberately Not Doing

- **Adding a `decision` public skill.** The user is usually asking the current
  workflow to frame its next choice, not asking to switch workflows.
- **Making `find-skills` the default for "what should we decide?"** That would
  answer routing when the operator asked for judgment.
- **Adding `simplification` or similar enum examples as recommended taxonomy.**
  The example exists to show the checkpoint, not to bless a replacement design.
- **Making every enum split invalid.** The checkpoint should allow a new
  user-facing enum when it creates safety, clarity, or interoperability.

## Constraints

- Keep manually maintained docs in English.
- Keep `SKILL.md` core concise and push examples into references.
- Avoid host-specific behavior in public skill bodies.
- Since this changes public skill prompt surfaces, run skill validation,
  markdown/secret checks, and the repo's cautilus planning/proof path.
- If generated plugin export surfaces are affected, sync before validators.

## Success Criteria

1. `ideation` explicitly recognizes decision-shaped prompts and answers with
   the decision, 2-4 options, tradeoffs, recommendation, reasons, and next step.
2. `spec` explicitly runs a taxonomy-axis checkpoint before adding a new
   user-facing mode/kind/strategy/profile/target enum.
3. Mixed-axis enum values are named as mixed purpose, method, evidence source,
   trigger/reason, objective, selection policy, or internal preset.
4. The guidance prefers strong defaults and internal presets unless a
   user-facing enum does real safety or clarity work.
5. `find-skills` clarifies that capability discovery is not the default answer
   to ordinary decision-shaped prompts.
6. `find-skills` still owns explicit skill/capability/support discovery prompts,
   including "which skill handles this?" and named `X skill` / `support/X`
   requests.
7. Korean examples from #65 are represented in the decision-question reference.

## Acceptance Checks

- **A1**:
  `rg -n "decision-shaped|뭘 결정|쟁점|2-4" skills/public/ideation`
  finds the decision response guidance.
- **A2**:
  `rg -n "taxonomy-axis|mode/kind/strategy|purpose|method|evidence source|selection policy" skills/public/spec`
  finds the enum-axis checkpoint.
- **A3**:
  `rg -n "decision-shaped|capability discovery" skills/public/find-skills/SKILL.md`
  finds the routing guardrail.
- **A4 (Scenario)**:
  A Korean prompt such as "다음 작업 계속해봅시다. 뭘 결정해야 하죠?" is covered
  by guidance that produces a core decision, 2-4 options, tradeoffs,
  recommendation, reasons, and next step.
- **A5 (Scenario)**:
  An explicit capability prompt such as "which skill handles release?" or
  "quality skill 있죠?" still routes through `find-skills`.
- **A6 (Scenario)**:
  A proposal to add a new mixed-axis enum such as optimizer kind
  `simplification` is challenged by separating reason, evidence focus,
  objective, selection policy, and internal preset/default alternatives.
- **A7**:
  `python3 scripts/validate_skills.py` passes.
- **A8**:
  `./scripts/check-markdown.sh` and `./scripts/check-secrets.sh` pass.
- **A9**:
  `python3 scripts/check_doc_links.py` passes because new references are linked.
- **A10**:
  Prompt-surface proof is refreshed or the release closeout records the exact
  cautilus blocker instead of calling same-agent review enough.

## Premortem

Spec review should stress these risks before implementation:

- A reviewer could read the new decision response frame as mandatory ceremony
  for every question, slowing down concrete implementation requests.
- A reviewer could read the taxonomy checkpoint as "never add enums", blocking
  legitimate compatibility or safety vocabulary.
- The guidance could duplicate between `ideation` and `spec`, causing future
  drift.
- `find-skills` could overcorrect and stop helping when routing is genuinely
  ambiguous or when the user explicitly asks for a skill/capability.

Tightening rule: `SKILL.md` bodies should contain only the trigger/checkpoint
hook. Detailed examples and anti-overuse rules belong in references.

## Canonical Artifact

`charness-artifacts/spec/issue-65-66-decision-taxonomy-routing.md`

## First Implementation Slice

1. Add `ideation/references/decision-question-response.md`.
2. Add `spec/references/taxonomy-axis-checkpoint.md`.
3. Wire concise hooks into `ideation/SKILL.md`, `spec/SKILL.md`, and
   `find-skills/SKILL.md`.
4. Run acceptance checks and prompt-surface proof planning.
5. Run implementation premortem with bounded subagents before release prep.
