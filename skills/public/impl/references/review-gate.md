# Review Gate

Every meaningful implementation slice needs a review pass before stopping.

## Minimum Lenses

- runtime behavior and branch reachability
- boundary honesty and ownership
- docs/spec synchronization

## Stronger Gate

Use a stronger review pass when the slice touches:

- shared runtime seams
- package or module boundaries
- orchestration or recovery flows
- operator-facing setup or repair flows
- docs that claim architectural ownership

## Good Outcome

A good review pass either:

- finds nothing important and confirms the slice is coherent
- or finds concrete issues that get fixed before stopping

It is not a decorative reread.

Fresh-eye review is the default. The stronger gate adds depth, not the existence
of review itself.
