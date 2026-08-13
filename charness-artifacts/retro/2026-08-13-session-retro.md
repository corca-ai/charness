# Session Retro
Date: 2026-08-13
Goal: charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md

## Context

This session reconciled the fixed 22-issue cohort without converting an OPEN
tracker state into a completion claim. It repaired #607's conservative static
subprocess-settlement inventory, recorded #527 as an operator-owned product
decision rather than inventing its lock/docs design, and made the execution
ledger, goal, and handoff agree on the final frozen reconciliation.

The trustworthy evidence is the committed local proof, the two-round bounded
reviews for #607, and GitHub issue/comment readback. The 22 carriers were
checked by asking each issue reader for its comment URLs; a browser comment URL
fragment was not treated as a REST comment identifier. No push, release,
remote CI, issue close, or hosted behavior proof occurred.

## Window

`022c09a9..7f9733ed`, including #607's implementation and the frozen cohort
reconciliation. The branch remains ahead of `origin/main`; all 22 cohort issues
remain OPEN by design pending the goal's final closeout conditions.

## Evidence Summary

- `1570ba32` adds the #607 settlement inventory and focused regressions;
  `tests/quality_gates/test_standing_test_economics.py`,
  `test_subprocess_settlement_inventory.py`, and `test_quality_skill_docs.py`
  passed (45 tests).
- `charness-artifacts/critique/2026-08-13-issue-607-subprocess-settlement-inventory-resolution.md`
  binds the two bounded review rounds. R1 caught no-timeout/mixed-stream
  false-greens; R2 caught dynamic-timeout false-greens. The last R2 repair is
  recorded accepted-unreviewed under the two-round cap, not silently approved.
- `charness-artifacts/issue/2026-08-13-issue-527-brief.md` and its GitHub
  carrier keep #527 OPEN until an operator chooses the product boundary.
- `charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md` has
  22 rows. Live reconciliation found 22 matching OPEN tracker issues, 22
  matching carrier comment URLs, and neither a ledger-only nor tracker-only
  issue number.
- `mine_closeout_telemetry.py --detail` read 1,652 historical records through
  2026-08-12. Its recurring slow-gate/over-slice signals are local-machine
  history, not evidence for this session or a safe budget change; #503 already
  owns their remeasurement boundary.

## Waste

The initial reconciliation probe used a GitHub browser comment URL's visible
fragment as though it were the REST comment id. It returned 404, but no absence
claim was made; the method was corrected immediately to issue-reader comment
URL matching. This was small, reversible rework caused by confusing two
identity channels, not a tracker defect.

#607's R1/R2 repair cycles were not avoidable waste: the first draft would have
said finite/bounded where a process may wait forever or capture an unbounded
stream. The reviews found the exact false-greens before shipment. The planning
lesson is narrower: generate the final critique packet after the final repair,
not before it, so review identity and repaired code do not require extra packet
turns.

The telemetry miner still reports recurring full-pytest, release-bundle,
read-only-pytest, and over-slice cost. This is a standing gate-baseline cost,
not a reason to weaken proof: #503 records the quality/achieve owner split and
requires a matched remeasurement before changing execution or budgets.

## Critical Decisions

1. **Keep #527 as `unproven-defer`.** Product-lock, docs lifecycle, and working
   criteria were not specified. A decision brief and OPEN carrier preserve the
   question without fabricating a feature.
2. **Treat #607's static signals as conservative facts, not runtime truth.** A
   literal finite timeout is the only finite lifecycle claim; dynamic/absent
   values and process-tree ownership remain unknown. This constrained the code
   and prevented an attractive but false completeness claim.
3. **Freeze the cohort by reconciliation, not closure.** Every row has local
   proof, split, or tracker-visible defer, while GitHub stays the source of
   truth for OPEN state. This makes the release decision inspectable without
   laundering unresolved product premises into “done.”

## Trends vs Last Retro

The prior durable retro says the existing #503 telemetry cluster must not be
filed again; the current miner reports the same class and remains bounded by
the same owner. The stronger current improvement is claim discipline: this
session's #527 premise was explicitly deferred, while #607's later repair is
explicitly accepted-unreviewed rather than described as a completed second
review.

## North Star Alignment

**P4/P5 held.** #607 crossed an irreversible proof-surface boundary only with
independent bounded readers, and GitHub carrier presence was verified through
the issue reader rather than inferred from local files. Both channels caught or
could falsify an author claim.

**P1 held for #527.** The evidence did not establish a concrete defect with a
safe implementation choice, so the work stopped at a named operator decision.

