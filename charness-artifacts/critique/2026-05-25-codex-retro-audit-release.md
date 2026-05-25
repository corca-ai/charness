# Release Critique: Codex Retro Audit

Date: 2026-05-25

## Execution

Fresh-eye satisfaction: parent-delegated.

## Change

Release GitHub issue #218 as a patch release by adding a Codex-specific retro
efficiency evidence producer:

- `$SKILL_DIR/scripts/audit_codex_session.py`
- repo-owned parser/reporting helpers under `scripts/codex_session_audit_*.py`
- focused sqlite/TUI fixtures for source selection, token snapshot semantics,
  snippet privacy, unreadable sources, schema drift, and malformed rows
- public/plugin retro docs that keep the analyzer as an evidence pointer rather
  than a waste conclusion

## Angles

- schema honesty and token-signal semantics
- local-log privacy and snippet exposure
- bounded TUI fallback and sqlite schema drift
- public-skill boundary and plugin export readiness
- release closeout hygiene

## Act Before Ship

- Fixed TUI selected-thread leakage so auto/explicit scope limits the reported
  counts, phase counts, repeated families, and proxy outliers.
- Fixed sqlite source honesty: auto skips unreadable sqlite when TUI exists,
  explicit sqlite reports `source_unreadable`, and required `logs` columns are
  validated before a sqlite source is marked used.
- Fixed malformed sqlite row handling so bad timestamp rows are skipped instead
  of breaking JSON output.
- Fixed missing/unreadable source output so no waste candidates or measured
  cost signals are emitted without source evidence.
- Removed the generated `uv.lock` after validation; final changed-surface
  inspection reports no unmatched generated file.

## Bundle Anyway

- Keep plugin export copies in the same commit so installed Charness surfaces
  receive the analyzer.
- Keep `docs/retro-self-improvement-spec.md` aligned with the shipped command:
  token observations are `snapshot` or `unavailable`, never proven full-session
  totals.

## Over-Worry

- Exact Codex session token totals remain out of scope. The analyzer reports
  runtime/context snapshots and event aggregates only.
- Perfect phase taxonomy is not required for this patch; phase labels are
  evidence pointers and the public phase-aware review rule still owns waste
  interpretation.

## Valid But Defer

- Richer taxonomy beyond the current command-family and phase heuristics.
- Adapter-level auto-discovery or automatic retro invocation.
- A future optimization that computes sqlite thread `repo_hits` fully inside
  SQL rather than via row bodies.

## Verification

- `python3 -m pytest tests/quality_gates/test_retro_codex_session_audit.py tests/quality_gates/test_retro_skill.py tests/quality_gates/test_retro_host_log_probe.py -q`
- `pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`
- surface validators listed by `python3 scripts/check_changed_surfaces.py --repo-root .`

## Final Fresh-Eye Result

Newton: no release blockers.

Tesla: no release blockers after `uv.lock` removal and sqlite schema-drift
validation were confirmed.

## Next Move

Commit the implementation, run release preflight, publish the next patch
release, comment on and close GitHub issue #218.
