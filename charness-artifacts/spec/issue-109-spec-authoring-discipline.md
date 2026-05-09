# Spec: Issue #109 — Reusable top-level spec authoring discipline

Source: https://github.com/corca-ai/charness/issues/109

이 spec은 이슈 #109의 **design extraction 패스**다. 이슈 본문이 명시적으로
요구한 대로, Cautilus rework가 끝나고 user/maintainer-facing 스펙이 충분히
HITL을 거치기 전까지는 Cautilus 드래프트로부터 일반화된 권고를 추출하지 않는다.
첫 Charness 패스의 산출은 옵션 비교, 안티골, design→implementation 이행에
필요한 증거다.

## Problem

Charness가 관리하는 레포는 도메인 특성상 user-facing 스토리, maintainer-facing
proof map, cross-concern 가시성을 묶은 "top-level 스펙"이 필요해질 때가 있다.
공유 어휘, 가독성 있는 acceptance criteria, 검사 가능한 evidence를 갖되,
하나의 워크플로우 분해가 다른 관심사(증거 위치, 책임, 비용, 어휘, agent/human
가독성)를 가리지 않게 해야 한다.

현재 charness 표면이 가진 부분 커버리지:

- `narrative` — 진리 표면 정렬, claim audit, brief skeleton, landing-rewrite
  loop, scenario blocks를 가르친다. README/landing/operator-doc 같은
  first-touch 문서에 강하다.
- `spec` — 구현 계약, fixed/probe/deferred 분류, success criteria, acceptance
  checks, executable spec cost를 가르친다. 슬라이스 단위 build contract에
  강하다.
- `support/specdown` — executable spec syntax, report shape, adapter check
  protocol을 가르친다. specdown이 substrate일 때 권한이 명확하다.

가려지는 빈틈은 "도메인을 가로지르는 user/maintainer/cross-concern 스펙 패키지를
어떻게 구성하는가"라는 작가 디시플린이다. 이 디시플린은 단일 슬라이스 계약도,
단일 first-touch 문서도, 단일 executable substrate도 아니다.

## Current Slice

design extraction 한정. 출력은 본 spec 한 문서다. 공개 스킬 본문, 공개
reference, 공개 export, 또는 임의 인접 레포의 스펙 디렉토리 형태에는 손대지
않는다. Cautilus rework 종료 + 충분한 HITL 통과 이후의 추출 패스에서 본 spec을
입력으로 다시 사용한다.

## Fixed Decisions

- **본 패스는 design extraction이며 implementation이 아니다.** 이슈 본문의
  "Do not implement this from the current Cautilus drafts too early"를
  계약으로 받는다.
- **Cautilus 의존성은 이슈 메타데이터로만 다룬다.** 본 spec은 Cautilus의
  현재 드래프트 내용을 인용/모방/일반화하지 않는다. Cautilus rework 진행
  현황은 root [.agents/cautilus-adapter.yaml](../../.agents/cautilus-adapter.yaml)
  의 `run_mode: disabled` 상태와 [docs/handoff.md](../../docs/handoff.md) 24번
  항목으로 추적한다.
- **이슈 #108(specdown 라우팅)과 본 이슈의 경계.** #108은 task language가
  hidden support skill로 라우팅되는 것을 보장한다. 본 이슈는 그 위층의 작가
  디시플린을 다룬다. #108 변화는 본 spec이 아닌 `find-skills` 표면이 owner다.
- **Charness scope.** 본 디시플린은 portable해야 한다. Cautilus나 임의 단일
  consumer repo가 가진 product-local 어휘를 일반 권고로 굳히지 않는다.

## Options Compared

세 가지 owner 분포를 비교한다.

### Option A — `narrative`가 단독 owner

Pros:

- 진리 표면 정렬, claim audit, scenario blocks가 이미 `narrative`에 있다.
- user-facing 스토리/landing/operator 표면은 이미 `narrative`의 영역이다.
- adapter 계약이 이미 `narrative` 쪽에 있어 host-specific overlay가 자연스럽다.

Cons:

- "implementation contract" 어휘(fixed/probe/deferred, success criteria,
  acceptance checks, executable spec cost)는 `narrative`에 없다. 옮기면
  `narrative`가 build-time 계약 관리까지 떠안게 된다.
- `narrative`의 brief/announcement 경계가 흐려진다.
- maintainer-facing proof map은 build contract 가족이지 narrative가 아니다.

### Option B — `spec`이 단독 owner

Pros:

- maintainer-facing proof map, acceptance criteria, evidence placement,
  executable spec cost는 이미 `spec`의 어휘다.
- specdown substrate에 대한 cost/boundary rule도 `spec/references`에 있다.

Cons:

