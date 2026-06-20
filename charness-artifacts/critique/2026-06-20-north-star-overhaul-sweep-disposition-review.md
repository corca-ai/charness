# Disposition Review — North-Star Overhaul Sweep (rung-2 honesty audit)

Goal: `charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md`
Retro: `charness-artifacts/retro/2026-06-20-north-star-overhaul-sweep.md`
Reviewer: bounded fresh-eye disposition reviewer (rung 2, distinct evidence channel)
Date: 2026-06-20

This is the human-audited honesty layer. Rung 1 only checks the disposition lines
are present and well-formed; below I judge **substance** — does each surfaced
improvement get a real home, or is it hand-waved? I verified every load-bearing
claim against the actual index/code/script behavior, not against an artifact
re-read.

## Surfaced improvements audited (from the retro)

Source sections: `## Next Improvements` (3 items), `## What Created Waste` (3
items, the same three traps the Next Improvements abstract), `## Sibling Search`
(the transferable deferred body-redesign).

| # | Surfaced improvement | Goal disposition | Verdict |
| --- | --- | --- | --- |
| NI-1 | Gate-failure triage must use the exact enforcement invocation | `out-of-scope` (process lesson) → claimed "captured in the wired recent-lessons retro digest, registered source #241" | **weak** |
| NI-2 | Skill-body cut needs a pre-cut lossless+contract-safe check (WS-B instrument gap) | `out-of-scope` → "belongs to the deferred body-redesign follow-on"; carried in retro + S3 slice log + Operator Decision Queue | **verified** |
| NI-3 | Bloat diagnoses are hypotheses to verify per-body, not mandates to cut | `out-of-scope` (process lesson) → "captured in the wired retro digest" | **weak** |
| SF-1 (Structural follow-up) | Deferred impl/debug/quality/achieve body redesign + the pre-cut instrument (the transferable waste) | `repo-local guard`: retro `## Next Improvements`/`## Sibling Search` + S3 slice log; tracked issue deferred to Operator Decision Queue | **verified** |

## Honesty checks (what I verified and how)

### Check A — the "wired retro digest / registered source #241" claim (NI-1, NI-3): PARTIALLY FALSE

