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

TWO HALVES OF ONE DECLARED SESSION, folded into one artifact because the lesson
evaluator's unit is the session and `duplicate-session-reference` refuses a session
claimed by more than one retro. I learned that by writing a second artifact and having
the pre-push lane refuse it — recorded here rather than quietly merged, because
claiming evidence that belongs to something else is the class this whole goal is about.

FIRST HALF — six commits, `8527936fd` through `f24f76b44`. Two slices, four bounded
review rounds (two per slice), plus the four-angle pre-implementation critique that
preceded activation.

SECOND HALF — thirty-four commits, `66116e14a` through the retro commit. Slice 3, slice
4 part 1, and slice 5 rows 1-26. TWELVE further bounded rounds across seven batches.
Census `accepted-risk-unguarded` 37 -> 11. Its full report is the
`## Second Window` section at the end of this artifact.

Push was deferred to after this retro by operator ruling, and happens once it lands.

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

## Second Window

Slice 3 through slice 5 rows 1-26, in the same declared session as everything above.

### Context

Slice 3 through slice 5's first twenty-six rows of the probe-provenance goal. The goal's
thesis is that a behavioral probe must not claim more than it measured, and that the
adapter-consumer debt is the corpus proving the mechanism on real rows rather than on one
worked example. This window is where that corpus got large enough to falsify things — and
it did, repeatedly, including the mechanism's own claims.

What matters next: nineteen rows remain, but they are now DECIDED rather than merely
unfinished, and the decision is recorded per row. The push this window has been holding is
the immediate next act.

### Window

Thirty-three commits, `66116e14a` through `68e53b82c`, all local. Slice 3, slice 4 part 1,
and slice 5 rows 1-26. TWELVE bounded review rounds across seven batches. Census
`accepted-risk-unguarded` 37 -> 11.

### Evidence Summary

- Twelve `bounded-reviewer` reports, all read-only, all spawned unnamed, each with a
  boundary fingerprint snapshot/verify around it (`ok: true`, `clean` or
  `parent-attributed` with every drifted path declared). Every finding was re-measured by
  the parent against the code before folding; several were refuted or narrowed on
  re-measurement.
- Ten probe records under `charness-artifacts/probe/2026-08-19-*.md`, each resolving
  `evaluated` / `verified` / `covers_all_call_sites: true` under
  `check_probe_record.py --require-evaluated`.
- Gate output: standing lane 10417 passed; `-m release_only` 102 passed at each batch
  boundary; changed-line proof `clean` at every commit — after being `blocked` twice and
  `no-verdict` once, each fixed rather than absorbed.
- `mine_closeout_telemetry.py` over 1779 closeout records: the recurring gate-runtime
  findings remain the broad pytest lanes (16 occurrences, 475s peak), all pre-existing.
- No host token/time telemetry is claimed. Commit-level and gate-level facts only.

### Waste

**The dominant waste was re-publishing a claim I had already been corrected on.** Not
re-deriving facts — re-asserting refuted ones. Three instances:

