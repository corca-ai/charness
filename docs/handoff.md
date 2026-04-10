# charness Handoff

## Workflow Trigger

- 다음 세션에서 이 문서를 멘션하면 `impl`로 이어서, 사용자가 `~/cautilus` 작업 완료를 알리기 전이면 pre-`cautilus` self-work를 계속하고, 완료를 알린 뒤에는 evaluator integration Session을 시작한다.
- pre-`cautilus` self-work를 이어갈 때는 [master-plan.md](/home/ubuntu/charness/docs/master-plan.md), [docs/control-plane.md](/home/ubuntu/charness/docs/control-plane.md), [public-skill-validation.md](/home/ubuntu/charness/docs/public-skill-validation.md), [docs/support-skill-policy.md](/home/ubuntu/charness/docs/support-skill-policy.md)를 먼저 읽고 support/control-plane/validation 빈칸을 메우는 쪽을 host packaging보다 우선한다.
- `cautilus` integration을 시작할 때는 [master-plan.md](/home/ubuntu/charness/docs/master-plan.md), [docs/control-plane.md](/home/ubuntu/charness/docs/control-plane.md), [public-skill-validation.md](/home/ubuntu/charness/docs/public-skill-validation.md), [integrations/tools/agent-browser.json](/home/ubuntu/charness/integrations/tools/agent-browser.json), [integrations/tools/specdown.json](/home/ubuntu/charness/integrations/tools/specdown.json), [integrations/tools/crill.json](/home/ubuntu/charness/integrations/tools/crill.json), [skills/public/quality/SKILL.md](/home/ubuntu/charness/skills/public/quality/SKILL.md), [docs/support-skill-policy.md](/home/ubuntu/charness/docs/support-skill-policy.md)를 다시 읽고 `cautilus` contract와 `charness` validation contract를 연결한다.

## Current State

