# Quality Runtime Metrics Premortem
Date: 2026-04-29

## Decision

Issue #81 closes when quality runtime timing summaries stop treating
`latest.md` prose as the raw timing store. Runtime hot spot numbers must cite a
structured source and the summary helper that rendered them, or state that
timing capture is missing.

## Fresh-Eye Satisfaction

- status: parent-delegated.
- angle: downstream consumer repo usability.
- angle: validator false positives and artifact compatibility.
- counterweight: avoid overfitting the validator or forcing one schema.
- Cautilus: not used for this premortem.

## Acted Before Ship

- Added `render_runtime_summary.py` so quality artifacts can render runtime
  source and hot spot lines from `runtime_budget_lib.evaluate()`.
- Tightened `validate_quality_artifact.py` so numeric runtime hot spots require
  a structured source plus a rendered/generated/summarized provenance marker.
- Kept exact timing freshness out of `validate_current_pointer_freshness.py`
  because runtime samples are volatile machine-local state.
- Made the missing-source fallback generic: add structured timing capture
  before reporting trends.

## Bundled Anyway

- Updated `quality` guidance to point at the helper before reporting runtime
  trends.
- Updated handoff and artifact policy so transient pre-push timing stays out of
  `docs/handoff.md` unless it changes the next operator action.
- Synced checked-in plugin exports after source changes.

## Deliberately Not Doing

- No exact comparison between committed markdown timing numbers and
  `.charness/quality/runtime-signals.json`.
- No mandatory Charness-only runtime schema for consumer repos.
- No broader coverage/evaluator source validation in this slice.

## Verification

- `python3 -m pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`
- `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`
- `python3 scripts/validate_quality_artifact.py --repo-root .`
- `python3 scripts/validate_current_pointer_freshness.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `./scripts/check-markdown.sh`
