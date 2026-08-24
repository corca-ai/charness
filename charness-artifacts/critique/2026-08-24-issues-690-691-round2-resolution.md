# Issues #690/#691 Round-2 Resolution Critique

Date: 2026-08-24

## Reviewed Input

- Round-2 packet: `charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-packet.json`
- Packet SHA-256: `42c3a1e05e2eb370dcd49d25ead640579befbae6e5b7f2c4577211be5a06779a`
- Declared reviewed identity: `bacbbf3af760b74f7b74b94820362649b93c0ada1ad44c6560996841df38e6e0`
- Fresh-eye satisfaction: `parent-delegated`, read-only; boundary fingerprint verified clean.
- Round-2 focused proof: 131 tests passed; Ruff, packaging, and packet verification passed.

## Round-2 Verdict

`FAIL / repair required`. The two-round proof-surface cap is consumed.

The reviewer found that readiness reduced H2 headings to a set and therefore
accepted substantive duplicate `Goal`/portability sections that full validation
rejected. The reviewer also proved that the packet's `changed_ref: HEAD` bound
the old committed substrate rather than the uncommitted repaired worktree. The
remaining length advisory identified Closeout Binding Plan parsing as a concrete
separable concept.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model `gpt-5.6-luna`, reasoning effort `xhigh`, fork
  turns `none`; the host-required task identifier was supplied for result retrieval.
- Host exposure state: requested_fields_sent
- Application state: the spawn API accepted the requested fields; no independent
  runtime signal proves the effective model or effort.
- Delivery state: findings-received.

## Accepted-Unreviewed Cap Repair

- Readiness now consumes the canonical markdown duplicate-section report and
  emits a typed `duplicate_sections` blocker.
- Source/plugin full validation and pursue readiness reject substantive duplicate
  `Goal` and `Context Sources` fixtures with matching results.
- Two legacy control fixtures that accidentally contained duplicate required
  headings were corrected; they were invalid controls exposed by the new guard,
  not product regressions.
- Focused proof after repair: 165 tests passed, with compilation, Ruff,
  packaging, direct source/plugin byte parity, debug validation, length gate,
  and diff hygiene executed.
- These repairs are accepted-unreviewed under the two-round cap. No third review
  is claimed.

## Corrected Identity Binding

The old round-2 packet is retained as failure evidence and is not closeout proof.
The cap repair is bound by a working-tree packet with `changed_ref: null`:

- Packet: `charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-cap-final-packet.json`
- Packet SHA-256: `8a515e21a8bd253cea5fd58d1f7e592f1937b537bcf422d4d61e1b72b8f5eb2d`
- Reviewed identity: `6847d3f037c964d646ba8a3934592c6c22d9986ba84730101ac51efd141d47f7`
- Verifier result: `ok: true`, `status: current`.

## Structural Follow-ups

- #717 tracks cohesive extraction of the Closeout Binding Plan floor. The cap
  repair left `goal_artifact_pursue.py` at 355 code lines and
  `goal_artifact_lib.py` at 359, both in the advisory band; no line shaving is
  accepted as resolution.
- #718 tracks the prepare-packet substrate mismatch that allowed a historical
  `HEAD` identity to verify as current while reviewed worktree paths differed.

## Post-Merge Standing-Suite Repair

Fresh base-to-HEAD coverage collection ran the full standing suite and exposed
two legacy backlog fixtures that built `User Acceptance` twice: once explicitly
and once through `REQUIRED_SECTIONS`. The focused readiness suite had not owned
those dependent controls. Production correctly refused the duplicate H2; the
fixtures now share one `_complete_shaping_body` builder that renders every
required/portability section exactly once and preserves the valid acceptance
sentence. The backlog file passes 17 tests and Ruff. This test-only repair is
accepted-unreviewed under the already-consumed round cap; no new semantic review
or production approval is claimed.

## Boundary Ownership

- Producer: canonical goal Markdown parsing plus lifecycle/readiness composition.
- Consumer: `check_goal_artifact.py --pursue-ready` and full goal validation.
- Owner: markdown owns H2 duplicate facts; lifecycle owns terminal state;
  `goal_artifact_pursue.py` composes their typed readiness blockers.
- Verdict: owned-correctly

The accepted-unreviewed duplicate repair moved no parser semantics into the CLI;
the CLI renders the shared producer's typed result.

## Non-Claims

- The length advisory is not claimed resolved.
- The old `changed_ref: HEAD` packet is not claimed to bind the repaired worktree.
- No issue was closed or commented on, and no push, release, PR, tag, version
  bump, or Cautilus run occurred.
