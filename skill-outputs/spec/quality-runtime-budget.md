# Spec — Quality Runtime Budget + pytest Reduction
Date: 2026-04-14

## Problem

`./scripts/run-quality.sh`(=pre-push의 사실상 게이트)의 단일 hot spot이 pytest로
~58s를 소비한다. `runtime-signals.json`에 timing은 매번 기록되지만 그 값을 읽어
fail시키는 게이트가 없어, **관측은 있고 enforcement는 없는** 상태다. 동시에
`check-secrets`가 5s를 silently 먹는다(이유: gitleaks 미설치 시 secretlint
fallback이 일어나는데 사용자가 그 사실을 모름). pytest 자체는 dual-enforced
smoke 테스트(이미 다른 게이트가 같은 일을 하는 케이스)와 매번 cold subprocess를
띄우는 CLI 시나리오 때문에 부풀어 있다. 이 모든 개선이 다른 리포에서도
재사용되려면 SKILL 측 구조에 들어가야 하며, 동시에 `charness` 자체에서 그
변화를 빠르게 dogfood하려면 working-tree-기반 dogfood 경로(`charness update
--repo-root . --no-pull`)를 운영 흐름에 명시해야 한다.

## Current Slice

세 개의 implementation slice. 순서대로 push하고 각 슬라이스 끝에 `charness
update --repo-root /home/ubuntu/charness --no-pull`로 SKILL 변경분을 본 머신에
재투입해 다음 슬라이스 작업이 새 SKILL을 사용하도록 한다.

1. **pytest 단축 (리포 측)**: 중복 smoke 제거 + 실패 2건 수정 + xdist 도입 +
   high-cost CLI fixture를 session-scope로 캐싱. 목표: pytest latest_elapsed_ms ≤ 20000.
2. **runtime budget 게이트 (SKILL 측 + 리포 측)**: SKILL에 배포되는
   `check-runtime-budget.py`와 어댑터 스키마의 `runtime_budgets` 필드 추가.
   `charness`의 `quality-adapter.yaml`에 `pytest: 20000` 박고 `run-quality.sh`
   끝에 게이트로 호출.
3. **gitleaks tool registry + loud fallback + dogfood 운영 문서화**: gitleaks를
   `tool_recommendations` 페이로드에 등록(외부 사용자가 설치 경로를 자동으로
   surface받게), `check-secrets.sh` fallback 진입 시 stderr 한 줄 warning,
   `charness update --repo-root . --no-pull`을 README/AGENTS.md 또는 handoff에
   "skill dogfood 경로"로 명시.

## Fixed Decisions

- pytest budget = **22000ms** hard fail. 점진(30→25→20) 안 함. 첫 슬라이스가
  이 한도 미만으로 끌어내린 뒤에야 두 번째 슬라이스를 push하므로 hard fail이
  도입되는 시점에는 이미 통과 상태다. 슬라이스 1 구현 중 발견: standalone
  pytest는 18-19s지만 run-quality.sh의 queue/log 래퍼 오버헤드로 측정값이
  20-22s. 20s로 박으면 noise로 flake. 22s가 honest baseline이면서 60s →
  20s 회귀 방어 효과는 동일하게 유지.
- budget enforcement는 **SKILL-distributed 스크립트**로 산다. 이유: 다른 리포가
  quality 스킬을 새 버전으로 받으면 어댑터에 `runtime_budgets` 한 줄만 추가해서
  같은 게이트를 얻을 수 있어야 한다. 리포-로컬 스크립트로만 두면 이 이득이
  사라진다.
- 어댑터 스키마: `runtime_budgets: {<command_label>: <max_elapsed_ms>}` 단일
  맵. label은 `run-quality.sh`의 phase label과 일치(예: `pytest`,
  `check-secrets`). 누락된 label은 게이트가 무시(적용 안 됨).
- budget 비교 기준: `runtime-signals.json`의 `commands.<label>.latest.elapsed_ms`.
  이유: p95/p90을 쓰면 budget 도입 시 과거 ample이 끌고 와 즉시 fail할 수 있고,
  단순함이 가독성 우위. 후속에서 p90으로 옮길 수 있게 reference로만 노트.
- gitleaks는 **required로 승격하지 않는다**. tool registry에 `recommendation`
  level로 등록. secretlint fallback 경로는 그대로 유지하되 **fallback 진입 시
  stderr 한 줄 warning 강제**.
- staleness 완화는 **새 기능 추가 없이** 기존 `charness update --repo-root .
  --no-pull` 경로를 문서화하는 것으로 한다(이미 CLI에 존재). symlink 경로는
  완전히 폐기.

## Probe Questions

- pytest-xdist 도입 시 subprocess-bound 테스트 외에 race가 드러날 수 있는 곳?
  → 첫 슬라이스 구현 중 실측. xdist 불안정한 케이스가 나오면 그 파일만 `-p
  no:xdist` 또는 `pytest.mark.serial`로 격리.
