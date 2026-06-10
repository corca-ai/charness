# Achieve Goal: Next queue — #342 adapter-schema commit-time pull + #343 host-hook lifecycle + deferred-proof verification

Status: active
Created: 2026-06-10
Activation: `/goal @charness-artifacts/goals/2026-06-10-342-343-adapter-schema-hook-lifecycle-deferred-proofs.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: slice 1 — #342 adapter-schema commit-time pull (verify-first).
- Next action: confirm the adapter/schema sibling set, record the seam
  decision, then wire the pull.
- Timebox: 4h
- Activation time: 2026-06-10T11:41:15+09:00
- Closeout reserve: 35m
- Done-early policy: continue_next_improvement (if a slice closes early,
  continue to the next surfaced improvement rather than stopping).
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Clear the post-v0.36-lane next queue in three independent per-slice-closed-out
slices, synthesized from the 2026-06-10 session retro, the open issues, and
the handoff/recent-lessons state: (1) **#342 — ADAPTER-SCHEMA COMMIT-TIME
PULL.** An `.agents/*-adapter.yaml` edit passed commit-time `validate-adapters`
while the integration's own `manifest.schema.json` (`additionalProperties:
false`) rejected it, so the usage-episode emitter failed two slices later
(`invalid_adapter`). Close the two-validation-owners seam: when a staged path
matches `.agents/*-adapter.yaml` and a matching
`integrations/<name>/manifest.schema.json` exists, jsonschema-validate the
adapter at the commit boundary through ONE single-source seam (decide:
extend `validate_adapters.py` to resolve integration schemas vs a new small
bridging validator wired via `_timing_layer_gates`) — per the
`docs/conventions/validator-timing-layers.md` frame (cheap, changed-scoped,
deterministic, not validate-all). Generalize across the real sibling set
(usage-episodes, t-events, worktree — NOT tools/, which has no
`.agents/*-adapter.yaml`). (2) **#343 — HOST-HOOK LIFECYCLE ROBUSTNESS.**
Add a dangling-checkout liveness check (each state-tracked hook's script path
still exists) to the existing status surface
(`reconcile_usage_episodes_host_hooks.py --mode status` /
`session-capture status`), record the multi-checkout posture decision (accept
one-logical-hook-per-machine + commit-sweep backstop, or key hooks per
checkout — decide, document, do not silently leave both), and factor the
`reconcile_host_hooks` fan-out into a registry so a fourth hook intent does
not copy the lazy-import block a third time. (3) **DEFERRED-PROOF
VERIFICATION.** Consume the now-executed deferred proofs from the 2026-06-10
goal + release lane: the first remote `quality-core.yml` CI run verdict
(triage any first-run friction per the CI-only failure-recovery protocol in
`skills/public/quality/references/maintainer-local-enforcement.md`, fix
repo-locally), the fresh-session edit-time #N-anchor guard firing (a real
`PostToolUse` flag on a `#NNN` edit in `skills/public/**`), and the #335
auto-close check on the next green scheduled mutation run (the workflow
marker owns the close — verify, never manually close). Each slice closes out
independently; skill-script changes mirror byte-synced; deterministic gates
own closeout; no `#N` anchors in skill-package files (dogfood).

## Non-Goals

- Do NOT take on **#184** (product success metrics) — product-level; needs an
  operator `ideation`/`spec` session, not a slice (third consecutive
  deliberate exclusion; if the operator wants it next, it should be its own
  goal shaped through `ideation`).
- Do NOT cut a release or push as part of this goal — the v0.36 lane
  (2026-06-10 push + release) is already executed and phase-scoped; this
  goal's repair commits (if CI triage finds any) stay local until the next
  operator-authorized push lane.
- Do NOT manually close **#335** — the scheduled mutation workflow's
  auto-issue marker owns it; slice 3 only verifies.
- Do NOT add consumer-inherited blocking behavior: the #342 pull degrades to
  no gate when the repo lacks the schema/validator (the `_timing_pull_gate`
  existence-guard pattern); #343's liveness check is status/doctor surfacing,
  not a new hard gate.
- Do NOT fork validation logic for #342 — one single-source seam invoked at
  the commit timing; rejected by the disposition review this session was
  exactly "an inline dispatcher hack would itself fork validation logic".
- Do NOT pull anything failing the timing-layer criteria (expensive /
  validate-all) while wiring #342; the broad gate stays the enforcement floor.

## Boundaries

- **Slice 1 — #342.** VERIFY-FIRST: confirm which integrations actually pair
  an `.agents/*-adapter.yaml` with a `manifest.schema.json` (usage-episodes,
  t-events, worktree confirmed; tools/ confirmed NOT — per the disposition
  review). Single-source seam decision recorded in the slice log before
  wiring. A test per covered adapter pair + a negative test (repo without the
  schema inherits nothing). Budget: the pull must stay sub-second and inside
  the ~1s pre-commit line from `validator-timing-layers.md`; update that
  doc's classification table row for the new pull. Closes #342 via the issue
  closeout contract (`issue_tool.py validate-closeout-draft` before the
  closing carrier; the closeout-draft preflight
  `check_artifact_surface_preflight --type closeout-draft` exists — use it,
  the 2026-06-09 retro paid 4 round-trips learning this contract).
- **Slice 2 — #343.** The liveness check extends the EXISTING status surface
  (no new command); the registry refactor must keep
  `reconcile_host_hooks`'s per-host error-isolation semantics (an enabled
  host's failure reports per-host, never aborts the chain) and the existing
  three intents' behavior byte-stable (the 52-test host-hook suite is the
  floor). The multi-checkout posture is a DECISION + doc line, not
  necessarily code. Closes #343 (same closeout contract as slice 1).
- **Slice 3 — deferred proofs.** READ/VERIFY-FIRST slice: consume executed
  remote results (`gh run list/view` for quality-core + mutation-tests), do
  not trigger new remote actions beyond what GitHub already ran on the
  pushed state. Repair commits for CI first-run friction are in-scope but
  local-only; a repair that changes workflow behavior re-runs only via the
  next operator push (named deferred proof again if so). The edit-time guard
  proof needs a fresh host session — if this goal's session IS fresh, prove
  it directly (edit a scratch `#NNN` into a skills/public file, observe the
  hook flag, revert); if the host blocks observation, record the concrete
  signal honestly instead of claiming.
- **Public-skill + generated-surface scope.** Any skill-script change
  mirror-synced (`plugins/charness/...`); deterministic gates own closeout;
  no `#N` anchors in skill-package files; `quality`-package semantic changes
  re-trigger the public-skill validation review (ack with a recorded
  decision, as this session did).
- Discuss before activation: RESOLVED — (a) `issue_close` trigger: this goal
  close-intends #342 and #343 (named in `## Goal`/`Coordination Cues`), via
  the validated closeout-draft contract; that is the goal's purpose, not an
  incidental side effect. (b) `production_or_live_proof` trigger: slice 3
  CONSUMES remote CI results that the operator-authorized 2026-06-10
  push/release lane already produced; the goal triggers no new remote
  side-effects (re-push after CI repairs is the next operator lane, named as
  a deferred proof if needed). (c) No release is cut by this goal. Safe to
  activate; re-open if a reviewer disagrees.
- External side-effect scope: the 2026-06-10 push + v0.36 release lane was
  operator-authorized in the shaping session and is phase-scoped to that
  lane; it does NOT carry forward into this goal. This goal is local-only
  except read-only `gh` consumption of existing runs/issues and the #342/#343
  issue-closing carriers.

## User Acceptance

What the user can do to verify completion directly.

- **#342:** edit an `.agents/usage-episodes-adapter.yaml` key that the
  integration schema forbids, stage it, and see the commit blocked at
  pre-commit (not two slices later at the emitter); a repo without the
  schema/validator inherits nothing; #342 closed with the validated carrier.
- **#343:** `python3 scripts/reconcile_usage_episodes_host_hooks.py --mode
  status` reports a dangling hook (point a state entry at a deleted path to
  see it flagged); the multi-checkout posture is written down where the
  hooks are documented; the reconcile fan-out is registry-driven (adding a
  hypothetical fourth intent touches a table, not a copied import block);
  #343 closed with the validated carrier.
- **Deferred proofs:** the goal artifact's slice 3 log names the first
  `Quality Core` remote run id + verdict (green, or triaged + repaired), the
  edit-time guard's observed flag (or the honest blocked-observation signal),
  and the #335 state after the next green scheduled run.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths --headroom` on every touched
  file; mirror byte-sync for any skill-script change; the touched test
  modules per slice (`test_staged_commit_gate_plan.py` family for slice 1,
  the host-hook suite for slice 2).
- For slice 1: the new pull appears in `--predict-commit --plan-only` for an
  adapter path and NOT for unrelated paths; measured cost recorded.

### High-Confidence Checks

- Full relevant test surface green per slice; broad gate
  (`run-quality.sh --read-only`) + changed-line producer
  (`run_slice_closeout.py --base --produce-mutation-coverage
  --verification-lock`) at the bundle boundary — cover new branches IN the
  introducing slice so the producer CONFIRMS (the standing repeat trap;
  4-lines-discovered last run). Fresh-eye `critique` at each slice boundary;
  issue-closeout drafts validated via the author-time preflight before the
  carrier commit.

### External Or Live Proof

- Slice 3 consumes the ALREADY-EXECUTED remote proofs (quality-core first
  run, scheduled mutation run for #335) read-only via `gh`. If CI repairs
  land, their remote re-verification is the next operator push lane — named
  here as the residual deferred proof, not run by this goal.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | #342: single-source adapter-vs-integration-schema validation pulled to commit time via the existing dispatcher; sibling set covered; doc table updated; issue closed via validated carrier | the two-owner seam burned ~25min this session and the family (#320→#335 lineage) keeps recurring; the timing-layers frame + dispatcher seam landed this week make it cheap now | seam decision recorded; tests per adapter pair + negative test; predict-commit shows the pull; cost measured <1s; #342 closed | planned |
| 2 | #343: dangling-hook liveness in status, multi-checkout posture decision documented, reconcile fan-out registry refactor; issue closed via validated carrier | three hooks now share the copied pattern — the third copy was this session; the dangling hazard got louder with a PostToolUse hook | liveness check + test; posture doc line; registry refactor with the 52-test suite green + per-host error isolation preserved; #343 closed | planned |
| 3 | Deferred-proof verification: quality-core first-run verdict (triage/repair if red), fresh-session edit-time guard observation, #335 auto-close check | the 2026-06-10 goal + release lane named these three as its non-claims; consuming them closes the loop the honest way | run id + verdict in slice log; guard flag observed (or honest blocked signal); #335 state recorded; any repairs committed locally with the re-push named deferred | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out. (Reminder from the 2026-06-10
  closeout: the summary `Routing:` line must be ONE line naming find-skills
  plus each triggered phase skill — wrapped lines fail the floor parser.)
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — this goal close-intends **#342** (slice 1) and
  **#343** (slice 2): record carrier (`direct-commit` expected) +
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof per
  slice; #335 is verify-only (auto-close owner is the mutation workflow) and
  #184 is context-only (`Issue closeout: n/a` for those two).

## Slice Log

### Slice 1 — seam decision (recorded before wiring)

- **Decision: extend `validate_adapters.py`**, not a new bridging validator in
  `_timing_layer_gates`. `validate-adapters` already runs as the SAME command at
  both the commit boundary (dispatcher `.agents/` path condition,
  `staged_commit_gate_plan.py:294`) and the broad gate (`run-quality.sh:397`) —
  extending it keeps one rule across all timings with zero new dispatcher
  wiring. A separate bridging validator would itself be a second validation
  owner for the same file (the exact two-owner seam #342 closes) and would need
  parallel broad-gate wiring to avoid verdict drift. Per-integration
  hardcoding stays pre-rejected (Non-Goals).
- **Verified sibling set (verify-first):** `usage-episodes`, `t-events`,
  `worktree` each pair `.agents/<name>-adapter.yaml` with
  `integrations/<name>/manifest.schema.json` (all three schemas are
  `additionalProperties: false`); `tools/` has a schema but NO
  `.agents/tools-adapter.yaml` (not a sibling, matching the disposition
  review); `locks/` has no schema. All three live adapters pass their schemas
  pre-wiring (verified directly).
- **Degradation contract:** schema file absent → no new validation (consumer
  repos inherit nothing); `jsonschema` import unavailable → skip; schema
  present but unreadable/broken JSON → hard `ValidationError` (a real defect,
  not a missing capability). `.agents/cautilus-adapters/*.yaml` excluded by
  the parent-dir guard.
- **Baseline cost:** `validate_adapters.py` ≈0.9s standing (resolver
  subprocesses); the schema step adds ~3 file reads + 3 jsonschema validations
  (~10ms). No new gate command, so no new budget entry — measured delta
  recorded at slice close.

### Slice 1: Slice 1 — #342 adapter-schema commit-time pull

- Objective: Run the integration manifest schema (the stronger validation owner) at every validate-adapters timing so a schema-rejected adapter edit blocks at pre-commit instead of failing slices later at the emitter; close #342.
- Why this approach: Extend validate_adapters.py (single-source seam): validate-adapters already runs as the same command at the commit-time dispatcher (.agents/ path condition) and the broad gate, so one rule covers all timings with zero new dispatcher wiring; parse with yaml.safe_load to match the runtime owner.
- Commits:
- What changed: scripts/validate_adapters.py (+ byte-synced plugins mirror), tests/test_validate_adapters_integration_schema.py (20 tests), docs/conventions/validator-timing-layers.md table row
- Alternatives rejected: New bridging validator via _timing_layer_gates (rejected: itself a second validation owner for the same file, needs parallel broad-gate wiring); per-integration hardcoded checks (pre-rejected: forked logic)
- Targeted verification: 20/20 new tests; 114 across touched families; live probe: forbidden key blocks at exit 1 naming the key; predict-commit shows validate-adapters for adapter paths only; cost ~0.07s inside the already-pulled command (~0.94s total, sub-second); mirror byte-synced; closeout draft validated (status draft_verified)
- Test duplication pressure: 20 new tests in a new module for a previously untested script (validate_adapters.py had zero direct tests); no duplication with test_usage_episodes_schema.py / test_t_events_schema.py, which validate example fixtures rather than the gate seam
- Critique: Fresh-eye bounded subagent (agentId a098aa449792d349f): SHIP-WITH-NITS, no blockers; nits folded (main() wiring subprocess test, missing-yaml degrade case, consumer-fallback asymmetry doc line); artifact charness-artifacts/critique/2026-06-10-342-adapter-schema-commit-pull-critique.md
- Off-goal findings:
- Lessons carried forward: The runtime owner and the gate must share the parse path (yaml.safe_load), or the pull itself creates a new two-parser drift; the first cut used the minimal adapter_lib parser and a test caught the divergence.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **This session's retro + dispositions:**
   `charness-artifacts/retro/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`
   (`## Waste` W1→#342, the slice-2 critique nits→#343, `## Next
   Improvements` I1–I4) and the disposition review
   `charness-artifacts/critique/2026-06-10-producer-base-nanchor-edittime-pushtag-ci-disposition-review.md`
   (the I1 "no existing single-source seam" analysis that scopes slice 1, and
   the tools/-is-not-a-sibling correction).
2. **Open issues:** corca-ai/charness#342 (Destination section = slice 1's
   contract), corca-ai/charness#343 (Destination = slice 2's contract),
   #184 (excluded, Non-Goals), #335 (verify-only, slice 3).
3. **Deferred proofs named by the prior goal:**
   `charness-artifacts/goals/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`
   `## Final Verification` ("Deferred live proof: the quality-core.yml remote
   CI execution") and its non-claims (fresh-session hook firing).
4. **Recent lessons:** `charness-artifacts/retro/recent-lessons.md` — the
   coverage confirm-not-discover repeat trap (cover new branches in the
   introducing slice), the closeout-draft contract preflight (use
   `check_artifact_surface_preflight --type closeout-draft` before the
   carrier), and the release-helper persistence note.
5. **Surfaces to touch:** `scripts/validate_adapters.py` or a new bridging
   validator + `scripts/staged_commit_gate_plan.py` (`_timing_layer_gates`) +
   `integrations/*/manifest.schema.json` (slice 1);
   `scripts/host_hook_install_lib.py` + `scripts/reconcile_usage_episodes_host_hooks.py`
   + `scripts/host_hook_{find_skills,skill_anchor_guard}.py` +
   `tests/test_usage_episodes_host_hooks.py` family (slice 2);
   `gh run list --workflow quality-core.yml` / `--workflow mutation-tests.yml`
   (slice 3, read-only).
6. **Doctrine:** `docs/conventions/validator-timing-layers.md` (the pull
   criteria + budget line slice 1 must satisfy and update).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Which next work (operator-directed: "이번 세션 교훈, handoff, 열린 이슈,
  최근 레슨 포함해서 다음 할 일").** Family: {#342; #343; deferred-proof
  verification; #184 product metrics; idle until CI verdict}. Chosen:
  **#342 + #343 + deferred proofs** — the three are exactly this session's
  structurally-dispositioned outputs plus the prior goal's named non-claims;
  together they close the loop the dispositions opened. Rejected: #184
  (third consecutive exclusion — product-level, needs its own
  ideation-shaped goal; bundling it as a slice would repeat the mistake the
  operator already declined twice); idle-until-CI (the CI verdict is one
  read-only check inside slice 3, not a blocker for slices 1–2).
- **Slice 1 seam (probe, not fixed).** Family: {extend `validate_adapters.py`
  to resolve integration schemas; a new small bridging validator wired via
  `_timing_layer_gates`; per-integration hardcoded checks}. Deferred to slice
  1 verify-first — but per-integration hardcoding is pre-rejected (forked
  logic, the exact anti-pattern the disposition review named).
- **Slice 2 registry shape (probe, not fixed).** Family: {data-table registry
  in `host_hook_install_lib`; a hooks/ package with one module per intent;
  leave the copies}. Deferred to slice 2 — leaving the copies is pre-rejected
  only for the RECONCILE fan-out (the issue's narrow ask); module layout
  stays free.
- **Activation timing.** This goal activates AFTER the v0.36 push/release
  lane completes, so slice 3's remote runs exist; if CI is still running at
  activation, slices 1–2 proceed first (no ordering dependency).

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- **Provenance:** self-critique by the shaping session (a fresh-eye plan
  critique runs at activation per the verification cadence).
- **Slice 1 could fork validation logic per integration (the anti-pattern the
  disposition review named).** Folded: single-source seam decision is a
  recorded slice-log step BEFORE wiring; per-integration hardcoding
  pre-rejected (Non-Goals + Interview Decisions).
- **Slice 1 could re-trip the #N-anchor/quality-package review loop.**
  Folded: the public-skill validation review re-trigger is named in
  Boundaries with the ack-with-recorded-decision pattern from this session.
- **Slice 2's registry refactor could silently change reconcile semantics.**
  Folded: per-host error isolation + byte-stable behavior of the three
  existing intents named as the floor, with the 52-test suite as evidence.
- **Slice 3 could quietly trigger new remote side-effects.** Folded:
  read-only `gh` consumption only; repairs local; re-push is the next
  operator lane (Boundaries + External side-effect scope).
- **Over-worry (raised, not folded):** that slice 3 is "not real work" — it
  is the prior goal's named non-claims becoming evidence; skipping it is how
  deferred proofs silently rot into assumed truths.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named