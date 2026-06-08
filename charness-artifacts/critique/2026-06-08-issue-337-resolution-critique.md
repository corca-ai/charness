# Resolution critique — issue #337 (waste-retro structural-follow-up destination classification)

Date: 2026-06-08
Target repo: `corca-ai/charness`
Issue: **#337** "Require waste-retro disposition reviews to classify structural follow-ups"
Resolution bundle: `git diff 281fc373..HEAD` (4 commits — `3dc8e79c` rung-1e floor +
rung-2 mandate, `e3dbd266` one shared destination vocabulary, `101c1f33` guard-branch
coverage tests + `.coverage` gitignore; plus the goal artifact closeout).

Fresh-eye, read-only rung-2-style **resolution** critique: does the resolution genuinely
resolve #337, and does it close the *class* of issue ("a disposition floor that proves
process ran but not substance, letting memory masquerade as a structural fix") so it does
not recur? Verified by reading the diff, the two `disposition_form.py` /
`goal_artifact_disposition.py` copies + their `plugins/` mirrors, `lifecycle.md`, the
shared `retro-issue-destination-split.md`, the retro `waste-sibling-scan.md`, the new
tests, the resolution's own goal artifact + bound disposition review, and by running the
floor logic against the live goal corpus and edge inputs. No index/worktree mutation;
this artifact is my only write.

Fresh-eye satisfaction: complete — read-only review ran in the shared parent worktree,
inspecting prior state via `git show`/`git diff` only.

## Q1 — Does it resolve #337's actual ask? (make prose-only memory harder to slip past)

**Yes, by construction, with a correctly-named honest limit.** #337 asked Charness to
"make it harder for an agent to close the loop with prose-only memory when the surfaced
waste clearly asks for a structural owner decision." The resolution lands that as a *floor
plus a mandate*, not documentation alone:

- The deterministic floor (rung 1e) fires when the cited retro names transferable waste —
  `apply_structural_followup_floor` at `skills/public/achieve/scripts/goal_artifact_disposition.py:318`
  reads the bound retro once (`:372-378`), calls `names_transferable_waste`
  (`scripts/disposition_form.py:254`) to detect a real `## Sibling Search` decision bullet,
  and then requires a valid `Structural follow-up:` destination line in `## Auto-Retro`
  (`evaluate_structural_followup`, `scripts/disposition_form.py:295`). A bare
  `Retro dispositions: applied: …` with no destination line yields `problem: "missing"`
  (`:318-327`) and sets `report["ok"] = False` (`:348-350`). I confirmed this against the
  live floor: a transferable-waste Auto-Retro with no `Structural follow-up:` line returns
  `problem: "missing"`.
- Crucially, the floor does **not** count the seeded template placeholder as a satisfying
  destination: `evaluate_structural_followup` only treats a line as `valid` when
  `kind != "placeholder"` (`scripts/disposition_form.py:308`). I verified empirically that
  an untouched `Structural follow-up: TODO — …` line (the template seed at
  `skills/public/achieve/scripts/goal_artifact_template.md:121`) yields `problem: "missing"`,
  so an agent cannot satisfy the floor by leaving the scaffold in place.
- The rung-2 mandate (`skills/public/achieve/references/lifecycle.md:556-565`) makes the
  fresh-eye reviewer **reject "recorded in recent-lessons" as a destination** unless paired
  with one of the four forms. That is the substantive half the regex cannot do.

**Where an agent could still slip a memory note past it (the honest residual):** the floor
is form/enum only, so `Structural follow-up: applied: recorded in recent-lessons` *passes
the floor* — I confirmed `evaluate_destination_form("applied: recorded in recent-lessons")`
returns `ok: True, kind: "applied"`. This is by design (the #337 Non-Goal forbids a content
classifier), and it is exactly what rung 2 exists to catch: the reviewer must reject a
memory note dressed as `applied:`. So the slip is not closed by the floor — it is closed by
the floor **plus** the reviewer, and the resolution says so rather than over-claiming. That
matches #337's own framing ("the gap is in the reviewer/operator workflow… that remains a
reviewer/human judgment"). The floor's contribution is real and load-bearing: before this
change, `Retro dispositions: applied: persisted to recent-lessons` passed with *no*
destination prompt at all; now a transferable-waste retro forces an explicit, separately-
labeled `Structural follow-up:` line that the reviewer is mandated to audit.

## Q2 — Did it honor the issue's explicit Non-Goals?

**(a) Floor is presence/form-enum only, NOT a content classifier — honored.**
`evaluate_destination_form` (`scripts/disposition_form.py:158`) matches only on leading
tokens: `repo-local guard` (`_REPO_LOCAL_GUARD`, `:109`), or delegation to
`evaluate_disposition_form` whose checks are anchored enum prefixes (`_APPLIED`/`_ISSUE_LEAD`/
`_NONE`, `:70-77`). It never scores prose quality — `evaluate_destination_form("applied: tweak")`
returns `ok: True` (asserted at `tests/quality_gates/test_disposition_form_floor.py:418`).
`evaluate_structural_followup` only counts presence/form (`:306-328`). This is the same
discipline as the sibling rungs and `validate_proposal_fields.py`'s `Destination` enum, and
the module docstring + the goal's Non-Goals re-state it (`goal_artifact_disposition.py:324-332`).

