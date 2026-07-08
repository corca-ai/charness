# Resolution Critique — corca-ai/charness#422 fix (2026-07-08, pre-commit)

Bounded fresh-eye reviewer (parent-delegated, high-leverage tier), recurrence
focus: "what would let a real blocking signal be replaced by a collateral
symptom in the posted mutation-gate comment again." Prior context: the causal
review at
[2026-07-08-issue-422-causal-review.md](./2026-07-08-issue-422-causal-review.md)
(root cause not re-litigated).

Reviewer verified in code: CI wiring lines up end-to-end with zero flag
threading — `check_mutation_suite_score.py` passes only `--repo-root`; both
checkers default to `DEFAULT_BASELINE_ABORT_MARKER` and resolve against
repo_root; the sampler writes the same resolved default. A fresh CI checkout
cannot carry a stale marker; the parent's end-to-end simulation confirmed the
posted-body shape.

## Act Before Ship (folded before commit)

- Local stale-marker false report: the marker was deleted only at sampler
  start, so locally (gitignored `reports/` persists) a stale abort marker
  could mask a newer mutation run's real results — the same misattribution
  class in reverse. Folded: `check_mutation_score.py` now ignores the marker
  when the stats file exists and is at least as fresh (`_marker_is_stale`
  mtime guard), with tests for stats-newer / stats-absent / marker-newer.

## Bundle Anyway (folded before commit)

- `parse_failed_nodeids` missed pytest collection `ERROR <nodeid>` lines; a
  collection-dead baseline would fall back to log-tail only. Folded: `ERROR`
  short-summary alternation added with tests.

## Valid but Defer

- Baseline output is now buffered (captured, teed after completion) instead
  of streamed: the ~3-4 min CI baseline appears silent until done. Accepted
  trade for nodeid capture; revisit only on operator complaint.
- workflow_dispatch/PR-path proof of the misreport class — already deferred
  by the causal review; recorded in the close carrier.
- JS checker's collateral line stays marker-presence based (no mtime guard);
  CI is the consumer that matters for the posted comment, and the cosmic-side
  guard removes the primary local false-report path.

## Over-Worry

- Marker + adapter-config-None path: falls through to stats-missing rc 2;
  covered by test. Dismissed.
- `mutation_coverage_producer.py` caller of `run_test_coverage`: same
  exception type, capture change type-compatible; its suite passed. Dismissed.
- Close-carrier overclaim: the carrier carries the provider-roundtrip
  non-claim and all bug-ledger fields. Dismissed.

Fresh-Eye Satisfaction: parent-delegated
Reviewer tier: high-leverage requested; host default reviewer model spawn (no
per-spawn tier fields exposed to confirm application).
