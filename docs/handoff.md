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
- **v0.52.6 release findings — resolved:** family_id churn on same-file edits → filed
  [#395](https://github.com/corca-ai/charness/issues/395); pre-push vs release-mode proof
  divergence → confirmed intended design (layered proof).
- **Gate buy-vs-build — only demotions left.** lychee BUY (item ②) **REJECTED** by cold
  analysis: 0 behavioral gain vs the existing 2-line `.exists()` (the 3 divergence cases —
  URL-encoded / fenced-code / inline-code links — occur 0 times across 281 docs), while
  costing a required dep + ~300 LOC + 3 CI installs; reverted. Lesson: compare a BUY
  against the *existing baseline*, not a strawman. ①③④ already landed. **Next slice
  (Track A):** demote check_doc_links backtick/bare-mention enforcement to advisory (WARN,
  keep principle), then critique/skill-ergonomics demotions. See
  [gate buy-vs-build](../charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md).
- **Untouched tracks:** [#391](https://github.com/corca-ai/charness/issues/391)
  extractions + tool_version stamp; #387 goal-closeout shape; #392 gather X; #371
  agent-browser teardown.

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
