# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Design north star landed + #386 shipped as v0.52.4** (published/verified;
  [`design-north-star.md`](./design-north-star.md) governs, referenced from
  `AGENTS.md`). #386 fixed by a Rung-2 distinct-observer/distinct-channel
  disposition-review mandate, **no new gate**.
- **Overhaul COMPLETE (Track 1a + Track 2 core), 2026-06-18** —
  [`north-star-overhaul` goal](../charness-artifacts/goals/2026-06-18-north-star-overhaul.md)
  (S1–S6). **Track 1a:** the #386 per-unit behavioral-verdict framing is
  generalized to every audited irreversible boundary (issue/PR close, release
  publish, release-linked close, deletion), each citing P4 with a distinct
  channel and **no new gate/token**. **Track 2:** standing surface shrank
  (`retro` core 160→146 off the cap; Cautilus detail pulled from `AGENTS.md`).
  Four slice critiques + a rung-2 disposition review PASS; broad pytest green.
  Step-0 mechanism archived in
  [`step0-experiment-program-archive`](../charness-artifacts/retro/2026-06-18-step0-experiment-program-archive.md).
- **#371 remains open by design** — no close without controlled invocation-end
  teardown proof (process tree + `agent-browser-chrome-*` dir) for completion,
  cancellation, provider failure, and timeout.
- Open issues (2026-06-18): #387 (closeout-validator one-pass UX — **not** the
  overhaul pilot, the prior handoff mislabeled it), #371 (browser teardown).
  #388 closed.

## Next Session

- **Primary spin-out: the remaining-13-capped-skill-body SRP sweep** (Track-2
  follow-up the overhaul sized). 14 public SKILL.md bodies sit within ~8 core
  lines of the 160-core cap (retro is now off it); compress each by own-concept
  separation like the retro S5 pilot. **Pre-check each body first** (overhaul
  retro lesson): grep `check_skill_contracts.py` for pinned snippets + run
  `check_skill_surface_preflight.py` for core-headroom BEFORE editing, and run the
  **broad** `pytest -q` at the bundle boundary (the per-slice `run_evals` subset
  misses some pinned-phrase tests).
- **Deferred: the `AGENTS.md` Skill-Routing duplication** — it duplicates Start
  Here, but `## Skill Routing` is a setup-generated surface pinned by
  `setup/scripts/render_skill_routing.py` (collapsing it flips `charness doctor`
  `repo_onboarding`); a real collapse needs a lockstep change.
- **External side effects deferred:** the overhaul pushed nothing. Pending local
  commits include the overhaul series + the older Step-0 archive `4da92874` /
  `8a92985f`; a push is a separate explicit operator decision.
- #371 stays on its own track. #387 (closeout-validator one-pass UX) is unrelated
  to the overhaul. Older deferrals: D28/D29 in
  [deferred decisions](./deferred-decisions.md).

## Discuss

- Who owns the #371 upstream lifecycle proof path.

## References

- [north-star overhaul goal (COMPLETE — S1–S6)](../charness-artifacts/goals/2026-06-18-north-star-overhaul.md)
- [Step 0 experiment program archive — RESOLVED](../charness-artifacts/retro/2026-06-18-step0-experiment-program-archive.md)
- [overhaul plan v2 (Track 1a now LIGHT)](../charness-artifacts/critique/2026-06-18-overhaul-plan-v2.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [release latest](../charness-artifacts/release/latest.md)
