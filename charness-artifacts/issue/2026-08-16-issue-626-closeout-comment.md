Closeout body for this issue, added as a comment.

**Why a comment and not a reopen.** This issue was closed ACCIDENTALLY. A commit message
in an earlier push carried the prose "S7 closes" immediately before this issue's number,
describing a future release rather than instructing one, and GitHub read the keyword as a
directive. The resulting state is nonetheless the intended one — the work below did land
— so the repo owner ruled not to reopen. What was missing was this body, and that is what
this comment supplies.

**What shipped.** The title scope is delivered and shown by execution rather than by
reading the implementation: the lifecycle review emits runnable commands,
`record_lesson_lifecycle.py --action archive` writes `state: archived`, and the
selection preview's archive bucket then fills. The resurrection slot this issue reports
as never fillable is fillable.

**What is NOT closed.** This issue's post-graduation-compaction section is open.
`apply_contract_transition.py` writes no lifecycle event, so a graduated lesson stays
`active` against the budget. That remainder was first recorded as F25 of this release's
own execution critique. It was NOT recorded in
`charness-artifacts/critique/2026-08-14-issue-618-628-closeout.md`'s cohort-B failure
angle — that angle records this issue's resurrection slot, which this
slice delivered — and an earlier draft of the release closeout mis-attributed it there.

**Guard against the recurrence.** The accidental close is now floored:
`scripts/prepush_close_keyword_guard.py` runs first in the pre-push hook, reads the
stored message of the commits in a push range — capped, and the cap reported, when a ref
creation cannot be bounded — and refuses when one close-keywords an issue without a
closeout carrier. It was calibrated against this repo's own recent `main`
history, where the only commit it refuses is the one that closed this issue — a
population that had, as the guard's own docstring records, already passed the commit-msg
floor, so it establishes no false-refusal rate.

Behavior #626: the archive disposition was executed and the preview's bucket observed
filling, which is also what caught that this issue's earlier close comment was stale in
the conservative direction.

Critique #626: charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md

AI-provenance: agent-drafted by Claude (Opus 5) operating the charness `issue` skill;
every verdict above was produced by executing the named command in this worktree or is
cited to the review that produced it.
