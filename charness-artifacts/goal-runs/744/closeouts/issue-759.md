Classification: bug

Jtbd: A range- or commit-bound critique must remain reviewable when it deletes files, without dropping those paths or weakening the identity to an unbound prepared-for packet.
Root Cause: The reviewed-input identity owner modeled each path only as current file bytes. A removed path was therefore required by exact range membership but impossible to hash, producing two correct checks whose intersection refused every deletion range.
Debug Artifact: charness-artifacts/debug/2026-08-30-issue-759-deletion-range-premise.md
Siblings: Decision: keep #731's broader worker-lifecycle friction separate; proof: the #759 tests exercise reviewed-input identity and no reviewer worker state. Decision: leave consumer Git/submodule topology to consuming agents and #761's separate disposition; proof: this closeout proves regular added, modified, and deleted file identity only and makes no topology claim.
Prevention: Preserve exact range membership, typed deletion pre-image hashing, single-commit parity, path-omission refusal, and stale-input refusal in focused tests and the public prepare-packet contract.
Implementation: Commit `67555154eeb90766857125b34ac30151dc18d4ad` added the deletion disposition and pre-image identity; later commits extended adjacent identity forms without removing the regular-file contract.
Critique: charness-artifacts/critique/2026-08-30-issue-759-resolution-critique.md
Behavior #759: verified through a focused published-main pytest channel: range deletion and single-commit deletion captured the removed pre-image, while deliberate changed-path mismatch and stale-input controls refused; 4 tests passed in 1.07s.
AI-provenance: Agent-authored manual closeout prepared from the live issue, published source history, focused current tests, and bounded resolution critique. GitHub state is not treated as behavior evidence.
