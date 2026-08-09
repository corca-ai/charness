# Issue #574 resolution critique

Date: 2026-08-09
Classification: bug
Fresh-eye satisfaction: parent-delegated
Verdict: CLOSABLE after two bounded review rounds and the repairs they forced.

## What #574 asked for

Three adapter readers outside the 16-resolver glob still accepted an unsupported
adapter `version`, and two of them published a verdict that contradicted the
resolver's verdict on the same file. The job-to-be-done: a reader must not honor
fields from a schema version it never reconciled, and two surfaces must not
render opposite `valid` verdicts for one file.

## Delegated review rounds

Both rounds ran as bounded read-only fresh-eye subagents in the shared parent
worktree. `reviewer_boundary_fingerprint.py` verified `clean` around each round.

### Round 1 — NOT-CLOSABLE

Confirmed all four named defects repaired and mirrored (`capability_catalog_sources.py:224`
gates the entire field-honoring block behind `if not errors`, so `trusted_skill_roots`
and `allow_external_registry` never leave their safe defaults; `setup_adapter.py:31-41`
empties adapter data so `setup_inspect_lib.py:192` agrees with `resolve_adapter.py`;
`chunked_routing_issue_config.py:73-75` short-circuits before reading the raw block;
`quality_bootstrap_lib.py:216-223` raises instead of silently normalizing).

Refused the close on two grounds, both the same class the issue filed:

- **B1** `tests/quality_gates/test_adapter_version_reconciliation.py` advertised
  "18 sites, 0 exempt" while the four just-repaired sites appeared in neither
  `SITES` nor `EXEMPT_SITES` — absent, not exempt, which the file's own comment
  forbids. A proof surface stating a false coverage count is the defect #574 is about.
- **B2** Two readers still fail open on `.agents/quality-adapter.yaml`:
  `scripts/check_cli_skill_surface.py:49-52` (HIGH — it selects the subprocesses
  it runs from that adapter, and `product_surfaces` can switch the gate off) and
  `skills/public/quality/scripts/inventory_ubiquitous_language.py:60-70` (MEDIUM —
  the contract selects scan scope and exemptions). The issue's own census of
  "3 remaining" was short.

### Round 2 (owed: the repairs changed verdict logic on proof surfaces) — BLOCKERS-REMAIN

Round 2 read the repaired surfaces and found the repair had shipped a **new**
false completeness claim:

- **BLOCKER** `scripts/worktree_doctor_lib.py:58-66` hand-rolled
  `data.get("version") != 1` on `.agents/worktree-adapter.yaml`, whose
  `prepare.commands[].argv` the tool executes. `True == 1` in Python, so it
  accepted `version: true` — exactly the row the census pins at every driven
  site. It was absent from both lists, so "24 ... none of them is absent" was false.
- **MAJOR** `EXEMPT_SITES` reasons were unverified prose; only non-emptiness was checked.
- **MINOR** the `handoff_chunked_routing` row was misclassified (those files consume
  the `simple_skill` verdict rather than rendering one); a stale "17 of the 19"; a
  "Two things to check" heading over four bullets.

## Repairs made in response

- `scripts/worktree_doctor_lib.py` now delegates to the shared
  `validate_adapter_version(..., required=True)` and prefixes errors with `manifest.`,
  closing the boolean-version acceptance on a subprocess-selecting manifest.
- `scripts/check_cli_skill_surface.py` `_load_adapter` returns `(data, errors)` and
  yields empty data on an unspeakable version; `build_payload` returns `blocked`
  (not `not_applicable`, which would let the adapter silence the gate).
- `skills/public/quality/scripts/inventory_ubiquitous_language.py` raises
  `InventoryError` instead of honoring `domain_language_contract`.
- The census is now executable rather than advertised:
  `test_the_census_names_every_caller_of_the_shared_check` enumerates every
  `validate_adapter_version` caller from the tree and fails on any site absent from
  `SITES ∪ EXEMPT_SITES`; `test_every_exempt_site_names_a_test_that_actually_exists`
  resolves each exemption's `path::function` (it caught one invented name on its
  first run). `VERDICT_CONSUMERS` names readers that honor a verdict rather than
  render one, so the two categories stop rendering the same.
- New construction tests pin each refusal with both halves (refusal fires AND the
  refused field does not survive).

Round-2 repairs are recorded as accepted-unreviewed per the two-round cap.

## Behavioral verdict (channel distinct from CLOSED state and carrier body)

Executed against a fresh `git init` fixture carrying `version: 7` adapters:

- `capability_catalog_sources.load_adapter` -> `valid False`, `errors ['version must be 1']`,
  `trusted_skill_roots []`, `allow_external_registry False`
- `./charness catalog list --repo-root <fixture> --summary` -> same refusal through the
  installed CLI entrypoint
- `skills/public/setup/scripts/resolve_adapter.py` -> `valid False`
- `skills/public/setup/scripts/inspect_repo.py` -> `valid false`, `invalid_adapter_version`
  (the contradicting verdicts are gone)
- `chunked_routing_issue_config.load_issue_source_config` -> forces `enabled=False`
  and never reads the raw block

Round 2 verified `plugins/charness/**` mirror parity by reading both copies; that
parity is static, not a separate behavioral probe, and is stated as such.

## Non-claims

- Mirror parity was proven by reading both trees, not by executing the plugin copy.
- `setup_inspect_lib.py:192` conflates non-version warnings with version errors;
  the two surfaces are reconciled **for version only**, not in general.
- `#576` remains an explicit no-verdict design gap and is not claimed fixed here.

AI-provenance: this critique and the repairs it records were authored by an agent
session; the bounded review rounds ran as separate read-only subagent contexts.

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (the repo's typed read-only subagent).
- Requested spawn fields: `subagent_type: bounded-reviewer`, prompt, synchronous
  return; deliberately no host addressing/team `name`, per the repo's spawn-shape rule.
- Host exposure state: host-defaulted
- Application state: n/a — no per-subagent model or effort override was requested, so
  the host had no such control to apply or report.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: the adapter/scope readers and the tests that render verdicts about them.
- Consumer: a consuming repo running the shipped gates, and the next session reading
  the census count as coverage.
- Owning surface: the reader that honors the declaration, plus the census test that
  states how many readers are covered.
- Verdict: owned-correctly
