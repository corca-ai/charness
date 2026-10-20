# Release Critique: Charness v8.15.0
Date: 2026-10-20

## Decision Under Review

Release `9da6bf77e` as minor version 8.15.0. This record supersedes the candidate critique `2026-10-20-release-critique-charness-v8-15-0.md`, which approved only the event-stamping candidate at `526fbaa17`. Since that review the release gained four more units:

- the event-capture close and clock repair (`37a0e7fc6`);
- network access for executor lanes (`0d4b1f703`);
- the lane progress rule, which replaces the wall-clock default (`c9ba15393`..`edd6fde20`, with design and implementation critiques in `2ea461a0c`);
- debug follow-up records named per lane (`6d7042f8e`).

It also covers the repairs from two review lanes over the final candidate, plus the extended notes. The first lane is the fresh release critique and its follow-ups. The second is the claims rounds on two prepared release records, `ea8f9dea5` and `b8d41c368`. Neither was pushed or tagged; a claims round blocked each, and each was withdrawn by a soft reset.

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
- Changed surfaces: in `ddab9c888..9da6bf77e`, the `scripts/task_run/` modules (progress, rule, execution, runtime, plan, detach, signals, event timing, self-review and brief critique), the `charness` CLI help, `skills/public/debug/scripts/debug_followup_routing.py`, their tests, the docs above, and the release notes.
- Minimum sufficient proof: a fresh file-backed read-only review over every changed source, test, doc and the notes (`release-8150-final`), then narrowed follow-ups on each repair until one passed (`release-8150-final-followup34`, then `-followup35` on the last test-only commit); the parent's release changed-line coverage gate (clean for `1f09b8012..HEAD`) and focused pytest suites; live probes that drove a real `codex exec` lane through a loop preemption and a window checkpoint; and the receipts of the ceal lanes that ran under the live tree.
- Deliberately omitted checks: the reviewers did not execute tests, and the parent's runs stand in; the full quality lane runs in the publish helper and the pre-push hook, not here.
- Verifier contract: `skills/shared/references/bounded-review-result.schema.json` plus packet and worker-report identity readback; unchanged in this release.
- Failure classification: subject-defect
- Negative control: none with rationale: each code repair is pinned by a test that fails on the pre-repair code (a negative or zero window, aliasing branch names, an unreadable git link, reused Codex item ids, a short sink write, Muse read tools, the read-only reviewer argv, a request delivered between checks, a command starting during a slow tree probe, a completion probe holding the rule lock, and the fallback completion probe, whose `state = None` and deleted-line mutants both fail its test), and the passing follow-ups judged the frozen repaired inputs.
- Subject identity: sha256:3713fbfbe892f9e81b194ced00a6dd46d202f2e1edac78bd1752b88faba84d44
- Verifier identity: sha256:67288fc99eab9333366dfd0e07094b5b9dfec0f91f95b4e4cdc8a508a41c0304
- Input identity: sha256:6d24313b87f02da4519e3c74d0d0fb58dbb54d7a4642ff496282ea75834c0633
- Failure identity: stable:no-failure
- Evidence identity: sha256:138b1057c66fd17132128ff24a5eac5420b4289d78c23cbfc7e64b0d11fd43ec
- Retry disposition: retry-new-identity
- Retry key: sha256:61cf0dc8083b54c7e296894805526145d1eb54eeedec10a002ad2025977d7898

## Failure Angles

- Gawande / operational: whether the progress rule is safe once no wall clock bounds a lane.
  - Code repairs:
    - a negative window disabled the rule (R-002);
    - a zero window still raised loop messages (claims B1);
    - debug lane tokens could alias (R-003);
    - the `--commands` reader merged reused Codex item ids across a resume (claims B2);
    - a short sink write left the capture "complete" (followup8 R-002);
    - read-only reviewers carried the lane network key (claims A6);
    - Muse read and search tools counted as progress (followup15 R-004);
    - a request delivered between checks could be followed by a stop seconds later (claims round 2 C-B1);
    - the checkpoint and the stop did not name or count every command the kill interrupts (follow-ups 24 to 33);
    - a window check probing the tree under the rule lock could kill a command that started during the probe (follow-ups 24 to 33).
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
    - a loop message interrupting a parallel command;
    - the per-invocation scope of `--timeout-seconds` (claims round 2 C-A2);
    - the young-command guarantee scoped to starts the rule has seen, with the reader-probe exception and the two-check deferral of a start first seen mid-probe disclosed.
- Release: whether minor is the right bump given the default changes. The reviewer deferred this, because the packet contains no repo semver policy.

## Counterweight Pass

- Act Before Ship:
  - code fixes with tests: R-002, R-003, claims B1, claims B2, claims A6, followup8 R-002, followup15 R-004, claims C-B1, and the follow-up 24 to 33 repairs;
  - notes, docs and spec wording: claims A1-A5, C-A1 to C-A4, and the later follow-up wording findings.
