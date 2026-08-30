# Goal Run #744 Proof-Policy Amendment — Ignore Mutation Tests

Date: 2026-08-30
Status: operator-approved
Session: `goal-744-2026-08-30`

## Frozen Lineage Preserved

- Goal Draft:
  `charness-artifacts/goals/2026-08-30-close-current-open-issues-goal-run.md`
- Goal Draft SHA-256:
  `eec33587771e5f6abf0e06eb32b1291f475b5b549860c96f73f89218fda44e20`
- Goal Binding:
  `charness-artifacts/goals/2026-08-30-close-current-open-issues-goal-run.binding.json`
- Goal Binding SHA-256:
  `2b5ac12a3722897bc5a11e88a881b45784adcbaab5e84840629ccd1d57421eb8`
- Provider parent: `corca-ai/charness#744`

The frozen draft and binding remain byte-identical. This record is a sparse
post-establishment parent-contract change under `docs/goal-lifecycle.md`; it does
not rewrite the initial approved baseline.

## Operator Decision

The operator asked whether ignoring Mutation Tests would make this Goal faster
and explicitly approved doing so: “mutaion test 쪽을 무시하도록 이번 골을
가져가면 더 빨라질 것 같은데 맞나? 그렇다면 무시해도 됨”.

## Contract Delta

- Remove hosted Mutation Tests and mutation-score evidence from Goal #744's
  child-close and parent-close proof policy.
- Close #758 as `decision-needed` with reason `not planned`. Its closeout records
  the two failed hosted attempts and durable diagnosis, but claims no successful
  mutation execution, mutation score, or repair of the follow-up referent seam.
- A current successful Quality Core run remains required after the final material
  integration and before #744 closes. Ordinary focused/local checks remain
  proportionate to each Work Item.
- No other Work Item membership, identity, order, JTBD, or completion policy
  changes. All seventeen direct children still must be `CLOSED` before #744.
- No release is added.

## Why This Reduces Serial Cost

Each Mutation Tests attempt spent about 13 minutes in the standing baseline
before mutation could begin. Two attempts failed before mutation, and every
repair would require another hosted round. Removing that proof obligation cuts
the longest repeated serial loop without changing the composable Charness
capabilities delivered by the remaining Work Items.

## Evidence and Non-Claims

- First failed run: https://github.com/corca-ai/charness/actions/runs/33296181601
- Second failed run: https://github.com/corca-ai/charness/actions/runs/33297693085
- Durable diagnosis:
  `charness-artifacts/debug/2026-08-30-issue-758-mutation-workflow-standing-baseline-followup.md`
- Non-claims: neither run executed mutation; no mutation result or score is
  accepted as green; the diagnosed local-object/provider-history seam is not
  claimed repaired.

AI-provenance: Agent-authored amendment transcribing the operator's explicit
proof-policy decision; the frozen Goal Draft and Binding remain unchanged.
