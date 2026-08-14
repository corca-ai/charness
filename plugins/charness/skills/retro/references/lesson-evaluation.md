# Lesson Evaluation

This boundary applies only when opened repo-owned evidence explicitly defines a
declared-session lesson evaluator. An arbitrary `evidence_paths` string does not
imply one, and repos whose evidence declares no evaluator have no lesson-scoring
duty.

Append sparse scores only for lessons selected and actually presented by a
contemporaneous agent-authored session-start action before the affected work.
When the evaluator persists a session bundle, recover the explicit session ID
and bundle path from the affected work's durable artifact, then load the frozen
bundle before judging effects. Do not substitute a newest-file guess, mutable
lesson source, or host transcript search. A valid bundle proves the issued
content, not human readback, lesson use, or positive effect; retro-time
inspection alone does not justify a score.

When the repo-owned evaluator defines a disposition grammar:

- use its exact status, reason, identity, and score-count form;
- treat an affirmative no-effect judgment as distinct from merely having zero
  score events;
- record absent or uncertain presentation honestly without appending a score;
- run its declared read-only reconciler after the retro is persisted; and
- keep the reconciler's denominator label explicit rather than implying it
  covers host sessions the repo cannot observe.

The adapter may expose the repo-owned authoring form through
`artifact_sections` and its reconciler through `metrics_commands`. Those fields
route an evaluator contract; they do not create one. Exact grammar, commands,
and proof limits stay in the repo-owned evidence named by the adapter. An
`artifact_sections` entry must not re-declare a heading the scaffold already
emits: the scaffold owns those, and a duplicate heading fails the same validator
the section exists to satisfy.

## Where presentation comes from

The hook EMITS; the agent DECLARES; nothing automatic writes to the ledger.

At session start, the charness SessionStart routing hook checks one thing — does
`<repo-root>/charness-artifacts/retro/lesson-ledger.json` exist under the
session's repo? If
it does not, the hook injects nothing and this whole boundary stays inert. If it
does, the hook renders the same deterministic selection preview a declared session
would freeze and injects those bytes verbatim, followed by the exact
`open_lesson_session.py` command (session id and seed are one value, so the list
is reproducible and citable). When the preview cannot be produced at all — a stale
selection index, a timeout, an unreadable ledger — the hook says `state:
not-established` out loud rather than going quiet, because a silently missing
lesson list is indistinguishable from a repo that owes nothing.

Declaring the session is a deliberate act taken before the affected work, by the
agent, using the id the hook printed. No hook may append to the ledger:

- an automatic per-session declaration emits one receipt per session, and every
  session that does not end in a retro then becomes a permanent
  `unclaimed-emission` violation;
- it is not idempotent, and resume/clear re-fires are normal;
- it has no rollback — the ledger append happens before the bundle, the stdout,
  and the receipt; and
- it would mutate a committed append-only file with no operator present.

Emission is not presentation. A receipt, a ledger session, and the hook's own
injection each prove that bytes were ISSUED. None of them proves an agent read
them, and none may be reported as though it did — that is exactly what
`not-evaluated / presentation-unproven` is for, and it stays reachable and
correct.

At retro time the run plan carries a `lesson_session` block naming which
receipted session, if any, is still unclaimed, with its frozen lesson ids, its
bundle path, and a filled-in score command. Append scores first, write the
disposition second, run the reconciler after persistence.

## Being asked, not just routed

When the repo-owned evaluator defines one, that block also carries a
`solicitation`: the questions the evaluator wants answered about the emitted
list, alongside each lesson's emitted wording rather than its id alone. Routing
an author to a session says where to record a judgment; it does not obtain one.
A lesson that failed to change anything produces no signal unless something
asks, and with no signal there is nothing later to judge its form against.

Reading a lesson's wording at retro time is not presentation, and an evaluator
that renders wording here must not be read as licensing a score for it. The
scoring precondition is unchanged: a list emitted before the affected work.

Answer the evaluator's harmful or negative question first and explicitly. A
reader walking a list volunteers what helped long before what hurt, and the
unhelpful cases are the ones that can change a lesson's form. Answering is still
not the same as scoring everything: an unobserved lesson stays unscored, and a
high score count is not a health measure.

Claim only what the evaluator implements. Where scoring feeds a ranking, a score
changes the weight at which a lesson is drawn; it does not rewrite the lesson.
Unless the repo declares a mechanism that revises wording from scores, do not
tell an author that scoring will.

## Declaring an evaluator, or not

Declaring one is an explicit repo-level opt-in, because it turns on a per-retro
disposition duty. Absent a declaration there is no duty and the disposition floor
is inert — that is a configuration state, not a per-session finding, and the
validator says which of the two it is on every run rather than leaving an author
to guess.

When the repo-owned evaluator is the declared-session ledger, the declaration is
the ledger file itself and `init_lesson_ledger.py` creates it — resolved
repo-locally under `scripts/` when the repo has one, otherwise from the installed
package, and printed as a runnable command by the retro artifact validator
whenever the floor is inert. That is the whole opt-in; it is not the whole
lifecycle. An empty ledger
makes sessions *reachable*, not *possible*: a lesson enters it only from a retro
bullet tagged `recurrence-class: <slug>`, so until at least one lesson is seeded,
session declaration still refuses and `not-evaluated / missing-start` remains the
only honest disposition. Say that plainly rather than reporting the opt-in as the
lifecycle being live.

Never backfill scores from a later retro. The disposition belongs in the retro,
not in a ledger field unless the repo-owned evaluator contract explicitly owns
such state.
