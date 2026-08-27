---
name: prove
description: "Use when explicitly selected to format evidence for a concrete proof, irreversible, release, or live-boundary claim. It is conditional, not part of ordinary implementation."
---
# Prove

Use Prove only when the user, current contract, or boundary owner explicitly
selects it. Prove turns one concrete claim into a concise evidence report;
ordinary reversible implementation can finish with focused evidence in its own
workflow.

## Workflow

1. Identify the claim.
   - State what changed, what the evidence must establish, and the non-claims
     that will remain open.
2. Run the narrowest strongest evidence.
   - Prefer an executed test, command, consumer, or provider observation over
     inspection. Use the smallest path that can actually observe the claim.
   - If the strongest path is unavailable, name the concrete limitation and
     leave that part unproven.
3. Sync actual truth surfaces.
   - Update the source-of-truth docs, README, adapter, or generated surface
     when the claim changes it. Do not imply that an untouched surface or live
     runtime was synchronized.
4. Route owned boundaries.
   - `quality` owns standing repo-wide checks.
   - `hotl` owns applied live behavior and provider readback.
   - `issue` and `release` own external and publication boundaries.
   - `critique` owns fresh-eye review and its artifact validator, including
     cross-surface boundary checks.
   - Cite an owner's result; do not duplicate its validator or state record.
5. Report evidence and non-claims.
   - Give the exact command or input, observed result, and relevant proof
     level. State what remains unverified and which owner must provide it.

## References

- `references/verification-ladder.md`
- `references/review-gate.md`
