# Session Retro
Date: 2026-08-01

## Context

One goal run end to end — handoff chunked routing, two operator decisions, then
`achieve` shaped and `/goal` ran the "un-dispositioned stragglers" chunk through
five slices and seven commits.

**This retro replaces an earlier one written the same day.** The first version was
composed while the goal's disposition review was still in flight, and that review
returned the session's most important finding. A retro that misses the finding
that most changes the next session is not a small miss; it is the retro failing at
its one job. The re-run is itself the first evidence below.

## Window

`cb35991e..056db667`, 2026-07-31T12:53:29Z → 2026-07-31T17:42:06Z — **4h 49m**,
2074 session records, 0 context compactions.

## Evidence Summary

Measured, from the Claude host session log via
`probe_host_logs.py --format markdown` plus a direct read of the same JSONL:

| signal | measured |
| --- | --- |
| wall clock | 4h 49m |
| my output tokens | 656,381 |
| subagent output tokens | 895,847 across 13 spawns |
| cache read | 338,900,879 |
| tool calls | 560 — Bash 519, Agent 13, Edit 11, Read 9, Write 4, Skill 3, AskUserQuestion 1 |
| explicit `sleep` polling | 45 calls, 5,075s = **84.6 min (29% of the session)** |
| reviewer wall time | 3,029s = 50.5 min (mean 233s, 68,911 tokens per review) |
| bash calls that were python heredocs mutating files | 158 of 519 |

Also read: the run's
[goal artifact](../goals/2026-07-31-disposition-the-stragglers-a3-c6-d4-d28-s3-stub.md),
the six [slice and disposition critiques](../critique/), the
[prepare packet](./2026-07-31-174143-packet.md) over `cb35991e..HEAD`, and
`mine_closeout_telemetry.py` over 1146 records (top recurring gate-runtime finding:
the standing pytest verify, 16 occurrences, peak 475s — carried, not acted on).

Gates: full suite 6403 passed; locked closeout with mutation-coverage production
completed 0 FAIL; armed changed-line coverage `clean`; dup-ratchet 0 new families.

Cached input is **not** counted as waste here, per the phase-aware-efficiency
reference — 338.9M cache reads across a 4h49m session with zero compactions is the
harness working, not a signal.

## Waste

**1. The retro ran in the wrong phase, and lost its own headline.** `achieve`'s
After-phase order is closeout evidence → retro. I ran `retro` while the
disposition review was still executing, because both were "closeout work" in my
head. The review then found that this goal's own acceptance line required one
critique artifact per slice and **none existed** — ten review rounds recorded only
as self-report inside the artifact being judged, which is sweep row S11's shape
running inside the goal that was repairing that class. The first retro does not
mention it. Cost: a persisted retro plus a `recent-lessons` digest refresh, both
redone. Phase: `verification`, claim strength `strong` (the timestamps are in the
transcript).

**2. 29% of wall clock was polling `sleep`.** 45 sleep calls totalling 84.6
minutes, against 50.5 minutes of actual reviewer execution. The excess is not the
reviews — it is that I slept in 115-second increments rather than doing
independent work, and that rounds across slices were fully serialized when slices
2, 3 and 4 had no dependency on each other. Within a round I did parallelize
(three plan reviewers, two slice-1 reviewers). Across rounds I never did. Phase:
`verification`, claim strength `strong`.

**3. 158 of 519 bash calls were python heredocs mutating files, against 15 total
Edit/Write calls.** The harness has dedicated file tools and guidance to prefer
them; I routed ~90% of my edits through the shell instead. This is not style.
It cost a concrete failure: backticks in a `append_slice_log.py` invocation were
command-substituted by zsh, and the recorded slice-3 report lost every code span
before I noticed and rewrote it by hand. Every heredoc edit is also invisible to
the harness's file-state tracking, which is why several edits came back with
"file modified since last read" warnings I then had to reconcile. Phase:
`implementation`, claim strength `strong`.