- user-facing 스토리, cross-concern visibility, 공유 어휘 정렬, landing
  rewrite는 `narrative`의 영역이다. `spec`이 다 떠안으면 단일 슬라이스 build
  contract 관리라는 본업이 흐려진다.
- `spec`은 한 슬라이스 단위 계약이다. "도메인을 가로지르는 스펙 패키지"는
  여러 슬라이스를 가로질러 살아 있어야 한다.

### Option C — split: narrative가 의미/관심사, spec/specdown support가 실행 substrate

이슈 본문이 직접 명시한 가설.

Pros:

- 각 스킬이 이미 가진 어휘와 충돌하지 않는다. `narrative`는 진리 표면 정렬
  + scenario blocks + landing rewrite loop를 그대로 owner로 둔다. `spec`은
  acceptance criteria + executable spec cost + contract modes를 그대로 owner로
  둔다. `support/specdown`은 substrate syntax/report/adapter를 그대로 owner로
  둔다.
- 도메인 어휘 정렬은 단일 home(narrative)이고, 슬라이스 계약은 단일
  home(spec)이며, executable substrate는 단일 home(specdown). 작가가 어디를
  먼저 봐야 하는지가 layer로 결정된다.
- portable: substrate가 specdown이 아닐 때 specdown 부분만 비워도 디시플린이
  무너지지 않는다.

Cons:

- 두 공개 스킬과 한 support skill을 가로질러 권고가 분포한다. cross-skill
  trigger와 reference 정합성을 의도적으로 관리해야 한다.
- 잘못 쓰면 "어디서부터 봐야 하는지"가 오히려 불명확해진다. layer 진입 규칙을
  명시해야 한다.

### Recommendation

**Option C — split.** 단, 본 패스에서는 권고만 기록하고 스킬 본문은 바꾸지
않는다. 실제 분포는 design→implementation 이행 조건을 만족한 다음 패스에서
landing한다.

Layer 진입 규칙(권고):

1. user-facing 스토리, 공유 어휘, cross-concern 가시성, landing/first-touch
   문서, brief 적합성은 `narrative`로 진입한다.
2. 슬라이스 단위 build contract, fixed/probe/deferred, success criteria,
   acceptance checks, executable spec cost는 `spec`으로 진입한다.
3. 실행 가능한 substrate 본체(syntax, report, adapter, filter, focused
   iteration)는 `support/specdown`로 진입한다(또는 다른 substrate가 선택되면
   그 자리에 자리를 비워둔다).

## Anti-Goals

- Cautilus product 어휘를 일반 charness 작가 디시플린으로 굳히지 않는다.
  "ScenarioPacket", "EvaluationInput" 같은 product-local 개념이 본 디시플린의
  공유 어휘로 새어 들어오면 portability가 깨진다.
- 새로운 top-level 공개 스킬(예: `top-spec`, `domain-spec`)을 신설하지 않는다.
  이미 있는 세 표면의 owner 분포가 우선이다.
- specdown을 "공식 substrate"로 강제하지 않는다. 디시플린은 substrate-agnostic
  해야 하고 specdown은 example-of-substrate일 뿐이다.
- 단일 reference 파일에 user/maintainer/cross-concern 작성법을 모두 욱여넣지
  않는다. 그것이 가능하다면 split 권고 자체가 필요하지 않다.
- `narrative` brief과 maintainer proof map을 같은 lifecycle artifact로 합치지
  않는다. 각각 다른 reader-fit과 freshness 정책을 가진다.
- HITL 미성숙 단계의 Cautilus 드래프트에서 "패턴"을 즉흥적으로 추출하지 않는다.

## Evidence Required To Move From Design To Implementation

본 spec은 다음 증거가 동시에 모이기 전에는 implementation 패스로 넘어가지
않는다.

1. **Cautilus rework re-enable**. root adapter `run_mode`가 `disabled`에서
   다른 mode로 바뀌었고 [charness-artifacts/cautilus/latest.md](../cautilus/latest.md)
   가 그 상태를 반영한다.
2. **Cautilus user/maintainer spec HITL maturity**. 이슈 본문이 요구한 대로
   user-facing index와 maintainer proof map이 충분한 HITL 통과를 거쳤다.
   증거는 Cautilus 측 HITL artifact의 reviewed 상태로 본다.
3. **Charness narrative의 첫 dogfood result**. narrative `v0.5.0` 이후 다른
   레포에서의 dogfood가 misses를 issue로 모은 다음, 그 misses 중 본 디시플린이
   닫아주는 것이 있는지 확인한다 (handoff next-session 28번 항목).
4. **두 번째 substrate 후보 관찰**. specdown 외 substrate(예: 다른 executable
   spec runner) 후보가 실 사용 사례로 1회 이상 등장하면, substrate-agnostic
   layer 분포가 이론이 아니라 관측된 필요가 된다. 후보가 없으면 specdown
   single-substrate 가정이 안전하다.
