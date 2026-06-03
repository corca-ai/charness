# Session Retro: Generalized, Destination-Split Retro Issue Proposals

Mode: session

Goal: `charness-artifacts/goals/2026-06-03-retro-issue-structural-decouple-split.md`
(slug `retro-issue-structural-decouple-split`).

## Context

Goal run implementing the A4-lite contract that turns retro waste findings into
**structural, destination-routed** issue proposals instead of incident-coupled
ones (shared reference + retro/achieve/issue wiring + issue-adapter
`harness_upstream` + presence-only `validate_proposal_fields.py` + tests).
Committed as `6432d6c1`. This retro is the goal's After-phase review and the
live dogfood source for the new feature.

## Evidence Summary

- `git show --stat 6432d6c1` (15 files, +1198): the implemented surface.
- Broad gate run `./scripts/run-quality.sh --read-only` (62 passed / 7 failed)
  and the targeted re-runs that isolated which failures were mine vs
  environmental.
- `charness-artifacts/retro/recent-lessons.md` repeat traps (handoff edit
  cascade; fixtures pinning live issue numbers) — corroborating siblings.

## Waste

1. **Conciseness-ceiling breach forced a revert + extra gate cycle.** I added
   body prose to issue/retro/achieve `SKILL.md` without first checking each
   file's core(160)/total(200) headroom. `issue/SKILL.md` sat *exactly* at the
   ceiling (core 160, total 200), so any body addition breached `validate-skills`
   and the `long_core` ergonomics rule. Discovery came from the ~50s broad gate,
   not a pre-edit signal, forcing a full revert of the issue body change plus
   trims to retro/achieve and re-syncs.
2. **Reference-depth bug** (`../../` vs `../../../` from a `references/` subdir)
   and **wrapped inline code spans** — both only caught at gate time, each adding
   a fix + re-sync cycle.
3. **Broad gate before the cheap targeted set.** The four failure classes above
   (skills length, ergonomics, markdown spans, doc-link depth) are all catchable
   by a <2s targeted validator set; running the ~50s broad gate first also
   produced an environmental `check-runtime-budget` false-positive
   (check-duplicates timing under parallel load) that needed disambiguation.

Not waste: mapping the sync mechanism + test pins up front (necessary and reused
all session); the design discussion (user-requested).

## Critical Decisions

- **A4-lite** (distribute the two axes across retro/achieve/issue, each
  standalone) over centralizing in one skill. Kept skills standalone-useful but
  raised the "where does detail live" tension that collided with conciseness
  ceilings — resolved by carrying detail in the shared reference + issue-backend.md.
- **Presence-only validator**, never a content classifier — respected the
  achieve disposition-floor guardrail.
- **B1 adapter pointer + E1 collapse** for portable upstream identity over
  prompt-only inference — avoids wrong-repo filing.

## Expert Counterfactuals

- **Gary Klein (pre-mortem).** Before editing a skill surface, ask "which gate
  will this trip?" A 10-second `wc -l` + core-count on each target `SKILL.md`
  would have shown `issue` was at the ceiling, avoiding breach-then-revert.
- **Atul Gawande (checklist).** Skill-surface edits have a known coupled-gate set
  (conciseness, `long_core`, markdown spans, reference-depth doc-links, mirror
  sync). A cheap pre-flight running that set *before* the broad gate catches all
  four classes in one pass instead of serial gate-fail/fix cycles.

## Next Improvements

Each improvement is classified on the two axes the new contract introduces
(this is the dogfood of the feature shipped this run).

1. Pre-edit preflight for skill-surface edits.
   - `Structural pattern:` editing a `SKILL.md` (or its references) adds content
     with no pre-edit signal that the file is near the core(160)/total(200)
     conciseness ceiling, has a known coupling (reference link-depth, mirror
     sync), or will wrap an inline code span — so breaches surface only at the
     ~50s broad gate, forcing revert/trim/re-sync cycles. A cheap preflight that
     reports remaining core/total headroom and runs the targeted skill/doc/markdown
     validators would prevent the class.
   - `Triggering instance(s):` this run (issue at the ceiling; reference-depth and
     wrapped-span fixes) plus the 2026-06-03 handoff edit cascade in recent-lessons.
   - `Destination:` upstream-harness — kind: capability.
2. Stop hard-pinning live issue numbers in repo test fixtures.
   - `Structural pattern:` repo-local test fixtures that hard-pin live GitHub
     issue numbers (e.g. handoff Next-Session refs) break on unrelated issue
     closes, coupling unrelated edits to issue lifecycle churn. Pin via synthetic
     fixture data, not live state.
   - `Triggering instance(s):` #261 close broke `test_handoff_chunker_parse`
     (recent-lessons repeat trap); same class observed editing handoff this run.
   - `Destination:` repo-local — kind: workflow/capability (this repo's fixtures).

Improvements 1 and 2 are the upstream and repo-local halves of one root pattern
("skill/repo surface edits trip coupled gates"), which is exactly the D1 "both"
case the new contract is meant to split.

## Sibling Search

The "edit a surface without checking its known couplings" pattern is
transferable, so I scanned for siblings (four-axis: skill / script / doc /
workflow):

- skill: `SKILL.md` <-> conciseness/ergonomics ceilings (this run). Hit.
- doc: `references/*.md` link-depth <-> `check-doc-links`; handoff <-> doc-links
  (recent-lessons). Hit.
- script/fixture: tests pinning live issue numbers <-> issue lifecycle
  (recent-lessons #261). Hit.
- workflow: broad gate vs targeted-set ordering. Hit.

Decision: the siblings cluster into one upstream "pre-edit coupling preflight"
improvement (1) plus one repo-local fixture-decoupling improvement (2); filed as
the dogfood split rather than four separate narrow issues.

## Persisted

(to be set by the persistence helper)
