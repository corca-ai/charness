# Skill Contract Whitespace Coupling Debug
Date: 2026-07-19

## Problem

The final standing suite failed `test_eval_cautilus_scenarios_writes_summary`
after a quality-skill sentence was wrapped and strengthened, although its core
consumer-proof rule remained present. A public skill could not be edited
without an unrelated Markdown line-wrap tripping the representative contract
gate, and the rendered failure summary hid diagnostic stderr whenever earlier
scenarios wrote stdout.

## Correct Behavior

Given an unchanged contract phrase, when Markdown whitespace or wrapping
changes, then representative contract validation passes. Given a changed
semantic phrase, it still fails. When an eval emits both streams, the durable
summary shows both.

## Observed Facts

- The broad suite reported 1 failure after 4,955 passes.
- Serial reproduction reduced the failure to `representative-skill-contracts`.
- The required core words existed across lines 92-93 of quality `SKILL.md`.
- A second run exposed an obsolete package pin for the prior scaffold-only rule.
- `summary.json` retained both streams, while `summary.md` selected stdout with
  an `or` expression and therefore omitted the failure stderr.

## Reproduction

`python3 scripts/run_evals.py --repo-root . --scenario-id
representative-skill-contracts --jobs 1` failed on the wrapped raw substring;
the two-file focused standing run reproduced the outer test failure.

## Candidate Causes

- The quality skill accidentally removed the consumer-proof contract.
- Raw substring matching coupled a semantic contract to Markdown whitespace.
- The checked-in plugin export was stale and the eval read the wrong copy.
- Parallel execution or Cautilus availability made the scenario flaky.

## Hypothesis

- If raw substring coupling is the cause, whitespace-normalized membership will
  accept the wrapped phrase while a changed word still fails; disconfirmer: the
  focused eval continues to reject the same core phrase after normalization.

## Verification

- confirmed — a regression accepts line wrapping and rejects changed meaning;
  the representative scenario and outer summary test now pass, 15/15 focused.
- confirmed — package pins now describe the current execute-or-record contract.
- confirmed — a summary regression proves both stdout and stderr are rendered.

## Root Cause

The contract gate described itself as representative rather than a prose
snapshot but implemented exact raw substring membership. A stale package pin
also froze the superseded scaffold-only behavior. Separately, the Markdown
renderer treated mutually informative output streams as alternatives.

## Invariant Proof

- Invariant: when the contract producer preserves words across Markdown
  formatting, the representative gate must accept it; when an eval consumer
  fails, its durable summary must surface the failure stream.
- Producer Proof: the wrapping regression and the changed-meaning negative case.
- Final-Consumer Proof: the actual representative scenario passes, and the
  summary regression reads both rendered streams.
- Interface-Shape Sibling Scan: all core/package/forbidden snippets share the
  normalized matcher; forbidden phrases remain caught when rewrapped.
- Non-Claims: this deterministic scenario run is not a live Cautilus evaluation.

## Detection Gap

- contract validator unit tests | tested missing/present location but not
  formatting invariance | add wrapped-positive plus semantic-negative case
- eval summary tests | asserted success metadata only | add dual-stream render
  assertion independent of live evaluation

## Sibling Search

- Mental model: exact text storage was mistaken for semantic contract identity.
- same layer: package and forbidden snippet matching | decision: same bug, fix
  now through the shared matcher | proof: focused unit tests
- abstraction up: public dogfood acceptance strings | decision: same class,
  diagnostic-only for this slice | proof: structured exact values intentionally
  identify reviewed cases rather than parse prose
- specialization down: summary stdout/stderr rendering | decision: same bug,
  fix now | proof: local payload and rendered-file test
- cross-file: `scripts/eval_cautilus_scenarios.py`

## Seam Risk

- Interrupt ID: none-internal-deterministic-gate
- Risk Class: none
- Seam: none
- Disproving Observation: focused deterministic tests now fail
- What Local Reasoning Cannot Prove: live evaluator behavior, outside this run
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/critique/2026-07-19-portable-proof-path-and-release-identity-critique.md

## Prevention

Match representative prose contracts after whitespace normalization, update
behavior pins when the owned contract changes, and render diagnostic streams
independently instead of choosing the first non-empty stream.
