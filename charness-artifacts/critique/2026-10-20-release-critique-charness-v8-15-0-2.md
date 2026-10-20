# Release Critique: Charness v8.15.0
Date: 2026-10-20

## Decision Under Review

Release `454191a8f` as minor version 8.15.0. This record supersedes the candidate critique `2026-10-20-release-critique-charness-v8-15-0.md`, which approved only the event-stamping candidate at `526fbaa17`. Since that review the release gained four more units:

- the event-capture close and clock repair (`37a0e7fc6`);
- network access for executor lanes (`0d4b1f703`);
- the lane progress rule, which replaces the wall-clock default (`c9ba15393`..`edd6fde20`, with design and implementation critiques in `2ea461a0c`);
- debug follow-up records named per lane (`6d7042f8e`).

It also covers the repairs from two review lanes over the final candidate, plus the extended notes. The first lane is the fresh release critique and its follow-ups. The second is the claims round on a first prepared release record. That record, `ea8f9dea5`, was never pushed or tagged; the claims round blocked it, and it was withdrawn.

## Release Scope

- Version: `8.15.0`
- Tag: `v8.15.0`
- Bump rationale: minor. `task run` keeps its flags and result shape. The release changes these defaults:
  - `--timeout-seconds` no longer has a default;
  - executor lanes now have network access;
  - the task result gains `progress_guard.progress_rule` and `execution.preemptions`.

  These are behavior changes behind existing invocations. No option or field was removed, and the notes tell launchers what to change.
- Consumer change: a launcher that wants the progress rule alone drops `--timeout-seconds`. If its longest legitimate command exceeds the default window, it also sets the window above that command.

## Surface-Lock Inventory

- Generated artifacts: materialized plugin and marketplace manifests produced by the publish helper.
- Consumer-visible behavior:
  - the progress rule, with its receipt and live view;
  - the removed `--timeout-seconds` default;
  - network access in Codex and Muse lanes, while read-only reviewers drop it;
  - the stamped events log;
  - `task status --commands`;
  - `execution.event_capture_incomplete`;
  - debug follow-up record names.
- Documentation: `docs/agent-task-runs.md`, `docs/cli-reference.md`, `charness-artifacts/spec/lane-progress-rule.md`, and the v8.15.0 release notes.
- Adapter and integration surfaces: none changed.

## Verification Scope Decision

- Claim under test: no lane is left unbounded once the timeout default is gone; the progress rule neither kills a productive lane nor misses a lane that only reads; network access applies only to workspace-write lane sandboxes; distinct readable non-default branches share a debug follow-up record only on a hash-prefix collision; and the notes, docs, spec and docstrings claim no more than the code and its tests show.
- Changed surfaces: in `ddab9c888..454191a8f`, the `scripts/task_run/` modules (progress, rule, execution, runtime, plan, detach, signals, event timing, self-review and brief critique), the `charness` CLI help, `skills/public/debug/scripts/debug_followup_routing.py`, their tests, the docs above, and the release notes.
- Minimum sufficient proof: a fresh file-backed read-only review over every changed source, test, doc and the notes (`release-8150-final`), then narrowed follow-ups on each repair until one passed (`release-8150-final-followup23`); the parent's release changed-line coverage gate (clean for `1f09b8012..HEAD`) and focused pytest suites; live probes that drove a real `codex exec` lane through a loop preemption and a window checkpoint; and the receipts of the ceal lanes that ran under the live tree.
- Deliberately omitted checks: the reviewers did not execute tests, and the parent's runs stand in; the full quality lane runs in the publish helper and the pre-push hook, not here.
- Verifier contract: `skills/shared/references/bounded-review-result.schema.json` plus packet and worker-report identity readback; unchanged in this release.
- Failure classification: subject-defect
- Negative control: none with rationale: each code repair is pinned by a test that fails on the pre-repair code (a negative or zero window, aliasing branch names, an unreadable git link, reused Codex item ids, a short sink write, Muse read tools, and the read-only reviewer argv), and the passing follow-up judged the frozen repaired inputs.
- Subject identity: sha256:69aecc6e5fa245110d297ba5fd6cb913d35866c1116054adce0cb790e77fcf46
- Verifier identity: sha256:67288fc99eab9333366dfd0e07094b5b9dfec0f91f95b4e4cdc8a508a41c0304
- Input identity: sha256:aa7ffed8edf2ad9a8774903dff9268f532eec86b295c42931b594ea555ee576c
- Failure identity: stable:no-failure
- Evidence identity: sha256:102a385952a5d8c57ab2e22b24f71de9e85d5549187877e08484ec21be0ac582
- Retry disposition: retry-new-identity
- Retry key: sha256:9409d23aa8e22538f7cbd28f050a061c5657899396432cb70d1035cd6548ca1a

## Failure Angles

- Gawande / operational: whether the progress rule is safe once no wall clock bounds a lane.
  - Code repairs:
    - a negative window disabled the rule (R-002);
    - a zero window still raised loop messages (claims B1);
    - debug lane tokens could alias (R-003);
    - the `--commands` reader merged reused Codex item ids across a resume (claims B2);
    - a short sink write left the capture "complete" (followup8 R-002);
    - read-only reviewers carried the lane network key (claims A6);
    - Muse read and search tools counted as progress (followup15 R-004).
  - Confirmed safe:
    - watcher failures stop the lane;
    - Codex resume is probed and falls back to relaunch-in-place;
    - read-only review sandboxes no longer carry the network setting.
