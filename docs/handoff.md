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

- **v0.24.0 is shipped and verified.** Tag `v0.24.0`, GitHub release live, all
  version surfaces at 0.24.0, `main` in sync with `origin`. Release:
  <https://github.com/corca-ai/charness/releases/tag/v0.24.0>.
- **#318 and #319 are CLOSED** (verified). Shipped via the `2026-06-06-318-319`
  achieve goal (complete) as two committed slices, then a minor release:
  - #319 — commit-boundary SKILL.md `core_nonempty` ≥4 headroom **ratchet**
    (changed-file-scoped; mechanism chosen via `quality`).
  - #318 — opt-in orchestrator/sub-goal closeout-proof **delegation** gate for
    `achieve` (standalone default unchanged).
  - Each slice fresh-eye reviewed CLEAR; standalone + release critiques CLEAR;
    local `--release` gate green is the bundle proof.

## Next Session

1. **Pending operator real-host proof** (the only release follow-up): the v0.24.0
   publish reported `real_host_required: true` — run the standing `nose`
   checklist on a second machine / clean temp-home (`charness update` +
   `charness tool doctor/install nose`). This was also pending for v0.23.0; do it
   once for the current published surface.
2. Open backlog (route through `find-skills` then `issue`/`ideation`): **#184** —
   제품 성공 기준과 핵심 메트릭 정의 (the only remaining open issue).
3. Do not reopen #318/#319 or the 318-319 goal unless current verification
   contradicts the shipped evidence.

## Discuss

- **No push/tag-triggered CI.** charness runs CI only on
  `workflow_dispatch`/path-scoped `pull_request`/cron, so the v0.24.0 SHA got
  **no** automatic CI on push; the local `--release` gate is the bundle proof.
  Worth deciding whether to add light push/tag CI.
- **Two deferred, no-action items from the 318-319 run** (transparency, not
  follow-ups): the recent-lessons "Current Focus" digest generator picks a
  wrapped fragment; the #318 `negated-verified` resolution guard errs-safe
  (over-blocks, never bypasses). Both documented in the closeout critiques.

## References

- [318-319 goal](../charness-artifacts/goals/2026-06-06-318-319-achieve-closeout-and-quality-headroom.md),
  [closeout retro](../charness-artifacts/retro/2026-06-06-318-319-closeout.md),
  [v0.24.0 release auto-retro](../charness-artifacts/retro/2026-06-06-v0-24-0-release-auto-retro.md)
- [#319 critique](../charness-artifacts/critique/2026-06-06-319-commit-boundary-headroom.md),
  [#318 critique](../charness-artifacts/critique/2026-06-06-318-orchestrated-closeout-delegation.md),
  [v0.24.0 release critique](../charness-artifacts/critique/2026-06-06-v0.24.0-release-critique.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
