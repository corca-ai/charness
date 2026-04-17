# charness Handoff

## Workflow Trigger

- 다음 세션이 artifact output policy, skill adapter contract, plugin export, 또는 checked-in artifact 경로를 이어받는다면 이 handoff부터 읽는다.
- 반복 실수 방지는 [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)를 함께 읽는다.

## Current State

- Public artifacts는 `charness-artifacts/<skill>/`, hidden runtime state는 `.charness/<skill>/`를 쓴다. 일반 current pointer는 `latest.md`, durable record는 `YYYY-MM-DD-<slug>.md` 규칙이고 `docs/handoff.md`만 rolling canonical 예외다.
- 현재 quality gate는 aggregate `60.0%` + per-file `85.0%` coverage floor, test/source ratio 상한 `1.00`, recent-median runtime budget(`pytest` 40s, `check-secrets` 5s, `check-coverage` 15s, `run-evals` 5s, `specdown` 8s)을 enforce한다.
- 가장 최근 review proof 기준 control-plane coverage는 `98.0%` (`1196/1221`), test/source ratio는 `0.54` (`11279/20721`), standing pytest는 `321 passed`, eval은 `19` scenario pass, review gate는 `38 passed, 0 failed, 50.3s`다.
- `run-quality.sh`는 `specdown run -quiet -no-report`를 포함하고, `.githooks/pre-push`는 export sync 뒤 canonical quality gate를 강제한다.
- `charness task`는 작업 리포의 `.charness/tasks/*.json`에 claim/submit/abort/status를 남긴다. 이 리포의 runtime state에는 `sah-task-envelope`와 `doctor-next-action` record가 있어 `charness task status <task-id>`로 이어받을 수 있다.
- Checked-in plugin export는 source 변경 뒤 `python3 scripts/sync_root_plugin_manifests.py --repo-root .`로 맞춘다.
- `docs/public-skill-dogfood.json`는 현재 17개 public skill 전체를 커버하는 reviewed consumer dogfood registry다.
- Packaging/plugin release surface는 이제 `0.2.0` 기준이고, 태그/게시 release는 아직 만들지 않았다.
- `#33`/`#34` 방향의 public spec boundary 정리는 반영됐다. `spec`은 public executable contract vs implementation guard를 명시하고, `quality`는 proof layering inventory plus actionable `move_down` / `delete_or_merge` / `keep_if_integration_value` recommendation payload를 갖는다.
- `quality` public skill은 이번 slice에서 structure-first routing을 더 명시했다. 길이/중복/pressure signal은 기본적으로 concept-review advisory로 보고, explicit low-noise invariant와 clear structural response가 있을 때만 `AUTO_CANDIDATE`/`AUTO_EXISTING`로 올린다. 이 caution은 coverage floor나 runtime budget 같은 standing threshold gate까지 일반화하지 않는다.
- 2026-04-17 quality review 기준 남은 advisory pressure는 `AGENTS.md`/`README.md`/`UNINSTALL.md` entrypoint ergonomics, `init-repo`/`retro`/`spec`의 mode-pressure wording, 그리고 `quality` SKILL core의 `long_core`다.
- `#35`의 첫 구현 뒤 hardening도 들어갔다. `render_markdown_preview.py`는 unsupported `backend`를 upfront reject하고, manifest에 `backend_version`, `git_head`, per-file `source_sha256`를 남긴다. repo-local scope는 `.agents/markdown-preview.yaml` 같은 config search path로 열어뒀고, 현재 이 repo에는 scaffolded config가 checked in 되어 있다. preview output은 `.artifacts/markdown-preview/` 아래 machine-local runtime artifact로 본다. 2026-04-17 현재 `glow`는 `charness tool install --repo-root . glow`로 로컬 설치 완료됐고, preview helper는 `backend: glow` rendered artifact를 생성한다.
- `premortem` public skill contract은 이제 canonical subagent path를 요구한다. host가 subagent를 못 주면 같은-agent 로컬 패스로 약화하지 말고 canonical path unavailable로 stop해야 한다.
- `quality`의 fresh-eye premortem reference도 같은 방향으로 맞췄다. explicit subagent allowance가 없으면 same-agent local fallback을 equivalent로 취급하지 않는다.

## Next Session

1. `git status --short`를 먼저 확인한다.
2. public-spec executable proof 약점은 이번 slice에서 정리됐다. `inventory_public_spec_quality.py`는 실제 `run:shell` fence를 읽고, `specs/index.spec.md`/`specs/tool-doctor.spec.md`는 direct CLI proof로 바뀌어 현재 flagged spec이 없다.
3. `0.2.0` release slice는 additive `glow` install/runtime surface와 related release/test hardening을 포함한다. 태그/게시 release는 아직 없으니, 다음 세션이 release를 이어받으면 published tag를 만들지 말지부터 결정하고 `python3 skills/public/release/scripts/current_release.py --repo-root .`로 checked-in version surface부터 확인한다.
4. `markdown-preview`는 이제 이 repo에서 `glow` installed/ready 상태다. 다음 slice 우선순위는 `narrative`/`announcement`/`quality` 중 어떤 workflow가 이 helper를 기본 호출할지 결정하고, `docs:preview`류 command surface가 실제 가치가 있는지 판단하는 것이다.
5. Agent Harness Guide adaptation을 이어가면 [charness-artifacts/spec/agent-harness-guide-adaptation.md](../charness-artifacts/spec/agent-harness-guide-adaptation.md)를 읽고 `Slice 1`부터 시작한다. 첫 범위는 `docs/harness-composition.md`, `docs/artifact-policy.md`, 최소 handoff cross-link다.
6. Dogfood 개선은 registry 확장보다 reviewed case 강화가 다음 move다. `hitl` 또는 `ideation`처럼 policy-heavy한 case 하나를 골라 실제 consumer prompt replay와 stronger acceptance evidence를 추가한다.
7. sah/specdown lesson line을 이어가면 task envelope와 doctor `next_action`을 실제 멀티에이전트 세션에서 dogfood한 뒤 필요하면 task list/status summary만 다듬는다. 반복 setup/JSON 추출이 두세 번 생기기 전에는 specdown adapter를 만들지 않는다.
8. source가 checked-in plugin export에 들어가는 파일이면 focused managed-checkout 테스트 전에 export sync를 먼저 실행한다. 이번 slice에서도 `plugins/charness/README.md` drift가 packaging/managed-install pytest를 바로 깨뜨렸으니, root README 계열 변경 뒤에는 `python3 scripts/sync_root_plugin_manifests.py --repo-root .`를 먼저 습관화한다.

## Discuss

- stale artifact를 언제 삭제/아카이브할지, 아니면 `superseded_by` frontmatter만 도입할지 아직 정책으로 잠그지 않았다.
- singleton 성격이 강한 스킬도 dated record를 항상 남길지, 일부는 current pointer만 둘지는 dogfood 후 다시 본다.

## References

- [AGENTS.md](../AGENTS.md)
- [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
- [public-skill-dogfood.md](public-skill-dogfood.md)
