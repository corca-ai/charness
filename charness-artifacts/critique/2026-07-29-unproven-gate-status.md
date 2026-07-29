# A gate that judged nothing must not print PASS
Date: 2026-07-29

## Decision Under Review

Adding a third gate status to `run-quality.sh`. A gate exiting 3 renders
`UNPROVEN`, is counted in neither the passed nor the failed column, and does not
fail the run.

The premise is this session's own retro, which named one waste as load-bearing:
the mechanism that catches dead guards already exists and is blocking, and I ran
it in the order that makes it lie. The changed-line gate printed
`PASS check-changed-line-mutation-coverage` beside its own warning that the run
proved nothing; the warning was read past and two dead guards nearly shipped. The
Engelbart counterfactual was not "remember to commit first" — it was that the
T-loop has a false-green window the gate already detects and only labels. This
closes it in the tooling rather than in memory.

North-star fit: P5's "there is no terminal green", applied to the surface that
renders every other gate's verdict.

## Failure Angles

- **The byte is not ours.** Exit 3 has meanings across the queue. Reinterpreting
  it globally turns some other tool's real failure into a non-blocking word.
- **A green removed in one place survives in another.** The console line is not
  the only verdict surface; the durable telemetry record is quoted later.
- **A new status nothing can reach.** A third column that no queued gate produces
  is dead weight that reads as coverage.
- **A new status that blocks.** The changed-line lane is deliberately toothless
  mid-work; a change that makes it stop ordinary runs gets the lane disabled,
  which is the failure history being repaired.
- **The word without the reason.** `UNPROVEN <label>` with no output is the same
  unexplained verdict in a new spelling.

## Counterweight Pass

- Not over-worry: the escape is measured. It happened to me, in this repo, this
  session, and cost a full gate cycle plus two dead guards that reached commit.
- Real constraint accepted: an EMPTY changed set still exits 0. Nothing was in
  scope, which is honestly nothing to prove, and marking every such run UNPROVEN
  would train the reader past the word — the exact way the previous warning died.
- Scope refused: `check_mutation_run_proof` still marks a changed-line claim
  `provable` on `base_sha` alone, so a CI range with no eligible pool file remains
  a citable green. Round 1 argued this is where the escape actually escaped. It is
  a different surface with a different owner and is recorded as open, not closed.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh | action: fix | note: measured `pytest` exit 3 = INTERNAL_ERROR and `shellcheck` exit 3 = bad invocation, so the status is opt-in per label; a global reading would have stopped gating on a suite that never ran
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_focused_changed_line_coverage.py | action: fix | note: run-quality runs the WRAPPER, which sent any code outside (0,1) to exit 2 = FAIL, so every ordinary mid-work run would have hard-failed and `--refuse-unestablished` would have been dead code
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/record_quality_runtime.py | action: fix | note: the real recorder rejected the new status and dropped the sample; the test-support STUB accepted anything, which is why no test saw it
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh | action: fix | note: the aggregate telemetry recorded `pass` for an all-UNPROVEN run, so the green survived in the durable artifact after being removed from the console
- F5 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/scripts/standing_gate_discovery_lib.py | action: fix | note: `VAR=1 command` matched the assignment skip, so adding an env prefix to the hook made `scripts/run-quality.sh` undiscoverable as a surface entirely
- F6 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_mutation_run_proof.py | action: document | note: a changed-line claim is `provable` on base_sha alone, so an empty-range CI run stays a citable green; different surface, recorded as open
- F7 | bin: valid-but-defer | evidence: moderate | ref: scripts/changed_line_run_trust.py | action: document | note: `fg_warning` under-approximates untrustworthy runs (non-HEAD `--head-sha`, a git failure read as "nothing found", dirty non-pool files); pre-existing, but exit-code semantics are load-bearing now

## Executed Proof

- The motivating run, after the change: `UNPROVEN check-changed-line-mutation-coverage`
  and `81 passed, 0 failed, 1 UNPROVEN (ran, established nothing)` — the same run
  that printed PASS before.
- Exit-3 collisions MEASURED on this machine, not assumed: `pytest` INTERNAL_ERROR
  is 3, `shellcheck` with a bad flag is 3. A third candidate the reviewer raised —
  `lychee` on a broken link — measured 2, and is recorded as refuted.
- `bash scripts/run-quality.sh`: 82 passed, 0 failed after commit, with the
  changed-line verdict real rather than a pre-commit false green.
