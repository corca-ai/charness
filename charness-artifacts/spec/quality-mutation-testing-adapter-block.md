# quality mutation_testing adapter block + propose flow

## Problem

charness consumer repos에 mutation testing 설치를 도와주려면, 현재 `quality`
스킬은 어떤 mutation testing 도구도 모르고, `quality-adapter.yaml`에 대응 슬롯
이 없으며, consumer 리포로 install 가능한 워크플로 템플릿도 없다. craken-agents
가 보유한 `.github/workflows/mutation-tests.yml` + Stryker 지원 자산은 모든 설정
이 Node/TypeScript/Stryker에 hardcode되어 있어 다른 stack에 그대로 옮길 수 없다.
charness는 harness 포터빌리티 정책상 stack 결합 자산을 직접 들고 올 수 없다.

이 작업은 stack-agnostic 추상화 한 층을 `quality` 스킬에 도입한다: 단일
`quality-adapter.yaml` 안에 `mutation_testing` 블록 한 개를 추가하고, 어댑터가
비어 있으면 `quality` 실행 중 "설치할까?"를 propose, 어댑터가 채워져 있으면
워크플로 템플릿 install 및 score break 감시까지 한 흐름으로 이어준다.
capability 매니페스트, integration tool 매니페스트, stack별 helper는 신설하지
않는다.

## Current Slice

`mutation_testing` 어댑터 블록 + 검증 + 기본값 + 예제 + 어댑터 컨트랙트 문서
+ propose 프로브 스크립트 1개 + 워크플로 템플릿 1장 + references 1장 +
`quality` SKILL.md 본문에 detect/propose 단계 wiring. 모든 stack-specific
헬퍼는 consumer 리포 소유로 남긴다 (craken-agents의 `bin/mutation-*.mjs`는
그대로 craken-agents에서 살아 있다).

## Fixed Decisions

- **단일 어댑터 블록**: `<repo-root>/.agents/quality-adapter.yaml`의 새 top-level
  키 `mutation_testing`. 별도 capability/integration manifest 신설 안 함.
- **stack-agnostic command slot**: 어댑터의 `mutation_testing.commands.{dry_run,
  full, sample, summary}` 4개 슬롯이 stack과 도구를 가린다. charness는 어떤
  도구도 직접 호출하지 않는다.
- **default value origin**: craken-agents `.github/workflows/mutation-tests.yml`
  (2026-05-14 시점 SHA pin)이 정책 기본값의 출처다. 단 stack-결합 라인은
  탈Stryker화한다 (`stryker.log → run.log`, craken marker 제거). 채택 값:
  `score_break: 60`, `schedule_cron: "17 */3 * * *"`, `changed_quota: 5`,
  `max_files: 10`, `auto_issue.enabled: true`,
  `auto_issue.label: "mutation-test"`,
  `auto_issue.title: "Mutation test regression on main"`,
  `auto_issue.marker_token: "mutation-test-regression"` (워크플로가 런타임에
  `<!-- ${{ github.repository }}-${marker_token} -->`로 조합 — 소비 리포 간
  marker collision 방지),
  `workflow_path: ".github/workflows/mutation-tests.yml"`,
  `report_paths.summary_md: "reports/mutation/summary.md"`,
  `report_paths.sample_md: "reports/mutation/sample.md"`,
  `report_paths.log: "reports/mutation/run.log"`.
- **DEFAULT_MUTATION_TESTING은 stack-neutral**: `quality_policy_defaults.py`의
  default는 구조적 슬롯과 craken 출처 정책 값만 들고, **`commands.*`는 모두
  빈 문자열** (스택 도구 가정 없음), `auto_issue.enabled` 기본도 false
  (consumer가 명시 opt-in)로 해서 init_adapter가 portable-defaults preset에
  Stryker 가정을 새기지 않게 한다. Stryker-구체 라인은
  `presets/typescript-quality.md` 권장 라인 후속 슬라이스(Deferred Follow-ups
  참고)로 분리.
