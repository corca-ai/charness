# Issue #511 Nose Inventory Scope And Receipt Contract

Date: 2026-08-05  
Source: [Issue #511 debug review](../debug/2026-08-05-debug-review-followup-2.md)

## Problem

`inventory_nose_clones.py` assumes that every consuming repository has
Charness's `scripts`, `skills/public`, and `skills/support` roots. When a
consumer instead has ordinary source roots, `nose` receives nonexistent paths;
the wrapper emits zero families and exits successfully. `run-quality.sh` can
therefore record a non-scan as a completed measurement.

## Capability Contract

The clone inventory must resolve its requested scope before invoking `nose` and
must carry scope validity through the final quality receipt.

- CLI `--path` wins over adapter configuration. Otherwise the optional adapter
  field `nose_inventory_paths` wins over `DEFAULT_PATHS`.
- The producer reports `requested_paths`, `scanned_paths`, and `missing_paths`.
  `scope_status` is one of `scanned`, `partial`, `inapplicable`, `missing-tool`,
  or `error`. JSON `exit_code` remains the underlying `nose` result;
  `cli_exit_code` records the wrapper's terminal exit.
- Missing default/configured roots are not passed to `nose`. Existing roots are
  scanned; no existing root produces `status: inapplicable` without invoking
  `nose`. A partial scope remains explicitly partial even when its scanned
  subset is `clean` or has `findings`.
- A missing tool is `status: missing` and a query failure is `status: error`;
  neither is a completed scan. Query failure exits nonzero. Missing-tool,
  inapplicable, and partial outcomes use the runner's unproven exit contract.
- `run-quality.sh` recognizes those unproven outcomes as `UNPROVEN`, not
  `PASS`, and its receipt does not list them as measured scope. Receipt
  eligibility is `phase status == pass`, not merely that a phase process exited.

The terminal matrix is fixed for this slice:

| Producer result | `scope_status` | `nose` runs | CLI exit | Runner/receipt |
|---|---|---:|---:|---|
| `missing` | `missing-tool` | no | 3 | `UNPROVEN`; not measured |
| `inapplicable` | `inapplicable` | no | 3 | `UNPROVEN`; not measured |
| `clean`/`findings` over a partial scope | `partial` | yes | 4 | `UNPROVEN`; not measured |
| `clean`/`findings` over all requested roots | `scanned` | yes | 0 | `PASS`; measured |
| `error` | `error` | attempted | 1 | `FAIL`; adverse, not measured |

`nose_inventory_paths` accepts a list of non-empty repo-relative paths with no
absolute path or `..` escape. Omitted and empty are fallback-to-default; an
invalid configured value makes the adapter invalid and the inventory returns an
actionable error without scanning. The shipped helper loads this adapter field
through the normal repository/plugin runtime; this is portable behavior, not a
consumer-specific fork.

## Current Slice

Repair the nose inventory scope resolver, quality-adapter field, runner exit and
receipt handling, consumer-field declaration, tests, and portable
documentation. Synchronize the checked-in plugin mirror before verification.

## Fixed Decisions

- Built-in defaults remain Charness-compatible for repositories with those
  roots; they are a fallback, not a universal filesystem assumption.
- `nose_inventory_paths` is a repo-relative list of source roots and an empty
  list means “use the portable defaults.” It is independent of enabling the
  duplicate ratchet.
- Explicit `--path` is the operator escape hatch and is never silently replaced
  by a default. Missing requested paths remain visible in the payload.
- `scope_status` is the machine-readable completion boundary. `status` retains
  the clone result (`clean`/`findings`) only for the paths actually scanned.
- Missing tool is non-blocking but unproven; malformed/failed query is a real
  inventory failure. No baseline is written for either non-scan state.
- Existing quality artifact consumers must engage at least two scope/error
  fields, not infer scan completion from family counts or process exit alone.

## Probe Questions

- Whether a future scanner needs a richer root type than repo-relative paths is
  outside this slice; tests will pin the current list-of-roots contract.
- Whether a consumer should make partial advisory scope blocking is adapter or
  policy work; this slice makes it visible and unproven without adding a hard
  duplication threshold.

## Deferred Decisions

- A general scope schema shared by every quality inventory.
- A redesign of `dup_ratchet_scan.py`; its configured `scope_paths` boundary is
  a related but separate contract.
- A private consumer-repository or installed-plugin provider roundtrip.

## Non-Goals

- Reducing duplicate-family counts or changing nose ranking, fingerprints,
  baselines, exclusions, or ignore-file semantics.
- Making absent optional source roots a blocking quality failure.
- Inferring source roots from arbitrary repository files or adding a language
  discovery framework.
- Claiming external consumer behavior from the local reconstruction.

## Deliberately Not Doing

- Passing `DEFAULT_PATHS` to `nose` when none exists.
- Treating zero families, a zero process exit, or an advisory label as proof
  that a scan completed.
- Reusing `dup_ratchet.scope_paths` as an implicit configuration for an
  independent advisory; consumers must opt into `nose_inventory_paths` or use
  `--path`.

## Constraints

- Preserve successful Charness scans and the skill-bearing `skills/public` and
  `skills/support` roots.
- Keep `--summary` and `--json` semantically aligned, with the summary exposing
  the scope fields needed for first-read triage.
- Keep source and plugin helper/skill surfaces synchronized before validators.
- Keep the changed proof surface covered by focused tests and the required
  changed-line mutation lane.

## Success Criteria

- A repository with `src`, `scripts`, and `worker` roots but no skill roots
  invokes `nose` only for existing configured/explicit roots and reports the
  missing skill roots; it does not present a completed default scan.
- A repository with no valid requested root returns explicit `inapplicable`
  scope, names the missing paths, does not invoke `nose`, and is rendered
  `UNPROVEN` by `run-quality.sh`.
- A failed `nose` query is `status: error`, has distinguishable error details,
  and is not rendered as `clean`, `findings`, or a measured receipt.
- A successful full-scope Charness run retains its existing findings/clean
  behavior and reports `scope_status: scanned`.
- An adapter-configured alternate root is honored without changing the public
  skill body, and the docs explain both the adapter field and `--path` escape.

## Acceptance Checks

- `python3 -m pytest tests/quality_gates/test_quality_nose_advisory.py tests/test_nose_inprocess_coverage.py`
  (unit and integration: scope classification, query command, and payload/exit contract)
- `python3 -m pytest tests/quality_gates/test_quality_runner.py tests/quality_gates/test_quality_runner_runtime_aggregate.py`
  (integration: phase status, unproven inventory, and measured receipt scope)
- `python3 skills/public/quality/scripts/resolve_adapter.py --repo-root .`
  (integration: `nose_inventory_paths` resolves)
- `python3 scripts/export_plugin.py --repo-root . --host codex --output-root . --with-marketplace`
  followed by source/plugin parity checks (integration)
- `python3 scripts/validate_inventory_consumption_declaration.py --repo-root .`
  and `python3 scripts/check_inventory_declaration_coverage.py --repo-root .`
  (unit: declared scope/error fields are present)
- `python3 scripts/validate_debug_artifact.py --repo-root .`
  (integration: debug interrupt record remains valid)
- `python3 scripts/plan_risk_interrupt.py --repo-root . --changed-paths charness-artifacts/spec/2026-08-05-issue-511-nose-inventory-contract.md`
  (integration: no unresolved spec interrupt)

## Boundary Ownership

- `preserve`: the inventory producer owns scope resolution and must disclose
  what was and was not scanned.
- `preserve`: `run-quality.sh` owns the final local receipt verdict and must not
  turn a non-scan into measured scope.
- `preserve`: the consuming repository owns alternate source-root configuration
  through its adapter or explicit command arguments.

## Critique

- Interrupt Source: quality-511-default-scope
- Seam Summary: default-root resolver -> `nose query` -> advisory payload -> quality
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the delegated fresh-eye critique identified and this
  revision fixes the missing exit matrix, measured-scope eligibility, exact
  fixture shape, adapter path validation, and summary-field obligations
- What Disproving Observation Is Resolved: the minimal `src/scripts/worker`
  fixture currently produces `status: error`, zero families, and `rc=0`; the
  contract requires it to be explicit non-scan/unproven instead
- Fresh-Eye Review: unnamed bounded reviewer `019fd112-3027-7d52-9d4c-745708d470e2`
  classified the first draft `needs-revision`; its boundary fingerprint was
  verified clean at `/tmp/charness-reviewer-boundary-issue-511-spec.json`.
- Implementation Review Round 1: unnamed bounded reviewer
  `019fd11e-076e-7310-b517-b04942b5e315` found three repairs: explicit path
  precedence, missing-helper unproven fallback, and Windows-form path guards.
  The review boundary was verified clean before those parent repairs.
- Implementation Review Round 2: unnamed bounded reviewer
  `019fd122-30f1-71b3-9458-da7556560e10` read the repaired surface and accepted
  the first two repairs, then found the final Windows-root (`\\windows-root`)
  vector. The round-2 boundary was verified clean; the final root guard and
  regression were applied afterward and are recorded as accepted-unreviewed
  under the two-round cap. No third review is claimed.

## Canonical Artifact

- `charness-artifacts/spec/2026-08-05-issue-511-nose-inventory-contract.md`

## First Implementation Slice

Add scope resolution and payload fields, load `nose_inventory_paths` through the
quality adapter, wire non-scan exit statuses into `run-quality.sh`, update
consumer declarations/docs, add regression and in-process tests, then sync the
plugin mirror before verification.
