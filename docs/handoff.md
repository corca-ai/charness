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

- **v0.44.0 shipped and public release is verified.** `main`/`origin/main`
  are at `f27f18d7 Record release verification for v0.44.0`; tag `v0.44.0`
  is published and the maintainer install auto-refreshed to 0.44.0 (see
  [release latest](../charness-artifacts/release/latest.md)).
- **#358 resolved and CLOSED (carrier `22f3542d`, GitHub state verified).**
  The `mutation-dispatch-no-base-sha-false-proof` conversion is upgraded
  from retro_lesson to gate:
  [check_mutation_run_proof.py](../scripts/check_mutation_run_proof.py)
  refuses citing a dispatch/no-base-sha mutation run as changed-line proof,
  the coverage script's no-base-sha verdict is loud, the mutation workflow
  auto-close is schedule-only (repo workflow + shipped template), and the
  upgrade is in the RCA ledger via the new `conversion_upgrade` mechanism.
  Resolution critique:
  [issue-358 critique](../charness-artifacts/critique/2026-06-13-issue-358-dispatch-proof-gate-resolution.md).
- **#184 target verdict stays not-met by design** until the 06-05 recurrence
  ages out of the rolling 28d window (tripwire-response contract: the
  upgrade annotates, never clears). The aggregator now renders
  `(artifact upgraded 2026-06-12, #358)` on the falsified entry.
- **Open issues (`gh`, 2026-06-13): none.**
- Restart note: active sessions carry pre-0.44.0 plugin cache paths; restart
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

- After #354's fix shipped, decide whether an operator announcement is still
  useful for the v0.40.0 scheduled-mutation-lane change and the v0.41.0
  YouTube/issue retrieval improvements — and now whether the v0.43.0
  scorecard/cadence contracts deserve one consumer-facing announcement.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [v0.44.0 release record](../charness-artifacts/release/latest.md)
- [overnight bundle critique](../charness-artifacts/critique/2026-06-12-autonomous-structural-quality-bundle.md)
