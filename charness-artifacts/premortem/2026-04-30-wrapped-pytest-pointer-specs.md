# Wrapped Pytest Pointer Spec Closeout Premortem

Date: 2026-04-30

## Decision

Fix issue #86 by treating wrapped `Covered by pytest:` continuation lines as
part of the same pointer block for implementation-reference pressure scanning.
The adapter regex remains unchanged; `_scan_prose` now excludes continuation
lines that consist only of backticked `tests/...` references after a matched
pointer line.

## Likely Misread

- The fix could be mistaken for a blanket exemption for any wrapped
  implementation path. It is narrower: only continuation lines made entirely of
  `tests/...` references are skipped.
- The pointer proof counter still counts the leading `Covered by pytest:` line,
  not every continuation line. That is acceptable because this scanner only
  needs to establish pointer proof presence and avoid implementation-pressure
  false positives.
- Real pytest reference existence is still owned by the separate validator; this
  change does not validate reference targets.

## Counterweight

- A multiline regex would have changed adapter semantics and risked
  repo-specific wrapping behavior. The block-level scan keeps the public adapter
  contract stable.
- The test preserves both sides of the contract: wrapped `tests/...` references
  are counted as total implementation references but exempted from pressure, and
  the spec still satisfies pointer proof.

## Proof

- `python3 -m pytest tests/quality_gates/test_quality_public_spec_quality.py -q`
- `ruff check skills/public/quality/scripts/public_spec_scan_lib.py tests/quality_gates/test_quality_public_spec_quality.py`
- `python3 -m pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`
- Fresh-eye review: no blocker to commit, push, or close #86.
