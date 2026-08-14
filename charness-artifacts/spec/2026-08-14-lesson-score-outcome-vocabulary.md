# Spec — Lesson Score Outcome Vocabulary
Date: 2026-08-14

## Problem

The lesson ledger collects a signed scalar (`-3..3` plus an optional anchor) and
the lifecycle review consumes it to propose one of three dispositions --
`graduate`, `rewrite-in-place`, `strengthen-binding`
(`render_lesson_lifecycle_review.py:67-82`). The scalar cannot carry what those
dispositions need, and three defects were measured on
2026-08-14 in the first session that actually answered the scoring solicitation
(`ed27af68f`).

1. **One number, two meanings.** The solicitation's `harmful` arm asks which
   lessons pushed toward a WRONG action; its `read_and_failed` arm asks which were
   read and did not transfer. Both produce a negative. The first says the lesson is
   defective; the second says the lesson may be perfect and never landed. Those are
   different repairs.
2. **A positive cannot be cited at all.** `lesson_ledger_lib.py:375` requires a
   score's `source_retro` to be one of that lesson's own sources, and sources are
   rebuilt live from retro recurrence tags. A negative cites an observation of the
   class recurring. A positive is an observation of the class NOT recurring, so
   there is nothing to tag — crediting a lesson that worked would mean declaring it
   recurred. Three lessons that measurably changed an action in that session went
   unrecorded for this reason.
3. **The review sorts sign-blind.** `render_lesson_lifecycle_review.py:187` keys on
   `(-anchored_score_count, -score_count, lesson_id)`, so a lesson with three `+3`
   anchors outranks one with a single `-3` anchor.

Root cause of (2), and the reason this is a design fix rather than a bug fix:
`lesson_ledger_lib.py` uses the SAME citation rule for two different acts. Line 174
governs seeding a transition, line 375 governs scoring an encounter. Seeding needs
evidence that the class exists — a recurrence tag is exactly right. Scoring needs
evidence that an encounter happened — the anchor is exactly right. One rule serves
the first and structurally excludes half the second.

The ledger held zero negative scores until 2026-08-14 not because nothing had
failed, but because the signal had no path in.

## Decision

Replace the signed scalar with a **typed outcome**, four values, no magnitude.

| outcome | the question the author answers | feeds |
| --- | --- | --- |
| `changed-an-action` | did it change a specific action you took? | a lesson that is working; evidence toward `graduate` |
| `read-but-not-applied` | was it in view AT the decision and still did not land? | `rewrite-in-place` |
| `not-consulted` | did you never revisit it at the moment the class came up? | `strengthen-binding` |
| `pushed-a-wrong-action` | did it move the work toward something wrong, or cost a read that returned nothing? | `rewrite-in-place`, or retirement |

Every one of the four is a **fact about the author's own behaviour**, not a
judgement about the lesson's wording. That is the whole reason the split works.
An earlier draft used three outcomes and left `rewrite-in-place` versus
`strengthen-binding` to the anchor prose, on the argument that an author asked to
pre-classify a disposition will guess. That argument was right about the wrong
axis: whether better wording would have caught you is a counterfactual and
unknowable from the inside, but whether the lesson was in front of you when you
decided is a fact you remember. Splitting on the observation yields the
disposition for free.

Magnitude is dropped rather than reinterpreted. It was doing two jobs badly --
"how strong was the effect" and "how confident am I" -- and neither is needed:
strength is carried by the anchor, and aggregation is a COUNT of encounters per
outcome, which the ledger computes rather than an author guessing.

Dropping it also raises the floor. The current `anchor_rule` requires an anchor
only at magnitude 2 or more; with no magnitude, **every outcome requires an
anchor**. One fewer rule, one more obligation.

## Three deliberate asymmetries

These are the load-bearing part of this spec. The symmetric design is the obvious
one and it is wrong in three specific ways.

**A commit hash is permitted evidence, never required evidence.** An anchor may
cite a commit, a `path:line`, or a command, and a hash makes the anchor stronger.
Requiring one would delete the class of failure this vocabulary exists to capture:
the 2026-08-14 negative on `premise-not-checked-against-source` rests on three
anchors, two of which are reading failures that touched no file -- naming an issue
as a release blocker without reading the code that had already fixed it, and
citing a superseded spec line as live policy. A lesson usually fails at a
judgement, not at an edit. A hash requirement collects only the failures that
edited something.

**`changed-an-action` carries a stricter anchor bar than the other three.** Its
anchor must name both the action taken AND where the work would have gone
otherwise. The others need only the observation. The reason is incentive, not
symmetry: an agent scoring its own session finds `changed-an-action` the easiest
and most flattering claim available, and the same session that produced this spec
had four self-assessments proven false by readers. Making positives recordable
removes a structural bias that was suppressing them and installs a self-serving
one in its place; the asymmetric bar is what pays for that.

**`not-consulted` is recordable only when the session actually committed the class
the lesson names.** Without that guard it is the default: every lesson the session
had no occasion to use is trivially "not consulted", and a ten-lesson presentation
would emit ten `strengthen-binding` signals per session for lessons that were
merely irrelevant. A lesson that never came up is not an encounter and gets no
record at all. This is the one outcome needing a precondition, because it is the
one whose literal reading is almost always true.

## Migration

- Score events are a closed key set with `score` validated as an integer in
  `-3..3` (`lesson_ledger_lib.py:351,362`). Adding `outcome` and removing `score`
  is a schema-version bump, not an additive change.
- The ledger is append-only and its committed prefix is compared against
  `git show HEAD:<path>`, so the migration must preserve prior bytes or move
  through the same reviewed path `record_lesson_lifecycle` migrations use.
- The 8 existing score events are all positive and were authored under the old
  semantics. Mark them `legacy-scalar` and do NOT translate them into the new
  vocabulary: they were recorded when `changed-an-action` was not expressible, so
  reinterpreting them would manufacture evidence that was never given.
- `render_lesson_lifecycle_review.py` groups by outcome instead of sorting by
  count, which retires the sign-blind ordering rather than patching it.

## Success criteria

- A lesson that worked can be recorded without declaring that it recurred.
- `read-but-not-applied`, `not-consulted`, and `pushed-a-wrong-action` are
  distinguishable in the ledger without reading prose, and each routes to one
  disposition without a human re-deriving which.
- The lifecycle review answers "which lessons have a `read-but-not-applied`
  encounter" as a grouping, with no ordering heuristic.
- An anchor is required for every outcome, and `changed-an-action` anchors name a
  counterfactual.

## What would falsify this

If `read-but-not-applied` and `not-consulted` are never used differently in
practice — if authors pick one by habit rather than by recalling whether the lesson
was in view — then the split bought nothing and the honest move is to collapse them
and route by anchor prose after all. Equally, if `not-consulted` dominates every
session despite its precondition, the precondition is not being applied and the
outcome is acting as a default. The count per outcome after ten sessions is the
measurement for both.

## Non-claims

Nothing here is implemented. No schema bump, migration, or renderer change has
been made. The three defects are measured; the vocabulary is decided. The three
asymmetries are the parts most likely to be discarded by an implementer who reads
only the table, which is why they have their own section: without them the design
collects only failures that edited a file, fills with flattering self-reports, and
emits a `strengthen-binding` signal for every lesson a session had no occasion to
use.
