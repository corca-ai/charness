# Issue 466 mutation lane baseline repair

Date: 2026-07-30

## Decision Under Review

Close #466 (the scheduled mutation lane aborted on two coverage-baseline pytest
failures) by removing the suite's two dependencies on ambient CI-runner state,
and repair the product false green that the first of those failures exposed in
the portable changed-line coverage gate.

## Failure Angles

- **Fixing the test and calling the product fine.** Both baseline failures were
  test-isolation defects, and stopping there was the obvious scope. But the
  reason the range-leak test failed was that the gate silently adopted an
  ambient `MUTATION_HEAD_SHA` — reproduced as a real false green: the same
  `--base-sha B` run over the same tree went from `FAIL: 1 changed file(s) have
  uncovered changed lines` to `OK: no eligible changed files in this range`,
  exit 0. A test-only fix leaves a verdict surface reporting a pass over a range
  nobody asked for.
- **The repair carrying the class it fixes.** The first repair added a second
  head resolver (`^{commit}`-peeled) alongside the existing bare `rev-parse` in
  `_false_green_warning`. On an annotated tag the two disagreed: the run was
  cleared to a verdict while the one guard against an uncommitted-changes false
  green switched itself off. A repair for "renders a verdict over inputs that
  cannot support one" that itself renders a verdict over inputs that cannot
  support one.
- **Refusing an empty scope.** The first placement refused before the changed
  set was known, so a range that touched no eligible file became refusable — the
  incoherent-blocker shape `prepush_focused_changed_line_coverage` already names
  by name, on the gate whose credibility is the point.
- **Putting a could-not-judge in the coverage-failure bucket.** Exit 1 for the
  mismatch made it indistinguishable, by exit code, from real uncovered lines.
  CI reads exit codes, not stdout.
- **Consumer breakage with no notice.** `actions/checkout` on a `pull_request`
  checks out the merge ref, so a consumer pinning `--head-sha` to the PR head
  sha now trips the refusal on every run. Legitimate-looking usage the two
  reference docs invited without qualification.
- **A nested pytest reaping the outer run's processes.** The regression guards
  spawn a nested pytest; `pytest_sessionfinish` gated its agent-browser orphan
  cleanup only on `PYTEST_XDIST_WORKER`, so under the serial `cosmic-ray.toml`
  test-command a nested session would SIGKILL trees it did not start — the suite
  erasing the evidence its own hygiene gate exists to observe.

## Counterweight Pass

- **Real blockers, fixed before shipping:** the divergent resolvers, the
  placement, the exit-code collapse, the nested-session reaper, and the
  tautological first draft of the range regression test. Each was verified
  against the repo's own recorded prior art or reproduced at the command line
  before being accepted.
- **Over-worry:** the `head_sha == "HEAD"` early return waving through an
  unborn/unresolvable HEAD. Traced: it falls to `changed_eligible`, which raises
  and lands in `unestablished`. No verdict escapes.
- **Deliberately not folded:** `MUTATION_SAMPLE_*` was checked and left
  unscrubbed — no reader can change a verdict today. The docstring now records
  that this rests on a call-site convention rather than a property of the names,
  so the next editor sees the trap.
- **Accepted cost:** the consumer break is real and is the point. A refusal is
  the honest answer for a head that is not this worktree; the previous behavior
  was a silent wrong verdict. It is named in the adapter contract, the
  mutation-testing reference, and the dogfood registry rather than left to be
  discovered.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/changed_line_coverage_gate_lib.py | action: fix | note: two head resolvers disagreed on an annotated tag, silently disabling the false-green guard; single-sourced through resolve_head_scope
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_changed_line_mutation_coverage.py | action: fix | note: refusing before the changed set was known made an empty scope refusable, the incoherent blocker the sibling already corrected; moved below changed_eligible with a disclosure on the empty path
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/check_changed_line_coverage.py | action: fix | note: could-not-judge exited 1 alongside real coverage failures; split to exit 3 with ok true
- F4 | bin: act-before-ship | evidence: strong | ref: tests/conftest.py | action: fix | note: a nested pytest would run the agent-browser orphan reaper against the real repo mid-outer-run under the serial test-command; gated on CHARNESS_NESTED_PYTEST
- F5 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_mutation_baseline_abort.py | action: fix | note: the first regression test asserted its own postcondition and passed with the fixture deleted; replaced with a nested reproduction, negative-controlled
- F6 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/references/adapter-contract.md | action: document | note: exit 3 is a consumer-visible contract change, including the actions/checkout PR shape; documented in both references and the dogfood registry
- F7 | bin: over-worry | evidence: moderate | ref: skills/public/quality/scripts/changed_line_coverage_gate_lib.py | action: defer | note: the head_sha == HEAD early return does not wave through an unresolvable HEAD; changed_eligible raises into unestablished
- F8 | bin: valid-but-defer | evidence: moderate | ref: tests/conftest.py | action: document | note: MUTATION_SAMPLE_* stays unscrubbed on a call-site convention, not a property of the names; recorded in the docstring for the next editor

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (typed read-only Claude Code subagent).
- Requested spawn fields: subagent_type bounded-reviewer, session-model inheritance, no host addressing name.
- Host exposure state: applied
- Application state: host-confirmed: each reviewer reported seeing only Read/Grep/Glob and no Bash/Edit/Write/Agent tool.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

Two rounds. Round 1 (two reviewers, one per repair) produced the coverage-loss
and tautology findings that were applied. Round 2 (two reviewers, reading the
REPAIRED surfaces, required because this slice changes verdict logic on a proof
surface) produced F1–F4 — every one of them a blocker the first round could not
have seen, because the surfaces they name did not exist until round 1's fixes
were applied.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with `- Packet consumed: <packet-path>` plus three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. That `Packet consumed:` line is what turns the binding floor on. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: `skills/public/quality/scripts/changed_line_coverage_gate_lib.py` resolves the analyzed head and renders the changed-line verdict.
- Consumer: `check_changed_line_coverage.py` (exit code and operator line), plus any repo vendoring the quality skill.
- Owning surface: the portable quality gate package, with its contract in the quality references.
- Verdict: owned-correctly

## Non-Claims

- The reviewer boundary fingerprint `verify` reports worktree drift. Every
  drifted path is one the parent edited after the snapshot was taken, both
  reviewers were read-only by their own report, and no path was declared to the
  tool — so this is a parent bookkeeping miss, not a clean verify and not
  evidence of reviewer mutation.
- The nested-session orphan-reaper finding (F4) is read-derived, not reproduced:
  the probe that would have observed it required mutating a repo script and was
  declined. The fix is applied regardless because it is cheap and cannot regress
  the guarded behavior.
- No claim that the scheduled mutation workflow has been observed green. The
  proof is that the workflow's own baseline command
  (`python3 -m pytest -q -m 'not release_only' tests`) passes locally, including
  under the exported `MUTATION_BASE_SHA`/`MUTATION_HEAD_SHA` that broke it.
