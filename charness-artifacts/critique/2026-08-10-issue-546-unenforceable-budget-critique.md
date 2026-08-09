# Resolution critique — #546 (an unenforceable bar that reads as protection)
Date: 2026-08-10

## Decision Under Review

Whether to make `check_runtime_budget` FAIL on a budgeted label that no profile has
ever sampled — and close #546 on it.

**Outcome: the repair was BUILT, reviewed, MEASURED defective, and REVERTED.** #546
stays open, with one of its three candidate options now refuted by evidence rather
than by argument.

## Failure Angles

- **The obvious fix is the one the issue warns against.** Refusing on plain absence
  fires on every fresh machine. The issue says so and says it "should probably be
  avoided".
- **A discriminator that cannot discriminate.** Separating "fresh" from "dead"
  needs evidence the machine has run; getting that wrong turns a correctness fix
  into a gate that blocks every new host — strictly worse than the WARN it replaced.
- **Conditional gates.** A budget can legitimately exist for a label that only some
  run modes queue.
- **Fitting the rule to this repo's signals file**, which is the defect class this
  whole goal exists to remove.

## Counterweight Pass

- The concern that this blocks fresh machines was NOT over-worry. It was the
  outcome, twice, in two different ways — once caught by a probe, once by review.
- The concern that a budget nothing queues is zero protection remains TRUE. #546 is
  a real defect. What is refuted is one way of fixing it, not the issue.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/runtime_budget_lib.py | action: fix | note: FIRST DEFECT, caught by a synthetic probe of the agent's own work. Guarding only on "the signals file knows some labels" hard-failed every budget against a file holding one label. A second guard was added — the selected profile must have sampled something.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:949 | action: fix | note: SECOND DEFECT, caught by bounded review and then CONFIRMED BY MEASUREMENT. `check-runtime-budget` is queued second-to-last, and samples are written during the run, so by the time the gate executes `commands` holds ~80 labels and the "profile has demonstrably run" guard is TRUE while the history is still partial. Probe against this repo's real 36cpu budget block with every label sampled EXCEPT `run-quality-read-only` (which `print_final_summary` records AFTER this gate): exit 1, "unenforceable runtime budget: run-quality-read-only". A fresh machine's first run would have hard-failed. The passing fresh-machine test passed only because its fixture writes no samples concurrently.
- F3 | bin: act-before-ship | evidence: strong | ref: .agents/quality-adapter.yaml | action: fix | note: six labels in this repo's own adapter are legitimately conditional — release-path (`run-quality-read-only-release`, `run-quality-full-release`, `pytest-release`), opt-in (`dead-code-advisory`), and mode-gated (`check-coverage`, `run-quality-full`). On a second maintainer box reporting the same profile id and running only pre-push read-only, all are permanently "never sampled". The remedy message would tell that operator to delete correct budgets, and `CHARNESS_QUALITY_LABELS` is an allowlist, so the only escape is `--no-verify`. This repo's own prose for a sibling gate names that shape: "a gate whose remediation names a flag the operator cannot pass is a gate that lies at the moment it blocks."
- F4 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/scripts/runtime_budget_lib.py | action: fix | note: the timing-log fallback reassigns `commands` from `timing_log`, while `known_labels` reads only `signals` — so the two sides of the test describe different sources, and a label whose evidence lives only in the timing log reads as dead.
- F5 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/scripts/runtime_budget_lib.py | action: fix | note: `(profile or {}).get(...)` guards falsy but not wrong-typed values, so a truncated signals file (rewritten in full per phase flush, so a real state) raises AttributeError and takes the gate down — against a docstring promising an empty set on an unreadable file.
- F6 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_runtime_budget_gate.py | action: fix | note: two of the four new tests exited through the FIRST clause of the guard (`commands` empty), never reaching the comparison they were named for, and no test covered the headline case — this profile has run AND the label is sampled on another profile. The story the design rests on was unpinned.

## Disposition

REVERTED. The code, its tests, and the mirror are restored; only this record and
the #546 comment remain. Reverting rather than iterating, because F2 and F3 are not
bugs in the implementation — they say the CHOSEN DISCRIMINATOR is wrong. Sample
history cannot distinguish a dead label from an unexercised run mode, and no amount
of guarding fixes that, because the information is not in the signals file.

What #546 now has that it did not: its cheapest option is refuted, with the reason
measured. The reviewer named the direction that could work — classify against the
runner's DECLARED gate inventory rather than the recorded window — plus an
adapter-declared exemption for conditional labels and an operator escape matching
the `CHARNESS_SEED_FIXTURE_ADVISORY` precedent. That is a larger build than this
slice, and it is now specified rather than guessed.

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye reviewer (`bounded-reviewer`), unnamed and synchronous.
- Requested spawn fields: subagent_type=bounded-reviewer, run_in_background=false, no host addressing name.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer returned findings in-band. The boundary verify for window `w-20260809T230237Z-2134563` reports `boundary-drift`, and the drift is the PARENT's — the five files of the reverted repair plus their mirrors, written after the reviewer returned. The tool's own attribution note says undeclared drift is a boundary signal only for a window in which the parent made no writes, and this parent made exactly those writes. Recorded as drift rather than claimed clean, because a verify that returns drift is not a verify that returned clean.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. The reviewer returned HOLD with three blockers; the parent then
confirmed the decisive one (F2) by executing the probe the reviewer named but could
not run, and reverted. The review did not improve the repair — it stopped it.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed: the reviewed input was the uncommitted working tree. -->

## Boundary Ownership

- Producer: `check_runtime_budget` / `runtime_budget_lib`, which render the budget verdict.
- Consumer: the pre-push quality run, whose pass/fail an operator reads as protection.
- Owning surface: `skills/public/quality/**`.
- Verdict: single-surface