- Bundle Anyway: R-001, stated as launcher guidance in the notes and the spec (set the window above the longest legitimate command).
- Over-Worry: none.
- Valid but Defer:
  - R-004 (`latest.md` can still conflict across parallel lanes): the operator required keeping the pointer semantics, and the notes state the limitation.
  - The bump size: the repo has no semver policy that makes a changed default major.
  - The followup34 advisories: the notes call a reader-probe start unnamed but not also uncounted (the spec says both), and `docs/agent-task-runs.md` says a young command delays a check where the due check runs and defers its action.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/2026-10-20-v8.15.0-notes.md | action: document | note: R-001. A command still running a window later can be killed. The notes and spec tell launchers to set the window above their longest legitimate command.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_progress.py | action: fix | note: R-002 and claims B1. A negative window falls back to the default, and `0` turns the whole rule off, loop check included (`43f81d5bd`, `49ad61a19`).
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/debug/scripts/debug_followup_routing.py | action: fix | note: R-003. Every readable non-default branch yields a slug plus an 8-hex hash of the raw branch, with `branch` as the fallback (`978119cf5`..`1ad900e68`).
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/public/debug/scripts/debug_followup_routing.py | action: document | note: R-004. `latest.md` can still conflict across parallel lanes. The operator kept its semantics, and the notes state the limitation.
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_event_timing.py | action: fix | note: claims B2 and followup8 R-002. Reused Codex item ids open new commands (`b84e4dfb5`). A short sink write is recorded as lost bytes (`7f407e378`).
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_runtime.py | action: fix | note: claims A6. `read_only_codex` drops the lane network key for self-review and the brief critique (`18e520d12`).
- F7 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_progress_rule.py | action: fix | note: followup15 R-004. Only Muse edit tools count as outcomes (`3171a9635`).
- F8 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-10-20-v8.15.0-notes.md | action: fix | note: notes, docs, spec and docstring wording repaired across the follow-ups, ending at `4f3c633e2`.
- F9 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_progress_rule.py | action: fix | note: claims C-B1. A request delivered between checks is `delivered-between-checks`, and the next check opens its window instead of stopping (`d1ff04f3f`).
- F10 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_progress_rule.py | action: fix | note: follow-ups 24 to 33. The checkpoint and the stop name every interrupted command they have text for and count the rest (`fdcc6d80f`, `8b51e4620`, `d394845c1`); tree probes run outside the rule lock and command ages are taken from before the check's probe (`26131a7f6`, `c6843bd27`); the fallback completion probe is covered (`9da6bf77e`).
- F11 | bin: act-before-ship | evidence: strong | ref: skills/public/debug/scripts/debug_followup_routing.py | action: fix | note: claims C-A3. The first follow-up name on a lane branch carries the lane token too (`0412e55ff`).
- F12 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/release/2026-10-20-v8.15.0-notes.md | action: document | note: followup34 advisories on the notes' unnamed-but-not-uncounted wording and the docs summary's "delays a check" phrasing; the spec states both accurately.

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
- Worker report: charness-artifacts/critique/workers/release-8150-final-followup35/worker-report.yaml
- Worker report identity: be009e88c8a942c2714268c04b83101f7813ac417b8616ff50a4b37688d9687b
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: 70749a5cf52d9e9ea028773c9991a6e19a1cd962b2c336aeadd08433da679098
- Worker report input identity: 6d24313b87f02da4519e3c74d0d0fb58dbb54d7a4642ff496282ea75834c0633
- Worker report parent receipt identity: parent-7bb786297a68c0317066467485a54d94a78b290924310948
- Worker report findings identity: 138b1057c66fd17132128ff24a5eac5420b4289d78c23cbfc7e64b0d11fd43ec

## Fresh-Eye Satisfaction

worker-delivered:

- The fresh file-backed read-only worker `release-8150-final` returned `block` with R-001 to R-006.
- Narrowed follow-ups ran on each repair. `release-8150-final-followup7` passed before the first prepare.
- After the claims round blocked that prepared record, `release-8150-final-followup8` to `-followup22` reviewed the repairs and the widened surface, and each returned `block` or `defer` on a remaining finding.
- `release-8150-final-followup23` returned `pass`, and the second prepared record followed. After its claims round blocked it, `release-8150-final-followup24` to `-followup33` reviewed the repairs, and each returned `block` on a remaining finding.
- `release-8150-final-followup34` returned `pass` at `1277baf9f` with two advisories. `release-8150-final-followup35` returned `pass` on the test-only commit `9da6bf77e`, with an approval-eligible carrier bound to the packet below.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release-8150-final-followup35-packet.md
- Packet path: charness-artifacts/critique/release-8150-final-followup35-packet.json
- Packet SHA256: 70749a5cf52d9e9ea028773c9991a6e19a1cd962b2c336aeadd08433da679098
- Identity SHA256: 6d24313b87f02da4519e3c74d0d0fb58dbb54d7a4642ff496282ea75834c0633
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8150-final-followup35-packet.json --packet-sha256 70749a5cf52d9e9ea028773c9991a6e19a1cd962b2c336aeadd08433da679098 --identity-sha256 6d24313b87f02da4519e3c74d0d0fb58dbb54d7a4642ff496282ea75834c0633`

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
