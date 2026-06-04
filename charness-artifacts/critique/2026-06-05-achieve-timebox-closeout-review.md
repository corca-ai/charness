# Critique: Achieve Timebox Closeout Review

Execution: parent-delegated fresh-eye review, medium effort.

Fresh-Eye Satisfaction: parent-delegated.

Packet Consumed: n/a (bounded working-tree diff packet in parent prompt).

Target: code-critique.

## Reviewer Tier Evidence

- Requested tier: medium
- Requested spawn fields: agent_type=explorer, reasoning_effort=medium
- Host exposure state: metadata-hidden
- Application state: requested-fields-sent; host did not expose provider application confirmation

Change: add an `achieve` timebox mode contract and deterministic closeout gate so fixed-duration goals keep working until the closeout reserve unless the artifact records a falsifiable reason to stop.

Findings:

- Act Before Ship: `Closeout reserve >= Timebox` made the closeout window start before activation, allowing immediate completion for short timeboxes. Fixed by rejecting reserves that are not shorter than the timebox and adding `test_check_timebox_rejects_reserve_not_shorter_than_timebox`.
- Act Before Ship: early-close evidence was accepted from the full artifact, so a planned `Stop condition:` outside closeout could satisfy the gate. Fixed by scoping early-close evidence to `## Final Verification` and adding `test_check_timebox_ignores_planned_stop_condition_outside_final_verification`.
- Bundle Anyway: duration parsing accepted annotated strings such as `3h (180m)` and silently summed both fragments. Fixed by requiring a strict duration grammar and adding `test_check_timebox_rejects_annotated_duration`.

Counterweight Triage:

- The first two findings were real blockers because they bypassed the user's time-budget intent.
- The duration parser finding was smaller but cheap to fix in the same module and reduced future ambiguity.
- No additional Cautilus run was required: the planner reported `next_action: none`, and deterministic validators plus dogfood scenario review cover the changed consumer contract.

Deliberately Not Doing:

- No new maintained Cautilus scenario was added because routing, draft artifact creation, and inert-until-activation behavior are unchanged.
- No attempt was made to classify whether the closeout rationale is substantively good; the gate only proves a falsifiable line exists in the closeout section.

Next Move: ship with the fixed validator, mirrored plugin export, updated dogfood review, and full slice closeout gate.
