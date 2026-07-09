# Disposition Review — goal 2026-07-09-prompt-mutation-pilot

Date: 2026-07-09 (re-review pass, same day)

Fresh-eye satisfaction: parent-delegated — both the FAIL first pass and this
re-review ran as bounded read-only subagents in distinct contexts from the
producing session (first pass agent a0ef774d28924ab10, re-review agent
a7cb7a723638f51ad).

Rung-1b review of the Auto-Retro dispositions for the prompt-mutation-pilot
goal (binding + honesty check). Source retro:
`charness-artifacts/retro/2026-07-09-session-retro-prompt-mutation-pilot-goal.md`.
Goal: `charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md`.

This is a **re-review** of the same decision after the producer applied fixes
for the three findings (F1/F2/F3) raised by the first pass, which ended
`Verdict: FAIL`. See `## Prior findings and resolutions` for the audit trail;
the rest of this document is written fresh against the current state.

## Decision Under Review

Whether each Auto-Retro disposition for this goal is bound to a real
committed/tracked change (not prose-only memory), and whether the
`Structural follow-up:` line's class classification is honest — specifically
whether either `issue #N (novel: ...)` marker actually understates a known
recurrence lineage, and whether the claimed "class coverage" matches what was
actually applied.

Auto-Retro text under review (verbatim, current state):

> Retro dispositions: applied: docs/prompt-mutation-policy.md stream-drop
> re-score rule + commit-diff blinding caveat (commit 5ce78e9d); applied:
> docs/prompt-mutation-policy.md "red-team the observer once, up front" floor
> (channel enumeration at design time — the lesson behind the three blinding
> iterations, committed with this closeout); issue #426 (novel: mutant
> snapshot commits are diffable against their baseline parent — symmetric
> parentless snapshots for all arms); issue #427 (recurs: #415 — textual
> mention counted as genuine action, the same matcher-honesty class as the
> closed doc-open-floor instance; lineage noted on the issue)
> Structural follow-up: issue #427 (recurs: #415 — mention-vs-execution
> matching is a transcript-scorer class defect; the applied re-score rule is
> scoped to this pipeline, and the efficiency-A/B sibling named in the retro
> is dispositioned none-for-now because its committed reports derive from
> committed results.json, so the trap binds only if a future claim cites
> pruned evidence)

## Failure Angles

- A `novel:` recurrence-lineage marker asserted on an `issue #N` disposition
  when a matching recurring class already exists in the tracker — re-checked:
  now relabeled `recurs:`, but does the relabel actually bind (issue-side
  lineage, not just goal-file prose)?
- A `Structural follow-up:` destination that narrows its claim in words
  without the narrower claim being factually true — re-checked: does the
  stated reason ("committed reports derive from committed results.json")
  actually hold against the efficiency-A/B artifacts, or is it an unverified
  assertion substituted for the previous overclaim?
- A named transferable lesson recorded only in retro prose
  (`## Waste` / `## Expert Counterfactuals`) and never given an Auto-Retro
  disposition — re-checked, and broadened to a full sweep: does *every*
  `## Waste` / `## Sibling Search` / `## Next Improvements` item in the retro
  now carry some disposition (`applied:` / `issue #N` / `repo-local guard:` /
  `none`), not just the one item the first pass named?
- New angle for this pass: a disposition claiming a doc change is
  "committed with this closeout" while the working tree still shows that doc
  as an uncommitted edit — is this future-tense phrasing honest, or does it
  launder an uncommitted change as done?

## Counterweight Pass

**Verified clean (real checks, not over-worry):**

- **F1 relabel is real and double-bound.** The goal's `## Auto-Retro` line for
  `#427` now reads `recurs: #415 — textual mention counted as genuine action,
  the same matcher-honesty class as the closed doc-open-floor instance;
  lineage noted on the issue` — the `novel:` marker is gone. Independently,
  `gh issue view 427 --json comments` shows a comment posted 2026-07-09T04:26:38Z
  by `spilist` (member): "Recurrence lineage correction (from this goal's
  disposition review): this is **not novel** — it recurs the matcher-honesty
  class of closed #415 ... The fix direction stands; any resolution should
  also check other transcript matchers for the same mention-vs-execution
  scope error." Both halves of the fix (goal-file relabel + issue-side
  lineage note) are present and consistent with each other and with the
  original F1 finding's requested correction. **Genuinely resolved.**
