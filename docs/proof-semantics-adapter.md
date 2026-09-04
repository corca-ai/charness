# Proof-Semantics Adapter

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

The portable Charness residual/disposition ledger
([`scripts/core/disposition_form.py`](../scripts/core/disposition_form.py)) stays
presence/form-enum-only and learns **no** domain proof concept. The **domain
proof semantics** live entirely in this optional adapter, resolved by
[`scripts/adapters/proof_semantics_adapter_lib.py`](../scripts/adapters/proof_semantics_adapter_lib.py).
Charness asks; the adapter answers.

This keeps the gate-and-intelligence split: Charness does only generic lookups
and a rank/incomparability comparison over the tokens the adapter declares,
never a domain proof level or acceptance class.

Closes a portable gap: a closeout can carry honest non-claims and still publish
unless the workflow requires a machine-checkable acceptance/proof/disposition
ledger (background:
[339 goal record](../charness-artifacts/goals/2026-06-08-339-portable-disposition-ledger-adapter-proof-semantics.md)).
The blocking conditions are in [Closeout proof ledger](#closeout-proof-ledger)
below.

## Resolution

The adapter is optional. Identity is `ADAPTER_CANDIDATES` in
[`proof_semantics_adapter_lib.py`](../scripts/adapters/proof_semantics_adapter_lib.py):
only `<repo-root>/.agents/proof-semantics-adapter.yaml`. A file under `.codex/`, `.claude/`,
`docs/`, or the repo root is not resolved.

- **Missing** → degraded, not absent: the portable residual/disposition ledger
  floor still fires, and proof-mismatch detection degrades to *requiring a ledger
  disposition* (no domain map available) rather than silently passing.
- **Found but invalid** → fails closed, so a repo cannot ship a broken proof map.

> **charness itself ships no proof-semantics adapter.** So a `## Proof Ledger` added
> to a charness closeout runs the proof-mismatch floor in DEGRADED mode — every row
> needs an explicit disposition because there is no domain map to verify reached
> proof against. charness closeouts that declare no proof ledger (the norm) are
> unaffected, and the residual ledger is a separate surface that needs no adapter.

Field identity and the generic queries (`level_satisfies`,
`min_level_for_acceptance`, `gap_disposition_for`,
`acceptance_map_available`) live in
[`proof_semantics_adapter_lib.py`](../scripts/adapters/proof_semantics_adapter_lib.py).
Issue closeout calls them through
[`proof_mismatch.py`](../scripts/evidence/proof_mismatch.py).

> **Note — two distinct `out-of-scope` meanings.** `gap_policy.out_of_scope` is a
> *policy classification* (the adapter pre-clears a class so its gap needs no
> issue). The residual-ledger `out-of-scope: <reason>` form is a *human-supplied
> disposition* in the ledger. Do not conflate them.

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

[`scripts/evidence/proof_mismatch.py`](../scripts/evidence/proof_mismatch.py) checks each row
against the adapter and BLOCKS the closeout when a row has a proof gap left
undispositioned:

- the row's reached proof satisfies the adapter's minimum for the class →
  no gap, the `Disposition` cell may be empty;
- a gap (condition (i) empty `Reached`, (ii) reached below the class's required
  level, an unmapped class, or a missing/empty adapter map) →
  the `Disposition` cell **must** carry a real disposition
  (`applied:` / `issue #N` / `accepted-risk:` / `out-of-scope:`) — a placeholder,
  empty cell, or prose like `defer` is rejected.

The floor fires only when a `## Proof Ledger` is present. A found-but-invalid
adapter blocks (fails closed). The columns are located by header name
(`Acceptance`/`Class`, `Reached`/`Proof`, `Disposition`), so column order is free —
name them `Acceptance Class`, `Reached Proof`, and `Disposition` exactly (the
first header containing each needle wins, so avoid a second `Proof`/`Class` column).
