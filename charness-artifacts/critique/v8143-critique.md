# Release Critique — charness v8.14.3 (patch)

Date: 2026-09-29

## Decision Under Review

Ship charness v8.14.3 as a patch release carrying the #877 (interrupted-lane
WIP checkpoint across merges and clean trees), #878 (reviewer `claude_p`
JSON-schema rejection plus backend stderr in the failure reason), and #879
(scope-evidence precision) fixes with their focused tests.

Kind: charness release critique
Prepared for: v8.14.3 patch release
Scope: 13 shipped files (8 task-run scripts, 1 shared reviewer script, 1 quality declaration, 3 test files); 11 were packet-reviewed and the checkpoint function moved verbatim to a 12th file after review to satisfy the file-length gate, plus its attention-state declaration
Reviewers: 7 file-backed worker runs (codex_exec, read-only envelope)

## Release Scope

v8.14.3 is a patch release: three bug fixes plus focused tests. It closes
#877, #878, and #879. Issue #825 (mutation-test-regression tracker) is not
closed by this release; it carries a bot-posted recovery candidate awaiting a
distinct observer, and its closeout is recorded separately as an observer
confirmation, not as release work.

## Surface-Lock Inventory

No operator-facing surface changes. No new CLI commands, flags, skills, or
doctor checks; no README or help-text changes; the release manifest version is
the only version-surface edit (8.14.2 → 8.14.3). Changed operator-visible
wording only: two new distinct merge blockers
(`unresolved merge in progress: …`,
`resolved merge changes paths outside the declared scope: …`) and one
enriched worker failure reason (backend exit code plus the backend's stderr
line). Payload shapes are unchanged. The canonical bounded-review schema file
is byte-identical; only the `claude_p` inline projection drops `$schema`.

## Operator Action Required

None. Patch upgrade with no migration, no config change, and no behavior an
operator must adopt. Installed copies refresh through the published update
instructions.

## Upgrade Path

Standard patch upgrade from any 8.x install. No rollback notes beyond the
normal "reinstall the previous release" path; no data or state migration.

## Verification Scope Decision

