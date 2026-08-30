## Situation

A committed critique packet inside a reviewed range cannot be declared through
the DEFAULT path. The auto sweep excludes `charness-artifacts/critique/` so a
packet does not review itself — correct. Committed-ref mode requires the declared
set to match the range EXACTLY — also correct. This repo commits its review
packets by convention (16 tracked at time of writing).

So any range containing a committed packet refuses by default:

```
reason_code: changed-ref-path-mismatch
declared = 7 paths
changed_ref = 9 paths   (+2 critique packets)
```

## Observed problem

Same intersection shape as #759: two individually-correct rules leaving a
legitimate range undeclarable through the ordinary path.

Unlike #759, an EXACT declaration exists and does not weaken the evidence:
passing the full path set via `--reviewed-paths-file` produces `carrier_ok: true`
with the range binding preserved. That is materially different from the
`--prepared-for` workaround #759 described, which drops the changed-ref binding
entirely.

## Impact

Friction rather than a hole. Any session reviewing a range that includes its own
prior review artifacts must build an explicit manifest, and the default failure
mode is a refusal whose message does not say why the two sets differ or that an
explicit manifest resolves it.

## Expected behavior

Owner's call among at least:

- reconcile the sweep exclusion with committed-ref exactness (exclusions apply to
  the auto sweep, so a range-derived set could carry them);
- keep the refusal but name the remedy in it — report WHICH paths differ and that
  an explicit manifest declares the range exactly;
- decide that committing packets is what should change.

## Non-claims

- Neither rule is wrong on its own; this is about their intersection.
- Not urgent: the exact declaration exists today and preserves range binding.

AI-provenance: agent-authored from the 2026-08-30 declaration-intersection sweep,
at the operator's direction.

---

<!-- charness-work-item-key: issue-762-committed-packet-default -->
# Work Item #762 — Make committed-packet refusal actionable

## Purpose and premise

Retain exact reviewed-input safety while making the default refusal identify differing paths and the supported `--reviewed-paths-file` remedy.

## Acceptance and proof

A committed-packet mismatch lists exact paths and remedy; silent self-inclusion or subject-identity drift fails. The issue owns its decision record and behavior verdict.

## Non-claims

No silent auto-inclusion of review artifacts and no consumer-specific policy.
