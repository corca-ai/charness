# Session Retro

Date: 2026-08-15

## Context

S1 of the 6.0.0 release contract, committed at `667f6dcdb`: the release-notes
generator, its notes-versus-tree gate, the narrative-containment lint, the
`what-reads-this` command (#599), and the `check-markdown.sh` npm fallback
(#630). The slice changes verdict logic on a proof surface, so it owed the
two-round bounded review — and the second round is what makes this retro worth
writing, because it caught three repairs that carried the class they repaired.

Next: S2 (producer-scaffold subject identity), then S3-S6, then S7 publishes.

## Window

One session, from the handoff pickup through the S1 commit. Nine lessons served
at open as session `2026-08-15-s1-release-tooling`; five bounded reviewers across
two rounds; four full-suite runs.

## Evidence Summary

- `667f6dcdb` — 31 files, 5013 insertions.
- Full suite: **9403 passed**, 0 failed (`/tmp/full-final3.log`, 1254s). Three
  earlier runs each surfaced exactly one failure, both since fixed.
- `ruff check --no-cache .` clean. Cache-free, per the recorded false-green.
- Five bounded reviewers, `parent-delegated`; both
  `reviewer_boundary_fingerprint verify` runs returned `verdict: clean`, so no
  approval is quarantined.
- `lint_release_narrative.py` over
  `charness-artifacts/release/2026-08-14-v6.0.0-notes.md`: 49 findings before the
  severity split, 29 after (8-10 blocking depending on the lookaround repair).
- Two gates verified RED AT HEAD in throwaway worktrees, so not attributable
  here: `check_dup_ratchet` (21 families at `0b1ef4300`) and `check-shell`
  (SC2016 x2 in `run-quality.sh`, zero diff from this slice).

## Waste

**The dominant waste was building an over-strict rule and paying for it in two
review rounds.** The containment lint first blocked on quantities *and* the six
completeness words. Measured against this repo's own release note that refused 49
lines, including `"verified only after the release has been published"` — the
honest-limits language the north star requires. Cost: a full design reversal
mid-slice, two reviewer findings, and a deviation record.

The cheap counter existed and I skipped it: **running the new rule against the
repo's own artifact takes seconds, and I ran it only after writing the tests.**
Had I run it first, the severity split would have been the original design.

Second waste, smaller: two full-suite runs (~21 min each) were started and then
invalidated because I edited the tree while they collected. Both were stopped
deliberately rather than lost, but the sequencing was mine to get right.

- **The premise check ran first and the class still got through one surface
  over.** Checking #630 and #599 against source before implementing is exactly
  what the lesson asks, and it worked — it refuted a live assumption about #599.
  Then I wrote into a `dup-review.json` review note that the slice "added six
  release scripts" when it added four and modified two, asserting a quantity I
  had not counted, inside the artifact that records WHY duplicate families are
  accepted. A bounded reviewer caught it. The lesson transferred to the code path
  it was written about and not to artifact prose, which is the same shape as
  writing a false quantity into release notes — the defect this whole slice
  exists to prevent.
  (recurrence-class: premise-not-checked-against-source)

## Critical Decisions

- **Default-true for `require_derived_release_claims`.** Deleting the key
  re-arms the gate instead of disarming it. This is the `bar-recorded-as-prose`
  lesson applied directly, and it survived both review rounds.
- **Splitting the lint into blocking quantities and advisory completeness
  words**, on measurement rather than argument. Recorded as a DEVIATION from an
  owner-approved criterion rather than by quietly amending SC3 to match the code.
- **Reverting my own `not on_resume` skip.** Round 1 argued the resume lane was
  redundant; round 2 proved the argument was about the tree and did not transfer
  to the notes, and that resume is the only path reaching `create_release`.
- **Fixing a pre-existing date-coupled test** (`test_router_and_gate_agree...`)
  that self-destructed at UTC midnight. Out of slice scope, but it blocks every
  future slice's honest green claim.

## North Star Alignment

`docs/design-north-star.md` says brief a capable judge and keep teeth only where
a wrong answer escapes, and at irreversible boundaries confirm through a
different observer and evidence channel.

Held: the publish boundary is where the teeth went, and the observers were
genuinely different — five bounded reviewers on five distinct lenses, plus
throwaway HEAD worktrees as a second evidence channel for both pre-existing red
gates. P4 in particular: the dup-ratchet and check-shell attributions came from a
different command against a different tree, not from re-reading my own diff.

Mis-applied: the first containment rule put teeth where a wrong answer *did not*
escape — an honest hedge is not an escaping wrong answer — and the north star
would have predicted the operator response (disable the rule, taking the working
arm with it). The rule was briefing nobody; it was refusing everybody.

Named failure signature walked into: **the fix that carries its own class**,
three times in one slice (resume-lane skip, dead `except Exception` handler,
hyphen lookaround). All three were caught only by the round that read the
repairs, which is exactly what the two-round rule exists for.

## Trends vs Last Retro

Against `2026-08-15-release-scope-design.md`, which recorded
`premise-not-checked-against-source` recurring on the same issue number two days
running: **this session broke that streak on its trigger** — the premise check
ran first and refuted a live assumption (#599 is partly covered by
`removed_name_consumers.py`). But the class recurred in a lower-stakes surface:
a `dup-review.json` note asserting "six release scripts" over four. So the lesson
transferred to the path it was written about and not to artifact prose.

`proof-surface-review-binding` (repairing inside an open window, which quarantined
twelve paths last session) did **not** recur: both verifies returned `clean`.

## Expert Counterfactuals

**Engelbart (`system-improving-itself`) — treat H + LAM + T as one unit.** I
built the tool (T) and the rule (LAM) but never ran T against the repo's own
corpus before hardening it. Engelbart's move is to close the loop at the smallest
scale first: the very first executable step should have been
`lint_release_narrative.py` over the existing 6.0.0 notes, because that artifact
*is* the system's record of what it considers acceptable prose. Doing that in
minute five instead of hour three converts two review rounds of correction into
one design decision. Generalized: **when a new rule will judge existing
artifacts, run it over them before writing its tests** — the corpus is the
specification.

**Ousterhout (deep modules, errors defined out of existence).** The 49 findings
were not a tuning problem, they were an interface problem: one boolean adapter
key controlled two rules with different error rates, so the only escape from the
noisy rule also disarmed the quiet one. Ousterhout would have said the severity
distinction belongs *inside* the module rather than in the operator's
configuration — which is exactly where it ended up. The counterfactual action:
when a single switch governs two mechanisms with different false-positive
profiles, split the mechanism before shipping the switch.

## Sibling Search

- axis: **same-class rule with a deletable arming flag** | location:
  `resolve_adapter.py` BOOL_FIELDS is the only boolean adapter field in the
  release skill; other skills' adapters use list fields whose empty state is the
  declared opt-out | decision: no sibling defect — the list-field pattern already
  carries the D48 "absence is not a declaration" treatment | proof:
  `skills/public/release/scripts/resolve_adapter.py:96-108` documents it for
  `required_release_surfaces` / `unpublished_release_surfaces` | follow-up: none
- axis: **date-coupled test fixture** | location:
  `tests/test_lesson_loop_wiring.py` was the instance; the class is any test
  pinning a literal `date(...)` against a fixture whose timestamp is real-now |
  decision: valid follow-up outside the slice | proof: `grep -rn "date(20"
  tests/` returns further candidates I did not audit; the one measured instance
  failed on a clean HEAD worktree at 2026-08-15T00:23Z | follow-up: deferred
  s2-handoff-date-coupled-tests
- axis: **`except Exception` over a `SystemExit` subclass** | location:
  `RepoFileListingError` subclasses `SystemExit`, so every `except Exception`
  around a `require_git=True` listing is dead | decision: valid follow-up outside
  the slice | proof: `scripts/repo_file_listing.py:14`; my own instance was found
  by a reviewer, not by me | follow-up: deferred s2-handoff-systemexit-handlers

## Lesson Evaluation

Lesson evaluation: {"score_event_count":1,"session_id":"2026-08-15-s1-release-tooling","status":"effect-recorded"}

**One score, and the count is a mechanism limit rather than a judgment.** Five
further lessons changed an observable action this session and are NOT scored,
because the ledger will only accept a score whose citing retro declares a
`recurrence-class` tag for that lesson (`lesson_ledger_lib.py:376`). Declaring a
recurrence for a lesson that WORKED would be false, so the honest record is to
leave them unscored and say why:

- `proof-surface-review-binding` — held every repair until all reviewers
  returned; both boundary verifies returned `clean`, against twelve quarantined
  paths last session.
- `bar-recorded-as-prose` — produced the default-true arming direction for
  `require_derived_release_claims`.
- `closeout-diagnostic-visibility` — four background suite runs, none lost to a
  wrapper timeout.
- `durable-lesson-ledger-first` — the session was declared before the work, which
  is why this disposition exists at all.
- `agent-authored-score-role` — these judgments were authored from cited actions
  before asking whether to record any.

This is not a gap in the retro; it is **S3's Success Criterion 6 met from the
failing side**: *"A lesson that is read and then works can be recorded as such
without declaring a recurrence."* Today it cannot. Five anchored positive effects
were observed and are unrecordable, so the ledger's recurrence counts see only
failures and the selection ranking cannot distinguish a lesson that is working
from one nobody consults.

Three lessons are genuinely unscored because nothing observable happened:
`guard-adjacent-to-action` (no handoff authored), `artifact-contract-late-feedback`
(no quality artifact), `goal-closeout-evidence-binding` (no goal artifact).

## Next Improvements

- workflow: **run a new judging rule over the repo's own existing artifacts
  before writing its tests.** The corpus is the specification; 49 findings on the
  6.0.0 notes was available in minute five and arrived in hour three.
- workflow: **do not start a full-suite run until the tree is settled.** Two
  ~21-minute runs were invalidated by edits landing mid-collection.
- capability: audit the `except Exception` / `SystemExit` class named in the
  sibling search; `RepoFileListingError` is a `SystemExit` and any handler
  written for it is dead.
- capability: audit date-coupled test fixtures; one already self-destructed at a
  UTC midnight boundary on an unchanged checkout.
- memory: when one configuration switch governs two mechanisms with different
  false-positive profiles, split the mechanism rather than shipping the switch —
  the noisy arm's escape hatch will disarm the quiet one.
- capability: **S3 now has a measured instance, not just a spec clause.** Five
  positive lesson effects were observed and could not be recorded, because
  scoring requires the citing retro to declare a `recurrence-class` for that
  lesson. Carry this retro as the evidence when S3 implements SC6.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-15-session-retro.md
