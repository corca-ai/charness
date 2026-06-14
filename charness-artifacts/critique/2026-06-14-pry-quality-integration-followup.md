# Critique Review: pry quality integration follow-up

Date: 2026-06-14

Bounded fresh-eye review (high-leverage tier, separate agent context — Explore
subagent `pry-reviewer2`) of the follow-up slice that (1) tracks the upstream pry
support skill the way specdown/cautilus/agent-browser are tracked, (2) makes
`quality` auto-run pry as an advisory phase, and (3) fixes a backlog-classification
bug the standing gate surfaced. Recurrence framing: "can the new standing-gate
phase ever fail standing quality, and is the welded-at-demand fix honest?"

## Decision Under Review

- **Track the upstream skill.** `integrations/tools/pry.json` becomes
  `external_binary_with_skill` with `support_skill_source` (upstream_repo,
  `skills/pry`, ref `main`), so `charness tool sync-support` materializes
  `support/pry/` — the upstream intelligence layer that labels findings
  GENUINE/FALSE-WELD/COSMETIC/AMBIGUOUS. charness stops reimplementing labeling.
- **Auto-run as advisory.** `scripts/run-quality.sh` gains an
  `inventory-testability-surface` phase (exists-guarded, mirrors
  `inventory-nose-clones`); the wrapper degrades exit 0 when pry is absent, so the
  standing gate never fails on it. A non-empty backlog surfaces as an `ADVISORY:`
  line so `run-quality.sh` prints it.
- **Bug fix.** The welded-at-demand backlog is `demand=true` AND
  `class=="welded"`, not `demand=true` alone. Before the fix the inventory kept
  reporting the two now-seamed findings as backlog (the standing gate printed "2
  welded-at-demand" when the true count is 0). Added `welded_at_demand` to totals.

## Failure Angles

- Standing-gate safety: could the new phase fail or hang the pre-push gate?
- Honesty of the fix: is `demand_total` (kept = subset total, includes seamed)
  misleading next to `welded_at_demand`?
- Integration-contract drift: is the `support_skill_source` shape wrong, or is
  `ref: main` an unstable pin?
- Declaration drift: do the declared `non_headline_fields` exist as JSON keys in
  both ok and degraded payloads?

## Counterweight Pass

- Gate-safe: the wrapper always exits 0 (advisory contract); the exists-guard
  matches the sibling advisory inventories; `flush_phase || OVERALL_RC=$?` only
  trips on a non-zero phase, which cannot happen here.
- Fix honest: `welded_at_demand` is the actionable headline; `demand_total`
  stays as diagnostic context (all demand-ranked findings, seamed or not). The
  real-repo run now reports 0 backlog, matching the seam fix from the prior slice.
- Contract correct: shape matches specdown/cautilus; `ref: main` matches
  agent-browser/specdown (cautilus pins only because it is mid-rewrite). pry is
  pre-1.0 and the bundled skill itself tracks main, so main is defensible.
- Declaration verified: `demand_backlog`, `scanned`, `totals`, `pry_version`
  appear in both ok and degraded payloads; `validate_inventory_consumption_declaration`
  passes.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/inventory_testability_surface.py:138 | action: fix | note: welded-at-demand backlog must filter demand=true AND class=="welded"; the standing gate caught the demand-only filter reporting seamed findings as backlog — fixed before closeout, with a seamed-demand test case locking it
- F2 | bin: valid-but-defer | evidence: moderate | ref: integrations/tools/pry.json:101 | action: defer | note: ref pinned to `main` like agent-browser/specdown; pinning to a tag (cautilus precedent) is optional polish, deferred until pry publishes a skill-layout-stable tag
- F3 | bin: act-before-ship | evidence: strong | ref: ../pry/skills/pry/SKILL.md:27 | action: file-issue | follow-up: https://github.com/corca-ai/pry/issues/1 | note: the bundled upstream skill says "pry has no published release yet" while v0.1.0 + the release installer are referenced by this manifest; filed upstream corca-ai/pry#1 to reconcile (per the user's request to file pry-side issues)
- F4 | bin: over-worry | evidence: strong | ref: skills/public/quality/scripts/inventory_testability_surface.py:48 | action: document | note: `pry map` rejecting multiple path args is by-design (single PATH); the wrapper loops one call per path — not an upstream issue

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model/reasoning_effort/service_tier from .agents/critique-adapter.yaml reviewer_tiers.high-leverage (Codex-host fields)
- Host exposure state: host-defaulted
- Application state: not host-confirmed; the adapter mapping targets a Codex host, so this Claude Code host spawned a bounded fresh-eye reviewer (Explore subagent) in a separate agent context instead of sending the gpt reviewer fields

## Fresh-Eye Satisfaction

parent-delegated — the parent spawned this bounded reviewer in a separate agent
context; it ran the failure angles and counterweight directly and returned a
clean (no-blocker) verdict. F1 was already fixed before closeout; F3 is tracked
as an upstream issue to file.
