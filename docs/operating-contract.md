# Operating Contract

> Status: current
> Source of truth: this page and the executable surfaces it names
> Last verified: 2026-09-06

This page states the operating floor under
[design north star](./design-north-star.md); each contract below earns its place
against that standard.

## Ownership

- [`AGENTS.md`](../AGENTS.md) is the short repo entry point.
- [`docs/index.md`](./index.md) is the documentation index; its linked owner page answers
  the detailed question.
- The provider-backed Goal Run parent and cursor are live progress state.
  `Achieve` owns navigation and progress updates. There is no session-start hook,
  handoff document, or second progress channel.
- `skills/public/` is the canonical skill source. `plugins/charness/` is a
  generated install/export surface and is changed only by its exporter.

## Git and worktrees

The parent worktree is user state. Preserve its tracked, untracked, and ignored
files; never reset, restore, stash, clean, or mass-delete it to prepare a task.

Proof or implementation worktrees use a temporary named branch, explicit base
and target commits, and an explicit path scope. They fail before execution when
the checkout is detached or dirty. Cache, coverage, pytest temporary data,
reports, and other runtime output are placed outside the worktree. A clean
start is not proof of a clean finish, so the runner reports both.

## Verification

- This section owns verification applicability. [Development](./development.md#verification-and-export)
  owns Charness authoring command recipes and the integration sequence;
  [validator timing](./validator-timing-layers.md) owns when existing validators
  run; and [parallel execution](./parallel-execution.md#disjoint-writers) owns
  serialized parent integration. Those pages link here instead of redefining
  the change classes.

| Change class | Applicable proof |
| --- | --- |
| Ordinary consumer reversible edit | Run deterministic focused tests or checks for the changed behavior. Use the default core lane when the changed surface has cross-module consumers. Full/read-only, release, changed-line mutation, artifact-ledger, and fresh-eye proof are not universal requirements. |
| Charness authoring integration | After source integration, run the standing runner followed by the full read-only lane. Development supplies the commands. This is the authoring-repository integration safeguard, not the default for an ordinary consumer edit. |
| Proof-surface repair or verdict logic | Add the narrow evidence that can catch the failure, including an independent observer when authoring or changing a proof surface and changed-line/mutation proof when the verdict or claim depends on it. |
| Release or other irreversible external boundary | Use the boundary owner's full/read-only and release checks, captured readback, and any required distinct observer. Push, publication, installation, and other external actions remain separately authorized; development owns their command recipes. |

- If an independent observer is unavailable, record that limitation as a
  non-claim. Never describe a same-agent reread as independent evidence.

## External changes

Issue writes are allowed only through the issue provider and must read the exact
target back after mutation. A close must state whether the issue was completed,
not planned, or superseded; external-repository confirmation is not a reason to
keep an issue open. Additional review is reserved for a material,
[irreversible](./design-north-star.md#the-boundary-load-bearing), security,
release, or uncertain deletion boundary.

Push, pull request creation, reopening, tagging, version changes, release
publication, installation, and evaluator execution require an explicit request
for that phase. A green local check is not authorization for any of them.
A skipped gate is not a passed gate: the quality summary line names every gate
the run did not execute and why (`not run (label: reason)`), so a green that
omitted a check says so in its last line.

## Generated surfaces

The materialized `plugins/` mirror is derived from `skills/` and `scripts/`.
[`plugin_mirror_preamble.py`](../scripts/gates_support/plugin_mirror_preamble.py)
regenerates it in a writing run and refuses a stale tree in read-only; a bare
`plugins/` directory in a consuming repo is never sufficient.

So batch source edits instead of exporting after each one, and run the exporter
yourself only when you invoke `pytest` directly, which is the one path with no
runner in front of it:

```bash
python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
```

Validate the source and generated host layout together when packaging changes.
The source is the only authoring surface; mirror drift detection belongs at the
release/package boundary. Do not hand-edit generated mirrors or add a duplicate
authoring gate for them.

## Durable state

Commit meaningful implementation, workflow, and durable artifact changes after
verification. Current pointers must be no-op when canonical content has not
changed. Historical proposals, evidence, and retros belong under
`charness-artifacts/`; they explain a decision but do not silently override the
current docs.

When a command cannot run because a host capability is missing, report the exact
failure and leave the affected proof unclaimed. Do not add a prose workaround
or a new blocking rule merely to make the report green.
