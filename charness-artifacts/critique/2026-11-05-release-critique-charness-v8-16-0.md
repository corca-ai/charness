# Release Critique: Charness v8.16.0
Date: 2026-11-05

## Decision Under Review

Release `5e97a4cc3` as minor version 8.16.0 (code as reviewed at `5ffcdce91`, plus the test guard `dd9ac98a2` and the preflight fix `a33a50f42`). Since v8.15.0, main gains the previously unpushed task-run lane work: the opt-in Claude executor (`--executor claude`, `--claude-model`), Claude grants for `--grant-writable`, command durations in the events log, and lane environment repairs. The release also carries the progress-observation, app-server exit and Windows portability fixes that origin/main already held, unreleased. It also gains the debug planner fix that reads a `Risk Class` value apart from trailing prose, and the release repairs made during this pass: gate repairs, coverage tests, deterministic timing tests, and the critique repairs below. Commits after `5ffcdce91` change the release notes, `docs/claude-task-executor.md`, this record and its review packets, in response to the first three claims rounds, and two code changes: `dd9ac98a2` skips the cache-custody Claude probe where bubblewrap is absent, and `a33a50f42` deletes the Codex preflight's copied `auth.json` when the review ends. The changed notes, docs, code and tests were re-reviewed (Reviewed Input Identity below).

## Release Scope

- Version: `8.16.0`
- Tag: `v8.16.0`
- Bump rationale: minor. The release adds a new executor and CLI option (`--executor claude`, `--claude-model`) and widens `--grant-writable` to Claude lanes; the version policy names new operator-facing commands as minor. No option or field was removed. One change can break a launcher: Codex lanes no longer inherit `writable_roots` from the operator's own Codex configuration, so a launcher that relied on it must pass the directory with `--grant-writable`. It stays minor rather than major because the inherited grant was unintended ambient authority and closing it is a security fix. This departs from the version policy's line that lists forced migration steps under major; the notes state it under Security with the migration step.
- Consumer change: a launcher can opt into Claude lanes. A launcher that relied on a Codex lane writing under a `writable_roots` path from the operator's own Codex configuration must pass that directory with `--grant-writable`.

## Surface-Lock Inventory

- Generated artifacts: materialized plugin and marketplace manifests produced by the publish helper; `docs/cli-reference.md`.
- Consumer-visible behavior: the Claude executor and its sandbox; `--claude-model`; `--grant-writable` for Claude; `charness_duration_ms`; live `task status --commands`; the lane `TMPDIR` and Go cache placement; Codex lanes no longer inheriting `writable_roots`; the app-server exit message; debug planner Risk Class parsing.
- Documentation: `docs/claude-task-executor.md`, `docs/agent-task-runs.md`, `docs/cli-reference.md`, and the v8.16.0 notes.
- Adapter and integration surfaces: none changed.

## Verification Scope Decision

- Claim under test: a Claude lane cannot write outside its grants, read listed credentials, connect to a container daemon through the five masked socket paths, or read another lane's preflight Codex credential after the runner has finished that preflight. The docs and notes state the known remaining boundary gaps, tracked in #889. The debug planner fix keeps another subject's valid record with its subject. The notes claim no more than the code and tests show.
- Changed surfaces: `v8.15.0..5ffcdce91`, split across two reviewers. Part 1 covers the Claude executor, the task-run CLI and runtime, their tests, and the docs and notes. Part 2 covers the debug planner, lane environment and progress, Windows portability, test repairs, and the notes.
- Minimum sufficient proof: two fresh file-backed read-only reviews over the current files (`release-8160-claude-lane`, `release-8160-rest`). Then narrowed follow-ups on each repair until both passed (`-followup4`), a rebind of the claude-lane follow-ups over the notes and docs changed by the first claims round until it passed (`release-8160-claude-lane-followup8`), a second rebind over the notes, docs and test changed by the second claims round until it passed (`release-8160-claude-lane-followup14`), a review of the third claims round's preflight fix, notes and docs until it passed (`release-8160-claude-lane-followup16`), and a review of the fourth claims round's wording until it passed (`release-8160-claude-lane-followup18`). Hand mutations of the covered lines: 11 in the coverage tests (9 killed at first; after two tests were strengthened, the rerun killed both), the masks for the new real-lane credential test, and the preflight auth deletion (made a no-op, 6 tests failed). The full release lane runs in the publish helper and the pre-push hook.
- Deliberately omitted checks: the reviewers did not execute tests; the parent's focused runs stand in. No Windows host run.
- Verifier contract: `skills/shared/references/bounded-review-result.schema.json` plus packet and worker-report identity readback, unchanged in this release.
- Failure classification: subject-defect
- Negative control: command `pytest tests/charness_cli/test_task_run_claude_sandbox.py::test_listed_home_credentials_are_unreadable_in_a_real_lane` with `_SECRET_FILES` and `_SECRET_DIRECTORIES` emptied | expected refusal: the test fails | observed `3 failed`, and `3 passed` with the masks restored; a sandboxed connect to `/run/docker.sock` printed `connected` with the socket mask removed and is refused with it | receipt none; direct pytest and probe stdout in the release session
- Subject identity: sha256:9f73490c14c830ba0eb6acc24922a9e1a474ff4a1c98f2d2e9403f321c0951c7
- Verifier identity: sha256:67288fc99eab9333366dfd0e07094b5b9dfec0f91f95b4e4cdc8a508a41c0304
- Input identity: sha256:aad5868cc70696ea12fbaf9d6e14e977725947a69abafe71dfbd466f1223de00
- Failure identity: stable:no-failure
- Evidence identity: sha256:97089e64a757b2015f53d93f838e02dbf67ed75e367c5cd7328e6cfd07cd1016
- Retry disposition: retry-new-identity
- Retry key: sha256:335ffff0461477b315fea9975e63fccef5908c8b0a6f741d39d94d9d479834d2

