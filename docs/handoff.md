# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` → **invoke `charness:handoff`**. A bare
  `/handoff` now fires chunked routing too (#249), and the chunker unions the
  **live open-issue backlog** with the entries below — so this list is a
  curation/sequencing memo, not the full queue. Then read
  [quality latest](../charness-artifacts/quality/latest.md) +
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **`main` ahead of `origin/main` by 9 — UNPUSHED.** This session built
  **handoff chunker v2** via the now-complete goal
  [2026-05-29-249-248-handoff-chunker-v2](../charness-artifacts/goals/2026-05-29-249-248-handoff-chunker-v2.md).
  Nothing pushed; #249/#248 still **OPEN** on GitHub.
- **#249 + #248 resolved in code.** Chunker unions the live backlog (deduping
  issues a handoff entry already cites), fires on a bare skill invocation, and
  its stage scripts compose with loud failure. Gate: 1793 passed / 0 failed.
- **End-only handoff timing codified** ([operating-contract Session
  Discipline](./conventions/operating-contract.md) + chunked-routing.md): the
  baton is written at closeout only. This handoff is the first under that rule.
- **SessionStart hook (old chunk-1) live-confirmed on Claude** this session;
  Codex not directly exercised (low-risk). v0.11.0 real-host proof still pending.

## Next Session

> A bare `/handoff` unions the tracker, so this memo carries only the
> cross-issue judgment the tracker can't express. Steps are ordered: decide the
> default BEFORE shipping (hard to walk back).

1. **Decide the issue-source default first.** Built **opt-out** (`--with-issues`
   shells out to `gh`, adapter-gated, graceful doc-only fallback) but exercised
   only against `gh`; non-gh backends are stub-tested. Confirm default-on vs
   default-off+opt-in — this gates step 2 (wrong default is painful to reverse).
2. **Then push + close #249/#248 + release.** All outward-facing — **await the
   operator's go-ahead before pushing.** On go-ahead: push, run `issue` closeout
   to close #249/#248, then bump via `release` (chunker feature ⇒ minor).
3. **Capability (closeout retro): make `check_python_lengths` a pre-commit gate**
   (warn ~330 / fail 360 for `skills/public/*/scripts/*.py`). The
   silent-lib-growth trap has recurred twice — the recurrence is the trigger.

## Discuss

- **Default-on is a behavior change for every consumer on update** (each
  `--with-issues` pickup calls the provider). Gated + doc-only fallback, but
  only the `gh` path is proven live. Resolve before release. Full waste /
  decisions / follow-ups: [closeout retro](../charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md).

## References

- [quality posture](../charness-artifacts/quality/latest.md),
  [chunker contract](./handoff-chunked-routing.md),
  [goal artifact](../charness-artifacts/goals/2026-05-29-249-248-handoff-chunker-v2.md)
