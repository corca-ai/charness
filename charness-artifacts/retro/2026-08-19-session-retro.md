# session retro

Date: 2026-08-19

Goal: charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md

## Context

Slices 1 and 2 of the probe-provenance goal, plus the precondition that unblocked
pre-push. The goal exists because on 2026-08-18 three of one session's own
measurements were refuted, two sharing one generator: the probe's stimulus came from
the agent's model of the mechanism rather than from the source that defines the claim.
Slice 1 built a probe record that can say it measured nothing; slice 2 wired it into
the issue-close and release close-issue boundaries. Four operator decisions landed
mid-run, one of which (REVIEW severity) changed what slice 2 ships.

What matters next: slice 3, whose groundwork is already measured and recorded in the
frame so it is not re-derived.

## Window

Six commits, `8527936fd` through `f24f76b44`, all local — push is deferred to after
this retro by operator ruling. Two slices, four bounded review rounds (two per slice),
plus the four-angle pre-implementation critique that preceded activation.

## Evidence Summary

- The goal artifact's `## Slice Log`, entries for slices 1 and 2, written from the
  work rather than from memory.
- Four bounded `bounded-reviewer` reports, all read-only, all spawned unnamed. Every
  factual finding was re-measured by the parent against the code before folding.
- `charness-artifacts/probe/2026-08-18-standing-lane-flake-bar.md` — the first real
  probe record, on the precondition repair rather than on a fixture.
- Gate output: 10255 standing tests, `-m release_only` 102, floor matrix `ok: true`
  across 36 pairs, changed-line proof `clean` at each slice commit, dup ratchet clean.
- `mine_closeout_telemetry.py` over 1727 closeout records: the recurring gate-runtime
  findings are the broad pytest lanes (16 occurrences at up to 475s peak, 13 at up to
  208s), all pre-existing and none introduced here.
- No host token/time telemetry is claimed. This retro carries measured gate output and
  commit-level facts; it makes no turn, token, or tool-call claim.

## Waste

- **The largest cost was not a mistake — it was the fixture migration.** Making the
  probe record a hard floor turned 67 existing tests red across 15 files. That was
  foreseeable in kind but not in size, and the size is what the operator's REVIEW-severity
  ruling was made against. It was not wasted: the number IS the deliverable that let the
  decision be made on measurement rather than on estimate.
- **Real waste: bulk regex edits on test fixtures.** Migrating by scripted regex inserted
  a `Probe record` line into a list of fields a test expected to be REFUSED. One test
  caught it. A bounded reviewer then enumerated all 31 inserted sites and found no others,
  which is the only reason I can say the migration is clean rather than hope it.
- **Real waste: three length-gate collisions in one slice.** `release_issue_closeout.py`
  crossed its 360-line cap three times, and my first response was a split that removed
  code with real dedicated test coverage — reverted. Two of the three cuts were right
  (a floors module, one parameterized loader); the first was reaching for the nearest
  lines rather than the right concept boundary.
- **Real waste, self-inflicted and the sharpest of the session: I destroyed this retro's
  first draft.** I ran `cp <retro> /tmp/retro-body.md && rm <retro> && persist ...` in one
  chain. The persist step refused (correctly — foreign helper copy), and `/tmp/retro-body.md`
  turned out to be another session's file, so the draft was gone and the source already
  deleted. Two rules were broken at once: a shared, guessable temp path, and a delete
  before the copy was confirmed. The whole retro had to be rewritten. This is the same
  class as everything else in this session — an operation that reported success while
  the thing it was supposed to preserve was not there.
- **Not waste, though it looks like it:** four standing-lane reruns. Each followed a
  repair round or a severity change that altered verdict logic on a proof surface. The
  cadence rule defers the broad lane to slice boundaries, and each of these WAS one.

## Critical Decisions

- **Answering Open Question 1 before wiring anything.** The per-arm base disposition
  table is what makes `base-unrunnable` always `not-established`; without it, "base and
  HEAD differ" is satisfied by a base that merely crashed, which is the `#528` shape.
- **Triggering the obligation on the CLAIM rather than the classification.** This is the
  goal's own thesis and it is why an honest non-verifying close is untouched. The
  alternative taxes every close for a claim it never made.
- **Splitting the severity decision into one constant read by every carrier.** Written
  the other way first — a branch per carrier — which is three copies of one decision on
  a proof surface, and precisely how three earlier floors came to disagree about which
  carriers they reached.
