# Review Gate

Every meaningful implementation slice needs a proof decision before stopping.
A reversible slice may record `Critique: not-required <reason>`; a review pass
is required only when the slice crosses a named risk boundary. What makes a
slice meaningful — a reviewable intent unit with a named proof intent and
verification boundary, never merely a small diff — is owned by
[meaningful-slice-cadence](../../../shared/references/meaningful-slice-cadence.md).

## Minimum Lenses

- contract closeout honesty
- runtime behavior and branch reachability
- [boundary honesty and ownership](../../../shared/references/boundary-ownership-brief.md)
  — run its producer/consumer question set when the slice touches shared, generic,
  or cross-surface code
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

Fresh-eye review belongs to the named high-risk boundaries. The stronger gate
adds depth there; it is not a default tax on reversible local work.

## Claims Review

Before a completion flip, one bounded reviewer audits **what the closeout
artifact asserts**, not whether the code is correct. Hand it the acceptance
criteria and the closeout sections and ask it to:

- re-derive every figure it can, and name the ones it cannot verify rather than
  assuming them;
- check each recorded reason against the text or code it cites;
- name anything claimed as proven that was only reasoned about;
- check each promised verification step against recorded evidence that it ran.

This is a different question from the code review above, so running more code
rounds does not satisfy it. A code reviewer is asked "is this right?" and reads
the diff; nobody reading the diff is asked whether the summary survives contact
with it — and the author, who wrote both, is the last one able to tell.

Use a distinct observer. When the host cannot provide one, record the concrete
signal and leave the review unproven; a same-agent reread is exactly the
observer this exists to exclude.

## Contract Re-read

When a canonical artifact or inline current-slice contract exists:

- re-read `Fixed Decisions` and named acceptance checks before stopping
- confirm each item is reflected in the delivered slice or explicitly deferred
  or reclassified in the contract
- if the review finds drift, update code or contract before closeout instead of
  leaving chat-only explanation
