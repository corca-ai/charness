# Achieve Goal: 현재 열린 17개 이슈를 다음 작업을 가능하게 만드는 순서로 닫기

Status: active
Created: 2026-08-05
Activation: `/goal @charness-artifacts/goals/2026-08-05-close-all-open-issues-generative-sequence.md`
Activation time: 2026-08-05T04:54:43Z

이 파일은 activation record가 작성된 뒤 active goal scratchpad로 실행 내역과 증거를 보존한다.

## Active Operating Frame

- Current disposition: active; activation preflight matched the live open-issue inventory and recorded the activation boundary below.
- Current slice: #468 local carrier complete at d2ec4f58, but its conditional pre-push boundary refused on the measured pytest runtime budget; #468 remains OPEN.
- Current slice intent: use the recorded #468 external-boundary non-claim to re-rank into #503's measured recurring-cost owner/decision slice without weakening the refusing gate.
- Next action: read and resolve #503 against the current runtime cohort, then choose the smallest measured owner/budget contract that lets the unchanged proof surface make an honest decision.
- Verification cadence: 이슈를 닫을 때마다 targeted deterministic proof → 필요한 경우 bounded fresh-eye/critique → 별도 behavioral verdict → GitHub adapter readback 순서를 지킨다. broad proof는 bundle/final 또는 risk-triggered 경계에서만 추가한다.
- Gate cadence: source와 `plugins/` export를 먼저 동기화하고, pre-lock bundle/risk 경계에서 `run_slice_closeout.py --skip-broad-pytest`, 묶음/최종 경계에서 verification lock과 broad proof를 사용한다.
- Sequence rule: 아래 순서는 기본 순서다. 앞 이슈가 막히면 조용히 건너뛰지 않고 이유와 재정렬을 기록한다. 재정렬해도 닫히지 않은 이슈를 닫힌 것으로 세지 않는다.
- History boundary: 이 frame은 현재 제어판으로만 유지하고 실행 내역은 `## Slice Log`, 결정은 `## Operator Decision Queue`, 최종 증거는 `## Final Verification`에 남긴다.

## Goal

현재 GitHub에서 열린 17개 이슈를 실시간 상태를 기준으로 다시 읽고, 앞선 해결이 뒤의 해결을 더 싸고 정확하게 만드는 Christopher Alexander식 generative sequence로 하나씩 reshape·구현·검증·closeout한다. 같은 구현을 공유하는 이슈는 구현 단위로 묶을 수 있지만, 각 이슈의 JTBD·carrier·resolution critique·distinct behavioral verdict·GitHub readback은 독립적으로 남긴다. 성공은 “전체 green”이라는 한 문장이 아니라, 17개 각각에 대해 정직한 closeout을 남기거나 외부 경계가 실제로 막힌 경우 그 non-claim과 잔여 이슈를 명시하는 것이다.

## Non-Goals

- 지금 이 shaping 단계에서 코드를 구현하거나 GitHub 이슈를 닫지 않는다.
- 17개 이슈를 새 umbrella issue 하나로 대체하거나, 원래 문제가 사라지는 식으로 이슈 본문을 다시 쓰지 않는다. reshape는 문제·JTBD·증거를 보존한 채 범위, carrier, 순서만 명확히 한다.
- 로컬 테스트의 green을 GitHub CLOSED, remote CI, 설치된 plugin, provider roundtrip의 증거로 간주하지 않는다.
- closeout floor, distinct observer/channel, fresh-eye review, source/plugin parity를 런타임 단축을 위해 약화하지 않는다.
- 새 PR, release publish, tag, version bump, `cautilus evaluate`는 이 goal의 기본 범위가 아니다. 필요한 경우 별도 승인과 해당 skill의 gate를 다시 요구한다.
- #491을 의미론적 문서-행동 일치를 판정하는 보편적 정적 gate로 자동 승격하지 않는다. 먼저 reviewer-owned question과 gate 후보를 비교한다.
- #503과 #505를 하나의 “느리다” 이슈로 합치지 않는다. 전자는 recurring-cost의 owner/decision이고 후자는 proof floor을 보존하는 실험이다.

## Boundaries