## Failure Angles

- Gawande / operational and boundary safety (part 1):
  - unrestricted network egress (F-001);
  - unmasked `~/.docker`, `~/.pypirc` and Cargo credentials (F-002);
  - reachable container daemon sockets (F-003);
  - real-sandbox tests that skip without bubblewrap in CI (F-004);
  - CLI help that omitted Claude (F-005);
  - a workspace-scan claim broader than the scan (F-006);
  - a socket comment broader than the code (F-007);
  - no real-lane test for the new masks (F-008);
  - another Claude lane reading a lane's preflight Codex credential copy (third claims round).
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
  - While a preflight is running, or after its runner is killed or crashes mid-preflight or the deletion fails, another Claude lane can read its credential copy (F12); disclosed and tracked in #891.
  - Network egress and other host Unix sockets, including abstract-namespace sockets (F-001, F-003 remainder), are disclosed in docs and notes and tracked in #889.
  - `cmd.exe` metacharacter escaping is disclosed and tracked in #890.
  - Real-sandbox tests skip in CI (F-004); disclosed.
  - The `sandbox_prefix` complexity split is tracked in #888.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->

- F1 | bin: valid-but-defer | evidence: strong | ref: scripts/task_run/task_run_claude_sandbox.py | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/889 | note: F-001. The sandbox does not restrict network egress, and Unix sockets outside the masked set stay reachable, including abstract-namespace sockets. Both are stated in the docs and notes.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_claude_sandbox.py | action: fix | note: F-002 and F-008. `~/.docker`, `~/.pypirc` and Cargo credentials are masked (`51d2453f2`, `31a94834b`). A real lane cannot read them (`522aa1769`).
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_claude_sandbox.py | action: fix | note: F-003. The five default Docker, containerd, Podman and CRI-O socket paths are masked; a daemon socket at another path stays reachable (F1). The negative control connected before the fix (`51d2453f2`).
- F4 | bin: valid-but-defer | evidence: moderate | ref: docs/claude-task-executor.md | action: document | note: F-004. The real-sandbox tests skip without bubblewrap, and CI does not install it. The cache-custody Claude probe lacked that guard and failed without bubblewrap until `dd9ac98a2`. They ran on the release machine; no durable receipt records that run.
- F5 | bin: bundle-anyway | evidence: strong | ref: charness | action: fix | note: F-005. The `--effort` and `--grant-writable` help names Claude, and the CLI reference is regenerated.
- F6 | bin: act-before-ship | evidence: strong | ref: docs/claude-task-executor.md | action: document | note: F-006 and F-007. The docs state the workspace scan's skipped trees and its symlink skip, and the socket comment matches the code (`522aa1769`, `5ffcdce91`).
- F7 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-11-05-v8.16.0-notes.md | action: fix | note: The part-2 claims were corrected in the notes: Risk Class forced-class wording, `cmd.exe` quoting, the untested lock fallback, and the Codex refresh test waits.
- F8 | bin: valid-but-defer | evidence: strong | ref: skills/shared/scripts/reviewer_process.py | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/890 | note: `cmd.exe` metacharacters are not escaped on Windows.
- F9 | bin: over-worry | evidence: moderate | ref: tests/quality_gates/test_semantic_review_worker_timeout.py | action: defer | note: Event-driven tests have no wall-clock fallback, by the operator rule. A broken event path hangs rather than passes.
- F10 | bin: valid-but-defer | evidence: strong | ref: scripts/task_run/task_run_claude_sandbox.py | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/888 | note: `sandbox_prefix` exceeds the C901 limit; it carries `noqa: C901` and its split into ordered helpers with an argv-order test is tracked.
- F11 | bin: act-before-ship | evidence: strong | ref: scripts/task_run/task_run_brief_critique.py | action: fix | note: Third claims round: another Claude lane could read a lane's preflight copy of the Codex `auth.json` for as long as that runtime existed. The preflight now deletes the copy when the review ends, including after a failed review or an interrupted copy (`a33a50f42`), but not when the runner is killed or crashes, or the deletion fails (F12); a real-lane test in `/tmp` and `/var/tmp` layouts pins the deletion.
- F12 | bin: valid-but-defer | evidence: strong | ref: scripts/task_run/task_run_claude_review.py | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/891 | note: While a preflight is running, another Claude lane can read its credential copy, and a runner killed or crashed mid-preflight, or a failed deletion, leaves the copy in the runtime until the runtime is removed. The notes and docs disclose both; moving that credential out of lane reach is tracked.

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
- Worker report: charness-artifacts/critique/workers/release-8160-claude-lane-followup18/worker-report.yaml
- Worker report identity: dff3cb16b279c747ec891bade7df1b7e203965a396363cff400640510ede20fa
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: fe321e8aae48d1cc3def491daa39ea9703d57be50fcef4ea049d33548df7f1a0
- Worker report input identity: aad5868cc70696ea12fbaf9d6e14e977725947a69abafe71dfbd466f1223de00
- Worker report parent receipt identity: parent-33591d98a2a14d7bf90d0b909edfe7421f2ed36bc5c5dada
- Worker report findings identity: 97089e64a757b2015f53d93f838e02dbf67ed75e367c5cd7328e6cfd07cd1016

