# Issue 298 Handoff And Publication Closeout Critique

## Execution

Fresh-eye code critique ran before the direct-commit closeout for issue #298.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `requested_fields_sent`
- **Application state**: `fields accepted by spawn call; provider application not independently confirmed`

## Packet Consumed

charness-artifacts/critique/2026-06-04-issue-298-closeout-packet.md

## Target

Code critique

## Diff Scope

The handoff chunker now reports merge policy facts without clearance semantics,
and issue, achieve, and retro guidance now separate issue-resolution carrier
publication from later lifecycle/audit artifact publication.

## Change

Success means `broad_only_overlap: false` never reads as safe-to-merge
clearance, unknown boundary tokens read as policy-no-opinion, malformed agent
output returns validation diagnostics instead of crashing, and post-carrier
lifecycle artifacts do not force a second issue-closeout push after verified
carrier publication.

## Angles

- Problem framing: checked whether the diff solves both #298a and #298b instead
  of renaming the old confidence signal.
- Diagnostic: checked whether validation remains a facts floor and not a
  brittle oracle around malformed agent output.
- Operational checklist: checked whether operator-facing references and tests
  make the facts-only contract visible at the package stage.

## Findings

- Act Before Ship: all three reviewers found that malformed
  `basis_boundary_tokens` could crash `validate_chunk_proposal_response` because
  `merge_policy_fact` used raw list values for set/sort operations after the
  validator had already recorded a non-string-list issue. Folded fix:
  `chunked_routing_agentic_facts.py` filters basis tokens to strings, and
  `test_validate_malformed_basis_tokens_reports_instead_of_crashing` proves the
  report returns `ok: false` with merge facts instead of raising.
- Bundle Anyway: the operator references now name that merge policy facts are
  diagnostic only; no broad-only warning is not merge clearance, and unknown
  basis tokens mean policy has no opinion.
- Over-worry: a full executable publication classifier is outside #298. The
  current slice fixes the closeout guidance and deterministic facts contract.
- Valid but defer: `chunked_routing_agentic.py` remains in the advisory length
  warn band, and a publication classifier could become useful if the contract
  expands.

## Counterweight Triage

- Act Before Ship: none remaining after the mixed/non-string token crash fix and
  regression test.
- Bundle Anyway: already bundled the reference wording and malformed-token
  regression.
- Over-Worry: do not require a full executable carrier-vs-lifecycle classifier
  for this closeout.
- Valid but Defer: monitor the handoff agentic script length and publication
  classifier need in later slices.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_agentic_facts.py | action: fix | note: filter basis tokens to strings before facts calculation so malformed agent output reports instead of crashing
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/handoff/references/chunked-routing.md | action: fix | note: document merge policy facts as diagnostic only, not clearance
- F3 | bin: over-worry | evidence: moderate | ref: https://github.com/corca-ai/charness/issues/298 | action: document | note: executable publication classifier is outside this issue's closeout scope
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/public/handoff/scripts/chunked_routing_agentic.py | action: defer | note: script remains below the hard length limit but in the advisory warn band

## Deliberately Not Doing

This slice does not hardcode Ceal label semantics, add a publication classifier,
or treat script output as semantic merge judgment. The script gives facts; the
agent still judges semantic fit, urgency, dependency, and operator value.

## Next Move

Proceed with direct commit for #298 after closeout draft validation and final
goal artifact update.
