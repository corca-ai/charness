# Proof-Semantics Adapter (#339)

The portable Charness residual/disposition ledger
([`scripts/disposition_form.py`](../scripts/disposition_form.py)) stays
presence/form-enum-only and learns **no** domain proof concept. The **domain
proof semantics** live entirely in this optional adapter, resolved by
[`scripts/proof_semantics_adapter_lib.py`](../scripts/proof_semantics_adapter_lib.py).
Charness asks; the adapter answers.

This keeps the gate-and-intelligence split (#253/#329/#337): Charness does only
generic lookups and a rank/incomparability comparison over the tokens the adapter
declares — it never hard-codes a domain proof level (`smoke`, `live`) or an
acceptance class (`reliability`, attachment delivery).

## Why it exists

Filed from `corca-ai/acme` closeout misses where honest prose non-claims still
carried a `Close #…`: a Slack multi-image closeout whose acceptance class was
attachment delivery but whose reached proof was local deterministic adapter
simulation, and a long-body closeout that recorded provider-observed write/read
but only `normalized_matched` (not exact-body) verification. Acme added a
Acme-specific guard; the **portable** gap is that a closeout flow can contain
honest non-claims and still publish unless the workflow requires a
machine-checkable acceptance/proof/disposition ledger.

The portable contract: require the adapter to supply the acceptance class and the
proof-satisfaction mapping, then **block closeout** when

1. a declared acceptance class has **no evaluated proof entry**;
2. the **reached proof level does not satisfy** the acceptance class; or
3. the gap **lacks an explicit disposition** — `issue #N` / `applied: <change>` /
   `accepted-risk: <reason>` / `out-of-scope: <reason>`.

Conditions (1)–(2) are the proof-mismatch detection; (3) is the residual-ledger
floor. None require Charness to know a domain concept.

## Resolution

The adapter is optional and resolved from the first existing candidate:

```text
.agents/proof-semantics-adapter.yaml   (canonical)
.codex/proof-semantics-adapter.yaml
.claude/proof-semantics-adapter.yaml
docs/proof-semantics-adapter.yaml
proof-semantics-adapter.yaml
```

- **Missing** → degraded, not absent: the portable residual/disposition ledger
  floor still fires, and proof-mismatch detection degrades to *requiring a ledger
  disposition* (no domain map available) rather than silently passing.
- **Found but invalid** → fails closed, so a repo cannot ship a broken proof map.

> **charness itself ships no proof-semantics adapter.** So a `## Proof Ledger` added
> to a charness closeout runs the proof-mismatch floor in DEGRADED mode — every row
> needs an explicit disposition because there is no domain map to verify reached
> proof against. charness closeouts that declare no proof ledger (the norm) are
> unaffected, and the residual ledger is a separate surface that needs no adapter.

## Schema

```yaml
version: 1
repo: <repo-name>
language: en

# The ordered backbone of proof strength, weakest -> strongest.
proof_levels:
  - lint
  - smoke
  - integration
  - live

# Unordered level pairs that do NOT satisfy each other despite their backbone
# rank (a partial order, not a chain). Each pair is a delimited "a, b" (or "a|b")
# string, or an [a, b] list. Both elements must be declared proof levels.
incomparable:
  - lint, smoke

# Acceptance-class -> the MINIMUM proof level that satisfies it. Each value must
# be a declared proof level.
acceptance_map:
  reliability: integration
  safety: live

# Proof-level -> a free-form verifier / artifact reference (each key a declared
# proof level).
verifier_refs:
  integration: pytest tests/integration
  live: provider roundtrip observed

# How a proof gap may be dispositioned per acceptance class.
gap_policy:
  acceptable:        # classes whose gap is acceptable without an issue
    - perf
  out_of_scope:      # classes explicitly out of scope
    - telemetry
  needs_issue: true  # an unclassified gap needs an explicit issue/disposition
```

## Generic queries (what Charness calls)

All domain-blind — they operate only on the declared tokens:

- `level_satisfies(data, reached, required)` — `True` if equal or higher backbone
  rank; `False` for a declared-incomparable pair (either direction) or a lower
  rank; `None` when a level is undeclared (a degraded / no-map case, never a
  silent pass).
- `min_level_for_acceptance(data, acceptance_class)` — the required level, or
  `None` when the class is unmapped.
- `gap_disposition_for(data, acceptance_class)` — `acceptable` / `out-of-scope` /
  `needs-issue`.
- `acceptance_map_available(adapter)` — the degradation signal: a valid adapter
  with a non-empty `acceptance_map`.

Charness (Slice 3) wires these into achieve/issue closeout to enforce conditions
(1)–(3) above. The adapter owns the proof semantics; Charness owns only the
presence/form floor and the generic comparison.

> **Note — two distinct `out-of-scope` meanings.** `gap_policy.out_of_scope` is a
> *policy classification* (the adapter pre-clears a class so its gap needs no
> issue). The residual-ledger `out-of-scope: <reason>` form is a *human-supplied
> disposition* in the ledger. Slice 3 must not conflate them: a `gap_policy`
> classification answers "does this gap need a disposition?", while the ledger
> form is one of the dispositions a human can write.

## Closeout proof ledger

A closeout (a goal artifact or an issue closeout body) declares which acceptance
classes it is claiming and the proof level it reached, in a `## Proof Ledger`
table. The closeout AUTHOR owns the rows — Charness never infers a domain
acceptance class:

```markdown
## Proof Ledger

| Acceptance Class | Reached Proof | Disposition |
| --- | --- | --- |
| reliability      | integration   |                              |
| safety           | smoke         | accepted-risk: low traffic   |
```

[`scripts/proof_mismatch.py`](../scripts/proof_mismatch.py) checks each row
against the adapter and BLOCKS the closeout when a row has a proof gap left
undispositioned:

- the row's reached proof satisfies the adapter's minimum for the class →
  no gap, the `Disposition` cell may be empty;
- a gap (condition (i) empty `Reached`, (ii) reached below the class's required
  level, an unmapped class, or a missing/empty adapter map) →
  the `Disposition` cell **must** carry a real disposition
  (`applied:` / `issue #N` / `accepted-risk:` / `out-of-scope:`) — a placeholder,
  empty cell, or prose like `defer` is rejected.

The floor fires only when a `## Proof Ledger` is present (no over-fire; no existing
artifact carries one, so no date grandfathering is needed). A found-but-invalid
adapter blocks (fails closed). The columns are located by header name
(`Acceptance`/`Class`, `Reached`/`Proof`, `Disposition`), so column order is free —
name them `Acceptance Class`, `Reached Proof`, and `Disposition` exactly (the
first header containing each needle wins, so avoid a second `Proof`/`Class` column).
