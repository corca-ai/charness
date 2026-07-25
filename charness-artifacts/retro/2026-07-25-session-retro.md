# Session Retro
Date: 2026-07-25

## Mode

session

## Context

Closeout retro for the `ranked-chunks-1-3` goal: six slices closing #453's blocking
signal, three named residuals, and the operator's unused-mode sweep. Six commits
(`c846dc26`, `5a31ca81`, `7b710a85`, `3b0750a6`, `c92e9561`, `90d197d2`). What matters
next is that one slice found a bug shipped in every tag since v2.2.1, and the operator
has three queued decisions.

## Evidence Summary

- Six commits on `main`; full `./scripts/run-quality.sh --read-only` green (81 passed,
  0 failed) at slices 4 and 5.
- Five bounded fresh-eye reviews (`bounded-reviewer`), each with a
  `reviewer_boundary_fingerprint.py` snapshot/verify pair; one verify returned drift
  (attributable, see Waste).
- One 17-agent dynamic workflow for the sweep: 27 candidates scouted, 12 adversarially
  verified, 9 confirmed, 3 refuted. Artifact:
  [the sweep inventory](../audit/2026-07-25-unused-mode-option-sweep.md).
- Host log probe (measured, claude session scope): 457 token snapshots, 282 function
  calls, 25 patch applications, 0 context compactions, 6 subagent spawns. Proxy signals:
  no repeated broad gates, no repeated VCS commands.
- Mutation evidence: all four #453 changed-line targets verified COVERED via
  `mutation_sampling_lib.run_test_coverage`, each individually mutated and killed.

## Waste

- **`git checkout -- <path>` used to restore a mutation-test target while the slice was
  uncommitted.** It reverted to HEAD and silently discarded the slice-2 refactor. Worse,
  it poisoned the evidence: the reverted tree made one test raise `AttributeError`, so
  every subsequent mutant reported KILLED regardless of the mutation. Four "verified"
  results were meaningless. Cost: one full re-do plus a reviewer round-trip.
- **Two wrong justifications written into a docstring** (slice 3): ledger fields framed
  as "rung-2 content judgment" when they are presence-only checks that `verify-closeout`
  applies to this same carrier, and close-keyword rejected for a signature limitation
  that does not exist. Both contradicted by files one directory away. A docstring that
  exists to stop the next reader re-filing a gap is worse than absent when it is wrong.
- **The first replacement test reproduced the defect it was replacing** (slice 4):
  it asserted `-config` was present rather than binding it to the generated path, so
  passing the repo's own `specdown.json` would have kept it green and restored the churn.
- **Reviewer boundary verify run after applying fixes** (slice 3), making that review's
  boundary proof inconclusive — the drift set was the parent's own edits.
- **Sweep agents were not read-only.** One edited `.agents/cautilus-adapter.yaml`
  (`run_mode: ask` → `auto`) to A/B a planner branch and left it dirty. Caught by
  `git status` and restored, but the repo has a `bounded-reviewer` type for exactly this
  and it was not used for workflow agents.
- Smaller: the 800-line gate fired mid-slice forcing an unplanned split; two failed
  attempts at the specdown ephemeral config before discovering specdown resolves `entry`
  against the config file's directory; a widened drift-guard regex that over-matched
  skill-package gates on first try.

## Critical Decisions

- **Reproduce before fixing (slice 4).** A prior debug artifact suggested the specdown
  residual might already be closed. Running the full gate first showed it reproducing,
  with a one-line diff that named the root cause immediately. Closing it as
  already-fixed would have been wrong and would have kept the tax.
- **Test the "untested" path rather than trusting it (slice 5).** The handoff said the
  fresh-install render path was untested. Reading "untested" as "unknown" rather than
  "probably fine" is what surfaced a bug shipped through eight releases.
- **Remove the branch instead of chasing the mutant (slice 2).** With two argparse
  choices, `==` and `>=` are behaviourally identical, so one survivor was unkillable by
  any test. A dispatch table removed the surface rather than accumulating a permanent
  known-survivor.
