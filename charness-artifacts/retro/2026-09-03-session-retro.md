# Session Retro

Date: 2026-09-03

## Context

Goal Run #765, third session, second half: #770 scripts-packaging from the
first foundation lane to the pushed closeout (`ff71dc9a9`) and the cursor at
#772. Five Codex lanes (P0 foundation, P1 to P4 package moves) produced the
moves; the parent integrated them by cherry-pick with a rename-aware conflict
resolver and a cumulative rename sweep, then spent the larger part of the
window reconciling the packaged tree to green. What matters next is #772, the
integrated closeout, which starts from a tree whose standing pytest and full
read-only lane are both green.

## Window

`c6477cefb` (#769 push, 23:35) to `235f3abf6` (cursor at #772, 04:21):
32 commits, of which 5 are lane candidates, 4 are integration commits, and the
rest are P0 follow-ups, the closeout, and the goal-run records.

## Evidence Summary

- `charness-artifacts/goal-runs/765/2026-09-02-session-record.md` (the #770
  paragraph and the lessons list), `briefs/map-770.md` section 0 (the four
  stale premises).
- Integration commit sizes: `a2fff8c52` 9 files, `77b13c795` 10 files,
  `5866235e6` 319 files, `71784f289` 72 files. The two large ones are the
  reconciliation, not the moves.
- Gate evidence: full standing pytest 8592 passed; `./scripts/run-quality.sh
  --full --read-only` 80 passed on the parent and 79 on the clean clone;
  `tools/snapshot_gate_universes.py` against
  `charness-artifacts/quality/2026-09-02-gate-universes-before-770.yaml`
  identical by basename except the one test module split in this session.
- No adapter `metrics_commands`; this retro is narrative with the counts above.

## Waste

- **A stale green.** A full bare pytest run reported 8568 passed early in the
  reconciliation; later family-level reruns were trusted against that number
  while the standing runner still had 31 failures and one collection error. The
  runner is the only shape the lane runs, and the bare result was from an
  older tree. About one hour went to re-deriving failures that one standing
  run would have listed at once.
- **The sweep rewrote strings it did not own.** The cumulative rename sweep
  rewrote `$SKILL_DIR/../quality/scripts/suggest_public_skill_dogfood.py` and
  `shared/scripts/plan_risk_interrupt.py` inside the skill-contract checker,
  the critique scaffold's validator names, and a test expectation for an
  immutable 2026-08-12 snapshot. Each looked like a repo path and was not.
  Five repairs, found one gate at a time.
- **Root derivations the map named but the sweep could not see.** Map premise
  3 said `parent.parent` root arithmetic breaks for nested files. Imports were
  swept; the arithmetic in `_scaffold_rel`, `_plugin_schema_source`, and the
  quality skill's `load_repo_script_module` was not, and each surfaced as a
  distinct test failure after the moves.
- **Seeded fixtures were not a declared universe.** Dozens of tests copy repo
  scripts into a temp repo by flat path. No brief listed them, so every P-lane
  left them for the parent; `seed_script_closure` was written mid-reconciliation.

## Critical Decisions

- Rename `packaging` to `plugin_export` and `coverage` to `mutation` before
  landing, because both shadowed installed distributions (map section 0).
- Give every repo script, flat residue included, the same ten-line
  root-walking shim and exclude the shim from the length gate, instead of a
  raising shim for nested files only. Flat residue imports packaged siblings,
  so the exception would have been the rule.
- Report a `moved-path-referent` instead of editing frozen artifacts: a path
  that existed at the record's last commit is reported, not blocking.
- Keep consumer-facing names bare and make the lookups package-aware
  (`_repo_script`, `present_gate`, `load_repo_script_module`), instead of
  spelling packages into scaffolds, contracts, and consumer commands.
- Push from a clean clone with the hook lane, then confirm with
  `verify-closeout` reading GitHub state, as in the two earlier closeouts.

## North Star Alignment

- P4 held at the boundary: the push ran the full lane in a clean clone, and the
  closeout claim was re-examined by `verify-closeout` reading the backend, a
  different channel from the parent's lane.
- P2 held on the length gate: the shim is identical boilerplate in every file,
  so excluding it measures the file's own concept; no body was shaved. The
  test split (`test_changed_line_mutation_coverage_worktree.py`) separated a
  concept rather than trimming one.
- P1 was walked past once: the stale green above treated a proxy from an older
  tree as the current state. That is the "re-reading the same proxy" signature
  applied to a reversible surface; cheap here, but the habit is the one P4
  forbids at cliffs.
- Count was not used as the metric: the closeout cites seventeen packages and
  322 renames as figures, and the success claim rests on gate-universe parity
  and the two green lanes.

## Trends vs Last Retro

The 2026-09-02 retro's `verification-shape-mismatch` lesson (verify in the
shape production uses) recurred in a new form: this time the mismatch was
bare pytest versus the standing runner, not package versus flat imports. Its
`derived-surface-batching` lesson held: the mirror was regenerated before every
full lane and never produced a false red. The `.agents` sandbox and
collection-set bisect items did not recur and were kept out of briefs as
instructed.

