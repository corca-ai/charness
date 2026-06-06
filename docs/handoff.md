# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **6 commits are local-only (unpushed); nothing is pushed this session.** The
  maintainer's push is the next external step (see Next Session).
- **#318 + #319 resolved as two committed slices via the
  `2026-06-06-318-319` achieve goal (complete).** Both issues are still **OPEN**
  on GitHub — they auto-close on the maintainer's push of their `Close #N`
  carriers (CLOSED state is an explicit non-claim):
  - `b92dd9f9` `Close #319`: commit-boundary SKILL.md `core_nonempty` ≥4
    headroom **ratchet** (changed-file-scoped; mechanism chosen via `quality`).
  - `9bc40f2a` `Close #318`: opt-in orchestrator/sub-goal closeout-proof
    **delegation** gate for `achieve` (standalone default unchanged).
  - `479345a4` / `c427e327`: goal closeout (retro + disposition review) and a
    dead-export cleanup. Each slice fresh-eye reviewed CLEAR; the local quality
    gate ran 72/0 as the bundle proof.
- **v0.23.0 is the shipped release** (tag `v0.23.0`, unchanged this session).
  Release: <https://github.com/corca-ai/charness/releases/tag/v0.23.0>.

## Next Session

1. **Push the 6 local commits** -> auto-closes #318/#319 via the `Close #N`
   carriers; then `issue_tool.py verify-closeout --expect-state CLOSED` to
   confirm GitHub state. Do not close out-of-band.
2. Open backlog (route through `find-skills` then `issue`/`ideation`):
   **#184** — 제품 성공 기준과 핵심 메트릭 정의 (the only remaining open issue
   after #318/#319 close).
3. Do not reopen #318/#319 or the 318-319 goal unless current verification
   contradicts the shipped evidence.

## Discuss

- **No push/tag-triggered CI.** charness runs CI only on
  `workflow_dispatch`/path-scoped `pull_request`/cron, so a direct-to-`main`
  push gets **no** automatic CI on the released SHA; the local `--release` gate
  is the bundle proof. Worth deciding whether to add light push/tag CI.
- **Pending operator real-host proof** for v0.23.0 (the standing `nose`
  checklist: a second-machine `charness update` + `tool doctor/install nose`).
- **Two deferred, no-action items from the 318-319 run** (transparency, not
  follow-ups): the recent-lessons "Current Focus" digest generator picks a
  wrapped fragment; the #318 `negated-verified` resolution guard errs-safe
  (over-blocks, never bypasses). Both documented in the closeout critiques.

## References

- [318-319 goal](../charness-artifacts/goals/2026-06-06-318-319-achieve-closeout-and-quality-headroom.md),
  [closeout retro](../charness-artifacts/retro/2026-06-06-318-319-closeout.md)
- [#319 critique](../charness-artifacts/critique/2026-06-06-319-commit-boundary-headroom.md),
  [#318 critique](../charness-artifacts/critique/2026-06-06-318-orchestrated-closeout-delegation.md),
  [disposition review](../charness-artifacts/critique/2026-06-06-318-319-disposition-review.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
