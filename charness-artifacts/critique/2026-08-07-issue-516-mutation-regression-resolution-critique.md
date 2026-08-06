# Issue #516 mutation regression resolution critique
Date: 2026-08-07

## Decision Under Review

Resolve #516 by carrying the confirmed historical publish-state mismatch into
the diagnosis and correcting the machine-local absolute packet path that made
the current remote mutation mirror fail at `5df4fb61…`. Closeout is allowed
only after a new remote run proves the repaired artifact in a runner checkout.

## Failure Angles

- Problem framing: the historical alert and the current remote failure are two
  distinct observations; collapsing them into “27 local tests pass” would hide
  the actual repair boundary.
- Diagnosis/boundary ownership: the bad current value is authored by the
  critique artifact, while the validator correctly owns repo containment; the
  fix must stay at the artifact field and must not weaken validation.
- Operations: the failed remote run must be recorded as terminal, local proof
  must be rerun after the path edit, and a post-repair remote run must precede
  any direct-commit closeout.

## Counterweight Pass

- Act before ship: record `source_claim_mismatch` at
  `sources.handoff.claim`, record Quality Core run `31115253605` as failed on
  its absolute packet path, and wait for a new remote mutation result.
- Bundle anyway: keep the repo-relative path correction, debug artifact,
  handoff/goal synchronization, and issue carrier in one closeout slice.
- Over-worry: a local historical checkout of `79ea3447…` is not required for
  diagnosis because the original GitHub log and historical source comparison
  directly identify the mismatch.
- Valid but defer: dependency equivalence, provider behavior, cross-host
  behavior, and a mutation workflow redesign remain unproven or out of scope.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: run 31103691239; `sources.handoff.claim` | action: fix | note: record the confirmed historical mismatch between handoff `7eed13ec…` and goal/manifest `e7c3e1b3…`.
- F2 | bin: act-before-ship | evidence: strong | ref: run 31115253605; critique artifact Packet path | action: fix | note: replace the machine-local absolute packet path with a repo-relative path while retaining fail-closed validator containment.
- F3 | bin: act-before-ship | evidence: strong | ref: GitHub Actions run 31115253605 | action: document | note: do not close until a new remote run proves the committed repair; local 775-artifact validation is not runner proof.
- F4 | bin: valid-but-defer | evidence: moderate | ref: historical runner environment | action: defer | note: do not replay the old checkout unless a later remote discrepancy requires environment diagnosis.

## Reviewer Tier Evidence

- Requested tier: `gpt-5.6-terra`, medium reasoning, priority service tier.
- Requested spawn fields: unnamed one-shot bounded reviewers; `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`, `fork_context=false`.
- Host exposure state: requested_fields_sent
- Application state: host-confirmed: three unnamed angle agents and one separate counterweight agent were accepted and returned findings; provider-side model application is not independently exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — three distinct unnamed angle reviewers, a separate counterweight
reviewer, and clean boundary fingerprints for both rounds; no same-agent
substitute was used.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-06-154530-packet.md`
- Packet path: `charness-artifacts/critique/2026-08-06-154530-packet.json`
- Packet SHA256: `0f16d211f5342a0ed375360689be62f4335d3c808bc2510dec927c74fb9f467f`
- Identity SHA256: `01ec4f14053dd5b90a3789e535d150baffb11429470f10b9b576c859af2b3456`

## Boundary Ownership

- Producer: the durable critique artifact's `Packet path` field.
- Consumer: `scripts/validate_critique_artifacts.py`, the whole-tree critique
  corpus test, and the remote changed-line mutation mirror.
- Owning surface: the critique artifact field; the validator remains the
  fail-closed consumer of repo containment and packet identity.
- Verdict: owned-correctly.

## Deliberately Not Doing

- No weakening of `verify_packet_binding` or repo-containment validation.
- No historical local checkout, provider/browser roundtrip, Cautilus run,
  cross-host claim, or mutation workflow redesign.
- No #516 closeout until the new commit receives a distinct remote mutation
  readback.

## Next Move

Commit the repo-relative path and synchronized evidence records, run the local
artifact and mutation gates, push only through the conditioned pre-push gate,
read back the new Quality Core result, and then bind the direct-commit closeout
carrier to the distinct behavior proof and GitHub state readback.