## Fresh-Eye Satisfaction

worker-delivered. Part 1 passed at `release-8160-claude-lane-followup4` and, after the first claims round changed the notes and docs, at the rebind `release-8160-claude-lane-followup8` (follow-ups 5 to 7 returned wording findings, which were fixed, and are retained). After the second claims round it passed at `release-8160-claude-lane-followup14` (follow-up 9 passed before further wording fixes; follow-ups 10 to 13 returned wording findings, which were fixed). After the third claims round it passed at `release-8160-claude-lane-followup16` (follow-up 15 found that a failed copy could survive, which was fixed). After the fourth claims round it passed at `release-8160-claude-lane-followup18` (recorded above; follow-up 17 found the deletion stated as certain, and the wording now names a failed deletion). Part 2 passed at `release-8160-rest-followup4`: `charness-artifacts/critique/workers/release-8160-rest-followup4/worker-report.yaml`, approval_eligible true, packet identity `b634d5d19dd2498b2b88500dd0767810d45ccd402a6c1a812f2495e2b7bccc0b`, findings identity `f7c79f163e929c9b31f4b15021b9dd52faf8310498dd0dcb7955cd4ad0bba929`. Every earlier round in each lane is retained as evidence, not approval.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release-8160-claude-lane-followup18-packet.md
- Packet path: charness-artifacts/critique/release-8160-claude-lane-followup18-packet.json
- Packet SHA256: fe321e8aae48d1cc3def491daa39ea9703d57be50fcef4ea049d33548df7f1a0
- Identity SHA256: aad5868cc70696ea12fbaf9d6e14e977725947a69abafe71dfbd466f1223de00
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8160-claude-lane-followup18-packet.json --packet-sha256 fe321e8aae48d1cc3def491daa39ea9703d57be50fcef4ea049d33548df7f1a0 --identity-sha256 aad5868cc70696ea12fbaf9d6e14e977725947a69abafe71dfbd466f1223de00`

## Boundary Ownership

- Producer: `scripts/task_run/task_run_claude_sandbox.py` produces the Claude lane's bubblewrap argv and masks.
- Consumer: the Claude lane process and the operator who enables `--executor claude`.
- Owning surface: task-run Claude executor
- Verdict: escalated-to-issue-spec
