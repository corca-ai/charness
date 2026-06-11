# Quality Duplication Improvement 6h Retro
Date: 2026-06-11

## Mode

session

## Context

This retro closes the active goal
`charness-artifacts/goals/2026-06-11-quality-duplication-improvement-6h.md`.
The run started from user concern that the new `nose` findings and repeated
bootstrap/scaffold structures might be hiding real quality debt, not just noisy
portable boilerplate.

## Evidence Summary

- Commit `23c12960` simplified 11 public skill `init_adapter.py` bootstrap
  loaders and synced plugin mirrors.
- Commit `a153ca80` extracted achieve goal-artifact markdown fence masking into
  one helper.
- Commit `beb7c28f` extracted scaffold validator, CLI output, and current-pointer
  payload logic into `scripts/scaffold_artifact_lib.py`.
- Commit `daa4a05b` split find-skills workflow recommendations and summary
  output into leaf helpers.
- Broad `nose --top 0`: moved from `526 families / 13164 dup_lines` at the run
  baseline to `525 families / 12580 dup_lines` at closeout.
- Python length warn-band count moved from `10` files before the find-skills
  slice to `8` files at closeout.
- Broad pytest passed after the last two implementation slices:
  `2803 passed, 4 skipped, 26 deselected`.

## Waste

The main waste was proving that not every duplication-looking family should be
collapsed. Resolver and bootstrap loader repetition is partly portability
scaffolding, so the useful work was separating extractable behavior from
root-discovery boilerplate instead of chasing the largest `nose` numbers.

## Critical Decisions

- Used `nose --exclude` for focused analysis only, not as proof that excluded
  duplication disappeared.
- Avoided broad `resolve_adapter.py` commonization because public skill export
  safety needs a narrower shared contract first.
- Kept scaffold templates local while extracting only shared validator, CLI, and
  current-pointer mechanics.
- Switched from duplicate-only cleanup to length-gate cleanup once the next
  safer quality signal was `find-skills` warn-band pressure.

## Expert Counterfactuals

- A portability reviewer would have stopped a broad resolver refactor up front
  and asked for the same narrower helper boundaries used here.
- A quality-gate maintainer would have prioritized the find-skills length split
  once it became clear the next duplicate families were mostly bootstrap
  surface, not behavior.

## Sibling Search

n/a - examined sibling surfaces during the run; no additional transferable rule
is ready beyond the applied helper-extraction pattern and the residual ledger
below.

## Next Improvements

- applied: keep using `nose` scope filters as review lenses, not success metrics.
- accepted-risk: broad `resolve_adapter.py` duplication remains until a smaller
  shared resolver contract can prove public skill export safety.
- accepted-risk: remaining bootstrap loader duplication should be reduced only
  where a script already has focused tests or a cohesive helper boundary.
- out-of-scope: installed tool upgrades surfaced by diagnostics (`defuddle`,
  `gws`, and newer upstream releases) are not part of this local quality goal.

## Persisted

yes: `charness-artifacts/goals/2026-06-11-quality-duplication-improvement-6h.md`
