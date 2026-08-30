Classification: bug

Jtbd: Dup-ratchet summary consumers must see the same non-zero new-document-family count and sample that caused the underlying blocking verdict.
Root Cause: The summary projection was tested only on the zero-valued branch, so a constant zero or mistyped source key could disagree with a real doc-family block while the suite stayed green.
Debug Artifact: charness-artifacts/goal-runs/744/bodies/issue-709-summary-projection.md
Siblings: Decision: cover both code and document summary projections in the existing focused owner; proof: the adjacent blocking-run fixture pins the code count while #709's fixture pins document count and names. Decision: do not add an aggregate meta-gate; proof: the direct `summarize()`/CLI fixtures discriminate the wrong-key and constant-zero failures at the owning projection.
Prevention: Retain zero, non-zero, and non-scan fixtures; the non-zero test asserts both exact count and exact sample names so a stale key or constant result cannot pass.
Implementation: Commit `0341faa4b4b436e10ccc5ab33275eb83efa39b03` added the non-zero document-family summary proof.
Critique: charness-artifacts/critique/2026-08-30-goal-744-no-code-and-integrated-resolution-review.md
Behavior #709: verified through focused current-main summary fixtures: the zero document arm, a two-family blocking arm with exact count/sample equality, and non-scan withholding all passed; 3 tests passed in 1.01s.
AI-provenance: Agent-authored manual closeout from the live issue, published fix commit, focused current behavior tests, and Goal #744 bundled resolution review. No provider state or consumer-specific policy is claimed.
