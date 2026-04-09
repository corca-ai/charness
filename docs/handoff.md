# Ceal Handoff

## Workflow Trigger

- 다음 세션에서 이 문서를 멘션하면 `$ceal:impl`로 이어서 `charness` Session 5를 진행한다.
- 시작하자마자 [master-plan.md](/home/ubuntu/charness/docs/master-plan.md), [skill-migration-map.md](/home/ubuntu/charness/docs/skill-migration-map.md), [entity-stage-design/SKILL.md](/home/ubuntu/ceal/.codex/skills/entity-stage-design/SKILL.md)를 다시 읽고 `ideation`을 설계한다.

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
- master plan에는 모든 public skill을 나중에 `workbench` 시나리오와 `hitl` 검토로 검증한다는 규칙이 추가됐다.
- manifest와 profile metadata는 v1에서 JSON을 canonical format으로 두고, preset은 schema 도입 전까지 markdown convention으로 관리한다.
- 아직 없는 것:
  - 실제 tool별 manifest instance
  - migrated public/support skill bodies
  - validation scripts와 doctor implementation

## Next Session

1. `skills/public/ideation/` 초안을 만든다.
   - `interview`를 흡수하는 public concept
   - entity와 stage를 분리해서 생각하는 장점을 가져오되, 별도 specialist surface로 쪼개지지 않게 유지
2. Ceal의 [entity-stage-design/SKILL.md](/home/ubuntu/ceal/.codex/skills/entity-stage-design/SKILL.md)를 reference로 읽고 필요한 아이디어만 portable하게 차용한다.
   - durable entities vs chronological stages 분리
   - incremental design refinement
   - contradiction surfacing
3. `ideation`이 `spec`과 겹치지 않도록 경계를 명확히 한다.
4. validation은 지금 바로 하지 말고, public skill cluster가 더 모인 뒤 `workbench` + `hitl` 묶음으로 수행한다.

## Discuss

- `sync-support` 기본 전략을 `reference`, `copy`, `symlink` 중 무엇으로 둘지 아직 결정이 필요하다.
- upstream support skill version과 binary version 상태를 하나의 lock artifact로 둘지, 별도 lock으로 나눌지 정해야 한다.
- future evaluation engine을 `workbench` transitional id로 계속 둘지, extraction 전에 새 permanent id를 줄지 결정이 필요하다.
- profile inheritance를 얼마나 허용할지, 아니면 flattened bundle만 허용할지 결정이 필요하다.
- preset schema를 JSON으로 둘지 markdown-first catalog를 더 유지할지 나중에 정해야 한다.
- `ideation`에서 entity/stage thinking을 어느 정도까지 public core에 넣고, 어디부터 reference나 examples로 뺄지 조정이 필요하다.

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
- [entity-stage-design/SKILL.md](/home/ubuntu/ceal/.codex/skills/entity-stage-design/SKILL.md)