- `charness`는 Ceal과 분리된 portable Corca harness product로 정의됐다.
- public skill / support skill / profile / integration 경계가 문서로 고정됐다.
- `quality`는 public skill 하나로 두고, `hitl`은 collaboration profile에 두며, `ideation`이 `interview`를 흡수하고, `retro`는 mode로 확장한다는 결정이 반영됐다.
- external binary는 `charness`가 vendor하지 않고 integration manifest와 sync/update/doctor flow로 다룬다는 정책이 고정됐다.
- Session 2 산출물로 [manifest.schema.json](/home/ubuntu/charness/integrations/tools/manifest.schema.json), [profile.schema.json](/home/ubuntu/charness/profiles/profile.schema.json), [control-plane.md](/home/ubuntu/charness/docs/control-plane.md)가 추가됐다.
- Session 3 산출물로 [skills/public/create-skill/SKILL.md](/home/ubuntu/charness/skills/public/create-skill/SKILL.md)와 관련 references가 추가돼 canonical portable authoring contract가 생겼다.
- 첫 profile instance로 [constitutional.json](/home/ubuntu/charness/profiles/constitutional.json)이 추가됐고, sample preset convention으로 [portable-defaults.md](/home/ubuntu/charness/presets/portable-defaults.md)가 생겼다.
- Session 4 초안으로 [skills/public/retro/SKILL.md](/home/ubuntu/charness/skills/public/retro/SKILL.md)와 adapter/reference/script 세트가 추가됐다.
- `retro`는 `session`/`weekly` mode를 하나의 public skill 안에서 처리하고, adapter가 없을 때 `session`은 soft fallback, `weekly`는 adapter scaffold를 우선하는 방향으로 설계됐다.
- `retro`의 핵심 가치는 self-growing/healing으로 잡았고, `Next Improvements`를 `workflow` / `capability` / `memory`로 나누는 방향이 반영됐다.
- Session 5 초안으로 [skills/public/ideation/SKILL.md](/home/ubuntu/charness/skills/public/ideation/SKILL.md)와 관련 references가 추가됐다.
- `ideation`은 `interview`를 흡수하고, product/system/workflow concept shaping에 맞춰 problem lens + entity/stage lens를 함께 쓰되 `spec`으로 넘어가기 전 discovery-to-concept 단계에 머무르도록 설계됐다.
- `ideation`은 living concept model, truth/edge, world modeling, and agent/human lenses 중심으로 재구성됐다.
- Session 6 초안으로 [skills/public/spec/SKILL.md](/home/ubuntu/charness/skills/public/spec/SKILL.md)와 관련 references가 추가됐다.
- `spec`은 `ideation` 산출물을 그대로 이어받아 현재 구현 계약을 관리하는 living contract skill로 재설계됐다.
- `spec`은 이제 explicit mode menu 대신 lighter contract-shaping heuristic을 따르며, `Fixed Decisions` / `Probe Questions` / `Deferred Decisions`로 현재 slice의 불확실성을 관리한다.
- `spec`은 success criteria를 acceptance checks와 직접 연결하고, 구현 중 새 사실이 나오면 canonical artifact를 갱신하도록 설계됐다.
- Session 7 산출물로 [skills/public/impl/SKILL.md](/home/ubuntu/charness/skills/public/impl/SKILL.md), [skills/public/debug/SKILL.md](/home/ubuntu/charness/skills/public/debug/SKILL.md), [skills/public/gather/SKILL.md](/home/ubuntu/charness/skills/public/gather/SKILL.md), [skills/public/handoff/SKILL.md](/home/ubuntu/charness/skills/public/handoff/SKILL.md)와 관련 references가 추가됐다.
- `impl`은 living contract를 소비하되 별도 `spec` 세션이 없어도 inline current-slice contract를 부트스트랩할 수 있는 execution skill로 조정되고 있다.
- `debug`, `gather`, `handoff`는 durable artifact 기본 위치를 `skill-outputs/<skill-name>/` 아래 정해진 파일로 두고, adapter `output_dir` override와 helper script bootstrap까지 갖추는 방향으로 보강되고 있다.
- Session 8 초안으로 [skills/public/quality/SKILL.md](/home/ubuntu/charness/skills/public/quality/SKILL.md), 관련 references, adapter helper scripts, 그리고 [typescript-quality.md](/home/ubuntu/charness/presets/typescript-quality.md) / [python-quality.md](/home/ubuntu/charness/presets/python-quality.md) sample preset이 추가됐다.
- `quality`는 `concept-review`, `test-improvement`, security posture review를 하나의 public proposal skill로 묶고, 기본 artifact를 `skill-outputs/quality/quality.md`에 두며 adapter `output_dir` override를 허용한다.
- Session 9 dogfood pass로 [quality.md](/home/ubuntu/charness/skill-outputs/quality/quality.md)가 추가됐고, repo-specific self-validation 초안으로 `scripts/validate-skills.py`, `scripts/validate-profiles.py`, `scripts/validate-adapters.py`, `scripts/check-doc-links.py`가 생겼다.
- Session 9에서 skill frontmatter description은 YAML-safe quoted string으로 통일됐고, `constitutional` profile에서 아직 없는 `find-skills` bundle reference를 제거했다.
- Session 9에서 [AGENTS.md](/home/ubuntu/charness/AGENTS.md)가 추가돼, commit discipline, portability, validator entrypoints, handoff update 원칙을 repo-local operating guide로 정리했다.
- Session 9 후반에 [pyproject.toml](/home/ubuntu/charness/pyproject.toml), [run-quality.sh](/home/ubuntu/charness/scripts/run-quality.sh), [check-duplicates.py](/home/ubuntu/charness/scripts/check-duplicates.py), [tests/test_quality_gates.py](/home/ubuntu/charness/tests/test_quality_gates.py)가 추가돼 Python helper layer에 `ruff`/`pytest`/repo-owned quality runner가 생겼다.
- Session 9 후반에 [package.json](/home/ubuntu/charness/package.json), [.markdownlint-cli2.jsonc](/home/ubuntu/charness/.markdownlint-cli2.jsonc), [.secretlintrc.json](/home/ubuntu/charness/.secretlintrc.json), [check-markdown.sh](/home/ubuntu/charness/scripts/check-markdown.sh), [check-secrets.sh](/home/ubuntu/charness/scripts/check-secrets.sh), [check-shell.sh](/home/ubuntu/charness/scripts/check-shell.sh), [check-links-external.sh](/home/ubuntu/charness/scripts/check-links-external.sh)가 추가돼 markdownlint/secretlint와 optional shell/link external gate가 quality runner에 연결됐다.
- Session 9 마무리로 [run-evals.py](/home/ubuntu/charness/scripts/run-evals.py)와 [evals/README.md](/home/ubuntu/charness/evals/README.md), fixture repos가 추가돼 repo-owned smoke scenario layer가 생겼고, `run-quality.sh`가 이를 호출한다.
- Session 10 산출물로 [skills/public/announcement/SKILL.md](/home/ubuntu/charness/skills/public/announcement/SKILL.md), [skills/public/hitl/SKILL.md](/home/ubuntu/charness/skills/public/hitl/SKILL.md), 각 adapter/reference/script 세트, 그리고 [collaboration.json](/home/ubuntu/charness/profiles/collaboration.json)이 추가됐다.
- `announcement`는 draft-first delivery skill로 정리됐고, sections/audience/delivery backend는 adapter seam으로 밀어냈다.
- `hitl`은 resumable human-judgment review skill로 정리됐고, runtime state는 repo-local `output_dir` 아래에 두는 portable state model로 축약했다.
- Session 11에서 [skills/public/find-skills/SKILL.md](/home/ubuntu/charness/skills/public/find-skills/SKILL.md), [docs/support-skill-policy.md](/home/ubuntu/charness/docs/support-skill-policy.md), [skills/public/find-skills/adapter.example.yaml](/home/ubuntu/charness/skills/public/find-skills/adapter.example.yaml), [skills/public/find-skills/scripts/resolve_adapter.py](/home/ubuntu/charness/skills/public/find-skills/scripts/resolve_adapter.py), [skills/public/find-skills/scripts/list_capabilities.py](/home/ubuntu/charness/skills/public/find-skills/scripts/list_capabilities.py)가 추가됐다.
- `find-skills`는 Vercel-style discovery flow를 참고하되 charness에서는 local public/support/integration을 먼저 보고, adapter가 있으면 `official_skill_roots`를 통해 Ceal 같은 host-official skill pack도 함께 찾는 구조로 정리됐다.
- [constitutional.json](/home/ubuntu/charness/profiles/constitutional.json)은 `find-skills`를 다시 포함하고, [tests/test_quality_gates.py](/home/ubuntu/charness/tests/test_quality_gates.py)에 adapter-configured official root smoke가 추가됐다.
- Session 11 중 duplicate gate가 큰 문서 집합에서 느려지는 문제가 드러나, [check-duplicates.py](/home/ubuntu/charness/scripts/check-duplicates.py)에 quick upper-bound filtering을 넣어 [run-quality.sh](/home/ubuntu/charness/scripts/run-quality.sh)가 다시 빠르게 통과하도록 보강했다.
- Session 12에서 [integrations/tools/agent-browser.json](/home/ubuntu/charness/integrations/tools/agent-browser.json), [integrations/tools/specdown.json](/home/ubuntu/charness/integrations/tools/specdown.json), [integrations/tools/crill.json](/home/ubuntu/charness/integrations/tools/crill.json)이 추가돼 real upstream sources를 가리키는 첫 manifest wave가 생겼다.
- `agent-browser` upstream은 `https://github.com/vercel-labs/agent-browser`, `specdown` upstream은 `https://github.com/corca-ai/specdown`, `crill` upstream은 `https://github.com/corca-ai/crill`로 고정했다.
- Session 12에서 [scripts/validate-integrations.py](/home/ubuntu/charness/scripts/validate-integrations.py), [scripts/doctor.py](/home/ubuntu/charness/scripts/doctor.py), [scripts/sync_support.py](/home/ubuntu/charness/scripts/sync_support.py), [scripts/update_tools.py](/home/ubuntu/charness/scripts/update_tools.py), [scripts/control_plane_lib.py](/home/ubuntu/charness/scripts/control_plane_lib.py)가 추가돼 control-plane dry-run and doctor seam이 생겼다.
- `doctor`는 실제 machine state를 읽으므로 이 머신에서는 `specdown`만 `ok`이고 `agent-browser`와 `crill`은 아직 `missing`이다. quality gate에는 doctor를 직접 넣지 않고, manifest validation과 deterministic tests만 넣었다.
- future evaluation engine manifest는 의도적으로 deferred 상태다. 추출된 upstream repo나 release boundary가 생기기 전에는 placeholder manifest를 만들지 않기로 했다.
- public skill set의 deeper evaluation은 future workbench successor로 하기로 했고, provisional product name은 `cautilus`다. 사용자가 `~/cautilus` 작업을 끝냈다고 알려주기 전까지는 `charness`에서 실제 evaluator integration을 시작하지 않는다.
- checked-in [cautilus-adapter.yaml](/home/ubuntu/charness/.agents/cautilus-adapter.yaml)이 추가돼 `charness`는 이제 `Cautilus doctor` 기준 최소 live-consumer surface를 가진다.
- 현재 root `cautilus-adapter`는 repo-owned `quality` gate를 외부 evaluator entrypoint로 감싼 첫 migration step이고, richer scenario/eval surface는 이후 named `cautilus-adapters/`로 분리한다.
- public skill별 provisional validation tier는 [public-skill-validation.md](/home/ubuntu/charness/docs/public-skill-validation.md)에 정리됐다. 현재 배정은 `smoke-only` 없음, `HITL recommended`는 `announcement` / `hitl` / `ideation` / `quality` / `retro`, `evaluator-required`는 `create-skill` / `debug` / `find-skills` / `gather` / `handoff` / `impl` / `spec`이다.
- constitutional core의 public execution cluster가 이제 `gather` / `ideation` / `spec` / `impl` / `debug` / `retro` / `handoff` 수준에서 실제 skill body를 갖추게 됐다.
- master plan에는 모든 public skill이 tier에 맞는 maintained validation path를 가져야 한다는 규칙이 반영됐고, deeper validation policy는 [public-skill-validation.md](/home/ubuntu/charness/docs/public-skill-validation.md)에 고정됐다.
- [engineering-quality.json](/home/ubuntu/charness/profiles/engineering-quality.json)이 추가돼 `quality` overlay profile 빈칸이 메워졌고, checked-in [quality-adapter.yaml](/home/ubuntu/charness/.agents/quality-adapter.yaml)이 canonical `./scripts/run-quality.sh` gate를 기록한다.
- `evals`는 이제 repo-owned smoke뿐 아니라 checked-in quality adapter resolve와 `find-skills` local-first discovery까지 대표 intent check로 포함한다.
- `HITL recommended` skill들의 실제 인간 검토는 아직 남아 있지만, durable queue가 [skill-outputs/hitl/hitl.md](/home/ubuntu/charness/skill-outputs/hitl/hitl.md)에 잡혀 있다.
- `sync-support`의 v1 기본 권장 전략은 이제 `reference`로 고정됐고, generated reference artifact가 [skills/support/generated/agent-browser/REFERENCE.md](/home/ubuntu/charness/skills/support/generated/agent-browser/REFERENCE.md), [skills/support/generated/crill/REFERENCE.md](/home/ubuntu/charness/skills/support/generated/crill/REFERENCE.md)에 생겼다.
- integration lock은 이제 [lock.schema.json](/home/ubuntu/charness/integrations/locks/lock.schema.json) 기준의 단일 per-tool shape를 갖고, `support` / `doctor` / `update` section을 merge하는 방향으로 정리됐다.
- [meta-builder.json](/home/ubuntu/charness/profiles/meta-builder.json)이 추가돼 target taxonomy의 profile 빈칸이 메워졌고, maintainer-facing authoring/discovery/quality overlay 범위가 explicit해졌다.
- [check-skill-contracts.py](/home/ubuntu/charness/scripts/check-skill-contracts.py)가 추가돼 `handoff` / `gather` / `create-skill` / `spec`의 representative contract markers를 deterministic gate와 eval scenario로 검증한다.
- `spec` public body는 explicit mode menu를 버리고 lighter contract-shaping heuristic 중심으로 축약돼 `create-skill`의 option-minimalism과의 충돌이 줄었다.
- 서브에이전트 탐색 결과, `cautilus` 없이 바로 할 가치가 큰 self-work는 `sync-support` 기본 전략 고정, support lock artifact shaping, 첫 real support artifact, `meta-builder` profile, representative intent checks 확대, `spec` mode drift 정리로 좁혀졌다.
- Claude plugin 구조와 Codex plugin 구조를 모두 지원해야 하지만, 이 repo의 source of truth는 host-neutral하게 유지하고 host-specific packaging은 shared artifact에서 generate하는 방향으로 정리됐다. 설치 호환 구조 작업은 support/control-plane/self-validation 빈칸을 먼저 메운 뒤 시작하는 편이 낫다.
- [packaging/charness.json](/home/ubuntu/charness/packaging/charness.json), [plugin.schema.json](/home/ubuntu/charness/packaging/plugin.schema.json), [host-packaging.md](/home/ubuntu/charness/docs/host-packaging.md), [validate-packaging.py](/home/ubuntu/charness/scripts/validate-packaging.py)가 추가돼 Claude/Codex dual-support용 shared packaging contract가 생겼다.
- [export-plugin.py](/home/ubuntu/charness/scripts/export-plugin.py)가 추가돼 shared packaging manifest에서 temp Claude/Codex plugin layout을 실제로 materialize하는 첫 export path가 생겼다.
- packaging contract는 이제 shared repo inputs, host-specific manifest paths, Codex repo marketplace shape까지 고정하고, richer install-surface metadata와 host-specific `commands/agents` generation만 다음 단계로 남겼다.
- `run-evals.py`는 이제 `handoff` / `gather` adapter init/resolve bootstrap까지 포함해 representative skill 검증이 marker check에서 one-step workflow smoke로 넓어졌다.
- [eval_registry.py](/home/ubuntu/charness/scripts/eval_registry.py)와 강화된 [validate-profiles.py](/home/ubuntu/charness/scripts/validate-profiles.py) 덕분에 profile `validation.smoke_scenarios`가 실제 repo-owned eval scenario와 동기화되는지, `extends`와 validation metadata가 drift하지 않는지까지 본다.
- `doctor.py`는 이제 prior `sync-support` lock에 적힌 `materialized_paths`가 사라졌을 때 `support-missing`을 보고해 broken support sync drift를 잡는다. first-run에서는 아직 sync하지 않은 support artifact 때문에 fail-closed하지 않는다.
- `validate-skills.py`는 이제 모든 public skill이 실제 `## References` section을 유지하고, reference 파일이 SKILL body에 빠짐없이 연결돼 있는지까지 검증한다. `SKILL.md`도 200줄을 넘기기 전에 references로 detail을 밀어내도록 guard가 생겼다.
- `validate-profiles.py`와 `validate-packaging.py`는 이제 custom cross-file checks 전에 schema validation도 함께 실행해 unknown field나 structural drift를 더 일찍 막는다. smoke fixture도 canonical taxonomy에 맞게 갱신됐다.
- [check-python-lengths.py](/home/ubuntu/charness/scripts/check-python-lengths.py)가 추가돼 helper-layer Python에서 함수 길이와 파일 길이를 deterministic gate로 본다. 현재 scope는 `scripts/*.py`와 `skills/public/*/scripts/*.py`이고, `tests/`는 제외한다.
- `charness`는 이제 격리 에이전트 런타임도 first-class target으로 본다. 새 [runtime-capability-contract.md](/home/ubuntu/charness/docs/runtime-capability-contract.md)는 grant-first / authenticated-binary / env fallback 모델을 고정하고, `gather`를 exemplar로 capability-driven onboarding 방향을 문서화한다.
- [skills/public/gather/SKILL.md](/home/ubuntu/charness/skills/public/gather/SKILL.md)와 [create-skill/SKILL.md](/home/ubuntu/charness/skills/public/create-skill/SKILL.md)는 이제 public skill 설치 모델과 capability/access-mode boundary를 반영한다.
- [manifest.schema.json](/home/ubuntu/charness/integrations/tools/manifest.schema.json)과 shipped integration manifests는 이제 ordered `access_modes`를 실제 metadata로 가진다. 현재 schema는 `grant` / `binary` / `env` / `public` / `human-only` / `degraded`를 허용하고, 현재 bundled tools는 `binary`-first + human/degraded fallback contract를 명시한다.
- [list_capabilities.py](/home/ubuntu/charness/skills/public/find-skills/scripts/list_capabilities.py)는 이제 integration discovery 결과에 `kind`와 `access_modes`를 포함한다. `find-skills`는 external integration을 단순 존재 여부가 아니라 실제 access path가 보이는 capability surface로 보여준다.
- [validate-integrations.py](/home/ubuntu/charness/scripts/validate-integrations.py)는 이제 `access_modes`가 canonical runtime preference order를 따르는지도 검증한다. ordered metadata가 단순 관습이 아니라 repo-owned contract가 됐다.
- [create-skill/SKILL.md](/home/ubuntu/charness/skills/public/create-skill/SKILL.md)와 관련 references는 이제 integration manifest가 discovery surface에 드러날 capability kind/access metadata까지 담아야 한다고 명시한다. capability contract가 validation/discovery뿐 아니라 authoring guidance에도 연결됐다.
- integration manifest schema는 이제 optional `capability_requirements`를 받아 `grant_ids`, `env_vars`, `permission_scopes` 같은 non-secret requirement를 표현할 수 있다. `find-skills` discovery도 이 metadata를 노출하고, `validate-integrations.py`는 `grant`/`env` access mode가 있을 때 필요한 requirement fields를 요구한다.
- [doctor.py](/home/ubuntu/charness/scripts/doctor.py)는 이제 live health 결과와 함께 manifest의 `kind`, `access_modes`, `capability_requirements`도 JSON payload에 실어 control-plane consumer가 별도 manifest reread 없이 capability context를 볼 수 있게 한다.
- integration manifest schema는 이제 optional `readiness_checks`도 지원한다. `doctor.py`는 이를 실행해 `readiness` payload와 `not-ready` status를 낼 수 있으므로, binary가 있더라도 setup prerequisite가 빠진 host를 별도 상태로 구분한다.
- [list_capabilities.py](/home/ubuntu/charness/skills/public/find-skills/scripts/list_capabilities.py)는 이제 integration discovery 결과에 `readiness_checks` 요약도 포함한다. [create-skill/SKILL.md](/home/ubuntu/charness/skills/public/create-skill/SKILL.md) 역시 setup prerequisite를 operator prose 대신 manifest readiness probe로 표현하라고 요구한다.
- integration manifest schema는 이제 optional `config_layers`도 지원한다. 이건 host-neutral precedence만 담는 레이어로, `grant -> authenticated-binary -> env -> operator-step -> public-fallback` 순서를 validator가 강제하고 `find-skills` discovery도 요약을 노출한다.
- `gather` reusable provider surface의 첫 concrete manifests로 [github-gh.json](/home/ubuntu/charness/integrations/tools/github-gh.json), [google-public-export.json](/home/ubuntu/charness/integrations/tools/google-public-export.json), [notion-published-export.json](/home/ubuntu/charness/integrations/tools/notion-published-export.json), [slack-bot-export.json](/home/ubuntu/charness/integrations/tools/slack-bot-export.json)이 추가됐다. 이들은 `~/claude-plugins/plugins/cwf/skills/gather`의 existing implementation을 기준으로 provider별 capability/access/onboarding metadata를 repo-owned manifest로 고정한다.
- generated support reference는 이제 access modes, capability requirements, config layers, reuse notes까지 포함하도록 두꺼워졌고, [REFERENCE.md](/home/ubuntu/charness/skills/support/generated/google-public-export/REFERENCE.md), [REFERENCE.md](/home/ubuntu/charness/skills/support/generated/notion-published-export/REFERENCE.md), [REFERENCE.md](/home/ubuntu/charness/skills/support/generated/slack-bot-export/REFERENCE.md)도 추가됐다.
- Ceal consumption model v1이 [ceal-consumption-model.md](/home/ubuntu/charness/docs/ceal-consumption-model.md)에 정리됐다. 핵심은 Ceal repo maintainer 환경은 full `charness`를 소비하고, Ceal Slack app 조직 설치는 Ceal-owned preset을 install unit으로 삼는 dual consumption model이다.
- preset contract가 한 단계 강해졌다. preset file은 이제 YAML-safe frontmatter로 `name`, `description`, `preset_kind`, `install_scope`를 가져야 하고, [validate-presets.py](/home/ubuntu/charness/scripts/validate-presets.py)가 이를 검증한다. shipped `charness` preset은 현재 전부 `maintainer` scope이고, future `organization` scope preset은 `product-slice` kind와 `## Exposure Contract` section을 요구한다.
- repo root 자체가 plugin root로 동작할 수 있도록 [plugin.json](/home/ubuntu/charness/.claude-plugin/plugin.json), [marketplace.json](/home/ubuntu/charness/.claude-plugin/marketplace.json), [plugin.json](/home/ubuntu/charness/.codex-plugin/plugin.json), [marketplace.json](/home/ubuntu/charness/.agents/plugins/marketplace.json)을 checked-in generated artifact로 두기 시작했다. 이 파일들은 [charness.json](/home/ubuntu/charness/packaging/charness.json)에서 [sync_root_plugin_manifests.py](/home/ubuntu/charness/scripts/sync_root_plugin_manifests.py)로 생성되고, [validate-packaging.py](/home/ubuntu/charness/scripts/validate-packaging.py)가 shared packaging manifest와의 일치를 강제한다.
- manifest와 profile metadata는 v1에서 JSON을 canonical format으로 두고, preset은 schema 도입 전까지 markdown convention으로 관리한다.
- 아직 없는 것:
  - support skill migrations and integration wrappers
  - extracted evaluation engine (`cautilus`) integration manifest
  - executable support-sync beyond the current reference-only seam
  - support control-plane lock artifact shaping beyond the current initial seam
  - the first concrete downstream org-installable preset in the host repo

