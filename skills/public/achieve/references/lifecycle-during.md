# Achieve Lifecycle — During

## During

## Pickup

The active run starts from the exact objective `/goal #N`. The achieve-owned
pickup helper resolves the repository from the adapter or one compatible git
remote, reads the provider-backed parent, validates the frozen Goal Draft and
Goal Binding, and returns the parent's managed `charness.goal-progress/v1`
cursor. The cursor already names the next child; pickup does not read the child
graph or hydrate child bodies.

The cursor carries the reconciled membership revision, counts, revision number,
and one exact `OPEN` child identity. The binding still owns rank and dependency
provenance, while the parent owns the current next-child decision. A missing or
stale cursor is a typed `progress-sync-required`/`progress-stale` refusal, not
an invitation to perform a hidden full scan.

Full graph membership, child-body, dependency, and evidence reconciliation is
reserved for bootstrap, explicit progress sync/doctor, graph amendment, and
closeout. Those paths use the provider's graph/evidence readers; routine pickup
is one parent read. Routine pickup also skips a separate capability/auth probe:
the live parent read is its backend check, while the stronger preflight remains
on the explicit lifecycle paths.

## Execution

Delegate the selected child to its owning workflow. `impl` changes the smallest
meaningful code/config/test surface, `quality` chooses proportionate proof,
`prove` records the closeout, and `issue` owns any issue-bound close operation.
The parent progress cursor carries the current navigation state; the child
issue carries behavioral evidence and its provider state. Advance the cursor
when the child transition is published. The frozen Goal Draft and immutable
binding are never used as a scratchpad.

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
