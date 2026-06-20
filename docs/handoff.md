# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff entries + live open issues. `## Next Session` is
  sequencing judgment, not the full queue — **body-read the issues, don't trust it flat.**
- Refresh: `git status -sb`, `git log --oneline origin/main..HEAD`,
  `gh issue list --state open --limit 50`, and skim `git log --oneline -10`
  (de-stale the queue against what recently shipped). Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **#391 baseline `tool_version` stamp — RESOLVED + PUSHED** (@ `edd8bade`); **#391
  stays OPEN** for its 3 extraction candidates. Both nose code id-set baselines now
  stamp the producing nose version and WARN (never degrade) on a scanner-version skew;
  additive field, no schema bump, legacy-unstamped = "unknown". RCA + version-safe/
  unsafe derived-surface inventory:
  [debug artifact](../charness-artifacts/debug/2026-06-21-nose-baseline-tool-version-stamp.md).
- **nose 0.14.0 floor + multi-root global clustering live** (prior sessions). The
  clone resolver analyzes the whole scope as one corpus; both baselines at 526 ids,
  stamped 0.14.0. First place to look if a consumer repo's clone gate behaves oddly.

## Next Session

> Pickup must **body-read the open issues**, not trust this list flat — a prior
> session found #391's concrete fix buried under a tracking-issue title. Tiers below
> are from a live-backlog read on 2026-06-21.

- **Tier 1 — backlog clearing via the draft
  [open-issue-hotl-closeout goal](../charness-artifacts/goals/2026-06-16-open-issue-hotl-closeout.md).**
  Activate it to clear #387 (goal-closeout shape errors — one-pass repair report),
  #392 (gather still cannot acquire exact X/Twitter posts after #338), #371
  (agent-browser orphaned chromium trees + profile dirs). Body-read each first.
- **Tier 2 — #391 extraction candidates + #394 triage.** #391's remaining open scope:
  the cross-dir subprocess-timeout wrapper (7 sites), `scaffold_*_artifact.py`
  scaffolding, `*_adapter_lib`/`_adapter_policy` logic — judgment per family ("decide
  per family, don't chase the count"). #394 mutation regression re-fires on
  changed-line coverage while the score passes — real-gap vs noise triage.
- **Tier 3 — the deferred skill sweep: `quality` anchor-split APPROVED + VERIFIED, ready to execute.**
  Operator approved (2026-06-21); a distinct-channel adversarial verifier proved it
  `LOSSLESS-ACHIEVABLE` via concept-separation (zero orphans; the prior defer was
  delete-without-merge). The ready-to-execute slice plan lives in the
  [sweep goal Operator Decision Queue](../charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md)
  (merge distinct routing → `inventory-dispatch.md`, fold principles → Workflow/
  Guardrails verbatim, re-point ~38 quality-skill-doc test pins = the
  losslessness oracle, sync/critique/commit). Then impl/debug/achieve bodies follow
  the same recipe.
- **Tier 4 — deferred ledger + ops.** D30 (dup-ratchet id-rotation affordance), D31
  (handoff chunker reconcile-against-recent-commits) in
  [deferred-decisions.md](./deferred-decisions.md); ceal #417; other-machine
  `charness update all` (low-urgency).

## Discuss

- **D31 is still manual:** the handoff chunker does not yet reconcile against recent
  commits, so a pickup must read `git log` by hand to de-stale the queue (done this
  session to confirm #391). Worth pulling the slice if pickup keeps mis-prioritizing.
- **Multi-root + version-stamp are live quality-contract surfaces** — a scanner bump
  now self-detects (skew WARNING), but the doc-signature baseline stamp is deferred.

## References

- [dup-ratchet reference](../skills/public/quality/references/dup-ratchet.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [deferred-decisions](./deferred-decisions.md)
