# Skill structure audit (Raskin + north-star) + quality ref-dedup pilot (2026-06-21)

Operator-requested: check, by the north-star standard, whether public skills are
well-structured — body length, concept separation, reference bloat — and whether
any skill should be **split**, through Jef Raskin's eyes (modelessness, monotony,
discoverability, locus of attention). Read-only fan-out audit of all 20 public
skills (one agent per skill), each split/merge proposal adversarially challenged.
Method artifacts: two dynamic workflows (audit + challenge). Nothing was applied.

## Headline

- **Structure is healthy. split = 0, merge = 0.** Every skill is one well-formed
  concept; lenses/phases (e.g. quality's 4 lenses, achieve's before/during/after)
  are facets of one lifecycle, not separate triggers. A per-lens split would
  shatter monotony into a routing maze that competes with siblings — worse than
  bloat. Sibling boundaries are crisp (quality vs code-review/debug/security-review;
  issue vs debug substrate-consumer; create-skill vs create-cli).
- **Body length is NOT the lever.** All 20 bodies are ratchet-capped at ~180–197
  lines (handoff 146 / hotl 147 are the only slack). Length alone is not a finding;
  cutting it further is the operator-rejected "fewer lines" metric.
- **The only recurring flag was reference duplication** (14/20 "trim-references",
  6 "healthy"). BUT see the pilot below: under test-verification these flags are
  **largely false positives** — the references are load-bearing.

## Verdict table

- healthy (no action): retro, hitl, narrative, ideation, find-skills, hotl.
- trim-references (flagged, needs per-flag test-verification): quality, critique,
  achieve, issue, create-skill, spec, setup, create-cli, debug, announcement,
  gather, impl, release, handoff.
- Quantitative leads (ref-lines): quality 4239/41files (22×, outlier), achieve
  1478 (lifecycle.md = 58%), critique 1313, issue 1101, spec 714/16files.

## Quality ref-dedup pilot — RESULT: surface already disciplined (no clean delete)

Ran the disciplined dedup on `quality` (the 22× outlier). All three audit flags,
on verification, are NOT clean deletion targets:

1. `quality-lenses.md` (124 lines) — audit said "un-routed duplicate". Deleting it
   **broke 3 tests** (`code-reduction`, `structure-over-heuristic`,
   `agent-production-runtime` lens are test-pinned). It is **load-bearing unique
   content**, not duplication. Reverted. Real (minor) defect: it is un-routed from
   body/dispatch → a discoverability gap fixable by **routing**, not deletion.
2. `skill-quality.md` ↔ `skill-ergonomics.md` — referenced by **~15 test files**
   (ergonomics gate, interpretation, runner). Both carry unique load-bearing
   machinery (ergonomics owns the `inventory_skill_ergonomics.py` advisory
   contract). The overlap is the review-question checklist only; a merge is a
   high-risk, test-heavy refactor, not a clean dedup.
3. `security-{npm,pnpm,uv}.md` — zero test pins (the only "clean" candidate), but
   each carries load-bearing per-manager nuance (npm multi-lockfile, pnpm
   overrides/workspace patching, uv dependency-free + package indexes; distinct
   audit commands). The audit itself rated it "acceptable to keep"; collapsing to
   a table flattens nuance and reduces per-manager discoverability — a net loss.

**Conclusion (mirrors the pin sweep's 126/128 keep): the surface is already
disciplined.** The 22× ratio is justified, test-pinned load-bearing content, not
deletable bloat. The Raskin audit's strong output was "structure healthy, no
splits/merges"; its reference-bloat flags were its weakest output.

## Re-scope for the next session (the "B" rollout)

- **NOT a 14-skill deletion sweep.** Treat the audit's per-skill flags as a
  "where to look" map only; **verify each flag against the test suite first** —
  expect mostly keeps. The pilot's false-positive rate (3/3 on quality) is the
  warning.
- Where a genuine fix exists, it is a **content-move refactor** (move unique
  load-bearing bullets to a routed ref + move the tests that pin them, then
  retire the source), NOT a deletion. Judgment-heavy; metric stays concept
  clarity, never line count.
- The one concrete small lead: `quality-lenses.md` is load-bearing but un-routed
  (Raskin discoverability gap) → add a dispatch/body pointer (routing), or do the
  audit's option-2 content-move. Deferred as judgment-heavy.
