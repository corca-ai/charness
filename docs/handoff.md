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

- **Local goal bundle complete, publication pending (2026-06-15):**
  [nose/issues/runtime goal](../charness-artifacts/goals/2026-06-15-nose-issues-371-373-test-runtime.md)
  reduced current-pointer scan runtime, locally resolved #373 and #372 via
  direct-commit closeout carriers, recorded #371 as an upstream
  `agent-browser` lifecycle split, and reduced selected nose 0.10.0 adapter
  helper duplication. Broad pytest passed locally (3056 passed, 26 deselected).
  Push `main` to publish the `Close #372` / `Close #373` commits, then add the
  prepared #371 upstream-split comment if not already posted.
- **#367 resolved end-to-end and shipped in v0.50.0.** The `quality` skill gained
  two portable gate-speed capabilities
  ([goal](../charness-artifacts/goals/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md)):
  (1) a **CI-recoverability triage lens** (`inventory_ci_recoverable_gates.py`) —
  the explicit counterweight to the local-proof guardrail that flags only the
  costly local gates CI fully re-runs as move-off-local candidates (ranked by
  wall-clock), keeping the rest `keep-local`; (2) a **`command_timing_log` adapter
  key** that feeds `render_runtime_summary` / `check_runtime_budget` / the lens
  from a repo's existing timing log. Both advisory/inert (no blocking floor).
  Four slices, two fresh-eye reviews (SHIP), broad pytest green (3033 passed).
- **Open issues (`gh`, 2026-06-14): #368** — shift the inference-interpretation
  surface-registration check left into the commit-time structural sweep (it is
  enforced only by a broad-pytest test today) plus an "adding-an-advisory-surface"
  authoring checklist. Filed as the #367 retro disposition.
- The #184 verdict still flips on its own as the rolling window advances if no new
  falsified conversion lands — check `python3 scripts/aggregate_rca_ledger.py`.

## Next Session

- **Prioritized pickup: #368** — promote the inference-interpretation
  unregistered-declaration leak scan into the commit-time structural sweep (where
  `validate_attention_state_visibility` already runs), so a new advisory surface's
  registration requirement surfaces at commit, not at the ~4-min broad pytest;
  bundle the authoring checklist. Changes the shared commit-gate aggregate, so it
  warrants its own critique.
- **Still deferred** (reopen triggers): **E2b** (chunker ingests recurring waste —
  needs real 0.45.0+ usage telemetry) and the **Coordination-Cues floor merge**
  (a floor *removal*, separately critiqued).
- Older deferrals: D28/D29 in [deferred decisions](./deferred-decisions.md); the
  [contract-effectiveness fixture](../evals/cautilus/contract-effectiveness.fixture.json)
  needs a log-backed request.

## Discuss

- Whether a consumer-facing announcement is worth it for the v0.50.0 #367
  quality gate-speed surfaces (CI-recoverability lens + `command_timing_log`),
  or whether they ride the next batched release note.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [#367 goal](../charness-artifacts/goals/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md)
- [#367 retro](../charness-artifacts/retro/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md)
