# Recent Retro Lessons

## Current Focus

- This slice reviewed recent bug-fix patterns and closed issues, then hardened two sibling seams: direct current-pointer writes to `latest.*` artifacts and gitignore-blind standing scans. (source: `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`)
- Reviewing the 2026-05-20 quality session that landed depth-bounded `_pytest_temp_footprint`, `release_only` routing, `## References` link inventory, and the seed-fixture budget gate. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)

## Repeat Traps

- **Added `check-seed-fixture-budget` before asking root-cause questions.** First instinct was to bound the 9.78 GiB advisory finding. The structural fix (`release_only` routing) was already declared in `pyproject.toml:3-4` and saved 70% pytest time once routed; it was waiting to be honored, not invented. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)
- **Audit only happened on user push.** "그 테스트들이 뭘 하는 거죠? 예전에는 가치있었지만 이제 필요없을 것 같은." This was the right first question for any expensive test fixture; I should have asked it myself before recommending a fixture refactor. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)
- **Quoted "~1.4 GiB per seed" from a mental model, not measurement.** Real per-seed is 26-54 MB; the cost is fan-out, not seed size. Multiple commits carried imprecise numbers before the user pushed (`왜 아직도 seed materialization이 필요한가?`) and I ran `du`. The diagnostic landed in commit `2c6f873` only after that push. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)
- **Treadmill bias in `Recommended Next Gates`.** Quality skill ended each turn with "add more gates" (budget gate, references link inventory, advisory-only scope classifiers, attention-state declarations). I produced three new gates before the user prompted me to look for an existing convention being violated. The 2026-05-17 empty-policy lesson warns about invisible advisory state but I did not extend it to "advisory cost." (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)

## Next-Time Checklist

- before promoting a new source scanner, add one mixed safe/unsafe fixture so helper-use exemptions cannot mask direct violations. (source: `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`)
- carry the current-pointer helper boundary in the debug seam-risk index so future artifact-writing changes start from the same distinction. (source: `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`)
- keep `check_current_pointer_writes.py` narrow until another concrete `latest.*` write shape is observed; expand by fixture, not by broad text search. (source: `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`)
- **Anti-need before need in `Recommended Next Gates`.** Before proposing a new enforcement gate for an advisory cost, the workflow must check (a) `git log -S <subject>` for origin context, (b) `grep -rn <subject>` for existing markers and conventions, (c) `rg -tpython "<subject>" pyproject.toml` for existing routing. Add a new gate only after confirming no existing convention is being violated; otherwise the recommendation is a routing fix. ### capability (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`
- `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`
