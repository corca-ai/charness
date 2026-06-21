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

- **`quality` anchor-split EXECUTED + PUSHED** (@ `62224d9b`): `## Load-Bearing Anchors`
  → routing in `inventory-dispatch.md` + judgment in Workflow/Guardrails + a `## Routing`
  pointer (SKILL.md 200→191/200); lossless (green oracle + 3 fresh-eye). [critique](../charness-artifacts/critique/2026-06-21-quality-anchor-split.md).
- **#391 `tool_version` stamp RESOLVED** (@ `edd8bade`); #391 stays OPEN for 3 extraction
  candidates. nose 0.14.0 floor + multi-root clustering live; baselines 526 ids @ 0.14.0.
- **`main` is red by one (pre-existing/environmental):** the `nose doctor` version-mismatch
  test fails on clean HEAD too (this machine's nose vs the manifest). Item 1 owns it.

## Next Session

> **Operator-decided order (2026-06-21): work 1 → 2 → 3 → 4 below** (gate-trust +
> velocity first, external #392 last). **Body-read each issue — titles undersell.**

- **1 — Green `main` + #394 triage (FIRST).** Diagnose the standing-red
  `nose doctor doctor_status == version-mismatch` (this machine's installed nose vs
  the manifest's expected version — which is stale?). Coupled: #394's block is
  changed-line coverage + 12 survived *config-literal* mutants
  (`init_adapter.py` / `resolve_adapter.py` `...: True` dict values) — kill-worthy
  vs typed-disposition, per mutant. Score itself passes (90% vs 80%).
- **2 — #387 one-pass goal-closeout shape report.** List every missing/malformed
  required closeout line (`Retro:` / `Host log probe:` / `Disposition review:`),
  show the accepted shape, distinguish missing vs wrong-syntax — no flip-serial
  discovery. Fits `describe_goal_closeout_shape.py` (describe-first preflight), not
  a new blocking floor.
- **3 — WS-B body redesigns + #391 extraction.** Apply today's anchor-split recipe
  (concept-separate → verify lossless+contract-safe BEFORE cutting → re-point the
  test oracle → fresh-eye) to impl/debug/achieve — only where a clean split verifies
  (prior check flagged them concept-dense; some legitimately stay). #391 open scope:
  subprocess-timeout wrapper (7 sites, clearest extract), `scaffold_*_artifact.py`,
  `*_adapter_lib` / `_adapter_policy` — decide per family.
- **4 — #392 gather-X honest-failure contract (LAST).** Exact X fetch is likely
  infeasible (captcha/login-wall); deliver a typed result distinguishing
  `exact-acquired | blocked-by-X | auth/browser-route-required | unsupported` +
  route-level trace + a regression fixture, so Ceal stops retrying without losing
  source identity. Scope call at pickup (see Discuss).
- **Parked:** #371 (charness-side shipped v0.50.1 `charness tool repair agent-browser`;
  upstream-blocked on vercel-labs/agent-browser#1334 — verify the cmd, leave open).
  D30/D31 in [deferred-decisions.md](./deferred-decisions.md); ceal #417;
  other-machine `charness update all` (low-urgency).

## Discuss

- **#392 scope (decide at pickup of item 4):** attempt a real exact-X route
  (browser/auth/syndication — likely infeasible) vs commit to the typed-unsupported
  honest-failure contract only. Operator-decided priority puts this last.
- **D31 still manual:** the chunker does not reconcile against recent commits, so a
  pickup reads `git log` by hand to de-stale the queue (done again this session). Worth
  pulling the slice if pickup keeps mis-prioritizing.

## References

- [dup-ratchet reference](../skills/public/quality/references/dup-ratchet.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [deferred-decisions](./deferred-decisions.md)