## Next Session

1. pre-`cautilus`로 계속 가면 `gather` provider manifests 다음 단계로, upstream executable support surface를 `reference` 이상으로 materialize할지 (`copy` / `symlink` / fetch) 아니면 host가 별도 provider runtime을 책임지게 둘지 결정하고 그 contract를 좁힌다.
2. packaging export는 계속 최소 generated surface만 유지하고, richer install-surface metadata는 capability contract와 충돌하지 않게 나중에 본다.
3. checked-in root host manifests로 Claude/Codex direct install experiment를 실제로 해 보고, 필요하면 packaging metadata를 더 보강한다.
4. `create-skill` / `spec`도 marker check를 넘는 repo-owned workflow gate로 올릴 수 있을지 본다.
5. profile inheritance를 실제 merged bundle feature로 키울지 정하기 전까지는 현재 validator contract 안에서 metadata drift만 막는다.
6. Ceal repo 쪽에서 first `organization`-scope preset을 실제로 정의할 때, 방금 추가한 preset contract를 그대로 쓸지 보고 필요한 최소 metadata만 더한다.
7. `Cautilus doctor`가 통과하는 root adapter를 유지하면서, richer evaluator surface가 필요해지면 named `cautilus-adapters/`를 설계한다.
8. extracted evaluation engine용 integration manifest를 추가하고 control-plane contract에 연결한다.
9. [public-skill-validation.md](/home/ubuntu/charness/docs/public-skill-validation.md)의 provisional matrix를 `cautilus` contract 기준으로 confirm하거나 필요한 최소 범위만 조정한다.
10. `quality`가 이미 가진 smoke/lint/validator layer 위에 어떤 intent/workflow eval을 더 올릴지 정하고, evaluator-required 경계와 HITL fallback 경계를 함께 문서화한다.
11. manifest validation, control-plane tests, eval fixtures, handoff를 새 evaluator contract에 맞게 갱신한다.

