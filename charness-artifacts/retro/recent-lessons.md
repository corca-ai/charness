# Recent Retro Lessons

## Current Focus

- Issue 146/148 work found the immediate worktree readiness and cleanup gaps, but the first sibling search stayed too close to the `worktree` noun and nearby CLI surfaces. (source: `charness-artifacts/retro/2026-05-12-worktree-search-generalization.md`)
- The reviewed miss is the realization during issue #146/#148 Cautilus proof work that Charness does not currently have a repo-local `skills/support` Cautilus support skill, even though the Cautilus integration manifest records an upstream bundled skill source. (source: `charness-artifacts/retro/2026-05-12-cautilus-support-surface-miss.md`)

## Repeat Traps

- **Acceptance Checks 미분리**. 첫 draft가 spec-slice (본 파일 land + critique fold) 와 impl-slice (validators + grep + dogfood)를 한 block에 섞어둠. 본 슬라이스가 spec 단독인데 validator가 acceptance에 listed → category error. Hidden Sequencing critique A3.5 catch. (source: `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-spec.md`)
- **Bootstrap line-wrap broke a contractual literal phrase**. First pass rewrapped "It must not use the current session's last created issue" across a newline; `test_issue_skill_records_github_sot_for_omitted_selector` and `check_skill_contracts.py` both use literal substring assertions, so the broken wrap surfaced as a fail, not a silent drift. Fixed by restructuring the bootstrap merge so both contractual phrases ("With no selector, `select` queries the newest open GitHub issue", "It must not use the current session's last created issue") stay continuous within a single line. ~2 retry cycles. (source: `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-impl.md`)
- **Bundle Anyway 항목을 사후에야 발견.** premortem이 "closeout-discipline.md를 SKILL.md 세 anchor에서 cite 했는지 검증하는 cheap test 추가"를 짚어줬는데, 이는 첫 contract test 작성 시 같이 들어갔어야 하는 패턴이었다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)
- **`MAX_SKILL_MD_LINES=200` 직격을 두 번 맞았다.** 1차 슬라이스에서 HITL SKILL.md(208줄) → impl SKILL.md(202줄) → issue SKILL.md(216줄) 순으로 budget을 넘겼고, 2차 슬라이스에서도 issue SKILL.md(214줄)가 또 넘었다. 매번 검증→압축→ 재검증 사이클을 돌았다. 추가 분량을 알고 있을 때 _먼저_ 기존 텍스트를 압축해 슬롯을 확보한 뒤 새 contract를 추가하는 순서였다면 한 번에 끝났다. (source: `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`)

## Next-Time Checklist

- before closing issue-class work, run one structural sibling pass in addition to keyword sibling search. (source: `charness-artifacts/retro/2026-05-12-worktree-search-generalization.md`)
- consider a lightweight reviewer checklist for issue resolution that records the structural pattern searched, not just matched files. (source: `charness-artifacts/retro/2026-05-12-worktree-search-generalization.md`)
- Keep this as a concrete lesson in retro artifacts so future integration work distinguishes binary, upstream support source, synced support skill, and installed plugin cache. (source: `charness-artifacts/retro/2026-05-12-cautilus-support-surface-miss.md`)
- phrase the pass as mental-model prompts: missing lifecycle endpoint, local check not included in aggregate, mutation skill without readiness probe, renderer hiding failing details, current-working-directory used as authority for safety checks. (source: `charness-artifacts/retro/2026-05-12-worktree-search-generalization.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-impl.md`
- `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-spec.md`
- `charness-artifacts/retro/2026-05-09-issue-122-127-resolve.md`
- `charness-artifacts/retro/2026-05-12-cautilus-support-surface-miss.md`
- `charness-artifacts/retro/2026-05-12-worktree-search-generalization.md`
