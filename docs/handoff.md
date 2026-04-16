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
  `check-coverage` 15s, `run-evals` 5s, `specdown` 8s다.
- `run-quality.sh`는 이제 `specdown run -quiet -no-report`를 실행한다. 첫
  스펙은 `tool doctor specdown --json`, `charness task` envelope, 그리고
  root `doctor`의 primary `next_action` 출력 계약을 다루며, adapter는 아직
  만들지 않았다.
- `charness task`는 현재 작업 리포의 `.charness/tasks/*.json`에
  claim/submit/abort/status 상태를 남긴다. 이 리포에서는
  `.charness/tasks/`를 runtime state로 gitignore한다.
- 현재 로컬 runtime state에는 `sah-task-envelope` submitted task record와
  이번 세션의 `doctor-next-action` task record가 있다. 같은 workspace에서
  이어가면 `charness task status <task-id>`로 확인할 수 있다.
- Checked-in plugin export는 source 변경 뒤
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`로 맞춘다.
- GitHub 이슈 #25-#31은 `main`에 반영했고 모두 close했다. Retro 결론은
  producer-side gate만으로는 부족하고 consumer-side dogfood matrix가 필요하다는
  것이다.
- `docs/public-skill-dogfood.json`가 현재 reviewed consumer dogfood registry다.
  지금은 `announcement`, `create-cli`, `create-skill`, `debug`,
  `find-skills`, `gather`, `handoff`, `hitl`, `ideation`, `impl`,
  `init-repo`, `narrative`, `premortem`, `quality`, `release`, `retro`,
  `spec` 전체 public skill을 커버하고, `suggest-public-skill-dogfood.py`와
  `validate-public-skill-dogfood.py`가 scaffold drift를 잡는다.
- Packaging/plugin release surface는 `0.0.7`로 bump되어 `main`에 push됐다.

## Next Session

1. `git status --short`를 먼저 확인한다.
2. Dogfood 개선으로 이어가면 이제 registry 확장보다 reviewed case 강화가
   다음 move다. `create-cli`, `ideation`, `premortem`, `hitl` 같은
   HITL-heavy skill 중 하나를 골라 실제 consumer prompt replay, stronger
   acceptance evidence, 또는 tier 재검토 근거를 추가한다. 새 public skill이
   생기면 그때만 `suggest-public-skill-dogfood.py` scaffold를 다시 추가한다.
3. Release follow-up이 필요하면 `charness-artifacts/release/latest.md`와
   `current_release.py` 상태를 먼저 확인한다. `0.0.7` 태그/게시 릴리스는 아직 만들지 않았다.
4. sah/specdown lesson line을 이어간다면 다음 작은 CLI 후보는 task
   envelope와 doctor `next_action`을 실제 멀티에이전트 세션에서 dogfood한
   뒤, 필요한 경우 task list/status summary를 다듬는 것이다. 스펙다운은
   반복 setup/JSON 추출이 두세 번 생기기 전에는 adapter를 만들지 않는다.
5. 이 handoff가 커밋된 상태라면 다음 품질 작업은 85% floor에 가까운
   `upstream_release_lib.py`, `control_plane_lib.py`, `install_tools.py`에서
   남은 branch를 리팩터링하거나 죽은 코드를 지우는 것이다. 테스트 추가보다
   생산 코드 축소를 먼저 본다.
6. source가 checked-in plugin export에 들어가는 파일이면, focused
   managed-checkout 테스트 전에 export sync를 먼저 실행한다.

## Discuss

- stale artifact를 언제 삭제/아카이브할지, 아니면 `superseded_by`
  frontmatter만 도입할지 아직 정책으로 잠그지 않았다.
- singleton 성격이 강한 스킬도 dated record를 항상 남길지, 일부는 current
  pointer만 둘지에 대한 UX 판단은 dogfood 후 다시 볼 수 있다.

## References

- [AGENTS.md](../AGENTS.md)
- [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
- [public-skill-dogfood.md](public-skill-dogfood.md)
