# Release Critique: Charness v8.15.0
Date: 2026-10-20

## Decision Under Review

Release `539d8f64c` as minor version 8.15.0. This record supersedes the candidate critique `2026-10-20-release-critique-charness-v8-15-0.md`, which approved only the event-stamping candidate at `526fbaa17`. Since that review the release gained four more units. The first is the event-capture close and clock repair (`37a0e7fc6`). The second gives executor lanes network access (`0d4b1f703`). The third is the lane progress rule, which replaces the wall-clock default (`c9ba15393`..`edd6fde20`, design and implementation critiques in `2ea461a0c`). The fourth names debug follow-up records per lane (`6d7042f8e`). This record also covers the release-critique repairs `978119cf5`..`539d8f64c` and the extended notes.

## Release Scope

- Version: `8.15.0`
- Tag: `v8.15.0`
- Bump rationale: minor. `task run` keeps its flags and result shape. `--timeout-seconds` loses its default, executor lanes gain network access, and the task result gains `progress_guard.progress_rule` and `execution.preemptions`. These are behavior changes behind existing invocations with no removed option or field, and the notes tell launchers what to change.
- Consumer change: a launcher that wants the progress rule alone drops `--timeout-seconds` and sets the progress window above its longest legitimate command if that exceeds the default.

## Surface-Lock Inventory

- Generated artifacts: materialized plugin and marketplace manifests produced by the publish helper.
- Consumer-visible behavior: the progress rule and its receipt and live view, the removed `--timeout-seconds` default, network access in Codex and Muse lanes, the stamped events log, `task status --commands`, `execution.event_capture_incomplete`, and debug follow-up record names.
- Documentation: `docs/agent-task-runs.md`, `docs/cli-reference.md`, `charness-artifacts/spec/lane-progress-rule.md`, and the v8.15.0 release notes.
- Adapter and integration surfaces: none changed.

## Verification Scope Decision

- Claim under test: no lane is left unbounded when the timeout default goes, and the progress rule does not kill a productive lane. Network access applies only to workspace-write lane sandboxes. Distinct readable non-default branches never share a debug follow-up record except on a hash-prefix collision. The notes claim no more than the code and its tests show.
- Changed surfaces: the `scripts/task_run/` progress, execution, runtime, plan, detach and signal modules, the `charness` CLI help, `skills/public/debug/scripts/debug_followup_routing.py`, their tests, the docs above, and the release notes, in `ddab9c888..539d8f64c`.
- Minimum sufficient proof: one fresh file-backed read-only review over every changed source, test, doc and the notes (`release-8150-final`). That review blocked, and narrowed follow-ups ran on each repair until one passed (`release-8150-final-followup7`). The parent also ran the release changed-line coverage gate (clean for `1f09b8012..HEAD`) and the focused pytest suites. Live probes on this machine drove a real `codex exec` lane through a loop preemption and a window checkpoint, and the ceal lanes that ran under the live tree carry receipts.
- Deliberately omitted checks: the reviewers did not execute tests; the parent's runs stand in. The full quality lane runs in the publish helper and the pre-push hook, not here.
- Verifier contract: `skills/shared/references/bounded-review-result.schema.json` plus packet and worker-report identity readback; unchanged in this release.
- Failure classification: subject-defect
- Negative control: none with rationale: each repair is pinned by a test that fails on the pre-repair code. These tests cover a negative window disabling the rule, aliasing branch names sharing a record, and an unreadable git link. The passing follow-up judged the frozen repaired inputs.
- Subject identity: sha256:e5f7fa31d37c83f6db4ef300b22f0db25f4abf42aab0edb4803dea12c2e698b2
- Verifier identity: sha256:67288fc99eab9333366dfd0e07094b5b9dfec0f91f95b4e4cdc8a508a41c0304
- Input identity: sha256:8e28fcc50b56126ff6e07cb95eede64cd92a1b62c6949c56627027fefc41d1ea
- Failure identity: stable:no-failure
- Evidence identity: sha256:9bbb44b962443ff9d336d5c7da6c0b1e22249d36b0f96e2988cec40ef57d975d
- Retry disposition: retry-new-identity
- Retry key: sha256:9a7b875551bc91c67e21ebada536175ebac0621642548ef2eb1a3c2038fbc07b

## Failure Angles

- Gawande / operational: whether the progress rule is safe once no wall clock bounds a lane. The first review found three problems. A long legitimate command can be killed (R-001). A negative window silently disabled the only bound (R-002). Debug lane tokens were lossy, so distinct branches could share a record (R-003). It confirmed that watcher failures stop the lane, that Codex resume is probed and falls back to relaunch-in-place, and that read-only review sandboxes are untouched by the network change.
- Minto / communication: whether the notes match the code. The first review found that same-session resume and network success were stated beyond the evidence (R-005), that byte-for-byte wording was not literal (R-006), and that `latest.md` can still conflict across parallel lanes (R-004). Later follow-ups narrowed the debug-naming sentence until it matched the code exactly (R-003 notes, R-007).
- Release: whether minor is the right bump given the default changes; the reviewer deferred this for lack of a repo semver policy in the packet.