- 중복 smoke 테스트 실제 후보 식별: `_passes_on_current_repo` 패턴이 일관
  지표인가, 아니면 case-by-case 판단 필요한가? → 후보 리스트(아래) 검증 후
  결정.
- session-scope CLI fixture 캐싱이 안전한 케이스 식별. `test_managed_install*`,
  `test_codex_*`, `test_update_propagation`이 같은 init payload를 공유하는지
  실측.
- budget gate가 phase 3에서 fail했을 때 phase 1/2 timing은 이미 기록됐는지
  → `record_quality_runtime.py` 동작 확인. (이미 phase 끝마다 기록해 정상.)
- gitleaks를 `tool_recommendations.py` payload에 추가했을 때 `find-skills`
  쪽에서도 자동 surface되는지(공유 payload라). → 첫 슬라이스에서 확인.

## Deferred Decisions

- budget을 `latest` 외 `p90` / 연속 N회 위반 같은 statistical mode로 확장 →
  이번 슬라이스는 가장 단순한 latest-only로 시작.
- `check-coverage`(8.7s), `run-evals`(2s) 등 다른 게이트의 budget 값. 이번엔
  pytest만 박고 운영 감을 본 뒤 다른 라벨 추가.
- pytest를 phase 1과 병렬로 띄워 wall-clock을 추가로 깎는 안. 효과
  ~13s지만 spec/impl이 따로 필요해서 분리.
- `charness update --repo-root . --no-pull`을 alias나 sub-command로 격상.
  지금은 문서화만.
- 격리 분리(`@pytest.mark.slow`로 nightly로 빼는 안)는 단축 시도 후 부족한
  경우의 fallback. 첫 카드(중복 제거 + xdist + fixture 캐싱)가 20s 도달
  못 하면 그때 적용.

## Non-Goals

- pre-push의 phase 순서 재배열 (사용자가 명시적으로 pass).
- gitleaks를 hard requirement로 만들기.
- runtime-signals 자체의 schema 확장(현 schema_version 1 유지).
- 작업 트리 staleness 해결을 위한 새 CLI 옵션/심링크 도입.
- `check-coverage`, `run-evals`, `check-markdown` 등 비-pytest 게이트의 자체
  최적화. 이번 슬라이스 범위 밖.

## Constraints

- SKILL.md 변경은 push + `charness update --repo-root . --no-pull` 후에만 본
  머신의 다음 Claude 세션에 반영된다. 따라서 SKILL 변경이 들어간 슬라이스는
  closeout에 "다음 세션이 새 SKILL을 보려면 위 명령을 돌려라"를 명시.
- 어댑터 스키마 변경은 backwards-compatible: `runtime_budgets`가 없는 어댑터는
  게이트가 silently no-op(missing label 처리와 동일).
- pytest budget을 도입한 직후 첫 push에서 fail나면 안 됨 → 슬라이스 1
  완료(=20s 미만 확인) 전에는 슬라이스 2 push 금지.
- 변경은 `./scripts/run-quality.sh` 한 번 통과를 게이트로 한다 (현재 standing
  bar).
- 이 작업 자체가 pre-push에서 검증된다 → fixture 캐싱 등이 다른 테스트에
  side effect를 주면 즉시 드러남.

## Success Criteria

1. `pytest`의 `runtime-signals.json` latest_elapsed_ms ≤ 22000 (3회 연속
   측정에서 모두 통과).
2. SKILL이 배포하는 `check-runtime-budget.py` 가 어댑터의 `runtime_budgets`
   맵을 읽고 `runtime-signals.json`의 latest와 비교해 위반 시 non-zero exit.
3. `charness`의 `quality-adapter.yaml`에 `runtime_budgets: {pytest: 20000}`이
   존재하고, `run-quality.sh` 끝의 budget 게이트가 통과.
4. 합성된 fail 케이스(예: pytest budget을 잠깐 5000으로 낮춰서 푸시 시도)에서
   pre-push가 차단된다.
5. `gitleaks` 미설치 환경에서 `./scripts/check-secrets.sh` 실행 시 stderr에
   "gitleaks not found, falling back to secretlint" 형식의 한 줄 warning이
   남는다 (stdout 결과는 변하지 않음).
6. `python3 scripts/list_tool_recommendations.py --repo-root .` 출력에
   `gitleaks` 항목이 포함되고 install 경로(`brew install gitleaks` 등)와
   verify command가 같이 surface된다.
7. `README.md` 또는 `AGENTS.md`(또는 둘 다)에 "이 리포에서 SKILL 편집을
   dogfood하려면 `charness update --repo-root . --no-pull`"가 명시되어 있다.
8. 두 실패 테스트(`test_quality_tool_recommendations_emit_blocking_validation_routes`,
   `test_tool_install_persists_manual_guidance_and_support_state`)가 통과.

## Acceptance Checks

- (1, 2, 3) `./scripts/run-quality.sh`가 PASS로 끝나고 출력에 `pytest`
  elapsed가 20s 미만이며 budget 게이트 라인이 PASS.