- Source of truth는 `corca-ai/charness`의 GitHub issue 상태·본문·댓글이다. activation 직전에 open issue set을 다시 read하고 각 read가 `comments_read: true`인지 확인한다. 이때의 live activation snapshot이 실행 범위의 기준이다. 2026-08-05의 17건은 shaping 당시 후보이며, 추가·삭제는 명시적 re-scope 후에만 반영한다.
- Shaping snapshot은 #468, #480, #482, #483, #484, #491, #496, #502, #503, #504, #505, #506, #507, #508, #509, #510, #511이다. 이 목록 밖의 이슈를 activation 후 조용히 성공 조건에 끼워 넣지 않는다.
- GitHub issue close는 user의 standing approval을 사용하되, `validate-closeout-draft`, delegated resolution critique, classification별 carrier ledger, `Behavior #N:` 또는 typed non-verified disposition, distinct evidence channel, `verify-closeout --expect-state CLOSED`를 모두 통과할 때만 수행한다. 한 이슈의 closeout이 끝나기 전 다음 이슈를 닫지 않는다.
- `git push`는 pre-push gate가 통과할 때만 standing approval을 사용한다. gate를 약화하거나 `--no-verify`를 쓰면 승인은 철회된 것으로 간주한다. PR/release 경계는 별도 승인 없이는 실행하지 않는다.
- bug 이슈는 debug causal review를 설계 전에 수행하고, verdict logic을 바꾸는 proof surface는 bounded fresh-eye 1차 리뷰가 수리를 만들면 수리된 surface를 읽는 2차 리뷰까지 수행한다. 리뷰 전후 worktree/index fingerprint를 확인한다.
- issue closeout의 carrier와 behavior verdict는 issue별로 분리한다. 동일한 summary, 동일한 `CLOSED` readback, 동일한 테스트 결과를 17건에 복사해 독립 증거처럼 세지 않는다.
- source/`plugins/` export 동기화는 validator보다 먼저 한다. `<authoring-repo>/`, `<plugin-dir>/`, consumer-relative `<repo-root>/`의 해석을 서로 혼동하지 않는다.
- 각 slice는 다음 이슈로 넘어가기 전에 짧은 `Slice Log` disposition을 남긴다. 최소 필드는 issue/live-read identity, selected·blocked·closed 상태, frozen SHA, reshape decision, carrier path+SHA, critique path, behavior channel/verdict, GitHub readback, non-claim, next unblock action이다. 원인 분석이 다음 순서를 바꾸면 그 이유와 re-rank authorization을 함께 남긴다.
- “reshape”는 기본적으로 goal-local plan 변경이다. live GitHub issue body·label·state를 바꾸는 tracker edit는 별도의 외부 write로 취급하고, issue identity/read timestamp, 보존한 JTBD/evidence, 변경 delta, authorization을 carrier에 남긴 뒤에만 수행한다.

## User Acceptance

- 사용자는 이 파일의 Slice Plan에서 17개 이슈가 빠짐없이 번호와 순서를 갖는지 확인할 수 있다.
- activation 후에는 각 issue closeout이 개별 carrier와 개별 `Behavior #N:` verdict 또는 typed non-verified disposition을 가진다. 최종 보고서는 issue 번호별로 `CLOSED` readback과 behavioral verdict를 따로 보여준다.
- 모든 이슈가 실제로 닫히지 못하면 “전부 닫혔다”고 보고하지 않고, 어느 이슈에서 어떤 외부 경계가 남았는지와 다음 unblock action을 보여준다.
- sequence의 품질은 issue 번호나 최신순이 아니라, 각 단계가 다음 단계의 계약·검증·판단 비용을 낮추는지로 평가한다. 완료된 각 단계의 `Slice Log`는 어떤 후속 이슈의 설계·증거·결정 비용이 어떻게 바뀌었는지 한 가지 이상 기록하고, 후속 slice는 그 generative 가설을 확인하거나 반증한다. 반증되면 다음 closeout 전에 re-rank한다.
- 사용자는 먼저 이 draft를 검토하고, activation 뒤에는 `/goal`이 자동으로 shape나 close를 하지 않는다는 점을 전제로 실행 여부를 결정한다.

## Agent Verification Plan

### Low-Cost Checks