- **F2 narrowed claim is factually accurate, not just reworded.** The
  `Structural follow-up:` line now states the re-score rule is scoped to this
  pipeline and dispositions the efficiency-A/B sibling as `none-for-now`
  because "its committed reports derive from committed results.json."
  Checked directly:
  `charness-artifacts/efficiency/prompt-mutation-handoff-refresh-pilot/report.md`'s
  per-arm table (baseline total_tokens mean 2.85361e6, m-bootstrap 5.56447e6,
  m-workflow 2.18266e6, m-closeout 2.72906e6 — matching duration_ms,
  tool_count, waste_smell_count, output_lines, pass_rate rows) is an exact
  match, field-by-field, against `results.json`'s `aggregate` block (e.g.
  baseline `total_tokens.mean = 2853614.5`, `duration_ms.mean = 337199.5`).
  `results.json`'s per-run entries are themselves sourced from each
  `preserved/<arm>__<n>/observed.v1.json` / `outcome-grade.md` (all present,
  committed, uncorrupted) — there is **no `stream.jsonl` anywhere** in the
  `prompt-mutation-handoff-refresh-pilot` bundle tree (confirmed by a
  recursive filename search), so the efficiency-A/B report's numeric metrics
  were never derived through the stream-fallback re-score path the policy
  caveat and #427 concern. The stated reason is true, not just plausible —
  the "none-for-now" disposition is honestly earned, and the line no longer
  claims the applied rule covers the class (it explicitly scopes it and
  explains why the sibling doesn't need the same fix *yet*). **Genuinely
  resolved.**
- **F3's lesson now has both a doc floor and a goal-file disposition.**
  `git diff docs/prompt-mutation-policy.md` shows an uncommitted addition:
  "**Red-team the observer once, up front.** Before a new
  capture-experiment design ships, enumerate in one pass every channel the
  captured agent can observe ... The pilot patched blinding three times
  because channels were discovered iteratively; the diff-against-parent
  channel that 4/6 mutant runs used was derivable up front from 'handoff
  runs do git ops'." This is a substantive, falsifiable, behavior-directing
  floor (not decorative), and it is the same lesson named in the retro's
  `## Waste` and `## Expert Counterfactuals` ("one exhaustive 'what can the
  captured agent observe?' enumeration ... would have caught the
  diffable-parent channel"). The goal's `## Auto-Retro` now carries a
  matching line: `applied: docs/prompt-mutation-policy.md "red-team the
  observer once, up front" floor (... committed with this closeout)`. The
  phrasing is honestly hedged — it does not claim the doc change is already
  committed (it isn't; `git status --short` still shows
  `docs/prompt-mutation-policy.md` as modified, alongside the goal artifact,
  the retro, the host-log probe, and this review file, all part of the same
  pending closeout commit). "Committed with this closeout" is forward-looking
  and accurate to the goal's own stated phase (`Current slice: closeout`,
  status `active`), not a false present-tense claim. **Genuinely resolved**,
  contingent only on the ordinary remaining step of actually landing the
  closeout commit — not a new finding, since disposition review runs before
  that commit by design and the goal's own phase-rule discipline (mutate ->
  sync -> verify -> publish) is what makes that commit happen next, not this
  review.
- **Full sweep of retro `## Waste` / `## Expert Counterfactuals` /
  `## Sibling Search` / `## Next Improvements` items (finding-4 recheck):**
  every item traces to a disposition in the current `## Auto-Retro` text:
  - Waste #1 (delete-before-rescore trap) -> `applied` (5ce78e9d re-score
    rule).
  - Waste #2 / Expert Counterfactual #1 (channel-enumeration lesson) ->
    `applied` (red-team-the-observer floor, F3 above).
  - Waste #3 (#427 mention-vs-execution) -> `issue #427 (recurs: #415)`.
  - Expert Counterfactual #2 (chain-of-custody rule) -> same `applied`
    disposition as Waste #1 (the committed re-score rule *is* the
    chain-of-custody rule, applied to the stream-drop case).
  - Sibling Search #1 (mention-vs-execution is a transcript-scorer class
    defect) -> `Structural follow-up:` on `#427`.
  - Sibling Search #2 (evidence-deleted-after-scoring across capture
    pipelines, naming efficiency-A/B) -> `Structural follow-up:`
    `none-for-now` with the verified-true reason (F2 above).
  - Next Improvements' own trailing "none further" item (30-unit UNTESTED
    debt list owned by the report artifact) -> already a disposition with a
    stated reason, untouched and not in question.
  No `## Waste` / `## Sibling Search` / `## Next Improvements` item is left
  without some disposition. **Finding 4: clean, nothing further to raise.**
- The `Structural follow-up:` line's **form** remains valid
  (`issue #N (novel|recurs: <reason>)` / `none-for-now: <reason>`), and the
  substance now matches the form.

**Minor observation, not elevated to a finding:**

