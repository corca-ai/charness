# charness Handoff

## Workflow Trigger

- 다음 세션이 artifact output 정책, skill adapter contract, plugin export, 또는
  checked-in artifact 경로를 이어받는다면 이 handoff부터 읽는다.
- 반복 실수 방지는
  [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)를
  함께 읽는다.

## Current State

- Public artifacts는 `charness-artifacts/<skill>/`에 둔다. Hidden runtime
  state는 `.charness/<skill>/`에 둔다.
- 일반 스킬 current pointer는 `latest.md`, durable record는
  `YYYY-MM-DD-<slug>.md` 규칙이다. Rolling canonical artifact가 더 맞는
  경우만 `docs/handoff.md` 같은 고정 이름을 예외로 둔다.
- `check-coverage.py`는 `60.0%` aggregate floor와 `80.0%` per-file floor를
  모두 enforce한다. 현재 control-plane coverage는 `88.1%` (`1125/1277`)다.
- `check-test-production-ratio`는 Python test/source ratio 상한 `1.00`을
  enforce한다. 현재 ratio는 `0.53` (`9240/17404`)다.
- `./scripts/run-quality.sh --review`는 최근 full pass에서
  `36 passed, 0 failed`, total `44.2s`로 통과했다. 이후 pytest runtime
  spike가 한 번 있었지만 `pytest,check-runtime-budget` 재측정은 통과했고
  최신 pytest 샘플은 `27.4s / 40.0s`다.
- Checked-in plugin export는 source 변경 뒤
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`로 맞춘다.

## Next Session

1. `git status --short`를 먼저 확인한다.
2. 이 handoff가 커밋된 상태라면 다음 품질 작업은 `install_tools.py` 또는
   `support_sync_lib.py`에서 남은 near-floor branch를 리팩터링하거나 죽은
   코드를 지우는 것이다. 테스트 추가보다 생산 코드 축소를 먼저 본다.
3. source가 checked-in plugin export에 들어가는 파일이면, focused
   managed-checkout 테스트 전에 export sync를 먼저 실행한다.
4. release/dogfood로 이어가면 `validate-packaging.py`,
   `run-slice-closeout.py`, 실제 `charness update` 경로로 managed checkout과
   checked-in plugin export 계약이 같은지 확인한다.

## Discuss

- stale artifact를 언제 삭제/아카이브할지, 아니면 `superseded_by`
  frontmatter만 도입할지 아직 정책으로 잠그지 않았다.
- singleton 성격이 강한 스킬도 dated record를 항상 남길지, 일부는 current
  pointer만 둘지에 대한 UX 판단은 dogfood 후 다시 볼 수 있다.
- `handoff` 스킬은 현재 “diary를 남기지 말라”고 말하지만 size gate가
  관대하다. 다음 개선 때는 “다음 첫 행동을 바꾸는 정보만 handoff에 남기고
  세부 이력은 quality/retro/debug로 spill”하도록 더 강하게 유도하는 편이
  낫다.

## References

- [AGENTS.md](../AGENTS.md)
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
- [charness-artifacts/retro/2026-04-15-control-plane-lib-cleanup.md](../charness-artifacts/retro/2026-04-15-control-plane-lib-cleanup.md)
- [charness-artifacts/debug/2026-04-15-retro-memory-test-anchor.md](../charness-artifacts/debug/2026-04-15-retro-memory-test-anchor.md)
