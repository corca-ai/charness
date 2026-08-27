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
decision. A routine `/goal #N` pickup does not bootstrap the full provider
preflight; it reads the parent once, including the provider's cheap sub-issue
summary when supported, and follows its current child cursor.

```bash
git status --short --branch
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 <issue-skill-dir>/scripts/goal_run_pickup.py --repo-root . --objective "/goal #<parent>"
```

`$SKILL_DIR` resolution for these bootstrap commands follows
[Bootstrap Resolution](../../shared/references/bootstrap-resolution.md).

Use `goal-run-preflight` only for establishment, graph repair, or an explicit
diagnostic. Missing or invalid adapter/backend capability is a typed stop; do
not guess a repository from the working-directory name or switch clients
silently.

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
   retry until a clean read resolves it. This is the explicit bootstrap/sync
   path, not routine pickup.
6. Start or resume execution only with the exact objective `/goal #N`. The
   provider reads the parent, binding, frozen draft, and its managed execution
   cursor, then reads only the cursor's next child. Routine pickup does not scan
   the graph or hydrate every child. The provider summary is an observational
   count, not a second cursor; a mismatch is reported, while a closed cursor
   child is a typed sync stop. The parent cursor is advanced whenever a child
   transition is published.
7. Execute the selected child using the lightest matching implementation path.
   A normal code slice may use `charness task run` to create one clean named
   worktree and run Codex without an envelope ceremony. Routine progress is
   provider child state and child-owned evidence; no local progress mirror is
   created and the frozen draft is not edited. Focused tests are the normal
   proof; stronger review or proof is conditional on the claim.
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
unverified establishment, missing or stale parent progress, no next child, or a
cursor child that is no longer open. When available, `subIssuesSummary` is
reported from the same parent read so remote `completed/total` cannot silently
look like the managed cursor. It never falls back to local artifact presence or
silently launches a full graph reconciliation. Use the issue-owned Goal Run
read/sync path when the parent cursor needs repair.

The selected result is `verified-read` only. A pending bootstrap marker is an
honest refusal until the final target roundtrip has re-read the provider,
binding, draft, graph, and observations from a clean process.

Routine pickup does not run the full Goal Run capability/authentication
preflight and then repeat the parent read. The single provider parent read is
the live backend check for this path; bootstrap, explicit sync/doctor, graph
amendment, and closeout retain the stronger full preflight.

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

Keep adjacent engines available, but let Achieve own the active run's
coordination and completion state:

- `ideation` and `spec` shape the concept and implementation contract.
- `critique` is selected for material authority, durability, external-write,
  security, release, compatibility, deletion, or proof-surface risk.
- `impl` changes code/config/tests; `prove` is an optional evidence formatter
  for slices that need its stronger boundary proof.
- `quality` selects a proportionate verification gate when the change needs one.
- `issue` owns provider operations and issue closeout.
- `retro` records lessons after the work unit.
- The active Goal Run parent and cursor are the only resume state; do not create
  or refresh a second progress artifact. A provider sub-issue summary is only a
  live readback/reporting field, never another progress store.
- `charness task` is an optional carrier for a cross-context or delegated child;
  use it when a claim/result needs a durable cross-context carrier, not for every local slice.
  Its parent-owned `review` transition records a verdict but does not create an
  observer, worktree, or proof gate.

Adjacent workflows consume exact Goal Run/Work Item lineage when they claim
execution evidence. They do not create a second goal tracker or rewrite the
frozen draft.

## Output and non-claims

The durable outputs are the frozen Goal Draft/Binding and the provider-backed
parent/child state. Add provider observations or stronger proof only when an
external mutation or the claim needs them. Historical artifacts may remain
readable but are not current execution authority.

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
