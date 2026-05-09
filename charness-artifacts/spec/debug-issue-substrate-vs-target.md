# Problem

`debug` skill 본문(steps 4-5: enumerate diverse causes, test falsifiable
hypothesis)과 `issue/references/causal-review.md` Lens 1(Root cause / 5 whys
or causal chain / common bottoms)이 같은 RCA discipline을 두 곳에서 본문화한
silent overlap. 결과:

- bug-class issue 안에서 `causal-review.md`만 보면 디버깅의 falsifiable
  hypothesis substrate가 없는 것처럼 보인다.
- GitHub issue가 없는 RCA(직접 운영 중 만난 버그, 별 issue로 안 떨어진
  현상)는 `debug` skill만 호출되는데, 이 경로가 `causal-review.md`의
  structural-cause discipline과 sibling-search 규율을 잃는다.
- 두 본문이 reword되면서 분기 drift할 위험 — Leg 5 premortem→critique과
  같은 트랩.

# Current Slice

`debug` ↔ `issue` 사이의 RCA ownership을 substrate-vs-target으로 분리해
checked-in contract를 한 의미로 잠근다:

- `debug` = RCA / falsifiable hypothesis substrate skill. standalone 호출
  가능. durable debug artifact + 5-whys/causal-chain 본문 owner.
- `issue/references/causal-review.md` = close-ledger lens layer. structural-
  cause 분류 기준, Over-reach check, detection-gap, sibling-search,
  classification-by-close-comment 규율 owner.
- bug-class `issue resolve` step 4는 `debug` skill substrate를 명시 호출하고,
  close comment의 root-cause line은 debug artifact path를 cite한다.

본 슬라이스는 spec 단독. impl 슬라이스는 별도 (First Implementation Slice 참조).

# Fixed Decisions

- **`debug`가 RCA substrate owner**. 5-whys / causal-chain 본문, "common
  bottoms that count vs. do not count", structural-cause 어휘는 debug
  references로 이전.
- **이전 대상 reference path = `skills/public/debug/references/five-whys-
  causal-chain.md`** (P1 default (a) promote — naming bikeshed만 deferable).
  step 2 시작 시 path lock-in.
- **`issue/causal-review.md`가 close-ledger lens layer**. Over-reach check
  (lens-internal counterweight), detection-gap lens, sibling-search lens
  (same-layer / abstraction-up / specialization-down), Output Shape, Resolution
  Critique handoff template, Close Comment Shape는 그대로 유지.
- **Lens 1 본문 압축 + dispatch**. `causal-review.md` Lens 1은 본문 RCA
  body를 잃고 "debug skill substrate 결과를 close-ledger 관점에서 triage" 한
  paragraph + debug reference cite + **"do not re-derive RCA body in causal
  review"** guard sentence로 줄어든다. 이 guard sentence는 *Lens 1 paragraph
  안에* land (subagent prompt가 cite하는 surface 안에 있어야 re-derivation
  방지).
- **`issue/SKILL.md` step 4 dispatch 갱신**. bug-class causal review가
  spawn하는 fresh-eye subagent prompt에 "consume `debug` skill의
  five-whys/causal-chain reference; do not re-derive RCA body"를 명시.
  close-comment ledger의 root-cause line 바로 *아래*에 단일-줄 `Debug
  artifact: <path>` slot이 들어간다 (close-comment shape `bug` bullet 안의
  canonical 위치).
- **debug standalone path 보존**. GitHub issue 없는 RCA도 정당한 surface.
  debug skill은 issue trigger 없이도 호출 가능하다는 명시 wording을 SKILL.md
  본문에 한 줄.
- **Hard cite churn, no alias**. Leg 5/6 패턴 동형. 단일 슬라이스 안에서
  관련 cite 일괄 갱신. **Cite 대상 surface 4개**: (a) `debug/SKILL.md`
  References list, (b) `debug/SKILL.md` 본문 1회 cite (RCA substrate가
  reference로 추출됐다는 표지), (c) `issue/references/causal-review.md`
  Lens 1 paragraph cite, (d) `issue/SKILL.md` step 4 dispatch wording cite.
