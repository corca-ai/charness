# Issue #507 Quality Adapter Bootstrap Lifecycle Contract

Date: 2026-08-05
Source: [debug review follow-up](../debug/2026-08-05-debug-review-followup.md)

## Problem

Quality adapter bootstrap currently treats a generated difference as permission
to rewrite a consumer-owned adapter. That can refill intentionally absent
surfaces and discard comments before the operator can review the change.

## Capability Contract

Bootstrap must distinguish normalized equivalence, an unapproved conflict, and
an explicitly authorized migration. The default command preserves the existing
adapter bytes on conflict and emits a precise advisory. A migration invocation
may rewrite the adapter, reports every intended rewrite, and retains existing
comments.

## Current Slice

Repair the quality adapter bootstrap planner, CLI, renderer/report, tests, and
portable source/plugin documentation for the three lifecycle outcomes.

## Fixed Decisions

- Matching normalized intent is a silent `unchanged` result, even when comments
  differ only because the renderer is canonicalizing YAML.
- A conflict is detected before any adapter write; the default path returns a
  `conflict` status and preserves existing values and comments.
- A conflict advisory names the exact surface, requested change, reason, and
  next action (`--migrate` or manual editing).
- Explicit `--migrate` is the authorization boundary for a rewrite.
- Migration reports each rewritten surface and retains all existing comments in
  the resulting adapter text.
- Absent or deliberately disabled surfaces are not installed by the default
  path merely because defaults exist.

## Probe Questions

- Whether preserved comments can retain their original YAML position is not
  required for this slice; textual retention and an explicit migration report
  are the acceptance boundary.
- Whether other bootstrap writers share this lifecycle defect is a sibling
  review question, not an expansion of this implementation slice.

## Deferred Decisions

- A future per-field migration allowlist or interactive migration UI.
- A generic conflict planner shared by markdown-preview and other generators.
- A private consumer-repository roundtrip beyond the reconstructed local
  fixture.

## Non-Goals

- Changing quality adapter inference defaults.
- Restoring disabled coverage, CI, lefthook, prompt, or spec surfaces.
- Rewriting the consumer's existing adapter during ordinary bootstrap.
- Proving behavior in an unavailable private repository or installed cache.

## Deliberately Not Doing

- Treating a post-write warning as sufficient protection.
- Silently converting every conflict into a no-op without an actionable report.
- Making comments a reason to report a conflict when normalized YAML intent
  already matches.

## Constraints

- Source and checked-in plugin surfaces must remain synchronized.
- The existing adapter must be read back byte-for-byte in conflict tests.
- The CLI report is the operator-facing evidence channel; tests must also read
  the file bytes as the consumer channel.
- Existing #481 deliberate-absence behavior remains intact.

## Success Criteria

- Matching normalized intent produces no write and no advisory.
- A conflicting adapter remains unchanged and the report/advisory identifies
  every requested rewrite with reason and next action.
- `--migrate` rewrites only under explicit authorization, lists every rewrite,
  and preserves existing comments.
- Focused tests cover all three outcomes through the actual CLI and source/
  plugin parity remains valid.

## Acceptance Checks

- `python3 -m pytest tests/quality_gates/test_quality_bootstrap.py tests/quality_gates/test_quality_bootstrap_absence.py`
- `python3 -m pytest tests/quality_gates/test_adapter_lib_yaml.py tests/test_adapter_lib.py tests/quality_gates/test_quality_adapter_block_rejections.py`
- `python3 scripts/check_skill_contracts.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/check_doc_links.py --repo-root .`
- `./scripts/check-markdown.sh`
- `./scripts/check-secrets.sh`
- `python3 scripts/plan_risk_interrupt.py --repo-root . --changed-paths charness-artifacts/spec/2026-08-05-issue-507-quality-adapter-lifecycle.md`

## Boundary Ownership

- `preserve`: bootstrap owns the default no-write decision and report; the
  consumer owns the adapter's existing values/comments.
- `preserve`: migration owns the explicit rewrite authorization and comment
  retention evidence.

## Critique

- Interrupt Source: none
- Seam Summary: generated YAML serializer to consumer-owned adapter; bootstrap planner,
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the local reproduction and this contract resolve the observed pre-write authorization gap; implementation remains bounded to the quality bootstrap surface
- What Disproving Observation Is Resolved: a conflicting adapter is no longer treated as an authorized write by default; the repaired tests must prove preservation before implementation proceeds to closeout

## Canonical Artifact

- `charness-artifacts/spec/2026-08-05-issue-507-quality-adapter-lifecycle.md`

## First Implementation Slice

Add pre-write conflict planning and explicit migration mode, preserve comments
during migration, update the CLI/report and tests, then synchronize the plugin
surface before verification.
