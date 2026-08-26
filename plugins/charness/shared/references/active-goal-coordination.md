# Active Goal Coordination (Shared)

This reference is a silent no-op when the current work has no verified
provider-backed Goal Run identity. It does not create a goal, infer one from
local file presence, or change a standalone workflow's behavior.

## Verified identity

When the operator supplies `/goal #N`, `achieve` resolves and reads the parent,
immutable binding, frozen draft, current graph, and selected child. The shared
identity is the `goal_lineage` record:

- frozen Goal Draft path and SHA-256;
- Goal Binding path and SHA-256;
- exact Goal Run repository, issue number, and URL; and
- selected Work Item key and exact child repository/number when applicable.

Every consumer validates the complete identity before consuming evidence. A
matching path or issue number alone is not enough. Planning-only and
not-goal-bound records remain explicit non-execution evidence.

## Per-workflow behavior

- `impl` treats the selected provider child as slice context and does not edit
  the frozen draft or create a local progress ledger.
- `quality` records verification on the owning child or evidence artifact and
  distinguishes local, fake-provider, and live-provider proof.
- `critique` records a material-boundary decision only when the changed surface
  warrants it; ordinary reversible work may use the explicit not-required
  disposition owned by `prove`.
- `issue` routes in-scope graph changes and issue-owned closeout through the
  selected provider. Off-goal findings are filed or deferred instead of being
  silently added to the run.
- `prove` emits the slice closeout with exact Work Item lineage and separate
  non-claims. It does not turn a provider state change into behavioral proof.
- `retro` may cite the same lineage as provenance but never changes Goal Run
  state or the frozen draft.

## Parent and child state

Routine progress is the provider's fresh child state. Parent updates are sparse:
shared intent, scope, policy, dependency order, graph amendments, deferrals, or
completion semantics only. Each provider mutation is a file-backed operation
with a typed started/terminal observation and distinct readback.

No consumer should require a session handoff or a micro-slice record merely
because a Goal Run is active. Those are operator choices, not hidden execution
state. A genuinely blocked run may use `handoff` when the operator requests a
next-session baton.
