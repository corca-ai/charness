<!-- charness-work-item-key: remote-truth-reconciliation -->

## Objective

Establish the approved Goal Run parent and reconcile remote issue state so GitHub reflects only live Work Items.

## Owned scope

Create one parent with exactly these ten children: existing #735, #730, #728, #705, plus the six approved new Work Items. Close #732, #729, #711, #702, #688, #612, #599, #584, #583, and #582 with concise absorbed, obsolete, policy, or consolidated reasons. Keep #731 and #709 independent.

## Acceptance

- Parent and all ten child relationships are created and read back.
- Each close target is freshly read with comments immediately before closure.
- Closed states and reasons are read back.
- The resulting open set contains only the parent's ten children plus independent P2 issues #731 and #709.

## Focused verification

Use Issue-owned preflight and provider readback for every relationship and closure. Do not perform a full routine issue-graph scan.

## Dependencies

None. This is the first Work Item.

## Non-claims

Do not implement any child work, close #731 or #709, push, tag, release, run remote CI, or mutate installed hosts.
