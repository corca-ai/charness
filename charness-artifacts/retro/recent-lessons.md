# Recent Retro Lessons

## Current Focus

- `charness-artifacts/spec/issue-109-spec-authoring-discipline.md` — design extraction only 다음 세션이 보통 같은 결의 issue closeout을 또 만났을 때 더 빠르게 닿는 게 이번 retro의 목표다. (source: `charness-artifacts/retro/2026-05-07-issue-108-109-closeout.md`)
- Compressed the `quality` public skill from a dense manual into a fast-path orchestrator while preserving checked-in plugin export, find-skills discovery, public-skill dogfood, and prompt-surface proof policy. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)

## Repeat Traps

- **`Close` 키워드를 첫 번째 이슈에만 붙였다.** 커밋 메시지가 `Close #108 by claim, #109 by design extraction`이었는데, GitHub auto-close는 키워드가 직전 토큰일 때만 fire 한다. 결과적으로 #108은 자동 close, #109는 수동 close + comment를 따로 호출해야 했다. 한 줄짜리 손해지만 실제 동작이 정확히 검증돼야 하는 흐름. (source: `charness-artifacts/retro/2026-05-07-issue-108-109-closeout.md`)
- Exact snippet pins were meant to keep load-bearing behavior from being deleted, but they also made useful skill compression look unsafe unless anchor text stayed in `SKILL.md`. (source: `charness-artifacts/retro/2026-05-07-validator-support-discovery.md`)
- Existing tests still asserted exact `SKILL.md` snippets for detail that now belongs in references. That reproduced the validator brittleness the user had flagged. (source: `charness-artifacts/retro/2026-05-07-skill-compression-validator-flex.md`)
- **find-skills bootstrap 경로 가정 미스.** SKILL.md의 bootstrap이 `python3 "$SKILL_DIR/scripts/resolve_adapter.py"`를 권하는데 처음에 repo root의 `scripts/resolve_adapter.py`로 호출했다 — 존재하지 않는 path. 즉시 정정했지만 매번 반복하면 지속 비용. (source: `charness-artifacts/retro/2026-05-07-issue-108-109-closeout.md`)

## Next-Time Checklist

- before broad skill compression, classify each sentence as trigger, stop gate, proof route, or reference detail. (source: `charness-artifacts/retro/2026-05-07-skill-compression-validator-flex.md`)
- before compressing or judging a public skill, inspect exact-string validators and classify each checked phrase as core, package detail, or a candidate for behavior-level proof. (source: `charness-artifacts/retro/2026-05-07-validator-support-discovery.md`)
- before shrinking a public skill, inspect exact-string contract validators first and decide which snippets are real core versus anchor-only. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)
- **capability**: 현재 가벼운 미스는 따로 capability 변경을 정당화하지 않는다. bootstrap path 미스도 한 번이라 SKILL.md 수정은 과잉. (source: `charness-artifacts/retro/2026-05-07-issue-108-109-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-07-issue-108-109-closeout.md`
- `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`
- `charness-artifacts/retro/2026-05-07-skill-compression-validator-flex.md`
- `charness-artifacts/retro/2026-05-07-validator-support-discovery.md`
