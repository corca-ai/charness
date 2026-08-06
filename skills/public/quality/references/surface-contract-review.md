# Surface Contract Review

The quality artifact separates a routed proof receipt from semantic coverage.
The receipt answers “which command ran?”; this packet answers whether the
affected surface's meaning was observed at the boundary where a user or
downstream consumer relies on it.

Use one packet for the review scope. If several surfaces share the same risk,
name them in `surface` and make the shared owner and projections explicit; split
the packet when their contracts differ materially.

Required fields:

- `semantic coverage`: `observed`, `partial`, or `not-in-scope`. `partial` and
  `not-in-scope` must name unexamined axes rather than implying a green result
  is complete.
- `surface`: the user-visible or cross-boundary surface under review.
- `owner`: the canonical source of the meaning, not merely the file that renders
  it.
- `projections`: where that meaning appears, such as URL, DOM, storage, remote
  payload, or geometry; use an explicit `n/a` only when the axis truly does not
  apply.
- `state scope`: whether state is cumulative, session, request, viewport, or
  another named scope.
- `transitions`: relevant success, pending, failure, reload, or narrow-viewport
  states; name `n/a` only when the transition cannot exist for this surface.
- `proof boundary`: the command, test, provider roundtrip, or final-consumer
  observation that can actually exhibit the claim.
- `unexamined axes`: every relevant axis not proved in this run. `observed` may
  say `none`; every weaker coverage status must list what remains.

This is a form and disclosure floor, not an automatic semantic judge. A packet
can be honestly marked `partial`; the quality artifact must not turn that into
an unqualified green claim. Product-specific meaning, geometry, ownership, and
tradeoffs remain reviewer-owned.
