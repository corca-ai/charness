# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1 — the premise check over S5's scoped issues —
  and only then invoke `impl` on slice **S5** of the release contract. S1-S4 are
  committed; S5 has not started.

## Continuation Capability

- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md) — the owner-approved wide scope,
  its S1-S7 sequence, `## Owner Rulings`, and the findings carried forward
  rather than fixed.
- [S2 retro](../charness-artifacts/retro/2026-08-15-session-retro-s2.md) — the measured claim that two review rounds
  were not one too many.
- [Release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md) — prepared, and still **false for the tree
  they would ship**; S7 regenerates them, and the S1 gate refuses them until it does.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.
- [Docs graph checks](./docs-graph-checks.md) — what each docs tool answers, and the
  `link_only_lines` ratchet record S4 armed.

## Current State

- **S4 is committed.** `check_docs_graph.py` judges named metrics against
  declared bars instead of `> 0`, `link_only_lines` among them at a ratchet the
  tests parse from a dated record; the handoff scaffold and validator now require
  a `## References` descriptor on the link's own line. Scope: `git show --stat HEAD`.
- **The docs repair was real work, not a re-baseline.** Every list entry in
  `docs/` whose link line carried no descriptor was rewritten to carry one; the
  bar is sized to the hard-wrapped-prose remainder, which is the population
  awiki's per-physical-line rule over-reports on. Recount with
  `python3 scripts/check_docs_graph.py --repo-root .`.
- **Two review rounds ran, and round 2 found defects in round 1's repairs** —
  including a ratchet whose "may only decrease" was satisfiable by two in-place
  edits, and a `## References` rule that scanned to end of file. Round-2 repairs
  are themselves unreviewed, which is where the cap stopped the loop.
  Record: `git show HEAD --no-patch --format=%B`.
- **One false claim was authored and caught in S4** — "two independent channels
  that agreed exactly", describing the gate shelling out to `awiki` and
  regex-reading its own stdout, which is one observer read twice. It reached
  three surfaces before a bounded reviewer refuted it; the corrected statement
  and what replaced it live in the
  [release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md).
- Ruff is clean only cache-free: `ruff check --no-cache .`, never `ruff check .`.
- Re-prove the suite with `python3 -m pytest tests/ -q --no-header`, BACKGROUNDED,
  and do not edit under an open collection. A suite run started before a repair
  does not prove the tree after it — in S4 a run begun before a mirror re-sync
  reported packaging failures that the re-sync had already fixed.
- The release is still PREPARED: no bump, tag, or publish. Confirm with
  `python3 skills/public/release/scripts/current_release.py --repo-root .`.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#633](https://github.com/corca-ai/charness/issues/633):
  #620, #628, #617, #626, #627, #631 and now
  [#629](https://github.com/corca-ai/charness/issues/629) are fixed in-repo and
  unreleased. [#633](https://github.com/corca-ai/charness/issues/633) is **scoped
  to S6 by owner ruling** — it lands before S7 publishes. Still no checked-in
  classification ledger; the closeout floor requires one.

Non-claims: no push, tag, version bump, publish, hosted CI, installed-consumer
readback, or issue closure. S5-S7 have not started. The exported gate ships this
repo's own bar to consumers without the record or test that ratchet it; a
consumer calibrates with `--link-only-lines-bar`, and S7 owes that a release note
alongside the breaking `## References` rule.

## Next Session

1. **Before S5, confirm each scoped issue still reproduces on the current tree**
   (`gh issue view <id>`, then run the reproduction). The standing remedy; in S3
   and S4 it is what confirmed the items were live before any code moved.
2. **S5** of the release contract: the structural umbrellas, #586 then #584,
   #583, #582. Decide the stopping rule BEFORE starting — the contract's probe
   question ("land one executable guard per umbrella, measure what it catches,
   defer the rest with the measurement attached") is that rule, and S5 is the
   least bounded slice in the release.
3. Then S6 — which also carries
   [#633](https://github.com/corca-ai/charness/issues/633) — then S7 publishes and closes
   [#608](https://github.com/corca-ai/charness/issues/608) and
   [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627);
   the classification ledger commits BEFORE the prepared release record.

## Discuss

- **A ratchet is only as strong as the surface that records it.** S4's first
  ratchet repair read as executable and was not; round 2 measured that a raise
  needed two in-place edits and no test change. Whether this repo's other bars
  and floors have the same shape is a `quality` question worth one sweep.
- **The exported gate carries a bar calibrated on this repo's docs.** Consumers
  get a number measured somewhere else, with neither the record nor the test that
  governs it. The `--link-only-lines-bar` flag makes it expressible; whether
  repo-calibrated thresholds should ship as defaults at all is the open question.
- **Delegated authoring needs its own proof floor.** S4's descriptors were
  written by parallel subagents over disjoint files and spot-checked, not
  independently verified line by line; a bounded reviewer checked roughly half.

## References

- [Design north star](./design-north-star.md) — P4, the different-observer rule that
  refuted this slice's own corroboration claim.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique
  floor, which earned its keep again: round 2 caught defects in round 1's repairs.
- [Parallel execution](./conventions/parallel-execution.md) — the disjoint-writer rule
  the docs fan-out ran under, and the proof floor a fan-out still owes.