5. **본 spec의 split 권고에 대한 fresh-eye review**. layer 진입 규칙이
   reader-fit 한지, edge case가 있는지 명시 검토.

3개 이상이 모이면 implementation 패스로 진행한다. 그 전 단계에서 이슈가
재오픈되면 본 spec을 입력으로 다시 사용한다.

## Probe Questions

- Q1. specdown 외 substrate가 실제로 등장했을 때, support skill 자리를 비워두는
  방식 vs. substrate-neutral reference를 `spec` 안에 두는 방식 중 어느 쪽이
  long-term 유지비가 작은가? 본 패스에서는 결정하지 않는다.
- Q2. user-facing 스토리와 maintainer proof map이 같은 디렉토리에 살되 다른
  freshness 정책을 가지는 패턴이 portable 한가, 아니면 문서 별 별도
  freshness validator가 필요한가? 후속 dogfood로 본다.
- Q3. cross-concern visibility를 "한 페이지에 같이 보이게"로 정의할지 "concern
  별 view를 자동 생성"으로 정의할지는 implementation 패스의 결정.

## Deferred Decisions

- 어휘 정렬을 강제하는 lint/validator(예: 같은 도메인 단어가 prose, packet,
  CLI output, 테스트, 어댑터, 스킬에서 동일하게 쓰이는지) 도입 여부.
- maintainer proof map의 권고 디렉토리 구조 표준(`docs/specs/maintainer/` 같은
  레이아웃)을 charness 권고로 굳힐지 여부.
- specdown 외 substrate에 대한 1차 호환 가이드의 owner.

## Non-Goals

- 새 공개 스킬 신설.
- 임의 consumer 레포의 spec 디렉토리 구조 강제.
- specdown CLI/syntax 변경 권고.
- Cautilus product 정의 변경.
- README/landing 문서의 의무화된 새 섹션.
- 스킬 본문 prose 변경.

## Deliberately Not Doing (거부된 대안과 이유)

- **Cautilus 현재 드래프트 기반 일반화.** HITL 미성숙 상태에서 "패턴"을 뽑으면
  product-local 결정이 일반 권고로 굳어 portability를 깬다(이슈 본문 가드).
- **`narrative` 또는 `spec` 단독 owner 권고.** 각 스킬의 본업 어휘를 흐린다
  (Option A/B Cons 참조).
- **새 top-level 공개 스킬 신설.** 분포는 owner를 늘리는 것보다 layer 진입
  규칙으로 푸는 것이 portable.
- **본 패스에서 reference/SKILL 본문 수정.** Cautilus gating 위반.

## Constraints

- 산출물은 본 한 파일이다. 다른 generated 표면을 건드리지 않는다.
- Cautilus binary, Cautilus eval, Cautilus 드래프트 인용을 금한다.
- 본 spec은 design extraction이라 acceptance check가 "fresh-eye가 layer
  분포를 한 번에 이해하는가"로 충분하다. executable check는 implementation
  패스에서 도입한다.

## Success Criteria

1. 본 spec이 narrative-only / spec-only / split 세 옵션을 명시 비교한다.
2. split 권고에 대한 layer 진입 규칙 3개가 본 spec 본문에 명시된다.
3. anti-goals가 portability 보호 관점으로 6개 이상 명시된다.
4. design→implementation 이행 증거 5개 중 3개 이상 모이기 전 implementation
   패스로 넘어가지 않는다는 게이트가 본 spec에 있다.
5. 스킬 본문, reference, plugin export 어디에도 본 spec이 강제하는 prose가
   landing되지 않는다.

## Acceptance Checks

- A1: `rg -n "Option A|Option B|Option C" charness-artifacts/spec/issue-109-spec-authoring-discipline.md`
  가 세 옵션을 식별한다.
- A2: `rg -n "Layer 진입 규칙" charness-artifacts/spec/issue-109-spec-authoring-discipline.md`
  이 규칙 섹션을 찾고, 그 아래에 1~3 번호 항목이 있다.
- A3: `rg -n "Anti-Goals|Cautilus" charness-artifacts/spec/issue-109-spec-authoring-discipline.md`
  이 anti-goal 섹션과 Cautilus gating 언급을 찾는다.
- A4: `git diff --name-only origin/main` (또는 PR 변경 파일 목록)이 `skills/`,
  `docs/`, `plugins/charness/skills/` 본문 prose 파일을 포함하지 않는다
  (find-skills support-consumption.md의 #108 분리 변경은 별도 spec scope이며
  본 spec의 가드와 충돌하지 않는다).
- A5: 본 spec의 "Evidence Required" 섹션이 5개 항목과 "3개 이상" 게이트를
  명시한다.

## Critique (bounded, inline)

