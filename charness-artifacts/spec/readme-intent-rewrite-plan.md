# README Intent Rewrite Plan
Date: 2026-04-17

## Goal

Turn the current README dissatisfaction into a repeatable improvement loop:

1. reach a README the user would actually approve through direct ping-pong
2. extract what the current `narrative` skill and repo-local adapter missed
3. upgrade `narrative` so it preserves intent, not only visible structure
4. prove the improvement with `cautilus`, then harden it with GEPA if the
   evaluation target is stable enough

## Current Working Thesis

The main failure was not missing surface rules by themselves.
The deeper failure was weak intent recovery and weak intent-preserving rewrite
judgment.

Examples already surfaced by the user:

- a public-skill taxonomy can disappear even when a flatter replacement still
  looks "organized"
- a README can gain product framing while losing the operator's first move
- sections can be structurally valid while still flattening the document's real
  hierarchy
- deletion can look like simplification while actually erasing a preserved
  intent that should have been carried forward in another form

## Sequence

### Phase 1. Lock the human target

Work directly with the user on this repo's README until the result is good
enough on human judgment, not on skill self-approval.

Deliverables:

- a revised README direction the user endorses
- a compact intent map for the current and prior README
- explicit notes on what was preserved, moved, compressed, or intentionally
  deleted

### Phase 2. Distill the missing `narrative` behavior

Compare:

- the README that `narrative` helped produce
- the README direction the user actually approves

Focus on failures of:

- intent extraction
- deletion review
- landing-page information architecture
- first-reader guidance
- boundary between README and reference docs
- confidence about when a structural suggestion is only a suggestion

Deliverables:

- an intent-preserving rewrite brief for `narrative`
- a repo-local adapter delta describing what this repo wants checked before a
  README rewrite is considered good

### Phase 3. Encode the improvement in the skill and adapter

Update the `narrative` skill and the charness repo-local narrative adapter so
the behavior becomes recoverable by another agent.

Priority direction:

- strengthen intent inventory before rewrite
- require deletion/absorption accounting for high-signal prior sections
- distinguish "proposed landing structure" from "required exact headings"
- keep section ordering and labels adaptable to repo context
- make README rewrites justify why a first-touch reader should see each block

Possible implementation surfaces:

- `skills/public/narrative/SKILL.md`
- `skills/public/narrative/references/*`
- `.agents/narrative-adapter.yaml`
- helper scripts or artifact format if intent accounting is otherwise too
  prose-only

### Phase 4. Test with `cautilus`

Build evaluation fixtures around this exact failure mode.

Candidate fixture families:

- previous charness README -> bad rewrite
- previous charness README -> approved rewrite
- sibling landing surfaces where intent is visibly preserved well
- adversarial cases where simplification deletes an important reader intent

Evaluation target:

- not exact section-title imitation
- not exact section-order imitation
- intent preservation
- correct absorption of old meaning into new structure
- first-reader usefulness
- honest README/reference-doc boundary decisions

### Phase 5. Improve with GEPA

Only run GEPA after the evaluation target is stable enough that score movement
means real improvement instead of prompt overfitting to a shaky rubric.

## Constraints

- README structure proposals are allowed to vary by repo.
- Exact heading text is not the contract unless a repo explicitly treats it as
  one.
- "Delete drift" does not justify deleting preserved intent.
- The README should remain a first-touch surface, not collapse into a second
  operator manual.

## Immediate Next Step

Draft the intent map for this repo's README and propose a candidate top-level
structure with block-by-block purpose.