- The retro artifact itself
  (`charness-artifacts/retro/2026-07-09-session-retro-prompt-mutation-pilot-goal.md`)
  still shows the stale wording in its own `## Next Improvements` list:
  "issue #427 (novel: constrain scorer stream fallback ...)". The retro file
  was not edited to match the correction; only the goal's `## Auto-Retro`
  (the authoritative disposition surface per this review's own
  `## Boundary Ownership`) and the issue itself were updated. This is a
  historical-snapshot-vs-live-tracker asymmetry, not a laundering risk: a
  reader who opens the issue or the goal's Auto-Retro sees the corrected
  `recurs:` lineage either way, and the retro's role is to record what was
  decided *in that retro session*, not to be re-edited after the fact by a
  disposition review. Noted for completeness; not a blocker.
- `#426`'s `novel:` marker (previously reviewed and left as F4/over-worry in
  the first pass) is unchanged this pass — still defensible as a distinct
  channel (git-history diffability vs. path/filename identity leak) from
  `#423`. Re-checked, still not elevated.

**Real problems found this pass:** none.

## Structured Findings

No findings survive this re-review; all three from the first pass are
resolved (see below), and the finding-4 general sweep and the F4/over-worry
item both remain clean.

## Reviewer Tier Evidence

- Requested tier: rung-1b disposition binding + honesty re-review (this
  review; bounded, read-only except for this artifact rewrite, no git
  mutation).
- Requested spawn fields: this review itself is the fresh-eye subagent
  execution the goal's `Disposition review:` line binds to (parent-delegated
  per the repo's standing subagent-delegation request; shared parent
  worktree, read-only `git show` / `gh issue view` / `git diff` only — no
  index or worktree mutation performed).
- Host exposure state: requested_fields_sent
- Application state: the parent sent an explicit lower-tier model override
  (sonnet) with the Agent spawn and the host accepted and ran the bounded
  reviewer (usage metadata returned); the host did not confirm provider-side
  field application, so `applied` is not claimed.

## Boundary Ownership

- Producer: the goal's `## Auto-Retro` section (achieve closeout) produces
  the dispositions; the retro artifact's `## Next Improvements` /
  `## Sibling Search` / `## Waste` produce the improvement and class-defect
  candidates.
- Consumer: the next session (via `recent-lessons.md`), the prompt-mutation
  policy surface (`docs/prompt-mutation-policy.md`), and the tracked issues
  `#426`/`#427`/`#415`.
- Owning surface: `docs/prompt-mutation-policy.md` for the applied re-score,
  blinding, and channel-enumeration rules; the GitHub tracker for
  `#426`/`#427`; the goal artifact's `## Auto-Retro` for the disposition text
  itself.
- Verdict: owned-correctly — every disposition lives on its owning surface
  and is fully bound: `#427`'s recurrence lineage is relabeled and noted
  on the issue (F1), the `Structural follow-up:` line's claim is narrowed to
  what is actually applied and the "none-for-now" reason for the
  efficiency-A/B sibling is factually verified true (F2), the design-time
  channel-enumeration lesson has its own `applied:` disposition backed by a
  real (if still-uncommitted-pending-closeout) doc floor (F3), and a full
  sweep of the retro's Waste/Sibling-Search/Next-Improvements items turns up
  no remaining undispositioned item (finding 4).

## Prior findings and resolutions

- **F1** (blocker — `#427` mislabeled `novel:` against closed `#415`'s
  matching matcher-honesty class): **RESOLVED.** Goal `## Auto-Retro` now
  reads `recurs: #415`; a lineage-correction comment is posted on `#427`
  (2026-07-09T04:26:38Z, author `spilist`). Verified both independently.
- **F2** (should-fix — `Structural follow-up:` line overclaimed "the
  evidence-deletion class trap is covered" when the applied rule is scoped to
  one pipeline): **RESOLVED.** Line now scopes the applied rule to this
  pipeline and dispositions the efficiency-A/B sibling `none-for-now` with a
  stated reason; the reason ("committed reports derive from committed
  results.json") is verified true by direct field-by-field comparison of
  `report.md` against `results.json` and confirming no `stream.jsonl` exists
  in the bundle tree that the reasoning would depend on.
- **F3** (should-fix — design-time channel-enumeration lesson had no
  disposition of any kind): **RESOLVED.** `docs/prompt-mutation-policy.md`
  gained a "Red-team the observer once, up front" floor (currently an
  uncommitted working-tree edit, honestly described in Auto-Retro as
  "committed with this closeout" rather than already-committed), and the
  goal's `## Auto-Retro` carries a matching `applied:` line.
- **F4** (over-worry, not elevated — `#426`'s "#423-class fix" phrase in
  tension with its own `novel:` marker): unchanged this pass, still not
  elevated; re-checked and remains defensible.
- **Finding 4 / general sweep** (any retro Waste/Sibling-Search/
  Next-Improvements item still undispositioned?): re-checked exhaustively
  this pass — none remain.

Verdict: PASS
