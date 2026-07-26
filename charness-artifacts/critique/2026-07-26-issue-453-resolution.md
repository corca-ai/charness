# Issue #453 resolution critique
Date: 2026-07-26

## Decision Under Review

Whether GitHub issue #453 ("Mutation test regression on main") is resolved, and
what has to be true before it closes. The issue was auto-filed by a scheduled
mutation run on `79d23b86b`: the mutation SCORE passed (94.2% vs an 80%
threshold), and the blocking signal was changed-line coverage on two files —
`scripts/quality_policy_defaults.py` (lines 209, 220, 253) and
`skills/public/quality/scripts/runtime_budget_lib.py` (line 305).

## Failure Angles

One bounded read-only reviewer on the causal and recurrence question rather than
on re-verifying the numbers: what class of defect this was, whether the fix has
teeth or merely restores coverage, what stops recurrence, whether siblings exist,
and whether anything in the issue body is left unaddressed.

Parent-side integrity was fingerprinted around the review. The post-review verify
reported drift on `.github/workflows/quality-core.yml` — that file is the one this
critique's own prevention fix edits, changed by the parent AFTER the reviewer
returned. Attribution is unambiguous (the reviewer had Read/Grep/Glob only), but
the snapshot should have been retaken before the fix; recorded rather than
glossed.

## What The Review Changed

**The proof I had was vacuous, and the reviewer caught the shape before I cited
it.** I had run the changed-line gate over `79d23b86b..HEAD` and observed that
neither named file appeared in `blocking_targets`. The reviewer demanded the
payload be checked for a skip-shaped false green. Checking it showed something
worse than a skip: **neither file appears in `changed_pool_files` at all.** The
fix for #453 added tests, not source edits, so over that range the two source
files are unchanged and simply out of scope — the gate said nothing about them,
and "not blocking" was an absence of analysis, not a verdict.

Replaced with direct evidence on the exact lines the issue named, measured on the
current tree:

```
quality_policy_defaults.py:209 -> COVERED
quality_policy_defaults.py:220 -> COVERED
quality_policy_defaults.py:253 -> COVERED
runtime_budget_lib.py:305      -> COVERED
```

**The prevention gap is the real finding, and it is this repo's seventh
instance.** The reviewer traced why a direct push to `main` had no blocking
changed-line signal anywhere:

- `.githooks/pre-push` does not call the gate; it runs `run-quality.sh
  --read-only`, which invokes it with `--skip-if-no-coverage`,
  `--require-fresh-coverage`, and `--allow-dirty`. Each independently exits 0.
  Without the author first paying ~10 minutes for the coverage producer, the gate
  emits a stderr warning and passes.
- The CI mirror that has real teeth was gated `if: github.event_name ==
  'pull_request'`, and #453's change reached `main` without a PR.
- So the scheduled cron was the only place the class surfaced, up to 3 hours after
  merge — which is how it auto-filed #219 -> #251 -> #260 -> #320 -> #321 -> #335
  -> #453.

The gate's own `coverage_not_verified_warning` docstring already describes this
recurrence in words. Fixed here: the CI mirror now also runs on pushes to `main`,
using `github.event.before` as the base, with an explicit skip when that base is
unreachable. The workflow's own header claimed it existed to "catch a bypass (a
direct push without the local hooks)" — while the job was PR-only, it did not.

## Counterweight Pass

- **The survived mutants are correctly out of scope.** The issue lists 7 survivors
  in `probe_host_logs.py`, but its own body separates the arms: the score arm
  PASSED at 94.2%, and survivors feed only the score. Same for the advisory
  selection-budget entry, which the issue marks non-blocking. Closing on the
  changed-line arm matches what the issue says blocked.
- **The fix has teeth, not just coverage.** The reviewer checked each covering
  test against the mutation it would kill: the tests assert message content and
  post-rejection state (that the rejected value never merged), not mere execution.
  Two go further — one pins that `enabled` does NOT fall through to the string
  check, and one pins that an honest budget emits no SLACK line.
