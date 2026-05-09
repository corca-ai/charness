# Five Steps

`debug` follows five deliberate moves.

1. define the problem
2. define correct behavior
3. build the smallest honest reproduction
4. enumerate diverse causes
5. verify a falsifiable hypothesis

These steps are non-linear. New observation may send the work backward. What is
not allowed is skipping a step and calling intuition a diagnosis.

## Durable Follow-Through

When the verified root cause reveals a reusable rule, contract, or repeated
mistake, do not let it die in the debug artifact alone. Either:

- update the durable surface that owns the rule (skill prose, reference
  doc, validator, recommendation list, or test) so the next operator
  inherits the rule, or
- file a follow-up issue with the seam, the symptom, and the proposed
  durable surface, or
- explicitly record why neither move applies (one-shot bug, repo-local
  oddity, scoped-out by current contract).

A debug artifact that names a reusable rule and stops there is incomplete:
the next session has no way to find the lesson except by re-debugging the
same class of failure.