**Mis-applied method corrected:** the first 404 reconciliation probe confused
URL display identity with REST identity. The result was treated as a failed
method, not an evidence verdict, then replaced with the appropriate reader.

**Failure signature avoided:** “local green becomes terminal trust.” Focused
tests and carriers establish local/tracker facts only; they do not establish a
push, release, hosted behavior, or cohort closure.

## Expert Counterfactuals

**Douglas Engelbart — design Tool, Language, and Method together.** The
settlement scan's first contract could have named literal-timeout, output-stream,
and ownership uncertainty as a small table before implementation. That would
have aligned the static tool with the conservative language and reduced the R1
repair surface; the separate reviewer remains necessary for adversarial cases.

**Falsification-first operator lens.** A carrier URL is a web-facing locator,
not automatically an API primary key. The first reconciliation command should
ask whether the identifier type matches the reader's contract before interpreting
its response. This changes the next move from “retry a 404” to “select the
evidence channel that owns the fact.”

## Sibling Search

- same layer: `skills/public/issue/scripts/issue_tool.py read` comment URL
  output | decision: same waste, fix now | proof: the final 22-row reconciliation
  used it to verify every exact carrier URL after the REST-id probe failed.
- abstraction up: `scripts/prepare_packet.py` identity binding | decision:
  intentional boundary | proof: packets bind a particular reviewed state; a
  repair necessarily needs a new packet rather than mutating an old identity.
- specialization down: `skills/public/quality/scripts/surface_marker_lib.py`
  timeout/output classifiers | decision: same waste, fix now | proof: #607 now
  tests no timeout, dynamic timeout, and mixed DEVNULL/PIPE streams.
- mental-model siblings: `charness-artifacts/quality/2026-08-05-issue-503-runtime-budget.md`
  | decision: intentional boundary | proof: the same historical telemetry class
  already has named quality/achieve owners and a matched-measurement condition.

Structural-follow-up destination: applied: #607 focused tests and the frozen
reconciliation method; none — #503 already owns the telemetry remeasurement.

## Next Improvements

- **workflow**: Before interpreting an external-read failure, check that the
  supplied identifier belongs to that API/read channel. Keep a failed probe as
  method evidence, never as absence evidence. (recurrence-class: evidence-channel-identity)
- **capability**: For conservative static inventories, write the known/unknown
  signal matrix before implementation and keep dynamic values unknown unless a
  direct parser proves them. (recurrence-class: conservative-static-verdicts)
- **memory**: Keep the goal, execution ledger, handoff, this retro, and #527's
  decision brief as the release-boundary record; #503 remains the owner of the
  historical runtime-cost question. (recurrence-class: premises-not-debt)
- **workflow**: freeze source, export, evidence receipt, and review inputs before
  minting one final packet; regenerate only when that reviewed identity truly
  changes. (recurrence-class: proof-surface-review-binding)
- **capability**: operate the local lesson ledger as a real loop by declaring a
  preview session and actually presenting its list before work, then recording only sparse, anchored effects at retro;
  do not infer continuity from the existence of the scripts.
  (recurrence-class: durable-lesson-ledger-first)
- **memory**: keep handoff state behind links to its goal, issue, debug, retro,
  and ledger owners; a green ownership-shape gate does not justify inline SHA,
  version, or test-count receipts. (recurrence-class: guard-adjacent-to-action)

## Packet Consumed

- `charness-artifacts/retro/2026-08-12-180732-packet.md`
- `charness-artifacts/retro/2026-08-13-090345-packet.md`

## Continuation: Issue #615 Focused Verdict Repair

### Context and Evidence

The late-arrival #615 slice repaired a focused changed-line coverage wrapper
that widened the standing test population with `--include-release-only`, even
though the broad mutation campaign deliberately excludes that marker. The
authoritative wrapper now executes the nonempty command owned by the command
suggester, the checked-in plugin export is byte-identical, and a real
release-only child sentinel proves that focused execution cannot silently add
the marker again.

The strongest behavioral evidence is the isolated historical-range replay in
`charness-artifacts/debug/2026-08-13-issue-615-focused-changed-line-false-clean.md`:
the repaired wrapper exits 1 and reports exactly lines 116, 117, 132, 133, and
134 as missing for base `d0c33e6b4a653bd758f5e5910c115819dd0333b4`.
Focused verification passed 132 tests. Two bounded critique rounds read the
repair; round 2 caught the stale plugin export before closeout. These are local
facts only: no push, hosted CI, GitHub closure, or installed-consumer readback
occurred.

### Waste and Critical Decisions