- The read-site rationale ("a refusal in `main()` would leave the importers reading
  charness defaults") was struck by rows 1-5's round 2, recorded in dup-review with the
  settled replacement — and I published it again for rows 6-13, into eight surfaces.
- Round 1 of rows 6-13 corrected the explicit-path exemption's wording; round 2 found the
  correction had landed in ONE of five surfaces.
- The `record_announcement` asymmetry claim went into a probe record, a census reason and
  a test docstring together, and was refuted whole.

The cost is not the wrong sentence, it is that one wrong sentence needs six to eight edits
and a review round to find. **The cheap detector is grep the phrase, not the file** — and
it was available every time.

**Second waste: four probe records shipped a polarity control that could not fail.** Each
time the published stimulus declared a field in a shape `adapter_lib` does not parse into
the type its validator requires — `command: [a, b]` as a flow sequence, `in_progress_sources`
as bare strings, `startup_probes` with `id` instead of `label`. Each time the matching TEST
FIXTURE was right. The section offered for independent replay was the wrong one, four
times, while the executable one was correct.

Not waste: the review rounds themselves. They cost more changed lines than the rows they
reviewed and found a blocker in every single batch.

### Critical Decisions

- **Keying the guard on the CONDITION rather than one check's wording.** Round 1 of slice
  5 found `version: !!int 9` — two characters — walking past every guard in the repo.
  `declarations_unhonored` replaced `version_refused` as the question consumers ask.
- **Adding the third door where the resolver reports it.** A silently dropped line lands in
  `warnings`, not `errors`, so an `errors`-only predicate answered False while the
  declaration was gone. `declarations_dropped` closed it for the ten resolvers that report
  it; the other six are `#673`.
- **Repairing `announcement_adapter_lib` ahead of `#673`.** One of the six, but its
  consumer is a publish gate, and two exit-0 bypasses were measured through it. Scope was
  widened deliberately and declared.
- **NOT widening `adapter_version_verdict` to ordinary invalidity**, twice. Where an
  ordinary field error still produced the harm (the prompt policy, the announcement source
  list), the refusal is CONSUMER-LOCAL and rests on that command's own contract. The shared
  predicate's polarity — never refuse because one unrelated field is typo'd — was preserved.
- **Deciding the remaining rows rather than leaving them open.** Five stay
  `accepted-risk-unguarded` with a measured caller-coverage reason and an argument for why
  a guard there would be wrong or impossible.

### North Star Alignment

The north star says brief a capable judge and keep teeth only where a wrong answer escapes,
and confirm at irreversible boundaries through a different observer and evidence channel.

This window is mostly the second clause. Every batch used a different observer (bounded
reviewers with no write capability) and a different evidence channel (the reviewer read
code; the parent re-ran CLIs). The single most valuable finding of the window —
`preflight_sources` cleared a delivery at exit 0 over a declared in-progress source — came
from a reviewer reading a validator's `continue` statement, and was confirmed by the parent
running the gate.

Where it fell short: the teeth were placed correctly but the CLAIMS around them were not,
and claims are what a later reader acts on. A guard that is right with a record that
overstates it is a proof surface that lies more quietly than no guard at all.

### Trends vs Last Retro

Against `2026-08-19-session-retro.md` (slices 1-2, four rounds):

- Round-1-not-clean is now 12 for 12. Not a fluke of the first slices.
- The class has SHIFTED. Slices 1-2's findings were mostly mechanism defects (an escape, a
  vacuous guard). This window's are mostly CLAIM defects — the guards held under attack
  almost every time; the records did not.
- New this window: two undeclared collateral changes (two planners, three announcement
  consumers), both found by review rather than by me. That class did not appear in slices
  1-2 because those slices touched fewer shared surfaces.

### Expert Counterfactuals

**Engelbart, system-improving-itself (the briefed lens).** Treat H + LAM + T as one unit:
design the TOOL alongside the language and method. This window improved LAM (the guard
vocabulary: three doors, one predicate) and H (my own detectors: grep the phrase, ask the
cheapest mutation). It did NOT improve T, and that is the gap.

Every claim-honesty failure was mechanically detectable and no tool detected it. A
`check_probe_record` extension that REPLAYS the record's own `## Stimulus` and diffs the
result against the recorded `## Base observable` would have caught all four dead controls
before publication — the information is already in the record, in a fenced block, next to
the arm it contradicts. Engelbart's point is that I kept exercising human vigilance on a
problem that wanted a tool, and the twelve rounds are the receipt.

The second T-gap: `check_adapter_consumer_classification`'s `guarded` token now spans four
coverage levels (three doors, one door, the raising variant, caller-covered) and the gate
sees one. I wrote per-row prose instead of a verdict vocabulary.

**Klein, pre-mortem on the next session.** Ask before starting: "it is three batches later
and a reviewer has found a blocker — what is it?" On this window's evidence the answer is
almost certainly (a) a control that cannot fail, or (b) a claim corrected in most of its
surfaces. Both are checkable in five minutes at the START of a batch rather than the end.

### Sibling Search

The transferable pattern is **a published artifact whose executable sibling disagrees with
it, where only the executable one is right**. Four instances here (record stimulus vs test
fixture). Axes scanned:

