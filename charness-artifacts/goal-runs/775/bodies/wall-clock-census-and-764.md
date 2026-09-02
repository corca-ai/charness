<!-- charness-work-item-key: wall-clock-census-and-764 -->

## Objective

The wall-clock-dependent tests in `tests/` are a recorded list, a form check refuses the next one, the tests that failed in the six #764 runs are deterministic or gone, and the hosted mutation sampler's coverage baseline runs green on this tree.

## Owned scope

- Census: every test whose claim depends on wall-clock time (sleeps as synchronisation, timeouts as the assertion, attempt counts under a real drain, `time.monotonic` deltas, retry counts against real children). Start from the union of failing tests across the six #764 runs (33346505915 to 33631065064); record the full list with its count before any rewrite.
- Rewrite the #764 union so each claim is deterministic (controlled clock, controlled child, or an observation the test itself forces), or delete a test whose only claim is timing. No retry, tolerance widening, or deselection. The remainder of the census is `wall-clock-rewrite-remainder`.
- A standing form check that refuses a new wall-clock claim; lands with the first batch.
- Reproduce the sampler baseline in the CI shape (fresh clone, mirror materialised, `node_modules/.bin` on PATH, `CHARNESS_REQUIRE_MARKDOWNLINT=1`, the sampler's own pytest command) before and after; record both.
- Push. Do not wait on the schedule.

## Acceptance

- The census list is recorded with its count; every #764-union entry is rewritten or deleted; the form check refuses a seeded new one.
- The CI-shape baseline passes on the pushed tree.
- Standing and release lanes green in a clean clone.

## Focused verification

CI-shape baseline run; `run_standing_pytest.py`; the form check's own tests.

## Dependencies

layout-resolver, release-lane-standing-evidence.

## Non-claims

Does not close #764; that happens through the recovery observer once a scheduled run is green (read in integrated-closeout or later).
