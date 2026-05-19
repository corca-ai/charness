# Recent Retro Lessons

## Current Focus

- Reviewing the 2026-05-20 quality session that landed depth-bounded `_pytest_temp_footprint`, `release_only` routing, `## References` link inventory, and the seed-fixture budget gate. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)
- The setup skill cleanup exposed a repeated quality pattern: `gate_rules` or similar list fields can be empty, leaving a validator advisory-only while the standing gate still reports a clean pass. (source: `charness-artifacts/retro/2026-05-17-empty-policy-silent-pass.md`)

## Repeat Traps

- **Added `check-seed-fixture-budget` before asking root-cause questions.** First instinct was to bound the 9.78 GiB advisory finding. The structural fix (`release_only` routing) was already declared in `pyproject.toml:3-4` and saved 70% pytest time once routed; it was waiting to be honored, not invented. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)
- **Audit only happened on user push.** "그 테스트들이 뭘 하는 거죠? 예전에는 가치있었지만 이제 필요없을 것 같은." This was the right first question for any expensive test fixture; I should have asked it myself before recommending a fixture refactor. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)
- **Quoted "~1.4 GiB per seed" from a mental model, not measurement.** Real per-seed is 26-54 MB; the cost is fan-out, not seed size. Multiple commits carried imprecise numbers before the user pushed (`왜 아직도 seed materialization이 필요한가?`) and I ran `du`. The diagnostic landed in commit `2c6f873` only after that push. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)
- **Treadmill bias in `Recommended Next Gates`.** Quality skill ended each turn with "add more gates" (budget gate, references link inventory, advisory-only scope classifiers, attention-state declarations). I produced three new gates before the user prompted me to look for an existing convention being violated. The 2026-05-17 empty-policy lesson warns about invisible advisory state but I did not extend it to "advisory cost." (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)

## Next-Time Checklist

- **Anti-need before need in `Recommended Next Gates`.** Before proposing a new enforcement gate for an advisory cost, the workflow must check (a) `git log -S <subject>` for origin context, (b) `grep -rn <subject>` for existing markers and conventions, (c) `rg -tpython "<subject>" pyproject.toml` for existing routing. Add a new gate only after confirming no existing convention is being violated; otherwise the recommendation is a routing fix. ### capability (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)
- **Measurement-before-claim rule.** When the quality skill (or any skill) writes a number for a size, runtime, or cost, the number must come from a command run this turn. Estimates must be labeled "estimate" with the reason measurement was skipped. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)
- Promote into `recent-lessons.md` (via summary refresh): - "Measure before quoting a size/runtime number; estimates must be labeled and justified." - "Before adding an enforcement gate for an advisory cost, grep for existing markers, policies, and `git log -S` for prior owner intent. A routing fix is often higher ROI than a new gate." - "Quality `Recommended Next Gates` has a treadmill bias toward additive enforcement; explicitly ask whether an existing convention is being violated before adding." (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)
- **Quality skill `Recommended Next Gates` proposal flow.** Extend `skills/public/quality/references/proposal-flow.md` to require a one-line "existing convention check" beside each recommendation, with the format "no existing marker/comment/policy already governs this cost; gate is additive, not duplicative." If a marker exists, the recommendation must be the routing fix instead. ### memory (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-17-empty-policy-silent-pass.md`
- `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`
