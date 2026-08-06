## Source

- Source origin: github
- Source identity: https://github.com/corca-ai/cmanki/blob/main/charness-artifacts/debug/2026-08-06-debug-review.md
- gathered: charness-artifacts/gather/2026-08-06-cmanki-debug-review-517.md
- access: binary (authenticated gh)
- freshness: 2026-08-06; blob read from main
- Source preservation: source-text
- Source text: authenticated GitHub Contents API read; canonical blob SHA f4a2f76795ccd0eec62f82641b37a5b2be35e8bf; public/raw fetch routes returned HTTP 404 in this environment.

## Knowledge Capability

Preserve the cmanki debug review needed to assess Charness issue #517 semantic surface-contract proof gaps.

## Route / Selected Attempt

- Selected: GitHub Contents API via authenticated gh read.
- Public URL helper: canonical blob and raw URL both returned HTTP 404; no public substitution was accepted.
- Content persistence: extracted Markdown source text.

## Captured Content


# Debug Review — 피드백 수리 후속 UI 의미·상태·기하 누락
Date: 2026-08-06

## Problem

배포 화면에서 소식 N의 좌표계·날짜 중복, 그래프 줌 문구·disclosure 정렬·열림 충돌·줌 값·50% 라벨
겹침, 공부법 가로 overflow·제목 중복, 복습 앞뒤 중복·세션 상세 과다, `두 단계 연결 오답 판정`과
  `직접 연결 판정`의 답 누설, 카드 제거 때 목록 시프트, 양끝 공백 정리를 수동 명령으로 둔 점,
  `편집`을 열어도 현재 줄 번호와 삭제 한 명령만 보이는 점이 발견됐다. 소식·공부법은 같은 외곽 스타일인데
  수정 이력·피드백·동기화는 각각 달랐고, 비밀번호 변경도 동기화에 있었다. 피드백 POST 뒤 목록
  요청이 끝나기 전에 작성 내용이 사라지는 현상도 관찰됐다. 질문은 “이번 패턴으로
미리 스캔했다면 잡혔는가? 아니라면 왜인가?”다.

## Correct Behavior

- 소식 N은 버튼의 좌표계에 붙고 충돌하지 않는다. literal `fixed`는 모바일 fixed 금지 계약과 충돌하므로 예외 여부를 확정한다.
- 그래프는 중복 문구 없이 compact하고 disclosure 아이콘은 중앙이며, 열린 목록·줌 도구·50% label은 겹치지 않는다. 줌은 선언된 집합을 따른다.
- 공부법은 좁은 viewport에서 가로 overflow가 없고 제목·부제·Markdown 본문 중 한 owner만 같은
  정보를 렌더링한다. 소식은 날짜를 반복하지 않는다. 버전 ID가 날짜를 표현하므로 버전명·제목만 쓴다.
- 보조 페이지는 공통 shell(폭·여백·제목·notice/card 표면)을 공유하고 내용 모듈만 개별 스타일을
  갖는다. 수정 이력·동기화는 문서 상태의 한 화면 두 섹션으로 묶을 수 있다.
- 비밀번호 변경과 세션 잠금은 동기화가 아니라 사람/계정 설정이 소유한다. 복습은 한 번에 한 카드가
  같은 주 위치에 들어오며, pre-answer metadata는 정답·오답·연결 여부를 누설하지 않는다.
- 양끝 공백은 파서가 의미로 쓰지 않는 입력 경계의 정규화 대상이다. 매 키 입력이 아니라 blur/저장 같은
  안정된 경계에서 자동 정리하고, 한 번의 undo 단위로 남긴다. `편집`은 현재 줄 번호만이 아니라 실제
  줄 내용·작용 범위·결과를 보여주는 contextual surface여야 한다.

## Observed Facts

- `src/App.svelte:1664-1679`의 `.news-link { position: relative }`와 `.new-badge { position: absolute }`가
  N을 링크 containing block에 둔다. `scripts/ui-check.mjs:338-353`는 앱 전체 `position: fixed`를 금지한다.
