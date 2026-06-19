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

- **nose 0.13.3 scan→query migration DONE + committed (`15d5df4f`), NOT pushed**
  (stack is 4 ahead of origin/main). Code-clone path moved to `nose query` behind
  the resolver [`nose_report_lib.py`](../skills/public/quality/scripts/nose_report_lib.py)
  (per-root query merge, sv2/sv3 + `families`/`top_candidates`, `id`→`family_id`);
  advisory + gate id-baselines re-seeded to 487 on 0.13.3; manifest floor
  `>=0.13.3`. Verified green (run-quality 77/0, 104 focused tests,
  packaging/managed-install, 2-reviewer fresh-eye critique). Detail: spec
  [`### Slice 3`](../charness-artifacts/spec/boy-scout-dup-ratchet.md).
- **Post-migration:** the mutation-coverage producer's "block" was a FALSE positive
  (stale, context-keyed 2.1GB leftover that bare `--reuse-coverage` trusted);
  diagnosed + leftover removed, real gates skip it safely. Lessons in the
  [retro](../charness-artifacts/retro/2026-06-19-nose-migration-and-self-diagnosis-miss.md).
- **Earlier:** slice-2 (dup ratchet teeth, closes C5) + chunk 1 (slice 1 + #393).

## Next Session

- **Before pushing the unpushed stack:** add in-process coverage for
  `check_dup_ratchet.py` (the slice-2 CLI is subprocess-tested → 0% *attributed*,
  the #393 class). It is a TEST addition; the changed-line gate skips non-blocking
  today, but the scheduled mutation run will flag it. Then decide on push.
- **Improvement candidates — advisory by default, NOT new blocking gates** (honor
  the Floor-Addition Restraint; promote to a floor only on recorded recurrence):
  make the changed-line gate's `--reuse-coverage` path skip a coverage file that
  contains none of the changed files' repo-relative paths (a degrade that *removes*
  the false-block class — not a floor); plus two workflow habits — sanity-check a
  tool's output shape before relaying a surprising all-fail, and don't let an
  off-contract probe outrank the canonical gate. Rationale: the retro above.
- **dup-ratchet hardening slice** (slice-2 critique deferrals): `--write-baseline`
  delta/confirm guardrail; wire `validate_gate_baseline` into a run-quality/validate
  phase; warn when `enabled` but `scope_paths` empty. See spec `### Slice 2 Critique`.
- **Remaining gate items + untouched tracks:** doc-links→lychee BUY +
  critique/skill-ergonomics demotions (see
  [gate buy-vs-build](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md));
  [#391](https://github.com/corca-ai/charness/issues/391) extractions +
  tool_version stamp; #387 goal-closeout shape; #392 gather X; #371 agent-browser
  teardown.

## Discuss

- On charness the boy-scout escalation arm is advisory-by-default
  (`fixable_ceiling` 0, floor_F 0), so its block path is proven only by the
  slice-2 acceptance fixture (SC4), not in production. The hard arm (new fixable
  family blocks) is live and green.

## References

- [item-5 spec](../charness-artifacts/spec/boy-scout-dup-ratchet.md) (Slice 3 nose
  migration + slice-2 decisions),
  [dup-ratchet reference](../skills/public/quality/references/dup-ratchet.md),
  [nose migration retro](../charness-artifacts/retro/2026-06-19-nose-migration-and-self-diagnosis-miss.md),
  [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [gate buy-vs-build decisions](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md),
  [design north star](./design-north-star.md)
