# Achieve Lifecycle — During

## During

## Pickup

The active run starts from the exact objective `/goal #N`. Run the achieve-owned
pickup helper in a clean process. It resolves the repository from the adapter
or one compatible git remote, reads the provider-backed parent and child graph,
validates the frozen Goal Draft and Goal Binding, checks current membership,
and selects one executable open child.

The selection predicate is:

1. child state is `OPEN`;
2. the body has one approved Work Item key, purpose, owned contract, acceptance
   and proof, and evidence boundary;
3. the child identity matches the binding or an approved graph amendment; and
4. every dependency is closed or explicitly satisfied by the current graph.

Candidates sort by approved rank, Work Item key, exact repository, and issue
number. No tie is guessed. Provider state is fresh for this pickup; a previous
receipt or local file cannot substitute for a readback.

## Execution

Delegate the selected child to its owning workflow. `impl` changes the smallest
meaningful code/config/test surface, `quality` chooses proportionate proof,
`prove` records the closeout, and `issue` owns any issue-bound close operation.
The child issue carries routine progress and behavioral evidence. The frozen
Goal Draft and immutable binding are never used as a scratchpad.

For ordinary reversible local work, deterministic proof may close the slice
with an explicit `Critique: not-required <reason>` disposition. Escalate to
critique when the work crosses authority, durability, external-write, security,
release, compatibility, deletion, migration, or proof-surface boundaries. A
required review that is blocked remains blocked; it never becomes approval.

### Lesson-session citation carrier

When SessionStart provides a lesson-session declaration command, run that exact
command before the affected work. Record the returned `session_id` and frozen
`bundle_path` in the active goal artifact's `## Context Sources`. retro reads
that exact bundle after context loss, never a newest-file guess or mutable lesson
source. Record the reference, not a copy of the bundle contents; the bundle
proves issued bytes, not human readback, lesson use, or lesson effect.

## Provider retry

Each provider mutation is one file-backed operation with a started observation
and a terminal observation. Treat outcomes distinctly:

- `verified-write`: exact target and readback match;
- `unverified-write`: stop and re-read before retrying;
- `partial-graph`: preserve verified identities and reconcile the remainder;
- `no-write`: provider was not invoked; repair input or readiness; and
- `refused`: no mutation occurred.

An invoked create with no discoverable identity is unresolved. Never create
again from memory. Re-read the provider and reuse an exact match.

## Graph amendments

After establishment, a concrete new Work Item or deferral changes provider
membership with an explicit reason and readback. The immutable initial binding
does not change. A semantic change to purpose, acceptance, architecture,
success, or proof policy returns to approval and a new binding.

## Coordination record

Adjacent evidence records carry the shared `goal_lineage` identity: draft
path/hash, binding path/hash, parent repository/number, and optional selected
child. Planning-only or not-goal-bound evidence is explicit and cannot satisfy
implementation or closeout proof. There is no second local progress ledger.
