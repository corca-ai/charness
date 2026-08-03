# Slice B semantic reviewer-question critique
Date: 2026-08-04

## Diff Scope

Add one portable semantic reviewer question, inject it into Charness's generated
critique packet, keep the checked-in plugin mirror synchronized, and record a
bounded worked application against the recorded #499 and #491 recurrence.

## Target

Code critique of a public-skill/reference and adapter contract slice. The
capability at stake is making a guard/reference/verdict-surface proposal name
the fact its reader or control needs, without replacing judgment with a new
semantic gate.

## Change

The shared question asks for semantic fact/invariant, owning boundary, recorded
instance, and axis-varying counterexample. It then requires a reviewer
comparison with the proposed control and records one of accept, reject/repair,
or `unproven — defer`. It explicitly permits `not applicable` and
`insufficient evidence`, keeps the decision human-owned, and rejects meta-gate
semantics. The Charness adapter inlines the canonical shared reference into
generated packets; the exact-content test protects that transport.

## Findings

- F1 | bin: act-before-ship then repaired | evidence: strong | ref: first-round fresh-eye review, `slice-b-semantic-question-application.md` | action: applied | note: delivery alone did not prove a recorded instance; added two concrete applications with proposed proxy controls and reject/repair outcomes.
- F2 | bin: act-before-ship then repaired | evidence: strong | ref: `tests/test_critique_prepare_packet.py` | action: applied | note: packet test now asserts exact source bytes and pins the decision boundary and its dispositions.
- F3 | bin: act-before-ship then repaired | evidence: strong | ref: `skills/shared/references/reviewer-packet-semantic-question.md` | action: applied | note: replaced packet-readiness wording with reviewer dispositions so the question cannot become a semantic meta-gate.
- F4 | bin: over-worry | evidence: strong | ref: `charness-artifacts/critique/slice-b-semantic-question-application.md:66-70` | action: defer | note: host rendering, reviewer uptake, and future efficacy are explicit non-claims, not missing local proof.
- F5 | bin: valid-but-defer | evidence: moderate | ref: final counterweight result | action: defer | note: later live review traffic is the right evidence for long-run efficacy; this slice proves bounded applicability only.

## Counterweight Triage

- Act Before Ship: persist this independent fresh-eye result and do not call the
  worked application proof of future reviewer efficacy.
- Bundle Anyway: none; the application already carries the concrete comparison
  and non-claims.
- Over-Worry: no semantic validator, `reference-claims` manifest, or extra
  host-rendering proof belongs in this slice.
- Valid but Defer: automatic applicability classification and long-run uptake
  measurement require later evidence and would add a new proxy surface now.

## Deliberately Not Doing

- No semantic meta-gate parses the four answers or declares them correct.
- No `reference-claims` manifest is introduced for #491.
- No claim is made that every host renders the section or that a reviewer will
  follow it.

## Pre-Merge Action

None. The final repair-read round found no implementation blocker; the minor
unasserted failed-section-render test is deferred because the renderer already
surfaces per-section errors and the changed control is the successful static
section path.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model `gpt-5.6-terra`, reasoning effort `medium`, service tier `priority`, fork turns `none`; no host addressing/name
- Host exposure state: requested_fields_sent
- Application state: host application not independently confirmed; no `applied` claim made
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — initial code critique used three named angle reviewers and a
separate counterweight; the repair-read round used the same four bounded scopes;
the final repaired-surface round returned three no-blocker angle findings and a
counterweight whose only condition was this independent evidence record. Every
window had a clean boundary fingerprint verified before parent writes.

## Packet Consumed

charness-artifacts/critique/slice-b-semantic-review-packet.md

## Reviewed Input Identity

- Packet Consumed: charness-artifacts/critique/slice-b-semantic-review-packet.json
- Packet path: charness-artifacts/critique/slice-b-semantic-review-packet.json
- Packet SHA256: 41c98ecd7389aa3e2fbf11a402ed1ec2e178a8ab38a418c37c5a44b864983e22
- Identity SHA256: 1d9b00ced77dba82d305e0b0aa0438596e23f972612cd4fd05c07067da7343ec
- Reviewer markdown consumed: charness-artifacts/critique/slice-b-semantic-review-packet.md; SHA256 cb941f268bb89e3a2738af3ebf8ecf167eb2983c9843047ed4aea2268c6b4eed

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` — guard at the easy-to-test
boundary instead of the boundary that breaks the invariant; shipped reference
claims that drift from the code.

## Boundary Ownership

- Producer: `skills/shared/references/reviewer-packet-semantic-question.md`
  produces the portable question; `.agents/critique-adapter.yaml` selects it
  for Charness packets.
- Consumer: the generated critique markdown packet and its bounded reviewer
  consume the question before judging the selected control.
- Owning surface: shared reference owns the wording; the adapter owns packet
  inclusion; plugin files are derived exports; the worked application owns only
  this slice's recorded applicability evidence.
- Verdict: owned-correctly — the control remains reviewer-owned and the static
  packet path fails visibly if its source cannot be read.