**(b) Fix is upstream in Charness, NOT consuming-repo AGENTS.md — honored.** Every behavior
change lands in portable charness surfaces: the shared script `scripts/disposition_form.py`
(+ `plugins/charness/scripts/` mirror), the achieve gate
`skills/public/achieve/scripts/goal_artifact_disposition.py`, the skill prose
`skills/public/achieve/references/lifecycle.md`, the shared reference
`skills/shared/references/retro-issue-destination-split.md`, and the retro reference
`skills/public/retro/references/waste-sibling-scan.md`. No consuming-repo `AGENTS.md` is
touched. The resolution even adds `repo-local guard: <path>` as a *destination value* so a
repo that genuinely owns a local fix has a first-class form — without moving the policy into
that repo's AGENTS.md.

**(c) Avoids forcing every tiny local waste to file an issue — honored, two guards.**
First, `none — <reason>` is a valid destination (`_NONE`, `scripts/disposition_form.py:77`;
`DESTINATION_FORM_SUMMARY`, `:103`), so a genuinely-local one-off discharges without an
issue — the resolution's own goal dogfoods this with `Structural follow-up: none — …`
(goal artifact `## Auto-Retro`, lines 333-336). Second, the floor is **inert unless
transferable waste is named**: `names_transferable_waste` returns False for the
`n/a — trivial fix; no plausible siblings` short-circuit (no `decision:` bullet) and for an
absent `## Sibling Search` (`scripts/disposition_form.py:254-275`); I confirmed against the
live corpus that a no-Sibling-Search retro yields `transferable_waste_named: False` and the
floor does not fire. Narrowly-local waste is never forced to a destination at all.

## Q3 — Recurrence prevention: does it close the CLASS, not just the #337 instance?