- **Recording rather than softening the acceptance consequence.** `## User Acceptance`
  bullet 2 requires the floor to REFUSE; at REVIEW severity it does not, and the queue
  says so in those words instead of rewording the bullet to fit what shipped.
- **Operator ruling 1B over my implementation.** I built the blocking floor because the
  acceptance is explicit. Scaling it down was the operator's call and they made it; the
  correct move was to measure the cost, surface it, and implement the ruling — not to
  pre-emptively narrow the work.

## North Star Alignment

P4 and P5 are the governing clauses here and the session's own results test them.

P5 — *closeout stops when the evidence record is populated with captured observables* —
is what slice 1 implements, and round 1 measured a `base-absent`/`existence` record
resolving `evaluated` with no captured observable at all. That was P5 violated inside
the mechanism written to serve it.

P4 — *no terminal green* — is why `evaluated` carries `RESIDUAL_JUDGMENT`. This slice
mints a new green at exactly the boundary where a wrong claim escapes, and a green that
returns nothing but the word is how `evaluated` would come to mean "reviewed".

The north star forbids a gate that renders verdicts about other gates. The probe record
stayed on the right side: it reads a hand-authored evidence file and types a state about
THAT record. It never inspects another gate's output. A reviewer checked this explicitly
rather than my asserting it.

Where alignment is now WEAKER than the goal intends, stated plainly: at REVIEW severity
the record is produced and read but not required, so the irreversible boundary is not
yet defended by it. That is an operator decision, not a drift, and it has a revisit
trigger.

## Trends vs Last Retro

The prior durable retro
(`charness-artifacts/retro/2026-08-18-adapter-version-containment-and-the-consumer-census.md`)
recorded three refuted measurements and named their generators. This session built the
countermeasures — and reproduced two of the three classes inside them:

- The "one of two entrypoints guarded" class recurred TWICE in the wiring of its own
  countermeasure: `close-with-comment` was missed on the issue side, and
  `ensure_release_issues_closed` on the release side.
- The "stimulus from a model rather than a source" class recurred as a MIRROR defect: I
  copied `issues?\b` from a sibling and dropped the tracker-ref conjunct the sibling's
  own comment explains, which is copying my model of the sibling rather than the sibling.

The trend is not that the lessons failed. It is that both recurrences were caught by
mechanisms this repo already owns — the closeout floor matrix and the two-round review —
rather than by my recall. That is the system working; it is also the honest reason the
countermeasures needed four review rounds.

## Expert Counterfactuals

**Engelbart — treat (H + LAM + T) as one unit; design T alongside LAM.** The briefed
lens for harness/contract work, and it names this session's sharpest miss. I designed
the LAM (the probe record and its floors) carefully and designed the T — the tooling
that would let a HUMAN or a future agent use it — barely. A bounded reviewer found the
consequence: `Probe record` appears in no closeout template, no shape describer, and no
reference doc. An author following the shipped starter writes a carrier the floor
refuses, and their discovery path is "get refused" rather than "read the shape". Under
this lens the template and the describer are not documentation chores; they are the
T-half of the same change, and shipping the floor without them means the mechanism's
only teacher is its own error message. **Changed action for slice 3 onward: a floor that
adds a required field ships its authoring surface in the same slice.**

**Gary Klein — premortem on the escape, not on the failure.** The reviews found four
escapes (`issues` as a sentence opener, a disposition discharging a claim, an
extension-less path, a vacuous silence guard), and I found none of them myself. What
would have: asking, of every refusal I added, "what is the CHEAPEST mutation that still
gets past this?" That question found nothing when I asked it about content and
everything when the reviewers asked it about FORM — for a path gate the cheapest
mutation was a shorter typo, not a longer one; for a status vocabulary it was an
ordinary English word. **Changed action: for each new refusal, write the cheapest
bypass I can construct as a test BEFORE writing the refusal's own passing test.**

## Sibling Search

The transferable pattern: **a mirrored guard that drops the conjunct its source
documents**. I copied `_HOTL_STATUS_LEAD`'s vocabulary into `_NON_VERIFYING_LEAD` as a
flat alternation, losing the `_HOTL_ISSUE_REF` conjunct that the source module explains
in a comment written for exactly that reason.

Scanned for siblings across the four axes:

- **Same-file**: none — the repaired module now carries both regexes with the conjunct.
- **Same-skill**: `issue_resolution_critique` and `issue_close_comment_floor` mirror the
  disposition grammar; both delegate to `_FLOORS` rather than re-spelling it. Clean.
