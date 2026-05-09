# Recent Retro Lessons

## Current Focus

- 이번 세션은 [#122](https://github.com/corca-ai/charness/issues/122)·[#123](https://github.com/corca-ai/charness/issues/123)·[#124](https://github.com/corca-ai/charness/issues/124)을 묶어 한 번, 이어 [#125](https://github.com/corca-ai/charness/issues/125)·[#126](https://github.com/corca-ai/charness/issues/126)·[#127](https://github.com/corca-ai/charness/issues/127)을 묶어 한 번 — 총 두 슬라이스로 닫았다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)
- `charness-artifacts/spec/issue-109-spec-authoring-discipline.md` — design extraction only 다음 세션이 보통 같은 결의 issue closeout을 또 만났을 때 더 빠르게 닿는 게 이번 retro의 목표다. (source: `charness-artifacts/retro/2026-05-07-issue-108-109-closeout.md`)

## Repeat Traps

- **Bundle Anyway 항목을 사후에야 발견.** premortem이 "closeout-discipline.md를 SKILL.md 세 anchor에서 cite 했는지 검증하는 cheap test 추가"를 짚어줬는데, 이는 첫 contract test 작성 시 같이 들어갔어야 하는 패턴이었다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)
- **`MAX_SKILL_MD_LINES=200` 직격을 두 번 맞았다.** 1차 슬라이스에서 HITL SKILL.md(208줄) → impl SKILL.md(202줄) → issue SKILL.md(216줄) 순으로 budget을 넘겼고, 2차 슬라이스에서도 issue SKILL.md(214줄)가 또 넘었다. 매번 검증→압축→ 재검증 사이클을 돌았다. 추가 분량을 알고 있을 때 _먼저_ 기존 텍스트를 압축해 슬롯을 확보한 뒤 새 contract를 추가하는 순서였다면 한 번에 끝났다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)
- **인라인 코드 스팬이 markdown lint에서 wrap 검출에 걸렸다.** 두 슬라이스 모두 `gh issue create --repo <org/repo>` 같은 긴 backtick span이 줄 끝에 걸쳐 pre-commit이 한 번 더 실패했다. 본문 작성 시 backtick span 시작을 줄 머리 가까이 두는 mental model이 없었다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)
- **테스트 환경 변수 PATH 설정 미스.** `test_issue_preflight_resolves_adapter_backend_when_gh_absent`에서 `env={"PATH": f"{bin_dir}"}`로 시작했더니 `python3` 자체가 PATH에 없어 SubprocessError로 죽었다. 즉시 `:/usr/bin:/bin`을 추가했지만 테스트 작성 시 흔히 잊는 디테일. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)

## Next-Time Checklist

- **capability**: SKILL.md 압축-친화 helper 후보가 떠올랐다 — `inventory_skill_ ergonomics.py`나 `validate_skills.py` 옆에 "MAX_SKILL_MD_LINES까지 N줄 남았다" 를 보여주는 dry-run 헬퍼가 있다면 budget 초과 전에 압축 슬롯 확보가 자연스 러워진다. 다만 한 번 패턴이라 capability 변경은 미루고 다음 회 같은 트랩이 반복되면 그때 짓는다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)
- **memory**: 본 retro가 lesson durable persistence. 다음 세션은 recent-lessons.md 로 surface된다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)
- **workflow**: contract test에 "anchor citation chain" 검증을 묶어 작성한다. 새 reference를 만들 때 SKILL.md/closeout/관련 reference에서 해당 파일을 cite 했는지 grep-기반 한 줄 테스트가 prose-only revert를 막는다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)
- **workflow**: SKILL.md 추가 분량이 명확할 때, _먼저_ 기존 텍스트의 압축 슬롯을 확보한 뒤 새 contract를 추가한다. budget(200) 직격 후 압축하는 패턴은 매번 검증 비용을 두 배로 만든다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-07-issue-108-109-closeout.md`
- `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`