- `src/lib/Graph.svelte:177-182`가 `관계 라벨 표시/숨김`을 줌 그룹에 항상 넣는다. summary에 직접적인
  `align-items:center`가 없고, 열린 `.relation-usage`는 absolute다(`Graph.svelte:289-325`). 검사는
  목록이 summary 아래이고 줌 도구가 밀리지 않는지만 보며 서로의 rect 교차·아이콘 baseline은 보지 않는다.
- `Graph.svelte:20-54`의 `ZOOM_STEP=.2` 덧셈은 50 → 70 → 90 → 110을 만든다. “110이 될 수 없다”가
  금지 뜻이라면 허용 집합이 먼저 필요하다. 50% 검사는 글자 높이만 보고 pairwise collision은 보지 않는다.
- `StudyGuide.svelte:18-25`의 eyebrow·h1과 `docs/concept-map-study-method.md:1`의 첫 h1이 중복된다.
  content에는 overflow-wrap만 있고 실제 `scrollWidth` 검사가 없다(`StudyGuide.svelte:38-49`).
- `NewsPage.svelte:57,86-88`는 `note.id`와 `publishedAt`을 함께 표시한다. ID 규칙은 `v<YYYYMMDD>.<순번>`
  이다(`docs/release-notes.md:8-12`). 날짜의 두 projection이 중복된다.
- `ReviewPanel.svelte:80-96,199-205`는 reveal한 답을 front와 `.back`에 함께 렌더링한다. `cards.ts:137-140`의
  `직접 연결 판정`·`두 단계 연결 오답 판정`은 reveal 전에 상단에 노출된다. 후자는 오답을, 전자는 직접
  연결을 알려준다. 기존 검사는 답 presence와 카드 종류만 본다.
- `ReviewPanel.svelte:132-150`은 세션 상세 전체를 즉시 렌더링한다. `ReviewPanel.svelte:207-239`는 cards
  전체를 `<ul>`로 그리고 채점 뒤 due 배열에서 한 항목을 제거한다. 기존 `dueAfter === dueBefore - 1`
  (`scripts/ui-check.mjs:614-621`)은 목록 모델만 보증하고 stable primary card rect는 보증하지 않는다.
- `NewsPage.svelte:98`·`StudyGuide.svelte:34`만 같은 `48rem` frame을 직접 정의한다. History·Feedback·Sync는
  각자 외곽을 정의하며 공통 shell 검사가 없다. `.sidebar-close`는 display만 지정되어 브라우저 기본
  버튼 border가 남는다. Sync에는 password change와 `잠그기`가 함께 있다(`Sync.svelte:304-377`).
- `Editor.svelte:110-118`의 양끝 공백 정리는 명시적 버튼으로만 실행되고, `App.svelte:1209-1213`의
  `편집` 패널은 `현재 줄 N행`과 `현재 줄 지우기`만 보여준다. 현재 줄의 텍스트나 삭제 범위는 없다.
- `Feedback.svelte:217-232`는 `submitFeedback()` 응답을 버리고, POST 직후 `draft`·첨부를 지운 뒤
  `listFeedback()`을 다시 기다린다. 따라서 두 번째 요청이 느리거나 멈추면 `pendingAction === 'submit'`
  인 동안 작성 내용은 없어지고 목록 projection은 먼저 나타난다. submit에는 route 이동 호출이 없다.

## Reproduction

- 390px에서 graph 50%·disclosure open의 `getBoundingClientRect()` 교차와 icon baseline을 읽는다.
- StudyGuide의 horizontal overflow·heading count, News의 version/date count를 읽는다.
- Review reveal의 front/back·pre-answer text, session detail visibility, 채점 전후 주 카드 rect를 비교한다.
- 다섯 보조 페이지의 frame·padding·heading·notice rect와 sidebar-close computed border를 비교한다.

## Candidate Causes

- 사용자 의도를 CSS keyword·DOM 존재·필드 존재로 축소한 계약 압축.
- 열림/닫힘·50%·reveal·좁은 viewport·primary interaction을 빠뜨린 상태×viewport 표.
- Markdown source/shell, card type/label/question, version/date의 이중 owner.
- geometry·설명 과잉·공통 shell 패턴을 sibling 전체에 전파하지 않음.
- 복습을 주 카드가 아니라 제거되는 데이터 목록으로 모델링하고, 계정/세션을 Sync에 넣음.
- 비의미적 whitespace를 cleanup command로 승격하고, 편집 command의 context projection을 생략함.
- mutation 성공과 목록 readback을 하나의 완료 상태로 뭉개고, 서버가 반환한 생성 thread를 버림.

