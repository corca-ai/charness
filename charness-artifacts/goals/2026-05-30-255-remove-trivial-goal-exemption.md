# Achieve Goal: Remove the trivial-goal portability exemption (#255)

Status: draft
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
| 1 | Remove the exemption from the core gate (`goal_artifact_lib.py`) + reconcile its docs | Root-cause fix; makes the #255 poisoning structurally impossible | Drops `_TRIVIAL_GOAL_MARKER` + `is_non_trivial_goal`; `check_goal` always checks the 3 headings; failure message + section comments updated; `test_goal_artifact_lib.py` dead tests removed and replaced with "prose can't exempt / missing heading fails" tests; `lifecycle.md` + `docs/prescribed-skill-closeout-contract.md` guidance rewritten; `plugins/` mirror synced; targeted tests green | planned |
| 2 | Retire the now-purposeless downstream scrub (handoff auto-draft, #249) | With no marker there is nothing to poison; a silent text-rewrite with no purpose is dead weight | Drops `_scrub_trivial_goal_marker` + `_TRIVIAL_MARKER_PHRASE_RE` + call sites in `chunked_routing_auto_draft.py`; `test_handoff_chunker_auto_draft.py` poison/scrub tests rewritten to the new structural invariant; `docs/handoff-chunked-routing.md` updated; mirror synced; targeted tests green | planned |

## Slice Log

_Execution has not started. Populated by `append_slice_log.py` after each slice during the During phase._

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

_Produced by the slice-0 plan critique at activation (`/goal`), via the `critique` skill with a bounded fresh-eye reviewer; findings + dispositions recorded here during the During phase._ Angles to probe:

- Does always-requiring the three headings regress any existing in-repo goal, or the #249 auto-draft path?
- Are there non-test production consumers of `is_non_trivial_goal` / `slice_plan_data_row_count` not surfaced by the pre-flight grep?
- Does removing the scrub change auto-draft output in a way a test depends on *beyond* the poisoning assertion?
- Line-length headroom of `goal_artifact_lib.py` after the removal.

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
