# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Current State

- **#454 RESOLVED, shipped in v2.6.0.** Passing `name` to the host spawn routes a
  bounded reviewer onto a teammate/mailbox protocol the parent has no tool to read,
  so a complete review is written and stranded. Corroborated by the still-open
  upstream defect anthropics/claude-code#71723 — the unnamed-spawn rule is a
  **workaround for a live upstream bug**, not a permanent fact; re-probe when it closes.
- The rule now lives where it cannot decay: `## Result Delivery` in
  [fresh-eye-subagent-review.md](../skills/shared/references/fresh-eye-subagent-review.md),
  plus a typed `Delivery state` floor in
  [validate_critique_artifacts.py](../scripts/validate_critique_artifacts.py) — a
  closeout cannot record a review as obtained without saying whether findings
  arrived. A **recurrence**: recorded 2026-06-20, decayed, re-derived wrongly twice
  ([debug artifact](../charness-artifacts/debug/2026-07-25-bounded-reviewer-result-delivery.md)).
- Every changed-line mutation blocker in the released range is cleared (66 tests
  across five files owned by earlier commits), so the next scheduled run should not
  fail for unrelated files. #453's fixes are now PUSHED; it stays deliberately OPEN
  for a human close. No other open issues (re-check `gh issue list --state open`).

## Next Session

1. **Close #453** once the next **scheduled** mutation run is verified with
   `check_mutation_run_proof.py --claim changed-line --run-id <id>`. A dispatch
   re-run cannot prove it (no `base_sha`). A local changed-line run over the
   released range came back clean — supporting evidence, not that proof.
2. **D38 (new):** nothing detects a correct retro lesson that never reaches a
   durable contract — the mechanism behind #454's five-week recurrence.
3. **Pinned, not fixed:** `REPO_ROOT.resolve() / "skills" / "public"` escapes the
   export-safety predicate ([decision point](../tests/quality_gates/test_export_safe_asset_paths.py)).
4. **Sweep is signed off — do not re-run it.** One surfaced twin,
   `recommended_commands` in `plan_cautilus_proof.py`, needs the same call as the
   deleted `required`; left alone only because it was outside the sign-off.
5. Three unowned follow-ups with evidence in the artifacts below: critique packet
   tier mismatch, specdown preset duplication, proxy-assertion review of ~9 tests.
6. Budgets retuned for `local-linux-x86_64-36cpu` only; run the budget check on
   aarch64/unprofiled hardware.
7. Still deferred: inline `.rglob`/`ls-files` pathspec discovery,
   `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero test-surface advisory, D18,
   stale `charness-run-*` basetemp reaping, #451's two unacted siblings. #449 declined.

## Discuss

- Four hazards learned 2026-07-25, detail in
  [recent lessons](../charness-artifacts/retro/recent-lessons.md): never restore a
  mutation target with `git checkout --` while the slice is uncommitted (reverts to
  HEAD, and a red baseline makes every mutant look killed); run
  `reviewer_boundary_fingerprint.py verify` the moment a reviewer returns; spawn
  discovery/workflow agents read-only — one edited a tracked adapter and left it dirty;
  and **never pass a host addressing/team `name` to a one-shot bounded reviewer** —
  it strands the findings in a mailbox the parent cannot read (#454).
- Do not re-litigate the two refuted audit findings (removing the dup-ratchet hard
  arm or the boundary-bypass ratchet). #448 scoped-accept items wait for the next
  dup-ratchet slice.

## References

- [#454 debug artifact](../charness-artifacts/debug/2026-07-25-bounded-reviewer-result-delivery.md) · [#454 resolution critique](../charness-artifacts/critique/2026-07-25-issue-454-resolution-critique.md)
- [ranked-chunks-1-3 goal](../charness-artifacts/goals/2026-07-25-ranked-chunks-1-3.md) · [session retro](../charness-artifacts/retro/2026-07-25-session-retro.md) · [unused-option sweep](../charness-artifacts/audit/2026-07-25-unused-mode-option-sweep.md)
- [v2.5.0 release critique](../charness-artifacts/critique/2026-07-25-v2-5-0-release-critique.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [release state](../charness-artifacts/release/latest.md) · [quality review](../charness-artifacts/quality/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
