# Critique — matcher for-loop read expansion (claim-fidelity instrument)

## Execution

Bounded fresh-eye subagent review: 3 angle reviewers + 1 separate counterweight,
plus 1 prior independent fresh-eye correctness review. All parent-delegated.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

charness-artifacts/critique/2026-06-29-125337-packet.md

## Target

references/code-critique.md (a code/diff change to the measurement instrument).

## Change

`scripts/agent-runtime/build-skill-execution-observation.mjs`: add
`expandForLoopReadCommands` to expand a literal-list
`for VAR in TOK...; do <read> "...$VAR..."; done` into the concrete read commands
each iteration ran, wired into the floor (`collectCommandLog`) and coverage
(`collectOpenedBasenames`). Corrects a false-negative where a live
`/charness:quality` run read all 9 planner primers (incl. `quality-lenses.md`)
via a for-loop yet the matcher scored it failed.

## Capability at Stake

Claim-fidelity measurement accuracy under the hard "never soften the matcher"
guardrail. A wrong change here either re-introduces a false-negative (erodes
trust in PASS verdicts across the whole sweep) or opens a fakeability surface
(a floor that passes when the doc was not read).

## Angles

1. Fix altitude & alternatives.
2. Guardrail integrity — does this soften the floor?
3. Maintenance cost & blast radius.

## Findings

- A1 (altitude): right altitude; alternatives (accept-as-limitation / teach
  skills to read attributably / coverage-only) correctly rejected; not a
  shell-interpreter slippery slope while the literal-only line holds. One SHOULD:
  document the literal-only boundary as a non-goal.
- A2 (guardrail): "never soften" RESPECTED — every floor-pass the change newly
  enables has a pre-change equivalent (plain literal `cat`/`grep`/Read naming the
  file); floor-blunt/coverage-sharp split preserved and test-locked. One NIT: the
  echo-exclusion comment over-claimed floor protection (it is a coverage-honesty
  measure). One minor SHOULD: expander trusts unparsed loop nesting (bounded —
  can only under-expand). One design-opinion: floor should ideally key off the
  sharp coverage signal (separate spec decision).
- A3 (maintenance): blast radius contained — `collectCommandLog`/
  `collectOpenedBasenames` each have one caller; `detectWaste`, trace, token math,
  A/B harness, and trace-digest are all events-driven, not command-log-driven.
  Perf negligible. One SHOULD: sync+stage the `plugins/` mirror (hard gate). One
  NIT: stale JS mutant-budget weight (breaks no gate).

## Structured Findings

- mirror-sync | bin: act-before-ship | evidence: strong | ref: scripts/check_staged_mirror_drift.py | action: fix | note: the .mjs is a checked-in plugin export; sync_root_plugin_manifests + stage plugins/ mirror in the same commit or the hard pre-commit gate blocks (#257).
- echo-comment-reword | bin: bundle-anyway | evidence: moderate | ref: scripts/agent-runtime/build-skill-execution-observation.mjs:142 | action: fix | note: comment over-claimed the read-only-body filter protects FLOOR integrity; reworded to coverage-honesty (done this slice).
- stale-mutant-weight | bin: valid-but-defer | evidence: moderate | ref: scripts/run_js_mutation.py:22 | action: defer | note: the 473 budget weight under-counts the added mutable statements but breaks no gate (test only asserts positive); fold into the next mutation-budget refresh.
- floor-keys-off-coverage | bin: valid-but-defer | evidence: contested | ref: scripts/agent-runtime/build-skill-execution-observation.mjs:608 | action: defer | note: re-keying the floor off the sharp coverage signal would remove the substring "named-anywhere" blur but is a deliberate direction change needing its own spec, not this false-negative patch.

## Deliberately Not Doing

- Non-goal header preamble (A1 SHOULD) — rejected as over-worry: the boundary is
  already self-documented at the enforcement point (`isLiteralLoopToken` + the
  existing "Only literal for-lists are expanded (no globs, seqs, or command
  substitution)" comment). A separate preamble is belt-and-suspenders prose for a
  maintainer who does not exist yet.
- Loop-nesting parser (A2 minor SHOULD) — rejected as over-worry: the walk can
  only UNDER-expand (breaks at the first `done`) or emit literal-token × read-
  operand combos the agent already typed; no new fakeability escape, no
  correctness regression. A real nesting parser is speculative robustness with no
  observed consumer.

## Next Move

Apply the two act/bundle items (echo-comment reword — done; plugins mirror sync —
at closeout), then run the agent-runtime JS tests + mutation dry-run, cautilus
diagnostics, doc/secret gates, and commit. Defer the two valid-but-defer items.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority (per .agents/critique-adapter.yaml)
- Host exposure state: host-defaulted
- Application state: requested high-leverage fields are not available in this host runtime; spawned the host-default general-purpose subagents (Claude) for all 3 angles + 1 counterweight + 1 prior fresh-eye correctness review.