- **Anchor citation chain test 추가**. retro lesson("새 reference를 만들 때
  SKILL.md/closeout/관련 reference에서 해당 파일을 cite 했는지 grep-기반 한 줄
  테스트") 적용. 검사 항목: (1) 새 reference 파일 자체가 존재 (typo
  방지), (2) 위 cite surfaces 4개 각각에서 path를 cite, (3) Lens 1 negative
  grep — `causal-review.md`에 "Common bottoms that count", "race condition",
  "edge case" 등 이전 phrase 0 hit, (4) `issue/SKILL.md` step 4의 "consume.*
  debug.*substrate" 또는 동등 dispatch phrase 1 hit, (5) `debug/SKILL.md`의
  standalone phrase ("callable directly", "without GitHub issue", 또는 동등)
  1 hit, (6) `issue/SKILL.md` close-comment shape에서 "Debug artifact:" slot
  1 hit.
- **본 spec은 GitHub issue 없이 진행**. 사용자 명시. spec 본 파일이 contract
  단독 owner.
- **Acceptance는 spec-slice ↔ impl-slice 분리** (Hidden Sequencing critique
  consumed). spec-slice acceptance는 본 파일 land + critique 결과 fold만.
  validator/grep/dogfood acceptance는 First Implementation Slice 안으로
  이동.

# Probe Questions

- **P2**: causal-review.md Lens 1 잔여 본문의 길이. 한 paragraph + cite +
  guard sentence로 충분한가, 아니면 "structural-cause 검증" + "Common bottoms
  cross-link" 두 paragraph가 필요한가. 압축 후 dogfood에서 첫 close comment를
  작성할 때 체감으로 결정. 제약: causal-review.md 전체가 현재 204줄이므로
  Lens 1 압축으로 슬롯이 생기는 형태가 정상 (net 감소).
- **P4**: bug-class causal review subagent prompt가 debug substrate를 어떻게
  consume하는가. 후보 (a) prompt가 debug skill 본문 + 새 RCA reference를
  cite, (b) prompt가 caller에게 debug skill 호출 결과 (debug artifact path)
  를 `prior_context`로 받음. (b)는 "debug → causal review" 순서 강제, (a)는
  causal review 안에서 RCA를 cite-only로 consume. **step 4 wording 작성은
  default (a)로 시작하되**, 첫 dogfood retro에서 (a)/(b) sequencing 적합성
  결정. P4 결정이 step 4 wording을 *block 하지는 않는다* — default (a)
  wording이 (b) 으로 upgrade될 때 무손실.

(P1, P3는 Fixed Decisions로 promote 됐다 — angle 1/3 critique consumed.)

# Deferred Decisions

- **debug standalone retro의 dogfood 누적**. issue 없이 debug만 호출된
  경로의 retro 1회 이상 관찰 후 separate guard 추가 여부 결정.
- **causal-review.md를 다른 close-ledger consumer가 reuse**. release
  post-mortem, incident retro 등이 같은 lens layer를 cite할 수 있을지는
  evidence 누적 후.
- **`references/causal-review.md`의 standalone link을 debug에서도 cite**.
  현재는 issue 한 곳만 cite. 양방향 cite는 churn 더 만들 수 있음. dogfood
  관찰 후 결정.
- **bug-class subagent prompt template에서 RCA chain의 "depth" parameter**.
  현재는 "stop when next why is out of scope". depth ceiling 강제는 dogfood
  evidence 후.

# Non-Goals

- `debug` 또는 `issue` skill 자체 rename.
- `causal-review.md`를 통째로 debug references로 이동 (close-ledger 특화
  부분이 issue domain).
- 본 슬라이스 안에서 GitHub issue 생성.
- 다른 skill (impl, release, retro, critique 등)의 RCA 어휘 cleanup.
- debug skill 본문을 5-whys 어휘로 rewrite (현재 step 4-5는 이미 RCA
  substrate; cite churn 으로 충분).

# Deliberately Not Doing

- `5 whys` 본문을 두 곳에 모두 본문화 (silent overlap 그대로 유지) — 정확히
  본 spec이 fix하려는 트랩.
- alias / wrapper skill 도입. cite churn은 단일 슬라이스로 일괄 (Leg 5/6
  동형).
- `debug` → `rca` rename. `debug`는 incident-investigation lifecycle 전체
  (problem statement, repro, hypothesis test, prevention)를 담는 substrate
  이며 RCA보다 scope가 넓다. RCA-only rename은 substrate scope를 좁힌다.
- causal-review.md Lens 2/3 (detection-gap, sibling-search) 본문도 debug
  references로 이전. 이 둘은 *issue lifecycle 안에서 close-ledger 정당화에
  쓰이는* lens — debug substrate scope 밖.