The disposition for the three process lessons rests on a single load-bearing
claim: they are "captured in the wired recent-lessons retro digest
(`...sweep.md`, registered source #241 via `refresh_recent_lessons.py`)". I tested
both halves.

- **Counted as a source: TRUE.** `lesson-selection-index.json` shows
  `source_artifact_count: 241` (git diff: was `240` / `as_of_source_date 2026-06-19`,
  now `241` / `2026-06-20`). Driving the lib (`scripts/recent_lessons_lib.py`)
  against the real retro dir confirms `len(scanned artifacts) == 241` and the
  sweep retro IS in the scanned set. So "registered source #241" is literally true
  as a *file count* (the count = `len(artifacts)` from `output_dir.glob("*.md")`,
  which hits the filesystem and so counted the still-untracked sweep retro).

- **Lessons actually captured into the digest: FALSE.** I searched the index and
  found ZERO candidates sourced from the sweep retro:
  `grep -c north-star-overhaul-sweep lesson-selection-index.json` = 0; programmatic
  scan over all 1156 candidates → "candidates sourced from sweep retro: 0". Root
  cause, verified in code: the sweep retro's `## Next Improvements` uses **numbered
  list items** (`1.`/`2.`/`3.`), but `_bullet_items()`
  (`scripts/recent_lessons_lib.py:81-94`) extracts ONLY lines starting with `- `
  (dash). Numbered items are silently dropped, so none of the three lessons become
  digest candidates. Re-running `_collect_lesson_candidates` over the live dir
  reproduces this (0 sweep candidates). The three lessons therefore do NOT appear
  in `recent-lessons.md` and will NOT be surfaced to a future session by the
  selection policy — the exact "carry the lesson forward" purpose the
  out-of-scope disposition leans on.

  Net: the disposition is honest that the file is a registered/counted source, but
  overstates "captured in the wired digest" — the wiring counted the file and
  dropped its lessons. This is prose-memory-in-a-validated-file dressed as digest
  capture. It is *weak* rather than *not-disposed* because the retro file does
  exist, validates, and is committed-pending (a real repo-local home a human can
  read), and the lessons are also restated in the goal's S1/S3 `Lessons carried
  forward` slice-log fields.

### Check B — retro artifact exists, registered, validates: PASS

- File exists (`4404` bytes), and `validate_retro_artifact.py --paths ...sweep.md`
  → "Validated 1 retro artifact(s)", exit 0.
- Currently `??` untracked + the index `M` (refreshed). These must commit with the
  closeout (per the repo's "treat charness-artifacts changes as repo state"
  contract). Flag: until committed, the "registered source" is working-tree-only.

### Check C — Operator Decision Queue carries the deferred items: PASS

Both deferral claims map to real queue entries (goal lines 167-191):
- The "deferred body-redesign follow-on" tracked-issue filing is the second queue
  entry (owner: operator; why-deferred: external write not approved; unblock:
  operator approves `issue` filing or starts the follow-on goal). This backs SF-1
  and the NI-2 "deferred to follow-on" claim honestly.
- The live GitHub R2 close is the first queue entry (separate, also honest).

### Check D — Structural follow-up has a real repo-local home (SF-1): PASS

The transferable waste (deferred impl/debug/quality/achieve redesign + the pre-cut
lossless+contract-safe instrument) is genuinely recorded in three durable places I
read: retro `## Sibling Search` (lines 77-81) + `## Next Improvements` item 2
(lines 72-73) + the goal S3 slice log (lines 326-337, "deferred with cause" +
"Lessons carried forward"). A follow-on session can reconstruct and resume it.
This is a real disposition, not a drop.

## Headline non-claim sanity-check vs. the slice log (all backed by committed code)

- **S1 (R2 escape closed, no terminal-green gate): HONEST.**
  `issue_verify_closeout_body.py` carries `evaluate_behavioral_verdict`,
  `evaluate_ai_provenance`, `has_ai_provenance_marker`, and the `Behavior #N:`
  grammar — presence/form floors, not an aggregate green. Committed `8c6fc16a`.
- **S2 (R1 grammar de-dup, tests green): HONEST.** Shared substrate
  `goal_artifact_floor_grammar.py` exists (4 grammar fns), committed `c10a5051`.
  (I did not re-run the 380 floor tests this pass; the S2 critique line records
  them green via a distinct channel, and the substrate + re-exports are present.)
- **S3 (graft + find-skills cure; deeper redesign deferred with cause — NOT
  shaved): HONEST.** `quality/references/unit-test-quality.md` = 82 lines (under
  cap); `find-skills/SKILL.md` = 198 lines with neg-directive count = 4 (matches
  the "7→4" endpoint). Committed `f496812b`. The deferral is recorded with cause,
  not a silent shave.

No overclaim found in the S1/S2/S3 headline non-claims.

## Overclaims found

1. **NI-1 / NI-3 "captured in the wired recent-lessons retro digest"** — overstated.
   The file is counted as source #241 but its three numbered-list lessons are
   dropped by `_bullet_items` (dash-only) and never enter the digest candidates or
   `recent-lessons.md`. The lessons are NOT actually wired into the forward-carry
   surface the disposition cites. (Falsifiable: index has 0 sweep candidates;
   the lessons use `1.`/`2.`/`3.`, not `- `.)

## Overall verdict

**The Auto-Retro dispositions every surfaced improvement (no improvement is
dropped: NI-2 + SF-1 verified; NI-1 + NI-3 weak-but-homed) — but ONE disposition
claim is partially dishonest.** NI-1/NI-3 are dispositioned as out-of-scope and DO
have a readable repo-local home (the committed-pending retro + slice-log
fields), so they are not prose-only; however the specific mechanism cited ("wired
retro digest capture") is overstated because the numbered-list format silently
excludes them from the digest pipeline. Overall: **PASS WITH ONE CORRECTION** —
acceptable to close, but the digest-capture claim should be softened to "recorded
in the retro + slice log (note: numbered-list lessons are not auto-surfaced by the
digest)", or the retro's `## Next Improvements` should be reformatted to dash
bullets so the wiring claim becomes true. Also ensure the untracked retro + the
refreshed index are committed with the closeout.