**4. Two repairs were built, measured, and reverted.** Arming the commit-boundary
preflight with `--include-worktree` refused a critique artifact written for an
earlier change; reusing the live-filter root as the citation root made a
checked-in fixture inherit this repo and drop an entry. Both were reasonable
instincts and both were wrong in ways only execution showed — but the second was
designed on top of an untested first, and the existing suite would have caught the
fixture regression for free. Phase: `implementation`, claim strength `strong`.

**5. Two pytest runs raced**, producing 17 false failures and 21 errors in
shared-state tests that I then spent a full clean serial run disproving. The
finding inside the waste: that is sibling-scan Tier 2 D's flake class one level
up — that row fenced the assertion against concurrent live *writers*, and
concurrent test *runners* are the same hazard from another direction. Opened as
S112.

**Not waste, examined rather than assumed:** subagent output (895,847) exceeded my
own (656,381) — the review apparatus cost more than the work it reviewed. Nine of
thirteen reviews changed the code, and three of those were blockers on gates that
decide whether commits and closeouts are refused. At ~69k tokens per review to
catch a fail-open in a commit gate, that trade is sound. What is *not* sound is
paying it serially.

## Critical Decisions

- **Reproducing before repairing re-sized three of five rows.** A3's planned
  legibility patch became a refusable hole; C6's "contract change" became one
  caller argument; S3's planned per-kind shape floor was measured and rejected
  before a line was written. Every re-size came from execution, not from re-reading
  the audit prose the plan was built on.
- **Measuring before writing separated S3's third attempt from the two withdrawn
  ones — and the withdrawal reasoning was itself a mis-measurement.** The recorded
  case against the previous floor was "it failed 34 existing tests, i.e. it sat
  above how this repo writes its own evidence." Those 34 were FIXTURES; the
  artifacts start at 427 bytes. A number nobody could re-run decided a design
  question twice.
- **Cutting the plan on reviewer evidence rather than defending it.** The operator
  selected a six-row chunk; two reviewers independently showed one row had shipped
  eleven days earlier and another's remainder was a credentials decision. Recording
  that the real remainder was smaller beat padding the plan to match the selection.
- **Accepting the disposition review's blockers rather than re-scoping the
  criterion.** The acceptance line requiring per-slice critique artifacts was mine.
  Weakening it after the fact would have been the exact escape
  `operating-contract.md` names; six artifacts were written instead.

## Trends vs Last Retro

The [2026-07-31 retro](./2026-07-31-session-retro.md) recorded the two-round rule
as **three-for-three**. This session makes it **four-for-four**, and it sharpened:

- slice 4's round-1 repair created round-2's blocker, and round 1's *other* repair
  created a regression the repo's existing test caught before any reviewer saw it;
- the class arrives in the direction the author was not looking. Slice 1's fix
  introduced a status-letter allowlist four lines below the file's own comment
  arguing against status-letter allowlists. Slice 2's fix shipped a refusal
  category three consumer renderers could not name, in files whose comments each
  record fixing that exact no-diagnosis defect once already. Slice 3's fix made an
  empty scope report `evaluated`.

Carried forward and **still unapplied for a third retro running**: teaching the
changed-line gate's `blocking_targets` payload to name when a blocked line's only
coverage path is a subprocess test. Three retros is no longer "carried" — it is
declined-by-inaction, and the honest move is to say so in the handoff or do it.

New trend, first observation: **the two-round rule has no analogue at the goal
level.** Every slice got a fresh-eye round on its repairs; the goal's own claims
got one review, at the very end, and it found two blockers. A goal is a verdict
surface too.

## Expert Counterfactuals

**Engelbart, `system-improving-itself`.** His distinction is between improving the
work (A), improving the capability that does the work (B), and improving how
capability itself improves (C). This session was strong at A and hand-rolled at B:
nine of ten review rounds changed code, and every finding arrived as prose I folded
by hand. The C-level reading of the measurements is sharper than "add a gate" — the
repeated finding is not any individual defect but two *structurally detectable*
shapes: a new refusal bucket that feeds `ok` with no consumer renderer, and a
widened scope with no report line. A `check_refusal_category_rendered` detector,
keyed on "bucket appears in the ok-computation but in no message builder", would
have caught slice 2's blocker without spending 316 seconds and 102k tokens on a
reviewer. That is the compounding move; ten hand-folded rounds is not.

