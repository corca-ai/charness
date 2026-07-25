# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Current State

- **v2.5.0 is PUBLISHED and ships a real bug.** `propose_mutation_testing.py` could
  not reach its workflow template from the plugin copy — the only copy a consumer
  installs — in every tag back to at least `v2.2.1`; `--execute` failed *after*
  writing the adapter scaffold, so a fresh install ends half-scaffolded. **Fixed
  after the tag** (`c92e9561`); correction in the
  [v2.5.0 notes](../charness-artifacts/release/2026-07-25-v2.5.0-notes.md).
- Three named residuals CLOSED: `issue_close_comment_floor` checks AI-provenance
  (the other two omissions are recorded as intentionally not wired); the specdown
  report no longer churns; the fresh-install render path is tested.
  `check_export_safe_imports.py` now rejects `skills/public` *filesystem paths*,
  the class that shipped the bug above.
- #453's blocking signal is fixed and evidence-commented; it is deliberately still
  OPEN for a human close. No other open issues (re-check `gh issue list --state open`).

## Next Session

1. **Three operator decisions**, all in the completed goal's
   `## Operator Decision Queue`: (a) patch release for the plugin-copy fix, or let it
   ride the next cut; (b) close #453 — needs the next **scheduled** mutation run
   verified with `check_mutation_run_proof.py --claim changed-line`, since a
   dispatch re-run cannot prove it; (c) which of the 9 unused options to delete.
2. **The sweep is done, awaiting sign-off — do not re-run it.** 9 confirmed / 3
   refuted, zero deletions, blast radius per candidate; four confirmed items are
   published portable contracts whose downstream use this repo cannot observe.
3. Three unowned follow-ups, each with its evidence in the artifacts below: the
   critique packet tier mismatch and the specdown preset duplication (sweep
   artifact), and a proxy-assertion review of ~9 source-grepping tests (retro
   sibling scan).
4. Budgets are retuned for `local-linux-x86_64-36cpu` only; aarch64 and the
   unprofiled defaults have **no samples here**, so nothing is actionable from this
   machine. Run the budget check on that hardware.
5. Still deferred, unchanged: inline `.rglob`/`ls-files` pathspec discovery,
   `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero test-surface advisory, D18,
   stale `charness-run-*` basetemp reaping, #451's two unacted siblings. #449 was
   declined over its CI write-permission surface.

## Discuss

- Three hazards learned 2026-07-25, detail in
  [recent lessons](../charness-artifacts/retro/recent-lessons.md): never restore a
  mutation target with `git checkout --` while the slice is uncommitted (reverts to
  HEAD, and a red baseline makes every mutant look killed); run
  `reviewer_boundary_fingerprint.py verify` the moment a reviewer returns; spawn
  discovery/workflow agents read-only — one edited a tracked adapter and left it dirty.
- Do not re-litigate the two refuted audit findings (removing the dup-ratchet hard
  arm or the boundary-bypass ratchet). #448 scoped-accept items wait for the next
  dup-ratchet slice.

## References

- [ranked-chunks-1-3 goal](../charness-artifacts/goals/2026-07-25-ranked-chunks-1-3.md) · [session retro](../charness-artifacts/retro/2026-07-25-session-retro.md) · [unused-option sweep](../charness-artifacts/audit/2026-07-25-unused-mode-option-sweep.md)
- [v2.5.0 release critique](../charness-artifacts/critique/2026-07-25-v2-5-0-release-critique.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [release state](../charness-artifacts/release/latest.md) · [quality review](../charness-artifacts/quality/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
