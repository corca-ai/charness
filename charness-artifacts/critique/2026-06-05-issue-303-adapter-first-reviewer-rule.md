# Resolution Critique #303 — setup adapter-first subagent reviewer rule

Date: 2026-06-05
Issue: #303
Classification: feature
Reviewer: bounded fresh-eye subagent (general-purpose, read-only, shared parent
worktree) + operator self-critique.

## Slice under review

Add an adapter-first subagent reviewer rule to the setup-generated/normalized
AGENTS.md (`COMPACT_SUBAGENT_DELEGATION`): subagent reviews follow the active
skill/repo adapter's reviewer tier and concrete spawn fields instead of
inheriting the parent turn's host defaults; Codex critique reviewers resolve the
high-leverage tier to medium reasoning effort *unless the adapter says
otherwise* (never a global claim); stop and report if the adapter/tier cannot be
applied. Regression test covers the rule.

## Verdict: no blockers

All four #303 acceptance criteria confirmed YES by the fresh-eye reviewer:

1. Adapter-first rule present in the generated AGENTS.md (renders via
   `render_agents_template`; section still `compact_contract_present: True`).
2. Standing-delegation language intact — the original bullet (standing
   delegation request, canonical scopes, same-agent substitutes forbidden) is
   untouched; the new rule is a pure additive bullet (0 deletions).
3. A regression test (`test_generated_agents_carries_adapter_first_reviewer_rule`)
   covers the rule and was empirically confirmed to fail on both a removed-rule
   and a regressed global-medium variant.
4. Host-facing and never "every subagent is always medium": medium is doubly
   fenced (Codex critique + high-leverage tier), conditioned on "unless it says
   otherwise", and capped by an explicit "not a claim that every subagent is
   medium" disclaimer.

## Adversarial questions resolved

- **Weaken standing delegation?** No. Bullet 1 governs *whether/when* to spawn
  (immediately, no second message); bullet 2 governs *how* to configure the
  reviewer once spawning. "Follow the adapter's tier" is spawn-field selection,
  not a precondition; the stop-and-report fallback mirrors the canonical "tier
  is a request, never a hard requirement" posture. Inspector confirms
  `weakening_caveats_detected: []`.
- **Consistency with the canonical shared policy?** Consistent. The rule uses
  the canonical tier name (`high-leverage`) and attributes concrete values to
  the adapter. AGENTS.md is a host instruction file (host-specific by nature),
  not portable skill prose, so naming medium as the Codex default does not
  violate the no-hardcoded-value boundary; the `test_reviewer_tier_policy.py`
  scanner does not (and should not) scan this template.

## Over-worry (not folded)

- "For Codex critique reviewers" names one host as the illustrative example. The
  #303 issue's own desired text requests exactly that Codex framing, and the
  goal boundary permits medium only as the Codex-critique default, so it is
  per-spec. Kept as written.
- The test proves "rule present and inspector-clean", not "inspector rejects a
  global-medium variant" — acceptable, since the inspector was never designed to
  detect tier wording and #303 does not require it.

## Prevention

The regression test fails if the rule is removed or regressed to a flat global
medium, so future template edits cannot silently drop the adapter-first
guidance.
