# Lesson Graduation (Shared)

Promotion step for a lesson that has proven itself. `retro` cites this reference
so a lesson leaves the ledger's working set the same way every time, instead of
each session inventing its own promotion. The step is prompt-driven and settled
by a person; the ledger only records a decision that was already made.

## What Graduation Is

A lesson graduates when a standing `docs/` page takes ownership of the rule it
carries. The lesson stops being working memory that has to be re-selected and
re-read, and becomes part of the contract the repo reads anyway. It stays
readable in the ledger with its score history, but it leaves the active lesson
budget, is no longer eligible for selection, and is not an archive-slot
candidate.

Graduation is a **proposal settled by a person and the agent together, lesson by
lesson**. No rule, score threshold, classifier, or commit inspection decides it
— this repo's own `graduation-is-proposal` lesson says so. The agent proposes
with evidence, the person settles, and the reason is written before the event is
applied. A retro may *propose* graduation; it never performs it in passing.

## When This Applies

Repo-gated, not consumer-facing: only where a lesson ledger with the graduate
lifecycle move already exists. Anywhere else this reference is a silent no-op —
do not create a ledger in order to graduate into it.

## The Three Questions, In Order

### 1. Owner and duplicates

Exactly one `docs/` page owns the rule. Every other page that restates it loses
the restatement and links to the owner instead; a cheat-sheet line may survive
only as one line plus that link.

Search before writing: `grep -rn` the command, the flag, or a distinctive phrase
across the docs tree, the README, the skill references, and the agent
instruction file. Done looks like one page carrying the sentence, with every
other hit either removed or turned into a link.

### 2. Mechanism

Ask whether a gate, a runner preamble, a refusal, or a form check can make the
rule impossible to forget.

- **Yes** — the mechanism ships in the graduation commit, and the docs sentence
  names it. The reader learns what enforces the rule instead of being asked to
  remember it.
- **No** — the docs sentence says what would have to exist and why it does not
  yet. A stated gap is a legitimate outcome; a silent one is not. A docs-only
  graduation is allowed only when the owning page is one a person reads at the
  moment the class comes up (the testing paragraph when writing a test, the
  brief rules when writing a brief). The ledger's selection preview is read at
  every session start and a docs page only on demand, so graduating a lesson
  into a page nobody opens at the decision moment lowers its exposure; keep
  that lesson active instead.

Examples from this repo's first graduations, as illustrations and not as rules:
a stale generated mirror became a preamble in the standing test runner; raw
module-cache eviction in tests became a form check; wall-clock sleeps in tests
became a form check whose exemption record starts empty because every existing
violation was folded first.

### 3. The event

Only after 1 and 2 have landed:

```bash
python3 <repo-root>/scripts/lessons/record_lesson_lifecycle.py \
  --event-id <id> --lesson-id <lesson-id> --action graduate \
  --decision-ref docs/<owning-page>.md --rationale "<settled reason>"
```

`--decision-ref` must name the owning `docs/` page; the ledger validator refuses
a graduate event that points anywhere else. `--rationale` carries the settled
reason in the disposition vocabulary — the lesson **helped**, **contradicted**,
**did not help**, or was **never consulted** — together with the evidence behind
that call.

Record the event in the **same commit** as the docs and mechanism edits, so the
event's reference is true at the commit it lands in.

## Archive vs Graduate vs Keep

| Move | When |
| --- | --- |
| archive | the lesson's premise no longer holds, or it named a one-off that cannot recur |
| keep | it is still changing actions, and no owner page or mechanism is ready yet |
| graduate | both halves exist: a `docs/` owner, and a mechanism or a stated reason there is none |

## Verification

- `check_lesson_ledger.py` passes.
- The lesson selection preview no longer shows the lesson in the working set.
- The repo's docs gate (`check-docs.sh`) is green at the commit.
