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

- **v0.52.5 shipped + verified** (latest public release, install `== repo`).
  Bundled the north-star overhaul (Track 1a per-unit verdict framing + Track 2
  slim) **and** the #390 code-layer pass. `origin/main` is current — nothing
  unpushed.
- **#390 CLOSED** (one closeable pass): the nose clone advisory is now
  **baselined** (547 accepted) so it reports only new/changed drift; the **14
  genuine extractable families are held visible (not baselined)** and filed in
  **#391**. Debug sweep (492 files) clean; doc↔code clean. Re-baseline only
  **after** surfaced candidates are fixed, never blindly. Record + held-out
  signatures: [#390 pass record](../charness-artifacts/quality/2026-06-19-390-code-layer-quality-pass.md).
- Open issues: **#391** (code-layer dup follow-ups, sub of #390), **#387**
  (closeout-validator one-pass UX), **#371** (browser teardown — own track, no
  close without invocation-end teardown proof).

## Next Session

- **A. Bootstrap-duplication justification (operator-requested, NEW).** #390
  *assumed* the resolve_adapter/init_adapter/skill_runtime_bootstrap copies are
  intentional portability boilerplate. **Verify that's really justified** — is
  the local-dup-for-package-independence trade still right, or should it
  consolidate to a shared bootstrap? This is the deepest residual the #390
  verification flagged. Reference **`../craken-agents`**.
- **B. Gate reduction (operator-requested, NEW).** Examine whether **existing**
  gates can be **removed** (~34.7K-line gate surface) — "less but better" on the
  gate layer, **without** adding new floors. Live case study (retro root-cause):
  the length **hard floor** invited gaming this session (squeeze-under vs the
  intended refactor split); consider shifting that signal to authoring-time /
  advisory. Reference `../craken-agents`.
- **C. SRP sweep (original primary).** Remaining capped-skill-body compression by
  own-concept separation. Pre-check each body: grep `check_skill_contracts.py`
  for pinned snippets + run `check_skill_surface_preflight.py` for core-headroom
  BEFORE editing; run the **broad** `pytest -q` at the bundle boundary.
- **D. #391 extractions** (subprocess-timeout wrapper — a non-release session;
  scaffold/adapter-lib classification) + the baseline `tool_version` stamp.

## Discuss

- A vs the portability model: consolidate bootstrap, or keep the deliberate copy?
- B: which existing gates are prunable without losing the teeth that matter?
- What `../craken-agents` is / how to use it (route via `gather` if external).
- Who owns the #371 upstream lifecycle proof path.

## References

- [release latest](../charness-artifacts/release/latest.md),
  [#390 pass record](../charness-artifacts/quality/2026-06-19-390-code-layer-quality-pass.md),
  [session retro](../charness-artifacts/retro/2026-06-19-390-code-layer-pass-retro.md)
- [design north star](./design-north-star.md),
  [capabilities over features](../charness-artifacts/gather/2026-06-18-capabilities-over-features.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [deferred decisions](./deferred-decisions.md)
