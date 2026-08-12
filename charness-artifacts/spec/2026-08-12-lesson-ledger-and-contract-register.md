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
4. Graduation cannot increase the always-loaded contract surface without naming
   what it displaces.
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