- activation 직전 `issue_tool.py plan --intent resolve`와 17개 `issue_tool.py read`를 다시 실행해 번호, state, comments, selected backend를 새로 확인한다.
- 매 slice 시작 시 live issue body의 JTBD와 현재 source/`plugins/` seam을 읽고, remedy가 이미 named decision에 있다면 그 premise를 먼저 재검증한다. #468의 핵심 규칙을 모든 slice에 적용한다.
- `git status`, 고정 commit SHA, generated/export surface를 기록하고 sync-before-verify 순서를 지킨다.
- bug slice는 재현 fixture와 causal hypothesis를 먼저 세운다. 기존 local carrier/test는 재사용하되 현재 HEAD에서 동작하는지 재검증한다.
- 각 issue 전에 live issue/comment read와 current counterfactual probe를 기록한다. 원래 관찰이 재현되지 않으면 regression·partial repair·duplicate·stale evidence 중 하나로 분류하고 source에 코드가 있다는 이유만으로 close하지 않는다. 적용 가능한 경우 source·`plugins/` export·affected reader/consumer를 함께 비교한다.
- 각 slice의 targeted tests와 `check_goal_artifact.py`를 cheap boundary로 실행한다. gate 출력은 `head`/`tail`로 자르지 않고 실패 로그를 보존한다. broad gate는 bundle/final/risk-triggered일 때만 실행한다.

### High-Confidence Checks

- `#506`을 먼저 닫기 전 stale default-window refusal을 현재 HEAD에서 읽는다. 그 뒤 `#502 → #507 → #511`은 quality/proof 결과의 첫 reader와 error/inapplicable semantics를 확인하는 별도 proof packet을 갖고, bounded reviewer들은 snapshot/verify fingerprint rail을 사용한다.
- 각 이슈는 이미 존재하는 remediation와 closed sibling을 먼저 대조한다. 특히 #507은 #481과의 관계를 regression·partial repair·duplicate 중 하나로 분류하고, #506은 #461이 닫은 broader axis와 default-path 잔여를 구분한다.
- `#504` closeout은 goal identity가 맞는 retro인지 확인하고, session-level retro mode를 깨지 않는다.
- `#508 → #509 → #510`은 preferred path다. hard dependency는 #508의 classifier 판정과 #510의 route join, #509의 persistence branch가 end-to-end에서 합쳐지는 것으로 기록하고, 각 branch의 독립 fixture도 허용한다. legitimate `design intent`, real login wall, uppercase/encoded URL, Markdown negotiation, dated-record persistence를 각각 fixture로 갖는다.
- `#491`은 정적 gate green이 아니라 현재 reference와 behavior를 다른 reader가 읽는 reviewer verdict로 확인한다.
- `#480 → #484 → #482 → #483`은 source-to-plugin mirror matrix를 고정하고, markdown link, command carrier, JSON/YAML/template carrier를 분리한다. 각 verdict logic 변경은 필요한 2차 fresh-eye round까지 포함한다.
- `#503`은 현재 telemetry cohort와 owner/예산 결정을 새로 측정하고, `#505`는 그 뒤 최종 runner에서 matched full-command timing을 측정한다. proof floor을 낮추는 “개선”은 성공으로 세지 않는다.

### External Or Live Proof

- issue close는 carrier publish 후 GitHub adapter로 `verify-closeout --expect-state CLOSED`를 읽는다. 이 결과는 tracker state만 증명하며, 별도 channel의 per-issue behavior verdict가 반드시 함께 있어야 한다.
- push/remote CI가 필요한 경우 push exit code와 다른 observer·channel에서 CI/check-runs를 읽는다. 확인하지 못한 remote/provider/installed behavior는 명시적 non-claim으로 남긴다.
- public-source URL을 새로 의사결정에 사용하지 않는다. 그런 source가 생기면 `gather`로 durable asset을 만든 뒤 그 asset을 context source로 고정한다. GitHub issue 내용은 issue adapter가 source of truth로 읽은 운영 상태다.

## Slice Plan

