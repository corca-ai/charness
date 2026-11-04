# Release Critique: Charness v8.16.0
Date: 2026-11-05

## Decision Under Review

Release `5ffcdce91` as minor version 8.16.0. Since v8.15.0, main gains the previously unpushed task-run lane work: the opt-in Claude executor (`--executor claude`, `--claude-model`), Claude grants for `--grant-writable`, command durations in the events log, lane environment and progress-observation repairs, and Windows portability fixes. It also gains the debug planner fix that reads a `Risk Class` value apart from trailing prose, and the release repairs made during this pass: gate repairs, coverage tests, deterministic timing tests, and the critique repairs below.

## Release Scope

- Version: `8.16.0`
- Tag: `v8.16.0`
- Bump rationale: minor. The release adds a new executor and CLI option (`--executor claude`, `--claude-model`) and widens `--grant-writable` to Claude lanes. No option or field was removed, and existing Codex and Muse invocations keep working. The version policy names new operator-facing commands as minor.
- Consumer change: a launcher can opt into Claude lanes. A launcher that relied on a Codex lane writing under a `writable_roots` path from the operator's own Codex configuration must pass that directory with `--grant-writable`.

## Surface-Lock Inventory

- Generated artifacts: materialized plugin and marketplace manifests produced by the publish helper; `docs/cli-reference.md`.
- Consumer-visible behavior: the Claude executor and its sandbox; `--claude-model`; `--grant-writable` for Claude; `charness_duration_ms`; live `task status --commands`; the lane `TMPDIR` and Go cache placement; Codex lanes no longer inheriting `writable_roots`; the app-server exit message; debug planner Risk Class parsing.
- Documentation: `docs/claude-task-executor.md`, `docs/agent-task-runs.md`, `docs/cli-reference.md`, and the v8.16.0 notes.
- Adapter and integration surfaces: none changed.

## Verification Scope Decision

- Claim under test: a Claude lane cannot write outside its grants, read listed credentials or drive a host container daemon. The docs and notes state every remaining boundary gap. The debug planner fix keeps another subject's valid record with its subject. The notes claim no more than the code and tests show.
- Changed surfaces: `v8.15.0..5ffcdce91`, split across two reviewers. Part 1 covers the Claude executor, the task-run CLI and runtime, their tests, and the docs and notes. Part 2 covers the debug planner, lane environment and progress, Windows portability, test repairs, and the notes.
- Minimum sufficient proof: two fresh file-backed read-only reviews over the current files (`release-8160-claude-lane`, `release-8160-rest`). Then narrowed follow-ups on each repair until both passed (`-followup4`). Hand mutations of the covered lines (11 in the coverage tests; the masks for the new real-lane credential test). The full release lane runs in the publish helper and the pre-push hook.
- Deliberately omitted checks: the reviewers did not execute tests; the parent's focused runs stand in. No Windows host run.
- Verifier contract: `skills/shared/references/bounded-review-result.schema.json` plus packet and worker-report identity readback, unchanged in this release.
- Failure classification: subject-defect
- Negative control: command `pytest tests/charness_cli/test_task_run_claude_sandbox.py::test_listed_home_credentials_are_unreadable_in_a_real_lane` with `_SECRET_FILES` and `_SECRET_DIRECTORIES` emptied | expected refusal: the test fails | observed `3 failed`, and `3 passed` with the masks restored; a sandboxed connect to `/run/docker.sock` printed `connected` with the socket mask removed and is refused with it | receipt none; direct pytest and probe stdout in the release session
- Subject identity: sha256:269cbb9d2228cd11ab3b6953b1d6af40ceaedb8a7279485a69bcc69614f9dc6f
- Verifier identity: sha256:67288fc99eab9333366dfd0e07094b5b9dfec0f91f95b4e4cdc8a508a41c0304
- Input identity: sha256:776b7a6bf137a1b96c7b25d36d9c560f4b4099f26dd25aa64a1f7a6200057f0d
- Failure identity: stable:no-failure
- Evidence identity: sha256:70d3da668e3fd2f5a6c6cbe71896bcec426112052575726482a9d189a3cc0e45
- Retry disposition: first-attempt
- Retry key: sha256:f9b84242019baadcf4a6e4f49889196854914a69544890215408d83fffef58a4

## Failure Angles

- Gawande / operational and boundary safety (part 1):
  - unrestricted network egress (F-001);
  - unmasked `~/.docker`, `~/.pypirc` and Cargo credentials (F-002);
  - reachable container daemon sockets (F-003);
  - real-sandbox tests that skip without bubblewrap in CI (F-004);
  - CLI help that omitted Claude (F-005);
  - a workspace-scan claim broader than the scan (F-006);
  - a socket comment broader than the code (F-007);
  - no real-lane test for the new masks (F-008).
- Minto / claims and Weinberg / layer (part 2):
  - `cmd.exe` quoting overstated;
  - forced-class-plus-unknown Risk Class wording;
  - Windows lock fallback untested;
  - the Codex refresh tests' wait described too broadly;
  - event-driven tests unbounded when the event never arrives.

## Counterweight Pass

