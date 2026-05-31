# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` → **invoke `charness:handoff`**. A bare
  `/handoff` fires chunked routing (#249); the chunker unions the **live
  open-issue backlog** with the list below, so `## Next Session` is a
  curation/sequencing memo, not the full queue. Then read
  [quality latest](../charness-artifacts/quality/latest.md) +
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **`main` PUSHED + synced** (origin/main == HEAD). Release line still
  **v0.13.0** (no new release this session).
- **#250 CLOSED this session** (`22597e8`): vendored `handoff` skill no longer
  cites author-repo-internal files with bare `<repo-root>/`/`docs/` notation
  that dangles downstream. Narrow handoff-package-only slice (a first
  flag-everything attempt that marker-spammed operator surfaces was reverted).
  Critique: [closeout artifact](../charness-artifacts/critique/2026-05-31-250-handoff-portability-closeout.md).
- **#264 FILED** (follow-up to #250): build the precise portability guard in the
  skill-portability lib (author-only doc/test cites, with operator-surface
  allowlist + marker escape hatch), sweep the same-class cross-skill cites, and
  add the rule sentence to the portable-authoring reference. The discriminator
  and allowlist are spelled out in the issue body.

## Next Session

> Chunk the live backlog rather than trusting this list verbatim.

1. **1순위 (planned, not started): mutation cluster as an `achieve` goal** —
   #262 (cosmic-ray module-path restore on exit/interrupt), then #261 (latent
   coordination-cues survivors), #219 (mutation regression on main).
2. **#264** — portability guard + cross-skill cite sweep (the deferred half of
   #250). Cheap, well-scoped; the discriminator/allowlist live in the issue body.
3. Other open: #259, #258, #252, #243, #241, #237, #236, #185, #184.

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there.
- This session hit the #258 echo-flood trap again (batched tool calls under
  delayed output → cascade cancels). Prefer serial tool calls when output
  latency is unstable.

## References

- [quality latest](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [#264](https://github.com/corca-ai/charness/issues/264) (follow-up scope + allowlist)
