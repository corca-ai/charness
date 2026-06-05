## Observed problem

Cheap, deterministic test-fixture structural invariants run only inside the
final broad pytest gate (`tests/quality_gates/test_repo_copy_invariants.py` ->
`scripts/check_test_repo_copy_invariants.py`), not in the per-slice / pre-commit
deterministic aggregate (`scripts/run_slice_closeout.py`). During the #302-#305
robustness goal, a new web-fetch cleanup test used `shutil.ignore_patterns(...)`
inline instead of the canonical `REPO_COPY_IGNORE`. Every per-slice aggregate and
the commit passed; the violation only surfaced ~172s into the final broad pytest
gate at closeout, forcing a late-stage fix commit after the slice that introduced
it was already closed.

## Structural pattern

A cheap deterministic invariant (a standalone `scripts/check_*.py` that is fast
and path-scoped) is enforced only through a `pytest` test inside the expensive
broad suite, so violations are detected at final-closeout cost instead of at the
commit boundary where the offending change was made. This is the inverse of the
repo's own "cheap deterministic checks at commit boundaries" discipline.

## Triggering instance(s)

#302 slice: `tests/test_web_fetch_cleanup.py` defined `shutil.ignore_patterns(...)`
inline; caught only by the broad gate at goal closeout (2026-06-05), fixed in a
follow-up commit.

## Suggested direction (not a decision)

Consider running the fast standalone structural checkers
(`check_test_repo_copy_invariants.py`, and peers of the same shape) in the
`repo-python` surface of the per-slice / pre-commit aggregate so test-fixture
drift fails at the commit boundary. Weigh against fast-aggregate latency; this is
a quality-contract change and should route through `quality`.

## Destination

charness (quality gate economics / `run_slice_closeout.py` + surfaces manifest).
Related: the standing "cheap checks at commit boundaries, expensive proof at
bundle boundary" cadence in docs/conventions/implementation-discipline.md.