The packet/critique binding was regenerated several times because exact
historical evidence and its declared digest continued changing after a packet
identity had been minted. This repeats the recent lesson that evidence identity
must be frozen after all source, export, and receipt synchronization, not while
review findings can still mutate the bundle. The independent review itself was
not waste: it found the installed-plugin false-clean path that same-agent source
inspection had missed.

The decisions that constrained the outcome were: keep broad marker policy as
the population owner; consume the suggester-owned command rather than build a
second command in the wrapper; preserve the exact historical command and
dirty-worktree nonclaim; and stop at a local direct-commit carrier without
turning `Closes #615` into a publication claim.

### North Star and Expert Counterfactual

The irreversible proof-surface boundary used a different observer and evidence
channel: round 2 inspected the exported plugin, while the historical-range
runtime replay falsified the old clean verdict. This is the north-star behavior
the slice needed; source parity tests alone would not have exposed the stale
export at the moment it existed.

Douglas Engelbart's system-improving lens would treat packet generation,
derived-surface sync, and critique binding as one Tool/Language/Method unit.
The changed next move is a declared freeze stage — mutate, sync every export and
receipt, validate, then mint the packet once — with a binder that rejects a
critique record whose declared packet digest is no longer current. That makes
the workflow enforce the lesson instead of relying on reviewers to remember it.

### Trends and Next Improvements

The 1,689-record local telemetry read still shows the same recurring broad-gate
and over-slice classes already owned by #503; occurrence is a cost signal, not
permission to weaken this slice's proof, and it says nothing about other repos.

- **workflow**: freeze source, generated export, exact runtime receipt, and
  critique text before minting the final review packet.
- **capability**: make critique binding validation reject a stale declared
  packet SHA/identity before review closeout, rather than discovering it during
  repeated readbacks.
- **memory**: retain the exact historical command, coverage fingerprint, five
  missing lines, and hosted/public nonclaims in the debug record.

The sibling at the abstraction layer remains `scripts/prepare_packet.py`'s
intentional immutable identity boundary. The improvement is sequencing and a
stale-binding validator around that boundary; no new tracker item is filed in
this slice because the existing recent lesson already names the recurrence and
the current repair demonstrates the required sequence.

## Continuation: Lesson Evaluation and Handoff Audit

### Evidence and Verdict

The lesson-evaluation mechanism is valid but was not continuously operated.
Before this audit, `check_lesson_ledger.py` validated 16 seeded lessons, two
declared sessions, and three score events; all three scores were `+2` records
from 2026-08-12. The #615 slice added no declared session or score, so the
evidence stream had paused rather than silently continuing.

The reason was structural: `docs/development.md` documented the local session
and score commands, but the installed `retro` workflow neither surfaced its
adapter evidence nor reminded the operator about them. The generated
`recent-lessons.md` digest also still names
its old advisory recency/recurrence policy; ledger scores feed the deterministic
preview, not the currently injected digest. Therefore the repo has a working
evaluation tool and a first cohort, but not yet an end-to-end feedback loop.

This audit recorded the third deterministic preview session,
`2026-08-13-issue-615-retro-handoff-audit`, before adding any new score. Its
snapshot lists 10 of 16 eligible lessons and is locally replayable. That proves
declared containment only, not human exposure, causal usefulness, or policy
calibration.

After the same deterministic list was actually read during this audit and
changed its actions, three sparse scores were
recorded: `+1` for ledger-first sequencing, `+3` for freezing review inputs
before packet creation, and `+2` for replacing handoff receipts with owner
links. The ledger now holds three sessions and six scores. The signs remain
positive-only, so the comparative score-policy goal correctly stays dormant.

The handoff shape gate was already green: 46 content lines, no unowned
`Current State`/`Next Session` entries, and no dated diary sections. Semantic
inspection still found avoidable inline receipts — a pushed SHA, version-like
release facts, and test counts — while the current #615 retro and lesson ledger
were not linked. The refreshed handoff keeps the required machine claim but
moves human continuation state back to owner links.

### Waste, Decisions, and Trend

- The ledger capability existed for roughly one day without a workflow trigger.
  That is not a data-loss bug: no session was fabricated. It is a method/tool
  gap that made “evaluation continues” false unless an operator remembered the
  development command. (recurrence-class: durable-lesson-ledger-first)
- #615 repeated the packet-binding churn already named by the selected lesson.
  In this follow-up the evidence facts and lesson session were frozen before
  minting one retro packet, so the lesson changed the sequence rather than only
  describing the prior miss. (recurrence-class: proof-surface-review-binding)
