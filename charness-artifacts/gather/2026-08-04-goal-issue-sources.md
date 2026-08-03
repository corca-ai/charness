# Gathered GitHub issue sources for the 2026-08-08 goal

Source: https://github.com/corca-ai/charness/issues/491
Source: https://github.com/corca-ai/charness/issues/499
Source: https://github.com/corca-ai/charness/issues/500
Source: https://github.com/corca-ai/charness/issues/502
Source: https://github.com/corca-ai/charness/issues/501
Source: https://github.com/corca-ai/charness/issues/497

Knowledge Capability: Preserve the primary issue observations, candidate remedies,
and current state for Slice A and the dependent issue slices.

Freshness: captured 2026-08-04 from GitHub issue JSON; issue states below are the
source-of-truth state at capture time.

Access Mode: authenticated `gh issue view --repo corca-ai/charness --json ...`.
The generic public URL route was attempted first for #499 and ended in a GitHub
captcha block without content persistence; the authenticated CLI route supplied
the captured source instead.

## Captured source facts

- #499 — CLOSED. Five instances in one 2026-08-07 goal put guards on transport,
  type, equality, cycle-marker, or error-spelling forms instead of outcome or
  structure. Its non-binding candidates are a reviewer-packet question, a
  prompt/contract line, or recording the class with no new structure. It asks to
  shape the answer with #491.
- #491 — OPEN. Three shipped-reference/code mismatches occurred across four
  slices: an obsolete `scope_not_checked` claim, an incomplete status vocabulary,
  and a copy-paste example missing the safe `--fields-file` command. Its stated
  candidates are a `reference-claims` manifest, literal-set matching, or an
  explicit review-owned question; it says the review-owned shape caught all
  three and is the cheapest candidate.
- #500 — OPEN. `upsert_goal.py` has value guards but
  `draft_goal_from_chunk.py` independently writes goal artifacts without them.
  Candidates are a shared value helper, a library-layer guard with special slug
  handling, or a recorded drafter exemption.
- #502 — OPEN. `run-quality.sh` emits a summary consumed by 17 hand-written
  assertions in three test files. Candidates are one named renderer owner or a
  structured sibling carrying fields such as failed labels; the issue favors the
  structured shape because the consumer is an agent under truncation.
- #501 — OPEN. `check_export_safe_imports.py` scans import AST statements but not
  dotted module paths passed as strings to `import_repo_module`; that blind spot
  let #497 ship. The proposed choice is helper-aware string-literal scanning or
  a broader dotted-path scan.
- #497 — OPEN. Exported `scripts/validate_adapters.py` cannot import because it
  hardcodes the authoring-tree `skills.public...` path, and its companion glob
  also assumes the unflattened tree. The issue records this as a portability
  decision, not a one-line repair.

## Captured vs human confirmation

Captured: all bodies, titles, URLs, timestamps, and states above through `gh`.
Human confirmation: none required for reading these public issue records.

## Open gaps

Issue bodies are context and candidate statements, not the Slice A decision.
Local commit history and current files still determine whether each proposed
remedy remains applicable. #499's current CLOSED state contradicts the older
handoff listing it as open; the goal must disposition it as already closed with
the decision still recorded.
