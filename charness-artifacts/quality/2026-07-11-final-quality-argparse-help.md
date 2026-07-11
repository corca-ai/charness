# Quality Review
Date: 2026-07-11

## Scope

Target boundary: the final ten quality-owned CLIs containing exactly 23
`argparse_missing_help` findings.

Ambient repo findings: after this campaign, repo-wide missing argparse help is
zero; host-surface reference heuristics remain a separate prose-review prompt.

## Current Gates

- `inventory_skill_ergonomics.py` reports missing help advisory-first.
- Direct help, option-scoped tests, existing behavior suites, Ruff, pycompile,
  length/boundary gates, mirror parity, and locked closeout own proof.

## Runtime Signals

- runtime source: timing capture is missing for this help-only campaign.
- runtime hot spots: none investigated.
- coverage gate: final verification-lock standing pytest and focused mutation
  coverage producer passed.
- evaluator depth: deterministic gates only because no prompt, routing, or
  agent-behavior contract changed.

## Healthy

- Repo-wide `argparse_missing_help` is now zero across every public/support skill.
- Twenty-three descriptions preserve every parser default, action, choice,
  repeatability rule, dry-run/write boundary, and output branch.
- Ten public sources match plugin mirrors; existing owner tests bind each option
  to its own wrapping-tolerant help block.

## Weak

- The ergonomics inventory still reports 92 host-surface references across the
  repo, including eight in quality; the lexical heuristic cannot distinguish
  legitimate adapters/examples from portability leaks.

## Missing

- none for argparse help; the target inventory is zero.

## Deferred

- Host-surface reference findings need bounded prose judgment before any edit.
- Shared help-test infrastructure stays deferred without measured drift.

## Advisory

- structural review result: evidence: `inventory_skill_ergonomics.py --summary`;
  capability_needed=quality operators understand every CLI's controls and side
  effects; sequencing matters because write/baseline semantics were reviewed
  before polish; current centers are ten parser owners and focused suites;
  next_center=quality's eight host-reference findings;
  transformation=23 descriptions and executable readback;
  proof_boundary=zero inventory, owner suites, mirrors, and locked closeout;
  enforcement_posture=no-gate.
- prose review result: artifact:
  `charness-artifacts/critique/2026-07-11-final-quality-argparse-help-critique.md`;
  semantic, UX, and verification lenses found two precedence/baseline caveats,
  which were fixed and approved by a clean-rail counterweight pass.
- command: `inventory_skill_ergonomics.py --summary` measured 23 findings before
  and zero after across the quality package and repo.

## Delegated Review

- Delegated Review: executed — three distinct lenses plus counterweight ran;
  one UX child was interrupted and retried successfully. An early fingerprint
  was quarantined after parent edits; the final snapshot verified zero drift.
- Slow-gate lenses `fixture-economics`, `parallel-critical-path`, and
  `duplicated-proof` were not re-delegated because one shared broad lock avoids
  five redundant runs and runtime economics are outside this help campaign.

## Commands Run

- Targeted quality planner and ergonomics inventory; all affected `--help`
  paths; 231 focused tests plus UX-fix tests; Ruff; pycompile; ten mirror
  comparisons; length and boundary ratchets; artifact/pointer validation;
  pre-commit hooks; locked standing pytest and focused mutation coverage.

## Recommended Next Quality Moves

- active quality-host-reference-review — capability_needed=portable quality
  guidance without leaking one host's runtime nouns; next_center=quality's eight
  host-reference findings; transformation=classify legitimate adapter/example
  versus portability leak; proof_boundary=bounded prose review and existing
  skill validation; enforcement_posture=advisory.
- passive shared-help-test-helper because no option-block helper has drifted —
  capability_needed=cheap maintainable CLI proof; next_center=deferred;
  transformation=none; proof_boundary=current owner tests;
  enforcement_posture=no-gate.

## History

- [Archived quality review](history/2026-06-16-quality-review.md)