- **One assertion is tautological and was left in place deliberately.**
  `test_runtime_budget_gate.py:627-635` compares `_render_slack(...)` against
  output produced by the same function, so it kills nothing on its own. Its
  comment is honest that it exists as a coverage-attribution witness. Recorded as
  a residual rather than removed, but noted: if the subprocess assertions above it
  ever break, only the tautology remains and the line stays green with zero
  assertion strength.
- **Root cause is a class, not an oversight.** Both proof targets are
  rejection/presentation lines created by collapsing N duplicated validation
  branches into one parameterized helper. The consolidation moves the message out
  from under the tests that covered it, and the natural test for a bad config
  (`assert not payload["valid"]`) exercises the caller while leaving the message
  line unasserted.

## Residuals

- **Siblings are named, not fixed.** The reviewer found ~12 same-class siblings in
  `quality_policy_defaults.py` (`:442`, `:447`, `:483`, `:488`, `:438`, `:479`,
  `:503`, `:319`, `:307`, `:328`, `:335`) and 2 in `runtime_budget_lib.py`
  (`_render_hotspot` at `:298-301`, the `format_human` WARN suffix at `:344-352`).
  All are currently UNCHANGED lines, so no changed-line gate blocks on them today;
  they are the recurrence surface for the next edit. Decision: not fixed in this
  slice, carried to the handoff, because fixing them is a test-writing sweep with
  its own scope rather than part of proving #453.
- `:442`/`:447` and `:483`/`:488` are two near-identical copies of one block — the
  exact "N duplicated branches" shape that produced #453 when someone consolidates
  them. That is the highest-value sibling to fix first.
- **The scheduled-run proof path remains unavailable.** `check_mutation_run_proof.py`
  refuses every existing scheduled run for lack of `base_sha`.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_changed_line_mutation_coverage.py:452 | action: fix | note: the changed-line run cited as proof did not analyze either named file — both are absent from changed_pool_files because the fix added tests, not source edits; replaced with direct line-coverage measurement
- F2 | bin: act-before-ship | evidence: strong | ref: .github/workflows/quality-core.yml:93 | action: fix | note: the blocking CI mirror was PR-only while the local pre-push gate defuses itself on the direct-push path, so a direct push to main had no blocking changed-line signal; the mirror now runs on push using github.event.before
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/quality_policy_defaults.py:209 | action: document | note: root cause is a class — rejection/renderer lines created by consolidating duplicated validation branches into a parameterized helper, which moves the message out from under the tests that covered it
- F4 | bin: valid-but-defer | evidence: strong | ref: scripts/quality_policy_defaults.py:442 | action: defer | note: ~14 same-class siblings named across both files; all unchanged lines today, so nothing blocks on them, but they are the recurrence surface for the next edit
- F5 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_runtime_budget_gate.py:627 | action: document | note: a self-comparing assertion kills no mutant; kept deliberately as a coverage-attribution witness, but it is the only thing left if the subprocess assertions above it break
- F6 | bin: over-worry | evidence: strong | ref: skills/public/retro/scripts/probe_host_logs.py:60 | action: defer | note: the 7 survived mutants feed the score arm, which the issue records as PASSED at 94.2%; excluding them matches the issue's own separation of arms

## Reviewer Tier Evidence

- Requested tier: typed `bounded-reviewer` subagent (read-only: Read/Grep/Glob), session-model inheritance per the Claude Code host branch of the repo subagent contract.
- Requested spawn fields: `subagent_type: bounded-reviewer`, causal/recurrence scope prompt for issue #453, no model or effort override.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported Read/Grep/Glob only, with no Bash/Edit/Write/Agent.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

The reviewer had no Bash, so it could not run the gate, the tests, or `git show`
against the failing sha; it named that limit and marked which claims depended on
it. Its central procedural finding — check the payload for a false-green shape
before citing it — was acted on and overturned my own evidence.

## Reviewed Input Identity

<!-- No prepared packet was consumed; the reviewer read the worktree at 361f8b95 plus the issue body quoted into its prompt. -->

## Boundary Ownership

- Producer: the changed-line mutation gate, which decides whether uncovered changed lines block.
- Consumer: whoever merges to `main` — locally via pre-push, remotely via the CI mirror.
- Owning surface: the CI mirror, which is the only one of the two that cannot be defused by not having paid for coverage first.
- Verdict: moved-to-owner