- **Cross-skill**: `release_closeout_floors` mirrors the issue floor by LOADING it, not
  by copying — the one mirror that could have drifted is now a delegation.
- **Cross-repo/portable**: the pattern is general (any repo that mirrors a guard between
  two modules), but the detection is not mechanical — it needs the source's comment read.

Decision: **fixed-here, no follow-up filed.** The three live mirrors in this family all
delegate rather than copy, so there is no second instance to repair. Recorded because
the NEXT mirror is the risk, and the cheap rule is: when copying a guard, copy its
comment first and check the comment is still true of the copy.

## Portable Candidate

Abstract pattern: a severity constant with BOTH arms pinned by test, so a gate can ship
its mechanism before its teeth and the later arming is a proven one-line change rather
than a first execution.

Triggering evidence: the operator held this floor at REVIEW pending a cost measurement,
and the changed-line gate then correctly reported every blocking line uncovered — which
would have made the eventual flip the first time that code ran.

Intended consumer shape: any repo introducing a gate whose cost is not yet known.

Destination: **not portable yet — one instance.** This repo has shipped rules that did
not survive their second case, and a pattern with one worked example is exactly that
shape. Reopen when a second gate uses it.

## Lesson Evaluation

Four lessons from the frozen bundle changed a specific action, each with the
counterfactual the anchor rule requires; scores are appended to the ledger.

Answering the harmful question first, as the solicitation asks: **none of the ten
pushed me toward a wrong action, and none cost a read that returned nothing.** The six
unscored lessons had no occasion in this work — `isolated-agent-base-mismatch` (no
isolated spawn), `goal-closeout-evidence-binding` (no goal completion), and the rest —
and an unscored lesson here means no encounter, not a silent failure.

Lesson evaluation: {"session_id": "2026-08-18-7647b3e5-9327-4d3c-99ba-2e0688df29ac", "status": "effect-recorded", "score_event_count": 4}

## Next Improvements

- **workflow — write the cheapest bypass first.** For every refusal added to a proof
  surface, construct and test the cheapest mutation that gets past it BEFORE writing the
  refusal's passing test. Four escapes this session were all cheapest-bypass shaped and
  none was found by me. Applied: the slice-2 repair commit adds exactly these tests
  (`test_an_ordinary_english_issue_lead_is_not_a_defer`,
  `test_a_typed_status_may_not_be_a_sentence_opener`,
  `test_an_impossibility_disposition_beside_a_claim_is_refused`).
- **workflow — never delete a source before the copy is confirmed, and never use a
  guessable shared temp path.** This retro's first draft was destroyed by
  `cp X /tmp/retro-body.md && rm X && persist`, where the persist refused and the temp
  path already belonged to another session. Applied: the rewrite uses a
  process-unique directory, and the source is deleted only after the persist succeeds.
- **capability — a floor that adds a required field ships its authoring surface.**
  `Probe record` reaches no template, no shape describer, and no reference doc, so an
  author's discovery path is the error message. Tracked issue, with the generalized
  pattern and destination below.
- **memory — the goal artifact's frame now carries slice 3's measured groundwork** so a
  compacted or resumed session does not re-derive that `what_reads_this.py` cannot
  express a shape while `consumer_files()` already does. Applied: `## Active Operating
  Frame`, Next action.

## Retro Dispositions

- `applied: the cheapest-bypass tests` — committed in the slice-2 repair commit; three
  named tests pin the escapes that were measured landing unbacked closes.
- `applied: the severity switch with both arms tested` — committed; `PROBE_RECORD_SEVERITY`
  plus `test_the_severity_switch_is_the_only_thing_that_decides_vetoing`.
- `applied: slice 3's groundwork recorded in the frame` — committed in the goal artifact.
- `applied: the retro's own rewrite uses a process-unique temp path and deletes nothing
  before the persist succeeds` — the fix for the draft this session destroyed.
- `tracked issue: the authoring surface for a newly-required carrier field.`
  Structural pattern: a rung-1 floor that adds a required carrier field ships without the
  template, shape describer, or reference doc that would teach an author to write it, so
  the field's discovery path is the refusal message rather than the shape.
  Triggering instance(s): `Probe record #N:` reaches
  `skills/public/issue/scripts/templates/closeout_draft_stub.txt`,
  `describe_closeout_draft_shape.py`, `issue/references/closeout-discipline.md` and
  `release/references/publication-boundary.md` in none of them.
  Destination: charness (the floors and the authoring surfaces are both repo-owned here).

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-19-session-retro.md
