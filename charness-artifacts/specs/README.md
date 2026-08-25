# Goal Phase Specifications

This directory holds the detailed, phase-level contracts for long-running
`achieve` goals. It is operational state, not evergreen product documentation.

Each goal owns a directory named `<goal-slug>`. Each planned phase has one
`phase-<number>-<slug>/spec.md` containing:

- objective and scope in/out;
- dependencies;
- observable completion criteria;
- exact verification commands and the readable receipt they must produce; and
- explicit non-claims and failure handling.

The goal artifact under `charness-artifacts/goals/` remains the compact control
panel. Its `## Phase Specifications` section links every phase spec before
activation. Create or update the files with the achieve helper
`scaffold_goal_specs.py`; it refuses to overwrite a changed existing spec.

Phase specs are complete only when their criteria and verification have an
executed receipt. A failed verification is a structural debugging signal: use
`debug` and a 5-whys pass, record the generalized pattern, then repair before
retrying.
