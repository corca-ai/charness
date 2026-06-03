# Retro — #282/#283 해결 + v0.16.0 릴리스 낭비 회고

Mode: session

## Context

- 검토 대상: 이번 세션에서 #282(provider-safe goal closeout metrics) 해결, #283
  뮤테이션 수정 푸시, v0.16.0 릴리스 발행, 두 번의 fresh-eye 서브에이전트 크리틱.
- 다음에 중요한 것: 같은 결합면(handoff·near-limit 헬퍼) 편집에서 반복되는
  재작업을 줄이는 것.

## Evidence Summary

- 직접 관찰(대화 기록): 검증 실패/재작업 사이클, 푸시 거부, 리팩터 사이클.
- host-log probe(`probe_host_logs.py --format markdown`, 새 렌더러 dogfood):
  윈도우가 `not_requested`이고 최신 **Codex** 롤아웃(이 Claude 세션과 다른 호스트
  세션, spawn=9 등 내 서브에이전트 3개와 불일치)을 읽음 → 측정 수치를 이 세션
  비용으로 귀속할 수 없어 토큰/툴 카운트는 `unavailable`로 처리. (메트릭 윈도우
  부재가 thread-wide 감사를 세션 총량처럼 만드는, 바로 #282가 해결하려는 그
  현상을 dogfood가 실증함.)

## Waste

- **handoff 편집 캐스케이드 — 반복 트랩 2회차.** `docs/handoff.md` 마감 편집이 세
  검증을 연달아 깨뜨림: (a) MD004 — `+`로 시작한 연속 줄이 리스트 항목으로 파싱,
  (b) 인라인 코드 스팬 줄바꿈, (c) 70줄 상한 초과(73줄). 결과: push 1회 실패 +
  수정-재검증 3사이클 + amend 1회. recent-lessons에 이미 적힌 "handoff edit
  cascade" 트랩의 재발. 청커 커플링은 사전 점검했으나 70줄 상한·마크다운 규칙은
  점검하지 않음. (source: charness-artifacts/retro/2026-06-03-282-283-release-waste-retro.md)
- **goal_artifact_lib.py 길이 게이트 초과(366/360).** window 함수를 인라인으로
  먼저 추가 → 닫기 리허설에서야 하드 한도 초과 발견 → 별도 모듈
  `goal_metric_window_lib.py`로 추출 + 재노출 + 미러 재동기 + 재테스트. discipline
  문서가 명시한 "큰 추가 전 `--headroom` 점검"을 생략해 1 사이클 낭비.
  (source: charness-artifacts/retro/2026-06-03-282-283-release-waste-retro.md)
- **릴리스 publish 1회 거부(dirty worktree).** `tee .charness/release-exec.log`가
  추적 안 되는 파일을 만들어 `publish_release`의 clean-worktree 요구로 거부 →
  백그라운드 실행 1회 낭비. 하니스가 백그라운드 출력을 task 파일에 이미 캡처하므로
  tee는 불필요했음. (source: charness-artifacts/retro/2026-06-03-282-283-release-waste-retro.md)
- 낭비 아님(올바른 투자): 두 fresh-eye 크리틱이 각각 실제 블로커(재발 미방지,
  릴리스 크리틱 게이트 누락)를 발견; 기존 probe/audit 인프라 재사용으로 재구축 회피.

## Critical Decisions

- 기존 파싱/감사 인프라 재사용하고 렌더러+레코더+신호 갭만 채움 → 스코프 최소화.
- `metric_window` 신호를 하드 게이트가 아닌 non-blocking으로 → 호스트가 타임스탬프
  없는 `unavailable` 케이스를 정당하게 허용(릴리스 크리틱 블로커를 이 결정으로 흡수).
- #283을 강제 종료하지 않음 — 닫힘은 예약된 mutation-tests.yml CI 점수에 귀속.

## Expert Counterfactuals

- Kent Beck("make the change easy, then make the easy change"): handoff·near-limit
  헬퍼를 건드리기 전에 알려진 커플링(70줄 상한, 마크다운 인라인/리스트 규칙,
  `--headroom`)을 먼저 점검했다면 두 캐스케이드를 모두 회피. 바뀌는 행동 =
  "결합면 편집 전 커플링 사전점검".
- Don Norman(forcing function): `tee`로 worktree를 더럽힌 실수는 "헬퍼 출력은
  worktree 밖으로"라는 강제장치 부재에서 비롯 — 규칙을 습관이 아닌 구조로.

## Next Improvements

- workflow: `docs/handoff.md` 편집 전 3대 커플링 일괄 사전점검 — 줄 수 vs 70,
  `check-markdown`(인라인 스팬/리스트 스타일), `check-doc-links`(백틱 경로 금지).
- workflow: clean-worktree를 요구하는 헬퍼 실행 시 `tee <repo경로>` 금지 — 하니스
  백그라운드 캡처를 쓰거나 worktree 밖 경로에 기록.
- workflow: 근접-한도 헬퍼에 큰 추가(>40줄) 전 `check_python_lengths.py --headroom`
  선점검.
- capability/memory: handoff 캐스케이드가 2회차 재발 → 구조적 수정 후보(handoff
  전용 통합 프리체크 헬퍼 또는 줄 상한 소폭 상향). 이번엔 미구현, issue 후보로 기록.

## Sibling Search

- workflow axis: 결합면을 알려진 커플링 점검 없이 편집(handoff 70줄/마크다운/링크,
  생성 미러 sync, 길이 게이트) | decision: durable fix는 위 "편집 전 커플링
  사전점검" 습관(메모리에 기록); handoff는 이미 3개 게이트로 보호되나 통합 프리체크는
  부재 → issue 후보 | proof: 이번 세 실패 모두 이미 존재하는 게이트
  (validate_handoff_artifact 70줄, check-markdown, check_python_lengths)가 사후에
  잡아낸 규칙이었음.
- capability axis: near-limit 헬퍼 추가 시 사전 `--headroom` 미사용 | decision:
  in-slice 코드 패치 불필요 — discipline 문서가 이미 명시, 빠진 건 습관이며 슬라이스
  닫기에서 자동 표면화됨 | proof: 366/360 초과는 닫기 리허설에서 잡혔고, 추출 후
  350대로 복귀.

## Persisted
