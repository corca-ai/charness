# 2026-05-09 debug ↔ issue substrate-vs-target spec slice

## Mode

`session`

## Context

charness 플러그인의 `debug` skill (RCA/falsifiable hypothesis substrate)와
`issue` skill (close-ledger lifecycle target) 사이의 silent overlap 분리 spec
slice. handoff Next Session item 1에서 시작. 사용자 명시로 GitHub issue 없이
spec 단독 진행. Canonical artifact = `charness-artifacts/spec/debug-issue-
substrate-vs-target.md`. 본 슬라이스는 contract land만; First Implementation
Slice (7 step atomic)는 별도. commit `21c348d` unpushed (push gate는 impl 묶음
까지).

## Waste

- **Pre-commit `check-doc-links` missing-artifact fail**. handoff item 1을
  갱신할 때 미존재 future-path `skills/public/debug/references/five-whys-
  causal-chain.md`를 backtick 안에 인용 — hook이 "backticked file reference
  ... use markdown links so renames do not rot"으로 차단. 평문 표기 (디렉토리
  backtick + 파일명 평문)로 풀고 재 commit. 미리 mental model이 없어 1회
  retry 비용.
- **Spec 첫 draft의 internal contradiction**. P1 (이전 reference path)은
  Probe Question으로 두고 First Implementation Slice step 2는 default (a)
  path를 본문 hard-code — Hidden Sequencing critique A3.3가 "Probe인 척
  Fixed" 패턴으로 surface. 같은 모양이 P4에서도 (step 4가 default (a)
  wording authoring). spec critique이 surface하기 전엔 self-detect 못 함.
- **Acceptance Checks 미분리**. 첫 draft가 spec-slice (본 파일 land + critique
  fold) 와 impl-slice (validators + grep + dogfood)를 한 block에 섞어둠. 본
  슬라이스가 spec 단독인데 validator가 acceptance에 listed → category error.
  Hidden Sequencing critique A3.5 catch.

## Critical Decisions

- **GitHub issue 없이 spec 단독 진행** (사용자 명시). handoff item 1 본문이
  "새 GitHub issue + 새 spec"이라는 보수적 sequence였지만 실용적 단축. spec
  파일이 contract owner 단독.
- **Substrate-vs-target 패턴이 두 skill 보존 케이스에도 적용 가능**하다는
  인지. #135 Leg 5는 *단일 skill rename + reference 흡수* (`premortem` →
  `critique` substrate, target lens가 reference로); 우리는 *두 skill 보존 +
  ownership 재할당* (debug = substrate skill, issue/causal-review.md =
  close-ledger target lens). 다른 모양이지만 동형 — Fixed Decisions에 cite.
- **Counterweight subagent를 angle subagent와 *parallel* spawn**. angle
  결과를 보지 않은 독립 perspective 확보. counterweight가 "grep → AST
  unit-test upgrade", "dogfood ≥3 scenario", "external announcement", "debug
  → rca rename" 등 over-engineering 요청을 미리 Over-Worry bin으로 차단해
  4-bin triage가 안정.
- **Spec-slice ↔ impl-slice acceptance 분리** 첫 명시 적용. 본 contract가
  spec 단독 land이면 validator/grep/dogfood acceptance는 impl-slice — slice
  scope 명료화. Hidden Sequencing critique consumed로 spec에 fold.

## Expert Counterfactuals

- **Donella Meadows (시스템 사고, leverage points)**: "위계 안의 동일 패턴
  layer 식별 후 single-owner 명명". substrate-vs-target 분리는 systems-
  thinking 의 leverage point — 두 skill에 분산된 RCA discipline을 한 owner
  로 모으면 drift 가능성이 줄어든다. Meadows lens면 spec 첫 draft에 "leverage
  = single-owner of structural-cause discipline; drift cost = 두 곳 reword
  divergence"를 한 줄로 정렬해 Problem 섹션이 더 강하게 lock됨. 본 spec은
  Problem이 정확히 그 lens였지만 명시 어휘는 critique fold 후에야 sharpened.
- **Christopher Alexander (생성적 순서, uncertainty 줄이는 move 먼저)**: "lock
  가능한 것은 spec lock-in 전에 lock". P1 default (a) 를 spec 첫 draft에서
  Fixed로 두면 critique이 surface하는 self-contradiction 1 cycle 절약. P2-P4
  는 진짜 dogfood 필요한 Probe만 남김. Alexander lens면 spec 작성 시 매번
  Probe 항목 별로 "이 question의 default가 본문 step에서 hard-code 되는가?
  되면 Fixed로 promote"라는 self-check가 자연.

## Next Improvements

- **memory** (본 retro가 lesson persistence): 미존재 future-path를 handoff/
  spec/PR-description에서 인용할 때 backtick 안에 둘 단일 path가 들어가지
  않게. 옵션: (a) 디렉토리만 backtick + 파일명 평문, (b) 본문 평문 표기, (c)
  파일이 land된 commit에서만 markdown link로 표기. 본 retro의 첫 lesson.
- **memory**: spec-slice ↔ impl-slice acceptance 분리가 본 슬라이스에서
  처음 명시 적용. 다음 spec slice는 이 구분을 spec 첫 draft에 직접 fold —
  spec section이 "Spec-slice acceptance" 와 "Impl-slice acceptance" 두 sub-
  block으로 나뉘는 형식. recent-lessons.md에 surface.
- **workflow**: spec 첫 draft 자체 self-check — "Probe Questions 각 항목에
  대해, default가 First Implementation Slice 본문에 hard-code 되어 있다면
  Fixed로 promote해야 한다". critique이 surface 하기 전에 self-detect 가능.
  recent-lessons.md repeat-trap 후보로 surface (반복 시 contract test로
  upgrade).
- **workflow**: critique invocation 시 counterweight subagent를 angle
  subagent와 *parallel* spawn (counterweight가 angle 결과를 보지 않은 독립
  perspective). 본 슬라이스에서 valuable했으므로 다음 critique 호출도 같은
  병렬 패턴. 직렬 spawn (angle 후 counterweight)은 counterweight가 angle
  결과 anchored 되어 over-worry 차단력이 약해짐.
- **capability**: pre-commit `check-doc-links` hook의 missing-artifact 메시지
  enhancement — 현재는 "use markdown links so renames do not rot"이지만
  미존재 path 케이스는 "use plain text for not-yet-created paths" 같은
  ramification이 더 정확. 단일 패턴, capability 변경은 미루고 다음 회 같은
  트랩 반복 시 짓는다 (recent-lessons "한 번 패턴이라 capability 변경은
  미루고 다음 회 같은 트랩이 반복되면 그때 짓는다" 휴리스틱 동형).

## Persisted

yes — `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-
spec.md` (본 파일).