## Expert Counterfactuals

- Engelbart, system-improving-itself (briefed lens): the sweep was a tool
  designed apart from the process it served. Treating the rename map, the
  layout resolver, and the tests as one unit would have produced a single
  resolver (`scripts/core/repo_layout.py` already owns tree-root paths) that
  the sweep, the scaffolds, the plan helper, and the seeding support all
  call, instead of four package-aware lookups written independently in one
  session. The sweep would then have been a consumer of the resolver, not a
  regex over strings, and could not have rewritten a skill-tree path.
- Direct lens, migration engineer: run the standing runner, and only it, as
  the truth after every integration step; a family rerun answers "did this
  fix land", never "is the tree green".

## Next Improvements

- **workflow — `recurs:` one runner, one truth.** After any integration step,
  the only green that counts is `run_standing_pytest.py` followed by the full
  read-only lane; family reruns are for locating, not for claiming. Structural
  pattern: a proxy from an older tree read as the current state. Triggering
  instance(s): the 8568-pass bare run trusted over the runner's 31 failures.
  (recurrence-class: verification-shape-mismatch)
- **capability — `novel:` one layout resolver.** Fold `_repo_script`
  (scaffold_artifact_lib), `_packaged_script`/`_seed_path` (seeding_support),
  `load_repo_script_module` (public_spec_adapter_policy), and `present_gate`
  (staged plan helpers) onto one resolver beside `scripts/core/repo_layout.py`
  that answers "where does repo script X live" for flat and packaged layouts.
  Destination: #772 integrated-closeout, as a follow-up item in its brief.
  Structural pattern: the same layout question answered independently in four
  places. Triggering instance(s): the four lookups above, all written this
  session. (recurrence-class: layout-oracle-duplication)
- **workflow — `novel:` a sweep owns only repo paths.** A rename sweep must
  skip `$SKILL_DIR`-relative strings, `skills/**` trees, contract-checker
  snippets, and any test expectation for a hash-bound artifact; add those to
  the sweep's exclusion set before the next path migration. Structural
  pattern: a text rewrite applied past the layout it models. Triggering
  instance(s): the two contract snippets, the critique validator names, the
  2026-08-12 snapshot expectation. (recurrence-class: sweep-overreach)
- **memory — `recurs:` briefs list the seeded-fixture universe.** Any brief
  that moves files names the tests that copy those files by path (`grep -rn
  'ROOT / "scripts"' tests`) as a deliverable of the lane, not of the parent.
  (recurrence-class: lane-brief-omits-parent-owned-surfaces)

## Sibling Search

- same layer: other ad-hoc "flat or packaged" lookups | decision: valid
  follow-up outside the slice | proof: `grep -rln 'glob(f"*/{' scripts skills
  tools tests` names exactly `scripts/core/scaffold_artifact_lib.py` and
  `skills/public/quality/scripts/public_spec_adapter_policy.py`, plus
  `_packaged_script` in `tests/quality_gates/seeding_support.py`; follow-up:
  deferred `2026-09-02-session-record.md#next-session-in-order` (#772 brief
  carries the resolver item).
- abstraction up: `parent.parent` root arithmetic in skill scripts | decision:
  diagnostic-only | proof: `grep -rn "resolve().parent.parent /" skills` after
  the fixes returns zero sites outside `$SKILL_DIR` resolution.
- specialization down: skill-tree strings still naming a package path |
  decision: same waste, fix now | proof: `grep -rn 'SKILL_DIR[^`]*scripts/(gates|core|adapters|gates_support|review)/' skills docs tools`
  returns zero after `71784f289`.
- mental-model siblings: any other immutable, hash-bound artifact whose test
  expectation the sweep may touch | decision: valid follow-up outside the
  slice | proof: the 2026-08-12 marker-rule snapshot was the one hit this
  session and its expectation now carries `sweep-keep`; follow-up: deferred
  `2026-09-02-session-record.md#next-session-in-order` (sweep exclusion set,
  workflow bullet above).

## Portable Candidate

- abstract pattern: a path-rename sweep needs a layout oracle it consumes, not
  a regex it owns; otherwise it rewrites strings outside the layout it models.
- triggering evidence: five sweep overreaches in one migration, each found by
  a different gate.
- intended consumer/repo shape: any repo migrating a flat script directory
  into packages while shipping some of those scripts to consumers.
- destination: not portable — the exclusion set is a property of this repo's
  export and skill layout; the fix is the repo-local resolver above.
- first-prompt acceptance claim: n/a.

## Packet Consumed

n/a (no adapter sections)

## Persisted

Persisted: yes: charness-artifacts/retro/2026-09-03-session-retro.md
