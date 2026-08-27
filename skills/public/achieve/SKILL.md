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
summary when supported, and follows its current child cursor. That command
also returns the bounded lesson projection; do not invoke the lesson reader a
second time for the same `/goal` entry.

```bash
# Required Tools: rg
rg --files docs skills/public/achieve
git status --short --branch
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 <issue-skill-dir>/scripts/goal_run_pickup.py --repo-root . --objective "/goal #<parent>"
```

`$SKILL_DIR` resolution for these bootstrap commands follows
[Bootstrap Resolution](../../shared/references/bootstrap-resolution.md).

For an artifact-only `/achieve @<goal-file>` start, once the goal file is
known, read the same projection once with the achieve-owned helper:

```bash
# Required Tools: rg
rg --files "$SKILL_DIR"
python3 "$SKILL_DIR/scripts/goal_lesson_pickup.py" --repo-root . --goal-key "artifact:<relative-goal-file>"
```

This is the only automatic lesson pickup path for that entry. It is advisory
context, so an unavailable projection does not stop shaping the goal. A new
goal start or resume may read it once again; intermediate steps reuse the
returned payload.

Use `goal-run-preflight` only for establishment, graph repair, or an explicit
diagnostic. Missing or invalid adapter/backend capability is a typed stop; do
not guess a repository from the working-directory name or switch clients
silently.

## Lifecycle

1. Research repository code, documentation, adapter, tracker state, and the
   compact lesson projection through the entry's one pickup path: consume the
   `lessons` field from `/goal` pickup, or invoke the helper once for an
   artifact-only start. Resolve facts before asking the operator. Never scan
   the ledger again during that goal entry.
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
   Inspect the live host tool surface first and fan out independent
   investigation, implementation, review, or question resolution immediately.
   Honor the consuming repository's declared delegation tier across resume or
   compaction; without one, use the host's fast tier for bounded independent
   sidecars and reserve stronger tiers for critical-path or high-leverage work.
   Use the live host spawn/subagent API for short interactive or judgment-bound work, and
   use `charness task run` for bounded Codex work needing a named branch,
   explicit isolation in an isolated worktree, explicit path scope, external runtime, or durable result.
   Both are normal parallel channels; do not infer either one is absent from
   memory or an earlier session. The parent agent owns intent, dependency
   order, integration, and final verification. Direct same-context execution
   is for dependent or tiny work, or a confirmed lack of both channels.
   Routine progress is provider child state and child-owned evidence; no local
   progress mirror is created and the frozen draft is not edited. Focused tests
   are the normal proof; stronger review or proof is conditional on the claim.
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

The pickup result also carries one bounded lessons projection. It reads the
retro-owned recent-lessons.md, falling back to the precomputed selection index
only when that digest is unavailable. This is context, not a gate: missing,
or malformed lesson memory is reported as non-blocking unavailable; freshness
is deliberately not checked here. Do not rebuild the ledger, refresh the
digest, record a shown set, or create a session receipt during pickup. Repeated
reads within one goal entry are unnecessary; a new goal start or resume may
read the projection once again.
The small reader is owned by achieve at scripts/goal_lesson_pickup.py.

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

Keep adjacent engines available, but let Achieve own the active run's coordination and completion state:

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
  for work that genuinely needs durable cross-context state or an external
  scheduler. It is not required for an ordinary one-shot lane, and its
  parent-owned `review` transition does not create an observer, worktree, or
  proof gate.

Adjacent workflows consume exact Goal Run/Work Item lineage when they claim execution evidence. They do not create a second goal tracker or rewrite the frozen draft.

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
- `../../shared/references/binary-preflight.md`
