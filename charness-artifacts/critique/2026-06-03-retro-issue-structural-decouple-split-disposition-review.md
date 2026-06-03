# Disposition Review: Generalized, Destination-Split Retro Issue Proposals
Date: 2026-06-03

Fresh-Eye Satisfaction: parent-delegated

Binds to goal slug `retro-issue-structural-decouple-split`.

## Scope

- Goal: `charness-artifacts/goals/2026-06-03-retro-issue-structural-decouple-split.md`
- Retro: `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`
- Host probe: `charness-artifacts/probe/2026-06-03-retro-issue-structural-decouple-split.json`
- Implementation commit: `6432d6c1`
- Dogfood issues: #284 (upstream-harness), #285 (repo-local)

## Fresh-Eye Review Outcome

A different-context bounded reviewer audited commit `6432d6c1` plus the closeout.
Verdict: `ship-with-nits`. It confirmed the load-bearing invariants — presence/
enum-only validator (not a content classifier), correct B1/E1/unknown resolver,
faithful `plugins/charness/**` mirrors, `issue/SKILL.md` byte-identical to base
(unbloated), correct reference-link depths — and found one real bug plus two nits,
all folded:

- Real bug (fixed): `validate_proposal_fields.py` used `\s` (which matches the
  newline under `re.MULTILINE`), so a label with an empty value backtracked across
  the line boundary and stole the next line as its value — under-enforcing the
  very presence contract the feature exists to uphold. Fixed to horizontal-
  whitespace-only matching; added `test_empty_value_treated_as_missing` as a
  regression guard.
- Nit (fixed): two Python docstrings used `../../shared/...`; corrected to
  `../../../shared/...` for their `scripts/` depth.
- Nit (kept): `.agents/issue-adapter.yaml` `repo: charness` is consumed by the
  generic adapter validator (it is required, not dead config); the issue resolver
  reads `harness_upstream`, which is what the feature needs.

## Per-Improvement Verdicts

- `Pre-edit preflight for skill-surface edits (headroom / coupling / markdown)`:
  dispositioned as `issue #284` (upstream-harness) in goal `## Auto-Retro`.
- `Stop hard-pinning live issue numbers in repo test fixtures`: dispositioned as
  `issue #285` (repo-local) in goal `## Auto-Retro`.

## Binding Checks

- Both dogfood issues are bound: the goal `## Auto-Retro` names #284/#285, and
  each issue body carries the `Structural pattern:` / `Triggering instance(s):` /
  `Destination:` fields and verified `OPEN` on GitHub.
- Retro evidence is bound both ways: the retro names the goal context, and the
  goal `## Auto-Retro` names the retro artifact.
- Host probe evidence is bound: the goal names the probe JSON, and the probe
  records the goal path under `goal_metric_window.path`.

## Blockers

- None. The one real bug was fixed and regression-tested before this review was
  recorded.
