Classification: bug

Jtbd: Every declared critique reviewed path must supply identity-bound semantic bytes to every supported reviewer backend, while empty, mismatched, unavailable, or oversized input refuses before launch.
Root Cause: The packet bound path names and hashes, but the worker prompt originally carried only an instruction to open those paths. That instruction was unreachable on the tools-disabled Claude backend and could read current workspace bytes for a committed-ref review.
Debug Artifact: charness-artifacts/goal-runs/744/bodies/issue-751-semantic-review-input.md
Siblings: Decision: preserve #759's deleted-preimage identity as an input form; proof: working-tree, commit, and range deletion discriminator tests pass. Decision: keep #731's reviewer lifecycle separate; proof: #751 changes only pre-launch semantic materialization and prompt preparation. Decision: leave consumer Git/submodule/worktree topology to the consuming agent; proof: no topology policy or unsupported-state declaration was added.
Prevention: Re-read from the bound working-tree or committed-ref source, recheck each content identity, carry exact read-only bytes into a backend-independent prompt payload, require exact path membership, and refuse zero, unavailable, mismatched, or oversized input before reviewer launch.
Implementation: Commits `943278d75` and `5126a6e32` established semantic path and deletion carriage; remediation commit `1a0a00e79` made the actual bound bytes reachable to every supported backend and pinned committed-ref source isolation.
Critique: charness-artifacts/critique/2026-08-30-issue-751-semantic-input-resolution.md
Behavior #751: verified on the integrated branch through 99 focused tests in 19.34s; a final independent Luna discriminator slice passed 10 tests covering present inline input, committed-ref source isolation, deleted preimages, mismatch/unavailable/oversize/empty refusals, and pass-versus-block eligibility.
AI-provenance: Agent-authored manual closeout from the live issue, integrated source history, focused current tests, and two fresh-eye rounds including one blocker caught and remediated before publication. Provider state is not behavior proof.
