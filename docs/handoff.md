# Ceal Handoff

## Workflow Trigger

- 다음 세션에서 이 문서를 멘션하면 `$ceal:impl`로 이어서 `charness` Session 8을 진행한다.
- 시작하자마자 [master-plan.md](/home/ubuntu/charness/docs/master-plan.md), [skill-migration-map.md](/home/ubuntu/charness/docs/skill-migration-map.md), [skills/public/impl/SKILL.md](/home/ubuntu/charness/skills/public/impl/SKILL.md), [skills/public/debug/SKILL.md](/home/ubuntu/charness/skills/public/debug/SKILL.md), [/home/ubuntu/ceal/.agents/skills/concept-review/SKILL.md](/home/ubuntu/ceal/.agents/skills/concept-review/SKILL.md), [/home/ubuntu/ceal/.agents/skills/test-improvement/SKILL.md](/home/ubuntu/ceal/.agents/skills/test-improvement/SKILL.md)를 다시 읽고 `quality`와 sample preset 방향을 설계한다.

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
- `spec`은 `contract-first` / `braided` / `executable-spec` mode를 갖고, `Fixed Decisions` / `Probe Questions` / `Deferred Decisions`로 현재 slice의 불확실성을 관리한다.
- `spec`은 success criteria를 acceptance checks와 직접 연결하고, 구현 중 새 사실이 나오면 canonical artifact를 갱신하도록 설계됐다.
- Session 7 산출물로 [skills/public/impl/SKILL.md](/home/ubuntu/charness/skills/public/impl/SKILL.md), [skills/public/debug/SKILL.md](/home/ubuntu/charness/skills/public/debug/SKILL.md), [skills/public/gather/SKILL.md](/home/ubuntu/charness/skills/public/gather/SKILL.md), [skills/public/handoff/SKILL.md](/home/ubuntu/charness/skills/public/handoff/SKILL.md)와 관련 references가 추가됐다.
- `impl`은 living contract를 소비하되 별도 `spec` 세션이 없어도 inline current-slice contract를 부트스트랩할 수 있는 execution skill로 조정되고 있다.
- `debug`, `gather`, `handoff`는 durable artifact 기본 위치를 `skill-outputs/<skill-name>/` 아래 정해진 파일로 두고, adapter `output_dir` override와 helper script bootstrap까지 갖추는 방향으로 보강되고 있다.
- constitutional core의 public execution cluster가 이제 `gather` / `ideation` / `spec` / `impl` / `debug` / `retro` / `handoff` 수준에서 실제 skill body를 갖추게 됐다.
- master plan에는 모든 public skill을 나중에 `workbench` 시나리오와 `hitl` 검토로 검증한다는 규칙이 추가됐다.
- manifest와 profile metadata는 v1에서 JSON을 canonical format으로 두고, preset은 schema 도입 전까지 markdown convention으로 관리한다.
- 아직 없는 것:
  - 실제 tool별 manifest instance
  - `quality` / `announcement` / `hitl` / `find-skills` public skill bodies
  - support skill migrations and integration wrappers
  - validation scripts와 doctor implementation

## Next Session

1. `quality`를 one-skill public concept로 설계하고, `concept-review` / `test-improvement` / `security-audit` 계열 참조를 어디까지 흡수할지 정한다.
2. TypeScript와 Python용 sample preset 방향을 정하고, proposal behavior가 repo stack을 어떻게 감지할지 정리한다.
3. `quality`가 지금까지 만든 `spec` / `impl` / `debug` cluster와 어떻게 이어지는지 경계를 고정한다.
4. `quality` 다음에는 `charness` repo 자체에 lint / test / concept / security review를 돌리는 dogfood session을 수행한다.
5. `workbench` + `hitl` validation은 public skill cluster가 더 모인 뒤 묶어서 수행한다.

## Discuss

- `sync-support` 기본 전략을 `reference`, `copy`, `symlink` 중 무엇으로 둘지 아직 결정이 필요하다.
- upstream support skill version과 binary version 상태를 하나의 lock artifact로 둘지, 별도 lock으로 나눌지 정해야 한다.
- future evaluation engine을 `workbench` transitional id로 계속 둘지, extraction 전에 새 permanent id를 줄지 결정이 필요하다.
- profile inheritance를 얼마나 허용할지, 아니면 flattened bundle만 허용할지 결정이 필요하다.
- preset schema를 JSON으로 둘지 markdown-first catalog를 더 유지할지 나중에 정해야 한다.
- `ideation`에서 entity/stage thinking을 어느 정도까지 public core에 넣고, 어디부터 reference나 examples로 뺄지 조정이 필요하다.
- `spec`이 procedural checklist로 무거워지지 않으면서도 implementation handoff를 충분히 단단하게 만들 수 있을지 계속 검증이 필요하다.
- `quality`가 proposal skill인지 gate skill인지, 또는 두 성격을 어떻게 함께 담을지 정리가 필요하다.
- shipped sample preset을 어디까지 repo-agnostic example로 둘지, 어디부터 host/profile seam으로 뺄지 결정이 필요하다.

## References

- [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md)
- [README.md](/home/ubuntu/charness/README.md)
- [master-plan.md](/home/ubuntu/charness/docs/master-plan.md)
- [external-integrations.md](/home/ubuntu/charness/docs/external-integrations.md)
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
- [contract-consumption.md](/home/ubuntu/charness/skills/public/impl/references/contract-consumption.md)
- [five-steps.md](/home/ubuntu/charness/skills/public/debug/references/five-steps.md)
- [source-priority.md](/home/ubuntu/charness/skills/public/gather/references/source-priority.md)
- [workflow-trigger.md](/home/ubuntu/charness/skills/public/handoff/references/workflow-trigger.md)
- [/home/ubuntu/ceal/.agents/skills/concept-review/SKILL.md](/home/ubuntu/ceal/.agents/skills/concept-review/SKILL.md)
- [/home/ubuntu/ceal/.agents/skills/test-improvement/SKILL.md](/home/ubuntu/ceal/.agents/skills/test-improvement/SKILL.md)
- [entity-stage-design/SKILL.md](/home/ubuntu/ceal/.codex/skills/entity-stage-design/SKILL.md)
- [clarify/SKILL.md](/home/ubuntu/claude-plugins/plugins/cwf/skills/clarify/SKILL.md)
