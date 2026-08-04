# Slice E #496 hollow-refill semantic repair critique
Date: 2026-08-04

## Execution

Parent-delegated before-implementation critique with three bounded code angles
(Jackson problem framing, Weinberg boundary diagnosis, Gawande operations) and
one separate counterweight, followed by the required second bounded review of
the repaired verdict surface. The implementation is now present: a narrow
mutation-command inert-leaf filter plus a safe nested warning remedy, with
generated source/plugin parity and end-to-end tests.

## Decision Under Review

Whether the smallest honest #496 repair is to suppress only omitted
`mutation_testing.commands.dry_run` and `.sample` leaves whose defaults are
empty strings, retain meaningful empty scope defaults, and replace the generic
nested warning's whole-block deletion advice with leaf-level review guidance.
Success means the exact issue fixture keeps real `full`/`summary` commands,
does not report the hollow leaves, and never recommends discarding the block;
#493's non-inert nested reporting remains unchanged.

## Diff Scope

Implemented in `scripts/quality_bootstrap_lib.py`,
`scripts/quality_bootstrap_absence.py`, their generated plugin mirrors, and
focused quality tests. The gathered issue, debug record, goal, and refreshed
packet bind the semantic invariant and axis-varying counterexample.

## Failure Angles

- Jackson: a generic empty-value filter would solve a convenient syntax rather
  than the named #496 harm and could hide non-inert empty policy settings.
- Weinberg: the merge helper has no policy-path context; the semantic exception
  must be scoped at the mutation boundary, while the destructive remedy belongs
  to `describe_intent_loss`.
- Gawande: the exact bootstrap consumer must prove real commands survive,
  fresh adapters stay silent, and source/plugin execution remains aligned.

## Counterweight Pass

- Act Before Ship: use an exact path/value allowlist for only the two inert
  command leaves; repair the nested remedy; add the end-to-end and axis-varying
  tests.
- Bundle Anyway: retain explicit-empty controls, #493 report-path coverage,
  fresh-bootstrap silence, and plugin/source parity in the same focused proof.
- Over-Worry: do not build a generic semantic-emptiness framework, change
  top-level symmetry, or infer future command consumers.
- Valid but Defer: sub-key `deliberately_absent` syntax is a separate contract
  decision; the safer warning is enough for this issue.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/quality_policy_merge.py:27 | action: fix | note: scope inert suppression to exact mutation command leaf paths and the empty-string default, never the generic recursive helper.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/quality_bootstrap_absence.py:176 | action: fix | note: nested refill warnings must not tell operators to drop a whole block containing real configuration.
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_bootstrap_absence.py:843 | action: fix | note: add exact end-to-end #496 proof plus partial report-path and prompt-asset empty-scope controls.
- F4 | bin: bundle-anyway | evidence: strong | ref: skills/shared/references/reviewer-packet-semantic-question.md | action: fix | note: retain an axis-varying counterexample so empty Python shape does not become the semantic predicate.
- F5 | bin: over-worry | evidence: moderate | ref: charness-artifacts/gather/2026-08-04-issue-496-hollow-refill.md | action: defer | note: generic empty-string/list/map semantics and top-level symmetry exceed the recorded issue evidence.
- F6 | bin: valid-but-defer | evidence: weak | ref: scripts/quality_bootstrap_absence.py:184 | action: defer | note: sub-key deliberate absence is a real future contract but not needed to stop this harmful remedy.
- F7 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_bootstrap_absence.py:953 | action: fix | note: round-2 review required the source/plugin fixture to compare the complete parsed payload, not only selected JSON keys; the test now does so and retains stderr parity.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: unverified — host returned findings but exposed no provider-application confirmation
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — Jackson, Weinberg, Gawande, and a separate counterweight
returned the pre-implementation findings; all four reviewer boundary windows
verified clean before parent writes. The required second repaired-surface round
was also parent-delegated: Chandrasekhar returned one proof blocker, the parent
verified its boundary window clean, and the complete-payload assertion was
folded as a cap-limited round-2 repair accepted-unreviewed (no third round).

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-04-slice-e-496-hollow-refill-packet.md
- Packet path: charness-artifacts/critique/2026-08-04-slice-e-496-hollow-refill-packet.json
- Packet SHA256: 4b561dc83243e68782e43ef2893fad90c2bae37e1272abb5a03a411cb92c208b
- Identity SHA256: 86c7d22a4a64773a6d52bfaa3a88b0af516ed617528579f3a15aa2e585d6fe75

## Boundary Ownership

- Producer: `refilled_policy_subkeys` derives nested refill names and
  `quality_bootstrap_lib` carries them into the report; `describe_intent_loss`
  renders the operator warning.
- Consumer: the quality maintainer/operator reading the bootstrap JSON/stderr
  and the rewritten adapter.
- Owning surface: quality policy merge/report contract, with the warning
  renderer owning the remediation wording.
- Verdict: owned-correctly

## Defect Class Cross-Link

The recurring proxy-to-semantic-invariant trap is recorded in
`charness-artifacts/retro/recent-lessons.md`; this slice applies its rule to a
field-aware predicate and axis-varying counterexample.

## Pre-Merge Action

F1–F4 are implemented and locally proven. The generic helper remains reusable;
the exception is applied at the mutation policy boundary. Focused proof covers
omitted versus explicit-empty command leaves, missing summary (with `full`
outside the allowlist), non-inert report paths, meaningful empty exemption
scope, fresh bootstrap silence, complete source/plugin payload and stderr parity,
and warning wording. Round-2's only blocker was the selected-key parity gap;
the repaired assertion is accepted-unreviewed under the two-round cap.

## Deliberately Not Doing

No generic semantic-emptiness abstraction, no top-level policy symmetry change,
no sub-key deliberate-absence vocabulary, no #503-derived behavior, and no
remote issue closure or release action.
