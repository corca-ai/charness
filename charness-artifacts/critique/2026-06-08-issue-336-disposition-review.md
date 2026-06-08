# Issue 336 / workflow-ergonomics bundle — disposition + closeout review
Date: 2026-06-08

Fresh-eye, read-only review of the `achieve` workflow-ergonomics bundle goal closeout (`charness-artifacts/goals/2026-06-08-workflow-ergonomics-goal-slot-and-authoring-friction.md`), the cited retro, the #336 resolution critique and closeout body, and the four shipped commits (`cead7949`, `a101e716`, `138366c1`, `297d52ab`). Verified via `git show`/`git diff`, source inspection, and `python3 -m pytest`. No index or worktree mutation performed. (Reviewer: fresh-eye subagent a43984bf6f9277169.)

## Mandate 1 — Disposition review (rung 2)

The retro's `## Next Improvements` has exactly two entries; both are dispositioned `applied — persisted to recent-lessons`. There are no `issue #N` dispositions and therefore no `novel:` lineage claims to falsify — confirmed (the `## Sibling Search` correctly records `n/a — habit lesson, no code sibling to fix this run`, consistent with both improvements being memory-only).

Per-improvement verdict:

- **Improvement 1 — "cover normalization/guard branches in the introducing slice"** (workflow/memory; treat a new normalization branch or new guard line as a same-slice test obligation). Goal `## Auto-Retro` claims `applied — persisted to recent-lessons this run`. **Verdict: DISPOSITIONED but the persistence is PARTIAL / mislabeled.** What actually landed in `charness-artifacts/retro/recent-lessons.md` for this run is two `## Repeat Traps` entries (the backward-looking "Changed-line coverage round-trip" waste record and the "Invalid-adapter test first miss") plus the retro added to `## Sources` and ingested into the candidate pool (`lesson-selection-index.json`). It did NOT land as a forward-looking `## Next-Time Checklist` obligation. The retro's Sibling Search claim that the lesson "generalizes the existing 'anticipate the no-increase ratchets' line by naming the specific trigger… folded into the signal" overstates what happened: the existing ratchet checklist line is about at-cap SKILL.md core-headroom / boundary-bypass, a different subject, and was not edited.

- **Improvement 2 — "keep the producer-first guardrail and the critique enum legend" (positive, keep)**. Goal claims `applied — recorded in recent-lessons as confirmed-effective habits`. **Verdict: DISPOSITIONED, honest, no teeth needed.** The existing producer-first checklist line and the critique-enum-authoring line already carry these as Next-Time Checklist signals; "keep these" is the correct disposition and nothing is overstated.

Teeth check: improvement 1 is the one to flag — it is a real Repeat-Trap memory entry and a pooled candidate (not prose-only-with-no-teeth), but the goal/retro present it as a Next-Time workflow signal when only the waste-record form persisted. Neither improvement maps to a code-site change, so the absence of a code fix is correct.

## Mandate 2 — Closeout cross-slice review

- **Cross-slice drift / behavior-preservation:** the three fixes are independent (different surfaces) and do not contradict each other or the goal Boundaries. "Behavior-preserving / verdicts unchanged" holds across all three. Slice 2's scaffold constants exactly match the validator frozensets (drift-test pinned); the dogfood "first-try critique" claim is real (`Validated 1 critique artifact(s)`). Slice 3's `main()` → `execute_publish_plan` extraction is byte-identical in the moved body; the dry-run/`--resume` branches are preserved; prep reuses the same `update_instructions_version_blocker` + version helpers, so its staleness verdict cannot diverge and the stub embeds the target version verbatim. All four files byte-synced to the `plugins/` mirror; 28 touched-module tests pass.
- **Closeout-state taxonomy:** accurate and not overclaimed. `carrier` is the honest reached level; `pushed-ci`/`issue-closed` are correctly NOT claimed; #336 correctly OPEN pending push.
- **#336 closeout body:** accurate. JTBD/Boundary/Resolution brief/Implementation/Prevention match what shipped; correctly carries `Close #336`.
- **Coordination floors:** honest. `Release: n/a` is correctly reasoned (touched release code, but no release cut — the right test is "did we cut a release"). Gather/Routing/Issue closeout accurate.
- **Host-runtime proof:** the bound "Host log probe" is a metrics-availability probe, not a direct slot-empty observation; the slot-empty determination rests on the `upsert_goal.py`-pure-file-I/O argument + the in-session observation, with the host-auto-activation residual recorded as a conditional non-claim (defensible; a reader should not mistake the probe for live slot-state proof).

## Findings

1. **SHOULD-FIX** — Disposition overclaim for retro improvement 1. The goal `## Auto-Retro` and the retro say the "cover normalization/guard branches in-slice" signal was `applied — persisted to recent-lessons` and "folded into" the existing ratchet checklist line. In reality `recent-lessons.md` carries it only as a backward `## Repeat Traps` entry, and the ratchet line was not edited. Either add the same-slice-test-obligation as a `## Next-Time Checklist` line, or downgrade the disposition wording to "recorded as a Repeat-Trap waste signal (candidate-pooled)". Files: `recent-lessons.md`, the retro (Next Improvements + Sibling Search), the goal (Auto-Retro).

2. **NIT** — "persisted to recent-lessons this run" is true only in the uncommitted working tree; `recent-lessons.md` + `lesson-selection-index.json` are unstaged at HEAD. Ensure the carrier commit includes `recent-lessons.md`, `lesson-selection-index.json`, the goal, the retro, the closeout body, and the probe, or the disposition silently regresses to memory-only.

3. **NIT** — The bound "Host log probe" is a metrics-availability capability probe, not a slot-empty host observation; the slot-empty claim is correctly hedged elsewhere, so this is a labeling nuance, not a falsehood.

4. **OVER-WORRY** — Slice 3 refactor risk fully retired (byte-identical moved body, branches preserved, prep verdicts cannot diverge). No action.

5. **OVER-WORRY** — Over-bundle risk: one theme, each small/structural, each SHIP-reviewed, no cross-slice contradiction. No action.

## Verdicts

Disposition verdict: all improvements dispositioned (2/2; both `applied`, no `issue #N`/`novel:` to falsify) — but improvement 1's wording overstates its teeth (Repeat-Trap record + pooled candidate, not a Next-Time-Checklist obligation).

Closeout verdict: SHIP-WITH-FIXES — the three fixes are real, behavior-preserving, mirror-synced, and test-backed; the #336 closeout body is accurate and carries `Close #336`; the closeout-state taxonomy and coordination floors are honest. Gate items before flip: Finding 1 (correct the improvement-1 disposition wording) and Finding 2 (stage the durable memory files in the carrier commit).
