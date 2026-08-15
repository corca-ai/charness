# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1 — the premise check over the next slice's scoped
  items — and only then invoke `impl`. S1-S6 are committed; **S6b-1** is next, and the
  tail was resequenced to `S6b-1 -> S6c -> S6b-2 -> S7`.

## Continuation Capability

- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md) — the owner-approved wide scope,
  its sequence, `## Owner Rulings`, each slice's review record, and the findings carried rather than fixed.
- [S6 retro](../charness-artifacts/retro/2026-08-15-session-retro-s6.md) — the trend line
  across S5 and S6, and the sibling scan that produced the next capability.
- [SC10 probe](../charness-artifacts/probe/2026-08-15-sc10-write-capable-worktree-isolation.json) — what this
  host does with agent worktrees, and the six things it does NOT establish.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique floor,
  the write-capable isolation rule, and the Claim Fidelity clause S6 skipped.
- [Docs graph checks](./docs-graph-checks.md) — the `link_only_lines` ratchet record the
  exported gate now reads, and how a consuming repo calibrates its own.

## Current State

- **S6 is committed** (`git show 54654b032 --no-patch --format=%B`): worktree isolation,
  the monitored standing runner, the exported bar default, and
  [#633](https://github.com/corca-ai/charness/issues/633). Six reviewers over two rounds;
  round 1 found two blockers that INVERTED their item's intent, round 2 two more that
  reproduced the fixed class. Round-2 repairs and the `AGENTS.md` spawn rule ship
  accepted-unreviewed at the cap.
- Re-prove the suite with `python3 scripts/run_standing_pytest.py` — xdist-parallel,
  budgeted, blocking. Run `python3 scripts/sync_root_plugin_manifests.py` FIRST: the
  generated mirror is a repair surface, and a run begun before its re-sync burns a cycle.
- Ruff is clean only cache-free: `ruff check --no-cache .`, never `ruff check .`.
- The release is still PREPARED: no bump, tag, or publish. Confirm with
  `python3 skills/public/release/scripts/current_release.py --repo-root .`.
- [#634](https://github.com/corca-ai/charness/issues/634) holds a measured export-completeness inventory: 25 exported files
  `import yaml` unguarded (one a documented `gather` entrypoint), the packaging validator
  uses the exporter as its own oracle so it is green BY the defect's cause, and
  `check_export_safe_imports.py` already has the right AST shape with a `skills/public`-only
  constant. Scoped as S6c; its SC20 negative case and the
  [repo-copy fixture](../tests/repo_copy.py) trap are in the contract.
- **The cost seam that recurred is code and config, not a document**:
  [cosmic-ray.toml](../cosmic-ray.toml) holds a bare-pytest `test-command`,
  `mutation_sampling_lib.coverage_run_command` refuses the standing runner, and its
  sibling `mutation_coverage_producer.instrument_broad_command` accepts it. SC18 is the
  reconcile; run `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root .`
  only for suite SHAPE — it does not answer command dominance.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#633](https://github.com/corca-ai/charness/issues/633):
  #620, #628, #617, #626, #627, #631, #629, #633 are fixed in-repo and unreleased.
  Still no checked-in classification ledger; the closeout floor requires one.

Non-claims: no push, tag, version bump, publish, hosted CI, installed-consumer readback,
or issue closure. S6b-1, S6c, S6b-2 and S7 have not started. S6's changed-line mutation
proof is UNOBTAINED — the run was killed at 25 minutes as dominated, not completed, and
SC18 exists so the retry is affordable.

## Next Session

1. **Before each slice, confirm its scoped items still reproduce on the current tree**
   (`gh issue view <id>`, then run the reproduction). The standing remedy; in S3-S6 it is
   what confirmed items were live before code moved — in S6 it rescoped the largest one.
2. **S6b-1 (SC18)** in the [release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md): give the two coverage builders ONE policy on the
   standing runner, then re-obtain S6's changed-line proof, which is still unobtained
   because that gate spawns serial bare pytest. Smallest item in the release and the one
   that makes every later slice cheaper to prove — which is why it moved first.
3. **S6c ([#634](https://github.com/corca-ai/charness/issues/634))**: export completeness, detector before repairs. It is
   RELEASE-BLOCKING — a new consumer installing the prepared release hits an unguarded
   `import yaml` from a documented entrypoint. Work from the inventory on the issue.
4. **S6b-2** (SC14, 15, 16, 17, 19 in the [release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md)): the rest of cost, which needs S6c's detector first so
   its consumer half ships verifiably rather than reproducing the class it fixes.
5. Then **S7** publishes and closes [#608](https://github.com/corca-ai/charness/issues/608) and
   [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627);
   the classification ledger commits BEFORE the prepared release record, and S7's
   release-note obligations are listed in the contract's S7 entry.

## Discuss

- **This repo writes correct rules and gives them no carrier.** S5's waste was a detector
  whose `disposition: file-issue` nobody was obliged to file; S6's was a Claim Fidelity
  clause nobody was obliged to run, which cost a round-2 blocker. #634 is the same shape
  at the artifact level. The S6 retro's next-improvement is a `capability`, not another
  sentence — but nothing has built it yet.
- **A test written to close a blocker should be watched failing first.** S6 nearly shipped
  a process-kill test that asserted nothing because its marker landed after the assertion
  window; a two-minute probe caught it. Habit, not rule.
- **Nothing checks whether an authored descriptor is TRUE.** The gate only checks a line
  is not bare. Future delegated authoring owes a verification step; no surface enforces one.

## References

- [Design north star](./design-north-star.md) — P4, the different-observer rule that earned
  every blocker this session.
- [Parallel execution](./conventions/parallel-execution.md) — the disjoint-writer rule the
  reviewer fan-out ran under, and the proof floor a fan-out still owes.
- [Implementation discipline](./conventions/implementation-discipline.md) — the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