## Discuss

- Claude plugin과 Codex plugin을 동시에 지원할 때 어떤 shared packaging manifest를 canonical source로 둘지 정해야 한다.
- future evaluation engine을 `workbench` transitional id로 계속 둘지, extraction 전에 새 permanent id를 줄지 결정이 필요하다.
- shared packaging manifest가 release version을 직접 들고 갈지, export-time override를 허용할지 나중에 정해야 한다.
- generated Claude/Codex export trees를 repo fixture로 보관할지, script+temp smoke만 canonical로 둘지 정해야 한다.
- profile `extends`를 실제 merged bundle feature로 키울지, 계속 mostly-deferred metadata seam으로 둘지 나중에 정해야 한다.
- capability grants, authenticated binaries, and env fallback를 `access_modes`/`capability_requirements` beyond metadata로 integration manifest schema에 어느 깊이까지 올릴지 정해야 한다.
- `cautilus` 쪽 contract가 나온 뒤 `find-skills`나 support policy에서 `official`보다 더 일반적인 용어(`trusted` / `declared`)로 바꿀지 다시 볼 가치가 있다.
- profile inheritance를 얼마나 허용할지, 아니면 flattened bundle만 허용할지 결정이 필요하다.
- preset schema를 JSON으로 둘지 markdown-first catalog를 더 유지할지 나중에 정해야 한다.
- `ideation`에서 entity/stage thinking을 어느 정도까지 public core에 넣고, 어디부터 reference나 examples로 뺄지 조정이 필요하다.
- `spec`이 procedural checklist로 무거워지지 않으면서도 implementation handoff를 충분히 단단하게 만들 수 있을지 계속 검증이 필요하다.
- `quality`가 proposal skill인지 gate skill인지, 또는 두 성격을 어떻게 함께 담을지 정리가 필요하다.
- shipped sample preset을 어디까지 repo-agnostic example로 둘지, 어디부터 host/profile seam으로 뺄지 결정이 필요하다.
- `quality` dogfood에서 나온 concrete gate proposals를 Session 10 이후 어느 층위에서 실제 구현할지 정해야 한다.
- `spec`의 explicit mode 구조를 유지할지, `create-skill`의 option-minimalism에 맞춰 heuristic branch로 낮출지 결정이 필요하다.
- `announcement` delivery kind를 `none | release-notes | command`까지만 public core에 둘지, downstream examples를 더 늘릴지 정해야 한다.
- `hitl` runtime state를 지금처럼 portable minimum으로 둘지, later support layer에서 richer queue/context tooling을 붙일지 정해야 한다.

