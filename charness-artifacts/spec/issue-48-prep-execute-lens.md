# Spec: Issue #48 (a) — agent-facing CLI의 prep/execute 아티팩트 분리 렌즈

Source: https://github.com/corca-ai/charness/issues/48 + 검토 코멘트
(https://github.com/corca-ai/charness/issues/48#issuecomment-4285127405)

이 spec은 이슈 #48의 (a) 스코프(= agent-facing CLI 설계 렌즈 추가)에만
집중한다. (b) 크로스-레포 이슈 작성 원칙의 홈 결정은 본 spec의 명시적
non-goal이며, 별도 이슈로 분리한다.

## Problem

공개 charness 가이드(`impl`, `create-cli`)에는 agent-facing CLI 표면을 설계할
때 "하나의 두꺼운 명령 vs prep/execute 아티팩트 분리"를 결정하라는 명시적
렌즈가 없다.

현재 가이드의 커버리지:

- `impl/references/design-lenses.md`: Beck/Ousterhout 기반 **슬라이스 규율**
  렌즈만 있음. 명령 표면 **형상**에 대한 결정 지원 없음.
- `create-cli/references/command-surface.md`: agent-facing rule 섹션이 있으나
  `--json` 안정성, probe layer 분리, task-envelope 정도에 머무름. 워크플로우
  명령을 "하나로 둘지 prep+execute로 쪼갤지"에 대한 결정 질문이 없음.
- `create-cli/references/case-studies.md`: `charness`, `agent-browser`,
  `specdown`, `cautilus`의 install/update/lifecycle 사례만 기록. 워크플로우
  명령의 prep/execute 분리 사례 없음.

그 결과 반복되는 실패 모드:

1. 공개 명령 하나가 selection + expansion + execution + policy를 모두
   떠안는다. agent가 단계별로 inspect/diff/subset/retry할 수 없다.
2. 또는 선택/확장 로직이 host-side wrapper로 새어 나가 host마다 다르게
   복제된다. 제품 경계가 흐려진다.

관찰 사례 (이슈 본문):
`cautilus workbench prepare-request-batch -> run-scenarios`가 단일 두꺼운
명령보다 훨씬 agent-orchestration-friendly했다. 그러나 charness 공개 가이드는
이 패턴을 첫 원칙으로 가르치지 않는다.

## Current Slice

`create-cli`를 **1차 배치**로, `impl`을 **crossref**로 다음을 추가한다.

1. `skills/public/create-cli/references/command-surface.md`의 Agent-facing
   rule 섹션 확장:
   - prep/execute 분리 결정을 **선택 4개 질문**으로 추가 (선언형 처방 아님)
   - 과적용 안티패턴 섹션 추가 (동일 파일 내)
2. `skills/public/create-cli/references/case-studies.md`에 `cautilus workbench
   prepare-request-batch -> run-scenarios` 사례 + design takeaway 추가
3. `skills/public/create-cli/SKILL.md`의 Workflow 2 ("Shape the command
   surface") 체크리스트에 prep/execute 결정 항목 한 줄 추가
4. `skills/public/impl/references/design-lenses.md` 말미에 "interface 형상
   문제라면 create-cli로" crossref 한 줄

## Fixed Decisions

- **1차 배치는 `create-cli`.** 이유: 본 렌즈는 명령 표면 **형상** 결정이며,
  표면이 그려지는 시점이 `create-cli`의 Workflow 2이다. `impl`은 슬라이스
  규율(어떻게 쪼개 구현할지)이 주 관심사라 결정이 늦게 호출된다.
- **`impl`은 crossref만.** 별도 섹션 신설하지 않는다.
- **새 reference 파일을 만들지 않는다.** 추가 콘텐츠(질문 4 + 안티패턴 3 + case
  study 1)가 기존 `command-surface.md`와 `case-studies.md` 확장으로 소화된다.
  신규 파일 유지비 > 콘텐츠 가치.
- **선언형 처방이 아니라 결정 질문으로 작성한다.** 이슈 댓글의 "why/what > how"
  원칙을 공개 가이드 문안 자체가 보여주도록.
- **스코프는 agent-facing surface에 한정.** human-first CLI 전반에 적용되는
  기본값이 아님을 명시한다.
- **(b)는 본 spec의 non-goal.** 별도 이슈로 분리한다.

## Probe Questions

- Q1. 안티패턴을 `command-surface.md` 내부에 녹일지, `anti-patterns.md` 같은
  신규 reference로 뺄지?
  - 현재 기본값: `command-surface.md` 내부에 짧게. 1페이지짜리 독립 reference로
    뗄 만큼 크지 않음.
  - 추후 임계: 안티패턴 항목이 6개를 넘거나 다른 스킬에서 reference할 필요가
    생기면 뗀다.
- Q2. `SKILL.md`에 체크리스트 한 줄을 올릴지, reference에만 둘지?
  - 현재 기본값: SKILL.md Workflow 2에 한 줄 + reference 본문 상세.
  - 이유: SKILL.md의 Workflow는 operator 점검 지점이라 질문 유도가 필요한
    지점이 있어야 실제 결정이 빠지지 않음.
- Q3. `impl/references/design-lenses.md`의 crossref가 한 줄로 충분한가, 아니면
  "Command Surface" 전용 소섹션을 개설할 만한가?
  - 현재 기본값: 한 줄. Beck/Ousterhout 렌즈와 결이 달라 섞어 두면 도메인
    구분이 흐려진다.
  - 추후 임계: impl 슬라이스에서 명령 표면 형상 결정이 반복적으로 슬라이스를
    얼어붙게 만들면 별도 섹션.

## Deferred Decisions

- prep/execute 렌즈를 `ideation`, `spec` 상류 단계에도 이식할지 — 현재는 아님.
  제품 surface가 굳기 전 개념 단계에서는 결정이 너무 이르다. `create-cli` 도입
  이후 피드백 보고 판단.
- 일반(non-agent-facing) CLI에도 권하는 수준으로 범위 확장할지 — 현재는 agent
  surface에 한정. 인간 운영자만 쓰는 CLI에서는 오히려 두 단계 강제가 마찰.
- case study로 `cautilus` 외 사례를 더 수집할지 — 필요해지면 추가, 선제적
  수집은 하지 않음.

## Non-Goals

- (b) 크로스-레포 이슈 작성 원칙(`why/what > how`)의 배치
- 신규 top-level 공개 스킬(예: `design-agent-surface`) 신설
- `create-skill`, `ideation`, `spec`, `narrative` 등 인접 스킬 변경
- 실제 `cautilus` 레포의 workbench 명령 표면 수정
- `docs/artifact-policy.md` 변경 (아티팩트 저장 위치 정책은 이미 충분)

## Deliberately Not Doing (거부된 대안과 이유)

- **1차 배치를 `impl`로**: 슬라이스 규율과 명령 표면 형상은 다른 축. 결정이
  필요한 시점은 `create-cli`의 Workflow 2이며, `impl`에 배치하면 실제 결정
  시점에서 읽히지 않음. 이슈 본문의 "likely impl and possibly create-cli"
  순서는 뒤집는 것이 자연스럽다.
- **신규 reference 파일 `agent-surface-split.md` 신설**: 현 콘텐츠는 기존
  두 파일 확장으로 충분. 파일을 분할하는 순간 유지비와 crossref 관리 비용이
  생기며, 현 수준에서는 오버킬.
- **선언형 bullet 그대로 채택** (이슈 본문 Candidate direction 4개): 이슈
  댓글 자체가 "why/what > how" 원칙을 말했고, 공개 가이드는 결정 렌즈로
  기능해야 한다. 질문 형식이 다양한 제품 맥락에서 더 robust.
- **`ideation`/`spec` 상류에 먼저 이식**: 표면 형상 결정이 개념 단계에 들어오면
  concept이 굳기도 전에 surface가 고착된다. 굳이 상류로 끌어올릴 필요 없음.
- **prep/execute 분리를 default로 강제**: human-first CLI에서는 단일 명령이
  보통 낫다. default가 아니라 렌즈여야 한다.

## Constraints

- 기존 `command-surface.md` 톤 유지 (짧은 불릿, 한 줄 규칙)
- SKILL.md 체크리스트 문구는 기존 bullet 형식과 동일 패턴
- 추가 콘텐츠가 기존 bullet과 중복되지 않아야 함 (`--json` 안정성, probe layer
  분리는 이미 있음 — 반복 금지)
- `impl/references/design-lenses.md`의 Beck/Ousterhout 섹션은 손대지 않고
  말미 crossref 한 줄만 추가
- 문서 변경만. 코드/스크립트/스키마 수정 없음
- case study 문장은 `cautilus` 실제 명령 이름 그대로 인용 (발명 금지)

## Success Criteria

1. `create-cli/references/command-surface.md`의 Agent-facing rule 섹션에
   prep/execute 결정을 묻는 **질문 4개**가 추가되어 있다.
2. 동일 파일에 prep/execute 과적용 실패 모드(안티패턴) **3개 이상**이
   명시되어 있다.
3. `create-cli/references/case-studies.md`에 `cautilus workbench
   prepare-request-batch -> run-scenarios` 사례가 design takeaway와 함께
   추가되어 있다.
4. `create-cli/SKILL.md` Workflow 2에 prep/execute 결정 체크 한 줄이 있다.
5. `impl/references/design-lenses.md`에 "명령 표면 형상 문제는 create-cli로"
   crossref 한 줄이 있다.
6. (b) 크로스-레포 이슈 작성 원칙을 다루는 별도 issue가 charness 레포에
   열려 있고, 본 이슈 #48에는 "(b)는 분리 이슈로 이관" 상태 코멘트가 남아
   있다.

## Acceptance Checks

- **A1**: `rg -n "prep|execute|prepare" skills/public/create-cli/references/command-surface.md`
  결과에서 결정 질문 4개 bullet을 식별할 수 있다.
- **A2**: 같은 파일에서 안티패턴 섹션의 항목을 `rg -n "anti-pattern|over-|unnecessary"`로
  3개 이상 식별할 수 있다.
- **A3**: `rg -n "prepare-request-batch|run-scenarios" skills/public/create-cli/references/case-studies.md`
  가 cautilus 사례 블록을 찾는다.
- **A4**: `rg -n "prep|execute|artifact split" skills/public/create-cli/SKILL.md`
  가 Workflow 2 체크리스트 한 줄을 찾는다.
- **A5**: `rg -n "create-cli" skills/public/impl/references/design-lenses.md`
  가 crossref를 찾는다.
- **A6**: `gh issue list --repo corca-ai/charness --search "cross-repo issue hygiene"`
  또는 동등한 쿼리로 (b) 분리 이슈를 찾을 수 있다.
- **A7**: 본 레포의 기존 `command-docs drift` gate(존재 시)가 이 문서 변경에서
  통과한다. 해당 gate가 본 문서를 대상으로 하지 않으면 면제 처리한다.
- **A8 (Negative)**: prep/execute 렌즈가 "human-first CLI의 default"로
  잘못 읽히지 않도록, agent-facing 한정임을 문서에서 `rg -n "agent-facing"`으로
  확인 가능해야 한다.

## Premortem (bounded, inline)

5분 fresh reviewer/implementer가 본 spec을 보고 범하기 쉬운 오독:

- **P1. 렌즈를 일반 CLI default로 오해**: agent-facing 한정임을 섹션
  첫 문장에 박고, 안티패턴에 "human-first CLI에서는 단일 명령이 보통 낫다"를
  반대 사례로 포함시킨다. A8이 이것을 강제한다.
- **P2. "prep은 반드시 별도 subcommand여야 하나, 같은 명령의 단계 옵션으로도
  되는가?"**: 결정 질문 중 하나가 "아티팩트 경계가 명령 경계보다 더 안정적인
  계약인가?"를 묻게 한다. case study는 두 개의 명령 사례로 구체를 제공한다.
  문안에 "분리는 subcommand 분리 또는 별도 binary 분리 모두 허용"을 명시.
- **P3. 안티패턴이 추상적이라 유도 효과 없음**: 각 안티패턴에 한 줄짜리 실물
  시나리오를 붙인다. 예: "단일 호출이 멱등하고 10초 내 끝나는데 중간 아티팩트를
  강제하면 상태 소스가 3개로 늘어난다."
- **P4. impl crossref 한 줄이 너무 작아 안 읽힘**: `impl/SKILL.md`의 References
  목록에 `design-lenses.md`는 이미 있어서 경로는 유지된다. 대안은 나중에
  "Command Surface" 소섹션을 design-lenses에 신설하는 것. Probe Q3으로
  남긴다.
- **P5. 수용 기준이 "파일에 글자가 있다" 수준으로 얕음**: A1–A5가 존재
  증거이고, A8이 의미 증거를 잡는다. 추가로 impl 단계에서 "fresh reader가
  질문을 통해 실제로 하나의 결정을 내릴 수 있는가"를 review-gate 통과 조건으로
  둔다. 이 검증은 `impl` review-gate의 "boundary honesty" 렌즈로 자연
  포섭된다.

Premortem 결과 tighten 항목:

- 안티패턴에 "human-first CLI에서는 단일 명령이 보통 낫다"를 포함 (P1)
- 결정 질문에 "아티팩트 경계가 명령 경계보다 안정적인 계약인가?"를 포함 (P2)
- 각 안티패턴에 한 줄 실물 시나리오 부착 (P3)

Bounded premortem으로 충분한 근거: 본 변경은 문서 한정·가역적이며, 영향이
공개 가이드 reader로 제한된다. standalone `premortem` 스킬은 deletion/rename,
breaking, runtime behavior 변경에 예약한다. impl 단계에서 cross-surface 마찰이
발견되면 그 시점에 호출한다.

## Canonical Artifact

`charness-artifacts/spec/issue-48-prep-execute-lens.md` (본 문서). impl은
본 spec의 Success Criteria와 Acceptance Checks를 재읽기 closeout 기준으로
사용한다.

## First Implementation Slice

단일 슬라이스로 묶어 진행:

1. `skills/public/create-cli/references/command-surface.md`
   - Agent-facing rule 섹션 끝에 "Prep/execute split decision" 소블록 추가:
     결정 질문 4개 + 안티패턴 3개 (각 한 줄 실물 시나리오 부착)
   - 첫 문장에 "agent-facing workflow commands" 스코프 고정
2. `skills/public/create-cli/references/case-studies.md`
   - `cautilus` 기존 블록 아래에 `cautilus workbench prepare-request-batch
     -> run-scenarios` workflow 사례 추가 + design takeaway
3. `skills/public/create-cli/SKILL.md`
   - Workflow 2 ("Shape the command surface") 체크리스트에 한 줄 추가:
     "prep/execute 분리가 필요한 agent-facing workflow인지 명시적으로 결정"
4. `skills/public/impl/references/design-lenses.md`
   - Translation For Impl 말미에 한 줄 crossref 추가:
     "명령 표면 형상 문제는 `create-cli/references/command-surface.md`
     Prep/execute split section 참조"

Verification: A1–A5 + A8을 `rg`로 기계적으로 확인. command-docs drift gate가
있으면 재렌더 확인(A7).

Closeout 후속:

- (b) 크로스-레포 이슈 작성 원칙 배치 probe를 별도 이슈로 생성 (A6).
- 본 이슈 #48에 "(b)는 분리 이슈로 이관, #?? 참조" 코멘트 남김.
