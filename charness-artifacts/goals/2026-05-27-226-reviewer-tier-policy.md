# Achieve Goal: Close #226: centralize Codex fresh-eye reviewer tier policy

Status: active
Created: 2026-05-27
Activation: `/goal @charness-artifacts/goals/2026-05-27-226-reviewer-tier-policy.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

Close GitHub issue #226 by centralizing a portable Codex fresh-eye reviewer model/tier policy in skills/shared/references/fresh-eye-subagent-review.md, with concrete Codex spawn fields resolved by the adapter, named skills citing the shared policy instead of hardcoding provider fields, and a deterministic validator backing the closure.

## Non-Goals

- No ceal or other cross-repo changes; #226 names ceal#188 separately as
  out-of-scope platform work.
- No new public skill and no new subagent execution engine; charness expresses
  the reviewer tier, the host honors it.
- No change to runtime spawn behavior beyond the documented tier mapping.
- No work on #227 / #219 / #184 / #185.
- Not re-implementing the delegated-reviewer fast path: it already exists in
  `fresh-eye-subagent-review.md` (lines ~24-43, ~90-106) and in
  `critique/SKILL.md`; this run confirms/tightens it, not rebuilds it.

## Boundaries

- Decision shape (confirmed with user): portable `reviewer tier` abstraction in
  the shared reference; concrete Codex fields live in the adapter mapping.
  Confirmed Codex defaults for the high-leverage tier: `model: gpt-5.5`,
  `reasoning_effort: medium`, `service_tier: priority` (when available).
- Portable surfaces (shared reference, skill prose) MUST NOT hardcode provider
  model names; concrete values appear only in `adapter.example.yaml` / clearly
  host-specific blocks.
- Likely files: `skills/shared/references/fresh-eye-subagent-review.md`; named
  skills `critique`, `quality`, `release`, `issue` (SKILL.md + relevant
  `adapter.example.yaml`); `spec`/`handoff` already reference the shared file;
  one new test (e.g. under `tests/quality_gates/`).
- `release` does not currently reference the shared file (confirmed by grep);
  wiring it is in scope.
- Honor `mutate -> sync -> verify -> publish`: sync generated/packaging mirror
  surfaces before validators.
- Repeat-trap guards: SKILL.md 200-line budget (check before editing any
  SKILL.md); doc-link backtick gate (use `<repo-root>/` placeholders for
  path-like backticks); Python file/function line budgets when touching a test
  or script.
- Stop conditions: stop and ask if (a) the portable-vs-adapter split forces a
  schema change larger than a single reviewer-tier field, (b) `gpt-5.5` is not a
  valid host model at run time, or (c) the mandated fresh-eye critique path is
  blocked by a concrete host signal.
- Critique plan: slice-level fresh-eye subagent review on the policy/wiring
  slice and a final bounded critique before closing #226 (repo Subagent
  Delegation contract pre-delegates these scopes).

## User Acceptance

What the user can do to verify completion directly.

- Read `skills/shared/references/fresh-eye-subagent-review.md`: a portable
  reviewer-tier policy and the delegated fast path are present, with no provider
  model name in the portable section.
- See `critique`, `quality`, `release`, `issue` SKILL.md cite the shared policy
  instead of carrying their own model fields.
- See a Codex `adapter.example.yaml` reviewer-tier mapping with `gpt-5.5` /
  `reasoning_effort: medium` / `service_tier: priority`.
- Run the new validator/test and see it pass; #226 is closed on GitHub with a
  closeout note mapping requested outcome to executed proof.

## Agent Verification Plan

### Low-Cost Checks

- New targeted test: named skills cite the shared policy; no portable surface
  hardcodes provider model/effort/service_tier; delegated fast-path note present.
- `validate_skills` (SKILL.md budgets), `check_doc_links`, adapter validators.
- Grep assertion that provider values appear only in adapter/host-specific blocks.

### High-Confidence Checks

- `./scripts/run-quality.sh --read-only`.
- Packaging/plugin mirror sync + packaging validators (shared + skill surfaces
  are mirrored), run after the mutate step.

### External Or Live Proof

- Mandated fresh-eye subagent critique (slice-level + final).
- `gh issue close 226` via the `issue` resolution closeout, with the required
  resolution critique.
- No Cautilus eval expected; consult `scripts/plan_cautilus_proof.py` only if a
  failing-log path is named. Deterministic gates own closeout otherwise.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Add portable reviewer-tier policy + host-specific Codex mapping block + confirm fast-path in `fresh-eye-subagent-review.md` | Net-new policy is the core of #226; everything else cites it | reference diff; `check_doc_links`; no provider name in portable section | planned |
| 2 | Wire named skills + adapters: `critique`/`quality`/`release`/`issue` cite shared policy; add Codex `reviewer_tiers` to relevant `adapter.example.yaml` | Centralization (#226 intent) is only real once consumers reference it; `release` is currently unwired | grep citations; `validate_skills`; adapter validators | planned |
| 3 | Add deterministic validator/test for citation + no-hardcode + fast-path note | User-chosen test-backed closure; prevents regression | pytest green; duplicate-pressure sample (this slice adds tests) | planned |
| 4 | Closeout: sync mirror, `run-quality --read-only`, fresh-eye critique, close #226 with note | Repo contract: critique + closeout are part of the work | quality pass; `gh` issue closed; RCA ledger event | planned |

## Slice Log

### Slice 1: Portable reviewer-tier policy in shared reference

- Objective: Add a portable reviewer-tier abstraction (high-leverage/standard, no provider names) to fresh-eye-subagent-review.md, pointing to one canonical Codex adapter mapping; the delegated fast-path already satisfied #226 and was left intact
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: check_doc_links.py: Validated markdown links; grep for provider model/effort/service_tier values in the shared reference: 0 (portable surface clean). No tests added this slice.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: Wire skills + real Codex reviewer_tiers adapter field

- Objective: Make reviewer_tiers a validated critique-adapter field (per user-chosen option A: adapter field+validation), add the canonical Codex mapping (gpt-5.5/medium/priority) once in critique adapter.example.yaml + adapter-contract.md, and load-bear the shared policy into release (critique/quality/issue already reference it)
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: validate_skills: 23 packages OK (SKILL.md budgets: release 199, critique/quality 200, issue 196, all <=200); check_doc_links: Validated; tests/test_critique_prepare_packet.py: 23 passed; adapter validation positive+negative cases confirmed (clean load, unknown sub-field errors, unknown tier warns, scalar errors). No new test files this slice.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 3: Deterministic reviewer-tier policy test (host-plural)

- Objective: Lock the policy with tests/quality_gates/test_reviewer_tier_policy.py: named skills cite the shared policy; portable surfaces never hardcode provider models; the policy stays host-plural (Codex + Claude Code); delegated fast-path note present; adapter validates reviewer_tiers and documents both host defaults
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: pytest tests/quality_gates/test_reviewer_tier_policy.py: 8 passed
- Test duplication pressure: check_duplicates --repo-root .: No duplicates found at threshold 0.98 (after adding 1 test file, 8 functions); duplicate-pressure not pushed toward gate
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 4: Closeout: mirror sync, broad gate, fresh-eye critique

- Objective: Sync the plugin mirror, run the full read-only quality gate, and run mandated fresh-eye subagent critique before closing #226
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: sync_root_plugin_manifests.py synced plugins/charness + marketplace manifests; validate_packaging: 1 manifest OK; run-quality.sh --read-only: 68 passed, 0 failed (98.5s). Fresh-eye critique: 2 bounded reviewers (correctness+portability, scope+acceptance) both returned NO BLOCKERS / close #226. Took 1 reviewer NIT: added test_adapter_example_keeps_host_plural_guidance so the example YAML cannot silently regress to Codex-only (test now 9 passed).
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Off-Goal Findings

- #229 (filed): `achieve`/`critique` over-anchored on a user-confirmed,
  issue-framed single-host value (`gpt-5.5`) and nearly shipped a Codex-only
  policy. Reason: the Before-phase interview and critique did not probe whether
  a confirmed input is one of a host-plural family. The #226 policy itself was
  corrected to host-plural (Codex + Claude Code) before closeout; #229 carries
  the process lesson. Feeds this goal's Auto-Retro.

## Final Verification

Self-verification against the original goal:

- Centralized portable policy: DONE — `fresh-eye-subagent-review.md` owns the
  portable reviewer tier (high-leverage/standard), no provider model names.
- Adapter-resolved concrete fields: DONE — `reviewer_tiers` is a validated
  critique-adapter field; concrete values live in `adapter.example.yaml` +
  `adapter-contract.md` only.
- Host-plural (the corrected scope): DONE — Codex (gpt-5.5/medium/priority) and
  Claude Code (sonnet-4.6) are documented as peers; the original Codex-only
  framing was fixed mid-run.
- Named skills cite the shared policy: DONE — `release` wired; `critique`,
  `quality`, `issue` already referenced it; none hardcode provider fields.
- Delegated fast path: CONFIRMED already present (not rebuilt).
- Test-backed: DONE — `tests/quality_gates/test_reviewer_tier_policy.py`,
  9 passed.

Proof levels:

- Low-cost + high-confidence: `check_doc_links` OK; `validate_skills` 23 OK;
  `validate_packaging` 1 OK after mirror sync; `run-quality.sh --read-only`
  68 passed / 0 failed (98.5s); duplicate-pressure sample clean at 0.98.
- Fresh-eye critique (external proof): 2 bounded subagent reviewers, both NO
  BLOCKERS; 1 NIT taken (host-plural guard test).
- NOT run: live Cautilus eval (none requested; planner consult not triggered),
  mutation gate (out of scope for this change), and `git push` (pending user
  confirmation — see below).

Residual risk / non-claims:

- `gpt-5.5` and `sonnet-4.6` are the values the maintainer supplied; not
  independently verified against host model catalogs. They live in adapter
  surfaces, so updating them is a one-line change if a name drifts.
- The tier→spawn-field translation is prompt/operator-consumed, not enforced by
  a runtime spawn-config code path (none exists today); the adapter field is
  validated config + documentation, not a live spawn injector.

## User Verification Instructions

- `python3 -m pytest -q tests/quality_gates/test_reviewer_tier_policy.py` (9 passed).
- Read `skills/shared/references/fresh-eye-subagent-review.md` "Reviewer Tier" —
  confirm no provider model name and both hosts named.
- `grep -nE "gpt-5|sonnet-4" skills/public/critique/adapter.example.yaml` —
  values present here (adapter surface), absent from portable surfaces.
- Decide the `git push` (the local commit carries `Closes #226`, so the issue
  closes on push). #226 is intentionally left open until you confirm the push.

## Auto-Retro

- What worked: local-first investigation (validator told us the exact sync
  command; grep confirmed which skills already cite the reference) kept the
  wiring slice from touching the two at-budget SKILL.md files. Slice ordering
  (policy -> wiring -> test) meant the broad gate ran once, at the end.
- Biggest waste / lesson: the over-anchoring miss (#229). I let #226's Codex
  title and my own confirm/defer question shape a single-host design, and only
  the user's nudge surfaced host-plurality. The durable fix is a Before-phase
  anti-anchoring probe for confirmed/issue-inherited values (now tracked in
  #229), not a one-off correction here.
- Smallest next improvement: when an `AskUserQuestion` would lock a
  host/provider-specific value, offer the family shape instead of a global
  confirm/defer binary.
- Metrics: when available (host log token/turn counts not asserted here).