## References

- [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md)
- [AGENTS.md](/home/ubuntu/charness/AGENTS.md)
- [README.md](/home/ubuntu/charness/README.md)
- [master-plan.md](/home/ubuntu/charness/docs/master-plan.md)
- [public-skill-validation.md](/home/ubuntu/charness/docs/public-skill-validation.md)
- [engineering-quality.json](/home/ubuntu/charness/profiles/engineering-quality.json)
- [meta-builder.json](/home/ubuntu/charness/profiles/meta-builder.json)
- [host-packaging.md](/home/ubuntu/charness/docs/host-packaging.md)
- [packaging/README.md](/home/ubuntu/charness/packaging/README.md)
- [plugin.schema.json](/home/ubuntu/charness/packaging/plugin.schema.json)
- [charness.json](/home/ubuntu/charness/packaging/charness.json)
- [quality-adapter.yaml](/home/ubuntu/charness/.agents/quality-adapter.yaml)
- [cautilus-adapter.yaml](/home/ubuntu/charness/.agents/cautilus-adapter.yaml)
- [lock.schema.json](/home/ubuntu/charness/integrations/locks/lock.schema.json)
- [skills/support/README.md](/home/ubuntu/charness/skills/support/README.md)
- [REFERENCE.md](/home/ubuntu/charness/skills/support/generated/agent-browser/REFERENCE.md)
- [REFERENCE.md](/home/ubuntu/charness/skills/support/generated/crill/REFERENCE.md)
- [REFERENCE.md](/home/ubuntu/charness/skills/support/generated/google-public-export/REFERENCE.md)
- [REFERENCE.md](/home/ubuntu/charness/skills/support/generated/notion-published-export/REFERENCE.md)
- [REFERENCE.md](/home/ubuntu/charness/skills/support/generated/slack-bot-export/REFERENCE.md)
- [check-skill-contracts.py](/home/ubuntu/charness/scripts/check-skill-contracts.py)
- [validate-packaging.py](/home/ubuntu/charness/scripts/validate-packaging.py)
- [export-plugin.py](/home/ubuntu/charness/scripts/export-plugin.py)
- [eval_registry.py](/home/ubuntu/charness/scripts/eval_registry.py)
- [external-integrations.md](/home/ubuntu/charness/docs/external-integrations.md)
- [runtime-capability-contract.md](/home/ubuntu/charness/docs/runtime-capability-contract.md)
- [skill-migration-map.md](/home/ubuntu/charness/docs/skill-migration-map.md)
- [control-plane.md](/home/ubuntu/charness/docs/control-plane.md)
- [manifest.schema.json](/home/ubuntu/charness/integrations/tools/manifest.schema.json)
- [profile.schema.json](/home/ubuntu/charness/profiles/profile.schema.json)
- [skills/public/create-skill/SKILL.md](/home/ubuntu/charness/skills/public/create-skill/SKILL.md)
- [portable-authoring.md](/home/ubuntu/charness/skills/public/create-skill/references/portable-authoring.md)
- [constitutional.json](/home/ubuntu/charness/profiles/constitutional.json)
- [skills/public/retro/SKILL.md](/home/ubuntu/charness/skills/public/retro/SKILL.md)
- [mode-guide.md](/home/ubuntu/charness/skills/public/retro/references/mode-guide.md)
- [section-guide.md](/home/ubuntu/charness/skills/public/retro/references/section-guide.md)
- [skills/public/ideation/SKILL.md](/home/ubuntu/charness/skills/public/ideation/SKILL.md)
- [concept-architecture.md](/home/ubuntu/charness/skills/public/ideation/references/concept-architecture.md)
- [truth-and-edge.md](/home/ubuntu/charness/skills/public/ideation/references/truth-and-edge.md)
- [world-modeling.md](/home/ubuntu/charness/skills/public/ideation/references/world-modeling.md)
- [agent-human-lens.md](/home/ubuntu/charness/skills/public/ideation/references/agent-human-lens.md)
- [skills/public/spec/SKILL.md](/home/ubuntu/charness/skills/public/spec/SKILL.md)
- [contract-modes.md](/home/ubuntu/charness/skills/public/spec/references/contract-modes.md)
- [fixed-probe-defer.md](/home/ubuntu/charness/skills/public/spec/references/fixed-probe-defer.md)
- [success-criteria.md](/home/ubuntu/charness/skills/public/spec/references/success-criteria.md)
- [acceptance-checks.md](/home/ubuntu/charness/skills/public/spec/references/acceptance-checks.md)
- [impl-loop.md](/home/ubuntu/charness/skills/public/spec/references/impl-loop.md)
- [ideation-boundary.md](/home/ubuntu/charness/skills/public/spec/references/ideation-boundary.md)
- [skills/public/impl/SKILL.md](/home/ubuntu/charness/skills/public/impl/SKILL.md)
- [skills/public/debug/SKILL.md](/home/ubuntu/charness/skills/public/debug/SKILL.md)
- [skills/public/gather/SKILL.md](/home/ubuntu/charness/skills/public/gather/SKILL.md)
- [skills/public/handoff/SKILL.md](/home/ubuntu/charness/skills/public/handoff/SKILL.md)
- [skills/public/quality/SKILL.md](/home/ubuntu/charness/skills/public/quality/SKILL.md)
- [typescript-quality.md](/home/ubuntu/charness/presets/typescript-quality.md)
- [python-quality.md](/home/ubuntu/charness/presets/python-quality.md)
- [skills/public/announcement/SKILL.md](/home/ubuntu/charness/skills/public/announcement/SKILL.md)
- [skills/public/hitl/SKILL.md](/home/ubuntu/charness/skills/public/hitl/SKILL.md)
- [profiles/collaboration.json](/home/ubuntu/charness/profiles/collaboration.json)
- [skill-outputs/hitl/hitl.md](/home/ubuntu/charness/skill-outputs/hitl/hitl.md)
- [contract-consumption.md](/home/ubuntu/charness/skills/public/impl/references/contract-consumption.md)
- [five-steps.md](/home/ubuntu/charness/skills/public/debug/references/five-steps.md)
- [source-priority.md](/home/ubuntu/charness/skills/public/gather/references/source-priority.md)
- [workflow-trigger.md](/home/ubuntu/charness/skills/public/handoff/references/workflow-trigger.md)