5분 fresh reviewer가 본 spec을 보고 범하기 쉬운 오독:

- **P1. "Option C가 결정됐으니 곧장 스킬 본문을 분배해도 된다"**. 본 spec은
  명확히 design extraction 한정이다. Fixed Decisions와 Constraints에서
  "스킬 본문 prose 변경 금지"를 박아둔다. Acceptance check A4가 이를 강제한다.
- **P2. "Cautilus 드래프트를 입력으로 추출하면 빠르다"**. Cautilus gating은
  이슈 본문의 명시 요구다. Anti-Goals와 Evidence Required 1·2번이 이를
  강제한다.
- **P3. "split이 portable하지 않다 — substrate가 바뀌면 무너진다"**.
  Anti-Goals가 substrate-agnostic 디시플린을 명시한다. Evidence Required 4번이
  두 번째 substrate 후보를 게이트로 둔다.
- **P4. "narrative와 spec이 같은 작가 디시플린을 따로 들고 있으면 둘이 어긋난다"**.
  본 패스의 산출은 디시플린 정의가 아니라 layer 진입 규칙이다.
  implementation 패스에서 layer 간 cross-reference를 명시하도록 Probe
  Questions Q1–Q3에 남겨둔다.
- **P5. "본 spec 자체가 implementation 시도다"**. 본 spec은 charness-artifacts
  하위 한 파일이며, 공개 스킬 표면에 진입하지 않는다. Success Criteria 5번과
  Acceptance Check A4가 이를 강제한다.

Critique 결과 tighten 항목:

- Acceptance Check A4를 "본 spec이 강제하는 prose가 다른 표면에 landing되지
  않는다"로 명시화 (P1, P5).
- Evidence Required에 "3개 이상" 정량 게이트를 명시 (P2).
- Probe Question Q1을 substrate-agnostic 모호성을 다루도록 유지 (P3).

본 패스는 문서 한정·가역적이며 영향이 design 의사결정 reader로 제한된다.
독립 `critique` 스킬 호출은 implementation 패스에서 실제 owner 분포가
landing할 때 사용한다.

## Canonical Artifact

[charness-artifacts/spec/issue-109-spec-authoring-discipline.md](./issue-109-spec-authoring-discipline.md)
(본 문서). implementation 패스는 본 spec의 Layer 진입 규칙, Anti-Goals,
Evidence Required, Probe Questions를 입력으로 다시 사용한다.

## First Implementation Slice

implementation 패스는 본 spec이 정의한 Evidence Required 게이트가 통과한
후에만 시작한다. 게이트 통과 시 첫 슬라이스 후보:

1. `narrative`에 짧은 reference: user-facing 스토리, 공유 어휘, cross-concern
   가시성에 대한 layer-level 권고. landing-rewrite-loop와 충돌하지 않는 한
   문장.
2. `spec`에 짧은 reference 또는 acceptance-checks/contract-modes 확장:
   maintainer proof map, evidence placement 권고. 기존 acceptance-checks.md /
   executable-spec-cost.md / contract-modes.md를 owner로 재사용.
3. `support/specdown`은 그대로. substrate-specific 본문은 이미 owner이며,
   layer 진입 규칙은 specdown 본문에 prose로 옮길 필요가 없다(triggers와
   references가 이미 routing함).
4. cross-skill validator(예: 같은 도메인 단어 정렬)은 본 슬라이스에 포함하지
   않는다. Probe Q1·Q2 결과를 보고 결정.
5. 첫 dogfood: charness 자체 도메인을 한 번 통과시킨다(meta-dogfood). 그
   다음에야 외부 consumer repo로 옮긴다.

## References

- 이슈 본문: https://github.com/corca-ai/charness/issues/109
- 이슈 #108(인접): https://github.com/corca-ai/charness/issues/108
- [docs/handoff.md](../../docs/handoff.md) (Cautilus disabled 상태 추적)
- [.agents/cautilus-adapter.yaml](../../.agents/cautilus-adapter.yaml) (`run_mode: disabled`)
- [skills/public/narrative/SKILL.md](../../skills/public/narrative/SKILL.md)
- [skills/public/spec/SKILL.md](../../skills/public/spec/SKILL.md)
- [skills/public/spec/references/acceptance-checks.md](../../skills/public/spec/references/acceptance-checks.md)
- [skills/public/spec/references/executable-spec-cost.md](../../skills/public/spec/references/executable-spec-cost.md)
- [skills/public/spec/references/contract-modes.md](../../skills/public/spec/references/contract-modes.md)
- [skills/support/specdown/SKILL.md](../../skills/support/specdown/SKILL.md)
- [skills/public/find-skills/references/support-consumption.md](../../skills/public/find-skills/references/support-consumption.md) (issue #108 closeout)
