# Lesson Ledger, Contract Register, and the Graduation Seam

Date: 2026-08-12

Operator-designed in session. This contract covers two coupled memory surfaces and
the single path between them. It is deliberately probe-heavy: the operator's
framing is that it cannot be right on the first try, and that the mechanism
itself becomes a retro subject.

## Problem

Two failures that look separate and are not.

**The lesson digest selects on the wrong signal.** `scripts/recent_lessons_lib.py`
ranks ~1,900 candidates by `recency_weight * (1 + alpha * (independent_sources - 1))`
and nothing else. There is no channel through which a session can report that a
lesson helped, so a lesson's score cannot depend on whether it ever worked. The
measured consequence is recorded in
[the harness-improvement thesis](./2026-08-11-harness-improvement-thesis.md): one
retro emitted five `Next Improvements` against four slots; the two dropped were
violated in the very next session, while a surviving slot held the line
`**memory** — This retro plus the recent-lessons digest.`, which instructs
nothing. Scarce capacity was spent on a non-lesson because recurrence rewards
whatever every retro emits.

**The contract layer only grows.** `AGENTS.md` and the docs under
[docs/conventions](../../docs/conventions/) accumulate standing rules with no
counter-pressure. Nothing measures whether a rule is ever used, and the cost is
paid on every session because these surfaces are always loaded. This slice's own
work is the demonstration: repairing the handoff gate promoted two lessons and
added a section to
[implementation-discipline.md](../../docs/conventions/implementation-discipline.md),
which is already past four hundred lines.

**The coupling is the reason for one contract.** The ledger's upward exit is the
contract layer's input. Fixing selection without fixing the contract lifecycle
turns graduation into a pump: the better the ledger works, the faster the
always-loaded layer rots.

## Capability Contract

**Actor:** the agent picking up a session, and the operator reviewing what the
repo asks agents to obey.

**Capability delta:** today an agent receives ten lessons chosen by recency and
repetition, and a contract layer whose every rule claims equal standing. After
this contract, the agent receives lessons selected by measured usefulness with a
deliberate exploration share, and every standing rule can be shown to have earned
its place by citation or by catching something.

**Acceptance boundary:** the ledger's selection and the register's counters are
computed by repo-owned scripts from checked-in state; the judgment calls
(scoring, citing, proposing a graduation) are agent work bound by anchors, and
the irreversible half (moving a rule into or out of a contract) stays behind
review.

## Current Slice

Part 1 (ledger) is the executable first slice. Part 3 (the graduation seam) is
specified here as a boundary only: this first ledger version does not represent
graduation, a contract target, displacement, approval, or registered status, and
its green result is not a graduation authorization. Part 2 (register) is
specified to the point of a probe, because its feedback signal is the least
certain thing here and building the counter before knowing it measures anything
would be the same mistake in a new place.

## Fixed Decisions

- **A lesson is a durable entity with an id, not a row re-derived each run.**
  Scores accumulate, so they cannot be recomputed from the retro corpus. The id
  is the existing author-declared `recurrence-class: <slug>` marker
  (`recent_lessons_lib.recurrence_class`), promoted from a grouping hint to the
  primary key. No second identity system, and no content classifier — the repo
  keeps content classification out of gates on purpose.
- **Ten lessons per session: 3 recent, 3 highest-value, 3 highest-uncertainty,
  1 archive resurrection.** Presented as a flat list of id plus text,
  deterministically shuffled by a session seed, with the bucket never labelled.
- **Ranking is a mean with a confidence bonus, never a sum.** `value = mean +
  c * sqrt(ln N / n_scored)`, with shrinkage toward zero for small `n_scored`.
  A sum lets frequently-shown items freeze the top, which is the failure this
  repo already measured once when recurrence counting put 121 copies of a release
  template above hand-authored lessons.
- **The exploration slots ARE the UCB term.** "Random, favouring rarely evaluated"
  is not implemented as a separate random draw; it falls out of the confidence
  bonus. One mechanism, not a heuristic stacked on a heuristic.
