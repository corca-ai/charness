# Coordination With Existing Skills

`achieve` owns lifecycle policy and identity selection. It does not reimplement
the engines owned by adjacent workflows.

Material cross-surface changes use the [boundary ownership brief](../../../shared/references/boundary-ownership-brief.md)
through `critique`; structural retro dispositions use the shared
[`retro-issue-destination-split.md`](../../../shared/references/retro-issue-destination-split.md)
contract. These links preserve owning evidence without making `achieve` a second
review or issue engine.

| Workflow | Achieve contribution |
| --- | --- |
| `ideation` | clarify demand, status quo, wedge, and product boundaries |
| `spec` | turn the approved concept into the current implementation contract |
| `critique` | review material authority, durability, external-write, security, release, compatibility, deletion, migration, or proof-surface risk |
| `impl` | change the selected Work Item's code, config, tests, or operator artifact |
| `quality` | choose proportionate deterministic, provider, and boundary checks |
| `prove` | close the implementation slice with evidence and non-claims |
| `issue` | own provider operations and issue-owned closeout evidence |
| `retro` | record lessons and explicit improvement dispositions after the work unit |
| active Goal Run parent | carries the next-child cursor and resume state |

## Shared identity

Execution evidence embeds or references one `goal_lineage` record containing
the frozen Goal Draft path/hash, Goal Binding path/hash, exact Goal Run
repository/number, and optional selected Work Item identity. Matching a path or
number alone is insufficient. A planning-only or not-goal-bound disposition is
explicit and cannot satisfy implementation or closeout proof.

`impl`, `quality`, `critique`, `issue`, `prove`, and `retro` remain useful
without an active Goal Run. When they claim goal execution, they consume fresh
provider identity and refuse cross-draft, cross-binding, cross-parent, or
cross-child substitutions. They do not create a local progress ledger.

## Tracked issue resolution

For a bug-class Work Item, use `debug` to establish a falsifiable cause before
the fix. For issue closeout, use the issue-owned closeout contract and preserve
the exact child evidence reference. A parent close is a separate guarded
provider operation; a local commit keyword or a closed issue state is not proof
by itself.

## Risk-adaptive review

Ordinary reversible local work may close on deterministic proof with
`Critique: not-required <reason>`. Material boundaries retain their owner and
their distinct evidence channel. A blocked required review remains blocked; it
does not become an approval. Removing review machinery is not a reason to
recursively review the removed machinery.

## Provider boundary

Use file-backed `issue_tool.py goal-run-*` operations for parent, child, and
relationship state. Re-read before mutation and persist typed started/terminal
observations. External writes, issue closure, push, release, tag, installed-host
mutation, and deletions require their own authorization and readback. Do not
infer a stronger claim from local tests.

## Off-goal findings

If a finding is not required for the current Goal Run, file or defer it through
`issue` with a reason. Do not expand the graph merely because a local fix is
convenient. If it is an in-scope independently closable Work Item, add it through the
issue-owned `add-child` operation with an `amendment` (rank, dependencies,
reason, operator approval); the parent metadata's `amendments` list records it
and the immutable initial binding is preserved.
