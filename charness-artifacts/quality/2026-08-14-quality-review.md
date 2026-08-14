# Quality Review
Date: 2026-08-14
Title: Monitored execution primitive and the release lane's silent quality gate

## Scope

Target boundary: the release-runner visibility owner named by the previous review
— one execution primitive with an explicit quiet-probe versus monitored-phase
caller choice, and the release lane's pre-push quality gate as its first caller.

Ambient: `charness init` is broken at HEAD by stale `--json` call sites (#619), a
dated quality record was overwritten in place (#620), and `release_only` is red.
Filed, not merged into this slice.

## Surface Contract Review

- semantic coverage: partial — lifecycle, timeout bound, isolated bodies, and the
  refusal contract observed; a live publish is not.
- surface: `scripts/subprocess_guard.py` child-process execution, and the lifecycle
  an operator reads from `run-quality.sh` under a release publish.
- owner: `subprocess_guard` owns spawn/timeout/lifecycle; callers own refusal
  policy and their own heartbeat env name.
- projections: stderr lifecycle lines, `PhaseOutcome`, the closeout record dict,
  the release `SystemExit` text, and `payload["release_runtime"]`.
- state scope: one child process and its process group; no repo state is written.
- transitions: start, heartbeat, terminal status, timeout-kill-drain, and the
  exception path that must still kill the child.
- proof boundary: focused tests plus measured process-tree runs; no live publish,
  installed host, or Windows.
- unexamined axes: Windows process groups, a D-state child that survives SIGKILL,
  live teeing of a streaming child's body.

## Current Gates

- Both shapes share one timeout contract: exit 124 with a marker naming the
  bound, never an exception.
- The monitored shape terminates the child's process GROUP (SIGTERM then SIGKILL)
  and bounds the post-kill drain, so a grandchild cannot outlast the budget; the
  release lane still refuses identically on a failing gate.

## Runtime Signals

- runtime source: `.charness/quality/runtime-signals.json` rendered by <!-- reproduction-source -->
  `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 240.0s latest / 102.4s median
  (budget 420s); `check-changed-line-mutation-coverage` 231.1s / 105.6s.
- coverage gate: `--read-only` 91 passed, 0 failed, 1 UNPROVEN (changed-line
  mutation coverage cannot see an uncommitted worktree).
- evaluator depth: deterministic-gates-only; two blockers settled by measurement.

## Healthy

- One owner, two shapes, all three real differences (what gets killed, granularity,
  timeout-stderr policy) stated where a caller reads them.
- `run`/`run_shell` refusal text, condition, and rendering stay byte-identical and
  the closeout record is unchanged for all four consumers.

## Weak

- `check_python_runtime_inheritance.py` matches only `subprocess.run` with a
  literal `["/bin/bash", "-lc", ...]` first argument; both monitored callers spawn
  through `Popen` inside the primitive, so the gate cannot see the seam it names.
- `publish_release_helpers.py` is at 357 code lines against a 360 hard limit. Its
  execution helpers are now a separate concept from its release-domain helpers;
  the next touch should split rather than shave.
- The `release_only` lane is red at HEAD (3 failed, 21 errors) and no standing gate
  runs it: `run_standing_pytest.py` passes `-m 'not release_only'` and the release
  adapter's `quality_command` omits `--release`.

## Missing

- Nothing compares a dated artifact's `Date:` header to the date in its filename,
  so a durable record can be overwritten in place with every gate green (#620) —
  the prose warning in `quality`'s own body was the only guard, and it failed.

## Deferred

- Teeing a single sequential child's body live. The prescribed transformation was
  "stream compact lifecycle while preserving isolated bodies", so the runner still
  surfaces only through the heartbeat — disclosed in the module header.

## Advisory

- structural review result: command: `rg -n "timed out after" -g '*.py'` found
  `subprocess_guard.run_process` already owning the quiet half, redirecting the
  slice from a parallel `monitored_run.py` to the existing owner.
- prose review result: artifact: `scripts/subprocess_guard.py` header now states
  both shape differences and the deliberate non-goal; no new blocking floor.
- command: `run_standing_pytest.py --mode full --include-release-only` shows the
  release-inclusive lane red; not a claim that all 21 errors are distinct.

## Delegated Review

- Delegated Review: executed — two bounded read-only rounds. Round 1 (angles:
  primitive, callers) returned three blockers, one confirmed by measurement (a
  1.0s budget returned after 25.0s because the kill reached only the direct
  child). Round 2 read the REPAIRS and found two more: the timeout branch still
  relabelled a child that had already exited, and the new group kill dropped the
  reaped-pid guard `Popen.send_signal` carries for bpo-38630 pid recycling. Both
  repaired; round-2 repairs are accepted-unreviewed at the two-round cap.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  covered by the caller review; the slice adds no standing gate or fixture.

## Commands Run

- Focused modules 27 pass (4 repeats, no flake); release publish/resilience/
  rollback/distinct-channel/backend 216 pass; closeout/docs/preflight 95 pass.
- `./scripts/run-quality.sh --read-only` — 91 passed, 0 failed, 1 UNPROVEN, after
  re-recording the residual-floor probe (artifacts 140 -> 141); `check_dup_ratchet`
  clean after classifying one coincidental `raise SystemExit` family intentional.
- Measured against `bash -c 'sleep 25 & sleep 25'` at a 1.0s budget: 25.0s before
  the group kill, 1.0s after, 6.2s with the kill reverted — which is why a timing
  assertion alone could not pin it. Boundary verified both rounds; mirror synced.

## Recommended Next Quality Moves

- active the `--json` collapse residue in `charness` (#619) — capability_needed=an
  operator can run `charness init`; next_center=`charness:488-496`;
  transformation=pick one format owner, fix caller and producer;
  proof_boundary=the release-inclusive pytest lane; enforcement_posture=existing-gate-reuse.
- active the `release_only` lane's invisibility — capability_needed=a red
  release-only test is seen before a publish, not during one;
  next_center=`run_standing_pytest.py`'s marker filter and the release adapter's
  `quality_command`; transformation=route the release gate through `--release`;
  proof_boundary=a broken release-only test failing preflight;
  enforcement_posture=candidate-floor pending #619.
- active dated-artifact date coherence (#620) — capability_needed=a durable record
  cannot be silently replaced; next_center=`artifact_validator.py`;
  transformation=fail when a `<date>-<slug>.md` header date disagrees with its
  filename; proof_boundary=the checked-in corpus; enforcement_posture=candidate-floor.
- passive remaining release-lane `run_shell` consumers until one is measured slow
  enough to earn a lifecycle — next_center=`run_post_publish_install_refresh`,
  the distinct-channel probes; transformation=measure first;
  proof_boundary=runtime signals; enforcement_posture=no-gate, since converting
  blind repeats the anti-need this slice avoided.

## History

- [Current-contract cleanup and runner visibility](./2026-08-14-current-contract-cleanup.md)
- [Portable proof-path learning review](./history/2026-07-19-portable-proof-path-learning-review.md)
