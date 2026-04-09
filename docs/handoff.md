# Ceal Handoff

## Workflow Trigger

- 다음 세션에서 이 문서를 멘션하면 `charness` Session 2로 이어서 integration manifest contract와 sync/update/doctor control plane 설계를 진행한다.
- 시작하자마자 [master-plan.md](/home/ubuntu/charness/docs/master-plan.md), [external-integrations.md](/home/ubuntu/charness/docs/external-integrations.md), [skill-migration-map.md](/home/ubuntu/charness/docs/skill-migration-map.md)를 다시 읽고, 이미 고정된 taxonomy와 ownership policy를 바꾸지 않는 범위에서만 작업한다.

## Current State

- `charness`는 Ceal과 분리된 portable Corca harness product로 정의됐다.
- public skill / support skill / profile / integration 경계가 문서로 고정됐다.
- `quality`는 public skill 하나로 두고, `hitl`은 collaboration profile에 두며, `ideation`이 `interview`를 흡수하고, `retro`는 mode로 확장한다는 결정이 반영됐다.
- external binary는 `charness`가 vendor하지 않고 integration manifest와 sync/update/doctor flow로 다룬다는 정책이 고정됐다.
- 현재 repo에는 README, master plan, external integration policy, skill migration map, 기본 디렉토리 skeleton만 있다.
- 아직 없는 것:
  - integration manifest schema
  - profile schema
  - support-skill upstream sync contract
  - actual skill content migration

## Next Session

1. Session 2 산출물을 만든다.
   - `integrations/tools/` manifest schema 초안
   - `profiles/` metadata schema 초안
   - `sync-support`, `update-tools`, `doctor` control plane 설계 문서
2. external tool별 1차 대상 목록을 구체화한다.
   - `agent-browser`
   - `specdown`
   - `crill`
   - future evaluation engine split from workbench
3. upstream support skill reuse contract를 문서화한다.
   - upstream skill을 그대로 쓰는 경우
   - thin compatibility wrapper가 필요한 경우
   - fork가 허용되는 예외 조건
4. Session 3 준비물까지 깔아둔다.
   - `create-skill` rewrite에서 참조할 공통 adapter-core / preset / manifest seams가 무엇인지 정리

## Discuss

- integration manifests를 JSON으로 둘지 YAML로 둘지 결정이 필요하다.
- `sync-support`가 외부 스킬을 symlink로 노출할지, copy/snapshot으로 둘지, host별로 다르게 둘지 결정이 필요하다.
- upstream support skill version과 binary version을 하나의 manifest에서 함께 관리할지, 별도 artifact로 나눌지 정해야 한다.
- future evaluation engine을 `workbench`라는 임시 이름으로 계속 부를지, 아직 generic id만 둘지 결정이 필요하다.

## References

- [docs/handoff.md](/home/ubuntu/charness/docs/handoff.md)
- [README.md](/home/ubuntu/charness/README.md)
- [master-plan.md](/home/ubuntu/charness/docs/master-plan.md)
- [external-integrations.md](/home/ubuntu/charness/docs/external-integrations.md)
- [skill-migration-map.md](/home/ubuntu/charness/docs/skill-migration-map.md)
