# Boundary-Bypass Ratchet

Use this reference when a repo has tests that spawn delivery-boundary
entrypoints even though the same behavior is reachable through an in-process
surface.

## Ownership

`quality` owns the portable policy:

- payload field contract
- no-increase ratchet semantics
- exemption discipline
- review questions and non-claims

The consumer repo owns stack-specific detection. A Python repo may inspect
`scripts/*.py` and `*_lib.py`; a TypeScript repo may inspect package exports and
Vitest/Jest subprocess calls; a Go repo may inspect packages, `main()`, and
`exec.Command`. Each detector emits the same payload shape.

## Payload

The stack-specific probe emits JSON with:

- `schemaVersion`: `charness.quality.boundary_bypass_inventory.v1`
- `status`: `advisory` or `ratchet`
- `summary.scanned_test_files`
- `summary.candidate_count`
- `summary.candidate_key_count`
- `summary.convertible_count`
- `summary.internal_boundary_count`
- `summary.keep_boundary_count`
- `candidates[]`

Each candidate row has:

- `test_file`
- `import_safe_targets`
- `clean_inprocess_targets`
- `internal_boundary_targets`
- `behavior_assert`
- `likely_keep_boundary`

`convertible_count` counts candidate test files that have at least one clean
in-process target and are not likely boundary-contract tests.
`internal_boundary_targets` are import-safe targets that still spawn
subprocesses, shell commands, network calls, or git internally. Converting those
tests may still be useful, but it moves the boundary inward rather than removing
it.
`candidate_key_count` is the number of unique derived candidate keys. The key
shape is:

```text
<test_file>::<target>
```

Ratchet baselines compare these derived keys so a new target inside an existing
test file cannot hide behind unchanged row counts.

Validate examples and repo-emitted payloads with:

```bash
python3 skills/public/quality/scripts/validate_boundary_bypass_payload.py \
  --input skills/public/quality/references/boundary-bypass-payload.example.json
```

## Ratchet Policy

The default enforcement shape is `no_increase`:

- commit the current payload baseline after detector correctness is acceptable
- fail when a new unexempt candidate key appears
- fail when enforced counts increase above the baseline
- allow improvements to reduce counts without requiring an immediate baseline
  rewrite
- require every exemption to include a `# why:` rationale; include an owner or
  revisit condition when the exemption is not self-evidently temporary or local

Exemptions are for intentional real-boundary tests, not for ordinary behavior
assertions that are merely inconvenient to move lower.

## Review Questions

- Is the delivery-boundary test proving packaging, exit code, stderr, protocol,
  or process environment? If yes, it may be a boundary contract.
- Is the test asserting ordinary domain behavior through stdout/files? If yes,
  ask why that behavior is not reachable in-process.
- Does the in-process target still spawn internally? If yes, classify it
  separately from clean conversion work.
- Does a helper DSL make broad subprocess tests easier to write? If yes, make
  sure it does not comfort-pave the boundary.
