---
name: achieve
description: "Use when operating a long-running auditable objective: research and freeze a complete Goal Draft, bind it to one provider-backed Goal Run, then resume with `/goal #N` and a real executable child. Coordinates adjacent skills without replacing their engines."
---

# Achieve

Use this skill when the user wants to shape, resume, or audit a long-running
objective. `achieve` owns the Goal Draft/Binding and lifecycle order; `issue`
owns provider state; the selected Work Item owns its implementation and proof.
It is an operator, not a second execution engine.

## Bootstrap

Read the current repository context and adapter before making a lifecycle
decision:

```bash
sed -n '1,200p' docs/handoff.md 2>/dev/null || true
git status --short --branch
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 <issue-skill-dir>/scripts/issue_tool.py goal-run-preflight --repo <repo> --number <parent> --plan-file <approved-plan.json> --repo-root .
```

`$SKILL_DIR` resolution for these bootstrap commands follows
[Bootstrap Resolution](../../shared/references/bootstrap-resolution.md).

The preflight is evidence about the selected provider only. Missing or invalid
adapter/backend capability is a typed stop; do not guess a repository from the
working-directory name or switch clients silently.

## Lifecycle

1. Research repository code, documentation, adapter, tracker state, and durable
   lessons. Resolve facts before asking the operator.
2. Create one complete local Goal Draft. It is mutable only before approval and
   remains the immutable planning record after approval. It is never a progress
   log, current-child pointer, percentage, or completion verdict.
3. Run the bounded interview. Resolve `interview.max_questions` from the
   adapter, defaulting to 15. Each consequential question records alternatives,
   tradeoffs, recommendation, reason, answer, and rejected alternatives. A
   ceiling reached with unresolved decisions blocks approval.
4. Run the required planning/alignment work, obtain explicit approval of the
   exact briefing and bytes, read the intended parent identity, and create the
   immutable Goal Binding. No provider mutation happens before approval.
5. Reconcile the parent and real sub-issue graph through the issue-owned
   Goal Run provider. Persist each typed provider observation and require exact
   identity/body/relationship readback. A partial or uncertain mutation stops
   retry until a clean read resolves it.
6. Start or resume execution only with the exact objective `/goal #N`. The
   provider reads the parent, binding, frozen draft, current graph, and every
   candidate child, then selects one open child whose dependencies are closed.
7. Delegate implementation and proof to the selected child. Routine progress is
   provider child state and child-owned evidence; no local progress mirror is
   created and the frozen draft is not edited.
8. Close children only with their issue-owned behavioral proof. The dedicated
   Goal Run close reads the complete graph, verifies child evidence/deferrals,
   records a terminal observation, closes the parent, and performs distinct
   post-close readback. No generic issue close may bypass that boundary.

## Exact pickup

The only issue-native user input is trimmed text matching `^/goal[ ]+#[1-9][0-9]*$`.
The host stores that ordinary objective; the helper performs the repository and
provider resolution:

```bash
python3 "$SKILL_DIR/scripts/goal_run_pickup.py" \
  --repo-root . --objective "/goal #<parent-number>"
```

Pickup refuses an unresolved or ambiguous repository, a non-Goal-Run issue,
malformed metadata, a closed parent, missing or mismatched draft/binding,
unverified establishment, stale membership, incomplete child body, stale
premise, blocked dependencies, or no executable child. It never falls back to
local artifact presence or a mutable local status.

The selected result is `verified-read` only. A pending bootstrap marker is an
honest refusal until the final target roundtrip has re-read the provider,
binding, draft, graph, and observations from a clean process.

## Provider and evidence boundary

Use the file-backed `issue_tool.py goal-run-*` commands for provider reads and
mutations. The operation file carries the repository, parent, binding/draft
hashes, attempt id, target, and repository-local observation directory. Keep
`started`, `no-write`, `verified-write`, `unverified-write`, `partial-graph`,
`verified-read`, and `refused` distinct.

Evidence producers use the shared `goal_lineage` record: frozen draft path/hash,
binding path/hash, exact parent repository/number, and optional selected child
identity. Planning-only and not-goal-bound records must say so explicitly and
cannot satisfy implementation or closeout proof. A path or issue number alone
never binds evidence.

## Coordination

Keep the standalone workflow owners intact:

- `ideation` and `spec` shape the concept and implementation contract.
- `critique` is selected for material authority, durability, external-write,
  security, release, compatibility, deletion, or proof-surface risk.
- `impl` changes code/config/tests and `prove` closes the implementation slice.
- `quality` selects and runs the appropriate verification gates.
- `issue` owns provider operations and issue closeout.
- `retro` records lessons after the work unit.
- `handoff` prepares the next session only when the user asks or the goal is
  blocked outside the active provider path.

Adjacent workflows consume exact Goal Run/Work Item lineage when they claim
execution evidence. They do not create a second goal tracker or rewrite the
frozen draft.

## Output and non-claims

The durable outputs are the complete frozen Goal Draft, immutable Goal Binding,
provider observations, exact parent/child graph, child-owned proof, and the
final guarded close observation. Historical artifacts may remain readable but
are not current execution authority.

Local tests prove schemas, selection, refusals, and fake-provider behavior. A
real provider roundtrip is required for live graph claims. This skill does not
push, publish, tag, mutate an installed host, close an issue without the
dedicated proof boundary, or claim live/hosted behavior from local tests.

## References

- `references/index.md`
- `references/lifecycle-before.md`
- `references/lifecycle-during.md`
- `references/lifecycle-after.md`
- `references/coordination.md`
- `references/adapter-contract.md`