| Seq | Issue | Reshaped closeout unit | Why now / generative contribution | Expected evidence | Status |
| ---: | --- | --- | --- | --- | --- |
| 1 | #468 | deferred remedy를 premise-reverification contract로 reshape | 오래된 “named remedy”를 그대로 구현하지 않게 모든 뒤 slice의 설계 경계를 만든다. | premise read/run record, durable contract, decision/closeout critique, distinct readback | blocked at remote publish/readback; local carrier complete |
| 2 | #506 | reviewer boundary의 stale default-window refusal | 모든 후속 proof-surface review가 오래된 window를 읽고도 통과하는 일을 먼저 막는다. 임시로는 explicit `--before`와 matching `--window-id`를 강제한다. | current-HEAD stale-window refusal, 24-test revalidation, snapshot/verify fingerprint, closeout carrier | re-ranked after #503 |
| 3 | #502 | `run-quality.sh` summary의 structured owner/consumer contract | quality/proof reader가 format drift를 test sanding으로 오해하지 않게 하는 공통 receipt spine이다. 현재 issue의 17 consumer 주장과 local matrix 차이를 먼저 재검증한다. | producer-reader inventory, focused proof, bundle/final broad proof, carrier, distinct behavior verdict | planned |
| 4 | #507 | quality adapter bootstrap의 no-op/preserve/explicit migration 경계 | 기존 consumer 설정과 comment를 덮는 destructive seam을 안정화해 이후 quality 검증의 입력을 믿을 수 있게 한다. #481과의 regression/partial-repair/duplicate 분류를 먼저 한다. | disposable consumer readback, no-op byte/comment preservation, conflict/migration cases, export parity | planned |
| 5 | #511 | nose inventory의 scanned/missing/error/inapplicable contract | adapter/root 설정이 안정된 뒤 false clean zero를 없애고 quality advisory를 실제로 읽을 수 있게 한다. | `src`/`scripts`/`worker` fixture, absent-root payload, consumer interpretation, advisory non-blocking proof | planned |
| 6 | #504 | retro persistence의 owning goal binding | 이 긴 goal의 closeout memory가 다른 goal에 붙는 churn을 막고, 뒤 slice의 evidence ownership을 고정한다. | goal-aware write/readback, session-mode preservation, distinct critique, GitHub close proof | planned |
| 7 | #496 | hollow refill report의 inert-default policy/semantics | 독립적인 mutation report 판단을 공통 schema나 runtime 정책으로 오염시키지 않고, 기존 local evidence를 현재 HEAD에서 정리한다. | positive/negative/axis-control matrix, plugin parity, issue-specific disposition | planned |
| 8 | #491 | semantic reference drift를 reviewer-owned decision으로 reshape | portability sweep 전에 “gate인가 reviewer question인가”를 결정해 의미론을 noisy static gate로 만들지 않는다. | three claim-family reads, copy-paste behavior check, bounded reviewer verdict | planned |
| 9 | #508 | gather classifier의 token-aware login-wall 판정 | gather route의 첫 판정을 바로잡아 정상 Markdown이 blocked로 분류되지 않게 한다. | `design intent` controls, real login fixture, classifier/route trace, fresh-eye review | planned |
| 10 | #509 | auto-derived URL slug의 normalization/persistence | 정상적으로 얻은 representation이 dated-record writer에서 다시 실패하지 않게 persistence branch를 안정화한다. | uppercase/percent-encoded URL fixtures, digest retention, disposable execute/readback | planned |
| 11 | #510 | content-negotiated Markdown acquisition route | classifier와 persistence branch가 안전해진 뒤 public URL에 Markdown representation을 먼저 요청한다. | Accept negotiation, route/representation trace, joined end-to-end record readback, fresh-eye review | planned |
| 12 | #480 | `<authoring-repo>/` resolver를 docs/artifacts까지 확장 | portability reader가 실제 authoring tree를 읽게 해 다음 shared/package sweep의 ruler를 만든다. | authoring docs/artifacts positive/negative cases, source/plugin matrix | planned |
| 13 | #484 | `skills/shared/**` portable package boundary | #480의 reader position을 shared shipped tree에도 적용해 unmarked-tree 판정의 구조적 빈틈을 닫는다. | shared package root cases, source/export parity, verdict-surface fresh-eye round | planned |
| 14 | #482 | COMMAND carrier의 consumer-layout resolution | reader/tree 모델이 고정된 뒤 command text만의 path predicate를 별도로 고쳐 false unreachable을 줄인다. | consumer-layout positive/negative command cases, distinct command-carrier proof | planned |
| 15 | #483 | non-Markdown asset carrier corpus | markdown-only ruler가 고정된 뒤 JSON/YAML/template를 typed carrier로 확장한다. 다른 portability issue와 proof를 섞지 않는다. | Markdown/JSON/YAML/executable-template fixtures, bounded corpus claim, second review if repaired | planned |
| 16 | #503 | recurring slow gate/over-slice telemetry의 owner/decision | 구조적 proof surface가 안정된 뒤 비용을 재측정해 “느리다”를 owner 없는 반복 보고로 남기지 않는다. | current cohort/percentiles, owner/budget or intentional-retention decision, distinct readback | next; explicitly re-ranked after #468 gate refusal |
| 17 | #505 | final mutation/quality runtime experiment | #502 이후 최종 runner를 기준으로 측정해야 하므로 마지막에 proof floor을 보존하는 실험을 한다. | matched full-command timing, phase/node map, unchanged failure visibility, final gate proof | planned |

