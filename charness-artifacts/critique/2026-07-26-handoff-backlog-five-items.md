# Five handoff items, and the measurement that broke the thing it measured
Date: 2026-07-26

## Decision Under Review

Closing the five items the previous handoff listed as next-session work:
`du_timeout` blocking policy, probing the BusyBox/BSD `du` claim, closing #453,
re-measuring the `local-linux-aarch64-4cpu` bars, and adding a
`--restamp-tool-version` path to the dup ratchet.

Two of the five could not be done as written, and saying which is part of the
result: **aarch64 hardware does not exist on this host** (x86_64, 36 cores), and
**#453's proof path via a scheduled run was refused** by the repo's own proof
tool for lack of `base_sha`. Both were reworked into something honestly provable
rather than reported as done.

## Failure Angles

One bounded read-only reviewer across all four code areas, briefed on the
specific way each could be hollow: is the temp-root carve-out cosmetic, are the
real-binary tests CI-safe, does the restamp dispatch silently swallow flags, and
can the raised budget bars weaken a gate that still binds here.

Parent-side worktree+index integrity was fingerprinted around the review
(`reviewer_boundary_fingerprint.py` snapshot/verify): `{"ok": true, "drift": []}`.

## What The Review Changed

The reviewer found a defect I had **created while measuring**, and it is the most
important finding of the slice.

**The 4-core measurement contaminated the profile it was not measuring.**
`machine_runtime_profile()` derived its CPU term from `os.cpu_count()`, which
ignores affinity. Under `taskset -c 0-3` it still reported 36, so all three
throttled runs filed their samples into `local-linux-x86_64-36cpu` — the
maintainer's own pre-push profile. Verified directly: `os.cpu_count()` returns 36
under `taskset` while `sched_getaffinity` returns 4, and the x86_64 window then
held `check-secrets` at max 76681ms with its median dragged to 11881ms against a
16500ms bar. The budget failure rule is median-based, so a few more samples would
have blocked a push on a machine where nothing regressed — **the exact class of
blocking false red this item existed to remove, relocated onto the box that
actually gets used.**

Three consequences, all acted on: the derivation now keys on
`len(os.sched_getaffinity(0))`; the 252 throttled samples were re-filed under
`local-linux-x86_64-4cpu` rather than deleted, since they are real measurements
that simply belonged elsewhere; and the aarch64 comment now cites that profile as
where its floors can be re-read.

Also from the review:

- **The `--restamp-tool-version` dispatch swallowed combined flags.**
  `--restamp-tool-version --accept-family X` dropped the accept and then refused
  with a message telling the operator to use `--accept-family` — a dead-end loop
  for anyone following the gate's own remediation. The three baseline-mutation
  modes are now mutually exclusive with a diagnostic naming which were combined.
- **Both real-binary tests skipped on the wrong predicate.** The unreadable-subdir
  test guarded on `which("du")` while actually requiring a `du` that accepts `-B`
  — so it would fail on precisely the BusyBox host its sibling test proves exists.
  It also assumed `chmod 000` denies access, which is false under uid 0. Now
  capability-probed and root-guarded.
- **The busybox shim needed `bash`.** On a busybox-without-bash image — the
  population the test targets — the `#!/usr/bin/env bash` wrapper would fail and
  surface as a misleading `du_missing`. Replaced with a symlink; BusyBox
  dispatches on `argv[0]`.
- **The architecture premise was asserted, not marked.** "x86_64 at 4 cores is
  faster than aarch64 at 4 cores" sat in the same register as the measured
  numbers, and it is not safe in general — Graviton and M-series cores beat many
  x86_64 cores single-threaded. Now explicitly split into MEASURED (core count)
  and ASSUMED (architecture), with the consequence of the assumption being wrong
  stated: loose bars, not false reds.
- **`root_source` labels intent, not ownership.** Any non-empty
  `PYTEST_DEBUG_TEMPROOT` reads as `configured`, including `/tmp`. Fail-closed, so
  not a reopened fail-open, but the message claimed "repo-owned" and nothing
  verified that. The claim is now scoped to what the code checks.

## Counterweight Pass

The reviewer's headline worry was **refuted by evidence I checked independently**:
it asked whether the unowned-root carve-out makes blocking unreachable in
practice. `run-quality.sh:60-61` sets and **exports** `PYTEST_DEBUG_TEMPROOT`
before any gate is queued, and both pre-push branches go through that script, so
`root_source` is `configured` on every path that matters and the blocking teeth
are intact. Confirmed by running the gate both ways. Not cosmetic.

Other findings graded down:

- The `classify_scan` ordering question resolves to "current order is right":
  capability gap and unowned root are both advisory, so the exit code is identical
  either way, and a `du`-is-broken diagnosis is true regardless of which root was
  scanned.
- The module-split double-load is real in mechanism (two module objects, since
  `load_path_module` bypasses `sys.modules`) but inert: neither loaded module has
  module-level mutable state. Recorded, not changed.
- Two floor values were transcribed low (`run-evals` 9400 vs 9512;
  `check-cli-skill-surface` 20300 vs 20399). Corrected, and both bars raised so
  they stay at ~1.4x the real max.