- Minto / communication: whether the notes, docs, spec and docstrings match the code.
  - Repaired across the follow-ups:
    - same-session and network claims stated beyond the evidence;
    - byte-for-byte and loss-case wording;
    - durations described as upper bounds;
    - family counts presented as exact;
    - an unreadable worktree described as progress;
    - stale timeout framing;
    - closed-form timing bounds, now stated as nominal windows and due-check counts;
    - the young-command deferral of the request or the stop;
    - a loop message interrupting a parallel command.
- Release: whether minor is the right bump given the default changes. The reviewer deferred this, because the packet contains no repo semver policy.

## Counterweight Pass

- Act Before Ship:
  - code fixes with tests: R-002, R-003, claims B1, claims B2, claims A6, followup8 R-002, followup15 R-004;
  - notes, docs and spec wording: claims A1-A5 and the later follow-up wording findings.
- Bundle Anyway: R-001, stated as launcher guidance in the notes and the spec (set the window above the longest legitimate command).
- Over-Worry: none.
- Valid but Defer:
  - R-004 (`latest.md` can still conflict across parallel lanes): the operator required keeping the pointer semantics, and the notes state the limitation.
  - The bump size: the repo has no semver policy that makes a changed default major.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/2026-10-20-v8.15.0-notes.md | action: document | note: R-001. A command still running a window later can be killed. The notes and spec tell launchers to set the window above their longest legitimate command.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_progress.py | action: fix | note: R-002 and claims B1. A negative window falls back to the default, and `0` turns the whole rule off, loop check included (`43f81d5bd`, `49ad61a19`).
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/debug/scripts/debug_followup_routing.py | action: fix | note: R-003. Every readable non-default branch yields a slug plus an 8-hex hash of the raw branch, with `branch` as the fallback (`978119cf5`..`1ad900e68`).
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/public/debug/scripts/debug_followup_routing.py | action: document | note: R-004. `latest.md` can still conflict across parallel lanes. The operator kept its semantics, and the notes state the limitation.
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_event_timing.py | action: fix | note: claims B2 and followup8 R-002. Reused Codex item ids open new commands (`b84e4dfb5`). A short sink write is recorded as lost bytes (`7f407e378`).
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_runtime.py | action: fix | note: claims A6. `read_only_codex` drops the lane network key for self-review and the brief critique (`18e520d12`).
- F7 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_progress_rule.py | action: fix | note: followup15 R-004. Only Muse edit tools count as outcomes (`3171a9635`).
- F8 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-10-20-v8.15.0-notes.md | action: fix | note: notes, docs, spec and docstring wording repaired across the follow-ups, ending at `454191a8f`.

## Operator Action Required

A launcher that passes `--timeout-seconds` keeps that hard cap until it drops the flag. To rely on the progress rule alone, drop the flag. If the longest legitimate command exceeds the default window, set `CHARNESS_TASK_RUN_PROGRESS_WINDOW_SECONDS` above it.

## Upgrade Path

Run `charness update`, then use `charness version` to read back the installed version.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: run_review.py file-backed worker, adapter backend codex_exec, read-only capability envelope, follow-up from the previous follow-up's result
- Host exposure state: host-defaulted
- Application state: the worker report records model_application_state unverified-by-provider, so the requested model and effort are not host-confirmed; the lifecycle records a read-only boundary
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: charness-artifacts/critique/workers/release-8150-final-followup23/worker-report.yaml
- Worker report identity: 896382093e8453ace4aef8f6416939c2ed413964d9468777ae40817eedb10ff0
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: a381d1c261744de0d0ed276ad0dcbab89065fefa3e488d80583169589fb841d5
- Worker report input identity: aa7ffed8edf2ad9a8774903dff9268f532eec86b295c42931b594ea555ee576c
- Worker report parent receipt identity: parent-115021bc573a3e9f7a5c173bcf80bc023b315aaed8e2c7a6
- Worker report findings identity: 102a385952a5d8c57ab2e22b24f71de9e85d5549187877e08484ec21be0ac582

## Fresh-Eye Satisfaction

worker-delivered:

- The fresh file-backed read-only worker `release-8150-final` returned `block` with R-001 to R-006.
- Narrowed follow-ups ran on each repair. `release-8150-final-followup7` passed before the first prepare.
- After the claims round blocked that prepared record, `release-8150-final-followup8` to `-followup22` reviewed the repairs and the widened surface, and each returned `block` or `defer` on a remaining finding.
- `release-8150-final-followup23` returned `pass` with an approval-eligible carrier bound to the packet below.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release-8150-final-followup23-packet.md
- Packet path: charness-artifacts/critique/release-8150-final-followup23-packet.json
- Packet SHA256: a381d1c261744de0d0ed276ad0dcbab89065fefa3e488d80583169589fb841d5
- Identity SHA256: aa7ffed8edf2ad9a8774903dff9268f532eec86b295c42931b594ea555ee576c
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8150-final-followup23-packet.json --packet-sha256 a381d1c261744de0d0ed276ad0dcbab89065fefa3e488d80583169589fb841d5 --identity-sha256 aa7ffed8edf2ad9a8774903dff9268f532eec86b295c42931b594ea555ee576c`

## Boundary Ownership

- Producer:
  - `LaneProgressWatch` and `ProgressRule` in `scripts/task_run/`;
  - the executor argv builders in `task_run_runtime.py`;
  - `StampingPipe` and the timing reader;
  - the debug follow-up router.
- Consumer: lane launchers (ceal), `task status` readers, the task result, and debug skill users.
- Owning surface:
  - the rule extends the existing progress watch and steer delivery owners;
  - the network flags live in the existing argv builders;
  - the naming fix lives in the existing router.
- Verdict: owned-correctly