Implementation grouping is allowed for #480/#484 and for #508–#510, but closure order is still one issue at a time: the shared implementation is not a shared closeout, and a later issue does not inherit an earlier issue's behavioral verdict.

## Operator Decision Queue

- Decision: CONFIRMED — #468은 모든 후속 slice에 적용되는 premise-reverification contract로 reshape한다.
  Owner: operator confirmed in this session
  Why deferred: 없음 — 원래 issue history/JTBD는 보존하고 contract가 실제 후속 remedy decision을 바꿨거나 premise를 반증하는 observable을 요구한다.
  Unblock action: activation 직전 #468 live read와 첫 causal review로 보존 범위와 observable을 고정한다.
  Revisit trigger: activation 직전 #468 live read와 첫 causal review. #468의 closeout은 단순한 새 문장 추가가 아니라, 그 contract가 적어도 한 후속 remedy decision을 바꿨거나 기존 제안의 premise를 반증했다는 observable을 요구한다.
- Decision: CONFIRMED — external route는 activation blocker가 아니다. 기본 route는 `direct-commit`/auto-close이며, PR/release/tag/version bump는 이 goal에 포함하지 않는다.
  Owner: operator confirmed in this session
  Why deferred: 없음 — 커밋에 close keyword와 closeout ledger를 싣고 push 후 adapter로 CLOSED를 다시 읽는다. auto-close가 지원되지 않거나 실패할 때만 adapter가 허용하는 manual fallback을 사용한다.
  Unblock action: first carrier 전에 selected backend, carrier route, and `validate-closeout-draft` shape를 re-read하고 그 결과를 Slice Log에 기록한다.
  Revisit trigger: first issue carrier를 만들기 전.
- Decision: CONFIRMED — activation 시점의 live open issue set을 실제 범위로 삼는다.
  Owner: operator confirmed in this session
  Why deferred: 없음 — shaping 당시 17건은 후보 snapshot이고, activation에서 추가·삭제가 생기면 re-scope를 기록한다.
  Unblock action: activation preflight의 issue list/read와 re-scope record를 남긴다.
  Revisit trigger: activation preflight의 issue list/read.
- Decision: CONFIRMED — blocked issue가 있어도 기록된 re-rank로 독립 후속 slice를 진행할 수 있다.
  Owner: operator confirmed in this session
  Why deferred: 없음 — blocked issue는 여전히 OPEN으로 남기고, missing proof·non-claim·unblock owner/action·re-rank authorization을 기록해야 한다.
  Unblock action: blocked row를 먼저 작성한 뒤에만 다음 slice를 시작한다.
  Revisit trigger: 첫 blocked external/live boundary.

## Coordination Cues

- Routing: `achieve` — 17개 live issue를 하나의 inert, reviewable goal artifact와 slice memory로 shaped한다.
- Routing: `issue` — 각 issue의 adapter read, classification, causal/resolution review, carrier, closeout readback을 소유한다.
- Routing: `quality` — quality/proof gate의 validation posture와 local-vs-live proof cost를 판단한다.
- Routing: `debug` — bug-class issue의 falsifiable root cause와 recurrence boundary를 먼저 세운다.
- Routing: `critique` — goal sequence와 각 meaningful proof-surface slice의 before-the-fact fresh-eye review를 수행한다.
- Routing: `retro` — goal closeout의 waste, decision, transferable improvement를 owning goal에 binding한다.
- Gather: n/a — shaping에는 새 public source URL을 사용하지 않았고, GitHub issue source of truth는 `issue` adapter가 읽었다.
- Release: n/a — 이 draft는 version/install-manifest/release publish를 하지 않는다.
- Issue closeout: planned for #468, #480, #482, #483, #484, #491, #496, #502, #503, #504, #505, #506, #507, #508, #509, #510, #511; each issue requires its own carrier, `validate-closeout-draft`, delegated critique, distinct `Behavior #N:` verdict or typed disposition, and `verify-closeout --expect-state CLOSED`.

## Discuss Before Activation

- Discuss before activation: CONFIRMED — #468 reshape, activation-time live snapshot as scope, re-rank allowed after a blocked-row record, and `direct-commit`/auto-close as the default carrier route are confirmed. PR/release/cautilus remain out of scope; manual fallback is allowed only when the adapter says auto-close is unavailable or failed. Activation still requires a fresh live issue read and a written Activation Record.

## Slice Log

Execution has started after activation. #468 has a local carrier but remains OPEN because its standing conditional push approval was withdrawn by the runtime-budget gate; see Slice 1 below. The 17 rows above are plan state, not substitutes for per-issue closeout.

