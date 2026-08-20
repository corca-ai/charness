# Critique Round Findings

- Round: 1
- Recorded date: 2026-08-21
- Boundary window id: `consumer-validator-round-1`
- Boundary snapshot: `.charness/reviewer-boundary/2026-08-21-round1-after.json`
- Boundary snapshot SHA-256: `a2cd82e98f1bb77539f9ba5e7695d42854d6468cbdd529059b65083196b2ed93`
- Findings SHA-256: `781c431c0dc5391f062321e2818c1619e5d731a3253a6c47a24a167bcceeefc0`

## Findings Returned

Verdict: BLOCK.

Blockers returned by the round-1 fresh-eye reviewer:

1. scripts/capability_catalog.py did not require the adoption declaration from the CLI path; a missing declaration could be reported as not_configured and still return zero.
2. The adoption declaration was untracked and the inventory/readback omitted consumer purpose, artifact type, exact invocation, adoption policy, and opt-out reason.

Risks and non-claims:

- The reviewer also flagged the installed-layout default risk, declaration-shape versus runtime-wiring non-claim, stale goal counts, and the need for focused/staged/export proof.
- The reviewer explored two wrong invocations: a doubled plugin path from the source checkout and a source-layout repo-root passed to the exported checker. These are invocation/path smells, not successful product calls.
- No pre-review boundary fingerprint was captured for round 1. The supplied snapshot is post-delivery only; boundary integrity is therefore unproven and this record must not be read as a clean boundary approval.
- The parent repaired the required-adoption CLI contract, detailed readback, installed/source layout defaults, staged-adoption check, surface ownership, and focused tests after this review.