- The aggregate-status test was proven falsifiable by disabling the branch it
  covers and observing the failure, then restoring it.
- `./scripts/run-quality.sh --read-only`: the mode the pre-push hook uses.
- NOT established: no live push has exercised `--refuse-unestablished` through the
  hook with `CHARNESS_PRE_PUSH=1` set. The refusal path is unit-pinned only.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: agent type `bounded-reviewer` (read-only Read/Grep/Glob),
  no host addressing name, session model inherited per the Claude Code host branch
  of the per-host subagent contract.
- Host exposure state: host-defaulted
- Application state: host resolved the typed read-only agent and inherited the
  session model; no per-subagent model/effort control was requested on this host.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — two bounded rounds. Both changed my design rather than
polishing it.

Round 1 ran two reviewers. One refuted the design outright: exit 3 is not this
runner's byte, and a global reinterpretation would have laundered a crashed test
suite and a mis-invoked shellcheck into non-blocking words. I measured both claims
before acting, which also refuted a third (lychee). The other traced that the
runner never runs the consumer — it runs the wrapper, which converted 3 into 2 and
therefore FAIL, so the change was wired backwards on the one gate that motivated
it, and the tests that pinned that behavior stubbed a consumer return code the
consumer could no longer produce.

Round 2 read the repaired surface and found it carrying the class it repaired, for
the third time this session: the status rewrite on exit 3 was unconditional, so a
payload that could not be READ — whose exit code therefore stands for nothing —
was reported as a bounded, non-blocking "ran, established nothing". It also found
the push-time refusal withholding the payload naming which files went unproven,
`--read-only` overloaded as "a push is imminent" although it is the published
mid-work command, an honest empty-scope result made refusable, and the aggregate
status change asserted only in a comment with no falsifiable test.

Per the two-round cap, the round-2 repairs are accepted-unreviewed. So is F5,
which no reviewer saw: adding the hook's env prefix made `run-quality.sh` vanish
from the discovery surface list, and the standing-gate-verbosity gate caught it.

Reviewer boundary: snapshotted before each spawn and verified at return BEFORE any
repair — round 1 exit 0 `verdict: clean` drift `[]`, round 2 exit 0
`verdict: clean` drift `[]`. This is the sequencing the earlier slice in this
session got wrong and this session's retro named; it was applied here.

Fresh-eye pass: `scripts/run-quality.sh` — round 1 swept every queued command and
every external tool for an existing exit-3 meaning; round 2 verified the allowlist
match cannot alias, fails closed on a typo, and treats glob metacharacters
literally.

Fresh-eye pass: `scripts/prepush_focused_changed_line_coverage.py` — round 1 found
the wrapper/consumer seam inverted; round 2 traced every return path and confirmed
a crashed producer still exits 2 rather than becoming UNPROVEN.

## Public Skill Validation Decision

`skills/public/quality/scripts/standing_gate_discovery_lib.py` changed, but only to
stop dropping env-prefixed command lines — a detection fix with no contract,
routing, or adapter-schema change, and it makes the library see MORE of what it
already claimed to read. The `quality` skill's prompt surface and adapter contract
are unchanged. Recorded as an explicit decision rather than an evaluator scenario.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-07-29-unproven-gate-packet.json
- Packet path: charness-artifacts/critique/2026-07-29-unproven-gate-packet.json
- Packet SHA256: e84b6246cde55e87f255d7f9109e5d19d79f7c27fa26d814ff98e2eec98c09df
- Identity SHA256: dc168a3e3018e16409a747fb28f85044127c73d7f30c478a7da6ea28ee05a0f1

Rendered after all repairs landed, so it is current against the tree. It is not
the input either round read: both rounds were spawned with inline prompts naming
their scope rather than with a packet file, so no packet SHA exists for either.
Recorded rather than papered over.

## Boundary Ownership

- Producer: the gates themselves, which decide whether they established a scope,
  and `_verdict_from_consumer`, which reads a consumer payload into a status.
- Consumer: `run-quality.sh`, which turns a status into an operator-visible verdict
  and a durable telemetry record, and `record_quality_runtime`, which stores it.
- Owning surface: `run-quality.sh` owns the vocabulary — it is the only place that
  knows which labels are entitled to report unestablished, and that entitlement
  cannot live in the gates, because the whole point is that a gate must not be able
  to claim a non-blocking status just by picking an exit code.
- Verdict: owned-correctly
