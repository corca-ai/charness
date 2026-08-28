# Next-session plan: switch-on release and closeouts

> Date: 2026-08-29 (designed with the operator at the end of the
> 2026-08-28 migration session; the three shaping decisions below are
> operator-chosen, not inferred).
> Inputs: `issue-748/evidence-748.md`,
> `2026-08-28-issue-748-migration-plan.md` rev 2 (Deferred work),
> `issue-753/2026-08-28-jtbd-audit-quality-gates.md`.

## Operator decisions shaping this plan (2026-08-29)

1. Session keystone: the FIRST switch-on release runs first (operator
   present for the live-host checklist readback); the #748 matcher
   slice follows in the same session once consumers can resolve
   `healthy`.
2. #753 closes on current evidence; the un-audited remaining test
   corpus (~57k lines outside `tests/quality_gates`) is an accepted
   boundary, extrapolated from the 96.5%-keep audit of the 69%-mass
   directory.
3. #672 closed as retired-subject (done 2026-08-29, verified readback).
   Also already done: `check-test-production-ratio` promoted from
   advisory to BLOCKING (ratio 0.993 on the executable surface;
   headroom is thin — roughly 1k net test lines — and that pressure is
   the point).

## Session order

1. **Retro of the 2026-08-28 session** (`charness:retro`). Candidate
   lessons the retro should test, recorded here so they are not
   re-derived:
   - an ambiguous sentence in a lane brief propagates as a lane defect
     (plugin-refs inline-code masking); briefs must state scan/skip
     sets by citing the owning source, not paraphrasing;
   - name EVERY consumer of a deleted symbol in the deleting lane's
     scope — the commit-time staged plan was missed and silently
     dropped a gate;
   - never bulk `ruff --fix` across test-support modules: it strips
     re-exports (seed_commit regression); re-exports use the `as`
     alias form;
   - schema-seam fakes must pin argv SHAPE, not just payloads (the
     multi-path `--path` usage error survived lane tests);
   - task-run receipts: `after_head` is parent-tree movement, NOT the
     candidate sha (one mis-pick, aborted cleanly);
   - do not park work behind background waiters; inspect candidate
     state directly (a finished lane worktree is integrable before its
     wrapper exits), and salvage timed-out lanes from their worktree
     (seed-dedup: 96% of the work was recoverable).
2. **First switch-on release** (`charness:release` flow):
   - version bump; add the `native_core` declaration to
     `packaging/charness.json` (supported tuple
     `x86_64-unknown-linux-gnu`); build via
     `scripts/build_native_artifact.py` (pinned 1.96.0 toolchain,
     `--locked`); publish; `scripts/check_native_release_asset.py`;
     post-publish `charness update` on this host and the
     `native_core: healthy` doctor readback the release-adapter
     checklist already demands.
   - Release content since 7.x/8.0.0 includes: native gate ownership
     (export-safe, plugin-refs, what-reads, standalone selection), the
     #743 role exclusion, the blocking ratio gate on the executable
     surface, and the seeding dedup.
   - The release lane now runs `check-test-production-ratio` BLOCKING.
3. **#748 slice 2 — `surfaces_lib.match_surfaces` → native
   projection** (unlocked by the release): lane obligations already
   recorded in plan rev 2 "Deferred work" — binary-unavailability must
   raise a type distinct from `SurfaceError`
   (`staged_commit_gate_plan.py:230` swallow site,
   `boundary_probe_lib.py:132` propagate site are the named audits);
   consumer-path verification happens against the PUBLISHED artifact,
   not dev-tree.
4. **`repo_file_listing` decision**: investigate real
   `CHARNESS_SUPPORT_DIR` usage (who sets it outside
   `test_monorepo_layout.py`?), then choose absorb-into-native /
   keep-Python-with-recorded-reason / deprecate-the-splice. This
   decision closes #748 (with slice 2) or records its final boundary.
5. **#753 closeout**: one small lane for the audited follow-ups
   (convert-pin: `test_narrative_adapter.py`,
   `test_quality_tool_recommendations.py`; trim-partial: the 8 files
   listed in the JTBD artifact), then close #753 citing: island/orphan
   zero, JTBD 96.5% keep, ratio decomposition + executable-surface
   fix + blocking promotion, dedup 6.8%→3.8%, two verified prose-pin
   deletions, and the accepted remaining-corpus boundary.
6. **Queue after this session**: #749 (retained-Python role +
   type-checking boundary — its own session; inputs are now rich),
   then the smaller independents (#750, #751, #752, #731, #709).

## Non-claims

- This plan does not pick the release version number or notes wording;
  the release skill flow owns those with the operator.
- Slice 2 does not revisit `load_surfaces` validation,
  `path_matches_patterns`, or changed-path git acquisition — those
  stay Python with recorded reasons until #749 re-inventories.
- Nothing here reopens the #753 mutation-testing pass; the operator
  replaced it with the JTBD method and the issue closes on that
  record.