**Direct lens: whoever has to re-run this number in six months.** Every decision
that went wrong twice went wrong because a measurement was recorded as prose. The
S3 floor was withdrawn twice on an unverifiable number; the fix this time is a
checked-in script plus a recorded run plus a test that re-runs the recorded run
against today's tree. *The measurement is a script, not a sentence.* This retro is
the same lesson applied to itself: the previous version declined to measure and
said "any per-slice number would be a proxy" — but output tokens, tool-call mix and
sleep time were all sitting in the session log, additive and honest, and one of
them (29% polling) is the largest single lever in the session.

## Sibling Search

- axis: **same-shape surface** | location: refusal buckets feeding `ok` in
  `check_prescribed_skill_executed_lib` and its three renderers | decision: **fixed
  in-slice** | proof: slice 2 round 2; all three now render `stub_evidence`, and
  `_refusal_bits` makes the next category one line | follow-up: none
- axis: **same-mechanism** | location: thresholds defended by prose rather than by
  a re-runnable measurement — `MIN_SKIP_DETAIL_LENGTH`, the dup-ratchet baselines,
  the coverage floors | decision: **valid follow-up outside the slice** | proof:
  `MIN_BOUND_RESIDUAL_CHARS` needed a script before it could be defended and its
  two predecessors died without one | follow-up: deferred `measurement-as-script`
- axis: **same-consumer** | location: exact-string boundary-token intersection in
  `chunked_routing_merger` | decision: **valid follow-up outside the slice** |
  proof: slice 4 broke it twice, once by slash and once by base, with no test until
  this session | follow-up: deferred `boundary-token-symmetry`
- axis: **same-workflow-phase** | location: the `achieve` After-phase order itself —
  nothing sequences retro *after* the disposition review, so running them
  concurrently is available and looks efficient | decision: **valid follow-up
  outside the slice** | proof: this retro is the second version because of exactly
  that | follow-up: deferred `retro-after-disposition-review`

## Portable Candidate

- Abstract pattern: **a deterministic gate that refuses on a new category must
  prove that category is renderable by its consumers.** A refusal an author meets
  only by failing a flip, with no message naming it, is worse than no gate.
- Triggering evidence: slice 2 round 2 — a new `ok=False` bucket left three
  renderers emitting a prefix with an empty tail, in files that each document
  having fixed that same defect for an earlier bucket.
- Intended consumer shape: any repo whose closeout or commit gates build
  human-facing messages from named refusal sets.
- Destination: **not portable yet — `quality`, as a gate-design reference.** It
  needs one more independent instance before it earns a checkable form.
- First-prompt acceptance claim: "adding a refusal category to this gate produces a
  message that names it, in every surface that renders the gate's verdict."

## Next Improvements

- workflow: **run `retro` after the disposition review returns, not beside it.**
  Concretely: closeout evidence → disposition review → fold → retro. This retro
  exists twice because that order was implicit rather than sequenced.
- workflow: **batch independent review rounds across slices, and do real work while
  they run.** 84.6 minutes of `sleep` against 50.5 minutes of review is the
  session's largest single lever, and slices 2-4 were mutually independent.
- workflow: **use Edit/Write for file mutation.** 158 heredoc edits against 15 tool
  edits cost one mangled artifact and repeated file-state reconciliation.
- capability: **`blocking_targets` should name subprocess-only coverage paths** —
  carried unapplied for three retros. Either land it or record it as declined; a
  third "carried forward" is not a plan.
- capability: **a refusal-category renderer detector**, per the Portable Candidate,
  once a second instance appears.
- memory: **the two-round rule is four-for-four, and the class arrives in the
  direction the author was not looking** — written into the goal's slice log, the
  six critique artifacts, and the digest, not only here.
- memory: **a goal's own claims are a verdict surface and got one review round, at
  the end, which found two blockers.** The slice-level discipline has no goal-level
  analogue.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-01-session-retro.md