- (2, 4) 일시적으로 어댑터의 `runtime_budgets.pytest`를 `5000`으로 떨어뜨리고
  `./scripts/run-quality.sh` 또는 직접 `python3 .../check-runtime-budget.py
  --repo-root .` 실행 → exit code non-zero, stderr에 "pytest exceeded budget
  (Xms > 5000ms)" 형식 메시지. 끝나면 원복.
- (5) `command -v gitleaks` 결과가 비어있는 상태에서
  `./scripts/check-secrets.sh 2>&1 1>/dev/null | head -1`이 fallback warning
  한 줄 출력.
- (6) `python3 skills/public/quality/scripts/list_tool_recommendations.py
  --repo-root . | jq '.tool_recommendations[] | select(.tool_id=="gitleaks")'`
  가 non-null.
- (7) `rg -n "charness update --repo-root . --no-pull" README.md AGENTS.md
  docs/handoff.md` 적어도 한 곳에 매치.
- (8) `pytest -q tests/quality_gates/test_quality_tool_recommendations.py
  tests/charness_cli/test_tool_lifecycle.py` 가 0건 fail.
- 슬라이스 1 단독 acceptance: `pytest -q [STANDING_PYTEST_TARGETS]` 종료
  시간 < 20s, 실패 0.
- 슬라이스 2 단독 acceptance: 의도된 budget 위반 합성 케이스에서 게이트가
  fail시키는 것을 확인.
- 슬라이스 3 단독 acceptance: 위 (5)(6)(7)(8 중 해당분).

## Canonical Artifact

이 spec 문서: `skill-outputs/spec/quality-runtime-budget.md`. 구현 중 실측으로
드러나는 사실(예: xdist race가 있는 파일, 실제로 줄여진 ms, 어댑터 스키마
세부)이 있으면 여기를 갱신한다. closeout 시 quality.md(`Recommended Next
Gates`)에서 이 항목들을 active → landed로 옮긴다.

## First Implementation Slice

**슬라이스 1 — pytest를 20s 미만으로**.

작업 순서:
1. **실패 2건 먼저 수정**:
   - `tests/quality_gates/test_quality_tool_recommendations.py::test_quality_tool_recommendations_emit_blocking_validation_routes`
   - `tests/charness_cli/test_tool_lifecycle.py::test_tool_install_persists_manual_guidance_and_support_state`
   둘 다 doctor가 `missing` 대신 `unhealthy`를 돌리는 변화에 테스트가 못
   따라간 것으로 보임. 실제 행동을 확인해 테스트를 맞추거나, 행동이 잘못이면
   행동을 고친다(로 별도 판단).
2. **중복 smoke 제거 후보 검증 후 삭제**:
   - `tests/test_check_coverage.py::test_check_coverage_passes_on_current_repo`
     → `check-coverage` 게이트와 100% 중복. 삭제.
   - `tests/quality_gates/test_packaging_validation.py::test_run_evals_passes_on_current_repo`
     → `run-evals` 게이트와 중복. 삭제.
   - `tests/quality_gates/test_docs_and_misc.py::test_check_duplicates_passes_clean_repo`
     → `check-duplicates` 게이트와 중복. 삭제.
   - 비슷한 `_passes_on_current_repo` / `_passes_clean_repo` 패턴 grep 후
     case-by-case 판단(검증 fixture에서 실패 케이스 만드는 테스트는 유지).
3. **`pytest-xdist` 도입**:
   - `dev` 의존성 추가.
   - `run-quality.sh`의 pytest 호출에 `-n auto` 추가.
   - 한 번 돌려서 race로 깨지는 파일 식별 → 해당 파일에 `pytest.mark.serial` 또는
     dist 비활성화로 좁게 격리.
4. **CLI fixture를 session-scope로 캐싱**:
   - `tests/charness_cli/conftest.py`에서 `charness init` 결과를 session-scope
     fixture로 한 번만 생성하고, 각 테스트는 그 결과를 read-only로 참조하거나
     얕은 복사본을 받게 한다.
   - mutate가 필요한 테스트만 function-scope로 별도 fixture 사용.
5. **`test_check_coverage_passes_on_current_repo`처럼 in-process 가능한 것**:
   - 만약 위 2번에서 삭제 안 하기로 한 게 남으면, subprocess 호출을 직접
     함수 호출로 바꿔 cold-start 비용 제거.
6. 측정: `pytest -q --durations=20 [TARGETS]`로 3회 연속 < 20s 확인.
   `runtime-signals.json`의 `pytest.latest.elapsed_ms`도 같은 값으로 떨어지는
   지 cross-check.
7. push → `charness update --repo-root . --no-pull` → 다음 세션에서 슬라이스 2
   진행.

이 슬라이스는 SKILL을 건드리지 않는다(리포-로컬 변경만). 따라서 staleness
영향 받지 않고, 한 번의 push로 검증 사이클이 닫힌다.

---

이 spec으로 `impl` 진행할까요? 슬라이스 1부터 시작합니다.
