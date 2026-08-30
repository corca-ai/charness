Classification: bug

Jtbd: `worktree prepare` must skip declared setup only when the selected doctor proves every setup responsibility that would be skipped.
Root Cause: The prepare owner treated a generic doctor `PASS` as proof of all declared preparation commands, although doctor checks had no required relation to those commands.
Debug Artifact: charness-artifacts/goal-runs/744/bodies/issue-752-worktree-readiness.md
Siblings: Decision: keep force execution as the existing explicit override; proof: `test_prepare_runs_commands_when_doctor_was_passing_with_force` passes. Decision: keep multi-root setup responsibility explicit rather than infer one healthy dependency covers all; proof: `run_prepare` reports uncovered command IDs and skips only when declared coverage is complete.
Prevention: `prepare.commands[].id` and `doctor.checks[].covers` form the typed coverage relation; focused false-ready and proved-ready fixtures pin both sides.
Implementation: Commit `8e86be65f98ffa390076b6d1203b0938f06513ef` licenses skipping by declared coverage rather than by a generic doctor verdict.
Critique: charness-artifacts/critique/2026-08-30-goal-744-no-code-and-integrated-resolution-review.md
Behavior #752: verified through focused current-main fixtures: an uncovered prepare responsibility executed and failed instead of reading ready, complete declared doctor coverage skipped it, and `--force` still executed it; 3 tests passed in 0.63s.
AI-provenance: Agent-authored manual closeout from the live issue, published fix commit, current focused behavior tests, and the Goal #744 bundled resolution review. Provider state is not behavior proof.
