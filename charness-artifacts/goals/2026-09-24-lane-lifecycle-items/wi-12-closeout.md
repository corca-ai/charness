# WI-12: guarded close of 837-843 with readback

Goal #844 slice 14 of 14. Integration gates on all prior slices; closes only what landed.

## Objective

Close #837-#843 if and only if their mapped slices landed, verified through provider readback: WI-1..WI-7 map to #840, #838, #837, #843-1..3, #843-4..7, #842, #839 plus #843-12; WI-8a maps to #841; WI-8b maps to #843-8,9; WI-9 maps to #843-10,11; WI-10a/WI-10b map to #843-13,14; WI-11 maps to #843-15..18. Anything unlanded stays open with a recorded reason. Produce the goal completion proof.

## Touchpoints

- No `scripts/`, `tests/`, or `docs/` edits (verification plus provider operations only).
- All provider mutations through the `issue` skill's Goal Run operations; exact readback decides completion.
- Evidence: dated records under `charness-artifacts/`, `check-docs.sh`, standing pytest, plugin-mirror export, one read-only lane per the goal verification plan.

## Acceptance

- Each of #837-#843 is closed iff its mapped slice landed and read back closed; anything unlanded stays open with reason.
- No slice reintroduced relaunch-where-resume-applies (#831/#834 stay fixed).
- `skills/public/` untouched by hand; no direct `gh` writes; no release, version, or push actions.

## Out of scope

No code changes of any kind; no reopening of #814-#836; no broad lanes before the single read-only verification lane; no docs edits (those rode in touching slices).

<!-- charness-work-item-key: wi-12-closeout -->
