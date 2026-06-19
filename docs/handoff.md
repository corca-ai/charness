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

- **This session: item-5 slice-2 DONE — the boy-scout dup ratchet's teeth**
  (closes C5). Landed per the spec
  [`### Slice 2`](../charness-artifacts/spec/boy-scout-dup-ratchet.md): pure policy
  lib + git seams, the [gate CLI](../skills/public/quality/scripts/check_dup_ratchet.py),
  a validated `dup_ratchet` adapter block, the green-seeded baseline + charness
  rollout (D6, `fixable_ceiling: 0`), run-quality + broad pre-push wiring, the
  [reference](../skills/public/quality/references/dup-ratchet.md), and tests SC1–SC6.
- **Chunk 1 (slice 1 + #393) earlier landed.** #393 closes on the next *scheduled*
  mutation run per its own contract.

## Next Session

- **nose 0.13.3 scan→query migration (NOW REQUIRED).** Verified this session that
  0.13.3 removed `nose scan`, breaking the code-clone path (`inventory_nose_clones`
  and the dup-ratchet gate); the gate degraded to advisory, never false-blocked
  (FD8 validated), and the repo stays on 0.13.0 until migrated. Findings + plan: the
  spec's [`## Constraints`](../charness-artifacts/spec/boy-scout-dup-ratchet.md) nose note.
- **dup-ratchet hardening slice** (deferred from the slice-2 critique — an
  "enabled-but-misconfigured → degrade / re-seed discipline" batch): a
  `--write-baseline` delta/confirm guardrail (FD6 lock-in has no code teeth yet);
  wire `validate_gate_baseline` into a run-quality/validate phase (a malformed
  committed baseline silently disarms the hard arm); warn when `enabled` but
  `scope_paths` is empty. See the spec's `### Slice 2 Critique`.
- **Remaining gate items** (B1 advisory pattern, fresh-eye + broad closeout):
  doc-links -> lychee BUY + demote backtick/bare-mention to advisory;
  validate_critique_artifacts (keep tier-honesty, demote rest);
  validate_skill_ergonomics export-leak arm (DELICATE adapter split). See the
  [gate buy-vs-build decisions](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md).
- **Untouched original tracks / open issues:** SRP skill-body reduction +
  [#391](https://github.com/corca-ai/charness/issues/391) extractions + tool_version
  stamp; #387 one-pass goal-closeout shape; #392 gather X/Twitter; #371
  agent-browser orphan teardown.

## Discuss

- On charness the boy-scout escalation arm is advisory-by-default
  (`fixable_ceiling` 0, floor_F 0), so its block path is proven only by the
  slice-2 acceptance fixture (SC4), not in production. The hard arm (new fixable
  family blocks) is live and green.
- The gate baseline is a re-seedable green snapshot of today's full code
  `family_id` set; re-seed it deliberately (only to accept reviewed new families)
  with `check_dup_ratchet.py --write-baseline`, and per scanner-version bumps.

## References

- [item-5 spec](../charness-artifacts/spec/boy-scout-dup-ratchet.md) (slice-2
  decisions + file plan), [corca-ai/nose#466](https://github.com/corca-ai/nose/issues/466),
  [dup-ratchet reference](../skills/public/quality/references/dup-ratchet.md),
  [gate buy-vs-build decisions](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [mutation-testing reference](../skills/public/quality/references/mutation-testing.md),
  [design north star](./design-north-star.md)