- The handoff validator proved ownership form, not semantic compression. The
  link audit removed regenerable receipts and made the current retro/ledger the
  owners of the claims that matter next. (recurrence-class: guard-adjacent-to-action)

The trend is mixed: yesterday's reform successfully prevents scores outside a
declared preview snapshot and rejects hand-edited projections, but today demonstrates
that containment teeth alone do not create observation cadence. The first
cohort was real and conservative; it was not a self-sustaining loop.

### North Star and Expert Counterfactual

The audit keeps the evidence boundary honest: three sessions and the recorded
scores are local declarations, while the digest, human usefulness, and score
policy remain unproven. The handoff follows the same rule by linking to owners
instead of transcribing a green receipt as terminal trust.

Douglas Engelbart's system-improving lens exposed the missing unit: the Tool was
the ledger, the Language was declared-session/score containment, but the Method
lacked a session-start and retro-close trigger. This slice repaired that unit:
repo-local adapter evidence exposes the ledger and authoring procedure, while
the public retro contract requires contemporaneous presentation, sparse scores,
and an explicit no-score disposition when presentation is unproven. The digest
remains unchanged until comparative evidence warrants reviewed policy change.

### Sibling Search and Next Improvements

- same layer: the local RCA ledger is prompt-wired through shared debug/issue/
  retro closeout instructions | decision: valid follow-up | proof: RCA events
  continued during #615 while lesson scores did not.
- abstraction up: usage episodes are emitted by slice closeout | decision:
  intentional boundary | proof: automatic objective events are appropriate
  there, while lesson scores still require agent judgment and anchors.
- specialization down: the contract register has zero live citations/catches |
  decision: valid but defer | proof: its specification already treats citation
  signal as an unproven probe rather than a required cadence.
- mental model: `recent-lessons.md` selection and lesson-ledger scoring |
  decision: intentional boundary | proof: the former remains advisory derived
  memory; the latter is measured local preview evidence and must not be
  described as controlling the digest yet.

- **workflow**: declare and actually present a deterministic lesson session at
  the start of the next meaningful repo slice, then record only sparse anchored
  effects during retro.
- **capability**: applied — the Charness adapter now surfaces ledger state and
  local authoring procedure, while the public planner exposes adapter evidence
  without hardcoding this repo's score schema or commands.
- **memory**: link the current retro, ledger contract, and dormant comparative
  score-policy goal from the handoff so the next operator sees both the evidence
  and the activation threshold.

Portable Candidate: not portable in its current form — identity, citations,
and session containment depend on this repository's checked-in retro corpus.

### Skill Improvement Closeout

The follow-up converted both misses into public-skill behavior without changing
score policy or validator verdicts:

- `handoff` now runs rules and current-target preflights before editing, then
  performs a semantic receipt/owner audit because deterministic literal checks
  cannot recognize every copied proof receipt. Immediate prerequisites must
  precede the governed slice in `Next Session`; future automation in `Discuss`
  is not a substitute.
- `retro` now promotes ordered adapter evidence into required reads with
  file/directory/missing disclosures. Its lesson-evaluation reference requires
  a contemporaneous session-start presentation, forbids retro backfill, and
  records `not evaluated` in the retro rather than inventing a ledger receipt.
- `.agents/retro-adapter.yaml` declares the local ledger and authoring procedure;
  `docs/development.md` now separates session-start presentation from retro-time
  sparse scoring.

The capability brief and pre-implementation review are durable at
`charness-artifacts/create-skill/2026-08-13-handoff-retro-feedback-loop-brief.md`
and
`charness-artifacts/critique/2026-08-13-handoff-retro-skill-feedback-loop.md`.
Focused planner/skill/dogfood tests passed 65 cases; skill, ergonomics,
packaging, handoff, ledger, Ruff, and canonical/export parity checks passed.
Cautilus mappings were inspected but not executed because evaluation remains
ask-before-run.

### Packet Consumed

`charness-artifacts/retro/2026-08-13-issue-615-memory-audit-packet.md`

## Continuation: Lesson-Evaluation Continuity

### Context, Window, and Evidence

This continuation reviews the structural answer to the user's question: how a
future operator can know that lesson evaluation keeps happening without relying
on the agent saying it will remember. The window begins with the audit above,
which established that the #615 work had no contemporaneous lesson session, and
ends with the repo-local continuity implementation and its two bounded review
rounds.

Strong evidence is the completed
`charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md`,
the implementation critique, the focused continuity/planner/scaffold/quality
runner tests, and the read-only continuity report. The report's activation-eve
baseline is zero eligible durable retros, zero dispositions, six historical
score events, and zero violations. That is a clean baseline, not evidence that
tomorrow's operation already happened.

