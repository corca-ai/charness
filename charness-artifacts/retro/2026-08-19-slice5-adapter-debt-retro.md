# session retro

Date: 2026-08-19

Goal: charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md

## Context

Slice 3 through slice 5's first twenty-six rows of the probe-provenance goal. The goal's
thesis is that a behavioral probe must not claim more than it measured, and that the
adapter-consumer debt is the corpus proving the mechanism on real rows rather than on one
worked example. This window is where that corpus got large enough to falsify things — and
it did, repeatedly, including the mechanism's own claims.

What matters next: nineteen rows remain, but they are now DECIDED rather than merely
unfinished, and the decision is recorded per row. The push this window has been holding is
the immediate next act.

## Window

Thirty-three commits, `66116e14a` through `68e53b82c`, all local. Slice 3, slice 4 part 1,
and slice 5 rows 1-26. TWELVE bounded review rounds across seven batches. Census
`accepted-risk-unguarded` 37 -> 11.

## Evidence Summary

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

## Waste

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

## Critical Decisions

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

## North Star Alignment

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

## Trends vs Last Retro

Against `2026-08-19-session-retro.md` (slices 1-2, four rounds):

- Round-1-not-clean is now 12 for 12. Not a fluke of the first slices.
- The class has SHIFTED. Slices 1-2's findings were mostly mechanism defects (an escape, a
  vacuous guard). This window's are mostly CLAIM defects — the guards held under attack
  almost every time; the records did not.
- New this window: two undeclared collateral changes (two planners, three announcement
  consumers), both found by review rather than by me. That class did not appear in slices
  1-2 because those slices touched fewer shared surfaces.

## Expert Counterfactuals

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

## Sibling Search

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

## Portable Candidate

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

## Lesson Evaluation

Repo-owned lesson evaluator applies. The presentation boundary holds: this retro backfills
nothing and does not repair the handoff by asserting a lesson was learned — the two lessons
that changed behavior (grep the phrase; replay the stimulus) are recorded as one applied
change and one tracked issue respectively. The four score events below were emitted during
the window by the surfaces that own them, not authored here.

Lesson evaluation: {"score_event_count":4,"session_id":"2026-08-18-7647b3e5-9327-4d3c-99ba-2e0688df29ac","status":"effect-recorded"}

## Next Improvements

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

## Retro Dispositions

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

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-19-slice5-adapter-debt-retro.md