# Constraints

- **`MAX_SKILL_MD_LINES=200` budget**: `issue/SKILL.md`는 현재 200줄로
  budget 정확히 닿음. step 4 dispatch wording 추가 *전*에 issue/SKILL.md를
  먼저 압축해 ≥3줄 슬롯 확보 (recent-lessons.md의 "먼저 기존 텍스트의 압축
  슬롯을 확보한 뒤 새 contract를 추가" 패턴).
- **causal-review.md 본문 길이**: 현재 204줄. Lens 1 압축으로 줄어들고
  dispatch line 추가로 다시 늘어나야 *net 감소* (Counterweight critique
  consumed — `+0` 어휘 제거).
- **Cite churn은 단일 슬라이스에서 일괄 갱신**. Leg 5/6 패턴 동형. alias
  안 둠.
- **portable**: charness 본문이 host 특정 host runtime을 가정하지 않는다.
  causal-review.md의 dispatch wording은 `debug` skill을 일반 호출 가능
  capability로 가정.
- **deterministic gates over prose rituals**: anchor citation chain test는
  grep-기반 한 줄. SKILL.md / reference 본문 mutation 없이 통과 안 되는
  형태.
- **backtick span 줄 끝 wrap 주의**. 본문 작성 시 `gh issue close --comment-
  file` 같은 긴 span은 줄 머리 가까이 둔다 (recent-lessons.md repeat trap).

# Success Criteria

- `debug` skill의 RCA substrate 본문이 한 reference (P1 결정)로 추출되어
  cite 가능한 path가 단일.
- `issue/causal-review.md` Lens 1이 dispatch + structural-cause check 본문
  으로 압축됐고, 본문에 debug RCA reference cite가 있다.
- `issue/SKILL.md` step 4 본문이 bug-class 호출에서 `debug` skill을 명시
  invoke 한다는 wording을 갖는다.
- `issue/SKILL.md` 또는 close-comment shape에서 `debug` artifact path를
  cite 가능한 ledger 슬롯이 정의된다.
- `debug/SKILL.md` 본문에 "issue trigger 없이도 standalone 호출 가능" 의미
  의 한 줄 wording이 명시된다.
- 신규 anchor citation chain test가 (a) `debug/SKILL.md`, (b)
  `issue/references/causal-review.md` 두 surface 모두에서 신규 RCA reference
  를 cite 하는지 검사하고, 미충족 시 fail.
- 기존 quality gate (validator, doc-link checker, public skill dogfood)가
  새 contract로 통과.

# Acceptance Checks

**Spec-slice acceptance** (본 슬라이스에서 충족):

- 본 spec 파일 land — `charness-artifacts/spec/debug-issue-substrate-vs-
  target.md`.
- 본 spec의 `Critique` 섹션이 spec-critique 4-bin triage 결과를 fold (현재
  buffer가 그것).
- handoff item 1이 본 spec land로 update.

**Impl-slice acceptance** (First Implementation Slice 종료 시 충족):

- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/check_skill_contracts.py --repo-root .` (있을 시)
- `python3 scripts/check_doc_links.py`
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`
- 신규 grep-기반 anchor citation chain test (single test, 6 assertion):
  - `test -f skills/public/debug/references/five-whys-causal-chain.md` —
    파일 존재 (typo 방지).
  - `rg -l 'five-whys-causal-chain' skills/public/debug/SKILL.md` 1 hit
    (References list 갱신 + 본문 cite).
  - `rg -l 'five-whys-causal-chain' skills/public/issue/references/causal-
    review.md` 1 hit (Lens 1 paragraph cite).
  - `rg 'consume.*debug.*substrate|debug.*RCA.*reference' skills/public/
    issue/SKILL.md` ≥1 hit (step 4 dispatch phrase).
  - `rg 'callable directly|without GitHub issue|standalone' skills/public/
    debug/SKILL.md` ≥1 hit (standalone wording).
  - `rg 'Debug artifact:' skills/public/issue/SKILL.md` ≥1 hit (close-
    comment shape slot).
  - **Negative grep**: `rg -c 'Common bottoms that count|race condition.*
    synchronization|edge case.*classifier' skills/public/issue/references/
    causal-review.md` → 0 (Lens 1 본문 이전 후 잔재 phrase 없음).
- `python3 scripts/validate_skills.py` 안에서 issue/SKILL.md ≤200줄
  (post-dispatch land 후), causal-review.md < 204줄 (net 감소) 확인.
- 1회 dogfood: 임의 bug-class scenario를 `issue resolve`로 실행해 close
  comment의 root cause line *바로 아래*에 `Debug artifact: <path>` 단일-줄
  slot이 들어갔는지 관찰. **Dogfood evidence는 impl-slice closeout retro
  artifact에 close comment quote로 기록** (agent self-report 아닌 grep-able
  artifact). retro 본문이 cite로 통과 가능.

# Critique

`charness:critique` 호출 — target reference `references/spec-critique.md`,
3 angle subagents (Likely Implementer Misread, Overstated Acceptance, Hidden
Sequencing) + 1 counterweight subagent, 모두 parent-delegated. 결과 4-bin
triage:

**Act Before Ship** (모두 본 spec에 fold됨, 위 sections 갱신):

- *P1을 Probe → Fixed로 promote* (Misread A1.5 + Sequencing A3.3): 이전
  reference path를 `five-whys-causal-chain.md`로 lock — Fixed Decisions에
  추가, Probe Questions에서 제거.
- *Cite surfaces 4개 enumeration* (Misread A1.6): debug/SKILL.md References
  list, debug/SKILL.md 본문 cite, causal-review.md Lens 1 paragraph cite,
  issue/SKILL.md step 4 dispatch wording — Fixed Decisions에 명시.
- *"do not re-derive RCA body" guard를 Lens 1 paragraph 안에 land* (Misread
  A1.2 + Sequencing A3.2): subagent prompt가 cite하는 surface가 그 paragraph
  이므로 guard sentence가 그 안에 있어야 효과 — Fixed Decisions에 명시.
- *Lens 1 압축 negative grep gate* (Acceptance A2.1): "Common bottoms that
  count", "race condition.*synchronization", "edge case.*classifier" 0 hit
  — Acceptance Checks에 추가.
- *Dispatch / standalone / Debug artifact slot 모두 grep check* (Acceptance
  A2.2-2.4): 6 assertion으로 anchor test 확장 — Acceptance Checks에 추가.
- *Anchor test에 reference 파일 존재 assertion* (Acceptance A2.5): typo
  방지 — `test -f` precondition 추가.
- *Acceptance를 spec-slice ↔ impl-slice로 분리* (Sequencing A3.5): 본 슬라이스
  는 contract land만; validator/grep/dogfood는 impl-slice closeout — 두
  acceptance block으로 분리.
- *Step 2-3 atomic move 명시* (Sequencing A3.1): 본문이 두 곳에 동시 존재
  하는 transient duplication 금지 — 단일 commit 안에서 reference 신설 +
  Lens 1 line 50-70 제거.
- *압축 line delta가 step 4+5 추가량 ≥ 매칭* (Sequencing A3.4): step 1이
  measure하고 budget — First Implementation Slice 본문 갱신.

**Bundle Anyway** (cheap fix, 같이 land):

- *Close-comment Debug artifact slot canonical 위치 명시* (Misread A1.3):
  `bug` bullet의 root cause line 바로 *아래* 단일-줄 — Fixed Decisions에
  명시.
- *Constraints "+0" wording 제거* (Counterweight): "net 감소" 단일 어휘 —
  Constraints 본문에 반영.

**Over-Worry** (counterweight가 미리 차단):

- grep test → AST/markdown-parser unit test upgrade 요청 — recent-lessons.md
  가 grep 한 줄 명시 endorse, over-engineering 위험.
- 1회 dogfood → ≥3 dogfood scenario 요구 — 본 슬라이스 acceptance scope
  밖.
- 외부 GitHub issue / operator announcement 의무 — 내부 repo-operating-
  contract churn, 외부 surface 변경 없음.
- `debug` → `rca` rename — substrate scope를 좁힘 (debug는 incident
  lifecycle 전체).
- causal-review.md Lens 2/3 (detection-gap, sibling-search) 도 같이 이전 —
  issue lifecycle 안에서의 lens, scope 밖.

**Valid but Defer**:

- *Dogfood verifiable artifact path 강제* (Acceptance A2.6): impl-slice
  closeout retro에 close-comment quote가 cite로 들어가는 형태로 충분 —
  Acceptance Checks impl-slice block에 retro artifact cite 요구만.
- *P4 default (a) → Fixed* (Sequencing A3.6): step 4 wording은 default
  (a)로 작성 가능 (P4가 wording을 block 하지 않음). P4는 dogfood로 (a)/(b)
  sequencing 결정 — Probe로 유지.
- causal-review.md를 release post-mortem / incident retro 등 다른 close-
  ledger consumer로 reuse — Deferred Decisions 그대로.
- causal-review.md → debug standalone path의 양방향 cite — Deferred
  Decisions 그대로.

`Fresh-Eye Satisfaction: parent-delegated` (4 subagents 모두 parent-
delegated, nested 없음).

# Canonical Artifact

- `charness-artifacts/spec/debug-issue-substrate-vs-target.md` (본 파일)

# First Implementation Slice

본 step 순서는 단일 commit/PR 안에서 atomic land — transient duplication 또는
land-time test fail이 되지 않도록 mutate 묶음.

1. **Pre-state 측정 + 압축 슬롯 plan**. `wc -l skills/public/issue/SKILL.md`
   = 200 (현재 budget 직격), `causal-review.md` = 204. step 4+5+6에서
   추가될 line delta 측정 (dispatch sentence + Debug artifact slot bullet =
   추정 ~3줄, standalone wording 1줄, anchor test 본문 별도 file). issue/
   SKILL.md 압축 surface 명시: 후보 (i) step 8 critique handoff template 1-2줄
   응축, (ii) bootstrap 코드 블록 주석 1줄 응축. *trivial whitespace 압축
   금지* — 의미 있는 line 응축만 인정.
2. **Atomic move: debug RCA reference 신설 + Lens 1 본문 제거**. 단일 commit
   에서:
   - `skills/public/debug/references/five-whys-causal-chain.md` 신설.
     `causal-review.md` 현재 Lens 1 body block (5 whys, structural-cause
     분류 기준, common bottoms count vs. do not count) 을 이전.
   - `causal-review.md` Lens 1 paragraph 압축: body block 제거, 자리에 한
     paragraph + "**Do not re-derive the RCA body in causal review.**
     Consume `../../debug/references/five-whys-causal-chain.md` and triage
     the substrate result through close-ledger lenses". Lens 2/3는 그대로
     유지.
   - backtick span은 줄 머리 가까이 (recent-lessons backtick wrap 트랩).
3. **`issue/SKILL.md` step 4 dispatch wording + close-comment slot**. 같은
   commit:
   - step 4 본문에 한 줄: "the bounded fresh-eye subagent consumes the
     `debug` skill substrate (`debug/references/five-whys-causal-chain.md`);
     do not re-derive RCA body in causal review".
   - close-comment shape `bug` bullet의 root cause line 바로 아래에 단일-
     줄 `Debug artifact: <path>` slot.
   - 추가 line delta가 step 1에서 확보한 슬롯 안.
   - post-mutation `wc -l skills/public/issue/SKILL.md` ≤ 200.
4. **`debug/SKILL.md` standalone wording + cite**. 같은 commit:
   - 본문 한 줄: "`debug` is callable directly when no GitHub issue exists;
     bug-class `issue resolve` invokes it through
     `issue/references/causal-review.md` Lens 1".
   - References list에 `references/five-whys-causal-chain.md` 추가.
   - 본문 1회 cite — step 4 (Enumerate diverse causes) 또는 step 5 (Test a
     falsifiable hypothesis) 안에 자연스러운 자리.
5. **Anchor citation chain test 신설**. 같은 commit:
   - `tests/quality_gates/test_debug_rca_reference_cite_chain.py` (또는
     repo의 quality_gates 패턴 따른 위치). 6 assertion (Acceptance Checks
     impl-slice block 참조).
   - test land가 step 2-4의 cite mutation과 *같은 commit* — test 단독
     commit 금지 (Sequencing A3.2 mitigation).
6. **Validator + dogfood**. `validate_skills.py`,
   `validate_public_skill_dogfood.py`, `check_doc_links.py`,
   `check_skill_contracts.py` (있을 시) 통과. 1회 dogfood: bug-class
   scenario를 `issue resolve`로 실행하고 close-comment 결과를 retro
   artifact (impl-slice closeout retro)에 quote로 기록.
7. **Slice closeout critique**. `code-critique` target — cite churn 정확성
   (4 surface 모두 갱신됐는가), anchor test 6 assertion 모두 통과, dispatch
   wording readability 우선. retro artifact에 close-comment quote 포함.

지금 본 spec 단독 슬라이스는 contract land만. impl 슬라이스는 다음 세션 또는
별도 슬라이스.
