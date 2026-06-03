# Recent Retro Lessons

## Current Focus

- Goal run implementing the A4-lite contract that turns retro waste findings into **structural, destination-routed** issue proposals instead of incident-coupled ones (shared reference + retro/achieve/issue wiring + issue-adapter `harness_upstream` + presence-only `validate_proposal_fields.py` + tests). (source: `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`)
- Reviewed the active achieve goal that turned the boundary-bypass advisory probe into a no-increase ratchet, skillified the portable `quality` contract, and converted the first clean `inventory_*` boundary-bypass test in-process. (source: `charness-artifacts/retro/2026-06-03-testability-quality-ratchet-retro.md`)

## Repeat Traps

- `check_auto_trigger.py` is state-sensitive: once a helper commits and pushes the release, the current diff is empty and the trigger cannot reconstruct the just-finished slice. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)
- **goal_artifact_lib.py 길이 게이트 초과(366/360).** window 함수를 인라인으로 먼저 추가 → 닫기 리허설에서야 하드 한도 초과 발견 → 별도 모듈 `goal_metric_window_lib.py`로 추출 + 재노출 + 미러 재동기 + 재테스트. discipline 문서가 명시한 "큰 추가 전 `--headroom` 점검"을 생략해 1 사이클 낭비. (source: charness-artifacts/retro/2026-06-03-282-283-release-waste-retro.md) (source: `charness-artifacts/retro/2026-06-03-282-283-release-waste-retro.md`)
- Handoff edit cascade: editing `docs/handoff.md` broke `check-doc-links` (backticked file paths instead of markdown links) and `test_handoff_chunker_parse.py` (it pins the live Next-Session issue refs at `[184, 261]`, now stale because #261 is closed). That forced one extra full `run-quality` (~51s) plus investigation. Root cause: edited a coupled surface without checking its two known couplings first. (source: `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`)
- **handoff 편집 캐스케이드 — 반복 트랩 2회차.** `docs/handoff.md` 마감 편집이 세 검증을 연달아 깨뜨림: (a) MD004 — `+`로 시작한 연속 줄이 리스트 항목으로 파싱, (b) 인라인 코드 스팬 줄바꿈, (c) 70줄 상한 초과(73줄). 결과: push 1회 실패 + 수정-재검증 3사이클 + amend 1회. recent-lessons에 이미 적힌 "handoff edit cascade" 트랩의 재발. 청커 커플링은 사전 점검했으나 70줄 상한·마크다운 규칙은 점검하지 않음. (source: charness-artifacts/retro/2026-06-03-282-283-release-waste-retro.md) (source: `charness-artifacts/retro/2026-06-03-282-283-release-waste-retro.md`)

## Next-Time Checklist

- a `--report-all` (collect-all) mode for `validate_quality_artifact.py` and peers would surface every violation in one pass; 21 `validate_*.py` raise on the first error today vs 10 that already collect failures. Optional candidate, not committed here. (source: `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`)
- Add an explicit release-helper handoff field such as `retro_trigger_evaluation` that records `triggered`, `paths`, and whether a bounded session retro was written or intentionally skipped. (source: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`)
- applied: Declare the new skipped attention state for release-retro closeout so skipped trigger status cannot masquerade as a clean closeout proof. (source: `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`)
- applied: Encode portable boundary-bypass invariants as validator-enforced fields, not only reference prose. (source: `charness-artifacts/retro/2026-06-03-testability-quality-ratchet-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`
- `charness-artifacts/retro/2026-06-03-282-283-release-waste-retro.md`
- `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`
- `charness-artifacts/retro/2026-06-03-quality-283-waste-retro.md`
- `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`
- `charness-artifacts/retro/2026-06-03-testability-quality-ratchet-retro.md`
