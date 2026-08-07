# Issue #553 resolution critique (delegated)

Classification: bug
Reviewer: delegated bounded reviewer (fresh-eye, read-only envelope: Read/Grep/Glob)
Verdict: RESOLVED WITH RESIDUAL RISK -> residual repaired in-slice, then re-reviewed

## Boundary Ownership

- Producer: `scripts/adapter_key_registry.py`, which renders the key-resolution verdict
- Consumer: its own `survey()` CLI and tests; nothing else calls it and no tier is armed
- Owning surface: the registry module itself; `scripts/adapter_lib.py` separately owns
  the shared-core key set and is referenced by name rather than duplicated
- Verdict: owned-correctly — the defect and its repair both sit in the producer, and no
  consumer holds a competing copy of the logic.

The defect and its repair both sit in `scripts/adapter_key_registry.py`, the
producer of the key-resolution verdict. No consumer holds a competing copy of
this logic: the module is called only by its tests and its own `survey()` CLI,
and nothing is armed on it. The one adjacent surface -- `scripts/adapter_lib.py`,
which owns the shared-core key set -- is referenced by name rather than
duplicated, so the shared-core owner is stated in one place.

No producer/consumer split to move or escalate.

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (read-only fresh-eye, `.claude/agents/bounded-reviewer.md`)
- Requested spawn fields: agent_type=bounded-reviewer, model=inherited (no per-agent override), one-shot spawn with no host addressing/team name
- Host exposure state: requested_fields_sent
- Delivery state: findings-received
- Host exposure note: typed subagents and the Agent tool were exposed; the `bounded-reviewer` type was available and used
- Application state: applied as requested; reviewer envelope was Read/Grep/Glob only and structurally could not write, and worktree+index integrity was fingerprinted around the rounds with `skills/shared/scripts/reviewer_boundary_fingerprint.py`

## Fresh-Eye Satisfaction

parent-delegated — a separate bounded-reviewer agent context performed this critique
against the committed tree. Not a same-agent pass: the reviewer had no access to this
session's reasoning and reached the central finding — that the fix carried the class it
fixed — independently. Its two unverifiable claims were checked by the parent with
measurement (closure size per adapter) rather than accepted.

## JTBD

An operator declaring an adapter key needs to know whether any reader actually
consumes it *in that adapter*. Before #553 the resolver answered a different
question — "does any module anywhere parse a key of this name" — and presented
the answer as though it were about the adapter.

## Root cause

Resolution was KEY-scoped, not (FILE, KEY)-scoped. `resolve_declared_keys`
discarded the adapter path entirely, so a verdict was a claim about the repo
wearing the costume of a claim about the adapter.

## Debug artifact

Measured, not inferred:

```
.agents/cautilus-adapters/chatbot-benchmark.yaml
  evaluation_surfaces  reader  scripts/cautilus_adapter_lib.py   <- cannot read this file
  ...9 keys total
```

`scripts/cautilus_adapter_lib.py:13` pins `ADAPTER_PATH =
Path(".agents/cautilus-adapter.yaml")` — the singular file. Its only mention of
`.agents/cautilus-adapters/*.yaml` is at `:43`, inside
`DEFAULT_PROMPT_AFFECTING_PATTERNS`, an unrelated list of prompt-affecting
globs.

## Siblings — decision AND proof

The delegated critique's central finding was that **the fix carried the class it
fixed**: the transitive closure conferred association by bare module BASENAME,
and this repo ships 16 files named `resolve_adapter.py`. So every module
mentioning `resolve_adapter` was associated with *every* skill adapter —
association by name collision, the same defect as verdict by name collision.

Decision: repaired in-slice rather than deferred, because shipping it would have
left a false-green channel on 16 adapters.

Proof: closure size fell from 15–22% of the repo to 0–7%, measured per adapter;
`test_association_stays_a_small_fraction_of_the_repo` now bounds it at 10%, and
`test_one_skills_modules_are_not_associated_with_another_skills_adapter` names
the specific cross-skill contamination. A mutant restoring the basename branch
is killed.

Two further siblings from the same critique, both repaired and pinned:

- `_convention_owners` accepted any file at the conventional path, fabricating
  an owner from a stub. It now requires the candidate to name the skill — the
  same reconciliation `audit_registry` already applied to its own entries.
- `shared-core` returned before the scope filter, so `version`/`repo` claimed
  readers in a file nothing loads — a residual instance of #553 inside its own
  fix. It now names its actual owner.

## Behaviour verdict — distinct channel

Behavior #1: the fix was developed against pytest and in-process measurement
scripts. The verdict channel is different in observer, invocation, and execution
root: the `survey()` CLI, run as a subprocess from a **clean detached git
worktree** at the commit.

```
git worktree add /tmp/ch553 f470cd83 --detach
cd /tmp/ch553 && python3 scripts/adapter_key_registry.py --repo-root .
-> exit 0; 37 adapters, 445 keys; gaps confined to the two cautilus-adapters files
```

Generalization was proven by constructing a NEW adapter with the same shape
rather than re-reading the reported one:

```
.agents/cautilus-adapters/zz-probe.yaml
  quality_phases           reader-elsewhere   <- parsed elsewhere, nothing reads this file
  not_a_real_key_anywhere  unknown            <- `unknown` is reachable, not vestigial
```

That second line answers the critique's question 3 directly: zero `unknown` keys
repo-wide reflects the repo's state, not an unreachable state.

## Prevention

The critique named the generalizable rule and it is adopted: **whenever this repo
widens a scope to avoid false positives, the widening ships with a measured upper
bound in the same commit.** Every seed in this module was justified by a
measurement of under-reporting; none carried a measurement of over-reporting, and
that asymmetry is the mechanism by which the class recurred. The bound now exists
as an executable test rather than as this sentence.

## Residual, stated

Narrowing association surfaced under-association residue: two adapters whose real
readers receive data from a caller rather than naming the adapter. They report
`reader-elsewhere`. This is the deliberate trade — a false `reader-elsewhere` is a
report an operator dismisses in one reading; a false `reader` is a false green
that hides an unreconciled declaration. The instrument reports and refuses
nothing, and no tier may be armed on it without revisiting this.

## Non-claims

No consumer repo was read. No remote CI. The consumer adapter population remains
what this measurement cannot speak for.
