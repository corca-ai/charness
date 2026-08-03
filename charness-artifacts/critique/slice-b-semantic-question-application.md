# Slice B Semantic Question Application

Date: 2026-08-04

This is the worked application for the reviewer-question control selected in
Slice A.
The source observations are the gathered issue record at
`charness-artifacts/gather/2026-08-04-goal-issue-sources.md:23-33` and the
primary issue bodies linked there. This records applicability, not a claim that
the reviewer question will catch every future instance.

## Recorded Instance: #499

- **Semantic fact or invariant:** value and outcome validation must hold
  regardless of how the value arrived; the guard must describe the protected
  value or structure, not the transport or failure spelling.
- **Owning boundary:** the value/outcome boundary in the changed helper or
  verdict surface; `_load_fields_file` owns transport only and cannot own a
  property that also applies to list-argv callers.
- **Recorded instance:** the issue's first row put guards inside
  `_load_fields_file`, so the documented-safe list-argv channel could write a
  forged heading at exit 0. Its other rows used `isinstance(merged_sub, dict)`,
  `merged_sub != default`, a cycle marker, and a wrong-shape error spelling;
  the issue records the outcome/structure as the actual boundary.
- **Axis-varying counterexample:** keep the malformed value or wrong outcome,
  but change only the transport (fields file to safe list argv), the value
  (`{}` versus a block carrying defaults), or the failure path (cycle swallowed
  versus sibling import error). A proxy predicate changes its answer while the
  protected invariant does not.
- **Proposed control under test:** guard only `_load_fields_file`,
  `isinstance(merged_sub, dict)`, `merged_sub != default`, a cycle marker, or a
  wrong-shape spelling.
- **Comparison and reviewer disposition:** the counterexample changes the
  observed form while the protected value/outcome does not, so the proposed
  proxy changes its verdict without a changed invariant. Reject/repair it and
  ask for the value or outcome predicate. This is a concrete reviewer refusal,
  not a clean-tree assertion.

## Recorded Instance: #491

- **Semantic fact or invariant:** every shipped reference that claims behavior
  must describe the current behavior and the executable path its reader will
  reuse.
- **Owning boundary:** the source/reference boundary, with the reference that
  carries the claim or copy-paste command named as the reader-facing owner.
- **Recorded instance:** Slice A changed `pursue_readiness` so fence balance was
  checked and removed it from `scope_not_checked`, but
  `lifecycle-before.md` still made the old claim. Slice D added `--fields-file`
  to `append_slice_log.py`, while `goal-artifact.md` still exposed the old
  flag-only invocation. The issue records both as shipped mismatches caught by
  bounded review rather than a gate.
- **Axis-varying counterexample:** update the implementation and two nearby
  references while leaving the copy-paste reference untouched, or change the
  status vocabulary while leaving one enumerated list old. Local docs look
  coherent, but the reader-facing owner still emits a false claim or unsafe
  command.
- **Proposed control under test:** update the implementation and two nearby
  references, then treat the reference set as aligned without checking the
  reader-facing copy-paste owner.
- **Comparison and reviewer disposition:** the implementation and nearby docs
  can remain locally coherent while the owning reference still emits the old
  claim or command. Reject/repair the incomplete alignment and name the owning
  reference. This catches the review-owned shape selected for #491 without a
  `reference-claims` manifest or semantic meta-gate.

## Non-Claims

- This application does not prove host rendering, reviewer uptake, or future
  efficacy. It proves that the generated packet's question can be answered
  against two recorded instances with distinct proxy axes.

## Fresh-Eye Satisfaction

parent-delegated — the final bounded angle reviewers and separate counterweight
read this application through the Slice B packet; clean boundary fingerprints
were verified before the parent wrote the critique record.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model `gpt-5.6-terra`, reasoning effort `medium`, service tier `priority`, fork turns `none`
- Host exposure state: requested_fields_sent
- Application state: host application not independently confirmed; no `applied` claim made
- Delivery state: findings-received

## Boundary Ownership

- Producer: the gathered issue record and the primary issue bodies produce the
  observed instances; this artifact records their bounded application.
- Consumer: the reviewer packet and bounded reviewer consume the four-part
  question and its proposed-control comparison.
- Owning surface: the shared semantic-question reference owns the prompt; this
  artifact owns only the Slice B worked application.
- Verdict: owned-correctly — the application is evidence of answerability, not
  an automated semantic verdict or a claim about future uptake.
