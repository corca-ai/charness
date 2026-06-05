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

- **v0.23.0 is shipped and verified.** Tag `v0.23.0` at `b85ab502`, GitHub
  release live, all version surfaces at 0.23.0, and #306/#311/#314/#315/#316/#317
  verified CLOSED. Release:
  <https://github.com/corca-ai/charness/releases/tag/v0.23.0>.
- Shipped via the **`2026-06-06-306-317-open-followups` achieve goal (complete)**:
  a dynamic workflow implemented all six as sequential committed slices —
  mutation-coverage honesty (#306), setup stale-AGENTS flag (#311), commit-boundary
  gate reconciliation (#314), setup commit-discipline seed (#317), achieve closeout
  placeholders (#315), achieve approval boundary (#316). S7 fresh-eye review +
  rung-2 disposition review both CLEAR; local `./scripts/run-quality.sh --release`
  72/0 is the bundle proof (minor bump, multiple additive `feat`).

## Next Session

1. Open backlog — route through `find-skills` then `issue`:
   - **#319** (filed this run): the `SKILL.md` `core_nonempty` headroom-buffer test
     runs only in the broad gate, not the commit boundary (generalizes #308/#314).
     The cleanest next quality pickup — it generalizes the just-shipped #314/#307.
   - **#318**: support orchestrator-owned external proof for achieve sub-goal closeout.
   - **#184**: 제품 성공 기준과 핵심 메트릭 정의 (product success metrics).
2. Do not reopen #306/#311/#314/#315/#316/#317 or the 306-317 goal unless current
   verification contradicts the shipped evidence.

## Discuss

- **No push/tag-triggered CI.** charness runs CI only on
  `workflow_dispatch`/path-scoped `pull_request`/cron (`mutation-tests.yml`), so a
  direct-to-`main` release gets **no** automatic CI on the released SHA; the local
  `--release` gate is the bundle proof, and a manual dispatch is a false proof
  (no `base_sha` — the #251/#306 trap). Worth deciding whether to add a light
  push/tag CI so released SHAs get a real remote run.
- **Pending operator real-host proof.** The v0.23.0 publish reported
  `real_host_required: true` (the standing `nose` checklist): a second-machine
  `charness update` + `charness tool doctor/install nose` run. Not done in-session.

## References

- [306-317 goal](../charness-artifacts/goals/2026-06-06-306-316-open-followups.md),
  [closeout retro](../charness-artifacts/retro/2026-06-06-306-317-open-followups-closeout.md)
- [v0.23.0 release critique](../charness-artifacts/critique/2026-06-06-v0.23.0-release-critique.md),
  [disposition review](../charness-artifacts/critique/2026-06-06-306-317-disposition-review.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
