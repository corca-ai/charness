# Autonomous Trigger

Use this when `critique` is invoked with no pending-change artifact, diff
summary, PR, spec, or release note. The goal is to find one honest review
target without pushing source summarization back to the caller.

## Scan Order

1. Read `docs/handoff.md` for the named next move, current blockers, and open
   decisions.
2. Inspect `git status --short` and the staged or unstaged diff summary.
3. Inspect commits ahead of `origin/main` when that ref exists with
   `git log --oneline origin/main..HEAD`; otherwise continue from local
   status and diff evidence.
4. Look for the nearest current contract in `charness-artifacts/spec/`,
   `docs/roadmap.md`, and docs sections named Next Session, Open Decisions,
   Deferred, Non-Goals, Acceptance, or Risk.
5. Prefer a live issue, handoff item, dirty diff, or ahead-of-origin commit
   over broad repo archaeology.

## Proceed Versus Ask

Proceed autonomously when one target clearly dominates with low inference risk
and the chosen target reference is stable from the evidence. State the inferred
target and cite the file or command that made it dominant.

Ask one concise clarifying question when:

- two plausible targets require different target references;
- the next move would create external side effects, deletion, release, or
  policy lock-in;
- the evidence points to a high-stakes decision whose success or out-of-scope
  boundary is not inferable.

Do not ask the user to provide a change artifact merely because none was
supplied. If the scan finds no live target, say that the autonomous trigger
found no pending change and ask for the missing target in one question.