Execution row schema: `issue` · live-read identity/time · selected/blocked/closed disposition · frozen SHA · reshape decision (`local-plan only` or authorized tracker edit) · carrier path+SHA · critique path · distinct behavior channel/verdict or typed disposition · GitHub adapter readback · non-claim · next unblock action. A blocked row must also name the open state, missing proof, owner/action, and explicit re-rank authorization before any later issue is started.

Per-issue irreversible sequence: freeze the exact carrier draft → run `validate-closeout-draft` → run delegated resolution critique → render the distinct behavior verdict/disposition → publish through the selected route → run adapter `verify-closeout --expect-state CLOSED` → append the complete row. If the published carrier, reviewed carrier, behavior channel, or readback identity differs, stop and rebind before proceeding.

Generative benefit field: each closed row names one later issue whose design, evidence, or decision cost was expected to change. The later row records `confirmed` or `falsified`; a falsified ordering hypothesis triggers re-rank before the next closeout.

### Slice 1: #468 carrier complete; pre-push boundary blocked

- Objective: Publish the validated direct-commit carrier for #468 and verify the issue CLOSED through GitHub.
- Why this approach: #468 was the planned first slice and its local contract/closeout evidence was complete; the pre-push gate is the next external boundary.
- Commits: d2ec4f58 — docs: record named remedy premise contract; commit hook and local slice closeout passed.
- What changed: Added the Named Remedy Premise Contract and structured D45/D47/D48 premise records; added the bound delegated critique and activated this goal.
- Alternatives rejected: Did not use --no-verify, weaken the runtime bar, manually close #468, or treat the local carrier as remote CLOSED.
- Targeted verification: validate-closeout-draft passed for deferred-work #468; docs/link/markdown/critique gates passed; pre-push reported 84 passes and refused on check-runtime-budget because pytest median was 61816ms over the 58500ms bar.
- Test duplication pressure: No tests were added or expanded in this documentation slice; no duplicate-pressure sample was applicable.
- Critique: charness-artifacts/critique/2026-08-05-issue-468-resolution.md; parent-delegated fresh-eye review returned clean boundary fingerprint and one D47 unit correction, which was applied before commit.
- Off-goal findings: None. The runtime-budget refusal is the in-goal unblock signal for #503, not a silently added issue.
- Lessons carried forward: A valid carrier and local green proof do not establish GitHub CLOSED. Re-rank authorization is exercised explicitly: #468 remains OPEN with remote publish/readback missing, and #503 is next because it owns the measured runtime decision.
- Metrics: Pre-push full quality elapsed 135.0s; pytest latest 60356ms, recent median 61816ms, recent max 69353ms; no remote CI or issue CLOSED readback was obtained.

## Activation Record

Activation record status: recorded — 2026-08-05T04:54:43Z.

- Live scope evidence: `gh issue list --repo corca-ai/charness --state open --limit 100 --json number,title,state,url` returned exactly #468, #480, #482, #483, #484, #491, #496, #502, #503, #504, #505, #506, #507, #508, #509, #510, and #511. No shaping-snapshot issue was removed and no additional open issue appeared; no re-scope was required.
- Fresh issue reads: `python3 skills/public/issue/scripts/issue_tool.py read --repo corca-ai/charness --number <n>` was run for all 17 numbers. Every result was `state: OPEN`, `comments_read: true`, and selected backend `gh`; no issue was designed from a missing or partial read.
- Queue decisions confirmed: #468 uses premise-reverification; activation-time live scope is authoritative; a blocked issue may be followed by an explicitly recorded re-rank row while the blocked issue remains OPEN; direct-commit/auto-close is the default carrier route. PR, release, tag, version bump, and Cautilus remain out of scope.
- Carrier route: selected backend `gh`; default route is a direct-to-default commit carrying explicit close keywords and the classification ledger, followed by `verify-closeout --expect-state CLOSED`; manual fallback is allowed only if the adapter reports auto-close unavailable or failed after remote verification.
- Ordering decision: start with #468 and stop or re-rank only through the blocked-row schema in `## Slice Log`; strict sequence remains the default. The four activation discussions are resolved as `CONFIRMED` in `## Discuss Before Activation` and `## Operator Decision Queue`.

## Context Sources

