# Critique Cadence

Critique cadence is scoped by risk boundary, not by commit count. The
slice-unit definition itself — what makes a unit meaningful enough to review —
is owned by
[meaningful-slice-cadence](../../../shared/references/meaningful-slice-cadence.md).

## Escalation Ladder

Use the lightest rung that still protects the next irreversible decision:

1. **No repo-change turn** — inspect-only, status-only, and routing-only work may
   record `Critique: not-applicable <reason>`.
2. **Small local-risk slice** — ordinary reversible edits use deterministic
   proof and may record `Critique: not-required <reason>`. A short scoped
   critique is optional judgment, not a forced fresh-eye run. The reason must
   name the boundary classification and the caller still records the next
   move when one matters.
3. **Substantial slice or bundle** — select standalone `critique` only when the
   change crosses a material authority, durability, external-write, security,
   release, compatibility, install/update, deletion, migration, or proof-
   surface boundary. The selected critique uses its configured bounded reviewer
   contract; it is not silently substituted with a same-context pass.
4. **Final closeout** — the owner of an irreversible boundary decides whether
   a distinct observer and second evidence channel are required. Do not repeat
   slice-level review merely because a goal is large; do not make ordinary
   local work pay a final-boundary cost.

## Review Unit

The commit is not the review unit. A slice may include several cheap commits
before one bounded critique, as long as the slice contract, changed files,
expected invariants, proof already run, non-claims, and reviewer questions stay
coherent. A later commit inside the same slice triggers another fresh-eye pass
only when it changes the risk boundary, such as adding a new public skill
surface, validator family, export path, issue-closeout carrier, release surface,
host-proof claim, or irreversible migration. Mandatory premortem follows the same
rule — it fires once per slice-intent boundary, not per commit; see the single
resolution in
[meaningful-slice-cadence](../../../shared/references/meaningful-slice-cadence.md)
*Review Cadence*.

## Verification Boundary And Retry

Before a gate or review rerun, record the smallest claim that needs proof and
the final consumers that can actually observe it. Treat the verifier as a
separate review surface when its implementation, trigger rules, output schema,
or trust assumptions changed, or when its output suggests over-checking or a
false green. The verifier check should be the cheapest contract/negative-control
proof that can establish that surface; it does not implicitly authorize a full
subject-suite rerun. Record the negative-control command, expected refusal,
observed result, and receipt (or a typed non-claim).

Classify a failure as `scope-too-broad`, `verifier-defect`, or
`subject-defect` before choosing a repair. A retry is justified only when at
least one member of the canonical identity tuple changed: subject, verifier,
input, or stable failure code. These identities must be content-addressed
`sha256:` digests; log timestamps, raw output, and newly renamed receipts are
not identity changes. Use `verification_retry.py` to emit the retry key and
disposition. Evidence is recorded for audit, but a new evidence label never
authorizes another run for the same tuple. To question an unchanged verifier,
run its smallest negative-control/input probe and bind that probe's digest as
the changed input; do not rerun the whole subject suite. The same tuple is
`stop-no-progress`. Record the narrowed scope or non-claim and move on. Keep a
broad final gate only when the irreversible boundary's required consumer
closure calls for it.

```bash
python3 "$SKILL_DIR/scripts/verification_retry.py" \
  --subject sha256:<subject-digest> --verifier sha256:<verifier-digest> \
  --input sha256:<input-or-negative-control-digest> \
  --failure-code <stable-failure-slug> \
  --evidence sha256:<receipt-digest-or-none> [--previous-key <key>]
```

The helper is a one-shot scope decision, not a retry ledger or a truth oracle.
The caller owns any durable history it genuinely needs; adding a second
attempt counter here would make the retry mechanism another broad verifier.

## Slice Packet

For standalone fresh-eye critique, pass a bounded packet instead of the whole
historical goal by default:

- intent and slice boundary
- changed files and owning/generated surfaces
- expected invariants and known non-claims
- tests or proof already run, including proof intentionally skipped
- specific reviewer questions and out-of-scope lines

Counterweight triage stays mandatory: findings should land in the standard bins
(`Act Before Ship`, `Bundle Anyway`, `Over-Worry`, or `Valid but Defer`), so the
caller does not convert every concern into process cost.
