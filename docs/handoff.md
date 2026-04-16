# charness Handoff

## Workflow Trigger

- 다음 세션이 artifact output policy, skill adapter contract, plugin export, 또는 checked-in artifact 경로를 이어받는다면 이 handoff부터 읽는다.
- 반복 실수 방지는 [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)를 함께 읽는다.

## Current State

- Public artifacts는 `charness-artifacts/<skill>/`, hidden runtime state는 `.charness/<skill>/`를 쓴다. 일반 current pointer는 `latest.md`, durable record는 `YYYY-MM-DD-<slug>.md` 규칙이고 `docs/handoff.md`만 rolling canonical 예외다.
- 현재 quality gate는 aggregate `60.0%` + per-file `85.0%` coverage floor, test/source ratio 상한 `1.00`, recent-median runtime budget(`pytest` 40s, `check-secrets` 5s, `check-coverage` 15s, `run-evals` 5s, `specdown` 8s)을 enforce한다.
- 가장 최근 review proof 기준 control-plane coverage는 `90.6%` (`1152/1272`), test/source ratio는 `0.52` (`10253/19801`), standing pytest는 `287 passed`, eval은 `19` scenario pass다.
- `run-quality.sh`는 `specdown run -quiet -no-report`를 포함하고, `.githooks/pre-push`는 export sync 뒤 canonical quality gate를 강제한다.
- `charness task`는 작업 리포의 `.charness/tasks/*.json`에 claim/submit/abort/status를 남긴다. 이 리포의 runtime state에는 `sah-task-envelope`와 `doctor-next-action` record가 있어 `charness task status <task-id>`로 이어받을 수 있다.
- Checked-in plugin export는 source 변경 뒤 `python3 scripts/sync_root_plugin_manifests.py --repo-root .`로 맞춘다.
- `docs/public-skill-dogfood.json`는 현재 17개 public skill 전체를 커버하는 reviewed consumer dogfood registry다.
- Packaging/plugin release surface `0.0.7`은 이미 `main`에 push됐고, 태그/게시 release는 아직 만들지 않았다.

## Next Session

1. `git status --short`를 먼저 확인한다.
2. 품질 cleanup 다음 우선순위는 warn band coverage seam이다. `support_sync_lib.py`, `upstream_release_lib.py`, `control_plane_lib.py`, `install_tools.py`에서 테스트 추가보다 생산 코드 축소와 branch 정리를 먼저 본다.
3. entrypoint/skill ergonomics advisory를 실제로 줄일지 판단하려면 `README.md`, `docs/operator-acceptance.md`, `skills/public/create-skill/SKILL.md`, `skills/public/quality/SKILL.md`, `skills/public/spec/SKILL.md`부터 본다. 지금은 inventory only이고 hard gate는 아니다.
4. Agent Harness Guide adaptation을 이어가면 [charness-artifacts/spec/agent-harness-guide-adaptation.md](../charness-artifacts/spec/agent-harness-guide-adaptation.md)를 읽고 `Slice 1`부터 시작한다. 첫 범위는 `docs/harness-composition.md`, `docs/artifact-policy.md`, 최소 handoff cross-link다.
5. Dogfood 개선은 registry 확장보다 reviewed case 강화가 다음 move다. `hitl` 또는 `ideation`처럼 policy-heavy한 case 하나를 골라 실제 consumer prompt replay와 stronger acceptance evidence를 추가한다.
6. sah/specdown lesson line을 이어가면 task envelope와 doctor `next_action`을 실제 멀티에이전트 세션에서 dogfood한 뒤 필요하면 task list/status summary만 다듬는다. 반복 setup/JSON 추출이 두세 번 생기기 전에는 specdown adapter를 만들지 않는다.
7. source가 checked-in plugin export에 들어가는 파일이면 focused managed-checkout 테스트 전에 export sync를 먼저 실행한다.

## Discuss

- stale artifact를 언제 삭제/아카이브할지, 아니면 `superseded_by` frontmatter만 도입할지 아직 정책으로 잠그지 않았다.
- singleton 성격이 강한 스킬도 dated record를 항상 남길지, 일부는 current pointer만 둘지는 dogfood 후 다시 본다.

## References

- [AGENTS.md](../AGENTS.md)
- [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
- [public-skill-dogfood.md](public-skill-dogfood.md)