- Claim under test: v8.14.3 patch ships the 877/878/879 fixes with tests and breaks no pinned contract (#880 advisory recall, #816/#822 checkpoint discipline, reviewer worker backend contract).
- Changed surfaces: scripts/task_run/task_run.py, scripts/task_run/task_run_checkpoint.py, scripts/task_run/task_run_contract.py, scripts/task_run/task_run_git.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_plan.py, scripts/task_run/task_run_scope_evidence.py, scripts/task_run/task_run_support.py, skills/public/quality/references/attention-state-visibility.json, skills/shared/scripts/reviewer_worker_backend.py, tests/charness_cli/test_task_run_merge_checkpoint_877.py, tests/charness_cli/test_task_run_scope_evidence_879.py, tests/quality_gates/test_reviewer_worker_backend.py
- Minimum sufficient proof: eleven file-backed worker reviews with all findings triaged and four passes over final trees; focused suites green on the final tree (877: 12, 879: 6, reviewer backend: 10); harness_cli 1303 passed; reviewer neighbors 38 passed; ruff check clean; release changed-line coverage green on the staged tree; live Claude CLI schema-acceptance probe reproducing the #878 rejection and its removal.
- Deliberately omitted checks: a third fresh-eye round on the one-line F1-population repair (two-round cap; executed counterexample regression recorded instead); end-to-end claude_p review run (operator OAuth expired; schema acceptance proven live, full run non-claim); scheduled mutation sample over these files (owned by the scheduled mutation lane, not this release).
- Verifier contract: run_review file-backed workers on the adapter backend (codex_exec, unchanged harness verifiers, none suspect); standing pytest; run-quality full read-only lane; ruff check; direct CLI probes; this artifact validated by validate_critique_artifacts.py.
- Failure classification: subject-defect
- Negative control: command: focused pytest of test_resolved_merge_with_base_restoration_is_not_committed against the guard temporarily reverted to changed_paths; expected: the test fails because no MixedScopeMergeError is raised; observed: 1 failed; receipt: this-session run record (guard restored, 9 passed after).
- Subject identity: sha256:ccf25006854375e0854097d95faf5c02348667f1a56edc6f554751e8a5b7722c
- Verifier identity: sha256:261e3509044b81ab88061b65758b8604470ddaf12e9d9636ae25e726b4980b06
- Input identity: sha256:db9bfff5617e05342680c2939a265919cfb75e57136a71dfeaa07bb10526cd24
- Failure identity: stable:f1-population-hole
- Evidence identity: sha256:b212a0c5bae15951329380a2901b3dcaf6ddc7f91b7873f97d46dc993618eef8
- Retry disposition: first-attempt
- Retry key: sha256:2721f39d00af1c8335dcfd9bf251bf411e7e0d60a87feea64929bd2eb4c452e5

## Failure Angles

- Correctness and contract preservation (worker release-8-14-3-correctness): each fix satisfies its issue without breaking pinned contracts; boundary-ownership question for the skills/shared change included. Returned a block verdict with one high finding (F1), repaired same-session.
- Correctness recheck (worker release-8-14-3-correctness-followup): re-read the F1 repair; returned defer with an evidence gap (population owners unbound), no defect. Gap closed by the supplemental run.
- Release-operational readiness and record legibility (worker release-8-14-3-operational): bump honesty, surface lock, manifest sync, test proof, pre-tag must-dos; release-record legibility; operator-legibility of the changed error and blocker wording (the Raskin angle folded in because no dedicated operator-surface change exists). Returned defer with two evidence requests (R1, R2), no defect asserted.
- Guard-population coverage (worker release-8-14-3-carrier-supplement): compare the MixedScope guard population with everything the merge commit can include. Returned a block verdict with one high finding (F1-population) plus one evidence gap, repaired same-session with executed proof.
- Closing correctness re-review (worker release-8-14-3-closing): the A1 lens rerun over the final 13-file tree after all repairs. Returned pass with zero findings and an approval-eligible carrier.
- Issue resolution (worker release-8-14-3-issue-resolution): each issue body read against its fix on the final tree. Returned block with one medium finding (F1-markers), repaired same-session.
- Issue resolution re-review (worker release-8-14-3-issue-resolution-r2): the resolution lens rerun after the marker repair. Returned pass with zero findings and an approval-eligible carrier.
- Issue resolution rebind (worker release-8-14-3-issue-resolution-r3): the same lens rerun with the byte-identical issue bodies relocated to charness-artifacts/issues/, because top-level critique/ .md files must be full artifacts. Returned pass with zero findings and an approval-eligible carrier.
- Issue resolution on normalized bytes (worker release-8-14-3-issue-resolution-r4): the lens rerun after the whitespace normalization the pre-commit hook required. Returned block with two findings (F1-receipt, F2-recall), both rebutted on committed-code evidence; F1's valid kernel (resolved-merge to target_sha composition) closed with a new end-to-end test.
- Issue resolution directed re-read (worker release-8-14-3-issue-resolution-r5): the lens rerun with an evidence map pointing at the end-to-end receipt tests, the #880 docstring, and the recall/boundary tests. Returned defer with one evidence gap (R1-completion): F2 accepted as answered, F1 narrowed to binding the completion owner.
- Issue resolution completion-bound pass (worker release-8-14-3-issue-resolution-r6): the lens rerun with task_run_completion.py and task_run_evidence.py bound, establishing the target_head to target_sha chain. Returned pass with zero findings and an approval-eligible carrier.
- No dedicated Raskin reviewer: the release changes no CLI surface, README, or doctor output; the only operator-visible deltas are three error/blocker wordings, which the operational lens covered and did not flag.

## Counterweight Pass

- Round 1 (correctness block F1: resolved-merge path commits out-of-scope content): ACCEPTED. The guard as built committed the whole merge plus everything `git add --all` stages, against the pinned #816 discipline that only scoped changes become candidates. Repaired with the MixedScope admission check plus three regression tests; the F1 repair was re-read by round 2.
- Round 2a (recheck defer): the recheck found the guard correct, branches preserved, and scenarios covered, and asked for the population and staging owners to be bound. ACCEPTED as an evidence request; closed by the supplemental run rather than by assertion.
- Round 2b (operational defer R1: no version surfaces bound): ACCEPTED as structural. Critique runs before the version bump by design, so no packet can bind the bump; version-surface truth belongs to the designed claims-review round after the release record exists. Patch rationale is recorded in Bump Honesty below.
- Round 2b (operational defer R2: no execution receipts in packet): ACCEPTED; receipts are bound in Lane Evidence below, and the mocked-versus-live distinction for #878 is explicit: live CLI probes prove schema acceptance, while a full end-to-end claude_p run stays a non-claim (expired operator OAuth).
- Round 3 (supplement block F1-population: base-relative cancellation hides restored paths): ACCEPTED. The reviewer's static counterexample was converted into an executed regression that fails on the old guard and passes on the dirty-population guard.
- Closing round: the release closeout gate requires a fresh-eye approval state, which the round-cap non-approval cannot satisfy, so one closing worker round re-read the final tree. It passed with zero findings, giving the dirty_paths repair its independent re-read and the release its approval carrier. This supersedes the round-cap stopping point recorded in earlier drafts of this artifact.
- Resolution round (block F1-markers: staged conflict markers clear the unmerged listing): ACCEPTED. Staging marker content defeats the unmerged-entries check the issue's "no conflict markers remain" condition needs, so the merge-state check now unions unmerged paths with leftover-marker paths from git diff --check (staged and unstaged), with a regression that stages markers and still raises. The re-review passed with zero findings.
- Resolution round R4 (block F1-receipt: checkpoint-to-target_sha propagation not proven): REBUTTED with committed-code evidence. The failed-lane tests drive the real run_task pipeline end to end (real worktree, git, and completion) and assert target_sha/blocker on the final payload; the completion owner is unchanged pre-existing code. The valid kernel — resolved-merge composition lacked an end-to-end receipt — was closed with test_failed_lane_with_resolved_merge_names_the_merge_sha (12 passed).
- Resolution round R4 (block F2-recall: file-shaped foreign tokens kept): REBUTTED; the finding's own alternative was already satisfied. The #880 advisory-recall rationale is documented in _keep_candidate's docstring in the reviewed code, the false-positive boundary is pinned by test_dotted_identifiers_and_foreign_slash_tokens_suggest_no_scope, and recall is pinned by test_file_shaped_slash_token_counts_without_a_repo_foothold. The R5 re-read accepted F2 as answered.
- Resolution round R5 (defer R1-completion: completion owner not in the bounded input): ACCEPTED as an evidence request; closed by binding task_run_completion.py and task_run_evidence.py in the R6 packet rather than by assertion. R6 passed with zero findings.
- Round 3 (supplement evidence gap on parser internals): ANSWERED with execution, not assertion: staged-only-reverted, nested-untracked, staged-addition, and both rename-endpoint cases run through the real status capture in the residue test, and the populations dispatch was parent-read (ordinary records including staged-only land in tracked with both rename endpoints; untracked captured per-file).
- Residual risks carried into the verdict: (1) no end-to-end claude_p review exists anywhere (pre-existing; the backend was fully broken before #878); (2) sampled-mutant verdicts on these files belong to a future scheduled lane.
- Post-review mechanical split: the full lane refused task_run_lane_runner.py at 500 code lines (limit 480), so the reviewed checkpoint function moved verbatim into the new cohesive module scripts/task_run/task_run_checkpoint.py, with a compatibility alias at the old site. No logic changed; the 877 suite passes through the alias, and the length gate passes. The split forced one declaration move in attention-state-visibility.json (the skipped-checkpoint rationale follows the code; the lane-runner entry now describes its remaining persistence skip); the attention gate fails without it and passes with it.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_checkpoint.py | action: fix | note: MixedScope admission check added; rechecked clean by the follow-up run.
- F1-population | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_checkpoint.py | action: fix | note: guard moved to dirty_paths with an executed counterexample regression; no third fresh-eye round per cap.
- F1-collector-evidence | bin: over-worry | evidence: strong | ref: tests/charness_cli/test_task_run_merge_checkpoint_877.py | action: defer | note: parser branches pinned by executed residue cases plus parent-read dispatch; no action left.
- R1 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/critique/workers/release-8-14-3-operational/result.json | action: defer | note: version-surface truth belongs to the designed post-record claims round.
- R2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/v8143-critique.md | action: document | note: execution receipts bound in Lane Evidence with mocked-versus-live labeled.
- F1-markers | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_git.py | action: fix | note: merge-state check unions unmerged entries with diff-check marker paths; re-review passed.
- F1-receipt | bin: over-worry | evidence: strong | ref: tests/charness_cli/test_task_run_merge_checkpoint_877.py | action: fix | note: finding rebutted (e2e failed-lane tests assert target_sha on the final payload); composition gap closed with a resolved-merge e2e test.
- F2-recall | bin: over-worry | evidence: strong | ref: scripts/task_run/task_run_scope_evidence.py | action: document | note: finding rebutted (#880 rationale already in the docstring, boundary and recall pinned by tests); accepted by the R5 re-read.
- R1-completion | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/critique/workers/release-8-14-3-issue-resolution-r6/worker-report.yaml | action: defer | note: completion chain bound in R6; passed with zero findings.

## Reviewer Tier Evidence

- Requested tier: high-leverage (release closeout review)
- Requested spawn fields: run_review.py file-backed workers, adapter backend codex_exec, 900s timeout, read-only capability envelope; lenses: correctness-and-contract, correctness-recheck, release-operational, guard-population
- Host exposure state: host-defaulted
- Application state: four worker findings received in parent context; read-only boundary_ok true on all four lifecycles; model/effort mapping not host-visible
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: charness-artifacts/critique/workers/release-8-14-3-issue-resolution-r6/worker-report.yaml
- Worker report identity: 18cdc50da447df7ad49a2b082b678388ccfaad948f25e53af1ca949fd3e8fef9
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: d8b6309ca8386d1b0abcfa409d8b626293c832d62482e330b543f27fe857b8c8
- Worker report input identity: 1eeb8a99496a75e9ce4d5df70123eecd303bf77b07e1d27826608ea090423fce
- Worker report parent receipt identity: parent-0676fea86b7bc895301223b1c205df2a5bf80cddef69052b
- Worker report findings identity: 700d49fecdd5d0bfb662915e15bac652083671babe87174114b7def25a341019
- Worker reports (all five; the closing report above is the approval carrier):
  - release-8-14-3-correctness (block): charness-artifacts/critique/workers/release-8-14-3-correctness/worker-report.yaml sha256 3d7fe9107d454b1ab2d382ecb674dc04e63aa317af2a905519f29de0af4d1ae0
  - release-8-14-3-correctness-followup (defer): charness-artifacts/critique/workers/release-8-14-3-correctness-followup/worker-report.yaml sha256 0901d8c91c2cc58465e7cca3c107a281b4a7cda332633bdb1d78322f61a15c1f
  - release-8-14-3-operational (defer): charness-artifacts/critique/workers/release-8-14-3-operational/worker-report.yaml sha256 bf2b21fa84db696a7fd29f6355f26e3730d678bf832ce86e1a7be3fcc3722e4e
  - release-8-14-3-carrier-supplement (block): charness-artifacts/critique/workers/release-8-14-3-carrier-supplement/worker-report.yaml sha256 e9cc68612991df24e0db59813e0603ab1bb01cec3305ac5773ebba5e29c14c6d
  - release-8-14-3-closing (pass): charness-artifacts/critique/workers/release-8-14-3-closing/worker-report.yaml sha256 568553637d4ada43699f3c697464c468ce570347ad2f461ae13d1dfc8695a234
  - release-8-14-3-issue-resolution (block): charness-artifacts/critique/workers/release-8-14-3-issue-resolution/worker-report.yaml sha256 0a2b81796c7cc77cada5617de5bf326d6db6809b9d35c06a14a03f86e85abcf6
  - release-8-14-3-issue-resolution-r2 (pass): charness-artifacts/critique/workers/release-8-14-3-issue-resolution-r2/worker-report.yaml sha256 8d7b66f094fabf4c1bb8c0edeebe83b09a0e8cd45f52a3333beb80dcbed5b8e0
  - release-8-14-3-issue-resolution-r3 (pass): charness-artifacts/critique/workers/release-8-14-3-issue-resolution-r3/worker-report.yaml sha256 9dc7510ce964c4366e20b105aac7a68b3f142fdd8e668c33a9087a57d57c9685
  - release-8-14-3-issue-resolution-r4 (block): charness-artifacts/critique/workers/release-8-14-3-issue-resolution-r4/worker-report.yaml sha256 c927a75bd10330202e2a37c8209497aa65f5faa9a99ae790b5d302d1b1b7c5a6
  - release-8-14-3-issue-resolution-r5 (defer): charness-artifacts/critique/workers/release-8-14-3-issue-resolution-r5/worker-report.yaml sha256 ceb58f68851400596fa0d78ebc2d49512810599e5a500ba97a6dd13c6e987882
  - release-8-14-3-issue-resolution-r6 (pass): charness-artifacts/critique/workers/release-8-14-3-issue-resolution-r6/worker-report.yaml sha256 18cdc50da447df7ad49a2b082b678388ccfaad948f25e53af1ca949fd3e8fef9

## Fresh-Eye Satisfaction

worker-delivered: eleven file-backed worker findings received and triaged; four block-verdicts repaired or rebutted with executed proof, three deferrals answered by supplemental runs plus in-artifact receipts and the designed claims round, and an issue-resolution completion-bound pass with zero findings carries the approval.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release-8-14-3-issue-resolution-r6-packet.json
- Packet path: charness-artifacts/critique/release-8-14-3-issue-resolution-r6-packet.json
- Packet sha256: d8b6309ca8386d1b0abcfa409d8b626293c832d62482e330b543f27fe857b8c8
- Identity sha256: 1eeb8a99496a75e9ce4d5df70123eecd303bf77b07e1d27826608ea090423fce

The closing packet binds the final 13-file tree and is current: no code
changed after its review ran. Earlier packets below were current when their
reviews ran and were superseded by same-session repairs, which is the
expected shape when findings are repaired instead of waived. Packet audit
trail (paths, packet SHA256, reviewed-input SHA256, currency):

```text
charness-artifacts/critique/release-8-14-3-issue-resolution-r6-packet.json
  packet d8b6309ca8386d1b0abcfa409d8b626293c832d62482e330b543f27fe857b8c8
  input 1eeb8a99496a75e9ce4d5df70123eecd303bf77b07e1d27826608ea090423fce
  current: binds the final tree (13 changed files plus 3 issue bodies plus 2 unchanged completion-chain context files)
charness-artifacts/critique/release-8-14-3-issue-resolution-r5-packet.json
  packet 2295b47c226e2b18b2398d2773923cc871c5361a3bc601d98b430fd2c428876f
  input 7b3d072dead0ae8a793991f8926aba67237b86de1be8f4702ec63849678060d6
  superseded by the completion-chain binding (defer R1-completion answered)
charness-artifacts/critique/release-8-14-3-issue-resolution-r4-packet.json
  packet 7b526dd42e04e826789eef393c415457b089f3e60542ec09b573029617edfd47
  input 096cf0e174a71287f34cb7eac2c1e4be56df92a990e6edf7e88ba235a338125b
  superseded by the R5/R6 re-reads (block F1-receipt/F2-recall rebutted)
charness-artifacts/critique/release-8-14-3-issue-resolution-r3-packet.json
  packet 17936592c4637cd7d30e7e7f5c3e4bc71af3bce75bbd287e740a2feb2b1f931e
  input 8c7bc52bc08709a246d241213db030ec365b2d59820997afadbcfa5d3a63d041
  superseded by the whitespace normalization (same content, committable bytes; R3 pass stands as evidence)
charness-artifacts/critique/release-8-14-3-issue-resolution-r2-packet.json
  packet 1f147cccc0e4f708fcdbef10f0c03a38fa1436a416d1d01e8f68c02d90c7e935
  input c0ba5deab5a1763c3c12d1670c829de7629571dde7c0e35f528126e7e87123b8
  superseded by the issue-body relocation (same bytes, legal paths; R2 pass stands as evidence)
charness-artifacts/critique/release-8-14-3-issue-resolution-packet.json
  packet 13906134ef14e8f3fa58a0cd2833652b57e56b71d7efd0be8fb9c440e2d28026
  input dd4c637e4edc38f0393686ffc1ecb4aaf7999b890237905567cf7c7fe609dc62
  superseded by the F1-markers repair
charness-artifacts/critique/release-8-14-3-closing-packet.json
  packet 030cd37a8155528adf11488aa9a101c29345f6f2724a1a28fd35514ea6140359
  input 89cebf2d9a0c839a76308a8ff04c39876b782a7b18ef463e6beefe95d3ab97c9
  superseded by the F1-markers repair
charness-artifacts/critique/release-8-14-3-correctness-packet.json
  packet b70bcfcc539aae78fff31ca37b98bdcad0a74d9e1655fb57287a2c4483bd0b4a
  input 77bcdf33b86992299c08edb518ffa99ec0de6c20cc705834b418c454d1936bc6
  superseded by the F1 repair (11 files, pre-repair tree)
charness-artifacts/critique/release-8-14-3-correctness-followup-packet.json
  packet 8d91b163d0712d284b6a01df193366b6ab591b6a26dbb76f6a26fb5ffe2b8c1
  input 6d5f3fa255be6197e6e2c4443ac90b7cc90fe5d4d9d96ce773f88339e3268f2c
  superseded by the F1-population repair (5 repair files)
charness-artifacts/critique/release-8-14-3-operational-packet.json
  packet cf4b8e4d4894013b0e02abfde100e631117ddbc1c47dd1ab0d6154b1671bf557
  input d663f3fb5c40212368ad2aa3c739542c3ae8991faf5d0c805812c78213266e65
  superseded by the F1-population repair (11 files, post-F1-repair tree)
charness-artifacts/critique/release-8-14-3-carrier-supplement-packet.json
  packet 907c5833432655f1b58145645e1bacdf09cbde39c743f9a1ce64f00f4d06d4aa
  input b95ac40703419a2028558486293ada651441078003f882bdbbb202c1f16b125a
  bound paths byte-identical in the final tree; follow-up context superseded
```

## Boundary Ownership

- Producer: the Claude CLI input contract (external; rejects draft 2020-12 `$schema` in the inline form) and the canonical bounded-review schema file (unchanged)
- Consumer: the `claude` CLI process receiving `--json-schema`, and worker receipt readers receiving the stderr line
- Owning surface: reviewer worker backend (the CLI-invocation owner in skills/shared)
- Verdict: owned-correctly

## Bump Honesty

Patch 8.14.2 → 8.14.3. Three bug fixes with tests, no new behavior surface,
no deprecation, no migration. Per the version policy this is a patch: the
kind of change where the honest question is "does anything outside the fixes
change," and the Surface-Lock Inventory above answers nothing does.

## Lane Evidence

- Focused suites on the final tree: test_task_run_merge_checkpoint_877.py 12 passed; test_task_run_scope_evidence_879.py 6 passed; test_reviewer_worker_backend.py 10 passed.
- tests/charness_cli: 1303 passed (post-split). Reviewer neighbors (worker, runner, lifecycle): 38 passed.
- Full read-only lane on the post-split tree: 85 passed, 0 failed, 5 not run (4 opt-in unmet, check-coverage read-only-excluded).
- Release lane on the staged fix tree: 90 passed, 0 failed including release-changed-line-coverage.
- Closing worker review on the final tree: pass, 0 findings, approval_eligible true.
- Issue-resolution re-review after the marker repair: pass, 0 findings, approval_eligible true.
- Issue-resolution rebind at the relocated issue-body paths: pass, 0 findings, approval_eligible true.
- Issue-resolution completion-bound pass with the target_head chain in front of the reviewer: pass, 0 findings, approval_eligible true.
- ruff check on scripts/task_run and the shared reviewer script: clean (the repo's pre-existing ruff-format drift left untouched).
- Changed-line execution probe: every changed production line executes under the focused tests; no multi-line changed statement survives in production code.
- Live Claude CLI probe: the issue's exact `$schema` payload is rejected with its exact error, and the same call without `$schema` proceeds past schema validation (then stops on expired operator OAuth, which is environmental).

## Verdict

SHIP v8.14.3 as a patch release. All four worker block-verdicts were repaired or rebutted with
executed proof; all three deferrals are answered (receipts above, version truth at
the claims round); the issue-resolution completion-bound pass approves the final tree. Carried
residuals: no end-to-end claude_p run exists (pre-existing gap, OAuth
expired); sampled-mutant verdicts on these files await a scheduled lane.
