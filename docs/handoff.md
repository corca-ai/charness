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

- **This session: item-5 slice-2 DESIGN resolved; NO code written (clean tree).**
  The identity fork the prior handoff flagged is settled and recorded in the spec
  [`### Slice 2 — Resolved Decisions + Plan`](../charness-artifacts/spec/boy-scout-dup-ratchet.md):
  nose's code baseline `key` is cluster-churny and not `family_id`-diffable
  (17/42 current "drift" families sit in unchanged files), so the gate keys code
  newness on a NEW stable `family_id` gate baseline; docs reuse the existing
  stable `signature` drift. Filed upstream **corca-ai/nose#466**.
- **Chunk 1 (slice 1 + #393) landed** (`origin/main == HEAD`). #393 closes on the
  next *scheduled* mutation run per its own contract.

## Next Session

- **Implement item-5 slice 2 (the ratchet's teeth).** The full contract — decisions
  D1–D6, inert/degraded ladder, the 9-step file plan, and gotchas — is in the spec
  [`### Slice 2 — Resolved Decisions + Plan`](../charness-artifacts/spec/boy-scout-dup-ratchet.md).
  First move: build `dup_ratchet_lib.py` (pure `evaluate` + injectable git seams)
  and `check_dup_ratchet.py`; add the validated `dup_ratchet` adapter block; seed
  `dup-ratchet-baseline.json` green + enable on charness (D6); wire run-quality +
  broad pre-push (not the docs-only subset; C5); tests SC1–SC5. Closes C5.
- **Remaining gate items** (B1 advisory pattern, fresh-eye + broad closeout):
  doc-links -> lychee BUY + demote backtick/bare-mention to advisory;
  validate_critique_artifacts (keep tier-honesty, demote rest);
  validate_skill_ergonomics export-leak arm (DELICATE adapter split).
- **Untouched original tracks / open issues:** SRP skill-body reduction +
  [#391](https://github.com/corca-ai/charness/issues/391) extractions + tool_version
  stamp; #387 one-pass goal-closeout shape; #392 gather X/Twitter; #371
  agent-browser orphan teardown.

## Discuss

- Slice-2 design fork is RESOLVED (spec D1–D6); no user input pending. Note: on
  charness the boy-scout escalation arm is advisory-by-default (`fixable_ceiling`
  0), so its block path is proven only by the slice-2 acceptance fixture, not in
  production.

## References

- [item-5 spec](../charness-artifacts/spec/boy-scout-dup-ratchet.md) (slice-2
  decisions + file plan), [corca-ai/nose#466](https://github.com/corca-ai/nose/issues/466),
  [gate buy-vs-build decisions](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [mutation-testing reference](../skills/public/quality/references/mutation-testing.md),
  [design north star](./design-north-star.md)
