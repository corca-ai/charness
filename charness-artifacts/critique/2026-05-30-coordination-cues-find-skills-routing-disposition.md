# Disposition Review — coordination-cues-find-skills-routing

Fresh-eye audit (rung 2 of the #253 improvement-disposition gate) of the
`## Auto-Retro` dispositions in
`charness-artifacts/goals/2026-05-30-coordination-cues-find-skills-routing.md`
against the surfaced improvements in
`charness-artifacts/retro/2026-05-30-coordination-cues-find-skills-routing.md`
(`## Next Improvements` + `## Sibling Search`). Goal slug:
`coordination-cues-find-skills-routing`.

## Per-Improvement Verdicts

1. **workflow — run `scripts/run_slice_closeout.py` (the pre-commit gate
   aggregate) before the first commit on a multi-validator-family slice.**
   → **dispositioned** (legitimately-claimed already-existing teeth). Verified:
   - `scripts/run_slice_closeout.py` exists (17KB, dated 2026-05-30) and is a
     real aggregate — it maps changed paths to matched surfaces, executes the
     per-surface gate commands (PASS/FAIL `executed_commands`), and emits
     near-limit headroom warnings + cautilus planning. Not a stub.
   - The pre-commit hook family is real and active: `core.hooksPath=.githooks`,
     `.githooks/pre-commit` runs ruff, `check_python_lengths`,
     `validate_attention_state_visibility`, `check_staged_mirror_drift`,
     `validate_skills`, `run_evals`, `check_doc_links`, and `check-markdown.sh` —
     i.e. exactly the gate families the retro names, none of which run under
     `pytest tests/`.
   - `docs/conventions/implementation-discipline.md:10` already prescribes
     running `run_slice_closeout.py --repo-root .` before commit.
   The disposition's "no new gate is warranted; the teeth fired and blocked every
   non-compliant commit; the miss was sequencing" is accurate. Correctly NOT an
   issue (Sibling Search: "existing tool, run it earlier"). Not prose-only.

2. **memory — "pre-commit gate family ≠ `pytest tests/`; a length-neutral string
   reword can still break `validate-attention-state-visibility`; re-sync the
   mirror after any post-sync source edit."** → **dispositioned** (applied as a
   real, self-surfacing memory fold). Verified:
   - The lesson is present in `charness-artifacts/retro/recent-lessons.md:20`
     under `## Next-Time Checklist`, sourced to this retro.
   - This is not decaying free-prose: `scripts/recent_lessons_lib.py` auto-builds
     the checklist from each retro's `## Next Improvements` section, recency- and
     recurrence-ranked into `lesson-selection-index.json` (505KB, refreshed
     2026-05-30 19:12). The next session reads `recent-lessons.md` before
     changing repo operating contracts (CLAUDE.md mandate), so the lesson
     self-surfaces. Genuine fold, not hand-waved. (The literal "fold … into
     recent-lessons.md" wording is the carried-through retro bullet, not evidence
     the fold is still pending — the fold is mechanically present and selected.)

## Coverage Check

The retro's only actionable improvements are these two (`## Next Improvements`).
`## Sibling Search` explicitly concludes no new gate is warranted and "Not a
new-issue candidate" — correctly resolved into the workflow disposition + memory
fold above, not an undispositioned thread.

## Overall Verdict

**all-dispositioned** (2/2; 0 undispositioned). No "applied" claim was found to
be false: `run_slice_closeout.py` exists, the `.githooks/pre-commit` family is
real and covers the named gates, and the recent-lessons fold is genuinely present
and self-surfacing.