**It closes the class to the maximum a deterministic floor honestly can, and names the
limit instead of over-claiming.** The class is "a disposition floor that proves *process
ran* but not *substance*." The resolution's structural move is the gate-and-intelligence
split applied to a new axis: rung 1e proves *a destination decision was made and labeled*
(ungameable, offline, clone-safe); rung 2 proves *the destination is substantively right*
(intelligence, recorded for a human). The honest limit is stated verbatim in
`lifecycle.md` ("**Honest limit.** The deterministic floor proves the *process* ran… it
never scores whether a non-empty Auto-Retro genuinely disposed each improvement. That
substantive judgment is rung 2's and the human's", `:567-577`) and in every new docstring
(`apply_structural_followup_floor`, `evaluate_destination_form`). It is NOT quietly
over-claimed as a deterministic substance check — the module headers explicitly forbid a
future maintainer from tightening it into a classifier.

Anti-drift is the second class-level move: the four-form vocabulary lives in **one** shared
source (`skills/shared/references/retro-issue-destination-split.md:99-135`), pointed to by
both the retro waste-sibling-scan (`waste-sibling-scan.md:47-63`) and the achieve gate
contract; the inline four-form list in `lifecycle.md` is explicitly named a "display copy,
not a second source" (`retro-issue-destination-split.md:108-109`). The code grammar has one
home too (`disposition_form.py`, loaded by parent-walk so the mirror cannot fork it). This
is what stops the *next* version of the class — two surfaces growing divergent destination
vocabularies — which is itself a sibling of the original "process vs substance" gap.

So: the class is closed at the floor/reviewer boundary, the limit is named, and a plausible
sibling failure (vocabulary drift) is pre-empted. The one residual the resolution cannot
close deterministically (`applied: <memory note>`) is correctly handed to rung 2, which is
the only place it *can* live without re-importing the word-list over-fire trap.

## Q4 — Regression risk to existing closeouts?

**None — every existing goal is grandfathered, confirmed against the live corpus.** Rung 1e
keys on `STRUCTURAL_FOLLOWUP_RULE_DATE = date(2026, 6, 9)` (`scripts/disposition_form.py:97`)
and fires only for goals `Created` on/after it (`goal_artifact_disposition.py:336`,
`enforced = created is None or created >= …`). I scanned every real goal artifact under
`charness-artifacts/goals/` (58 with a `Status:`+`Created:` header): the latest `Created`
date is `2026-06-08`, strictly before the `2026-06-09` rule date, so **every existing goal
is grandfathered** (`enforced=False`), independent of whether its retro names transferable
waste. The resolution's own goal (`Created: 2026-06-08`) is itself grandfathered and
dogfoods the destination lines voluntarily — exactly the "enforced=false for 2026-06-08
goals" probe result the brief cited. The 7 `*-early-close-report.md` files in that directory
have no `Created:`/`Status:` header and are not goal artifacts — they never flow through
`apply_disposition_rungs`, so their fail-closed `created=None` is moot. Fail-closed on a real
undatable goal (`created is None → enforced=True`) is the correct safety direction and is
covered by `test_rung1e_tolerates_unreadable_bound_retro`. Broad gate proof in the goal
artifact (`## Final Verification`): `run-quality.sh --read-only` 73 phases passed / 0 failed,
2584 pytest passed; I re-ran the new module's 44 tests (all pass) and `validate_skills` /
`check_doc_links` (both pass), and byte-confirmed all three source→`plugins/` mirrors are
in sync.

## Q5 — Fully or partially addressed? (the three candidate fixes #337 listed)

**Two of the three candidate fixes landed; the omitted third is acceptable and the omission
is honest.** #337 offered: (1) retro disposition-review guidance requiring a per-waste
structural destination; (2) achieve closeout guidance to reject "recorded in recent-lessons"
unless paired with teeth/issue/guard/none; (3) an adapter option for repos to require
destination labels in disposition-review artifacts.

- **(1) landed** — the retro side gets the destination vocabulary in
  `waste-sibling-scan.md` mapping each of the four sibling-scan decisions onto a destination
  form, sourced from the shared reference.
- **(2) landed, with deterministic teeth** — the achieve rung-2 mandate
  (`lifecycle.md:556-565`) is the exact "reject recorded-in-recent-lessons" rule #337 asked
  for, and rung 1e adds a deterministic floor underneath it that #337 did not even require.
- **(3) NOT landed** — no adapter knob to require destination labels was added. This is
  acceptable: #337 listed the three as "one or more" alternatives, not a conjunction; an
  adapter option is the heaviest of the three and would add a host-configuration surface for
  a behavior the portable floor+mandate already covers uniformly. The resolution's goal
  Non-Goals scope to #337-as-floor-and-mandate, and the omission is consistent with the
  Charness principle "host-specific behavior belongs in adapters" only when the behavior
  *needs* to vary by host — destination classification does not. Honest statement: an adapter
  option remains a future enhancement if a consuming repo ever wants to require destination
  labels in standalone disposition-review *artifacts* (vs the goal Auto-Retro the floor
  covers); nothing in this resolution forecloses it.

## Findings

- **NIT (clarity, not a blocker):** the `applied: <memory note>` form-passes-the-floor path
  (Q1 residual) is correctly delegated to rung 2, but the *template* seed
  (`goal_artifact_template.md:121`) and the user-facing acceptance text do not re-warn that a
  memory note wrapped in `applied:` still needs reviewer rejection. The `lifecycle.md` rung-2
  mandate covers it; a one-line template hint would put the warning where the author writes
  the line. Documentation polish only — the behavior is already correct via rung 2.
- **NIT (scope honesty):** candidate fix (3) (adapter option) is omitted without an explicit
  one-line "not done, deferred" note in the goal artifact's Non-Goals — it is inferable from
  the #337-only scope but is not called out as a #337-listed-but-skipped alternative. Naming
  it would make the partial-vs-full closure self-evident to a future reader. Not blocking;
  this critique records it.
- **OVER-WORRY (raised and dismissed):** "the floor's `none — <reason>` is a free escape that
  re-opens the prose-only gap." It is not — `none — <reason>` is a *falsifiable* claim the
  rung-2 reviewer reads the retro to contradict (`lifecycle.md:556-565`,
  `retro-issue-destination-split.md:119-120`), exactly like the existing disposition opt-out.
  An over-fire-free escape that a reviewer can falsify is the correct design, not a hole.
- **OVER-WORRY (raised and dismissed):** "grandfather-by-`Created` means the floor never
  actually fires on any real goal, so it is inert theater." It fires on every goal created
  on/after 2026-06-09 (proven by the `test_rung1e_*` synthetic suite); the live corpus simply
  has no such goal *yet* because the rule landed 2026-06-09 and today is 2026-06-08. This is
  the standard, broad-gate-safe landing pattern shared by rungs 1c/1d, not inertness.

## Verdict

**RESOLVES.** Rung 1e (presence/form-enum floor) + the rung-2 reject-recorded-in-recent-
lessons mandate genuinely make prose-only memory harder to pass off as a structural
disposition *by construction* when transferable waste is named, while honoring all three
#337 Non-Goals (no content classifier, upstream-not-AGENTS.md, no forced issue-per-waste via
`none —`/grandfather/no-over-fire guards). Recurrence-prevention judgment: the *class*
("floor proves process, not substance") is closed at the honest floor/reviewer boundary with
the limit named (not over-claimed) and vocabulary-drift pre-empted via one shared source; two
of #337's three candidate fixes landed and the omitted adapter option is an acceptable,
non-foreclosing deferral. Two NITs (template/scope-note clarity) are documentation polish, not
correctness gaps.