### Waste and Critical Decisions

The first feedback-loop repair improved reminders and evidence discovery but
still left success as an anecdote: no durable-retro denominator could distinguish
an affirmative `no-effect` session from a skipped evaluation. The implementation
also initially put Charness-specific grammar in the generic public retro
scaffold. Round 2 caught that ownership inversion; the capped repair moved the
exact section and command back to the Charness adapter and development guide.
(recurrence-class: rule-exists-but-does-not-bind)

The decisions that constrained the result were:

- count only dated durable retro artifacts from 2026-08-14, not every host chat;
- require an explicit disposition and never infer success from score volume;
- keep `missing-start`, `emission-unproven`, and `presentation-unproven`
  distinct;
- bind one declared session to at most one retro;
- treat the start receipt as stdout-write evidence only, never proof of display,
  reading, use, benefit, or before-work ordering;
- put exact Charness policy in the repo adapter while the public retro skill
  carries only the generic adapter seam.

### Trends vs Last Retro

The earlier audit could only say that three sessions and six positive-only
scores existed and that operation had paused. The new report adds the missing
lifecycle denominator and typed miss states. It does not improve the evidence
that lessons are useful, and it deliberately leaves host sessions without a
durable retro outside the measured cohort.

### North Star Alignment

The mechanism now puts teeth only on mechanically observable continuity:
eligible retro presence, exact disposition shape, receipt consistency, unique
session ownership, and score-count reconciliation. Human presentation remains
a judgment and is represented by an honest `presentation-unproven` state rather
than a fabricated machine verdict.

The first draft mis-applied ownership by embedding one repository's evaluator
grammar in a public skill. A different observer caught that cross-surface leak;
the adapter seam is now generic and the Charness policy is adjacent to its
actual consumer. The remaining named failure signature is “local green becomes
terminal trust”: today's zero-violation activation-eve report cannot prove the
first eligible session will be operated correctly.

### Expert Counterfactuals

Douglas Engelbart's system-improving lens changes the unit from “remember the
lesson command” to one Method/Language/Tool loop: the handoff orders the start,
the adapter declares the section and metric, and the quality reporter reconciles
the durable result. W. Edwards Deming's feedback-loop lens adds the denominator
and explicit negative states; six scores without complete dispositions are not
a healthy process signal.

### Sibling Search

- same layer: Charness RCA conversion ledger | decision: intentional boundary |
  proof: RCA records detected events automatically, while lesson effect scoring
  remains a bounded human judgment.
- abstraction up: generic public retro scaffold | decision: same waste, fix now |
  proof: `artifact_sections` is adapter-declared and public guidance no longer
  contains the Charness command or JSON grammar.
- specialization down: Charness handoff and development guide | decision: same
  waste, fix now | proof: the handoff links the owner and orders the start;
  development owns the exact forms and non-claims.
- mental-model siblings: host chats without durable retros | decision: valid
  follow-up outside the slice | proof: no observer can yet distinguish meaningful
  work from incidental host opens without noisy repo writes; follow-up: deferred
  docs/handoff.md#discuss.

Structural-follow-up destination: applied: adapter-owned artifact sections,
next-session handoff ordering, and the continuity quality report; the broader
host-session denominator remains deferred to `docs/handoff.md#discuss`.

### Next Improvements

- **workflow**: before #614, run the start command, actually present the exact
  selected list, and carry its session ID into one retro disposition.
  (recurrence-class: durable-lesson-ledger-first)
- **capability**: inspect the first eligible cohort after 2026-08-14 with
  `python3 scripts/check_lesson_evaluation_continuity.py --repo-root .`; fix any
  typed violation rather than adding a score to improve the appearance.
  (recurrence-class: rule-exists-but-does-not-bind)
- **memory**: keep the handoff pointed at the continuity contract, development
  procedure, ledger state, and this retro instead of copying test counts or
  packet hashes. (recurrence-class: guard-adjacent-to-action)

### Portable Candidate

The generic pattern is portable: an adapter-declared evaluation section plus a
repo-owned read-only reconciliation command. The exact Charness grammar is not
portable. Destination: `create-skill` only after a second consuming repository
needs the seam; first-prompt acceptance is that a repo with no evaluator gets no
extra section or command.

### Packet Consumed

`charness-artifacts/retro/2026-08-13-104307-packet.md`

## Lesson Evaluation

Lesson evaluation: {"reason":"missing-start","score_event_count":0,"session_id":"none","status":"not-evaluated"}

This work began before the session opener and continuity contract existed. No
score was appended retroactively.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-13-session-retro.md
