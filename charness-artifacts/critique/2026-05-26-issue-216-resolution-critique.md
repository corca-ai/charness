# Issue 216 Resolution Critique

Date: 2026-05-26
Target: code critique for GitHub issue #216 resolution
Fresh-Eye Satisfaction: parent-delegated
Packet Consumed: n/a

## Change

Fix false mutation scope-gap failures caused by sampler/filter coverage-oracle
drift. The change adds `scripts/mutation_line_coverage_lib.py`, routes both
`scripts/mutation_sampling_lib.py` and `scripts/filter_cosmic_ray_mutants.py`
through it, syncs the plugin export, and records the RCA in
`charness-artifacts/debug/2026-05-26-issue-216-mutation-scope-oracle.md`.

## Causal Context

Run 26415240334 failed at 92.2% reachable score because one sampled mutant was
filtered as uncovered. The sampled manifest treated
`scripts/setup_artifact_policy_lib.py` as fully mutation-line covered, while
the post-init filter used exact `executed_lines` membership and skipped a
multi-line statement continuation mutant at line 34.

## Counterweight Triage

### Act Before Ship

- Include both new helper files in the commit:
  `scripts/mutation_line_coverage_lib.py` and
  `plugins/charness/scripts/mutation_line_coverage_lib.py`.
- Tie final #216 closeout to a committed-head mutation proof showing
  `Status: PASS` and `Scope gaps (uncovered sampled mutants): 0`.

### Bundle Anyway

- Keep the helper, sampler/filter call sites, plugin export copies, debug
  artifact, and RCA ledger entry in the same commit.
- Strengthen the regression test so it asserts the shared oracle and filter
  decision agree for the same synthetic multi-line mutation.
- Preserve focused pytest, export parity, and `git diff --check` in closeout
  evidence.

### Over-Worry

- Requiring a broader redesign of all sampler/filter skip logic is out of
  scope. The RCA isolates the drift to statement-span coverage vs exact
  `executed_lines`.
- Treating helper coupling as a risk is inverted for this bug; sharing the
  classifier is the recurrence-prevention move.
- Exact-line-only coverage is not a safer model for multi-line Python
  statements; it is the false-negative source.

### Valid but Defer

- A future validator could detect new raw `line_number in covered_lines` style
  mutation-scope filters.
- A future fixture could replay a real Cosmic Ray work item/session shape
  instead of a lightweight mutation object.
- Annotation-union and trivial-entry-guard skip predicates remain a seam, but
  they are not the issue #216 failure mode.

## Resolution

The bundled equivalence-style regression was added before closeout. The
remaining required closeout proof is post-commit mutation execution at the
committed head.
