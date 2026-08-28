# Lane brief: 753-seed-dedup (extract test seeding duplication)

Governing context:
`charness-artifacts/design-studies/issue-753/2026-08-28-jtbd-audit-quality-gates.md`
sections "Why the ratio reads 1.18" and the JTBD verdict: cross-file
6-line clone coverage in tests is 7.2% (~10.4k duplicated lines) vs
4.4% in production, concentrated in per-file synthetic-repo seeding
boilerplate. The goal is extraction into shared helpers — NOT deletion
of tests and NOT any change to what the tests assert. Do not spawn
descendant agents.

## Outcome

1. Measure first, with this exact metric (also your success metric):
   normalize each `tests/quality_gates/*.py` line by `strip()`,
   drop empties and `#` comments, hash every 6-line window, and count
   lines covered by a window appearing in 2+ files. Record the before
   number.
2. Identify the LARGEST cross-file duplicated seeding/boilerplate
   families (expect: tmp_path repo seeding — `.agents/` +
   adapter/surfaces writes, git-init + commit sequences, module-load
   preambles, fake-binary/executable writers, env-dict assembly).
   Rank by total duplicated lines.
3. Create ONE new helper module
   `tests/quality_gates/seeding_support.py` (do NOT add to
   `support.py` — a concurrent lane owns that file) with small,
   parameterized helpers for the top families. Helpers must be
   behavior-preserving parameterizations, not config-object
   frameworks: a call site should shrink to 1-3 lines and stay
   readable in place.
4. Convert call sites for the top families across
   `tests/quality_gates/`, EXCLUDING these files a concurrent lane
   owns (do not touch them at all):
   `support.py`, `test_plugin_dir_references.py`,
   `test_test_production_ratio.py`, `test_standalone_imports.py`,
   `test_release_real_host.py`, `test_native_gate_lib.py`.
5. Target: reduce the metric from step 1 by at least 4,000 duplicated
   lines within `tests/quality_gates/`. If a family turns out to be
   deliberate per-file isolation (a test intentionally owning its own
   fixture shape), skip it and say so — do not force-extract semantic
   variation into a helper with 8 keyword arguments.
6. Every touched test keeps passing with UNCHANGED assertions; only
   setup plumbing moves. No test files are deleted or merged in this
   lane.
7. Re-measure the step-1 metric after; report before/after and total
   line-count delta (`git diff --stat`).

## Boundaries

Scope (must match the task-run `--scope` list exactly):
`tests/quality_gates`. Within it, the six files listed in Outcome 4
are FORBIDDEN (concurrent-lane ownership). Out of scope: everything
else — `scripts/**`, `tests/` outside quality_gates, `native/**`,
`plugins/**`, `.agents/**`. Do not change `run-quality.sh` labels or
any production behavior.

## Verification

- `python3 scripts/run_standing_pytest.py` is the standing gate, but
  for lane speed run the focused form:
  `python3 -m pytest tests/quality_gates -q` (full directory — your
  edits are cross-cutting) and report the pass count;
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`
  (extraction must not add test→script subprocess boundaries);
- `python3 scripts/check_test_production_ratio.py --repo-root .
  --require-git-file-listing --advisory` (report the ratio delta);
- `./scripts/check-python-lint.sh`.
The parent runs the FULL battery after integration.

## Stop condition and result shape

One coherent commit, prefix `prune(753):`. Final message: the
before/after duplication metric, families extracted with call-site
counts, families deliberately skipped with reasons, test pass count,
deviations with reasons.
