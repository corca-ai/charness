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

- **Released v0.52.6 (pushed + tagged + GitHub release `verified`).** Shipped the
  dup-ratchet hardening (F scope_paths-empty advisory, C `--write-baseline`
  delta/confirm guard, I `validate_gate_baseline` folded into the existing
  evaluate path — all advisory/non-blocking) + in-process coverage for
  `check_dup_ratchet.py` (0%→86%, closes the #393 attribution class) + the earlier
  nose 0.13.3 scan→query migration. Install refresh ran (`charness update`
  0.52.5→0.52.6, installed plugin `== repo`); CI Quality Core green on the release
  tip. Goal:
  [dup-ratchet hardening goal](../charness-artifacts/goals/2026-06-19-issue-393-harden-the-dup-ratchet-gate-scope-paths-empty-warning-write.md)
  (`Status: complete`).
- **Release-gate catch:** `run-quality --release` caught a stale `make_fake_nose`
  fixture (`0.6.0` < shipped floor `>=0.13.3`) that the read-only pre-push proof +
  CI Quality Core skip; fixed to `0.13.3` before publishing.

## Next Session

- **Improvement candidates — advisory by default, NOT new blocking gates** (honor
  the Floor-Addition Restraint; promote to a floor only on recorded recurrence):
  make the changed-line gate's `--reuse-coverage` path skip a coverage file that
  contains none of the changed files' repo-relative paths (a degrade that *removes*
  the false-block class — not a floor); plus two workflow habits — sanity-check a
  tool's output shape before relaying a surprising all-fail, and don't let an
  off-contract probe outrank the canonical gate. Rationale: the retro above.
- **Two findings from the v0.52.6 release (operator's call to file):** (a)
  **family_id churn on same-file edits** — editing a scanned member file rotates
  its clusters' nose `family_id`, forcing a re-baseline with no new duplication
  (transferable to consumer repos); (b) **pre-push vs release-mode proof
  divergence** — release-mode-only tests are skipped pre-push and by CI Quality
  Core, so a stale fixture shipped to main undetected. Detail in the goal's
  Off-Goal Findings + Operator Decision Queue.
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