- **commands.sample의 출력 컨트랙트**: `commands.sample`이 실행되면 stdout으로
  개행 분리 파일 목록을 쓰고, 동시에 `GITHUB_OUTPUT`에 `sample_files=<공백
  분리 목록>`을 추가한다. 워크플로는 그 목록을 환경 변수로 받아 `commands.full`
  에 `MUTATION_SAMPLE_FILES`로 노출한다. 결과적으로 Stryker 어댑터는
  `commands.full`을 `"npm run test:mutation -- --mutate $MUTATION_SAMPLE_FILES"`
  처럼 정의하고, mutmut/cosmic-ray 어댑터는 같은 env 변수를 자기 방식대로 쓴다.
  charness는 CLI flag shape (`--mutate`)를 고정하지 않는다.
- **unknown sub-key는 warning, error 아님** (precedent 정렬): 기존 mapping
  validator (`validate_coverage_floor_policy`, `validate_prompt_asset_policy`,
  `runtime_budgets` 등)는 모두 unknown sub-key를 silent ignore한다. spec 초안
  의 "error로 reject" 결정은 false precedent였다. `_apply_mutation_testing`
  은 알려진 sub-key만 validate하고, 알려지지 않은 sub-key는 warnings 리스트에
  "unknown mutation_testing sub-key: <name>" 한 줄을 적고 통과시킨다. 향후
  charness 전체 adapter validator에 일관 strict 정책을 도입할지는 별도
  슬라이스 결정.
- **어댑터 부재 / 블록 부재 fallback**: top-level `mutation_testing` key가
  없을 때 `_apply_mutation_testing`은 즉시 None을 리턴해 validated dict에
  아무것도 쓰지 않는다 (errors 0, warnings 0). `infer_quality_defaults`가
  `mutation_testing: <DEFAULT>` 를 미리 채워둔 상태이므로 caller는 항상 dict
  를 본다. 이 path는 acceptance check로 명시 (a1의 5번째 fixture).
- **commands.summary contract**: charness는 stack-specific report parser를 ship
  하지 않는다. consumer가 `commands.summary`로 지정하는 명령은 두 가지 책임을
  진다: (1) `report_paths.summary_md`로 사람-읽을 요약을 작성한다. (2) score
  break violation 시 비-0으로 종료한다 (workflow는 exit code만 본다). craken
  -agents의 `npm run test:mutation:ci-summary`는 이 컨트랙트를 이미 만족한다.
  이 결정은 charness가 stack helper를 들고 오지 않는 핵심 이유다.
- **detect: 어댑터 블록 부재 또는 commands 미설정으로 판정**: `mutation_testing`
  key 자체가 없거나, `commands.full`이 비어 있으면 "미설치"로 친다.
  `auto_issue.enabled: false`만 설정된 부분 셋업은 미설치가 아니다.