## Hypothesis

- 주 가설: 기존 6축(surface 의미·owner·projection·시간·실패·proof) 스캔이 선언 수준에 머물고
  state transition × coordinate system × content density × interaction model로 내려가지 않았다.
  disconfirmer: 실제 브라우저에서 기존 assertion은 통과하면서 duplicate/overlap/overflow/shift가
  관찰되는 것이다.
- 보조 가설: `absolute`, “목록이 보임”, “답이 있음” 같은 구현 증명이 사용자 의미를 덮어썼다.
  assertion과 사용자의 fixed/접힘/단일 표시를 대조하면 판정한다.

## Verification

- Producer Proof: current source locations, `npm run ui` 249/249, `CMANKI_SYNC_PORT=8797 npm run sync-check` 106/106,
  and the explicit selector collision reproduction above are the evidence for this record.
- confirmed — N absolute, session list visible, reveal answer presence만 성공으로 정의되며 disclosure
  교차·50% collision·horizontal overflow·heading uniqueness·exactly-once를 보지 않는다.
- confirmed — card label이 pre-answer surface에 노출되어 연결 여부와 오답을 알려준다.
- confirmed — News가 날짜 ID와 publishedAt을 이중 렌더링하고, Review가 전체 목록을 제거한다.
- confirmed — 보조 페이지 outer shell과 `.sidebar-close` 표면, 계정 action owner를 비교하는 검사가 없다.
- confirmed — whitespace 자동 정규화와 편집 패널의 line-context/operation scope를 검증하는 계약이 없다.
- confirmed — 피드백 submit은 POST 성공과 list readback 사이에 draft projection을 먼저 지운다. 기존 UI
  검사는 버튼의 `보내는 중..`과 최종 목록만 따로 보며, pending 중 draft 보존·중복 제출 방지를 보지 않는다.
- still-candidate — 110을 허용할지, history/sync를 한 페이지의 sections로 할지는 수리 전 계약 결정이다.

## Root Cause

바닥 원인은 패턴의 부재가 아니라 **executable contract로 승격하는 단위가 얕았던 것**이다. surface
명사는 검사했지만 상태·좌표계·콘텐츠 owner·primary interaction이 결합한 관계는 검사하지 않았다.

반례는 다섯 종류다. N은 의미를 `absolute`로 잘못 고정한 contract, 그래프는 state matrix·pairwise
geometry 누락, 도움말/복습은 single owner 누락, 소식은 날짜 projection 중복, 복습은 answer-bearing
metadata와 목록 기반 layout shift다. 더 위에는 공통 utility shell과 account owner 부재가 있다.
answer leakage는 “회상 기회를 뺏지 않는다”를 직접 깨는 BLOCKER다.

## Invariant Proof

- Invariant: PASS requires the browser surface to prove each state meaning, geometry, duplication,
  overflow, and interaction-stability claim directly; source strings and single presence assertions
  are insufficient.
- Producer Proof: source locations, UI 249/249, sync 106/106, and the selector collision reproduction.
- Final-Consumer Proof: browser probes consume visible label, active-state, hit-area, async, and selector semantics.
- Interface-Shape Sibling Scan: source, labels, Playwright helpers, UI/sync probes, and docs were compared.
- Non-Claims: no public deploy, real-device timing, or unresolved future graph/review/account design is claimed.
- PASS는 각 상태의 의미·geometry·중복·overflow·interaction stability를 브라우저 surface가 직접 증명해야
  하며 source 문자열·단일 presence assertion으로 닫지 않는다.
- 현재 source와 `scripts/ui-check.mjs`가 불완전한 assertion을 생산한다. `npm run check:ui-contract`가
  통과해도 final browser/public 화면을 대표한다는 주장은 하지 않는다.
