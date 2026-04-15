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
- `check-coverage.py`는 `60.0%` aggregate floor와 `85.0%` per-file floor를
  모두 enforce한다. 현재 control-plane coverage는 `89.9%` (`1127/1254`)다.
- `check-test-production-ratio`는 Python test/source ratio 상한 `1.00`을
  enforce한다. 현재 ratio는 `0.54` (`9345/17425`)다.
- Runtime budget gate는 latest 단일 샘플이 아니라 recent median drift를
  fail 기준으로 쓴다. 현재 예산은 `pytest` 40s, `check-secrets` 5s,
  `check-coverage` 15s, `run-evals` 5s, `specdown` 5s다.
- `run-quality.sh`는 이제 `specdown run -quiet -no-report`를 실행한다. 첫
  스펙은 `tool doctor specdown --json`의 operator-facing e2e 계약만
  다루며, adapter는 아직 만들지 않았다.
- Checked-in plugin export는 source 변경 뒤
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`로 맞춘다.

## Next Session

1. `git status --short`를 먼저 확인한다.
2. sah/specdown lesson line을 이어간다면 specdown 스펙을 넓히기 전에
   작은 operator behavior를 하나 더 고른다. 후보는 `sah-cli`에서 배운
   claim/submit/abort agent-task envelope 또는 doctor next-action UX다.
   반복 setup/JSON 추출이 두세 번 생기기 전에는 specdown adapter를 만들지
   않는다.
3. 이 handoff가 커밋된 상태라면 다음 품질 작업은 85% floor에 가까운
   `upstream_release_lib.py`, `control_plane_lib.py`, `install_tools.py`에서
   남은 branch를 리팩터링하거나 죽은 코드를 지우는 것이다. 테스트 추가보다
   생산 코드 축소를 먼저 본다.
4. source가 checked-in plugin export에 들어가는 파일이면, focused
   managed-checkout 테스트 전에 export sync를 먼저 실행한다.
5. release/dogfood로 이어가면
   [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md)에서
   clean temp-home proof와 남은 real-host proof를 먼저 확인한다.

## Discuss

- stale artifact를 언제 삭제/아카이브할지, 아니면 `superseded_by`
  frontmatter만 도입할지 아직 정책으로 잠그지 않았다.
- singleton 성격이 강한 스킬도 dated record를 항상 남길지, 일부는 current
  pointer만 둘지에 대한 UX 판단은 dogfood 후 다시 볼 수 있다.

## References

- [AGENTS.md](../AGENTS.md)
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md)
- [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
- [charness-artifacts/retro/2026-04-15-coverage-floor-runtime-budget.md](../charness-artifacts/retro/2026-04-15-coverage-floor-runtime-budget.md)
- [charness-artifacts/debug/2026-04-15-retro-memory-test-anchor.md](../charness-artifacts/debug/2026-04-15-retro-memory-test-anchor.md)