1. [North Star](docs/design-north-star.md) — governing standard: brief a capable judge; keep teeth where a wrong answer escapes; use a different observer and evidence channel at irreversible boundaries.
2. [Current handoff](docs/handoff.md) — previous session's warning not to reactivate the stale five-issue umbrella or #502 draft unchanged; this goal supersedes the narrow scope by explicitly adding all current open issues and reshaping them.
3. [Recent retro](charness-artifacts/retro/2026-08-05-session-retro.md) and [recent lessons](charness-artifacts/retro/recent-lessons.md) — repeated traps around proof boundaries, local-vs-remote claims, generated surfaces, and goal persistence.
4. [Quality record](charness-artifacts/quality/latest.md) — current local proof confidence, runtime/telemetry context, and non-claims.
5. [Implementation discipline](docs/conventions/implementation-discipline.md) and [operating contract](docs/conventions/operating-contract.md) — sync-before-verify, commit, critique, durable-artifact, and closeout rules.
6. [Issue skill](skills/public/issue/SKILL.md), [resolve flow](skills/public/issue/references/resolve-flow.md), and [closeout discipline](skills/public/issue/references/closeout-discipline.md) — GitHub source of truth, generative sequence, issue classification, and irreversible close floors.
7. Live adapter reads on 2026-08-05: #468, #480, #482, #483, #484, #491, #496, #502, #503, #504, #505, #506, #507, #508, #509, #510, #511; all were OPEN and all returned `comments_read: true`.
8. Three bounded ranking reviews for quality/gather (#507–#511), proof/runtime (#491/#496/#502–#506), and portability/deferred (#468/#480/#482/#483/#484/#491). Their findings are planning evidence, not issue closeout or remote proof.

## Interview Decisions

- Mode: artifact-only shaping. The user asked to create a goal, not to start executing it; implementation and GitHub closeout begin only after `/goal` activation. Rejected alternative: starting #511 or #502 immediately would consume an external workflow before the user reviewed the broad scope.
- Session confirmation (2026-08-05): the operator agreed to reshape #468 into the premise-reverification contract, use the activation-time live issue set as scope, permit recorded re-rank after a blocked issue, and use direct-commit/auto-close as the default carrier route; PR is excluded and manual fallback is conditional.
- Scope: 17-issue snapshot at shaping time, with an activation-time live refresh. Axis: issue-state/time. Rejected alternative: silently including future issues would make the goal's semantic input drift without a re-shape record.
- Ordering: quality/proof spine first, then independent judgment, gather, portability, and final cost measurement. Axis: subsystem/verification dependency. Rejected alternative: issue number order, newest-first order, or “quickest close first,” because those do not create conditions for later correctness.
- Reshape: preserve observed problem, JTBD, and evidence; reshape only the fix-unit, boundary, carrier, or sequence. Axis: issue classification (bug, deferred-work, decision-needed); the classification may change only after live read and causal/brief review.
- External effects: GitHub close and conditional push are in scope only behind their standing floors; PR, release, tag, version bump, and `cautilus evaluate` are not implicitly authorized. Axis: backend/host capability and irreversible boundary. Rejected alternative: treating a local goal artifact or terminal green as permission/proof of remote completion.
- Fresh-eye controls: use host-exposed bounded reviewer capabilities and adapter-defined model/role defaults rather than hard-coding one model globally. Axis: host/subagent capability. Rejected alternative: same-agent self-approval or a global model assumption.

## Plan Critique Findings

- Act Before Ship — `#468` must be a planning guardrail before remedy design; `#502` must settle the current producer/reader contract before broad proof; `#506` must refuse stale review windows before later fresh-eye claims; `#505` must be last because earlier runner changes invalidate timing.
- Act Before Ship — `#506` was moved ahead of every later proof-surface slice. Until it is closed, later reviews must use explicit `--before` plus matching `--window-id` and record that temporary boundary.
- Act Before Ship — “generative” is now an observable acceptance property: each step names a later cost/decision benefit and the later slice confirms or falsifies it. #468 also needs a downstream premise-decision observable, not process prose alone.
- Act Before Ship — every issue gets a current differential before implementation/reshape/closeout: live issue read, counterfactual reproduction where applicable, source/export/reader comparison, and a classification of regression, partial repair, duplicate, or stale evidence when the report no longer reproduces.
- Act Before Ship — #507 must be classified against closed #481 and #506 against #461 before independent closeout claims are made.
- Act Before Ship — the activation record, blocked-row schema, and exact carrier→critique→behavior→publish→CLOSED-readback sequence are required to make resumption safe.
- Act Before Ship — #508/#510/#511 and #480/#484/#482/#483 change verdict logic or proof scope. Their fresh-eye contract includes source/export parity, bounded review fingerprinting, and a second round when round one repairs the measured surface.
- Bundle Anyway — #507's no-op/preserve/conflict fixtures with #511's path/error consumer fixtures in the quality spine, while keeping their issue carriers and behavior verdicts separate. #508–#510 can share gather fixtures and route traces, but not issue closeout.
- Over-Worry — a universal 17-issue receipt schema, a single aggregate “all closed” gate, or exhaustive claims over every non-Markdown asset would add more judgment debt than confidence. Explicitly not folded into the goal.
- Over-Worry — broad gate, verification lock, and full critique machinery are not required mechanically for every issue; use targeted proof per issue and broad/lock proof at bundle/final/risk-triggered boundaries.
- Valid but Defer — #491's universal static reference gate, a broad consumer-repo audit beyond named evidence, PR/release publication, and runtime optimization before the final runner shape are deferred or out of scope.
- Bundle Anyway — keep quality (#502/#507/#511), gather (#508/#509/#510), and portability (#480/#484/#482/#483) shared at implementation/proof-packet level where cheap, but keep carriers, behavior verdicts, and GitHub readbacks issue-specific.
- Valid but Defer — a universal static semantic-reference gate for #491, full consumer-repo audit, and runtime optimization before final runner shape remain deferred; dependency claims are hypotheses to validate at live-read time, not permanent DAG edges.
- Reviewer provenance — three unnamed bounded ranking agents independently converged on the main family ordering; four additional named-lens/counterweight fresh-eye reviewers inspected this saved artifact. All four boundary fingerprints were `clean`. Their strongest changes were folded above; no reviewer claimed any issue fixed or closed.

## Closeout Binding Plan

- Reviewed inputs: the 17 live issue payloads with comments, the governing North Star, handoff, recent lessons, quality record, implementation/operating contracts, issue/achieve/quality/critique/retro skill contracts, current source and export trees, and each slice's fixed proof packet.
- Frozen target: before each meaningful slice, record the exact commit SHA and source/export inventory; a later semantic-input edit invalidates the verification lock and requires rebinding.
- Fresh-eye: a distinct bounded reviewer context, wrapped by reviewer-boundary snapshot/verify, reads the slice packet and repaired verdict surface when required. Issue resolution critique is delegated and separate from the implementer.
- Distinct evidence channel: issue state comes from GitHub adapter readback; behavior comes from a targeted behavior test, disposable consumer/provider readback, or direct artifact observation that did not produce the carrier/CLOSED state.
- Verification lock: record `run_slice_closeout.py`/quality lock evidence, focused and broad gate outputs, changed-line scope, and any remote check-runs read through a different observer. No terminal green substitutes for this lock.
- Complete flip: only after every issue is independently dispositioned, all permitted live boundaries are verified or explicit non-claims are recorded, retro/disposition evidence is bound to this goal, and the artifact itself passes its final validator may `Status: complete` be written.

## Off-Goal Findings

No new off-goal finding during shaping. If a new issue is discovered while executing a slice, file or reshape it through `issue`, record only its reference and reason here, and do not silently enlarge this 17-issue goal.

## Final Verification

Draft verification: all 17 current issue reads returned OPEN with `comments_read: true`; no implementation, issue close, push, remote CI, release, or live provider proof was performed during shaping. Final closeout fields remain intentionally unclaimed until activation and execution.

Retro: not run — this is artifact shaping only; no execution work unit exists to retrospect.
Host log probe: n/a — no active goal run or host-level live proof was requested during shaping.
Disposition review: not run — no slice or issue carrier exists yet.

## User Verification Instructions

1. Review the 17 shaping-snapshot issue numbers, the preferred sequence, and the items in `## Operator Decision Queue`.
2. If the default reshape/side-effect boundaries are acceptable, write an `Activation Record` that resolves the queue, records the live activation snapshot, and marks the discussion summary `CONFIRMED`; only then run the exact `Activation:` command at the top of this file.
3. On activation, expect a fresh GitHub read; if the issue set changed, reshape this draft before executing a slice. Nothing in this shaping turn has closed an issue.
4. During execution, verify each issue from its own carrier, distinct behavioral evidence, and `verify-closeout --expect-state CLOSED`; do not infer the remaining issue states from this goal artifact.

## Auto-Retro

Retro dispositions: none — draft creation only; no execution waste or new improvement was surfaced beyond the sequence and proof-boundary decisions recorded above.
Structural follow-up: none — draft creation only; any recurring waste discovered during execution must become an applied guard or a tracked issue with its structural pattern and destination.