- Graph/StudyGuide/News/History/Feedback/Sync/Review와 N·sidebar-close를 같은 projection/shell
  sibling으로 비교했다. 실제 iOS fixed 좌표계와 최신 public asset은 이번 진단에서 재측정하지 않았다.

## Detection Gap

- UI static check가 fixed/absolute의 의미·heading owner·duplicate policy·shell geometry를 모른다.
- Graph check가 open disclosure와 zoom controls의 rect 교차·icon baseline·50% pairwise collision을 모른다.
- Zoom check가 min/max과 한 step만 보며 선언된 허용값 sequence를 sweep하지 않는다.
- Help/News check가 vertical scroll·Markdown presence를 보며 horizontal overflow·heading/date uniqueness를
  보지 않는다.
- Review check가 answer presence·list visible을 보며 pre-answer leakage·exactly-once·collapsed default·
  one-card stable rect를 보지 않는다.
- Utility/account check가 component별 shell drift·button reset·sync/account 경계를 보지 않는다.
- Editor check가 whitespace를 안정된 입력 경계에서 자동 정리하는지, `편집` 패널이 현재 줄 context와
  action scope를 충분히 보여주는지 보지 않는다.
- Feedback async check가 mutation 응답·readback·draft visibility의 전이를 보지 않는다. POST 응답을
  즉시 화면에 투영하고, readback 실패 때 재제출하지 않아도 되는지 검증해야 한다.

## Sibling Search

- cross-file: src/App.svelte, src/lib/Feedback.svelte, scripts/ui-check.mjs, and scripts/sync-check.mjs
  share the same surface-contract/proof-boundary risk.
- Mental model: user-visible surface는 DOM 존재가 아니라 state × projection × coordinate × interaction 계약이다.
- Same layer: Graph summary/zoom/label, News/StudyGuide/History/Feedback/Sync outer shell — decision:
  same waste, fix now; proof: 각 요소를 따로 검사하고 sibling 간 rect·owner를 검사하지 않는다.
- Abstraction up: Markdown source/shell, Card type/label/front/back, version/date — decision: same waste, fix now.
- Interaction sibling: Review full list removal vs one-card primary surface — decision: contract decision first;
  follow-up: deferred `docs/handoff.md`의 복습 interaction model.
- Account sibling: Sync password/lock vs person/account menu — decision: same owner waste, fix now.
- Editor sibling: parser의 line trim vs Editor cleanup button, command panel의 line number vs actual line
  context — decision: same context/normalization waste, fix now.
- Async sibling: Feedback POST mutation vs list readback — decision: same completion-contract waste, fix now;
  proof: 반환된 thread를 버리고 중간 상태에서 draft를 비운다.

## Seam Risk

- Interrupt ID: surface-contract-state-geometry-20260806
- Risk Class: contract-freeze-risk
- Seam: Svelte projection·CSS coordinate system·SVG getBBox·Markdown renderer·Playwright DOM
- Disproving Observation: 동일 matrix에서 duplicate·overlap·overflow·shift가 재현되지 않고 acceptance가
  결과를 직접 읽으면 이 가설을 낮춘다.
- What Local Reasoning Cannot Prove: 실제 iOS fixed의 유효성, 최신 public asset이 현재 source와 같은지
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: open
- Critique Required: no
- Critique note: 아직 수리 설계 전 진단이다.
- Next Step: spec
- Handoff Artifact: this record

## Prevention

다음 구현 전에 6축 표를 state × viewport × projection × interaction matrix로 확장한다. 최소 행은
closed/open, 50/기본/최대 줌, front/reveal/graded, mobile/desktop, loading/success/failure,
one-card/list다. 각 행에 실제 DOM text uniqueness, rect collision, horizontal scroll, allowed sequence,
  default disclosure, answer leakage, stable primary rect, common shell, account owner, normalization boundary,
  editor context, mutation/readback completion을 적는다.
기존 assertion이 사용자의 의도를 잘못 고정하는지 먼저 검토한다. N fixed 여부·줌 허용 집합·history/sync
composition·person/account route·봉인/잠그기 용어를 수리 전에 봉인한다. `Card` 내부 label은 질문 화면에
직접 렌더링하지 않고, 회상 전 projection이 question-safe인지 별도로 증명한다.