- **Same skill, other artifacts:** `charness-artifacts/probe/` is the only artifact class
  that carries a replayable stimulus. No siblings.
- **Other skills producing replayable evidence:** `debug` artifacts carry repro commands
  and `quality` carries gate invocations; neither is machine-replayed against a recorded
  observable. Same latent class, no measured instance — recorded, not claimed.
- **Docs:** the regenerable-facts gate already covers the count-in-a-doc case, which is the
  same shape one axis over, and it is EXECUTABLE. That is the precedent for the fix.
- **Gates:** `check_probe_record` verifies the QUOTE against its source but never the
  STIMULUS against its own recorded result. That is the gap and it is the follow-up.

Decision: **capability**, tracked. Not fixed in this window because it changes a proof
surface mid-slice.

### Portable Candidate

Abstract pattern: *an evidence record that publishes both a reproduction command and its
result should have the record's own gate re-run the command and diff the result, because
the two halves drift and only the executable half is exercised.*

Triggering evidence: four records in one slice whose published stimulus reproduced the BASE
observable at the control arm — i.e. proved nothing — while the test fixture beside them
was correct every time.

Intended consumer: any repo whose review artifacts carry repro steps.
Destination: `create-skill` is premature; this is an extension to an existing validator, so
the honest destination is the tracked issue below.
First-prompt acceptance claim: "a probe record whose stimulus no longer reproduces its
recorded base observable resolves `not-established`, naming the diff."

### Next Improvements

- **workflow** — start each batch with the two-question pre-mortem (can this control fail?
  where else does this sentence appear?) rather than discovering both at review. Applied
  this window only from row 24 onward, where the `in_progress_sources` mapping shape was
  caught BEFORE publishing for the first time.
- **capability** — teach `check_probe_record` to replay `## Stimulus` and diff against
  `## Base observable`. Tracked, not built here.
- **capability** — give the census a verdict vocabulary that distinguishes coverage levels,
  so `guarded` stops meaning four things. Tracked.
- **memory** — the handoff now carries the review pattern and the two detectors, so a
  pickup inherits them without reading twelve reports.

### Retro Dispositions

- `applied: docs/handoff.md` now records the two-door guard, the review pattern and both
  detectors (`515592403`, `00c50ed3f`).
- `applied: scripts/adapter_version_verdict.py` — the predicate is the condition, with
  three doors and a pinned marker (`342cce165`, `7ab091dc7`, `1465689ac`).
- `applied: scripts/check_adapter_consumer_classification.py` — the `guarded` witness is an
  AST call check, after a substring version passed on its own repair's comment
  (`7ab091dc7`).
- `tracked issue`: [#673](https://github.com/corca-ai/charness/issues/673) — six of sixteen
  resolvers discard both the parse refusal and the dropped-line report.
  Structural pattern: *a resolver that loads without capturing the parser's uninterpreted
  report cannot distinguish "declared nothing" from "declared something I dropped", and
  every guard downstream inherits that blindness.*
  Triggering instance(s): `announcement` (repaired here), `quality`, `narrative`,
  `critique`, `achieve`, `create-skill`. Destination: this repo.
- `tracked issue`: [#674](https://github.com/corca-ai/charness/issues/674) — the
  stimulus-replay validator.
  Structural pattern: *an evidence record publishing both a reproduction command and its
  result should have its own gate re-run the command and diff, because the two halves drift
  and only the executable half is exercised.*
  Triggering instance(s): four probe records in this slice whose published stimulus
  reproduced the BASE observable at the control arm. Destination: this repo
  (`check_probe_record.py`).
- `tracked issue`: [#675](https://github.com/corca-ai/charness/issues/675) — the census
  verdict vocabulary.
  Structural pattern: *a classification token that comes to mean several materially
  different states, while its gate's witness checks only that the token's helper is
  mentioned, reports a decision it is no longer making.*
  Triggering instance(s): `guarded` now spans all-doors, version-only, the raising variant,
  and caller-covered. Destination: this repo (`check_adapter_consumer_classification.py`).
  Neither is built here because each changes a proof surface and would owe its own two
  rounds.
