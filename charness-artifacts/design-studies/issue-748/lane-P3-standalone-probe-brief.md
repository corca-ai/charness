# Lane brief: 748-standalone-probe (lane P3)

Governing contract:
`charness-artifacts/design-studies/2026-08-28-issue-748-migration-plan.md`
(rev 2), decisions D7 (normative), D9 (test seam + real-binary
carve-out), D1 (the shim, ALREADY LANDED as
`scripts/native_gate_lib.py` — read it; resolution order
override → managed → dev-tree, `NativeGateError`, CLI
`python3 scripts/native_gate_lib.py --repo-root <root> <cmd> [args...]`),
and `native/repograph/ABI.md`'s `standalone-targets` section (frozen v1
— the selection contract). Sibling lanes run concurrently but touch
only `native/**`; do not touch `native/**`. Do not spawn descendant
agents.

## Outcome

1. `scripts/check_standalone_imports.py` keeps ONLY what Python alone
   can prove: subprocess-executing the probe shapes and classifying
   `cycle` / `import-error` / `timeout` (including the wrong-shape
   `ModuleNotFoundError` fallback and cycle-marker veto — preserve
   that logic exactly). DELETE its discovery half: `SCAN_PATTERNS`,
   module discovery, shape construction, `--changed` resolution, and
   its `repo_file_listing` import.
2. Selection now comes from
   `repograph standalone-targets [--changed ...]` invoked through
   `native_gate_lib.resolve_native_core` (import it; do not re-resolve
   ad hoc). Parse the `repograph.standalone_targets.v1` document;
   execute each target's `shapes[].command` strings as today (same
   timeout, workers, and failure classification). `--changed` values
   pass through to the native command. `unmatched_changed`,
   `scope`/`scope_note` come from the native report (preserve the
   payload keys: scope, checked, discovered, cycles, other_failures,
   ok, unmatched_changed, scope_note, verdict, cycle_meaning,
   other_failure_meaning). ADD a provenance field
   `selection: "repograph standalone-targets v1"`. Exit semantics
   unchanged (0 ok / 1 BLOCKED). A `NativeGateError` or a native exit
   3/70 is a loud exit-1 failure naming the native condition — never
   a silent empty scope.
3. Tests (`tests/quality_gates/test_standalone_imports.py`):
   - Behavior tests (cycle reconstruction, `--changed` scoping,
     partial/full wording) keep passing — they may use the REAL
     dev-tree binary via the shim (D9 carve-out) since they already
     clone repo copies; do NOT convert them to fake-binary canned
     documents where doing so would hollow the claim.
   - The two enumeration-completeness tests
     (`test_every_tracked_module_is_either_discovered_or_deliberately_excluded`,
     `test_the_exported_mirror_enumerates_its_own_modules`) re-target
     the REAL binary's `standalone-targets` output (inventory-relative
     `targets[].path`), FAILING LOUD with the shim's remediation when
     the binary is unavailable — never skipping.
   - Do not add subprocess-boundary test shapes that would trip the
     boundary-bypass ratchet: drive `main()`/functions in-process
     where the existing tests do (`_load_check_module` pattern stays);
     run `python3 scripts/check_boundary_bypass_ratchet.py
     --repo-root .` before finishing.

## Boundaries

Scope (must match the task-run `--scope` list exactly):
`scripts/check_standalone_imports.py`,
`tests/quality_gates/test_standalone_imports.py`.
Out of scope: `native/**` (build-only), `plugins/**` (parent syncs),
`scripts/native_gate_lib.py` (consume, don't modify),
`scripts/staged_commit_gate_plan.py` (its literal reference stays
valid because the CLI surface is unchanged — verify, and report if
that assumption is false rather than editing it), run-quality.sh (the
script is not a queued label).

## Verification

- `cargo build --release` in `native/repograph` (read-only build) so
  the real binary exists;
- `python3 -m pytest tests/quality_gates/test_standalone_imports.py -q`;
- one real full run: `python3 scripts/check_standalone_imports.py
  --repo-root .` and one `--changed` run; report outputs verbatim;
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`;
- `./scripts/check-python-lint.sh`.
The parent runs the FULL battery after integration.

## Stop condition and result shape

One coherent commit, prefix `migrate(748):`. Final message: what was
built, commands run with observed results, deviations with reasons.