- **Fix the gate, not just the instance (slice 5).** `check_export_safe_imports.py`
  already encoded the export-collapse insight for imports and stopped one syntax short of
  filesystem paths. Extending it immediately found four more constants of the same shape.
- **Report-first on the sweep, and no release.** Both were the operator's boundaries and
  both held; the release decision is queued rather than taken.

## Expert Counterfactuals

- **Engelbart, `system-improving-itself` (the briefed lens): design T alongside LAM.**
  Four separate defects this session shared one shape — a check that asserts a proxy for
  the property it is named after. The specdown test grepped a flag string; the mutation
  loop trusted a test suite whose baseline was red; `check_export_safe_imports` covered
  the import syntax but not the path syntax; the `assert applies` guard was untestable.
  Engelbart's move is not to fix the four instances but to ask what in the *tool system*
  lets a proxy assertion pass for a property assertion — and the answer here is that
  nothing forces a test to demonstrate it fails when the property is violated. The
  counterfactual: before writing any guard, write the violation first and watch it fail.
  Applied late this session (adversarial mutation of every new guard) but only after the
  reviewer named it twice. Making it the *first* step of a guard-writing slice, not the
  verification step, is the durable change.
- **Gary Klein, pre-mortem on evidence rather than on outcome.** Every waste item above
  is a case of trusting a green signal whose validity was never checked: a green mutant
  loop over a red baseline, a green test over a reverted tree, a green quality run that
  dirtied the worktree. Klein's pre-mortem asks "assume this evidence is lying — how?"
  The concrete different action: assert the baseline is green *before* each mutation
  iteration (adopted mid-session, and it immediately caught the reverted tree), and treat
  any restore mechanism that can reach HEAD as unsafe while work is uncommitted.

## Sibling Search

Transferable pattern: **a check named for a property that only asserts a proxy for it.**

- same layer: `tests/quality_gates/test_quality_runner.py` source-guard tests that read
  `run-quality.sh` and assert literal substrings | decision: same waste, fix now | proof:
  rewrote `test_quality_runner_keeps_specdown_reports_out_of_the_worktree` to bind the
  flag to its variable and added `test_quality_runner_leaves_no_specdown_state_in_the_worktree`,
  which observes the worktree directly; both adversarially verified to fail when the churn
  is reintroduced
- abstraction up: `scripts/check_export_safe_imports.py` — the gate encoded the
  export-collapse rule for import syntax only | decision: same waste, fix now | proof:
  extended to filesystem paths; immediately fired on four dead constants, now deleted;
  585 files validate clean
- specialization down: other repo-file-grepping tests (`test_authoring_preflight_reference.py`,
  `test_critique_prepare_packet.py`, `test_handoff_chunker_auto_draft.py` and ~6 more
  assert literals against read file content) | decision: valid follow-up outside the slice
  | proof: `grep -rln 'read_text' tests/` ranked by literal-substring assertion count;
  most legitimately assert *generated output* content rather than a runtime property, so
  the pathology is narrower than the grep and needs a per-test read, not a sweep |
  follow-up: deferred [handoff Next Session](../../docs/handoff.md) proxy-assertion review
- mental-model siblings: the mutation-verification loop itself — "tests failed, therefore
  the mutant was killed" is the same proxy substitution | decision: same waste, fix now |
  proof: loop now copies a pristine file for restore and asserts a green baseline before
  each mutation; that assertion is what caught the reverted tree

## Next Improvements

- workflow: write the violation before writing the guard. Every new gate, validator, or
  source-guard test gets its failing case demonstrated first, not as a later verification
  step. Adopted reactively this session; make it the opening move.
- capability: spawn workflow/discovery agents as `bounded-reviewer` (or otherwise
  read-only) when the task is discovery. This session's sweep agents mutated a tracked
  adapter; the repo already has the type and the boundary-fingerprint helper for it.
- memory: two hazards recorded in the goal artifact's Active Operating Frame and carried
  to the handoff — never restore a mutation target with `git checkout --` while the slice
  is uncommitted, and run `reviewer_boundary_fingerprint.py verify` immediately on
  reviewer return, before applying any of its fixes.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-25-session-retro.md
