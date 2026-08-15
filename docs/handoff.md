# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1 — the premise check over the next slice's scoped
  issues — and only then invoke `impl`. S1-S5 are committed; **S6** is next.

## Continuation Capability

- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md) — the owner-approved wide scope,
  its sequence, `## Owner Rulings`, and the findings carried forward rather than fixed.
- [S5 guard record](../charness-artifacts/audit/2026-08-15-s5-umbrella-guards.md) — each umbrella
  guard's re-runnable measurement, its stated remainder, and the review record.
- [Release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md) — prepared, and still **false for the tree
  they would ship**; S7 regenerates them, and the S1 gate refuses them until it does.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.
- [Docs graph checks](./docs-graph-checks.md) — what each docs tool answers, and the
  `link_only_lines` ratchet record S4 armed.
- [S4 retro](../charness-artifacts/retro/2026-08-15-session-retro-s4.md) — the sibling scan over
  this repo's other bars, and the stale-mirror suite loss.

## Current State

- **S5 is committed** (`git show 88256feba --no-patch --format=%B`): one executable guard
  per structural umbrella, each with its measurement and remainder in the
  [S5 guard record](../charness-artifacts/audit/2026-08-15-s5-umbrella-guards.md). The
  premise check changed the slice — two umbrellas' scoped members were already fixed — so
  three of four guards are CLASS guards. **No umbrella is closed.**
- The S5 measurement is a command, not prose:
  `python3 scripts/check_closeout_classification_parity.py --repo-root . --assume-classification superseded`
  turns every exact site red without editing the tree.
- **Round 2 again found defects IN round 1's repairs**, including one a repair CREATED and
  one it UNMASKED; round-2 repairs are accepted-unreviewed at the cap. Both, and the
  exposure that leaves, are owned by the
  [S5 guard record](../charness-artifacts/audit/2026-08-15-s5-umbrella-guards.md) `## Review record`.
- **S6b is ruled in and lands before S7**: this handoff prescribed a command far slower
  than the repo's own budgeted runner for identical scope, and nothing could refuse it.
  Scope and rationale live in `## Sequence` S6b of the
  [release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md), beside its ruling.
- Re-prove the suite with `python3 scripts/run_standing_pytest.py` — xdist-parallel,
  budgeted, blocking, and the same scope the raw `python3 -m pytest tests/` spelling
  covers at many times the cost. Do not edit under an open collection. Run
  `python3 scripts/sync_root_plugin_manifests.py` FIRST: the generated mirror is a repair
  surface, and a run begun before its re-sync burns a full cycle on `needs_sync` failures
  the re-sync had already fixed.
- Ruff is clean only cache-free: `ruff check --no-cache .`, never `ruff check .`.
- The release is still PREPARED: no bump, tag, or publish. Confirm with
  `python3 skills/public/release/scripts/current_release.py --repo-root .`.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#633](https://github.com/corca-ai/charness/issues/633):
  #620, #628, #617, #626, #627, #631, #629 are fixed in-repo and unreleased.
  [#633](https://github.com/corca-ai/charness/issues/633) is **scoped to S6 by owner
  ruling**. Still no checked-in classification ledger; the closeout floor requires one.

Non-claims: no push, tag, version bump, publish, hosted CI, installed-consumer readback,
or issue closure. S6, S6b, and S7 have not started. The exported docs-graph gate ships
this repo's own bar to consumers without the record or test that ratchet it; a consumer
calibrates with `--link-only-lines-bar`, and S7 owes that a release note alongside the
breaking `## References` rule.

## Next Session

1. **Before S6, confirm each scoped issue still reproduces on the current tree**
   (`gh issue view <id>`, then run the reproduction). The standing remedy; in S3, S4 and
   S5 it is what confirmed the items were live before any code moved — in S5 it found
   two umbrellas already fixed and rescoped the slice.
2. **S6**: worktree isolation for write-capable subagents (SC10, RULED as isolation not
   refusal), the monitored-phase path for long-running children, the exported
   `link_only_lines` bar default, and [#633](https://github.com/corca-ai/charness/issues/633).
   Read `## Owner Rulings` before scoping.
3. Then **S6b** (cost as a proof surface), then S7 publishes and closes
   [#608](https://github.com/corca-ai/charness/issues/608) and
   [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627);
   the classification ledger commits BEFORE the prepared release record.

## Discuss

- **Bars record a value but not a direction.** S4's sibling scan
  ([S4 retro](../charness-artifacts/retro/2026-08-15-session-retro-s4.md)) found two:
  `check_python_lengths.py`'s file caps and `validate_skill_ergonomics.py`'s inline
  `max_core_lines`, both raisable by one literal edit with the suite green. S6b extends
  the same ask to COST bars, whose drift is already recorded in
  [quality-adapter.yaml](../.agents/quality-adapter.yaml) as budgets that only moved up.
- **Review is aimed at falsity, so a dominated-but-true instruction passes.** That is why
  fresh-eye review did not catch this handoff's own prescribed command. S6b adds the
  angle; until it lands, ask "is there a cheaper path to the same evidence?" by hand.
- **Nothing checks whether an authored descriptor is TRUE.** The gate only checks a line
  is not bare. S4's were accepted on sampled verification by owner ruling, and a
  re-verification sweep is explicitly NOT owed — but future delegated authoring owes a
  verification step, and no surface enforces one yet.

## References

- [Design north star](./design-north-star.md) — P4, the different-observer rule, and the
  "teeth only where a wrong answer escapes" clause S6b argues cost was never held to.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique
  floor, which earned its keep again: round 2 caught defects in round 1's repairs.
- [Parallel execution](./conventions/parallel-execution.md) — the disjoint-writer rule
  the reviewer fan-out ran under, and the proof floor a fan-out still owes.
