# Ceal Handoff

## Workflow Trigger

- 다음 세션에서 이 문서를 멘션하면 `$ceal:impl`로 이어서 `charness` Session 3을 진행한다.
- 시작하자마자 [master-plan.md](/home/ubuntu/charness/docs/master-plan.md), [control-plane.md](/home/ubuntu/charness/docs/control-plane.md), [manifest.schema.json](/home/ubuntu/charness/integrations/tools/manifest.schema.json), [profile.schema.json](/home/ubuntu/charness/profiles/profile.schema.json)를 다시 읽고 `create-skill`을 charness의 canonical authoring contract로 재작성한다.

## Current State

- `charness`는 Ceal과 분리된 portable Corca harness product로 정의됐다.
- public skill / support skill / profile / integration 경계가 문서로 고정됐다.
- `quality`는 public skill 하나로 두고, `hitl`은 collaboration profile에 두며, `ideation`이 `interview`를 흡수하고, `retro`는 mode로 확장한다는 결정이 반영됐다.
- external binary는 `charness`가 vendor하지 않고 integration manifest와 sync/update/doctor flow로 다룬다는 정책이 고정됐다.
- Session 2 산출물로 [manifest.schema.json](/home/ubuntu/charness/integrations/tools/manifest.schema.json), [profile.schema.json](/home/ubuntu/charness/profiles/profile.schema.json), [control-plane.md](/home/ubuntu/charness/docs/control-plane.md)가 추가됐다.
- manifest와 profile metadata는 v1에서 JSON을 canonical format으로 둔다.
- repo skeleton은 git에 남도록 `.gitkeep`과 README가 추가됐고, generated support-skill/lock 경로도 명시됐다.
- 아직 없는 것:
  - 실제 tool별 manifest instance
  - 실제 profile instance
  - migrated public/support skill bodies
  - validation scripts와 doctor implementation

## Next Session

1. `skills/public/create-skill/` 초안을 만든다.
   - portable authoring contract
   - adapter-core / preset seam rules
   - external integration manifest 참조 규칙
2. Session 3 문맥에서 필요한 preset / adapter vocabulary를 고정한다.
   - host-specific behavior를 skill body 밖으로 미는 기준
   - proposal / optional setup / validation 문구 규칙
3. manifest contract와 `create-skill`의 연결부를 정리한다.
   - 외부 tool dependency를 숨기지 않고 어떻게 드러낼지
   - support skill reuse를 authoring guidance에 어떻게 연결할지
4. 가능하면 첫 profile instance나 example metadata까지 하나 만든다.

## Discuss

- `sync-support` 기본 전략을 `reference`, `copy`, `symlink` 중 무엇으로 둘지 아직 결정이 필요하다.
- upstream support skill version과 binary version 상태를 하나의 lock artifact로 둘지, 별도 lock으로 나눌지 정해야 한다.
- future evaluation engine을 `workbench` transitional id로 계속 둘지, extraction 전에 새 permanent id를 줄지 결정이 필요하다.
- profile inheritance를 얼마나 허용할지, 아니면 flattened bundle만 허용할지 결정이 필요하다.

## References

- [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md)
- [README.md](/home/ubuntu/charness/README.md)
- [master-plan.md](/home/ubuntu/charness/docs/master-plan.md)
- [external-integrations.md](/home/ubuntu/charness/docs/external-integrations.md)
- [skill-migration-map.md](/home/ubuntu/charness/docs/skill-migration-map.md)
- [control-plane.md](/home/ubuntu/charness/docs/control-plane.md)
- [manifest.schema.json](/home/ubuntu/charness/integrations/tools/manifest.schema.json)
- [profile.schema.json](/home/ubuntu/charness/profiles/profile.schema.json)