- Act Before Ship: F-002 and F-003 were fixed with masks, a real-lane test and a real Docker-socket test. The notes and docs wording on Risk Class, Windows quoting, the lock fallback, the workspace scan and the Codex test waits was corrected.
- Bundle Anyway: the CLI help and reference (F-005); the socket comment (F-007); the real-lane credential test (F-008); the forced-class-plus-prose test.
- Over-Worry: event-driven tests can hang if their event never arrives. The operator rule is that a test verdict never rides on wall time, so a broken event path shows as a hung run, not a pass.
- Valid but Defer:
  - Network egress and other host Unix sockets (F-001, F-003 remainder) are disclosed in docs and notes and tracked in #889.
  - `cmd.exe` metacharacter escaping is disclosed and tracked in #890.
  - Real-sandbox tests skip in CI (F-004); disclosed.
  - The `sandbox_prefix` complexity split is tracked in #888.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->

- F1 | bin: valid-but-defer | evidence: strong | ref: scripts/task_run/task_run_claude_sandbox.py | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/889 | note: F-001. The sandbox does not restrict network egress, and Unix sockets outside the masked set stay reachable. Both are stated in the docs and notes.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_claude_sandbox.py | action: fix | note: F-002 and F-008. `~/.docker`, `~/.pypirc` and Cargo credentials are masked (`51d2453f2`, `31a94834b`). A real lane cannot read them (`522aa1769`).
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_claude_sandbox.py | action: fix | note: F-003. Docker, containerd, Podman and CRI-O sockets are masked. The negative control connected before the fix (`51d2453f2`).
- F4 | bin: valid-but-defer | evidence: moderate | ref: docs/claude-task-executor.md | action: document | note: F-004. The real-sandbox tests skip without bubblewrap, and CI does not install it. They ran on the release machine.
- F5 | bin: bundle-anyway | evidence: strong | ref: charness | action: fix | note: F-005. The `--effort` and `--grant-writable` help names Claude, and the CLI reference is regenerated.
- F6 | bin: act-before-ship | evidence: strong | ref: docs/claude-task-executor.md | action: document | note: F-006 and F-007. The docs state the workspace scan's skipped trees and its symlink skip, and the socket comment matches the code (`522aa1769`, `5ffcdce91`).
- F7 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-11-05-v8.16.0-notes.md | action: fix | note: The part-2 claims were corrected in the notes: Risk Class forced-class wording, `cmd.exe` quoting, the untested lock fallback, and the Codex refresh test waits.
- F8 | bin: valid-but-defer | evidence: strong | ref: skills/shared/scripts/reviewer_process.py | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/890 | note: `cmd.exe` metacharacters are not escaped on Windows.
- F9 | bin: over-worry | evidence: moderate | ref: tests/quality_gates/test_semantic_review_worker_timeout.py | action: defer | note: Event-driven tests have no wall-clock fallback, by the operator rule. A broken event path hangs rather than passes.

## Operator Action Required

None before ship. A launcher that relied on a Codex lane inheriting `writable_roots` from the operator's Codex configuration must pass the directory with `--grant-writable`.

## Upgrade Path

Run `charness update`, then use `charness version` to read back the installed version.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: run_review.py file-backed worker, adapter backend codex_exec, read-only capability envelope, follow-up from the previous follow-up's result
- Host exposure state: host-defaulted
- Application state: the worker report records model_application_state unverified-by-provider, so the requested model and effort are not host-confirmed; the lifecycle records a read-only boundary
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: charness-artifacts/critique/workers/release-8160-claude-lane-followup4/worker-report.yaml
- Worker report identity: b31d0833d3b66d8cffac9651acaaa8cef228e6db65851761cecb6127600de03d
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: e7d03d5d25da34116cf4798cceb577d3a57e466816c3c61f2207d40f09ca1882
- Worker report input identity: 776b7a6bf137a1b96c7b25d36d9c560f4b4099f26dd25aa64a1f7a6200057f0d
- Worker report parent receipt identity: parent-31edd68f42ccb117bcc6edd116dedf58ffb693b59938f1f6
- Worker report findings identity: 70d3da668e3fd2f5a6c6cbe71896bcec426112052575726482a9d189a3cc0e45

## Fresh-Eye Satisfaction

worker-delivered. Part 1 passed at `release-8160-claude-lane-followup4` (recorded above). Part 2 passed at `release-8160-rest-followup4`: `charness-artifacts/critique/workers/release-8160-rest-followup4/worker-report.yaml`, approval_eligible true, packet identity `b634d5d19dd2498b2b88500dd0767810d45ccd402a6c1a812f2495e2b7bccc0b`, findings identity `f7c79f163e929c9b31f4b15021b9dd52faf8310498dd0dcb7955cd4ad0bba929`. Earlier rounds in each lane delivered `block` and are retained as evidence, not approval.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release-8160-claude-lane-followup4-packet.md
- Packet path: charness-artifacts/critique/release-8160-claude-lane-followup4-packet.json
- Packet SHA256: e7d03d5d25da34116cf4798cceb577d3a57e466816c3c61f2207d40f09ca1882
- Identity SHA256: 776b7a6bf137a1b96c7b25d36d9c560f4b4099f26dd25aa64a1f7a6200057f0d
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8160-claude-lane-followup4-packet.json --packet-sha256 e7d03d5d25da34116cf4798cceb577d3a57e466816c3c61f2207d40f09ca1882 --identity-sha256 776b7a6bf137a1b96c7b25d36d9c560f4b4099f26dd25aa64a1f7a6200057f0d`

## Boundary Ownership

- Producer: `scripts/task_run/task_run_claude_sandbox.py` produces the Claude lane's bubblewrap argv and masks.
- Consumer: the Claude lane process and the operator who enables `--executor claude`.
- Owning surface: task-run Claude executor
- Verdict: escalated-to-issue-spec
