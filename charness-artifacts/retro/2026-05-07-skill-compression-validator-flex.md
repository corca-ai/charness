# Session Retro: Skill Compression And Validator Flexibility

## Context

This session finished the public-skill compression and validator flexibility
slice before push. The important surfaces were public `SKILL.md` bodies,
`check_skill_contracts.py`, support-skill discoverability for `specdown`, and
checked-in plugin exports.

## Evidence Summary

- `./scripts/run-quality.sh --read-only`: 51 passed, 0 failed.
- `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`: completed.
- Fresh-eye reviewers found load-bearing routing and proof triggers that had
  been over-compressed, plus one untracked reference-file risk.

## Waste

- The first compression pass removed some strings that were not just prose:
  validation-route discovery, success-criteria review escalation, impl
  fresh-eye stop gate, and prompt-surface proof policy.
- Existing tests still asserted exact `SKILL.md` snippets for detail that now
  belongs in references. That reproduced the validator brittleness the user had
  flagged.
- Running a sync/read command from a stale installed cache earlier rewrote
  `find-skills/latest.*` without rich references; final sync had to be repeated
  with the repo-local script.

## Critical Decisions

- Keep core routing and stop-gate triggers in `SKILL.md`; move only detail-heavy
  package promises to references.
- Let tests use package-level text for reference-worthy details, while keeping
  core snippets body-only through `CORE_CONTRACTS`.
- Treat support-skill discovery as task-text routing, not only named-skill
  lookup; `specdown` must surface from `docs/specs`, `run:shell`, `check:jq`,
  and similar task language.

## Expert Counterfactuals

- Gary Klein: run a pre-mortem before compressing each core paragraph and ask
  "what operator action disappears if this sentence moves?" That would have
  caught the validation-route and success-criteria review regressions earlier.
- Kent Beck: make the first test change express the new contract shape
  (`SKILL.md` core vs package text) before deleting prose. That would have
  shortened the red/green loop and reduced exact-snippet churn.

## Next Improvements

- `workflow`: before broad skill compression, classify each sentence as trigger,
  stop gate, proof route, or reference detail.
- `capability`: keep `check_skill_contracts.py` as the canonical example of
  body-only core contracts plus package-level reference contracts.
- `memory`: when a generated artifact can be produced by both installed-cache
  and repo-local scripts, use the repo-local source script before final sync.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-07-skill-compression-validator-flex.md`
