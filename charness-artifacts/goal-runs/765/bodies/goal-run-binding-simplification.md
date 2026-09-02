## Situation

Establishing Goal Run #765 on 2026-09-02 through `achieve` and the issue-owned `goal-run-*` operations. The plan was approved, the binding frozen, seven children created and linked, and `/goal #765` pickup verified. The operator then asked to (a) note that one bullet of child #766 was already done, and (b) add one more Work Item and reorder the sequence.

## Experience

Neither request could be applied to the live Goal Run:

- Child bodies are bound by full-body SHA-256 (`body_policy: managed`), and `require_created_children` re-hashes every live child body on readback. Editing one sentence of #766 would make `/goal #765` refuse. The only available move was a comment.
- `add-child` accepts only keys present in the immutable binding (`work_item_for_target`), and pickup rejects a `progress.next` whose key is not a binding key. `issue_goal_run_parent_amendment.py` authorises human-body edits of the parent only and keeps metadata immutable. `references/coordination.md` says an in-scope Work Item may be added "through the provider's explicit graph-amendment operation", but no such operation exists.
- During bootstrap itself, four refusals came from format rules that add no observation: `binding_path` required on every operation although the parent metadata already names it; parent metadata must be appended to the exact live body bytes (refused twice); `current_membership_sha256` is produced by no script and only checked for equality with `progress.membership_sha256`.

## Evidence

- `skills/public/issue/scripts/issue_goal_run_binding.py` `validate_managed_body`, `require_created_children`, `work_item_for_target`.
- `skills/public/issue/scripts/issue_goal_run_parent_amendment.py` `validate_parent_body_update` ("Keep metadata immutable while authorizing explicit human-body changes").
- `skills/public/achieve/scripts/goal_run_pickup_contract.py` `_validate_progress_next` ("progress.next is not an approved Work Item").
- `skills/public/achieve/references/coordination.md` "Off-goal findings" paragraph.
- Bootstrap record: `charness-artifacts/goal-runs/765/operations/*.out.yaml` (refusals), #766 comment 5503708077.
- Resolution: #765 and its children were closed as superseded and the Goal Run re-established with this issue included. The rework was one full re-bootstrap.

## Impact

The binding conflates identity (which issue is which Work Item, which plan was approved) with content (the prose of a child, the exact bytes of the parent body). Content edits are reversible and visible in GitHub edit history, so hashing them buys no new observation channel while making every routine correction a re-bootstrap. By the north star this is a P1 failure (rulebook where judgment suffices) and a taste failure (features beyond the capability needed). The genuine irreversible boundary, closing the parent on aggregate proof, is guarded by `goal-run-close` readback and does not depend on any of the content hashes.

## Weak direction (non-binding)

Keep: the draft hash at approval, the `charness-work-item-key` marker as child identity, the sub-issue graph as membership, `goal-run-close` readback. Drop: per-child full-body hashes (or reduce to marker presence), `current_membership_sha256`, the byte-exact parent-append rule (require one metadata block and an unchanged human body instead), and `binding_path` repetition on operations. Add: a real graph-amendment operation that appends a Work Item under operator approval and records the amendment in the parent, so coordination.md's promise is true.

Causing skill: achieve, issue (goal-run provider operations).

AI provenance: filed by an AI agent on the operator's instruction from a live rework instance.

---

## Work Item (Goal Run #765, added by amendment on 2026-09-02)

<!-- charness-work-item-key: goal-run-binding-simplification -->

### Owned scope

The first cut landed in the establishing session and is what let this issue join #765 without a re-bootstrap: child identity by marker only, `current_membership_sha256` dropped, the parent-append rule relaxed to "add the block, keep the human body", an amended draft reported instead of refused, and `amendments` in parent metadata with `add-child --amendment`. This Work Item finishes the class:

- Remove `binding_path`, `draft_sha256`, and `binding_sha256` repetition from operation files; read them from the parent metadata.
- Retire `body_sha256` from the binding's Work Item schema (or make it optional), and the `managed`/`managed-addendum` body policies that only existed to hash prose.
- Make `charness task`/`prove`/`retro` lineage checks consume `amendments` where they read the Work Item set.
- Update `references/lifecycle-before.md`, `lifecycle-during.md`, and the issue skill's goal-run reference to the identity-not-content rule; delete prose that still promises byte-exact binding.
- Seed the re-establishment case as a test: amend a live run, correct a child's prose, reorder the cursor, and prove `/goal #N` still refuses a swapped draft path, an unapproved child, or a closed cursor.

### Acceptance

- No goal-run operation refuses on content bytes; every refusal names an identity (parent, binding hash, draft path, marker, cursor) or a closed state.
- `tests/quality_gates/test_issue_goal_run*.py` and `test_achieve_goal_run_pickup.py` pass with the seeded amendment case.

### Dependencies

rework-instrument (label this issue `rework` once the label exists).
