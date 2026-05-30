# Rung-2 Disposition Review — Goal 253 (improvement-disposition closeout gate)

**Goal under review:** `charness-artifacts/goals/2026-05-30-253-improvement-disposition-gate.md`
**Retro (source of improvements):** `charness-artifacts/retro/2026-05-30-issue-253-disposition-gate.md`
**Reviewer disposition:** FRESH-EYE, adversarial, read-only (this is rung 2 of the #253 gate, dogfooded on its own goal).

This review records a per-improvement verdict for every improvement the cited retro
surfaced, and judges whether the goal's `## Auto-Retro` genuinely disposes each one
per the **#253 rule that prose-only retro memory is NOT a valid disposition**.

## Per-Improvement Verdict

| # | Improvement (from retro) | Claimed disposition (Auto-Retro) | Verdict | Justification |
|---|---|---|---|---|
| 1 | **capability** — pre-write headroom signal for near-limit files (3rd recurrence) | `issue #256` | **DISPOSITIONED** | `#256` exists, OPEN, scope matches exactly ("pre-write line-budget/headroom signal for near-limit skill-helper files"). Real filed teeth; polarity is genuinely "filed". |
| 2 | **workflow** — stage the plugin mirror after `sync_root_plugin_manifests.py` | `applied:` existing `validate_packaging_committed` gate + habit in recent-lessons | **WEAK** | Points at a *pre-existing* gate as the "applied" teeth. That gate **detects after commit** (it caught the drift, forcing an `--amend` this very session) — it does not prevent the wasted step. No new teeth were added; the only new artifact is a memory habit. Honestly narrated ("no new gate needed; residual is operator habit"), so not a fabricated `applied:`, but it is capture-without-new-teeth. A human should confirm "existing gate already covers it" is an acceptable bar here. |
| 3 | **memory** — fold both lessons into `recent-lessons` | `applied:` done by `persist_retro_artifact.py` | **WEAK / borderline-UNDISPOSITIONED** | This is the memory-smuggled-as-applied pattern the #253 rule warns against. The improvement *is itself* a memory action, and the disposition is "memory was written." Verified the digest does carry the headroom + stage-the-mirror lines (`recent-lessons.md` lines 18-19), so it is at least *real* (not narrated-only). But labeling a pure recent-lessons write as `applied:` is exactly the dressed-up-memory-note case #253 says is invalid as a disposition of a *separable* improvement. It is honest only because the improvement was itself "fold into memory" — i.e. self-referential. Human should decide whether a memory-only item may self-dispose as `applied:`. |
| — | *(off-goal)* `is_non_trivial_goal` full-text marker poisoning bug | `issue #255` | **DISPOSITIONED** | `#255` exists, OPEN, scope matches exactly (full-text `Single-slice goal:` scan poisoned by body prose, suggests scoping to `## Slice Plan`). Real filed teeth. Correctly handled as off-goal, not in `## Next Improvements`. |

## Overall Coverage Verdict

**All surfaced improvements are addressed (3/3 from `## Next Improvements`, plus the off-goal bug) — none are silently dropped or prose-only-narrated.** Spot-checks confirm both cited issues (#255, #256) are real, OPEN, and scope-matched, and `scripts/validate_packaging_committed.py` exists as claimed.

However, **2 of the 3 `applied:` claims are WEAK**: neither item #2 nor item #3 adds *new* deterministic teeth. Item #2 leans on an existing post-commit detector (not a preventer), and item #3 is a recent-lessons write self-labeled `applied:`. By the strict #253 rule, an `applied:` should mean a real change with teeth, not a memory note dressed up — items #2 and #3 sit on that line.

**Coverage is complete; disposition strength is mixed.** No improvement is fully UNDISPOSITIONED, but the gate's intent (every improvement gets real teeth or a tracked issue) is only fully met for the two issue-filed items.

## Flags A Human Should Act On

1. **Item #3 (memory → `applied:`).** Decide whether folding a lesson into `recent-lessons` may legitimately self-dispose as `applied:`. The #253 contract explicitly says prose-only retro memory is not a valid disposition; here it skirts that only because the improvement *was itself* "write to memory." If the bar is "applied means new teeth," this should arguably be an explicit-none or rolled under #256, not `applied:`.
2. **Item #2 (mirror → existing gate).** `validate_packaging_committed` is a *post-commit detector*, not a *pre-stage preventer* — it did not stop the very drift it is credited with handling (an `--amend` was needed). If the operator wants the wasted step prevented (not just caught), the real teeth would be the pre-write/pre-stage signal already filed as **#256**, suggesting item #2 substantively overlaps #256 rather than being independently "applied".
3. No action needed on #255/#256 themselves — both verified real and OPEN.

## Reviewer Note (binding)

This artifact binds to goal **253** and was written to the path the goal's
`Disposition review:` evidence line references. The literal string 253 appears in
this body. Verdict in one line: **coverage complete, two WEAK `applied:` claims
(items #2 and #3) flagged for human judgment; the two issue-filed items (#255, #256)
are clean.**

## Resolution (operator, post-review)

The rung-2 reviewer's two WEAK flags were acted on at closeout — this is the
gate-and-intelligence loop working: the deterministic floor passed (Auto-Retro
non-blank, review ran + binds), and the *intelligent* rung caught two
dispositions the author's framing glossed over.

- **Item #2 (mirror → existing gate).** Accepted as WEAK. Re-dispositioned from a
  `applied:` credit of the post-commit `validate_packaging_committed` detector to
  a filed **`issue #257`** (pre-commit staged-aware mirror-drift check — the real
  unbuilt teeth). Goal `## Auto-Retro` updated.
- **Item #3 (memory → `applied:`).** Accepted as memory-smuggled-as-applied.
  Withdrawn the `applied:` label; re-classified as the *capture rung*
  (`persist_retro_artifact` write), not a separable improvement — the lessons it
  carries are dispositioned as `#256` and `#257`. Goal `## Auto-Retro` updated.

Post-correction coverage: every surfaced improvement is now either filed
(`#256`, `#257`) or correctly classified as the capture rung; off-goal bug filed
(`#255`). No falsely-`applied:` disposition remains.
