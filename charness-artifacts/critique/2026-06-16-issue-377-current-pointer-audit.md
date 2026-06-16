# Critique: Issue #377 Current-Pointer Audit

Date: 2026-06-16
Fresh-Eye Satisfaction: parent-delegated
Reviewer: `019ece16-6578-7191-8913-392277827852`

## Reviewer Tier Evidence

- requested tier: default explorer
- requested spawn fields: inherited parent model and reasoning settings
- host exposure state: host-defaulted
- application state: spawn tool accepted reviewer agent id
  `019ece16-6578-7191-8913-392277827852`; reviewer-tier application details
  are host-hidden

## Scope

Review the local #377 slice before commit: resolver payload additions,
repo-wide current-pointer inventory, docs/quality guidance, plugin mirrors,
tests, and HOTL proof packet.

## Act Before Ship

- Finding: the initial inventory only discovered public skills with
  `scripts/resolve_adapter.py`, so `create-cli`, `ideation`, `spec`, and the
  `cautilus` artifact family were omitted while docs/proof said repo-wide.
- Resolution: broadened `scripts/inventory_current_pointer_layouts.py` to scan
  all `skills/public/*` directories plus existing
  `charness-artifacts/*/latest.md` families, and to report discovery source.
  `cautilus` now appears as an artifact-family row; no-resolver public skills
  appear as adapter-unmanaged rows.

## Bundle Anyway

- Finding: resolver failures were all counted as `adapter_unmanaged`, which
  could hide a genuinely broken resolver.
- Resolution: expected no-resolver and no-`output_dir` workflows remain
  `adapter_unmanaged`; other resolver failures now use `resolver_error` layout
  and keep status `unresolved`.
- Finding: add a JSON output smoke check.
- Resolution: added an in-process `main()` JSON smoke test to avoid creating a
  new boundary-bypass candidate.

## Valid But Defer

- Scaffold output exposure is already covered by shared scaffold behavior and
  existing tests; this slice keeps the resolver/inventory boundary.

## Over-Worry

- No unjustified blocking floor was added. `--require-resolved` remains optional,
  and no standing gate wiring changed.
- Plugin mirrors matched the touched source counterparts after sync.

## Proof

- Reviewer inspected the diff, plugin mirror equality, current pointer layout
  inventory, generic/quality resolver payloads, quality scaffold payloads, and
  focused tests.
- Parent follow-up proof after changes:
  `python3 -m pytest -q tests/quality_gates/test_artifact_naming.py
  tests/quality_gates/test_current_pointer_writes.py` -> 33 passed.
  `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .` -> passed.
