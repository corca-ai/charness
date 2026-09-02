# Operating Contract

> Status: current
> Source of truth: this page and the executable surfaces it names
> Last verified: 2026-09-02

Charness exists to help an agent reach a correct result with less rediscovery.
Every contract below must either prevent a real escape or make the next action
obvious. A ritual that only repeats another check is removable.

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

- Start with focused tests for the changed behavior.
- The default quality lane is the small core lane: [`run-quality.sh`](../scripts/run-quality.sh).
- Broad and review checks are explicit:
  [`run-quality.sh`](../scripts/run-quality.sh) `--full --read-only`.
  Release checks use the separate `--release` lane.
- Changed-line mutation proof, full-suite proof, and artifact ledgers are not
  universal implementation requirements. Use them when a verdict/proof surface,
  release, or claim actually depends on them.
- A proof-surface or [irreversible external change](./design-north-star.md#the-boundary-load-bearing) gets the narrow additional
  evidence that can catch its failure. A routine reversible code/doc change may
  finish with deterministic focused proof; it does not need a fresh-eye review
  merely because it is large.
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

## Generated surfaces

Batch source edits, then run the canonical exporter once:

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
