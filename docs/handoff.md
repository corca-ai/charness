# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff entries + live open issues. `## Next Session` is
  sequencing judgment, not the full queue — **body-read the issues, don't trust it flat.**
- Refresh: `git status -sb`, `git log --oneline origin/main..HEAD`,
  `gh issue list --state open --limit 50`. Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **#395 dup-ratchet family_id churn — RESOLVED + CLOSED + PUSHED** (@ `6658acec`).
  Family `id` folds member line-offset + path → member edits false-block. Shipped
  reporter solution (b) (doc + characterization test + lockstep re-baseline); the
  affordance (c) deferred as **D30**. RCA:
  [debug artifact](../charness-artifacts/debug/2026-06-21-dup-ratchet-family-id-rotation.md).
- **Chunk-2 multi-root resolver — DONE + PUSHED** (@ `91aae959`). `collect_families`
  now runs ONE nose 0.14.0 `--root` multi-root query (global clustering). **Quality-
  contract change**: 491→525 families (gains 108 cross-root clones; both baselines
  re-baselined lockstep). [critique](../charness-artifacts/critique/2026-06-21-quality-nose-multiroot-resolver.md).
- **nose 0.14.0 floor live**; this machine's plugin updated; other machines pending
  `update all`.

## Next Session

> Pickup must **body-read the open issues**, not trust this list flat — a prior
> session found #391 and the overhaul-sweep buried real signal under issue
> numbers. Tiers below are from a live-backlog read on 2026-06-21.

- **Tier 0 — DONE 2026-06-21.** #395→R2 live-proof recorded in the
  [overhaul-sweep goal](../charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md);
  the deferred WS-B body redesign is tracked **file-over-issue** there (no GitHub
  issue, per operator). Next session starts at Tier 1.
- **Tier 1 — #391 baseline `tool_version` stamp (concrete, session-adjacent).**
  The clone-advisory baseline records no scanner version, yet the contract says
  "re-baseline per scanner version" — a future nose bump silently reads a stale
  baseline. Fix: `--write-baseline` stamps the version; read path warns on mismatch.
  (#391 also lists cross-dir extraction candidates newly visible under multi-root.)
- **Tier 2 — backlog clearing.** Activate the draft
  [open-issue-hotl-closeout goal](../charness-artifacts/goals/2026-06-16-open-issue-hotl-closeout.md)
  to clear #387 (goal-closeout shape errors), #392 (gather X/Twitter), #371
  (agent-browser orphaned chromium).
- **Tier 3 — the deferred skill sweep (needs operator decisions).** Deeper body
  redesign of impl/debug/quality/achieve was deferred-with-cause (cuts blocked or
  lossy). Unblock starts at the **`quality` anchor-split (ODQ #2)**: the
  `Load-Bearing Anchors` section is pinned by ~60
  [test_quality_skill_docs.py](../tests/quality_gates/test_quality_skill_docs.py)
  assertions; operator must approve moving them to `quality/references/inventory-dispatch.md`.
- **Tier 4 — triage.** #394 mutation regression (re-fires on changed-line coverage,
  score passes — real-gap vs noise); **D30** ([deferred-decisions.md](./deferred-decisions.md));
  ceal #417; gate demotions; other-machine `charness update all` (low-urgency).

## Discuss

- **#395 may have satisfied overhaul-sweep R2's open live-proof** (a real issue
  closed through the distinct-channel verdict + AI-provenance floors). Confirm + mark
  it in the sweep goal before treating R2 as still-open.
- **Multi-root model is live (chunk-2)** — deliberate quality-contract change
  (per-root → global); first place to look if a consumer repo behaves oddly.

## References

- [dup-ratchet reference](../skills/public/quality/references/dup-ratchet.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [deferred-decisions](./deferred-decisions.md)
