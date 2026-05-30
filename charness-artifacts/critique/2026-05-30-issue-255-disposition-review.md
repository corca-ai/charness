# Rung-2 Disposition Review — Goal #255 (remove trivial-goal portability exemption)

**Goal under review:** `charness-artifacts/goals/2026-05-30-255-remove-trivial-goal-exemption.md`
**Retro (source of improvements):** `charness-artifacts/retro/2026-05-30-issue-255-remove-trivial-goal-exemption.md`
**Reviewer disposition:** FRESH-EYE, adversarial, read-only. Rung 2 of the #253 improvement-disposition gate, applied to #255. Default to flagging when a disposition looks weak.

Tests whether the goal's `## Auto-Retro` honestly disposes every improvement its retro
surfaced (#253 rule: prose-only retro memory is NOT a valid `applied:` disposition; an
`applied:` must be a real change with teeth, not a memory note dressed up).

## Per-Improvement Verdict

| # | Improvement (from retro) | Claimed disposition (Auto-Retro) | Verdict | Evidence + recommended action |
|---|---|---|---|---|
| 1 | **memory** — concept-grep the removed concept's natural-language name(s) across docs/skills up front when removing/renaming a concept | **memory (captured)**, explicitly **NOT** a separable `applied:`/`issue` item | **SOUND** | This is honestly classified, not dressed-up-memory-as-`applied:`. It correctly refuses to self-label the memory write `applied:` (the exact #253 trap). The "no deterministic concept-residue gate filed" call is proportionate, not a dodge: a concept-residue gate is genuinely hard to build deterministically (it would have to distinguish intentional past-tense removal notes from live stale prose — i.e. exactly the prose-classification the goal's own Non-Goals reject), and two fresh-eye critiques already caught all three stale spots this run. Calling it "not applied" is the correct anti-token-theater move. **No action.** |
| 2 | **workflow** — refresh `docs/handoff.md`'s #255 memo from the rejected "scope the scan" framing to the shipped "removed the exemption" resolution (F7) | **applied** at closeout (After-phase baton refresh edits the memo) | **WEAK — apply is still PENDING, label is false at review time** | The check the brief demanded was run, and it fails: `docs/handoff.md` lines 41–45 **still describe the rejected fix verbatim** — "#255 ... good `/achieve` candidate ... fix: scope the `_TRIVIAL_GOAL_MARKER` scan to the `## Slice Plan` section." `git status --short docs/handoff.md` shows the file is **unmodified**; `git log` shows no #255 closeout/baton-refresh commit; the residual-symbol grep even surfaces `docs/handoff.md:41` and `:43` as live `is_non_trivial_goal` / `_TRIVIAL_GOAL_MARKER` references. So the disposition labels as **`applied`** an edit that has **not happened** — this is the "token-theater 'applied' claim" the gate exists to catch. **Action: either perform the handoff.md memo edit now (rewrite lines 41–45 to the shipped full-removal resolution) and then the `applied` label is true, or re-label to `will-apply`/pending. As written, `applied` is dishonest.** |

## Dropped-improvement check

The retro's `## Next Improvements` lists exactly two items (the memory concept-grep; the
workflow handoff refresh) and its `## Sibling Search` resolves to **memory, no separable
follow-up** — which is the *same* item as disposition #1, not a third. Both are carried
into the Auto-Retro. **No improvement was silently dropped.** Off-Goal Findings is
genuinely empty (historical artifacts left immutable is a stated non-goal, not an
un-disposed finding).

## Bottom-line verdict

**Coverage is complete (2/2 surfaced improvements disposed, none dropped), but the
dispositions are NOT honest enough to flip the goal to `complete` as written: disposition
#2 must be re-dispositioned first.** Its `applied` label is false — `docs/handoff.md`
still carries the rejected "scope the scan" memo and is unmodified in git, so the baton
refresh it credits has not happened. Disposition #1 is SOUND. Fix #2 by either making the
handoff.md edit now (turning `applied` true) or re-labeling it pending.
