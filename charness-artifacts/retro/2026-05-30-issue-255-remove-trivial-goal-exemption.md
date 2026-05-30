# Retro — #255 remove trivial-goal portability exemption

Mode: session

## Context

Reviews the `/achieve #255` goal run: resolving the `is_non_trivial_goal`
full-text marker-poisoning bug. Mid-Before-phase the user reframed the goal from
the issue's literal "scope the scan" patch to **removing the size/marker
exemption entirely**. Shipped as two slices (core gate + downstream scrub
retirement), two fresh-eye subagent critiques, full suite green. What matters
next: push the now-8 local commits and close GitHub #255 + #253 (maintainer).

## Evidence Summary

- Goal artifact `charness-artifacts/goals/2026-05-30-255-remove-trivial-goal-exemption.md` (slice logs, decisions, critique findings).
- Two bounded fresh-eye subagent critiques: plan (`a5f7cee941b1643b1`) and implementation (`abb898bdb872afa09`).
- Full suite: 1870 passed, 4 skipped (422s). Targeted: `test_goal_artifact_lib.py` 32 passed; `test_handoff_chunker_auto_draft.py` 15 passed.
- Host-log probe `charness-artifacts/probe/2026-05-30-issue-255-remove-trivial-goal-exemption.json` (claude host detected; token counts available, turn/tool-call derivable; exact counts not tabulated — recorded as available, not fabricated).

## Waste

- **Doc blast-radius undercounted — twice, in the same file.** The Before-phase
  plan named only one line of `docs/prescribed-skill-closeout-contract.md`. The
  plan critique (fresh-eye #1) caught a whole `### Trivial Goal Exemption`
  subsection + a wrong `### Self-Test` fixture path (F1). The implementation
  critique (fresh-eye #2) then caught a *third* stale line in the *same* doc —
  the "non-trivial goal (defined below)" lead-in (IC-1) — that both I and the
  first critique missed. Same doc surface, three passes. Cost was low (no code
  rework; the gates caught it before close), but it is a clear under-scoping of
  doc reconciliation: I edited the line the issue/plan pointed at instead of the
  *concept* across the file.
- **Minor (phase-appropriate, not real waste):** the full suite legitimately
  takes ~7 min (it spawns the quality gate as a subprocess fixture); piping it
  through `| tail` buffered all output, so progress polling read blind. Writing
  raw output to a file (no `tail`) would have shown progress. Noted, not
  counted as waste — the run itself was the correct bundle-boundary gate.

## Critical Decisions

- **Pivot to full removal over the issue's literal patch.** The decision turned
  on three facts gathered *before* committing to the approach: the template
  already seeds all three portability headings; `check_goal` checks heading
  *presence* only; and a corpus scan found **zero** goals using the marker as an
  intended exemption. Those facts made removal both safe and strictly simpler,
  and made the poisoning bug structurally impossible. Good decision hygiene —
  facts first, then approach.
- **Flipped the #249 scrub from "keep (defense-in-depth)" to "remove."** The
  initial Before-phase lean was to keep it; once full removal landed it defended
  nothing, so it was swept in slice 2. Avoided leaving confusing dead weight.
- **Bundled the two slices with the full suite deferred to the boundary (F3).**
  Treated the transient red window (slice 1 reds the auto-draft test file) as
  expected, not a failure — so I didn't churn trying to keep a full suite green
  mid-bundle.

## Expert Counterfactuals

- **Technical-writer / single-source-of-truth lens (information architecture).**
  This lens treats "where does this *concept* live?" as the first question, not
  "which line does the ticket name?". It would have grepped the concept's
  natural-language names (`trivial`, `exemption`, `defined below`,
  `single-slice`) across `docs/` *before* the first doc edit, collapsing the
  three-pass doc reconciliation into one. This is the sharpest lens because the
  session's only real waste was concept-residue, not decision quality.
- (Klein/Kahneman decision-under-uncertainty lens considered but *not* forced:
  the core pivot decision was already handled well — facts before approach — so
  a decision lens would add little. The IA lens produces the different action.)

## Next Improvements

- **memory** — When a change removes or renames a *concept* (not just a code
  symbol), grep the concept's natural-language name(s) across docs/skills up
  front to scope reconciliation in one pass. Symbol-grep finds the code; only
  concept-grep finds the prose that teaches the removed idea. (Captured here +
  recent-lessons digest.)
- **workflow (applied at closeout)** — Refresh `docs/handoff.md`'s #255 memo
  from the rejected "scope the scan" framing to the shipped "removed the
  exemption" resolution (F7), as part of the After-phase baton refresh.

## Sibling Search

The waste pattern — *removing a code symbol but leaving the concept's
natural-language name in prose/docs* — is transferable (it could recur in any
skill or doc surface on a future concept removal). Four-axis scan of *this*
change's surface for leftover residue:

- **by-symbol:** `is_non_trivial_goal` / `_TRIVIAL_GOAL_MARKER` /
  `_scrub_trivial_goal_marker` / `_TRIVIAL_MARKER_PHRASE_RE` — no live source
  refs remain (only past-tense explanatory comments).
- **by-concept-word:** `trivial` / `exemption` / `single-slice` / `defined
  below` across `docs/` + `skills/` — remaining hits are intentional past-tense
  removal notes; the one dangling lead-in (IC-1) was fixed.
- **by-doc-surface:** the three docs that taught the mechanism
  (`lifecycle.md`, `prescribed-skill-closeout-contract.md`,
  `handoff-chunked-routing.md`) reconciled; `docs/handoff.md` deliberately
  deferred to the baton refresh (F7).
- **by-test:** the dead `is_non_trivial_goal` assertions removed; new tests lock
  the always-on behavior.

Decision: **memory** (the up-front concept-grep habit) — no separable code/gate
follow-up filed, because the two fresh-eye critiques already caught the residue
in this run, so a deterministic "concept-residue" gate would be disproportionate
to the self-correcting cadence already in place.

## Persisted

Persisted: yes (see persist path below).
