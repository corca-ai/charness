# Resolution Critique #304 — setup template ↔ inspector compact-delegation agreement

Date: 2026-06-05
Issue: #304
Classification: bug
Reviewer: bounded fresh-eye subagent (general-purpose, read-only, shared parent
worktree) + operator self-critique.

## Slice under review

Make `COMPACT_SUBAGENT_DELEGATION` and the setup inspector
(`detect_fresh_eye_normalization` via `inspect_repo.py`) agree on the minimal
valid `## Subagent Delegation` contract, so an agent copying the documented
compact default is not flagged as `fresh_eye_delegation_rule_drift`. Fix:
whitespace-normalize every contract-snippet match in
`scripts/setup_agent_docs_fresh_eye_lib.py`. Regression test pins the agreement
against the actual generator output (line-wrapped), not a single-line copy.

## Verdict: no blockers

All four invariants confirmed by the fresh-eye reviewer:

1. The wrapped generated default now passes — no `fresh_eye_delegation_rule_drift`
   / `fresh_eye_task_review_scope_drift` (verified end-to-end via the real
   inspector).
2. The contract is not weakened: a compact block that says "same-agent
   substitutes are allowed" is still rejected (`compact_contract_present=False`,
   `fresh_eye_delegation_rule_drift` still fires) — covered by
   `test_setup_inspect_rejects_compact_delegation_that_allows_same_agent_substitute`.
3. Normalization only adds robustness — it never invents words, and
   `_extract_section` still runs on raw line-structured text, so the in-section
   weakening-caveat check cannot attribute out-of-section text to the Subagent
   Delegation section.
4. Existing single-line accept / weakening-caveat / stale-marker /
   legacy-init-repo tests still pass (32 in the policy file; 107 across the
   cited files).

## Adversarial questions resolved

- **False acceptance from normalizing the haystack?** No. The acceptance gate
  still requires a forbidden same-agent snippet AND no missing required snippet;
  normalization only makes contiguous-word phrases matchable across a line break.
- **Cross-bullet false match?** Not plausible for these specific multi-word
  markers/caveat patterns; the generated block trips zero caveats/stale markers
  after normalization.
- **Genuine regression guard?** Yes — simulated pre-fix logic against the actual
  generator output yields `compact_contract_present=False`, so the new test
  would fail against HEAD; its negative-space assertions keep it exercising the
  wrap hazard.
- **Mirror divergence?** None — `plugins/charness/scripts/...` is byte-identical
  to source.

## Over-worry (not folded)

Redundant re-normalization of the same small AGENTS.md text per inspect run is
cosmetic; inputs are one file, so no correctness or performance concern. No
action taken.

## Prevention

The fix removes the whole class for this module (every matcher now normalizes),
and the regression test asserts the raw generated phrases are *not* contiguous,
so a future de-wrap that silently degrades coverage trips the test.
