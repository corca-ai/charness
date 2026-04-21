# Cautilus Dogfood
Date: 2026-04-21

## Trigger

- slice: strengthen `hitl` so every review chunk shows the original material
  under review, with anchors and bounded context, instead of relying on
  summary-only paraphrase
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes repo-owned HITL instruction surfaces, but it should
  preserve the first-skill routing contract while making human-review chunks
  more explicit about the original text or diff being judged.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/hitl/SKILL.md`
- `skills/public/hitl/references/chunk-contract.md`
- `skills/public/hitl/references/state-model.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- checked-in `AGENTS.md` still preserves `bootstrapHelper=find-skills` plus
  `workSkill=impl`
- compact startup-bootstrap cases still passed unchanged:
  `find-skills -> impl` and `find-skills -> spec`

## Scenario Review

- representative scenario 1: a README wording review should now present the
  exact paragraph excerpt plus its line anchor, not only a prose summary of
  what the paragraph "roughly says"
- representative scenario 2: a diff review should now show the concrete hunk
  under review as the smallest excerpt sufficient for judgment, with any extra
  context separated as context rather than replacing the hunk itself
- representative scenario 3: resumed HITL state now has to keep enough source
  anchor or excerpt data that the next chunk does not fall back to summary-only
  reconstruction

## Outcome

- recommendation: `accept-now`
- routing notes: strengthening HITL chunk presentation did not regress the
  checked-in startup routing contract, and the compact synthetic routing cases
  still matched the evaluator expectation

## Follow-ups

- if the repo wants stronger enforcement than prose contract alone, add queue
  or artifact validation that rejects HITL chunks missing original-material
  excerpts or anchors
- if future dogfood shows that "smallest sufficient excerpt" still causes
  context misses, keep the original-material rule and tune the context-window
  rule rather than relaxing back to summary-only review
