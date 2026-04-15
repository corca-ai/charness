# charness Handoff

## Workflow Trigger

- 다음 세션이 artifact output 정책, skill adapter contract, plugin export, 또는
  checked-in artifact 경로를 이어받는다면 이 handoff부터 읽는다.
- 반복 실수 방지는
  [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)를
  함께 읽는다.
- 기본 public output root는 `charness-artifacts/<skill>/`이고 hidden runtime
  state는 `.charness/<skill>/`이다.
- 일반 스킬의 current pointer는 `latest.md`, durable record는
  `YYYY-MM-DD-<slug>.md` 규칙이다. `handoff`는 rolling canonical artifact라
  기본값이 `docs/handoff.md`다.

## Current State

- 2026-04-15 두 번째 `quality` dogfood pass가
  [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)를
  갱신했다. `upstream_release_lib.py` focused coverage follow-up은 완료되어
  coverage가 `48.8%`에서 `87.6%`로 올랐고, `check-coverage.py`는
  이제 `60.0%` aggregate floor와 `80.0%` per-file floor를 모두 enforce한다.
- 2026-04-15 후속 품질 slice에서 `install_tools.py`/`update_tools.py`의
  lifecycle helper 중복을 `control_plane_lifecycle_lib.py`로 줄였고,
  `check-test-production-ratio`를 추가했다. `sync_support.py`의 반복
  selection/status 출력도 같은 helper로 줄여 coverage가 `80.0%`에서
  `86.5%`로 올라갔다. `install_tools.py`는 one-use wrapper를 접어
  `81.5%`에서 `84.2%`로 올라갔다. 현재 ratio는 `0.53`
  (`9240/17443` Python lines), 기본 상한은 `1.00`이다.
- `inventory-quality-handoff`가 `./scripts/run-quality.sh`에 추가됐다.
  `NON_AUTOMATABLE` 추천 항목에 HITL handoff 필드가 없으면 advisory로
  보고하지만 아직 hard gate는 아니다.
- `./scripts/run-quality.sh --review` 재실행은 `36 passed, 0 failed`,
  total `41.9s`로 통과했다. 새 `check-test-production-ratio`와 per-file
  coverage floor가 standing quality path에 포함됐다.
- 이번 pass에서 `recent-lessons.md`가 최신 retro digest로 갱신되는 계약과
  충돌하던 오래된 `plugin export` 테스트 앵커를 구조 검증으로 바꿨다.
  상세 원인은
  [charness-artifacts/debug/2026-04-15-retro-memory-test-anchor.md](../charness-artifacts/debug/2026-04-15-retro-memory-test-anchor.md)에
  남겼다.
- `skill-outputs/`는 repo-facing public output root에서 제거됐고,
  public artifacts는 `charness-artifacts/`로 정리됐다.
- `handoff` adapter fallback은 `docs/handoff.md`를 가리킨다. repo-local
  `.agents/handoff-adapter.yaml`도 `output_dir: docs`라 fallback과 일치한다.
- adapter resolvers는 일반 스킬에 대해
  `artifact_path=charness-artifacts/<skill>/latest.md`와
  `record_artifact_pattern=charness-artifacts/<skill>/YYYY-MM-DD-<slug>.md`를
  함께 제공한다.
- `scripts/artifact_naming_lib.py`와 `scripts/resolve_artifact_path.py`가
  slug/date 기반 record path 계산을 담당한다.
- 기존 checked-in artifact 중 current pointer 성격인 quality/HITL은
  `latest.md`로 이동했고, debug records는 `debug-` 중복 접두사를 제거했다.
- checked-in plugin export는 `python3 scripts/sync_root_plugin_manifests.py
  --repo-root .`로 재생성됐다.

## Next Session

1. 먼저 `git status --short`를 확인한다. 이 handoff가 커밋된 상태라면 새 첫
   품질 작업은 `control_plane_lib.py`를 리팩터링하거나 죽은 코드를 지우는
   것이다. 현재 가장 약한 tracked file이다.
2. artifact naming을 더 밀면 stale artifact 처리 정책을 별도 결정한다.
   이번 slice는 자동 삭제 정책을 추가하지 않았고, 기존 기록을 보존하는 방향만
   적용했다.
3. 새 skill 또는 adapter를 만들 때는 `latest.md` current pointer와
   `YYYY-MM-DD-<slug>.md` record pattern을 같이 노출한다. rolling canonical
   artifact가 더 맞는 경우만 `handoff.md` 같은 고정 이름을 예외로 둔다.
4. release/dogfood로 이어가면 checked-in plugin export와 managed checkout이
   같은 계약을 쓰는지 `validate-packaging.py`, `run-slice-closeout.py`, 실제
   `charness update` 경로로 확인한다.

## Discuss

- stale artifact를 언제 삭제/아카이브할지, 아니면 `superseded_by` frontmatter만
  도입할지 아직 정책으로 잠그지 않았다.
- singleton 성격이 강한 스킬도 dated record를 항상 남길지, 일부는 current
  pointer만 둘지에 대한 UX 판단은 dogfood 후 다시 볼 수 있다.

## References

- [AGENTS.md](../AGENTS.md)
- [skills/public/create-skill/references/adapter-pattern.md](../skills/public/create-skill/references/adapter-pattern.md)
- [scripts/artifact_naming_lib.py](../scripts/artifact_naming_lib.py)
- [scripts/resolve_artifact_path.py](../scripts/resolve_artifact_path.py)
- [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
- [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
