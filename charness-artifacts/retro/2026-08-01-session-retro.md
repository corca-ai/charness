# Session Retro
Date: 2026-08-01

## Context

One goal run, end to end: handoff chunked routing over the live backlog, the
operator's two queued decisions answered, then `achieve` shaped and `/goal` ran
the "un-dispositioned stragglers" chunk to completion. Five slices, six commits,
ten bounded review rounds. The unit worth reviewing is not any one repair — it is
what the review rounds kept finding, because that is now a four-session trend
with a sharper edge this time.

## Window

`cb35991e..1f6b1e38`, 2026-07-31 into 2026-08-01. Six commits: shape + operator
decisions, then A3 residual 1, S3's stub half, C6, the chunker's path resolution,
and record sync.

## Evidence Summary

- Goal artifact:
  [the stragglers goal](../goals/2026-07-31-disposition-the-stragglers-a3-c6-d4-d28-s3-stub.md),
  five slice reports with per-round critique detail.
- Host log probe: [the run's host log](../probe/2026-08-01-disposition-the-stragglers-a3-c6-d4-d28-s3-stub-host-log.json)
  — both hosts detected, token count `available`, duration/tool-call/turn counts
  `derivable`. Recorded as an evidence channel; no efficiency claim is made from
  it below, because the goal carried no `Host metric window:` line so the probe's
  `goal_metric_window` is `absent` and any per-slice number would be a proxy.
- Full suite: 6403 passed. Armed changed-line coverage over the committed range
  (`--base-sha cb35991e --refuse-unestablished`, source copy): `clean` after
  covering nine uncovered lines it found.
- Measurement script + its recorded run:
  [measure_evidence_residual.py](../../scripts/measure_evidence_residual.py),
  [the residual-floor probe](../probe/2026-08-01-evidence-residual-floor.json).
- Closeout telemetry: `mine_closeout_telemetry.py` over 1146 records — the top
  recurring gate-runtime finding is the standing pytest verify at 16 occurrences,
  peak 475s. Carried, not acted on this session.

## Waste

- **Two repairs were built, measured, and reverted.** Giving the commit-boundary
  preflight `--include-worktree` refused a critique artifact written for an
  earlier change; reusing the live-filter root as the citation root made a
  checked-in fixture inherit this repo and drop an entry. Both were correct
  instincts (close the divergence, arm the fix everywhere) and both were wrong in
  a way only execution showed. Not avoidable by more thinking — but cheaper if
  the existing suite had been run against the repair before the second one was
  designed.
- **The slice-log helper mangled a slice report.** Backticks in shell arguments
  were command-substituted, and the recorded report lost every code span before I
  noticed and rewrote it by hand. Pure transport waste.
- **Two pytest runs raced.** Running a full suite in the background while starting
  another produced 17 false failures and 21 errors in shared-state tests, which I
  then had to disprove with a clean serial run. The irony is the finding: that is
  the concurrency flake class sibling-scan Tier 2 D fixed for SessionStart hooks,
  reappearing one level up.
- **Not waste, though it looks like it:** ten review rounds on five slices. Nine
  of them changed the code. The one that did not (the disposition review) is the
  one the contract requires anyway.

## Critical Decisions

- **Reproducing before repairing re-sized three of five rows.** A3's planned
  legibility patch became a refusable hole; C6's "contract change" became one
  caller argument; S3's planned per-kind shape floor was measured and rejected
  before it was written. Each re-size came from execution, not from re-reading the
  audit prose the plan was built on.
- **Measuring before writing is what separated S3's third attempt from the two
  withdrawn ones — and the withdrawal reasoning itself turned out to be a
  mis-measurement.** The recorded case against the previous floor was "it failed
  34 existing tests, i.e. it sat above how this repo writes its own evidence."
  Those 34 were FIXTURES. The artifacts start at 427 bytes. A number nobody re-ran
  decided a design question for two attempts.
- **Cutting the plan on reviewer evidence rather than defending it.** Two
  reviewers independently found that one of the six selected rows had already
  shipped and another's remainder was a credentials decision. The operator picked
  a six-row chunk; recording that what remained was smaller beat padding the plan
  to match the selection.

## Trends vs Last Retro

The last retro recorded the two-round rule as **three-for-three**. This session
makes it **four-for-four**, and slice 4 extended the pattern a step further: round
1's repair created round 2's blocker, and round 1's *other* repair created a
regression that the repo's own existing test caught before any reviewer saw it.

The shape is now specific enough to state as a claim rather than a tally: **a
repair to verdict logic tends to carry the class it repairs, and it carries it in
the direction the author was not looking.** Slice 1's fix introduced a
status-letter allowlist four lines below the file's own comment arguing against
status-letter allowlists. Slice 2's fix landed a refusal category that three
consumer renderers could not name, in files whose comments each record fixing that
exact no-diagnosis defect once already. Slice 3's fix made an empty scope report
`evaluated`. Slice 4's fix broke a cross-source string intersection, then its
repair broke the same intersection again via a different field.

Also carried forward and still unapplied: teaching the changed-line gate's
`blocking_targets` payload to name when a blocked line's only coverage path is a
subprocess test.

## Expert Counterfactuals

**Engelbart, `system-improving-itself`.** Engelbart's distinction is between
improving the work and improving the capability that does the work. Nine of ten
review rounds changed code; every one of those findings arrived as prose I then
hand-folded. The counterfactual he would push: the repeated finding here is not
any individual defect but that *a new refusal category has no renderer* and *a
widened scope has no report line* — both are structurally detectable. A
`check_refusal_category_rendered` gate, keyed on any new bucket that feeds `ok`
without appearing in a consumer's message builder, would have caught slice 2's
blocker without a reviewer. That is the C-level move; ten hand-folded rounds is
the B-level one, and it does not compound.

**Direct lens: the person who has to re-run the number in six months.** Every
design decision in this session that went wrong twice went wrong because a
measurement was recorded as prose. The S3 floor was withdrawn twice on a number
nobody could re-run; the fix this time is a checked-in script plus a recorded run
plus a test that re-runs the recorded run against today's tree. That pattern —
*the measurement is a script, not a sentence* — is the transferable move, and it
applies to every threshold in this repo that currently lives in a comment.

## Sibling Search

- axis: **same-shape surface** | location: every refusal bucket that feeds `ok` in
  `check_prescribed_skill_executed_lib` and its three consumer renderers |
  decision: **fixed in-slice** | proof: slice 2 round 2 found `stub_evidence`
  unrendered in `check_goal_artifact`, `describe_goal_closeout_shape`, and
  `check_issue_closeout_commit_msg`; all three now render it | follow-up: none
- axis: **same-mechanism** | location: thresholds recorded as comments rather than
  as re-runnable measurements — `MIN_SKIP_DETAIL_LENGTH`, the dup-ratchet
  baselines, the coverage floors | decision: **valid follow-up outside the slice**
  | proof: `MIN_BOUND_RESIDUAL_CHARS` needed a script before it could be defended,
  and its two predecessors died without one | follow-up: deferred
  `measurement-as-script` handoff anchor
- axis: **same-consumer** | location: exact-string boundary-token intersection in
  `chunked_routing_merger` — any future normalization change on one source breaks
  it silently | decision: **valid follow-up outside the slice** | proof: slice 4
  broke it twice, once by slash and once by base, and neither had a test until
  this session added them | follow-up: deferred `boundary-token-symmetry` handoff
  anchor

## Portable Candidate

- Abstract pattern: **a deterministic gate that refuses on a new category must
  prove that category is renderable by its consumers.** A refusal an author meets
  by failing a flip, with no message naming it, is worse than no gate.
- Triggering evidence: slice 2 round 2 — a new `ok=False` bucket left three
  renderers emitting a prefix with an empty tail, in files that each document
  having fixed that same defect for an earlier bucket.
- Intended consumer shape: any repo whose closeout/commit gates build
  human-facing messages from named refusal sets.
- Destination: **not portable yet — `quality`, as a gate-design reference rather
  than a skill.** It needs one more independent instance before it earns a
  checkable form; a detector keyed on "bucket feeds `ok` but appears in no message
  builder" is plausible but unproven.
- First-prompt acceptance claim: "adding a refusal category to this gate produces
  a message that names it, in every surface that renders the gate's verdict."

## Next Improvements

- workflow: **run the existing suite against a repair before designing the next
  one.** Both reverted repairs this session were designed on top of an untested
  predecessor; the fixture regression in slice 4 was caught by a test that already
  existed and would have been free to run.
- capability: **a `blocking_targets` payload that names subprocess-only coverage
  paths** — carried forward unapplied from two retros now, and this session's nine
  uncovered lines included exactly that shape. Still owed its own two-round review.
- memory: **the two-round rule is four-for-four, and the class arrives in the
  direction the author was not looking.** Written into the goal's slice log and
  the recent-lessons digest, not just here.
- memory: **a threshold defended by prose gets withdrawn; a threshold defended by
  a checked-in script survives.** The S3 floor is the worked example — script,
  recorded run, and a test that re-runs the recorded run.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-01-session-retro.md