One dup-ratchet family this slice introduced was **genuine duplication, not
boilerplate**: I had written `usable_cpu_count`/`machine_runtime_profile`
identically in the recorder and the skill lib, which meant the affinity fix had to
be made twice in lockstep or writer and reader would disagree about which machine
a sample came from. Removed by delegation rather than classified as intentional —
unlike the three portability-preamble families, which were classified.

## Residuals

- **The aarch64 bars remain floors.** Only the core-count term is measured. A run
  on the real box is still owed, and that block still has no aggregate bar
  backstopping the eight looser per-gate bars.
- **BSD/macOS `illegal option` is still unprobed.** BusyBox and GNU are now
  measured; that third wording is inferred from documentation.
- **#453's scheduled-run proof path stays unavailable.** The tool refuses every
  existing scheduled run for lack of `base_sha`; the local explicit-range path was
  used instead, which is the tool's own second supported path.
- The `local-linux-x86_64-4cpu` profile now exists with real samples but has no
  budgets block, so it is observation-only.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/runtime_profile_lib.py:17 | action: fix | note: os.cpu_count() ignores affinity, so three taskset runs filed 4-core samples into the 36-core profile and dragged check-secrets' median to 11881 against a 16500 bar; the measurement manufactured the false-red class it was removing
- F2 | bin: act-before-ship | evidence: strong | ref: .charness/quality/runtime-signals.json:1 | action: fix | note: 252 contaminated samples re-filed under local-linux-x86_64-4cpu rather than deleted, since they are real measurements that belonged to a different profile
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/check_dup_ratchet.py:266 | action: fix | note: combining --restamp-tool-version with --accept-family dropped the accept and refused with a message naming --accept-family; the three modes are now mutually exclusive
- F4 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_seed_fixture_budget_gate.py:550 | action: fix | note: the unreadable-subdir test skipped on which("du") but required a du accepting -B, and assumed chmod 000 denies root; now capability-probed and root-guarded
- F5 | bin: act-before-ship | evidence: moderate | ref: tests/quality_gates/test_seed_fixture_budget_gate.py:536 | action: fix | note: the busybox shim needed bash, which the target minimal image may lack; a symlink removes the interpreter dependency
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/record_quality_runtime.py:37 | action: fix | note: the profile derivation existed twice, so the affinity fix had to be applied in lockstep or writer and reader would disagree; removed by delegation rather than classified as intentional duplication
- F7 | bin: act-before-ship | evidence: moderate | ref: .agents/quality-adapter.yaml:258 | action: fix | note: the architecture-ordering premise was asserted in the same register as the measured numbers; now split into MEASURED and ASSUMED with the consequence of being wrong stated
- F8 | bin: bundle-anyway | evidence: moderate | ref: skills/public/quality/scripts/pytest_temp_scan_lib.py:49 | action: fix | note: root_source labels whether a root was chosen, not whether the repo owns it; the operator message claimed the stronger property
- F9 | bin: over-worry | evidence: strong | ref: scripts/run-quality.sh:60 | action: defer | note: the unowned-root carve-out was suspected of making blocking unreachable; run-quality.sh exports PYTEST_DEBUG_TEMPROOT before any gate, so both pre-push paths still block
- F10 | bin: over-worry | evidence: moderate | ref: scripts/runtime_bootstrap.py:26 | action: defer | note: the split module loads a second copy of its dependencies, but both are pure-function modules with no module-level mutable state
- F11 | bin: valid-but-defer | evidence: moderate | ref: .agents/quality-adapter.yaml:244 | action: document | note: the aarch64 block has no aggregate bar backstopping the eight looser per-gate bars; pre-existing, but this change is what makes it matter
- F12 | bin: valid-but-defer | evidence: weak | ref: skills/public/quality/scripts/pytest_temp_scan_lib.py:41 | action: document | note: the BSD/macOS `illegal option` wording remains inferred; BusyBox and GNU are now measured

## Reviewer Tier Evidence

- Requested tier: typed `bounded-reviewer` subagent (read-only: Read/Grep/Glob), session-model inheritance per the Claude Code host branch of the repo subagent contract.
- Requested spawn fields: `subagent_type: bounded-reviewer`, a four-area scope prompt naming the specific hollowness risk in each, no model or effort override.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported Read/Grep/Glob only, with no Bash/Edit/Write/Agent.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

The reviewer had no Bash, so it could not diff against the pre-change commits or
run anything; it named that gap and flagged which of its claims depended on it.
Every finding acted on above was re-derived here against the running code first —
including the contamination, which was confirmed by running `os.cpu_count()` and
`sched_getaffinity` under `taskset` before any fix was written.

## Reviewed Input Identity

<!-- No prepared packet was consumed; the reviewer read the worktree at 0af8015d directly. -->

## Boundary Ownership

- Producer: `runtime_profile_lib.machine_runtime_profile`, which names the machine a runtime sample came from.
- Consumer: `check_runtime_budget`, which looks a budget up under that same name and blocks a push on it.
- Owning surface: the quality skill's profile library, now the single definition both the recorder and the budget gate consume.
- Verdict: moved-to-owner
