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
  stays OPEN** for its 3 extraction candidates. Both nose id-set baselines stamp the
  producing nose version and WARN (never degrade) on scanner-version skew (additive, no
  schema bump). [debug](../charness-artifacts/debug/2026-06-21-nose-baseline-tool-version-stamp.md).
- **nose 0.14.0 floor + multi-root global clustering live**; both baselines at 526 ids,
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
- **Tier 3 — `quality` anchor-split EXECUTED; impl/debug/achieve bodies are the
  same-recipe follow-on.** The `quality` `## Load-Bearing Anchors` catalog was dissolved
  (routing → `inventory-dispatch.md`, CORE+judgment → Workflow/Guardrails, a `## Routing`
  pointer replaced it; SKILL.md 200→191/200). Lossless by the green oracle
  (`tests/quality_gates/` 2283 + contracts + 3 distinct-channel fresh-eye reviewers, zero
  orphans); see the [critique](../charness-artifacts/critique/2026-06-21-quality-anchor-split.md)
  and the sweep goal ODQ EXECUTED block. **Next:** apply the SAME recipe to the
  impl/debug/achieve bodies (2 deferred NITs noted in the critique).
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
