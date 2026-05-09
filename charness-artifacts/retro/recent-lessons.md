# Recent Retro Lessons

## Current Focus

- charness 플러그인의 `debug` skill (RCA/falsifiable hypothesis substrate)와 `issue` skill (close-ledger lifecycle target) 사이의 silent overlap 분리 spec slice. (source: `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-spec.md`)
- 이번 세션은 [#122](https://github.com/corca-ai/charness/issues/122)·[#123](https://github.com/corca-ai/charness/issues/123)·[#124](https://github.com/corca-ai/charness/issues/124)을 묶어 한 번, 이어 [#125](https://github.com/corca-ai/charness/issues/125)·[#126](https://github.com/corca-ai/charness/issues/126)·[#127](https://github.com/corca-ai/charness/issues/127)을 묶어 한 번 — 총 두 슬라이스로 닫았다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)

## Repeat Traps

- **Acceptance Checks 미분리**. 첫 draft가 spec-slice (본 파일 land + critique fold) 와 impl-slice (validators + grep + dogfood)를 한 block에 섞어둠. 본 슬라이스가 spec 단독인데 validator가 acceptance에 listed → category error. Hidden Sequencing critique A3.5 catch. (source: `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-spec.md`)
- **Bundle Anyway 항목을 사후에야 발견.** premortem이 "closeout-discipline.md를 SKILL.md 세 anchor에서 cite 했는지 검증하는 cheap test 추가"를 짚어줬는데, 이는 첫 contract test 작성 시 같이 들어갔어야 하는 패턴이었다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)
- **`MAX_SKILL_MD_LINES=200` 직격을 두 번 맞았다.** 1차 슬라이스에서 HITL SKILL.md(208줄) → impl SKILL.md(202줄) → issue SKILL.md(216줄) 순으로 budget을 넘겼고, 2차 슬라이스에서도 issue SKILL.md(214줄)가 또 넘었다. 매번 검증→압축→ 재검증 사이클을 돌았다. 추가 분량을 알고 있을 때 _먼저_ 기존 텍스트를 압축해 슬롯을 확보한 뒤 새 contract를 추가하는 순서였다면 한 번에 끝났다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)
- **Pre-commit `check-doc-links` missing-artifact fail**. handoff item 1을 갱신할 때 미존재 future-path `skills/public/debug/references/five-whys- causal-chain.md`를 backtick 안에 인용 — hook이 "backticked file reference ... use markdown links so renames do not rot"으로 차단. 평문 표기 (디렉토리 backtick + 파일명 평문)로 풀고 재 commit. 미리 mental model이 없어 1회 retry 비용. (source: `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-spec.md`)

## Next-Time Checklist

- **capability**: pre-commit `check-doc-links` hook의 missing-artifact 메시지 enhancement — 현재는 "use markdown links so renames do not rot"이지만 미존재 path 케이스는 "use plain text for not-yet-created paths" 같은 ramification이 더 정확. 단일 패턴, capability 변경은 미루고 다음 회 같은 트랩 반복 시 짓는다 (recent-lessons "한 번 패턴이라 capability 변경은 미루고 다음 회 같은 트랩이 반복되면 그때 짓는다" 휴리스틱 동형). (source: `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-spec.md`)
- **capability**: SKILL.md 압축-친화 helper 후보가 떠올랐다 — `inventory_skill_ ergonomics.py`나 `validate_skills.py` 옆에 "MAX_SKILL_MD_LINES까지 N줄 남았다" 를 보여주는 dry-run 헬퍼가 있다면 budget 초과 전에 압축 슬롯 확보가 자연스 러워진다. 다만 한 번 패턴이라 capability 변경은 미루고 다음 회 같은 트랩이 반복되면 그때 짓는다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)
- **memory**: spec-slice ↔ impl-slice acceptance 분리가 본 슬라이스에서 처음 명시 적용. 다음 spec slice는 이 구분을 spec 첫 draft에 직접 fold — spec section이 "Spec-slice acceptance" 와 "Impl-slice acceptance" 두 sub- block으로 나뉘는 형식. recent-lessons.md에 surface. (source: `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-spec.md`)
- **memory**: 본 retro가 lesson durable persistence. 다음 세션은 recent-lessons.md 로 surface된다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-spec.md`
- `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`
