# Coordination With Existing Skills

`achieve` is a goal lifecycle operator, not a task execution engine and not a
replacement for the workflow skills. It coordinates them around one goal
artifact. Each coordinated skill must still be useful standalone; do not add
`achieve`-only branches to them.

| Skill | Role inside an achieve goal |
| --- | --- |
| `ideation` | clarify the user's intent and upstream decisions before the goal is shaped |
| `spec` | turn the goal into a living implementation contract when the target is complex enough |
| `impl` | execute slices; treat an active goal artifact as the slice memory surface |
| `quality` | design verification up front, run cheap checks during, broad gates near final |
| `issue` | record off-goal findings; only the issue reference and reason go in the goal artifact |
| `critique` | review the goal plan before activation, substantial slices, and final proof |
| `retro` | produce the automatic after-action review focused on time/token/waste |

## Activation

The user activates a saved goal explicitly:

```text
/goal @charness-artifacts/goals/<file>.md
```

`/goal` is the host's autonomous-run entrypoint and exists in both Claude Code
and Codex, so the skill references it directly. `achieve` prepares and audits the
goal; it does not implement the run loop itself.

## Boundary With `handoff`

Do not make `handoff` the default mid-goal state surface. While a goal is active,
the goal artifact owns running context. `handoff` is still the right surface when:

- the session is stopping outside an active goal
- a blocked goal needs the next session to resume with explicit context
- the user asks for a handoff artifact

## Off-Goal Findings

If a finding is not required for the current goal, file or defer it through
`issue` and append only the reference and reason to the goal artifact's
`Off-Goal Findings` section. Do not silently expand the active goal just because
a local fix is possible.
