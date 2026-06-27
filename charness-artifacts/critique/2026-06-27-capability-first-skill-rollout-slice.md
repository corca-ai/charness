# Capability-First Skill Rollout Slice Critique
Date: 2026-06-27

## Decision Under Review

Mutate the first non-release rollout target after the `create-cli` pilot:
`create-skill` should require a capability brief before public skill edits,
without converting generative sequence or capability language into a universal
gate. Existing v0.56.7 release WIP is out of scope and was ignored.

## Verdict

PASS WITH NOTES after remediation. The slice now improves `create-skill`'s
authoring contract, keeps the mirror synchronized, and records that
`ideation`, `spec`, `impl`, and irreversible-boundary skills are not claimed
migrated by this change.

## Reviewer Findings

Act Before Ship:

- The quality artifact originally proved only producer-side validation. It now
  records consumer dogfood evidence and the Cautilus scenario-review
  disposition for `create-skill`.
- The first wording made current/next-center language too universal. The skill
  now says to name current and next center only when improving an existing skill
  or when order matters.
- Focused post-mutation checks and mirror proof were required before closeout.
  These ran after remediation, including `validate_skills.py`,
  `check_doc_links.py`, markdown lint, skill ergonomics, public-skill dogfood,
  packaging validation, and mirror comparison.

Bundle Anyway:

- Keep the dated goal and quality artifacts with this slice; do not refresh the
  `quality/latest.md` pointer just to make an active local rollout look global.
- Keep `ideation`, `spec`, and `impl` as reviewed-but-deferred targets until the
  create-skill authoring contract proves useful in more than one slice.

Over-Worry:

- No live Cautilus run is required. The planner reported `next_action: none`;
  this prompt-affecting edit needs scenario review, not evaluator execution.
- No broad pytest or release proof is required while unrelated v0.56.7 WIP is
  dirty and the slice does not touch runtime behavior.

Valid But Defer:

- `create-skill` frontmatter still carries topology-heavy language; that is a
  possible later capability-improvement target, not necessary for this slice.
- A future rollout should apply the brief to `ideation` or `spec` and then
  decide whether their output shapes need concrete skill-improvement move cards.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: metadata-hidden
- Application state: parent spawned bounded reviewers
  `019f0780-e084-78e2-a6c5-a8f8ee9863d0`,
  `019f0781-8c2f-7303-a39a-2fe9397a3f73`, and
  `019f0781-573a-7902-954f-5915a5b4a7a8`; host accepted the agents but did not
  expose applied tier metadata.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Parent consumed the returned
four-bin critiques, remediated the Act Before Ship findings, and kept release
WIP out of the slice proof.
