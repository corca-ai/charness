<!-- charness-work-item-key: wall-clock-rewrite-remainder -->

## Objective

Every remaining entry of the wall-clock census is rewritten to a deterministic claim or deleted; done means the census list is empty.

## Owned scope

- Work the census recorded by `wall-clock-census-and-764`, entry by entry: controlled clock, controlled child, or an observation the test itself forces; delete a test whose only claim is timing. No retry, tolerance widening, or deselection.
- Each batch lands with the standing lane green and the census file updated; the item is not done at any batch count, only at zero entries.

## Acceptance

- The census file lists zero remaining entries and the form check is green on the whole of `tests/`.
- Standing and release lanes green in a clean clone.

## Focused verification

The form check; `run_standing_pytest.py`; per-batch focused runs for locating only.

## Dependencies

wall-clock-census-and-764.

## Non-claims

Does not touch the sampler workflow or #764.
