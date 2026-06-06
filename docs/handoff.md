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

- **v0.24.1 is shipped and verified.** Tag `v0.24.1`, GitHub release live, all
  version surfaces at 0.24.1, `main` in sync with `origin`. Release:
  <https://github.com/corca-ai/charness/releases/tag/v0.24.1>.
- **#320 is CLOSED** (verified). Patch release: covered the
  `staged_commit_gate_plan.py:72-73` `except SurfaceError: return []` degrade
  branch (mutation changed-line blocker) with a targeted-mutant proof. Bounded
  fresh-eye debug + release critiques CLEAR. The recurring changed-line class was
  escalated to a spec (see Next Session #3).
- Prior shipped state: **v0.24.0 / #318 / #319** (achieve goal complete). Do not
  reopen unless current verification contradicts the shipped evidence.

## Next Session

1. **Planned focus: full repo quality scan + improvements** via `find-skills` ->
   `quality` (`nose` clone advisory). Fold in #2 while there.
2. **Closeout-discipline gap (diagnosed 2026-06-06, #320 slice)** — a real
   prompt/validator slice; run `critique` + read recent-lessons first, do NOT
   rush. Two prompt-only debug-closeout steps silently slipped (the one that
   auto-fired, `validate-debug-seam-index`, was the gated one):
   - RCA-ledger append is prompt-only + deliberately non-gated
     ([rca-conversion-ledger spec](../charness-artifacts/spec/rca-conversion-ledger.md),
     anti-gaming). Consider an **advisory** nudge (warn when a slice adds a debug
     artifact but no RCA event refs it); no forced gate.
   - Cross-file sibling scan is required by the sibling-search reference (axis 1)
     but unenforced — a within-file `## Sibling Search` still passes
     `validate_debug_artifact` (shape-only).
3. **#320 follow-ups:** the
   [pre-merge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
   (folds in #251/#260; sibling population recorded there) and
   `follow-up:mutation-selection-budget-setup-libs`.
4. **Real-host proof** (carry-forward; not re-triggered by v0.24.1): standing
   `nose` checklist on a second machine / clean temp-home, pending since v0.23.0.
5. Backlog: **#184** — 제품 성공 기준과 핵심 메트릭 정의 (only other open issue).

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

- [#320 debug](../charness-artifacts/debug/2026-06-06-issue-320-mutation-changed-line-coverage.md),
  [pre-merge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md),
  [v0.24.1 release critique](../charness-artifacts/critique/2026-06-06-v0.24.1-release-critique.md),
  [v0.24.1 release auto-retro](../charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md)
- [318-319 goal](../charness-artifacts/goals/2026-06-06-318-319-achieve-closeout-and-quality-headroom.md),
  [v0.24.0 release critique](../charness-artifacts/critique/2026-06-06-v0.24.0-release-critique.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
