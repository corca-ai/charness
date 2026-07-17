# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the
  backlog below (the operator-directed affordance convergence closed on
  2026-07-17). Restart hosts first only when testing installed-plugin
  behavior; an explicit user task keeps its own authority.

## Current State

- v2.0.0 is public (operator: "push and release when done"): the
  operator-approved breaking affordance convergence landed in `7b20b0ce`
  (worktree string `next_action`→`next_step`, runtime doctor host map
  `next_steps`→`host_next_steps`, tool attention `next_action`→`next_step`,
  human prefix unified to `NEXT:`; no aliases), release commit `586c19e9`,
  tag `v2.0.0`, distinct-channel https confirmation 200. The first publish
  attempt was refused by the release battery; both gate failures were
  repaired at root in `630bcfce` before the rerun. Verification record in
  [release state](../charness-artifacts/release/latest.md).
- v1.3.0→v2.0.0 migration note: the first `charness update` from an old
  binary crashes once (`KeyError: 'next_steps'`) after refreshing the
  checkout+binary; the re-run completes. Recorded in the GitHub release
  notes ("Upgrading from v1.3.0") and the release state; the maintainer
  machine finished the re-run and reports `2.0.0`.
- The converged vocabulary contract lives in the
  [affordance spec](../charness-artifacts/spec/cli-output-affordance-contract.md)
  Fixed Decisions (with the kept exceptions: structured `next_action`,
  list-shape `next_steps`, `--next-action` flag projection,
  `next_action_hint` manifest input); the executable tool-doctor spec
  asserts `host_next_steps` live.

## Next Session

1. Restart hosts to load the installed v2.0.0 surface before testing
   installed-plugin behavior (plugin caches rotated at publish).
2. D18 disposition (passed over 2026-07-17, still pending with the same
   reopen trigger) — see the 2026-07-16
   [goal artifact](../charness-artifacts/goals/2026-07-16-scout-driven-improvement.md)
   `## Operator Decision Queue`.

## Discuss

- Optional polish: a one-time self-healing rerun (or clearer message) for the
  old-binary→new-checkout `charness update` crash class, if a future breaking
  release would otherwise repeat the v2.0.0 migration hiccup.
- Optional under the 2026-07-17 per-host split: a live Codex-host session can
  still add provider-applied evidence that the Codex-scoped
  `gpt-5.6-terra`/`medium` request is honored; evidence polish, not a blocker.

## References

- [affordance spec](../charness-artifacts/spec/cli-output-affordance-contract.md)
  · [slice critique](../charness-artifacts/critique/2026-07-17-affordance-convergence-slice.md)
  · [release critique](../charness-artifacts/critique/2026-07-17-v2-0-0-release-critique.md)
  · [release state](../charness-artifacts/release/latest.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept (`AGENTS.md`): the published-v2.0.0 restart-to-load state
  (first action), the carried D18 decision, and the per-host reviewer
  contract.
- Refresh non-claims ([release state](../charness-artifacts/release/latest.md)):
  the migration-crash observation is one maintainer machine; no consumer-repo
  upgrade was exercised at refresh time; the convergence's payload renames
  are proven by the test suite and one live doctor/update run, not by
  external-consumer evidence.
