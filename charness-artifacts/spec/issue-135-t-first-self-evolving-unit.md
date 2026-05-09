# Spec: Issue #135 — T-first Self-Evolving Unit (6-leg umbrella)

Source: https://github.com/corca-ai/charness/issues/135

이 spec은 issue 135의 design exploration을 implementation contract로 떨어뜨린
**umbrella spec**이다. 5개 leg이 한 narrative ("implicit T mechanism을
explicit하게") 아래 묶이며, 각 leg sub-section이 자기 success criteria +
acceptance check + mitigation entry를 보유한다. 5개 GitHub child issue로 split
되지만, contract truth는 본 문서가 owner다.

## Problem

charness는 c-families 중 (H+agent) T material이 가장 두꺼운 repo다 — anchor
lineup, retro skill, skill self-promotion, find-skills, lesson-selection-index
가 모두 unit-growth 형태다. 그러나:

1. **C-level 회로가 implicit**. retro/quality가 B/C 층을 건드리지만 "retro
   자체가 통했나?"라는 meta-retro는 없다.
2. **Engelbart anchor가 lineup에 없다**. Jackson/Raskin/Weinberg/Gawande/
   Minto 5인은 모두 LAM-비평 lens라 *"(H + LAM + T)를 한 단위로 보고 T를
   LAM 옆에 함께 설계"*라는 trigger가 비어 있다.
3. **운영자 T path가 산재**. day-1 vs. 8-week vs. 6-month 운영자 capability
   path가 README와 init-repo와 여러 skill doc에 흩어져 있다.
4. **Skill T mechanism이 미선언**. retro-driven SKILL.md 진화는 일어나지만,
   *그 mechanism 자체*가 명명된 surface가 아니다.
5. **`premortem` skill이 substrate 동형 critique과 분리된 이름**. premortem은
   pre-lock-in critique with anchor-discriminated multi-angle + counterweight
   substrate를 가지며, 동형 substrate가 code/PR critique에도 직접 적용된다.
   두 이름으로 두면 silent overlap 위험 + issue 135 narrative ("implicit →
   explicit")와 모순.

[hermes-agent](https://github.com/NousResearch/hermes-agent)는 이 T를 runtime
telemetry에 굽는 substrate (curator/insights/FTS5 session search/Honcho
dialectic user model). charness는 plugin이라 runtime을 못 가지므로 **artifact
diff + adapter-mediated event hook**으로 같은 T를 portable하게 표현한다. 이
substrate 차이는 의도이며 약점이 아니다.

## Current Slice

6-leg umbrella를 한 contract 안에서 정의. 각 leg은 자기 PR/issue로 land하지만
sub-section 간 의존관계와 sequencing은 본 spec이 owner. impl phase에서 leg별
acceptance check가 PR review의 1차 기준.

## Fixed Decisions

### Umbrella

- **6-leg split**, issue 135를 umbrella로 유지하고 6개 child issue 신규 생성.
  child issue 본문은 본 spec의 해당 sub-section을 cite.
- **Sequencing (PR-단위)**:
  1. **PR 1**: Leg 5 단독 (rename + 5 references). cite churn 격리.
  2. **PR 2**: Leg 2 + Leg 1 bundle (manifest + emit point + inventory가 Leg 2
     event 소비). 분리하면 절반 완료 anti-pattern.
  3. **PR 3**: Leg 3 (Engelbart anchor). PR 1의 critique reference 안에 적용.
  4. **PR 4 (parallel from PR 2 onward)**: Leg 4 standalone.
  5. **PR 5 (after PR 2)**: Leg 6 (`init-repo` → `setup` rename + consumer
     onboarding seed for t-events). t-events schema가 PR 2에 land하므로
     seed가 의존.
- **Build + cross-repo dogfood**, no probe-first. evidence는 charness 자체 +
  사용자 운영 인접 repo에서 누적된다.

### Leg 1 — Skill-T mechanism inventory

- **Tier B+ default**: lesson cite chain (`source: charness-artifacts/retro/...`)
  + lesson-selection lifecycle evidence (`lesson-selection-index.json`의 retro
  유지 횟수, recency rotation)가 inventory의 결정적 column.
- **Tier C placeholder**: 어댑터 매개 runtime telemetry column. data path는
  Leg 2 manifest. 없는 동안 *"awaiting events"* explicit marker (implicit
  absence ≠ "no T").
- **Anchor lineup wiring evidence는 별도 column** (T evidence와 직교).

### Leg 2 — T-events adapter manifest + self-dogfood

- `integrations/t-events/manifest.schema.json` + `adapter.example.yaml` land.
  worktree-adapter / cautilus-adapter / issue-backend-adapter 패턴 차용.
- **charness 자기 repo가 첫 consumer**. emit point 1개 lands in same slice.
- emit point 후보 결정은 Probe (아래).
- consumer repo는 어댑터 wiring을 opt-in. wiring 안 하면 Tier C empty, 침묵
  실패 없음.

### Leg 3 — Engelbart anchor entry

- **옵션 C 채택**: 모든 anchor entry에 `applies_when:` scope 메타데이터 한 줄
  추가.
- **`applies_when:` value 어휘 (closed set)**:
  - `lam-critique` — 기존 5인 (Jackson/Raskin/Weinberg/Gawande/Minto). 코드/문서
    /결정 산출물(LAM)을 비평하는 surface.
  - `system-improving-itself` — Engelbart. 시스템이 자기를 개선하는 설계
    surface (T-loop 디자인, skill 진화 mechanism, retro contract 변경 등).
  - 신규 value 추가는 본 spec 갱신 + 양성 dogfood 사례 동반 시에만.
- Engelbart trigger: *"treat (H + LAM + T) as one unit; design T alongside
  LAM."*
- Engelbart entry에 **falsifier 명시**: *"이 anchor가 `lam-critique` surface
  에서 잘못 발화해 verdict를 distort한 사례가 dogfood에서 1회 이상 관찰되면,
  옵션 B(별도 lineup)로 escalate"*. escalation cost는 `skills/public/critique/
  references/` 안에서 lineup metadata 형태 변경으로 bounded — 두 번째 rename
  event가 아님.
- 분류 type 신설은 하지 않음 (premature abstraction). 옵션 C에서 D(라우터)
  나 B(별도 lineup)로의 escalation은 위 falsifier로 trigger.

### Leg 4 — Operator-T progressive path doc

- `docs/operator-acceptance.md`에 day-1 / 8-week / 6-month 운영자 expected
  capability section 추가.
- `init-repo` seed가 새 surface를 cite.
- **본인 + 인접 운영 repo 관찰을 evidence로 ground**. 가설 단어 금지.

### Leg 5 — `premortem` → `critique` rename

- **Hard rename, no alias**. 한 슬라이스 안에서 전체 cite 일괄 갱신.
- **No flags**. 진입은 `charness:critique`. target은 reference doc로 분기,
  agent가 호출 컨텍스트로 선택.
- **5 references 한 슬라이스에 모두 작성**. 각 reference 의 shape 계약:
  - 모든 target reference는 공통 4 section 보유 — `When This Lens Fires`
    (target 식별 trigger 언어), `Anchor Angle Distribution` (5인 lineup +
    Engelbart 중 어느 angle이 어느 비중), `Counterweight Bins`
    (target-specific 진짜 blocker vs. over-worry 분류 기준), `Output Shape`
    (실 산출물 형식).
  - 이 4 section 위에 target별 본문 추가:
  - `references/premortem-decision.md` — Klein-style decision pre-mortem.
    "premortem" 단어 lineage 살린다. 현재 SKILL.md 의 decision 본문 이전 +
    Klein cite section 추가.
  - `references/code-critique.md` — commit/PR/snippet/repo critique. 신규.
    target-shape section: `Defect Class Cross-Link` (retro recent-lessons 와
    cross-link), `Capability Gap Routing` (find-skills 로 missing skill/
    integration 라우팅).
  - `references/release-critique.md` — 현재 premortem release 본문 이전.
    target-shape section: `Surface-Lock Inventory` (release가 lock하는 user-
    facing surface 식별).
  - `references/rename-critique.md` — rename/deletion 특이점 (#131 first-
    reader 결합). target-shape section: `First-Reader Probe`, `Slug Drift
    Check` ([scripts/check_title_slug_drift.py](../../scripts/
    check_title_slug_drift.py) 와 cross-link).
  - `references/spec-critique.md` — pre-impl spec critique. target-shape
    section: `Fixed/Probe/Defer Coherence`, `Acceptance Check Coverage`.
- 기존 `references/angle-selection.md`, `references/counterweight-triage.md`는
  substrate references로 보존 (모든 target이 cross-cite).
- `closeout-discipline.md`의 *"Treat premortem ... as part of task-completing
  repo work"* 라인을 critique으로 단어 갱신. substrate 의도 그대로.
- `premortem` 단어는 skill 이름이 아니라 reference 안의 *target lens 이름* 으
  로 보존됨.

### Leg 6 — `init-repo` → `setup` rename + consumer onboarding seed

- **Hard rename, no alias**. 한 슬라이스 안에서 일괄. `init-repo` 이름이
  greenfield 의미를 강제해 이미 init된 repo의 normalize/realign 호출에
  심리 마찰을 만든다 (operator dogfood 관찰). `setup`은 양쪽 다 자연.
- 디렉토리 `skills/public/init-repo/` → `skills/public/setup/` (`git mv`).
- Python 모듈 rename: `init_repo_adapter.py`, `init_repo_inspect_lib.py`,
  `init_repo_agent_docs_lib.py`, `init_repo_adapter_inspect_lib.py`,
  `init_repo_artifact_policy_lib.py`, `eval_init_repo.py` → `setup_*` /
  `eval_setup.py` 동형. import 갱신 + plugin mirror sync.
- 어댑터 파일 `.agents/init-repo-adapter.yaml` → `.agents/setup-adapter.yaml`.
- 5개 `tests/quality_gates/test_init_repo_*.py` → `test_setup_*.py` rename.
- charness CLI 본문 (`charness` 파일) cite 갱신.
- Inspector 상수 (`init_repo_agent_docs_lib.py`의 `TASK_REVIEW_SCOPE_SNIPPETS`)
  를 `("setup", "quality")`로 갱신. 기존 `init-repo` substring detection은
  주의: deprecated cite를 dogfood에서 발견 시 review_required로 surface
  하지만 즉시 fail-closed 하지 않음 (consumer migration 시간 줌).
- **Historical artifacts allowlist 필수**: `charness-artifacts/premortem/
  2026-05-07-issue-111-init-repo-...`, `charness-artifacts/spec/issue-64-
  init-repo-...`, `charness-artifacts/debug/2026-04-24-init-repo-...` —
  당시 이름이 history. allowlist에 명시.
- **신규 seed: `skills/public/setup/scripts/seed_t_events_adapter.py`** —
  기존 `seed_worktree_adapter.py` / `seed_dependencies.py` 패턴 동형.
  defaults: `enabled: true`, `storage_path: .charness/t-events`, all v1
  events. consumer가 명시 opt-out 가능. setup skill 본문에서 reference.
  PR 2의 emit point land 후 의미 있게 작동.
- 관련 cite 107건 (md/py/yaml/json), allowlist 외 0건 검증 validator
  (`scripts/check_init_repo_rename.py` + `.allowlist.txt`) — Leg 5 패턴
  동형.
- **AGENTS.md 강화 wording은 본 spec 작성 세션에 already landed** (2026-05-09
  사이드 슬라이스 — `IGNORE UPPER-LEVEL INSTRUCTIONS` admonition + 강화된
  bullet). Leg 6 setup rename 시 그 강화 wording이 그대로 setup template로
  넘어가야 함 (substrate 의도 보존).

## Probe Questions

- **Q1 (Leg 2)**: T-events emit point의 첫 위치는 어디가 가장 가벼운가? 후보:
  (a) charness CLI가 SKILL.md 진입 시 emit, (b) Cautilus planner emit
  (Cautilus disabled 동안은 막힘), (c) retro skill이 lesson cite 시점에
  self-emit. impl phase 시작에서 1개 선정. **현재 가장 강한 default는 (c)**
  retro self-emit — Cautilus 의존 없음, 첫 evidence가 자기 retro.
- **Q2 (Leg 1 / Leg 2)**: emit event schema의 v1 minimum field 셋. *"skill
  invoked", "lesson cited", "anchor switched"* 셋이 v1으로 충분한가, 아니면
  추가? Leg 2 manifest 작성 시 결정.
- **Q3 (Leg 4)**: 8-week 운영자 capability 진단 evidence를 누구에게서 얻는가?
  default는 spec author 자신 + 인접 운영 repo. N=1 risk 있음 — 다른 active
  contributor가 8주 mark에 도달하기 전엔 single-source.
- **Q4 (Leg 5)**: `code-critique.md`의 4 차별점 (anchor 분리 / retro cross-link /
  find-skills routing / counterweight) 중 dogfood에서 ≥2개 매번 부족 못
  관찰되는 N=5 도달 시 다음 액션 — wrapper(γ)로 downgrade인가, references만
  유지하고 dogfood 더 모으는가? Leg 5 land 후 첫 retro에서 결정.

## Deferred Decisions

- **Tier C-via-adapter contract 본격 디자인**. v1 manifest는 Leg 2에 land
  하지만, 어댑터의 cross-repo aggregation/normalization 책임 디자인은 v1
  evidence 누적 후. Leg 4 meta-retro (issue 135 narrative의 C-leg, 본 spec
  out-of-scope) 가 측정 부족 신호를 보내면 디자인 trigger.
- **meta-retro (C-level) skill**. issue 135 narrative의 "C-leg"는 본 spec의
  5-leg 외부에 있음. Leg 1 inventory가 baseline을 깐 *후* land. 본 spec은
  meta-retro의 placeholder만 인정 (Leg 1 result로 정당화 또는 기각).
- **Engelbart entry의 escalation 결정 (옵션 B / D)**. falsifier 통과 시
  (mis-fire 관찰) trigger. 사전 디자인 안 함.
- **`premortem` 단어의 영구 검색-어휘 보존 전략**. critique rename 후에
  `find-skills`가 "premortem"을 찾으면 어떻게 라우팅할지 — 기본은 SKILL.md
  본문이 reference cite하니 자연 검색됨. 별도 alias 메커니즘은 deferred.
- **5-leg 외 추가 leg**. issue 135 본문이 언급하는 다른 candidate (Engelbart
  hwidong.md §4.1의 5 raw 후보) 중 본 spec에 안 들어간 것은 evidence 본 다음
  separate issue.
- **Cross-repo evidence aggregation surface**. 사용자 인접 repo가 emit한 T-event
  를 charness가 어떻게 join/view할지. 본 spec은 per-repo only. aggregation은
  Tier C v1 데이터 누적 후 separate spec.

## Non-Goals

- meta-retro skill을 본 spec slice 안에서 land 하는 것. 본 spec은 그 baseline
  깔기까지.
- hermes-agent의 runtime curator/insights/Honcho를 직접 baking. 비교 substrate
  로만 reference.
- Cautilus rework. Cautilus는 disabled 유지, 본 spec은 Cautilus 출력에 의존
  안 함.
- 사용자 인접 repo에서 emit한 T-event를 charness가 자동 pull하는 메커니즘
  (deferred 참조).

## Deliberately Not Doing

- **`premortem` alias**. 1주기 alias 두는 옵션 검토했으나 폐기. user 명시
  결정. cite churn은 단일 슬라이스에서 일괄.
- **`critique --target` flag**. flag 없이 reference doc + agent 판단. user
  명시 결정.
- **probe-first delay on Leg 5 code-critique**. 4 차별점 dogfood 검증을 land
  *전*이 아니라 *후*로 연기. cross-repo dogfood가 evidence 누적 빠르게 한다는
  user 판단.
- **Engelbart 별도 meta-anchor lineup 분류**. 1개 entry용 분류 type은
  premature. 옵션 C `applies_when` scope로 충분.
- **5개 separate spec 분할**. 본 umbrella spec 안에 5 sub-section. cross-leg
  의존 (Leg 1↔2, Leg 3↔5)을 spec 간 cite churn 없이 한 자리에서 관리.
- **Tier A (commit-edit recency)** evidence 정의. 너무 시끄러운 false positive.

## Constraints

- **portable**: charness는 plugin이라 runtime을 가질 수 없음. T 표현은
  artifact diff + adapter-mediated hook 으로만.
- **SKILL.md 200줄 budget**: critique SKILL.md는 substrate 본문 + reference
  cites만. target별 운영은 references로 빠진 채 budget 안.
- **premortem cite의 일관 갱신**. spec 작성 시점 (2026-05-09) snapshot:
  `rg -l 'premortem' --type md --type py --type yaml --type json
  /home/ubuntu/charness | wc -l` → 138. PR 1 시점에 재실행해서 그 시점
  count를 PR 본문에 anchor (count 변동은 다른 in-flight work 신호 — Premortem
  mitigation 1 적용 trigger). missed cite는 validator로 fail-closed.
- **Cautilus disabled** 동안 emit point 후보에서 (b) 제외.
- **deterministic gates over prose rituals**: 가능한 acceptance check는
  validator/script로.
- **artifact policy**: charness-artifacts 변경은 commit 동반. 본 spec 자체가
  durable artifact.

## Success Criteria

### Umbrella

- S0. 6개 child GitHub issue가 issue 135 task list에 link 됨.
- S1. 본 spec의 6개 leg sub-section이 각각 ≥1개 acceptance check를 갖고,
  impl phase가 그 check 기준으로 PR review 가능.

### Leg 1

- S1.1. `charness-artifacts/skill-t-mechanism/inventory.{md,json}` 산출.
  대상 스킬 (charness public skills) 모두 행 보유.
- S1.2. inventory가 4 column 채움: lesson-cite-chain (B), lifecycle-survival
  (B+), anchor-wiring (orthogonal), tier-c-events (placeholder + marker).
- S1.3. Tier C column이 *"awaiting events"* marker로 explicit (없는 게
  silent로 missing 처리되지 않음).

### Leg 2

- S2.1. `integrations/t-events/manifest.schema.json` + `adapter.example.yaml`
  land.
- S2.2. charness 자기 repo가 1개 emit point wiring + 첫 event 1건 emit 검증.
- S2.3. Leg 1 inventory가 Leg 2 emit한 event를 Tier C column에 반영.

### Leg 3

- S3.1. anchor lineup의 모든 entry가 `applies_when:` 메타데이터 보유.
- S3.2. Engelbart entry가 lineup에 추가됐고 falsifier 명시.
- S3.3. critique reference / retro reference에서 Engelbart trigger 가
  cite됨.

### Leg 4

- S4.1. `docs/operator-acceptance.md`에 day-1/8-week/6-month section land.
- S4.2. 각 시점 capability가 본인 또는 인접 repo 관찰 evidence cite.
- S4.3. `init-repo` seed가 새 section을 cite.

### Leg 5

- S5.1. `skills/public/premortem/` → `skills/public/critique/` 디렉토리 이동
  완료.
- S5.2. SKILL.md 본문이 substrate 중심으로 재작성됨, 200줄 budget 안.
- S5.3. 5개 reference (`premortem-decision`, `code-critique`,
  `release-critique`, `rename-critique`, `spec-critique`)가 모두 land.
- S5.4. PR 1 시점 cite 모두 갱신, validator가 잔여 `premortem` cite를
  allowlist 외에서 0개 확인. **allowlist는 contracted file**:
  `scripts/check_premortem_rename.allowlist.txt` — 한 줄당 (path, 의도)
  쌍으로 명시. 후보 entry: critique reference 본문 (Klein lineage cite),
  본 spec 자체, retro/recent-lessons.md 의 historical 진단 cite
  (단어가 단어 그대로 보존되어야 의미 있는 곳만), release notes 에 적힌
  rename 자체의 변경 이력. allowlist 파일 자체가 PR 1 deliverable.
- S5.5. `closeout-discipline.md` substrate 의도 보존된 채 단어만 갱신.

### Leg 6

- S6.1. `skills/public/init-repo/` → `skills/public/setup/` 디렉토리 이동
  완료. Python 모듈 파일명 갱신, import 일관.
- S6.2. PR 5 시점 cite 모두 갱신, validator가 잔여 `init-repo`/`init_repo`
  cite를 allowlist 외에서 0개 확인. allowlist 파일 PR 5 deliverable.
- S6.3. inspector 상수 `TASK_REVIEW_SCOPE_SNIPPETS`가 `("setup", "quality")`
  로 갱신, 기존 `init-repo` 사용 consumer repo는 advisory drift로 surface.
- S6.4. `seed_t_events_adapter.py` land. dry-run에서 `.agents/t-events-
  adapter.yaml` 후보 출력, opt-in defaults가 manifest schema validate 통과.
- S6.5. setup SKILL.md 본문이 강화된 Subagent Delegation wording을 그대로
  reference (2026-05-09 land한 admonition 형태 보존).

## Acceptance Checks

### Umbrella

- A0. `gh issue list --label "feature request"` 또는 issue 135 본문에서 6개
  child issue link 확인.
- A1. 6개 leg sub-section 각각이 ≥1 acceptance check 보유 (정적 grep).

### Leg 1

- A1.1. `python3 scripts/validate_skill_t_inventory.py --repo-root .` (신규)
  가 inventory schema 준수 검증, 누락 column 발견 시 fail.
- A1.2. inventory에 charness 공개 스킬 수만큼 row, missing row는 fail.

### Leg 2

- A2.1. `python3 -c "import json; ..."`이 manifest schema validate.
- A2.2. charness retro 1회 실행 후 `.charness/t-events/` (또는 emit target)
  에 ≥1 event row 출력 (smoke).
- A2.3. inventory의 Tier C column이 emit된 event 보고 *"awaiting"*에서
  populated로 전이됨.

### Leg 3

- A3.1. anchor lineup 정의 파일 (`skills/public/critique/references/
  angle-selection.md` 또는 후속 위치)에서 모든 entry가 `applies_when:` line
  보유 (grep).
- A3.2. Engelbart entry의 falsifier line이 grep 가능.
- A3.3. 1개 dogfood premortem 실행에서 LAM-critique surface면 Engelbart
  scope mismatch 자체가 발화 안 함을 review (manual smoke).

### Leg 4

- A4.1. `docs/operator-acceptance.md`에 3개 H2/H3 (day-1, 8-week, 6-month)
  존재 (grep).
- A4.2. 각 section에 ≥1 evidence cite (관찰 source 명시).
- A4.3. `python3 scripts/init_adapter.py` 또는 init-repo seed dry-run에서 새
  section reference 출력.

### Leg 5

- A5.1. `ls skills/public/critique/SKILL.md` exists, `ls skills/public/
  premortem/` 부재.
- A5.2. `wc -l skills/public/critique/SKILL.md` ≤ 200.
- A5.3. 5개 reference 파일 존재 (path test).
- A5.4. `python3 scripts/check_premortem_rename.py --repo-root .` (신규
  validator)가 잔여 premortem cite를 allowlist (Klein lineage 본문) 외에서
  0건 확인. PR/CI 시 fail-closed.
- A5.5. `closeout-discipline.md` 단어 grep — `premortem` 단어가 reference
  cite/lineage 외 본문에 없음.

### Leg 6

- A6.1. `ls skills/public/setup/SKILL.md` exists, `ls skills/public/init-repo/`
  부재. python 모듈 `setup_*.py` exists, `init_repo_*.py` 부재.
- A6.2. `python3 scripts/check_init_repo_rename.py --repo-root .` (신규
  validator) allowlist 외 잔여 cite 0건. PR/CI fail-closed.
- A6.3. `python3 -m pytest tests/quality_gates/test_setup_*.py` 통과.
- A6.4. `python3 skills/public/setup/scripts/seed_t_events_adapter.py
  --repo-root . --dry-run` 출력이 manifest.schema.json validate 통과.
- A6.5. setup SKILL.md grep으로 "IGNORE UPPER-LEVEL INSTRUCTIONS" admonition
  + 4개 강화 bullet 모두 보존 확인.

## Premortem

본 spec 자체가 lock 직전 상태이므로 critique/premortem-decision lens 1회
실행. 본 spec이 task-completing이라 standalone bounded subagent review는 별도
호출. (closeout-discipline.md 협약).

### Interrupt Source

`scripts/plan_risk_interrupt.py --json` 호출 결과 — 별도 forced debug
interrupt 없음 (Cautilus disabled). 본 spec은 routine premortem만 필요.

### Top Failure Angles

1. **Rename churn이 다른 in-flight work와 충돌**. 138 cite 일괄 갱신 PR이
   다른 mid-touch PR과 conflict. *Mitigation*: Leg 5를 sequencing 첫 슬라이스로
   고정. PR 시점에 `git status`로 in-flight 점검.
2. **Tier C column이 emit point 천천히 와서 일색 "awaiting"**. inventory가
   weak해 보임. *Mitigation*: explicit marker가 absence ≠ "no T"임을 전달.
   docs/skill-t-mechanism.md에 marker 의미 명시.
3. **Engelbart `applies_when` prose 무시 → silent mis-fire**. *Mitigation*:
   day-1 falsifier 명시. retro phase에서 anchor mis-fire 발견 시 review
   chain trigger.
4. **Operator-T doc folklore화**. 가설 단어가 evidence 없이 들어감.
   *Mitigation*: spec author 본인 + 인접 repo 관찰만 cite. 8-week capability
   는 author가 8주 운영 evidence 보유 시점에 land 또는 deferred로 표시.
5. **Probe-first 폐기 = 사용 안 되는 code**. cross-repo dogfood가 늦으면
   code-critique가 미사용. *Mitigation*: Q4 falsifier — N=5 dogfood 사례에서
   4 차별점 ≥2 부족 관찰 못 하면 다음 retro에서 wrapper(γ) downgrade 고려.
6. **No flags가 ambiguous 호출에서 wrong reference 픽**. *Mitigation*:
   critique SKILL.md trigger 언어를 구체화 (`commit critique`, `decision
   premortem`, `release critique` 등 자연어 phrase가 reference 매핑을 자명하
   게).
7. **5-leg 일부만 land 후 stale**. *Mitigation*: Fixed Decisions / Sequencing
   의 PR 1-5 layout 그대로 — PR 1 (Leg 5) 단독, PR 2 (Leg 2 + Leg 1) bundle,
   PR 3 (Leg 3), PR 4 parallel (Leg 4), PR 5 (Leg 6). Leg 1·2 분리하면 절반
   완료 anti-pattern.

8. **Leg 5와 Leg 6의 cite churn 충돌**. 둘 다 heavy rename. premortem cite와
   init-repo cite는 namespace 직교지만 같은 파일(AGENTS.md / CLAUDE.md /
   docs/) 안에서 두 cite가 동시에 존재 가능 — 동시 PR이면 merge conflict.
   *Mitigation*: PR 5는 PR 1 land 후 시작. parallel 안 함.

9. **Leg 6 inspector 상수 갱신이 consumer repo에서 silent break**. 외부
   consumer가 `init-repo` substring으로 자기 AGENTS.md를 작성해 inspector를
   통과하던 것이 `setup`으로 검출되지 않음. *Mitigation*: Leg 6에 명시 — 기존
   `init-repo` substring detection을 deprecated advisory로 N release 유지,
   fail-closed로 즉시 전환 안 함. 이게 hard rename + soft inspector
   compatibility라는 작은 비대칭이지만 consumer migration 친화.

### Counterweight Pass

- *"5-leg 모두 imagined problem 풀고 있을 가능성"* — 약한 우려. issue 135
  본문이 4개 observed problem evidence를 design-study repo에서 cite. Leg 5는
  conversation 중 surfaced (premortem ↔ critique substrate identity), evidence
  는 본 spec 작성 사실 그 자체.
- *"hermes-agent를 너무 깊이 베끼게 됨"* — 약한 우려. 의도적으로 비교
  substrate로만 사용. Leg 1-5 어느 것도 hermes module 모방 아님.
- *"premortem 이름 인지 손실"* — 인지된 우려, 부분 mitigation. references
  안 lineage cite 보존, Klein 검색 시 reference 본문에서 발견됨.

### Resolved Disproving Observations

- "premortem과 code-review가 다른 substrate일 가능성" — 본 conversation 중
  분석으로 substrate 동형 (multi-angle pre-lock-in critique with
  counterweight) 확인. 다른 점은 *target shape*만.
- "Tier C가 charness substrate에서 불가능할 가능성" — 어댑터 매개로 가능,
  worktree-adapter 패턴 동형 확인.

## Canonical Artifact

본 spec — `charness-artifacts/spec/issue-135-t-first-self-evolving-unit.md` —
이 5-leg umbrella 의 contract truth. impl phase 동안 leg별로 새 사실이 발견
되면 본 spec을 갱신, 동기화하지 chat-only drift 두지 않음.

각 leg의 owning surface:

- Leg 1 — `charness-artifacts/skill-t-mechanism/inventory.{md,json}`
- Leg 2 — `integrations/t-events/manifest.schema.json` +
  `adapter.example.yaml` + emit point 위치
- Leg 3 — anchor lineup 정의 파일 (critique skill 내)
- Leg 4 — `docs/operator-acceptance.md`
- Leg 5 — `skills/public/critique/SKILL.md` + 5 references

## First Implementation Slice

**Leg 5 — `premortem` → `critique` rename**. 단독 PR.

이유:
- cite churn 격리, 다른 leg가 reference cite를 건드리기 전에 land.
- Leg 3 (Engelbart anchor)가 critique reference 안에 entry 추가하므로 Leg 5
  먼저가 자연.
- substrate 통합이 narrative ("implicit → explicit") 첫 가시 진전.

Slice 내 단계:

1. `skills/public/premortem/` → `skills/public/critique/` 이동 (`git mv`).
2. SKILL.md 본문을 substrate 중심으로 재작성 (decision-only premortem 어휘
   제거, target generic substrate 어휘로). 200줄 budget 안.
3. 5개 reference 작성:
   - 기존 `references/angle-selection.md`, `counterweight-triage.md` 보존
     (substrate, 모든 target cross-cite).
   - 신규: `premortem-decision.md` (현재 SKILL.md decision content 이전),
     `code-critique.md`, `release-critique.md`, `rename-critique.md`,
     `spec-critique.md`.
4. 138 cite 일괄 갱신 (validator pass 시까지 반복).
5. `closeout-discipline.md` 단어 갱신 (substrate 의도 보존).
6. `scripts/check_premortem_rename.py` + `scripts/check_premortem_rename.
   allowlist.txt` 신규. allowlist는 `<path>\t<reason>` 한 줄당. validator는
   allowlist 외 모든 `premortem` cite 0건 fail-closed.
7. `python3 scripts/sync_root_plugin_manifests.py --repo-root .` — export
   sync.
8. validator 통과, premortem-decision lens 1회 self-application으로 본 PR
   smoke.

이 slice 후 PR 2 (Leg 2 + Leg 1 bundle) — manifest + emit point + inventory가
같이 land. 그 후 PR 3 (Leg 3) 가 critique reference 안에 anchor 추가. PR 4
(Leg 4) 는 PR 2 시작 시점부터 parallel.

## Open Items

- Q1-Q4 (Probe Questions) — impl 진행 중 결정 시점 본 spec에 갱신.
- meta-retro (C-leg) — Leg 1 baseline 후 separate issue 정당화 또는 기각.
- premortem→critique rename 후 retro/handoff/recent-lessons.md cite의 자연어
  용례 ("premortem 단어가 본문에 자연스러운가") 가 어색해지는 경우 해당 본문도
  단어 갱신 (allowlist 아님).
