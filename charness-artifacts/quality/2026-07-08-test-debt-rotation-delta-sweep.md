# Test-Debt Rotation — Post-Audit Delta Sweep (2026-07-08)

Standing rotation from docs/handoff.md; scope = test additions AFTER the
2026-07-03 full-suite audit
([2026-07-03-pytest-suite-test-value-audit.md](./history/2026-07-03-pytest-suite-test-value-audit.md)),
which had already judged the pre-existing suite lean.

## Scope

- Baseline: `12652565` (2026-07-03 22:32 KST). Delta at sweep time:
  76,180 → 80,044 tokei test code lines (+3,864), 67 files touched.
- Method: 7 subsystem-batch classifiers (dup-ratchet, critique,
  issue-closeout, announcement, mutation, skill-safety, misc) each read the
  added tests AND the source under test; every non-keep candidate got an
  adversarial load-bearing verifier doing empirical mutant enumeration.
  13 agents, ~840k subagent tokens. Coverage-Model Correction honored
  (subprocess tests are traced and kill mutants here).

## Result

- 193 added/grown test functions judged: **187 keep** (load-bearing), 6
  candidates → **4 deletions confirmed, 2 rejected as load-bearing** by
  verifiers (33% candidate rejection — consistent with the audit's ~11-33%
  over-claim calibration; the delta is NOT bloated).
- Deleted (each with a verifier-documented no-unique-kill proof and named
  surviving siblings):
  1. `test_mutation_baseline_abort.py::test_check_mutation_score_marker_present_writes_summary_and_fails`
     (double-killed by the newer-than-stats sibling + `_marker_is_stale` unit
     trio + log-tail fallback test).
  2. `test_floor_addition_restraint_advisory.py::test_advise_silent_for_non_gate_named_new_script`
     (byte-identical fixture sibling; 6-mutant kill matrix, no unique kill).
  3. `test_check_issue_closeout_commit_msg_inprocess.py::test_bare_classification_defaults_to_bug_without_explicit_line`
     (subprocess sibling strictly stronger; every default-literal/branch
     mutant enumerated and double-killed).
  4. `test_check_issue_closeout_commit_msg_inprocess.py::test_exemption_advisories_empty_for_nonexempt_classification`
     (branch-free wrapper pinned at both CLI and owner layers).
- Rejected candidates (kept; verifiers produced concrete unique kills):
  the critique scaffold post-cutoff stub pair
  (`test_critique_boundary_ownership_presence.py` /
  `test_critique_fresh_eye_presence.py`) — the merge premise was false: the
  fresh-eye test dates its artifact 2026-07-05 (boundary floor grandfathered)
  and each kills a scaffold pre-fill mutant the other cannot see.
- Also folded: `test_check_issue_closeout_commit_msg_inprocess.py`'s
  docstring cited the debunked #393 subprocess-only-attribution premise as
  the file's rationale (the exact trap the audit's Coverage-Model Correction
  names); rewritten so the next audit does not trip on it.

## Discipline satisfied

- Mutation proof per deletion: adversarial verifier mutant enumeration
  (documented above) + post-delete focused pytest 74 passed across all
  affected and sibling files.
- Fresh-eye pre-delete review: bounded parent-delegated reviewer re-read
  every claimed sibling, confirmed `_advisory_fn` not orphaned, docstring
  accuracy vs the audit, and diff scope; verdict safe-to-commit.
- Not headroom-pressured: the ratio gate has been advisory-only since
  `6415175b` (#420); nothing in this sweep was motivated by LOC pressure.

## Found mid-sweep (fixed separately)

- The 2026-07-08 12:50 UTC scheduled mutation run went red on
  `test_migrate_dup_fingerprints.py::test_cli_dry_run_reports_plan_without_writing`
  — an env-dependent live-scan test missing the cluster's standard
  nose-presence skip guard; fixed and pushed as `28d76718`. That red was also
  the first provider-roundtrip proof of the #422 fix (the posted comment
  named the failing nodeid directly).

Next rotation trigger: the next meaningful test-LOC delta; baseline for it
is this sweep's HEAD.
