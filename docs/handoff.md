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

- **Quality-scan + closeout-discipline achieve goal complete (2026-06-06,
  unreleased).** 6 commits on `main` ahead of `origin` (`324da4e7`..closeout):
  refreshed `quality/latest.md` to v0.24.1 (71/0; `nose` now active locally);
  **#2b** cross-file sibling marker enforced in `validate_debug_artifact.py`
  (`latest.md` branch); **#2a** advisory RCA-ledger nudge (`rca_link_advisory.py`,
  wired into predict-commit, exit-0); advisory-interpretation contract first cut
  (`nose` pilot) with rollout split to **#322**. Full `run-quality.sh` 72/0.
  Three bounded fresh-eye reviews (one REVISE→folded). **Not pushed, not
  released** (a release is a separate later goal). Goal:
  [quality-scan goal](../charness-artifacts/goals/2026-06-06-quality-scan-closeout-discipline.md).
- **v0.24.1 is shipped and verified.** Tag `v0.24.1`, GitHub release live, all
  version surfaces at 0.24.1. Release:
  <https://github.com/corca-ai/charness/releases/tag/v0.24.1>.
- **#320 is CLOSED** (verified). Patch release: covered the
  `staged_commit_gate_plan.py:72-73` `except SurfaceError: return []` degrade
  branch (mutation changed-line blocker) with a targeted-mutant proof. The
  recurring changed-line class was escalated to a spec (see Next Session #3).

## Next Session

1. **Release decision (6 unpushed commits on `main`).** The quality-scan goal
   landed #2b/#2a/slice-5 unreleased. Decide whether to bundle these into the
   next release (with `release` + the local `--release` gate) or keep building.
   Items 1–2 from the prior handoff (full quality scan; closeout-discipline gap)
   are **DONE** in those commits.
2. **#321 (newly open) — "Mutation test regression on main"** (opened
   2026-06-06). Not yet investigated; route via `issue` resolve (bug-class →
   causal review first). Out of scope for the completed quality-scan goal.
3. **#322 (newly filed) — advisory-interpretation contract rollout.** Extend the
   slice-5 pilot to the remaining inference-layer surfaces (ergonomics, test
   economics, lint pressure, length smell, recommendation rankings, runtime
   trend); promote to a `spec` if it grows.
4. **#320 follow-ups:** the
   [pre-merge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
   (folds in #251/#260) and `follow-up:mutation-selection-budget-setup-libs`.
5. **Real-host proof** (carry-forward; pending since v0.23.0): standing `nose`
   checklist on a second machine / clean temp-home. (`nose` is now present on
   THIS machine — the carry-forward is specifically the clean second-machine run.)
6. Backlog: **#184** — 제품 성공 기준과 핵심 메트릭 정의.

## Discuss

- **No push/tag-triggered CI.** charness runs CI only on
  `workflow_dispatch`/path-scoped `pull_request`/cron; the local `--release` gate
  is the bundle proof. Worth deciding whether to add light push/tag CI.

## References

- [quality-scan goal](../charness-artifacts/goals/2026-06-06-quality-scan-closeout-discipline.md),
  [quality-scan retro](../charness-artifacts/retro/2026-06-06-quality-scan-closeout-discipline.md)
- [#320 debug](../charness-artifacts/debug/2026-06-06-issue-320-mutation-changed-line-coverage.md),
  [pre-merge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
