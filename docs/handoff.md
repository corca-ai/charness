# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state before acting: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.44.1 shipped and public release is verified.** Release commit
  `ac0d8063 Release charness 0.44.1`; release-verification commit
  `b0f06462 Record release verification for v0.44.1`; tag `v0.44.1`
  is published and the maintainer install auto-refreshed to 0.44.1 (see
  [release latest](../charness-artifacts/release/latest.md)).
- **#359 resolved, CLOSED, and shipped in v0.44.1 (carrier `ebff7d50`).**
  `achieve` complete-state closeout now blocks pending section placeholders via
  `section_placeholders`; draft/active scaffolds remain allowed. Critique:
  [#359](../charness-artifacts/critique/2026-06-13-issue-359-goal-placeholder-closeout-resolution.md).
- **#358 resolved and CLOSED (carrier `22f3542d`, GitHub state verified).**
  The dispatch/no-base-sha mutation-proof false conversion is now gate-backed
  and RCA-upgraded. Critique:
  [#358](../charness-artifacts/critique/2026-06-13-issue-358-dispatch-proof-gate-resolution.md).
- **#184 target verdict stays not-met by design** until the 06-05 recurrence
  ages out of the rolling 28d window (tripwire-response contract: the
  upgrade annotates, never clears). The aggregator now renders
  `(artifact upgraded 2026-06-12, #358)` on the falsified entry.
- **Open issues (`gh`, 2026-06-13): none.**
- Restart note: active sessions may carry pre-0.44.1 plugin cache paths; restart
  Claude/Codex sessions to load the refreshed install.

## Next Session

- No queued implementation candidate; the tracker is empty. The #184 verdict
  flips on its own as the window rolls forward if no new falsified
  conversion lands — check `python3 scripts/aggregate_rca_ledger.py`.
- Deferred from the #358/v0.44.0 critiques (valid-but-defer, not filed):
  run-id-mode refusal reason without the dispatch class key for schedule
  runs; a consumer template-drift advisory for installed mutation workflows;
  mutation-score skip-denominator semantics if skip volume grows.
- Live deferrals remain D28/D29 in
  [deferred decisions](./deferred-decisions.md) (D29: scorecard helper +
  metric-only closeout guard; reopens on consumer-repo discovery failure or
  operator request).
- Live execution of the
  [contract-effectiveness fixture](../evals/cautilus/contract-effectiveness.fixture.json)
  needs an explicit log-backed request naming a
  failing-prompt/transcript/operator-log path, then the
  [cautilus eval wrapper](../scripts/run_cautilus_eval.py).

## Discuss

- Decide whether a consumer-facing announcement is still useful for recent
  scheduled-mutation, YouTube/issue retrieval, and scorecard/cadence changes.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [v0.44.1 release record](../charness-artifacts/release/latest.md)
- [overnight bundle critique](../charness-artifacts/critique/2026-06-12-autonomous-structural-quality-bundle.md)
