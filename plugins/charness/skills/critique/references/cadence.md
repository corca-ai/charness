# Critique Cadence

Critique cadence is scoped by risk boundary, not by commit count. The
slice-unit definition itself — what makes a unit meaningful enough to review —
is owned by
[meaningful-slice-cadence](../../../shared/references/meaningful-slice-cadence.md).

## Escalation Ladder

Use the lightest rung that still protects the next irreversible decision:

1. **No repo-change turn** — inspect-only, status-only, and routing-only work may
   record `Critique: not-applicable <reason>`.
2. **Small local-risk slice** — a same-agent scoped critique is enough when the
   change is narrow, reversible, and does not alter workflow, prompt,
   public-skill, validator, export, release, issue-closeout, compatibility,
   host-proof, install/update, rename, deletion, design-lock, or migration
   behavior. Record the decision, likely misread, counterweight triage, and next
   move in the caller artifact. This is recorded in the caller artifact and is
   not an invocation of standalone `critique`.
3. **Substantial slice or bundle** — run standalone `critique` with bounded
   fresh-eye workers once for the meaningful slice or bundle. The adapter may
   select typed subagents as an alternate execution path. This covers
   non-trivial workflow, public-skill, prompt, validator, export, release,
   issue-closeout, compatibility, host-proof, install/update, rename, deletion,
   and design-lock decisions.
4. **Final closeout** — for non-trivial goals, use standalone fresh-eye worker review
   to check cross-slice drift, generated/export sync, disposition of surfaced
   improvements, and non-claims. Do not redo every slice-level review unless a
   new risk boundary appeared after the last review.

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
input, or stable failure code, or when the evidence identity changed. Use
`verification_retry.py` to emit the retry key and disposition; log timestamps
and raw output are not failure identities. The same tuple and same failure
without new evidence is `stop-no-progress`. Record the narrowed scope or
non-claim and move on. Keep a broad final gate only when the irreversible
boundary's required consumer closure calls for it.

```bash
python3 "$SKILL_DIR/scripts/verification_retry.py" \
  --subject <subject-identity> --verifier <verifier-identity> \
  --input <input-identity> --failure-code <stable-failure-slug> \
  --evidence <new-evidence-identity-or-none> [--previous-key <key>]
```

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
