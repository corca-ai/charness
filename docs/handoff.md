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

- **`main` == `origin/main`; `v0.12.0` released + verified**
  ([release latest](../charness-artifacts/release/latest.md),
  [tag](https://github.com/corca-ai/charness/releases/tag/v0.12.0)).
  **Handoff chunker v2** shipped; **#249 and #248 CLOSED**.
- **Chunker v2:** unions the live open-issue backlog at pickup (deduping issues
  a handoff entry cites), fires on a bare skill invocation, stage scripts
  compose with loud failure. **Issue source ships ON by default** (opt-out via
  `issue_source: {enabled: false}`; degrades to doc-only) — documented in the
  0.12.0 update instructions.
- **End-only handoff timing codified** ([operating-contract Session
  Discipline](./conventions/operating-contract.md) + chunked-routing.md): the
  baton is written at closeout only.
- **SessionStart hook live-confirmed on Claude** this session; Codex not
  directly exercised. v0.12.0 **real-host proof still pending** (clean-machine).

## Next Session

> A bare `/handoff` unions the tracker — so chunk the live backlog rather than
> trusting this list. This memo carries only cross-issue judgment.

1. **Capability (closeout retro): make `check_python_lengths` a pre-commit
   gate** (warn ~330 / fail 360 for `skills/public/*/scripts/*.py`). The
   silent-lib-growth trap recurred twice this session — the recurrence is the
   trigger.
2. **usage-episodes / hooks cluster:** #244 (auto-wire find-skills SessionStart
   hook — now more relevant; the 0.12.0 update note still tells operators to
   wire it manually), #245 (cross-checkout hook dup), #243 (consumer/report
   gap). #244+#245 both touch the host-hook installer.
3. **v0.12.0 real-host proof** (Cautilus clean-machine smoke) + remaining
   backlog: #242/#219 (mutation), #233, #241, #237/#236, #184/#185.

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there. Full session waste / decisions:
  [closeout retro](../charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md).

## References

- [quality posture](../charness-artifacts/quality/latest.md),
  [chunker contract](./handoff-chunked-routing.md),
  [release latest](../charness-artifacts/release/latest.md)
