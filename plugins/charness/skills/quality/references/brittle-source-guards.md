# Brittle Source Guards

Fixed-string source guards over prose markdown are fragile when the target file
uses hard column wrapping. A harmless editor reflow can split an asserted
substring across two lines and fail the matcher even though the rendered prose
still says the same thing.

Use `scripts/inventory_brittle_source_guards.py` when a repo keeps source-guard
tables or equivalent fixed-string assertions.

## Detection

Classify long fixed patterns as:

- `brittle`: exact match fails, but whitespace-normalized match succeeds in a
  hard-wrapped target
- `at_risk`: exact match currently succeeds in a hard-wrapped target
- `normalization_needed`: exact match fails but normalized match succeeds
  outside the hard-wrap heuristic

## Recommendation Order

Prefer semantic line breaks in the target prose. That removes the load-bearing
formatting choice from the source file itself.

If the repo deliberately keeps column wrapping, make the matcher normalize
whitespace before matching. This is a fallback, not the preferred fix.

When `quality` recommends a prose formatting policy, check whether a repo-owned
tool exists to enforce or apply it. A policy without an enforcement tool should
stay visible as follow-up work rather than disappearing into prose guidance.