- **propose는 quality 본 실행의 마지막 phase에서**: detect 미설치 → quality
  본 실행 결과 보고 직후 한 줄 propose ("mutation testing이 어댑터에 없습니다.
  설치할까요?"). 수락 시: (a) 어댑터에 `mutation_testing` 스캐폴드 블록 append,
  (b) `workflow_path`로 템플릿 install. propose는 quality 본 실행을 막지 않는다.
- **template은 어댑터 슬롯을 런타임에 읽는다 (cron은 예외)**: 워크플로 첫
  step이 `yq`로 어댑터를 파싱해 `commands.*`, `auto_issue.*`, `report_paths.*`
  를 `${{ steps.adapter.outputs.* }}`로 노출한다. 예외는 `schedule.cron`:
  GitHub Actions가 `on.schedule`을 job step 이전에 파싱하므로 런타임 어댑터
  read가 닿지 않는다. 따라서 `mutation_testing.schedule_cron`은 propose probe
  `--execute`가 템플릿을 install할 때 1회 substitute한다. cron을 바꾸려면
  어댑터를 수정한 뒤 `--execute`를 재실행해 워크플로를 다시 렌더한다. 다른
  슬롯은 어댑터가 단일 source of truth.
- **template hosting**: `skills/public/quality/scripts/templates/mutation-tests.yml`.
  `presets/`나 `packaging/`이 아니다 (presets는 advisory vocabulary 문서, packaging
  은 plugin 배포 메타). 템플릿 install은 detect/propose가 단독으로 책임진다.
- **stack-specific helper는 consumer-owned**: craken-agents의 sampler/summarizer
  helper는 craken-agents에 머문다. charness는 어떤 mjs/py 파일도 신설하지 않는다
  (단, propose probe script 1개와 install helper는 charness 자산).

## Probe Questions

- **어댑터 슬롯 명명**: `commands.{dry_run, full, sample, summary}` 4개 슬롯이
  craken 모드 3종(dry-run / sample-then-full / summary)을 표현하는 최소 분해인가,
  아니면 stack에 따라 `sample`이 의미 없어 `commands.run` 1개로 통합 가능한가.
  첫 dogfood (charness 자체 또는 craken-agents 변환) 후에 확정한다. 초기는 4
  슬롯으로 간다.
- **workflow가 어댑터를 어떻게 파싱하느냐**: 표준 GitHub Actions에는 YAML 파서
  step이 기본 제공되지 않는다. `yq` 또는 `python -c` 둘 다 후보. 첫 install
  타깃 (Linux runner) 위에서 작은 검증을 거쳐 확정한다. 초기는 `yq`
  (uses: mikefarah/yq 또는 brew/pre-installed) 가 깔끔하나 hosted runner 가용성
  확인 필요. fallback은 `python -c "import yaml; ..."`.
- **propose 거부 시 재제안 주기**: 한 번 거부하면 영원히 제안 안 함 vs. 매번
  제안. 한 번 거부 후 어댑터에 `mutation_testing.declined: true` 한 줄을 적어
  silenced 상태를 명시한다. 그 후엔 quality가 한 줄 "declined; remove flag to
  reopen" 노트만 띄운다. 첫 dogfood에서 어댑터 본문 mutate가 부담스럽다고 판단
  되면 별도 `.agents/quality-decisions.yaml` 같은 분리 파일로 옮긴다.
- **score break violation의 quality gate 통합**: 현재는 워크플로 단독 실행만
  가정. quality 본 실행에서 `summary.md`의 score를 읽어 standing gate로
  통합할지는 (i) consumer가 mutation을 standing gate에 포함하길 원하는지,
  (ii) score 읽기가 cheap한지에 달려 있다. 첫 dogfood 후 결정. 초기 슬라이스는
  통합하지 않고 워크플로 결과만 GitHub UI에서 본다.

## Deferred Decisions

- **Python/Ruby/Go stack 가이드**: `presets/python-quality.md` 등에
  `mutation_testing.commands`의 mutmut/cosmic-ray/mutant 권장 라인 추가는 첫
  non-TS dogfood 후. 본 슬라이스는 TS dogfood만 가정.
- **워크플로 outside of GitHub Actions**: GitLab CI / Buildkite / Jenkins용
  템플릿 분기는 첫 non-GitHub consumer 등장 후. 초기는 GitHub Actions only.
- **mutation report의 history 보존**: craken-agents는 14일 retention의 actions
  artifact만 보존한다. charness가 `charness-artifacts/mutation/` 같은
  durable artifact 정책을 들고 올지는 score trend 분석 demand 누적 후.
- **PR comment 통합**: craken-agents는 PR dry-run을 actions artifact로만
  push한다. PR에 score delta 댓글을 자동으로 다는 흐름은 향후 결정.
- **multi-language repo**: 한 어댑터 안에 `mutation_testing.commands` 한 벌만
  들어간다. Python+TS 모놀리포에서 두 도구를 병행하려면 어댑터 schema
  확장이 필요. 본 슬라이스 외.

## Non-Goals

- Stryker(JS/TS)나 mutmut(Python) 같은 mutation testing 도구 자체를 charness가
  ship하지 않는다.
- consumer 리포의 mutation testing 정책(어떤 파일을 mutate하나, exclude list)
  은 어댑터의 `commands.*` 슬롯이 호출하는 도구의 설정 파일이 소유한다.
  charness는 mutate target glob을 알지 않는다.
- score break threshold tuning은 어댑터가 소유한다. charness는 craken 기본값
  60을 default로만 제공한다.
- mutation testing이 charness의 standing gate가 되지 않는다 (선택적 확장).

## Deliberately Not Doing

- `integrations/capabilities/mutation-testing.json` 신설. 초기 sketch에 있었으나
  단일 어댑터 블록으로 충분히 표현되어 불필요.
- `integrations/tools/stryker.json` 신설. consumer가 Stryker를 쓰든 mutmut을
  쓰든 charness는 도구를 직접 알 필요가 없다 (commands slot이 추상화).
- charness 본체에 `mutation-sample-files.mjs` / `mutation-report-summary.mjs`
  유사 helper script 신설. 두 파일은 Stryker의 출력 스키마 (`status: killed
  /survived/nocoverage/...`)를 알아야 동작하므로 stack helper이며, consumer
  소유로 남긴다.
- `charness:mutation-testing` 신규 public skill 분리. `quality`의 자연스러운
  detect/propose 확장으로 충분.
- 어댑터 변수의 template-time substitution. 단일 source of truth를 어댑터로
  못 박기 위해 워크플로 런타임 파싱을 채택.

## Constraints

- harness portability (CLAUDE.md): stack-specific behavior는 어댑터/preset/
  integration manifest로 격리. charness 본체에 Node/Stryker 가정 금지.
- adapter contract (skills/public/quality/references/adapter-contract.md):
  새 필드는 `quality_adapter_lib.py`의 `infer_quality_defaults`, validator
  체인, `init_adapter.py`의 `build_items`, `adapter.example.yaml`, 그리고
  `adapter-contract.md` 5곳 동시 갱신.
- defaults는 `scripts/quality_policy_defaults.py`에 `DEFAULT_MUTATION_TESTING`
  로 추가. craken 출처를 주석으로 명시.
- 어댑터 블록 validator는 mapping shape + 알려진 key 화이트리스트 + 타입 체크
  (string, int, bool, list[str]). 알려지지 않은 key는 warnings 리스트에
  기록만 하고 통과 (Fixed Decisions 정렬, 기존 mapping precedent 따름).
- propose probe는 `quality` SKILL.md의 마지막 review/recommendation 단계에서
  호출된다. read-only quality phase는 propose를 trigger하지 않는다 (write
  side effect 분리).
- 워크플로 템플릿은 craken-agents 골격을 1:1로 보존하되 stack-결합 라인만
  어댑터 슬롯으로 치환. cron, concurrency, permissions, plan step의 SHA
  중복 가드 로직, schedule/PR/dispatch mode 분기, artifact upload, auto-issue
  open/close, fail step은 동일하게 들고 온다.

## Success Criteria

1. `quality-adapter.yaml`에 `mutation_testing` 블록이 있는 리포에서
   `python3 skills/public/quality/scripts/resolve_adapter.py --repo-root .` 출력
   `data.mutation_testing`이 craken 기본값 + 사용자 override 병합 결과로 나온다.
2. 어댑터에 `mutation_testing` 블록이 없을 때 resolve_adapter는 defaults에
   `mutation_testing` 키를 빈 mapping (또는 `enabled: false` 마커)으로 채우며
   propose probe가 "미설치"로 판정한다.
3. propose probe (`python3 skills/public/quality/scripts/propose_mutation_testing
   .py --repo-root .`)는 JSON으로 `{status: "missing"|"installed"|"declined",
   recommendation: <propose message>, install_actions: [...]}` 를 출력한다.
4. 알려지지 않은 key를 넣은 어댑터 fixture는 `load_quality_adapter`가 errors
   리스트에 메시지를 채우고 `valid: false`를 리턴한다.
5. 어댑터에서 `commands.full`만 채운 부분 셋업은 `valid: true`이며, propose
   probe는 "installed"로 판정한다. `commands.full`이 비어 있고 `declined: true`
   면 "declined"로 판정한다.
6. `quality` SKILL.md 본문에서 새 propose 단계가 read-only phase 밖에 위치하며
   reference (`skills/public/quality/references/mutation-testing.md`)를 cite
   한다.
7. 워크플로 템플릿 `skills/public/quality/scripts/templates/mutation-tests.yml`
   은 craken-agents의 워크플로와 동일한 mode 3종 분기 + auto-issue 로직을
   보존하며, 모든 `npm run` 라인이 `${{ env.MUTATION_CMD_* }}` 또는
   `${{ steps.adapter.outputs.* }}`로 어댑터 슬롯에서 주입된다.
8. 템플릿 첫 step에서 어댑터를 파싱해 env로 export하는 step의 dry-run (`yq`
   또는 `python -c`로 craken fixture를 파싱)이 craken 기본값과 동일한 명령
   문자열을 생성한다.
9. 모든 신규/수정 surface가 `python3 scripts/sync_root_plugin_manifests.py
   --repo-root .` 동기화 후 깨끗하다.

## Acceptance Checks

- **a1**: `tests/control_plane/test_quality_adapter.py` (또는 기존 quality
  adapter 테스트 파일)에 `mutation_testing` 블록 fixture 5개 — full,
  partial(commands.full only), declined, **no-block-at-all**(top-level key
  부재), **unknown sub-key**(`commands.weird: "x"`) — 를 추가한다. 각각:
  full → valid + 모든 슬롯 값 채움, partial → valid + propose probe가
  "installed" 판정, declined → valid + propose probe가 "declined" 판정,
  no-block → valid + warnings 0 errors 0 + propose probe가 "missing" 판정,
  unknown sub-key → valid + warnings에 "unknown mutation_testing sub-key:
  weird" 메시지 + 알려진 슬롯은 정상 채움. Success Criteria 1,2,4,5에 대응.
- **a2**: 잘못된 타입 fixture (예: `score_break: "high"`) 가 errors 리스트
  에 들어가 `valid: false`를 만든다는 네거티브 케이스. Success Criteria 4에
  대응.
- **a3**: propose probe의 fixture 기반 단위 테스트 — 어댑터가 없을 때
  / commands.full 비어 있을 때 / 채워졌을 때 / declined 일 때
  / declined를 제거(remove flag)했을 때(recovery) 5 케이스의 JSON 출력을
  단언. recovery 케이스는 declined-true fixture를 declined 제거 후 재로드
  해 propose가 다시 "missing"으로 돌아오는지 본다. Success Criteria 2,3,5에
  대응.
- **a4**: 워크플로 템플릿의 골격을 craken-agents 원본과 1:1 line-by-line으로
  비교하는 골든 텍스트 테스트는 *하지 않는다* (drift 잦음). 대신:
  (i) mode 분기 3개 step name, auto-issue step name, fail step 존재를 grep
  으로 단언, (ii) **negative grep**: `^\s*run:.*\bnpm\b` 가 0건이며 도구
  literal (`stryker`, `mutmut`, `npm`, `yarn`, `pnpm`)이 `run:` 라인에 없다.
  Success Criteria 7에 대응.
- **a5**: 어댑터 파싱 step의 작은 셸 fixture 시뮬레이션 — craken-agents
  defaults가 들어간 임시 yaml을 `yq -r .mutation_testing.commands.{dry_run,
  full,sample,summary}` 네 슬롯 모두로 parse해 craken 원본 명령 문자열
  ("npm run test:mutation:dry-run", "npm run test:mutation",
  "npm run test:mutation:sample", "npm run test:mutation:ci-summary") 가
  나오는지 확인. Success Criteria 8에 대응.
- **a6**: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
  실행 후 git diff 비어 있음. Success Criteria 9에 대응.
- **a7**: 플러그인 export 검증 — sync 실행 후 `plugins/charness/skills/quality
  /scripts/templates/mutation-tests.yml` 와 `plugins/charness/skills/quality
  /scripts/propose_mutation_testing.py` 가 존재한다. (templates는 새 서브
  디렉터리이므로 `packaging_lib.copy_tree`가 자동으로 mirror하는지 확인 필요;
  안 되면 `packaging/charness.json` include 한 줄 추가.)
- **a8**: docs/conventions/implementation-discipline.md의 sync-before-verify
  순서대로 작업했음을 closeout 시 reviewer가 확인 (commit 메시지 또는
  retro 노트에 명시).

## Critique

2026-05-14 bounded fresh-eye critique (3 angle + 1 counterweight, all parent-
delegated). Packet:
`charness-artifacts/critique/2026-05-14-084100-packet.md`.

**Act Before Ship (이번 슬라이스에 inline 반영 — 위 Fixed Decisions / Acceptance
Checks가 이미 반영):**

- A2-3: 워크플로 auto-issue marker가 craken 리터럴 (`<!-- craken-mutation-test-
  regression -->`)이면 모든 consumer 이슈 트래커에 craken 브랜딩이 새겨지고
  multi-repo 환경에서 marker collision 발생. → `auto_issue.marker_token` 어댑터
  슬롯 + 워크플로 런타임에 `${{ github.repository }}` prefix 조합으로 해결.
- A3-1: spec 초안의 "unknown sub-key를 error로 reject"는 false precedent
  (`validate_coverage_floor_policy:83-109`, `validate_prompt_asset_policy:112-
  128`, `adapter_validators.runtime_budgets:17-31` 등 모두 silent ignore).
  → Fixed Decisions에서 "warning 기록 + 통과" 정책으로 정렬, 추후 전체 strict
  정책 도입은 별도 슬라이스.
- A3-5: `init_adapter.py`가 `portable-defaults` preset 스캐폴드에 Stryker-flavored
  paths를 새기면 Non-Goal 위반. → `DEFAULT_MUTATION_TESTING`은 stack-neutral
  (commands 비움, auto_issue.enabled false)로 좁히고 Stryker 라인은
  `presets/typescript-quality.md` 권장 라인 후속 슬라이스로.
- A2-5: `commands.sample` 출력 컨트랙트 미정. Stryker `--mutate` flag shape에
  암묵적으로 묶여 있음. → stdout 개행 분리 + `GITHUB_OUTPUT.sample_files`
  컨트랙트로 정의, full 명령이 `MUTATION_SAMPLE_FILES` env로 받는다.
- A2-4: `report_paths.log` 기본값 `stryker.log` → `run.log`로 변경 (Stryker
  literal 제거).

**Bundle Anyway (Acceptance Checks에 반영):**

- A1-5: SC 7 grep negative (`^\s*run:.*\bnpm\b` 0건 + Stryker/mutmut literal 0건)
  를 a4에 추가.
- A1-6: a5의 yq parse를 4개 슬롯 모두로 확장.
- A3-3: a7 신설 — sync 실행 후 plugin export에 새 template + propose 스크립트
  존재 확인.

**Over-Worry (반영 안 함):**

- A1-1: validator-errors-block-propose는 SKILL.md 단계 ordering으로 절차적
  처리; 별도 fixture는 double-counting. a1+a3가 간접 커버.
- A1-2 / A3-2 / A1-3: 모두 "absent block / declined / recovery"의 fixture
  변형. a1/a3가 통합 커버 (위에서 5+5 case로 확장 반영).
- A1-4: 구현 순서 안전; 행동 없음.
- A2-1: `yq` non-Ubuntu 가용성은 spec의 Probe Question 유지 (`python -c`
  fallback 결정은 첫 dogfood 후). 본 슬라이스 install target이 Ubuntu라
  실제 차단은 아니다.
- A2-2: `summary.md` markdown shape은 consumer 소유 (Non-Goal). charness가
  형식을 강제하지 않는다.
- A2-6: workflow checkout-per-run 모델이라 mid-run drift는 비-시나리오.
- A3-6: craken-agents 마이그레이션 시 propose noise는 의도된 UX. 별도 prep
  필요 없음.
- A3-7: `recent-lessons.md`는 read input이지 write target 아님.

**Valid But Defer:**

- A3-4: 어댑터 write-back 안전성 (ruamel.yaml vs append-text). 초기 슬라이스
  는 fenced marker append (`# >>> mutation_testing (charness propose) >>>` /
  `# <<< mutation_testing >>>`)로 충분 — 단일 writer, idempotent. 두 번째
  writer가 등장하거나 사용자 편집 충돌 사례가 잡히면 ruamel 도입. Deferred
  Follow-ups에 명시.

**Fresh-Eye Satisfaction:** parent-delegated (3 angles + 1 counterweight as
bounded subagents). 호스트가 spawn을 차단하지 않았고, nested 위임은 요청되지
않음.

### Closeout critique (post-impl, 2026-05-14)

Code-critique target on the implemented slice. 1 angle subagent. Findings
acted before commit:

- **F1 (blocker, fixed)**: 워크플로 템플릿의 `schedule.cron`이 리터럴 placeholder
  였음. cron은 런타임 어댑터 파싱 이전에 GitHub Actions가 읽으므로 runtime
  resolution 불가. → propose `--execute`가 template 복사 시 1회 substitute.
  Fixed Decisions 정렬, a3 install 테스트가 placeholder 부재 + cron 값 확인.
- **F2 (bundle-anyway, fixed)**: `${{ steps.adapter.outputs.cmd_* }}` splicing의
  quoting 위험. → `references/mutation-testing.md`에 "Slot quoting" 단락 추가.
- **F6 (bundle-anyway, fixed)**: `--execute`가 어댑터 부재 상태에서 header 없는
  파일을 생성하면 valid 어댑터가 안 됨. → `init_adapter` 선행 요구로 거부;
  추가 acceptance test (`test_a3_execute_refuses_without_adapter`).
- **F7 (bundle-anyway, partially fixed)**: SKILL.md step 7 sub-bullet이 load-
  bearing anchor가 아니어서 anchor reader가 놓칠 가능성. → SKILL.md 본문은
  200줄 cap에 묶여 있어 anchor 추가가 어려움. 대안으로 propose probe routing
  을 `references/proposal-flow.md`에 "Adapter-Driven Probes" 단락으로 추가
  (proposal-flow은 step 7의 표준 reference). 향후 anchor 섹션 재정리 슬라이스
  에서 한 줄 anchor로 승격.
- **F3, F4, F5 (over-worry / valid-but-defer)**: validator의 비-dict commands
  값 merge 동작, 추가 negative fixture, --execute idempotence test. 마지막
  하나(idempotence)는 same-slice에 추가 (`test_a3_execute_idempotent`); 나머지
  둘은 follow-up.

## Canonical Artifact

본 spec 파일이 implementation contract의 canonical 본문이다.
`impl`은 본 파일을 cite하며 진행하고, 작업 중 발견된 사실 변화는 본 파일에
바로 반영한다 (chat-only drift 금지).

## First Implementation Slice

순서는 sync-before-verify를 따른다.

1. `scripts/quality_policy_defaults.py`에 `DEFAULT_MUTATION_TESTING` 추가
   (craken 출처 주석 포함).
2. `scripts/quality_adapter_lib.py`에 `_apply_mutation_testing` 검증 +
   `infer_quality_defaults`에 기본값 wiring.
3. `skills/public/quality/scripts/init_adapter.py`의 `build_items`에 항목 추가.
4. `skills/public/quality/adapter.example.yaml`에 샘플 블록 추가.
5. `skills/public/quality/references/adapter-contract.md`의 fields 섹션에
   `mutation_testing` 추가 + 별도 단락에서 슬롯 의미 + craken defaults 인용.
6. `skills/public/quality/references/mutation-testing.md` 신설 — detect/propose
   프로토콜, 워크플로 템플릿 사용법, commands.summary 컨트랙트.
7. `skills/public/quality/scripts/templates/mutation-tests.yml` 신설.
8. `skills/public/quality/scripts/propose_mutation_testing.py` 신설.
9. `skills/public/quality/SKILL.md` 본문에 새 propose 단계 wiring + reference
   링크.
10. fixture-based 테스트 (`tests/control_plane/`) 추가 — Acceptance Checks
    a1-a3,a5 대응.
11. `python3 scripts/sync_root_plugin_manifests.py --repo-root .` 실행.
12. `python3 scripts/render_cli_reference.py --repo-root . --output
    docs/cli-reference.md` 실행 (CLI surface가 새 propose 스크립트 알아야 할
    경우만).
13. quality 본 실행으로 self-dogfood.

## Deferred Follow-ups

- craken-agents 어댑터 마이그레이션 (별도 PR). craken-agents의
  `.agents/quality-adapter.yaml`에 `mutation_testing` 블록 채우고
  `.github/workflows/mutation-tests.yml`를 새 charness 템플릿으로 교체.
- presets에 stack별 commands 권장값 (typescript-quality.md에 Stryker 라인
  — `commands.{dry_run,full,sample,summary}` craken 기본값 + Stryker 도구
  의존성, python-quality.md에 mutmut/cosmic-ray 라인). 첫 non-TS dogfood 후.
- standing gate 통합 (quality 본 실행이 summary.md의 score를 읽어 critical
  gate로 fail) — 첫 dogfood 결과 후.
- workflow 어댑터 파싱 fallback 결정 (`yq` 부재 host에서 `python -c`로 fallback).
- 어댑터 write-back 안전성 강화 (ruamel.yaml round-trip). 첫 슬라이스의
  fenced-marker append 방식이 사용자 편집과 충돌하거나 두 번째 writer가 등장
  하면 도입.
- 전체 charness adapter validator의 unknown-key strict 정책 일관화 — 현재는
  모든 mapping validator가 silent ignore이며 `mutation_testing`은 warning까지
  올린 첫 사례다. 후속 슬라이스에서 일관화 여부 결정.