## Counterweight Pass

- Act Before Ship: R-002 and R-003 were fixed in code with tests. R-005, R-006 and R-007 were fixed in the notes.
- Bundle Anyway: R-001, stated as launcher guidance in the notes and the spec (set the window above the longest legitimate command).
- Over-Worry: none.
- Valid but Defer: R-004. The operator required keeping the `latest.md` pointer semantics, and the notes state that parallel lanes can still both change `latest.md`. The bump-size question is also deferred, because the repo has no semver policy that makes a changed default major.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/2026-10-20-v8.15.0-notes.md | action: document | note: R-001. A command still running a window after its start can be killed; the notes and spec tell launchers to set the window above their longest legitimate command; the follow-up accepted it.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_progress.py | action: fix | note: R-002. A negative window now falls back to the default and only `0` turns the rule off (`43f81d5bd`, parametrized test); the follow-up verified it.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/debug/scripts/debug_followup_routing.py | action: fix | note: R-003. Every readable non-default branch now yields a slug plus an 8-hex hash of the raw branch, and a slugless name becomes `branch`. Aliasing tests cover separator, case, plain-versus-task and crafted-hash names (`978119cf5`, `8d8448b52`, `418408ab8`, `1ad900e68`). The follow-up verified it.
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/public/debug/scripts/debug_followup_routing.py | action: document | note: R-004. `latest.md` can still conflict across parallel lanes; the operator kept its semantics and the notes state the limitation.
- F5 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-10-20-v8.15.0-notes.md | action: fix | note: R-005, R-006 and R-007. The notes now name Codex resume as probed and Muse as unprobed, say the network tests check flags only, describe the added stamp and newline, and scope the debug-name guarantee to readable non-default branches.

## Operator Action Required

A launcher that passes `--timeout-seconds` keeps that hard cap until it drops the flag. To rely on the progress rule alone, drop the flag and set `CHARNESS_TASK_RUN_PROGRESS_WINDOW_SECONDS` above the longest legitimate command if that exceeds the default.

## Upgrade Path

Run `charness update`, then use `charness version` to read back the installed version.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: run_review.py file-backed worker, adapter backend codex_exec, read-only capability envelope, follow-up from the sixth follow-up's result
- Host exposure state: host-defaulted
- Application state: the worker report records model_application_state unverified-by-provider, so the requested model and effort are not host-confirmed; read-only boundary on the lifecycle
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: charness-artifacts/critique/workers/release-8150-final-followup7/worker-report.yaml
- Worker report identity: 402d90d53534be5b768e5db2953a6f21f404fa9dd7ecaeaf808ac84bdc142079
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: 4b77a64769c139b0d3ddb414640389fe739c4ab2925d0ac2e03b14c80ed897a7
- Worker report input identity: 8e28fcc50b56126ff6e07cb95eede64cd92a1b62c6949c56627027fefc41d1ea
- Worker report parent receipt identity: parent-07b8bf23869166fe9dc515b9004f7ea0886e7fc0acc30fd8
- Worker report findings identity: 9bbb44b962443ff9d336d5c7da6c0b1e22249d36b0f96e2988cec40ef57d975d

## Fresh-Eye Satisfaction

worker-delivered: the fresh file-backed read-only worker `release-8150-final` returned `block` with R-001 to R-006. The narrowed follow-ups `release-8150-final-followup` to `-followup6` each returned `block` on a remaining R-003 or R-007 notes or naming defect. `release-8150-final-followup7` returned `pass` with an approval-eligible carrier bound to the packet below.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release-8150-final-followup7-packet.md
- Packet path: charness-artifacts/critique/release-8150-final-followup7-packet.json
- Packet SHA256: 4b77a64769c139b0d3ddb414640389fe739c4ab2925d0ac2e03b14c80ed897a7
- Identity SHA256: 8e28fcc50b56126ff6e07cb95eede64cd92a1b62c6949c56627027fefc41d1ea
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8150-final-followup7-packet.json --packet-sha256 4b77a64769c139b0d3ddb414640389fe739c4ab2925d0ac2e03b14c80ed897a7 --identity-sha256 8e28fcc50b56126ff6e07cb95eede64cd92a1b62c6949c56627027fefc41d1ea`

## Boundary Ownership

- Producer: `LaneProgressWatch` and `ProgressRule` in `scripts/task_run/`, the executor argv builders in `task_run_runtime.py`, and the debug follow-up router.
- Consumer: lane launchers (ceal), `task status` readers, the task result, and debug skill users.
- Owning surface: the rule extends the existing progress watch and steer delivery owners; the network flags live in the existing argv builders; the naming fix lives in the existing router.
- Verdict: owned-correctly
