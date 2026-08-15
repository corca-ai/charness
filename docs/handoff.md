# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1 — the premise check over the next slice's scoped
  items — and only then invoke `impl`. S1-S6b-1 are committed; **S6c** is next, and the
  remaining tail is `S6c -> S6b-2 -> S7`.

## Continuation Capability

- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md) — the owner-approved wide scope,
  its sequence, `## Owner Rulings`, each slice's review record, and the findings carried rather than fixed.
- [S6 retro](../charness-artifacts/retro/2026-08-15-session-retro-s6.md) — the trend line
  across S5 and S6, and the sibling scan that produced the next capability.
- [SC10 probe](../charness-artifacts/probe/2026-08-15-sc10-write-capable-worktree-isolation.json) — agent worktrees on this host, and the six things it does NOT establish.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique floor,
  the write-capable isolation rule, and the Claim Fidelity clause S6 skipped.
- [Docs graph checks](./docs-graph-checks.md) — the `link_only_lines` ratchet record the
  exported gate now reads, and how a consuming repo calibrates its own.

## Current State

- **S6b-1 is committed** — one classifier for coverage instrumentation, the closeout
  broad gate bound to it, `--test-command`, and the CI step on the standing runner; five
  reviewers over two rounds, and round 2 found the first executor repair had traded an
  uncaught crash for a SILENT green. Re-prove with
  `python3 -m pytest -q tests/quality_gates/test_coverage_builder_policy_parity.py`.
- **S6's changed-line proof is OBTAINED and now clean.** It completed rather than being
  killed, and found twelve unproven changed lines across five files before
  [these tests](../tests/quality_gates/test_s6_changed_line_gaps.py) closed them. Re-run:
  `python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha e12b41b52 --head-sha HEAD --test-command "python3 scripts/run_standing_pytest.py --repo-root ." --write-fresh-marker`.
- **S6 is committed** (`git show 54654b032 --no-patch --format=%B`): worktree isolation,
  the monitored standing runner, the exported bar default, and
  [#633](https://github.com/corca-ai/charness/issues/633). Six reviewers over two rounds;
  round-2 repairs and the `AGENTS.md` spawn rule ship accepted-unreviewed at the cap.
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
- [cosmic-ray.toml](../cosmic-ray.toml) still holds its bare-pytest `test-command` on
  purpose — cosmic-ray runs it per mutant, and it is SC17's subject in S6b-2.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#633](https://github.com/corca-ai/charness/issues/633):
  #620, #628, #617, #626, #627, #631, #629, #633 are fixed in-repo and unreleased.
  Still no checked-in classification ledger; the closeout floor requires one.

Non-claims: no push, tag, version bump, publish, hosted CI, installed-consumer readback,
or issue closure. S6c, S6b-2 and S7 have not started. The CI wiring that now passes the
standing runner to the changed-line step has NOT run on hosted CI — it is proven locally
only.

## Next Session

1. **Before each slice, confirm its scoped items still reproduce on the current tree**
   (`gh issue view <id>`, then run the reproduction). The standing remedy; in S3-S6 it is
   what confirmed items were live before code moved — in S6 it rescoped the largest one.
2. **S6c ([#634](https://github.com/corca-ai/charness/issues/634))**: export completeness, detector before repairs. It is
   RELEASE-BLOCKING — a new consumer installing the prepared release hits an unguarded
   `import yaml` from a documented entrypoint. Work from the inventory on the issue.
3. **S6b-2** (SC14, 15, 16, 17, 19 in the [release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md)): the rest of cost, which needs S6c's detector first so
   its consumer half ships verifiably rather than reproducing the class it fixes.
   S6b-1's carried remainder belongs here: `sample_mutation_files.py` still spawns the
   dominated serial coverage probe, and the broad gate matches the runner token anywhere
   while the coverage classifier is anchored at the start.
4. Then **S7** publishes and closes [#608](https://github.com/corca-ai/charness/issues/608) and
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
