# Resolution Critique — issue #491 (semantic reference drift)

Date: 2026-08-05
Repo: corca-ai/charness

## Decision under review

Keep cross-file semantic-reference checking as a reviewer-owned question, not a
universal `reference-claims` manifest, literal-set matcher, or semantic
meta-gate. Repair the concrete reader-facing references found by the issue and
record the current quality-bootstrap contract rather than reviving the
pre-#507 `refilled_subkeys` report claim.

## Packet binding

- Packet: `charness-artifacts/critique/2026-08-05-issue-491-decision-packet.md`
- Packet SHA-256: `69c1496e746dcdb43b7f60f0ed00efb2621b62db204c2f14acc400f49331e580`
- Reviewed-input identity SHA-256:
  `be309552caab5fb59d1d316b76ceb2cf4fa4a2fcbb7844cba2b4df6d9d6d9860`
- Binding includes the repaired source/plugin references, helper scripts, and
  `tests/quality_gates/test_achieve_before_activation.py`.

## Fresh-eye execution

- Round 1: four unnamed bounded reviewers covering problem framing, diagnostic
  quality, first-reader behavior, and counterweight. All returned findings.
- Round-1 boundary verification: clean for
  `issue-491-resolution-20260805`.
- Round 2: four unnamed bounded reviewers read the repaired goal-artifact
  example and semantic question. Three approved; the counterweight found two
  additional real contradictions and required repairs.
- Round-2 boundary verification: clean for
  `issue-491-repaired-20260805` before parent edits.
- Round-2 repairs are recorded as accepted-unreviewed under the two-round cap:
  the slug-coercion references/helper comments and the bounded candidate-search
  wording were repaired after that round's finding. Focused tests and parity
  checks provide the post-repair verification; no third reviewer round is
  claimed.
- Fresh-Eye Satisfaction: parent-delegated.

## Reviewer Tier Evidence

- requested tier: high-leverage
- requested spawn fields: model `gpt-5.6-terra`, reasoning_effort `medium`,
  service_tier `priority`, fork_context `false`
- host exposure state: requested_fields_sent
- application state: all four reviewers accepted the requested fields and
  completed the assigned read-only scope; no provider-side model confirmation
  was exposed.
- Delivery state: findings-received

## Findings and dispositions

1. **Act Before Ship — repaired**: the copy-paste `append_slice_log.py`
   example used lossy prose flags after the surrounding text required
   `--fields-file`. The source and plugin examples now use a quoted JSON
   heredoc and `--fields-file`; the focused test rejects the old prose flags.
2. **Act Before Ship — repaired, accepted-unreviewed**: `goal-artifact.md` and
   `lifecycle-during.md` claimed a slug was rejected unless already kebab-case,
   while `resolve_supplied_slug` coerces usable input and rejects only total
   loss. Both source/plugin references and `upsert_goal.py` comments now state
   the actual boundary.
3. **Act Before Ship — repaired, accepted-unreviewed**: the added first-reader
   rule could be read as applying to every behavior-changing internal helper.
   It now requires a bounded candidate search and applies the reader check when
   a reader-facing or copy-paste reference is in scope; otherwise it records
   `not applicable` with scope.
4. **Bundle Anyway**: carry a three-row claim ledger in the issue carrier for
   lifecycle readiness, current bootstrap status semantics, and the safe slice
   invocation. This prevents the generic reviewer question from standing in
   for readback of the three recorded escapes.
5. **Bundle Anyway**: distinguish helper behavior proof from reference proof.
   The helper input-channel tests prove `--fields-file` preserves prose; the
   reference test proves only that the demonstrated command selects that safe
   channel and that source/plugin copies match.
6. **Over-Worry**: no universal manifest or full-corpus literal matcher is
   justified by three heterogeneous claim families without a stable mapping.
   The focused test's local literals are intentionally narrow and are not a
   universal semantic control.
7. **Valid but defer**: revisit mechanical coupling only after a recurrence
   establishes a stable owner-to-reference mapping and a measured false-fire
   cost. Reviewer uptake and host rendering remain unproven.

## Historical/current distinction

The issue's `refilled_subkeys` wording describes the pre-#507 lifecycle report.
The current public report exposes current conflict/migration fields instead;
private `_subkey_refills` remains internal merge evidence. Adding the old key to
`bootstrap-posture.md` would create a new false claim, so the carrier must name
the supersession rather than pretend that historical wording is current.

## Boundary Ownership

- Producer: each behavior owner (`pursue_readiness`, current bootstrap
  lifecycle, and `append_slice_log.py`) plus its reader-facing reference.
- Consumer: the first agent/operator reading the reference or copying its
  command, and the reviewer packet evaluating the semantic claim.
- Owning control: the shared semantic reviewer question and the narrow
  source/plugin regression assertions; not a repository-wide manifest.
- Verdict: owned-correctly

## Non-claims

This review does not prove every shipped reference is synchronized, reviewer
uptake, host rendering, installed-machine behavior, or end-to-end execution of
the Markdown snippet. It proves the three recorded #491 instances were
read back within a bounded candidate scope and that the repaired local surfaces
are parity-checked.

## Recommended closeout

Close #491 as `decision-needed` with the reviewer-owned decision, the three-row
claim/readback ledger, the post-#507 historical distinction, the focused proof,
and a distinct `Behavior #491:` reader/reference verdict. Do not add a new
universal semantic gate.

AI-provenance: agent-drafted carrier and critique; bounded reviewer findings
were delegated under the repository's standing fresh-eye contract.
