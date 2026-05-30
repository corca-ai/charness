# Achieve Goal: Remove the trivial-goal portability exemption (#255)

Status: active
Created: 2026-05-30
Activation: `/goal @charness-artifacts/goals/2026-05-30-255-remove-trivial-goal-exemption.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

Resolve #255 at the root: remove the size-based / marker-based exemption that lets a goal skip the portability sections (Context Sources, Interview Decisions, Plan Critique Findings), instead of patching the poisoned full-text `Single-slice goal:` scan. Delete `_TRIVIAL_GOAL_MARKER` and `is_non_trivial_goal()` from goal_artifact_lib.py and make `check_goal()` require the three portability section HEADINGS on every goal regardless of size (content may be `N/A — <reason>`; only deleting a heading is penalized). Retire the now-purposeless `_scrub_trivial_goal_marker` defense added downstream in the handoff auto-draft (#249), since with no marker there is nothing to poison. The poisoning bug then becomes structurally impossible rather than narrowly patched, and the deterministic gate gets simpler and ungameable.

## Non-Goals

- **Not** the issue's literal suggested fix (scope + anchor the `_TRIVIAL_GOAL_MARKER` scan to `## Slice Plan`). Considered and deliberately rejected in favor of removal — see Interview Decisions.
- **Not** enforcing portability section *content* (e.g. a prose classifier on whether sections are "really filled"). The gate stays structural — heading presence only — per the #253 deterministic-floor / no-prose-classification philosophy.
- **Not** removing `slice_plan_data_row_count()`. It is a row-count utility still referenced by the handoff auto-draft invariant tests; only the *exemption path* (`is_non_trivial_goal` + the marker) is removed. Slice 1 confirms it has no remaining production consumer before deciding to keep it as-is.
- **Not** rewriting historical artifacts (past goals, retros, critique notes that mention the marker). Those are immutable records of what happened; only *live* surfaces (docs, lifecycle reference, code) are reconciled.
- **Not** changing the empty-scaffold / auto-draft (#249) lifecycle outcome. The auto-draft already seeds all three portability headings, so it keeps passing the always-on check.
- **Not** pushing or closing GitHub #255 inside the run. Push of the local commits and the GitHub close are maintainer decisions (the repo already carries unpushed commits + an open #253); the run records that closing #255 is the documented next step.

## Boundaries

- **Phase barrier (`mutate → sync → verify → publish`):** every change under `skills/public/**` is synced to its `plugins/charness/skills/**` mirror *before* validators run. The #257 pre-commit `check_staged_mirror_drift.py` gate blocks staged source without its mirror, so sync is mandatory, not optional.
- **New gate semantics:** `check_goal()` requires the three portability H2 headings (`Context Sources`, `Interview Decisions`, `Plan Critique Findings`) on *every* goal. Content may be `N/A — <reason>`; only *deleting* a heading is penalized. The `check_goal` failure message must drop the `Single-slice goal:` exemption hint.
- **Backward-compat:** verified pre-flight that *zero* in-repo goals use the marker as an intended Slice-Plan exemption (only prose mentions exist), and the template seeds all three headings — so no grandfathering keyed on `Created` date is needed. Slice 1 still re-runs `check_goal_artifact.py` against existing goals to confirm none regress under the always-on check.
- **Determinism preserved:** no agent-judgment classifier is introduced. The change only *removes* an exemption branch; the remaining check is the same structural heading-presence test.
- **Length:** `goal_artifact_lib.py` is ~359 lines; removal should shrink it. Stay within the single-file ceiling and watch the `check_python_lengths --headroom` advisory (#256).
- **Scope of the scrub removal (Slice 2):** removing `_scrub_trivial_goal_marker` changes auto-draft output (quoted "single-slice goal" text is no longer rewritten to U+2011). That is acceptable and arguably better — verify only that no *other* auto-draft behavior depended on the scrub beyond the poisoning defense.

## User Acceptance

What the user can do to verify completion directly:

1. Craft a goal whose prose mentions "single-slice goal" **and** is missing one portability heading, then run `check_goal_artifact.py` on it — it now **flags the missing heading** (before this change the prose mention silently exempted it).
2. A goal carrying all three portability headings passes regardless of any "single-slice goal" prose anywhere in the body.
3. `grep -rn "Single-slice goal\|_TRIVIAL_GOAL_MARKER\|is_non_trivial_goal\|_scrub_trivial_goal_marker"` over *source* (skills + tests + docs, excluding `charness-artifacts/` history) returns no production/live references.
4. Full `pytest` suite is green and the `plugins/` mirror is in sync (no `check_staged_mirror_drift.py` failure).

## Agent Verification Plan

Expected proof cost: low (pure deterministic library + doc change). Expected test-duplication pressure: low–moderate — the dead `is_non_trivial_goal` tests are *removed* and replaced 1-for-1 with the new "prose can't exempt / missing heading fails" assertions, so net test count should stay flat or shrink.

### Low-Cost Checks

- Targeted `pytest tests/quality_gates/test_goal_artifact_lib.py tests/test_handoff_chunker_auto_draft.py`.
- `check_goal_artifact.py` against a crafted fixture (prose mention + missing heading → must flag) and against *this* goal artifact (dogfood — its own prose mentions the marker).
- `grep` residual-reference scan over source (acceptance check 3).
- Mirror-drift check on staged files before commit.

### High-Confidence Checks

- Full `pytest` suite (the change touches a gate that other tests exercise indirectly).
- The repo's standard quality gate via its documented entrypoint (lint / length-headroom / mirror), routed through a `quality` recommendation rather than ad hoc.

### External Or Live Proof

- **None applicable.** This is a deterministic library + docs change with no provider, network, live-host, or release surface. The After-phase report states explicitly that no live/provider/release proof was run because none applies (not "skipped").

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Remove the exemption from the core gate (`goal_artifact_lib.py`) + reconcile its docs | Root-cause fix; makes the #255 poisoning structurally impossible | Drops `_TRIVIAL_GOAL_MARKER` + `is_non_trivial_goal`; `check_goal` always checks the 3 headings; failure message + section comments updated; `test_goal_artifact_lib.py` dead tests removed and replaced with "prose can't exempt / missing heading fails" tests; `lifecycle.md` + `docs/prescribed-skill-closeout-contract.md` guidance rewritten; `plugins/` mirror synced; targeted tests green | **done** |
| 2 | Retire the now-purposeless downstream scrub (handoff auto-draft, #249) | With no marker there is nothing to poison; a silent text-rewrite with no purpose is dead weight | Drops `_scrub_trivial_goal_marker` + `_TRIVIAL_MARKER_PHRASE_RE` + call sites in `chunked_routing_auto_draft.py`; `test_handoff_chunker_auto_draft.py` poison/scrub tests rewritten to the new structural invariant; `docs/handoff-chunked-routing.md` updated; mirror synced; targeted tests green | **done** |

## Slice Log

### Slice 1: Remove exemption from core gate + reconcile docs

- Objective: Delete the size/marker trivial-goal exemption so check_goal requires the 3 portability headings on every goal; reconcile the docs that taught the removed mechanism.
- Why this approach: Root-cause removal makes the #255 full-text poisoning structurally impossible (no marker to poison) and simplifies the deterministic gate, vs the issue's narrower scope-the-scan patch.
- Commits:
- What changed: goal_artifact_lib.py: removed _TRIVIAL_GOAL_MARKER + is_non_trivial_goal(); check_goal() now always checks PORTABILITY_SECTIONS with a marker-free message; updated PORTABILITY_SECTIONS comment + slice_plan_data_row_count docstring (now test-only utility). test_goal_artifact_lib.py: dropped 3 dead is_non_trivial_goal/marker-exempt tests, added 4 always-on tests (size doesn't exempt; prose mention doesn't exempt; prose+headings passes; scaffold passes via template). Docs: lifecycle.md marker guidance, docs/prescribed-skill-closeout-contract.md (removed ### Trivial Goal Exemption + fixed ### Self-Test fixture path), docs/handoff-chunked-routing.md (reframed off is_non_trivial_goal). plugins/ mirror + marketplace manifests synced via sync_root_plugin_manifests.py.
- Alternatives rejected: Issue's literal patch (scope+anchor marker to ## Slice Plan): rejected — marker has 0 real use, redundant with template-seeded headings, still a footgun. Removing slice_plan_data_row_count: rejected (F4) — kept as a row-count utility the auto-draft invariant tests pin.
- Targeted verification: pytest tests/quality_gates/test_goal_artifact_lib.py -> 32 passed. Import smoke OK; is_non_trivial_goal gone; file 359->343 lines (under 360 ceiling, F5). DOGFOOD: this goal's own body has 10 'single-slice goal' prose hits yet check_goal_artifact.py returns ok=True (has the 3 headings) — old code would have exempted it. Mirror verified clean. (F3: full suite intentionally NOT run as slice-1 acceptance — auto-draft test file is expected red until Slice 2.)
- Test duplication pressure: Low — new tests reuse _goal_with_table/_PORTABILITY_BODY fixtures; net test count ~flat (removed 3 dead is_non_trivial_goal tests, added 4 always-on tests). No new fixture duplication introduced.
- Critique: Slice-0 plan critique (fresh-eye subagent a5f7cee941b1643b1) folded F1+F2 doc-scope blockers into this slice. Implementation fresh-eye critique runs at the bundle boundary after Slice 2 (the two slices are one cohesive change; reviewing the transiently-red mid-state would be lower-signal).
- Off-goal findings: None.
- Lessons carried forward: A fresh-eye plan critique caught that the stale-doc surface was 3 blocks in one file + a wrong fixture path, not the single line the plan named — doc blast-radius is easy to undercount.
- Metrics: when available

### Slice 2: Retire the now-dead downstream scrub (handoff auto-draft, #249)

- Objective: Remove _scrub_trivial_goal_marker + _TRIVIAL_MARKER_PHRASE_RE + its 5 call sites from chunked_routing_auto_draft.py; rewrite the auto-draft tests that referenced the deleted is_non_trivial_goal/scrub to the new structural invariant.
- Why this approach: Slice 1 removed the marker mechanism, so the scrub now defends nothing; a silent U+2011 text-rewrite with no purpose is dead weight that could mask a future regression.
- Commits:
- What changed: chunked_routing_auto_draft.py: dropped _TRIVIAL_MARKER_PHRASE_RE + _scrub_trivial_goal_marker; unwound the scrub from _quote_entry_body, _render_goal_body (x2), _render_context_sources, render_auto_draft_artifact (x2) — source-chunk text now renders verbatim, with a docstring noting why no scrub is needed. test_handoff_chunker_auto_draft.py: dropped test_single_slice_goal_marker_is_never_inserted; rewrote the poison test -> test_quoted_handoff_marker_prose_is_harmless (verbatim render, no U+2011, check_goal ok before+after slice rows); dropped the is_non_trivial_goal assertion from test_slice_plan_data_row_count_is_zero; updated module docstring. plugins/ mirror synced.
- Alternatives rejected: Keeping the scrub as defense-in-depth (the initial Before-phase lean): rejected once Slice 1 removed the marker concept — nothing left to defend, and a silent no-op rewrite is confusing dead weight.
- Targeted verification: pytest tests/test_handoff_chunker_auto_draft.py -> 15 passed. Residual-ref grep over source: only explanatory comments/docstrings + docs/handoff.md (F7, deferred to baton refresh). FULL SUITE (bundle boundary): 1870 passed, 4 skipped in 422s. Mirror verified clean.
- Test duplication pressure: Low — net test count -1 (removed 2 stale tests, added 1 consolidated invariant test); kept tests reuse the existing HandoffEntry/ChunkCandidate fixtures. No new duplication.
- Critique: Bundle-boundary fresh-eye implementation critique on the full two-slice diff runs next (covers both slices together; the slices are one cohesive change).
- Off-goal findings: None.
- Lessons carried forward: A downstream mitigation (#249 scrub) went fully dead the instant the root cause was removed — a root-cause fix should sweep its now-purposeless guards in the same change, not leave them as confusing dead weight.
- Metrics: when available

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- **GitHub issue #255** — `is_non_trivial_goal` full-text `Single-slice goal:` scan poisoned by body prose. Issue's suggested (non-prescriptive) direction was to scope the scan to `## Slice Plan`; this goal supersedes that with full removal.
- `skills/public/achieve/scripts/goal_artifact_lib.py` — `_TRIVIAL_GOAL_MARKER` (L66), `is_non_trivial_goal()` (L256–266), `check_goal()` portability branch (L343–351), `missing_portability_sections()` (L269–271).
- `skills/public/achieve/scripts/goal_artifact_disposition.py` — the #253 section-scoping precedent (`_section_body`, `find_disposition_optout`) the issue proposed mirroring; relevant as the *rejected* patch path.
- `skills/public/achieve/scripts/goal_artifact_template.md` — seeds all three portability headings (the fact that makes full removal safe for new goals and auto-drafts).
- `skills/public/achieve/references/lifecycle.md:91` — documents the `Single-slice goal: <reason>` marker-in-Slice-Plan intent being removed.
- `skills/public/handoff/scripts/chunked_routing_auto_draft.py` — `_scrub_trivial_goal_marker` (#249 downstream poisoning defense), Slice 2 target.
- Live docs to reconcile: `docs/handoff.md` (#255 next-session memo), `docs/prescribed-skill-closeout-contract.md:256`, `docs/handoff-chunked-routing.md:294,302`.
- **Pre-flight facts established this session:** the template seeds all 3 portability headings; `check_goal` verifies heading *presence* only (not content); a full scan of `charness-artifacts/goals/` found **zero** goals using the marker as an intended Slice-Plan exemption (only prose mentions).

## Interview Decisions

- **Resolution approach for #255.** Family: {patch the scan, remove the exemption}. Chosen: **remove**. Rejected "patch (scope + anchor the marker to `## Slice Plan`)" — the literal issue suggestion — because the marker has zero real use, is redundant with the template's seeded headings, and is a pure poisoning footgun; removal makes the bug *structurally impossible* and simplifies the deterministic gate. User framing: trivial goals never reach `/achieve`; the agent can keep/fill headings.
- **Removal depth.** Family: {remove the explicit marker only and keep slice-count auto-detection; remove the whole exemption so every goal keeps the 3 headings}. Chosen: **full removal**. Rejected "marker-only" because the only behavior it preserves is "a <2-slice goal may delete the portability headings" — a grey zone the user explicitly did not want — and the template seeds the headings, so full removal does not break the empty-scaffold / auto-draft lifecycle.
- **Fate of the downstream `_scrub_trivial_goal_marker` (#249).** Initially leaned "keep as defense-in-depth" under the patch framing; under full removal it defends nothing. Chosen: **remove**. Rejected "keep" because a silent text-rewrite with no remaining purpose is dead weight that could mask a future regression.
- **Enforce portability content or only heading presence?** Chosen: **heading presence only** (unchanged), consistent with #253's deterministic-floor philosophy. Rejected content classification — it over-fires or passes pure narration (the #253 round-2 finding).

## Plan Critique Findings

Slice-0 plan critique by a bounded fresh-eye subagent (general-purpose, agentId `a5f7cee941b1643b1`). Verdict: core engineering **sound** (removal verified safe); needed a doc-scope revision before implementing.

**Blockers folded into Slice 1 (doc scope expanded):**

- **F1** — `docs/prescribed-skill-closeout-contract.md` undercounted. Beyond line ~256 it carries a whole `### Trivial Goal Exemption` subsection (~270–283) describing the deleted mechanism, plus a `### Self-Test` block (~260–267) pointing at a non-existent fixture `tests/skills/test_goal_artifact_portability.py` (the real file is `tests/quality_gates/test_goal_artifact_lib.py`). → Slice 1 rewrites/removes both blocks.
- **F2** — `docs/handoff-chunked-routing.md:302` prose ("the trivial-goal exemption applies cleanly") and the ~294 `is_non_trivial_goal` link go false. → Slice 1 reframes to "the auto-draft seeds all 3 portability headings, so the always-on check passes at write time" (verified true), not just a line touch.

**Over-worries (raised, not folded):**

- **F3** — Slice 1 alone reds `tests/test_handoff_chunker_auto_draft.py` (it calls the deleted `is_non_trivial_goal`). Both slices ship in one task. Disposition: Slice 1's "targeted tests green" = `test_goal_artifact_lib.py` only; the **full suite is a bundle-boundary (After-phase) gate**, not Slice-1 acceptance. Pre-commit hooks do not run pytest, so the Slice-1 commit is not blocked.
- **F4** — after removal, `slice_plan_data_row_count` has no production caller (test-only). Disposition: keep it as a stable public row-count utility (auto-draft invariant tests pin it); the note must say "now test-only," not imply a live consumer.
- **F5** — `goal_artifact_lib.py` is 358/360 (hard ceiling). The reviewer's Slice-1 simulation dropped it to 341 — removal *fixes* the thin margin. Disposition: keep the new failure message short; do not net-add lines.

**Verified safe (headline risk cleared):**

- **F6** — no new regression. Only `2026-05-27-226-reviewer-tier-policy.md` lacks the 3 headings, but it *already* fails `check_goal` today (pre-existing); no live gate scans the goals corpus through `check_goal`; the CLI consumes `check_goal()`'s dict (no message-text dependency); `_scrub_trivial_goal_marker` has no external importer.

**Deferred:**

- **F7** — `docs/handoff.md:41–45` still describes the rejected literal fix. Disposition: handled in the After-phase handoff baton refresh (the `/handoff` pruning surface), not a Slice-1 code edit.

## Off-Goal Findings

_None yet._ (Historical artifacts that mention the marker are intentionally left immutable — not a finding to action.)

## Final Verification

_Pending: completed in the After phase — self-verification, residual risk, and explicit non-claims (including that no live/provider/release proof applies)._

## User Verification Instructions

_Pending: finalized in the After phase. Expected shape:_

```bash
# 1. prose mention no longer exempts a missing heading
#    (build a goal with a "single-slice goal" prose mention and no Interview Decisions heading)
python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path <fixture>   # flags missing heading

# 2. no residual production references
grep -rn "Single-slice goal\|_TRIVIAL_GOAL_MARKER\|is_non_trivial_goal\|_scrub_trivial_goal_marker" \
  skills tests docs   # no live hits

# 3. suite + mirror
pytest -q
```

## Auto-Retro

_Pending: produced by `retro` in the After phase; substantive findings narrated inline at closeout (not collapsed to a path reference)._