- **Scoring runs on the ten that were shown, on `-3..+3`.** A score whose
  magnitude is 2 or more must name an anchor: a concrete moment in the session — a
  decision, a file, a command — where the lesson changed or failed to change an
  action. Unanchored scores are capped at `±1`.
- **`-3` is asked for explicitly.** The retro prompt asks which of the ten pushed
  toward a wrong action or cost a read that returned nothing. Actively harmful is
  the most valuable and least volunteered signal.
- **Pool cap 50, archive is not deletion.** Archived entries keep their stats and
  remain drawable through the resurrection slot.
- **Two exits, asymmetric on purpose.** Archive (down) is automatic and
  reversible. Graduation (up) is a proposal only; the move into a contract is an
  operating-surface change and stays behind review.
- **Graduation is the ONLY path from ledger to contract register**, and it is
  subject to a conservation rule: a graduation that would push the register past
  its budget must name a displacement or a retirement.
- The first ledger version accepts no graduation-shaped transition or
  contract-target field. Conservation is deferred to the later register/proposal
  slice, which must calculate before/after membership in the register's unit
  universe and name the displaced or retired unit; free text in a ledger record
  is not conservation evidence.
- **Roles split by what each surface can see.** A script computes candidates
  deterministically. `retro` scores lessons and records citations, and does not
  judge graduation, because it sees one session and graduation is a multi-session
  claim. `quality` reads the candidate list and proposes, because "can this be a
  validator instead of prose" is its own question and contract changes already
  route through it.

## Probe Questions

- **Does the contract register's citation signal measure anything?** Planned
  signal: `retro` records which contract sections it actually leaned on, with an
  anchor, under a per-session budget. Failure mode is self-report — the same
  hindsight problem as lesson scoring, one layer up. Signal that it works: over a
  handful of sessions the histogram is uneven and its top matches what an
  independent reader would say the sessions leaned on. If the histogram is flat or
  tracks section order, the signal is noise and the register needs a different one.
- **Can catches be attributed to contract units mechanically?** A gate failure
  names a check, not a contract section. Mapping one to the other needs a declared
  link on each gate. Probe whether that mapping can be declared without inventing
  a second registry that itself rots.
- **What is a contract UNIT?** Section-level is the obvious cut and may be too
  coarse: `Critique Discipline` holds several independently-citable rules. Probe
  on the live corpus before fixing the granularity.
- **Does blinding change behaviour at all?** Presenting ten unlabelled lessons is
  anti-anchoring hygiene, not a blind — the agent can read the ledger file. Worth
  measuring once whether it matters, and worth dropping if it does not.
- **Is the counterfactual set worth its cost?** Scoring ten unseen lessons is the
  most expensive and least reliable part. Gate it to sessions where the pool holds
  items with `n_scored < 2`, use forced choice (name at most two that would have
  changed a specific action; everything else is zero), and measure whether it adds
  discrimination over the shown-set scores alone.
- **Does positive-score drift require a budget?** Start without a per-session
  positive cap: shrinkage toward zero, anchored large-magnitude scores, and later
  relative ranking may already discriminate. After a small scored cohort, inspect
  score distribution and selection concentration. Add a cap or centering rule
  only if all-positive drift is observed; do not choose an arbitrary cap now.

## Deferred Decisions

- Per-repo tracker id shapes for a portable version of any of this. The ledger is
  charness-local first.
- Whether the register should cover skill `SKILL.md` bodies as well as `AGENTS.md`
  and `docs/conventions/`. Start with the always-loaded surfaces.
- Whether decay belongs in the ledger's ranking at all, given staleness eviction
  already removes rules whose world is gone.

## Non-Goals

- Replacing `retro` as a practice. This changes what a retro's output feeds, not
  whether retros happen.
- A general-purpose agent memory system. The scope is this repo's two memory
  surfaces and the seam between them.
- Automatic contract editing. Nothing here writes to `AGENTS.md`.

## Deliberately Not Doing

- **Not adding a filter to the current selection policy.** The operator's
  standing instruction: that stacks a heuristic on a heuristic. The
  content-free-lesson problem is solved by scoring, not by a predicate that
  recognises bookkeeping.
- **Not deriving lesson identity from content.** A classifier rots exactly like
  the surface text it replaces, and this repo's deterministic-floor rule keeps
  content classification out of gates.
