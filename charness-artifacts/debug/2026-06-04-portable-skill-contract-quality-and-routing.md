# Debug: Portable Skill Contract Quality And Routing Discipline
Date: 2026-06-04

## Problem

The last long goal exposed two related failures: `achieve` coordinated the run
but did not consistently route implementation/debug-shaped work through
`impl`/`debug`, and portable skill text still contains repo-local history,
concrete issue anchors, overfull-core pressure, and other text-quality smells
after recent broad quality review. Issue numbers are one symptom, not the whole
problem.

## Correct Behavior

Portable public/support skills should be invariant-first, host/repo-neutral,
discoverable through `SKILL.md` plus references/scripts, and free of repo-local
incident chronology unless expressed as generic portable fixtures or moved to
repo-local artifacts.

When a goal slice becomes implementation, diagnosis, validation, issue closeout,
or review, `achieve` should coordinate and record the phase while the owning
skill supplies the phase contract. It should not silently become the execution
skill.

## Observed Facts

- The prior goal used `achieve`, `quality`, `critique`, `retro`, `issue`, and
  `handoff`, but did not explicitly invoke `impl` for implementation slices or
  `debug` for the fresh-eye blocker.
- `find-skills` routed this follow-up to `achieve`, `debug`, `handoff`, `impl`,
  `issue`, and `quality`, confirming a cross-skill boundary problem.
- Static scan found 106 concrete issue/history-anchor candidates under
  `skills/public` and `skills/support`.
- `skills/public/achieve/SKILL.md` has 0 core-line headroom: 160/160 core
  non-empty lines, 190/200 total lines.
- `quality` already says skill prose review remains required even when
  `inventory_skill_ergonomics.py` reports zero heuristic findings, but recent
  quality narrative still summarized the skill surface as healthy.
- The user clarified that every Charness skill must be portable and that issue
  numbers are only one text-quality symptom.

## Reproduction

```bash
rg -n '#[0-9]{2,}|issues/[0-9]{2,}|issue-[0-9]{2,}|corca-ai/charness#[0-9]{2,}' skills/public skills/support
python3 scripts/check_skill_surface_preflight.py --repo-root . --path skills/public/achieve/SKILL.md --preview-delta 0
python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json
```

The first command shows the anchor symptom, the second shows `achieve` core
overfill, and the third shows why zero heuristics is not proof of text quality.

## Candidate Causes

- Detection scope: no gate models portable skill text quality as a full
  contract.
- Routing scope: `achieve` coordination prose is not checked against slice-level
  phase evidence.
- Accretion: incident fixes left history and chronology in portable packages.
- Line budget: overfull cores encourage link swapping and compressed policy.
- Consumer gap: quality can surface "prose review still required" without making
  the final narrative engage the unresolved text-quality risk.

## Hypothesis

If Charness adds a portable skill text-quality inventory/gate and `achieve`
completion requires phase-routing evidence or explicit opt-outs, future
full-surface reviews will catch these issues earlier and long goals will stop
absorbing execution-skill work.

## Verification

- PASS: `find-skills` returned the relevant cross-skill route.
- PASS: static scan found 106 issue/history-anchor candidates under portable
  skill roots.
- PASS: skill-surface preflight showed `achieve` has no core-line headroom.
- PASS: quality artifacts show prose-review status exists but is not yet a
  strong final-consumer obligation.
- NOT RUN: no cleanup or validator implementation happened in this RCA slice.

## Root Cause

Charness validates skill package shape, links, line limits, and selected
ergonomics heuristics, but it lacks a portable skill text-quality contract that
final consumers must engage. Incident-specific rationale and repo-local anchors
could therefore accumulate while quality passes still appeared clean.

The `achieve` miss has the same final-consumer shape: the skill says it
coordinates other skills, but completion validation does not prove the right
owning skill handled each phase.

## Invariant Proof

- Invariant: portable skill text is invariant-first, repo-neutral, discoverable,
  and separated from repo-local incident history.
- Producer Proof: a future inventory should emit typed findings for history
  leakage, issue anchors, reference discoverability, core overfill, prose ritual,
  host assumptions, and exact-prose/source-guard risk.
- Final-Consumer Proof: `quality` closeout and `achieve` completion should cite
  typed findings or reviewed exceptions, not summarize zero heuristics as
  health.
- Interface-Shape Sibling Scan: check public/support skills, references,
  scripts/docstrings, plugin mirrors, quality artifacts, and active goals for
  "prose contract not consumed by final gate."
- Non-Claims: this RCA does not clean skill text, add the validator, or prove
  installed plugin propagation.

## Detection Gap

- skill text portability | no standing detector covers history leakage,
  discoverability, host assumptions, prose ritual, and source-guard risk
  together | add a typed inventory/gate and quality-consumption tests.
- quality artifact consumption | "prose review still required" can coexist with
  "skill surface is healthy" | require explicit unresolved/reviewed status.
- achieve phase routing | coordination prose is not checked against slice
  evidence | validate phase evidence or explicit opt-outs.
- reference discoverability | overfull `SKILL.md` cores can hide/drop links
  without failing | add reference/index checks or restructure overfull skills.

## Sibling Search

- Mental model: passing shape/link/heuristic checks means skill text is healthy.
- public core axis: valid follow-up; `achieve` core is 160/160.
- references axis: valid follow-up; references preserve history as contract.
- scripts/docstrings axis: valid follow-up; portable helpers ship comments too.
- quality-consumer axis: valid follow-up; prose-review status was underweighted.
- achieve-coordination axis: valid follow-up; `impl`/`debug` were skipped.

## Seam Risk

- Interrupt ID: portable-skill-text-quality-routing
- Risk Class: contract-freeze-risk
- Seam: human-readable skill contract to validators and final goal/quality
  consumers.
- Disproving Observation: recent quality review and broad closeout did not stop
  portable skill text quality issues or `achieve` execution-skill absorption.
- What Local Reasoning Cannot Prove: installed host copies until export/update
  paths are exercised.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-06-04-portable-skill-contract-quality-and-routing.md

## Prevention

Treat skill text quality as a portable contract with typed producer output and
final-consumer obligations. Issue anchors are one detector, not the policy.
`achieve` should validate phase ownership so it cannot bypass the skills that
own implementation, debugging, quality, issue closeout, review, and retro work.