- **Not rotating contract rules.** A rule that fires one session in five is not a
  contract. The register measures usage; it never samples.
- **Not scoring contracts on `-3..+3`.** A negative score on an advisory lesson
  means "waste of a slot". On a binding rule it would mean "this rule is wrong",
  which is a much larger claim needing a different process.
- **Not imposing an uncalibrated positive-score budget.** A cap would force
  relative allocation before there is evidence that the observed scores need it;
  this stays a probe rather than a hidden scoring game.

## Constraints

- **The rebuild-determinism gate must change.**
  `recent_lessons_lib.check_lesson_selection_index` asserts the index equals what
  a rebuild from the retro corpus produces. Accumulated scores are not derivable
  from that corpus, so the gate becomes: ledger transitions are append-only and
  each transition cites the retro that produced it, while the still-derived parts
  (candidate extraction from retro sections) stay rebuildable and stay checked.
  The release helper path runs through this function and must be migrated with it.
- Cold start: ~1,900 undifferentiated candidates and no ids. Seed every currently
  eligible author-declared `recurrence-class` (16 at this contract's review), up
  to the later pool target of 25; do not invent a second identity to fill the
  difference. Include a Continuation Capability lesson only when its source
  already declares that marker rather than taking the top of the existing weight
  ranking.
- Everything must survive a repo whose retro corpus is empty; a consuming repo
  with no lessons gets an empty ledger, not an error.

## Success Criteria

1. A lesson that measurably fired in a session can outrank a fresher lesson that
   did not.
2. A content-free lesson loses its slot without any predicate that recognises
   content.
3. The contract register can name at least one standing rule that has neither been
   cited nor caught anything, with the evidence for that claim.
4. A schema-v1 graduation proposal that would exceed the fixed active-unit
   capacity cannot validate without naming existing active displacement units.
5. The digest becomes the only channel carrying a given lesson, so the channel
   comparison the thesis called impossible becomes possible.

## Acceptance Checks

- `unit` — ranking prefers a high-mean low-`n` lesson over a same-day one-off only
  after the confidence bonus is earned; pinned at the warmup boundary the way
  `tests/test_recent_lessons_recurrence.py` pins the current constants.
- `unit` — a score of `±2` or beyond without an anchor is rejected or clamped;
  score distribution remains inspectable so a later cap decision has evidence.
- `unit` — an archived lesson retains its stats and is reachable through the
  resurrection slot.
- `unit` — a graduation proposal that would exceed the register budget fails
  unless it names a displacement.
- `integration` — the append-only ledger gate rejects a transition whose cited
  retro does not contain the same single `recurrence-class`, rejects a duplicate
  marker, transition, or seeded identity, and rejects a hand-edited materialized
  score/state projection. Candidate extraction and digest rendering stay
  independently rebuild-checked.
- `manual` — after the seeding migration, the ten presented lessons are inspected
  once against operator judgment; this is the only check that can catch "the
  scores are technically consistent and the selection is useless".

## Boundary Ownership

- Verdict: owned-correctly

The ledger and register are charness-local state under `charness-artifacts/`,
computed by repo scripts. The consuming-repo question is deferred rather than
answered: nothing here ships in a public skill package yet. `retro` and `quality`
gain steps that read and write this state, which is the correct home for the
judgment halves, and the deterministic halves stay in `scripts/`.

## Critique

Design provenance and the known-weak joints, from a web survey run this session.

- The scoring half is the validated part. **ACE** (arXiv 2510.04618) tags each
  context bullet helpful / harmful / neutral after a task, keeps counters, and
  merges deltas deterministically rather than rewriting the whole context —
  motivated by *context collapse*, where iterative rewriting erodes detail into
  generic advice. This design is that shape with a wider score range.
- The exploration half should not be reinvented. **MemCon** runs memory control as
  a tabular contextual bandit with UCB and zero additional model calls.
- The weakest joint is named in the literature. **RoMeRL** calls it the
  Memory-Reward Trap: outcome-driven updates reinforce co-retrieved memories with
  little causal contribution, and *exploration reduces estimation variance but not
  attribution bias*. Stronger exploration alone does not fix it. The counterfactual
  set is the cheap approximation of the ablation that would, which is why it is
  specified as forced choice rather than dense scoring — **AEL** found LLM-driven
  credit assignment underperforms simpler methods in high-noise domains, and retro
  self-assessment is high-noise.
- Not claimed: none of this establishes that the digest channel changes agent
  behaviour at all. The thesis refuted the earlier claim that it does not, and did
  not replace it. Success criterion 5 exists to make that measurable, not to
  assume it.
- The self-evaluation clause is the operator's: this mechanism is itself a
  contract unit and a ledger subject. It gets cited or it does not, and its own
  lessons get scored like any other. A mechanism that cannot be seen working in
  its own histogram is a mechanism to retire.

## Canonical Artifact

This file, during implementation. The handoff points here rather than at the
thesis, which holds the defect analysis and two unimplemented proposals but not
this design.

## First Implementation Slice

The ledger's state file and its append-only gate, with nothing reading from it
yet: schema, id derivation directly from `recurrence-class`, the transition
record with a canonical repo-relative retro citation, deterministic replay, and
a gate that rejects a materialized projection that differs from replayed events.
Keep the existing candidate/digest rebuild check intact and compose it with the
new ledger transition check; do not replace it. Seed the currently eligible
declared classes (16 at review time), with each seed citing the exact source
retro and marker. This slice omits graduation, contract targets, displacement,
approval, register membership, selection, scoring, and presentation.

Selection, scoring, and presentation come second, because a ranking function
without durable state to rank is untestable, and the gate transition is the piece
that can break the release path if it is done late.

## Second Implementation Slice

Add replayed scoring state without implementing selection or presentation. A
schema-v2 ledger keeps the cited seed transitions unchanged and adds append-only
`score_events` with `event_id`, a repository-relative `source_retro`,
`lesson_id`, `score`, and optional `anchor`. Each score citation must declare the
same recurrence class, and a `(source_retro, lesson_id)` pair occurs once. Scores
are integers in `-3..+3`; an event with magnitude at least two requires a
non-empty anchor. The materialized score view is derived solely from events as
`score_total` and `score_count` per seeded lesson (including a count for a zero
score), and the validator rejects duplicate event IDs, unknown lesson IDs,
invalid score/anchor shapes, rewritten committed transition or event prefixes,
or a materialized-view mismatch. There is no positive-score budget in this
slice. The shown-set restriction, UCB ranking, archive state, shuffle seed,
selection output, register state, and graduation proposal remain out of scope.

## Third Implementation Slice

Add a deterministic, read-only selection preview that first validates both the
schema-v2 ledger and the checked-in lesson-selection index, then uses the same
in-memory rebuilt index to intersect non-empty `recurrence_class` values with
seeded ledger lesson IDs. It selects at most ten distinct lessons sequentially:
three recent slots, three high-value slots, three high-uncertainty slots, and one
archive-resurrection slot. Each bucket excludes IDs already selected; a bucket
reports the number it actually fills, and a pool smaller than ten returns every
eligible lesson without synthetic backfill.

The value statistic is `score_total / (score_count + 2)`, shrinking small samples
toward zero. The uncertainty statistic is that value plus
`sqrt(ln(max(total_score_count, 2)) / (score_count + 1))`; `total_score_count` is
the sum of every eligible lesson's `score_count`, and the coefficient is fixed at
one for this local preview. Recent ranking is latest-source date descending (a
missing date sorts last), then the index's stored `selection_weight` descending,
then recurrence-class slug ascending. Value and uncertainty ties also break by
slug. With no archive state in schema v2, the resurrection slot selects one more
uncertainty candidate and the audit counts name it as
`archive_fallback_uncertainty: 1` while `archive: 0`; archive behavior itself
remains deferred.

The output is `charness.lesson-selection-preview` schema version 1 with
`mode: "preview"`, a non-empty caller `seed`, `eligible_count`, audit-only bucket
counts (`recent`, `value`, `uncertainty`, `archive`, and
`archive_fallback_uncertainty`), and a flat `items` list of lesson ID, lesson
text, and latest source path. Item order is the ascending pair of
`sha256(seed + "\\0" + lesson_id)` and lesson ID. The output never includes a
per-item bucket, session, shown, archive, or score-event field, and the command
does not write any file.

This is not a shown-set record and does not authorize score events: no selected
session is persisted, no score event gains a session field, and no retro may claim
that this preview was presented to an agent. It gives a later presentation/retro
slice a reproducible candidate seam without inventing evidence it cannot observe.
UCB tuning, score budgets, archive writes, shown-set validation, and register or
graduation state remain out of scope.

## Fourth Implementation Slice

Add an independent `charness.contract-register` schema-v1 state file and
validator. Its active unit universe is deterministically rebuilt from every
unfenced ATX H2 heading in `AGENTS.md`,
`docs/conventions/implementation-discipline.md`, and
`docs/conventions/operating-contract.md`; a unit ID is the canonical
`path#heading-slug`, where heading text is Unicode-normalized, trimmed,
lower-cased, punctuation-separated, and rejected if empty or colliding within a
path. The materialized, lexically sorted `units` list must equal that rebuild.
This does not edit those surfaces or infer rule identity from prose: the authored
heading is the probe-level unit boundary.

The register has append-only `citation_events`, `catch_events`, and
`graduation_proposals`; their strict event shapes, non-empty IDs, repo-relative
paths, duplicate rules, and committed-prefix checks fail closed. A citation event
names an active unit, an existing repository-relative retro, and a non-empty
anchor; `(source_retro, unit_id)` and event IDs are unique. Catch events remain an
explicitly empty, strict field until a declared gate-to-unit mapping exists, so a
handwritten “catch” is not mistaken for mechanical attribution. The initial
register is enough to make the zero citation/zero catch state inspectable, not to
claim that citation is a proven signal.

The initial unit budget is seeded once to the active-unit count and then remains a
fixed capacity; re-baselining it is a new-schema, reviewed decision, not a rebuild
side effect. A graduation proposal is proposal-only: it names an existing seeded
lesson and cited recurrence-class source retro, an allowlisted target path and
heading whose canonical derived ID equals its non-colliding proposed unit ID,
rationale, and unique existing displacement unit IDs. The validator checks
`current_unit_count + 1 - displacement_count <= unit_budget`. It neither removes a
unit nor writes the proposed target. Thus a proposal that would grow the
always-loaded surface must name enough displacement candidates, while acceptance
remains an external contract-change process outside this goal. This schema is
validated only before a contract mutation; preservation of retired/renamed unit
history after a separately reviewed contract change is deliberately not claimed.
Accordingly, schema v1's checker is an explicit pre-mutation probe, not an
always-on `run-quality.sh` gate: wiring it there would make an approved future
contract mutation impossible before this contract defines an applied membership
transition.

## Fifth Implementation Slice

Add a local `record_lesson_score.py` authoring command. It accepts one seeded
`lesson_id`, one existing repository-relative session-retro path, integer score,
and optional non-empty anchor; it first validates the current ledger, then
appends exactly one event with a caller-supplied non-empty `event_id`, deterministically
replays the materialized lesson view, validates the candidate state, and writes
only the ledger JSON as durable ledger data (plus a stable OS-temporary lock
sidecar used solely for local writer coordination). The command never renders or records a selection,
presentation, shown set, archive, contract citation, or graduation. It is a
convenient atomic authoring path for the score-event contract already owned by
the ledger validator, not evidence that the cited retro actually presented a
lesson. Existing source recurrence-class, one-source-per-lesson, anchor, and
committed-prefix refusals remain the validator's single source of truth.
Candidate validation is pure and happens before any replace; every rejected
request leaves the ledger bytes unchanged. A repository-local exclusive lock
spans read, validation, replay, same-directory temporary write, and atomic
replace, so two concurrent local invocations cannot silently discard one
another's appended event. Whitespace-only identifiers and anchors are refused.

## Sixth Decision Slice: Graduation Boundary Completion

For this local goal, the graduation seam is complete at **proposal validation**:
a proposal proves seeded-lesson/source provenance, a canonical allowlisted
target identity, and fixed-capacity conservation through active displacement
IDs. It does not approve, apply, or record an H2 membership change. Existing
tests prove an over-capacity proposal without displacement is refused and a
proposal with a valid active displacement is accepted; the empty live state
remains inspectable as 26 active units with zero citations, catches, and
proposals.

Do not add a score threshold, citation/catch count, proposal reservation, target
heading creation, retirement, rename history, or an always-on register gate in
this goal. The evidence cohort is still zero and schema v1 deliberately has no
applied membership transition. A later, separately reviewed contract-change
workflow owns approval, its pre-mutation checker invocation, applied
add/remove/rename history, and any evidence-based eligibility policy.

## Seventh Implementation Slice: Declared Session Eligibility

Schema v3 adds the smallest durable **declared preview session** boundary. It is
not a delivery receipt: it proves only that the local recorder generated one
deterministic preview snapshot at record time and that a later cited score names
one lesson listed in that snapshot. It does not prove the list was displayed,
received, read, used, causally helpful, calibrated, or eligible for contract
graduation.

The schema-v3 top-level state retains transitions, score events, and materialized
lessons, then adds `legacy_score_event_count` and append-only `session_events`.
Migration from schema v2 copies every existing score event byte-for-byte into
the leading `legacy_score_event_count` prefix. Those legacy events keep their
schema-v2 shape and are never assigned synthetic sessions. Every score event
after that immutable prefix requires a non-empty `session_id`; a v3 event
without it is refused by replay, not merely by the authoring CLI. A committed
v3 ledger must retain its exact legacy count and score/session/transition
prefixes; migration from committed v1/v2 preserves the available historical
prefixes and fixes the new count at the former score-event length.

Each session event has a globally unique non-empty `session_id` and a frozen
preview snapshot: preview kind and schema version, explicit
`selection_policy_version`, non-empty seed, eligible count, audit bucket counts,
and an ordered, duplicate-free non-empty `lesson_ids` list of seeded IDs. The
event carries a named `snapshot_sha256`: SHA-256 over exactly that snapshot
object serialized as UTF-8 canonical JSON with recursively lexicographic key
order and `(',', ':')` separators, never over enclosing event formatting. Any
semantic selection-policy change must bump `selection_policy_version`. At record
time the command acquires the shared ledger
writer lock, validates current state, builds the current preview itself from the
given seed, copies its item IDs and audit fields into the snapshot, validates the
candidate ledger, and atomically replaces the JSON. It accepts neither caller
provided lesson IDs nor a separate preview file. Later replay checks event
shape, identity, seed, unique seeded IDs, and snapshot digest; it deliberately
does **not** re-render a historical seed against the current score/index state,
because accumulated scores can legitimately change that result.

The same path-derived cooperative lock protects both session and score writers
across read, preview/replay, candidate validation, temporary serialization, and
replace. The v3 score authoring command requires `--session-id`; replay resolves
it from `session_events` and refuses an unknown session or one whose frozen
lesson list excludes the score's `lesson_id`. Existing source-retro citation,
score range, anchor, duplicate event ID, and one-source-per-lesson rules remain
independent. Empty preview results refuse without a write.

Tests must pin a v2 ledger containing a real score through migration, reject a
new session-less v3 score, reject rewritten/deleted/reordered legacy score and
session prefixes, permit a newly appended session-linked score, and keep a
recorded session valid after its contained score changes the current preview.
Do not add timestamps, actor/device identity, presentation acknowledgement,
cryptographic receipts, score budgets, archive state, or a new quality gate: the
existing ledger checker owns this local eligibility predicate.

## Eighth Implementation Slice: Applied Lifecycle (#616)

Issue #616 opens the separately reviewed lifecycle slice that the sixth slice
deliberately deferred. It does not change the evidence policy: the current
positive-only score cohort still cannot justify a numeric archive, promotion,
or retirement threshold. This slice builds the reversible mechanics and keeps
every judgment explicit.

Ledger schema v4 preserves the complete v3 transition, session, score, and
legacy-prefix streams byte-for-byte. It adds a fixed `active_lesson_budget` of
50 and an append-only `lifecycle_events` stream. Each event has a contiguous
sequence, unique event ID, seeded lesson ID, action (`archive` or `resurrect`),
an existing repository-relative Markdown `decision_ref`, and a non-empty
rationale. Replay initializes every v3 lesson as active, then permits archive
only from active and resurrection only from archived. The derived lesson view
adds `state` and `last_lifecycle_event_id`; scores and source identity never
reset. More than 50 active lessons refuses. No score value creates an event.

Selection policy version 2 keeps recent, value, and uncertainty ranking over
active lessons only. Its tenth slot draws one archived lesson by the existing
deterministic uncertainty order. When no archived lesson exists, the archive
slot stays empty; it is no longer filled by an uncertainty item under a false
archive label. The preview JSON remains schema version 1, reports `archive: 1`
only when an archived item was actually selected, and reports
`archive_fallback_uncertainty: 0` for policy version 2. Historical frozen
policy-v1 session snapshots remain valid and are never rerendered.

`recent-lessons.md` and the lesson-selection index remain the independently
rebuilt source corpus. They do not gain score, lifecycle, archive, or graduation
state and are not rebuilt as a lifecycle-write side effect. The preview is the
sole score- and lifecycle-backed session projection.

Contract-register schema v2 migrates v1 by freezing its exact `units` as
`seed_units`, retaining its fixed `unit_budget`, and preserving citation, catch,
and proposal prefixes. It adds append-only `applied_transitions` and derives
current `units` plus `retired_units` solely by replaying those events from the
seed. The replayed active units must separately equal the live H2 inventory.
Changing docs without a transition, changing a transition without the matching
docs, directly editing a materialized projection, rewriting seed units, or
rewriting any committed event prefix all refuse.

A schema-v2 graduation proposal keeps the existing provenance and conservation
fields and adds at least two distinct `evidence_session_ids`. Every named
session must contain the lesson and have a score event for it; no score total,
mean, sign, or threshold is required. Quality may author this proposal, but it
remains inert until a reviewed apply event links it.

An applied graduation transition names one existing proposal, a durable
approval reference, rationale, and the proposal's exact displacement set. It
adds the proposed unit and retires the displacements atomically in replay. A
standalone retirement names active units, a durable approval reference,
rationale, successor unit IDs, and either those successors or the literal
`no-remaining-binding-behavior` disposition. Retirement history remains in
`retired_units` and in the append-only event after the unit leaves membership.
Every replay enforces the fixed budget.

Repo-owned operator commands append lesson lifecycle events, graduation
proposals, citations, and applied register transitions under the existing
cooperative lock and atomic-replace discipline. Candidate state validates
before replacement and every refusal leaves bytes unchanged. Applying a
contract transition never edits an operating document: the reviewed document
edit and event are prepared together, and validation proves their agreement.

A read-only retention report renders each active and retired unit's declared
citations, mapped catches when that mapping later exists, and membership
history. With the current empty catch mapping it says so explicitly and emits a
non-verdict; it never applies lesson scores, invents retirement eligibility, or
authorizes a transition.

Acceptance is focused replay/refusal and CLI roundtrip proof: v3/v1 migration,
score/history preservation across archive and resurrection, the active budget,
real archived selection, empty-archive no-backfill, multi-session proposal
eligibility, proposal-linked apply, displacement/retirement audit, live-doc
agreement, committed-prefix refusal, deterministic materialization, and
unchanged bytes on rejected operator commands. Threshold calibration, catch
mapping, retention-based retirement criteria, and a portable public schema stay
deferred.

## References

- [Harness-improvement thesis](./2026-08-11-harness-improvement-thesis.md) — the
  digest's slot-policy defect and two unimplemented proposals.
- [Recent lessons digest](../retro/recent-lessons.md) — the surface this replaces.
- [Implementation discipline](../../docs/conventions/implementation-discipline.md) — a
  contract doc this register would measure, including the section this slice added.
- [Operating contract](../../docs/conventions/operating-contract.md) — the other
  always-loaded contract surface.
- [Ownership gate critique](../critique/2026-08-12-handoff-bullet-ownership-critique.md)
  — four review rounds on the gate whose repair motivated the promotion problem.
