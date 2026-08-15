# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1 — the premise check over S4's scoped issues —
  and only then invoke `impl` on slice **S4** of the release contract. S1-S3 are
  committed; S4 has not started.

## Continuation Capability

- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md)
  — the owner-approved wide scope, its S1-S7 sequence, `## Owner Rulings`, and
  the S3 findings carried forward rather than fixed.
- [S2 retro](../charness-artifacts/retro/2026-08-15-session-retro-s2.md)
  — the measured claim that two review rounds were not one too many.
- [Release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md)
  — prepared, and still **false for the tree they would ship**; S7 regenerates
  them, and the S1 gate refuses them until it does.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
  — the digest a session reads before work.

## Current State

- **S3 is committed** (`34c5f4ec1`). The lesson score is a typed outcome, not a
  signed scalar; scoring cites the retro RECORDING the encounter rather than the
  lesson's origin; `render_lesson_lifecycle_review` emits runnable archive,
  resurrect, and graduation commands; the tenth presentation slot is filled
  again. Ledger schema 5 -> 6, selection policy 2 -> 3. Scope: `git show --stat 34c5f4ec1`.
- **THREE review rounds ran** — the owner overrode the two-round cap — finding
  11, 9, and 9 blockers. All three windows verified clean. Round 3 was
  mutation-driven and found seven claims with no test that would fail; its
  repairs are themselves unreviewed, which is where the loop was stopped.
  Record: `git show 34c5f4ec1 7817ace88 --no-patch --format=%B`.
- **Four false prose claims were written and caught in S3** — the class this
  release exists to prevent, committed inside it. Each is now stated as measured
  beside the refuted version; the S3 entry and carried-findings list in the
  [release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md)
  own the detail.
- Full suite GREEN at `7817ace88`: 9446 passed, 0 failed, 21m12s. Re-prove with
  `python3 -m pytest tests/ -q --no-header`, BACKGROUNDED, and do not edit under
  an open collection. A suite run started before a repair does not prove the tree
  after it.
- Ruff is clean only cache-free: `ruff check --no-cache .`, never `ruff check .`.
- The release is still PREPARED: no bump, tag, or publish. Confirm with
  `python3 skills/public/release/scripts/current_release.py --repo-root .`.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#633](https://github.com/corca-ai/charness/issues/633):
  #620, #628, #617, #626, #627, #631 are fixed in-repo and unreleased.
  [#629](https://github.com/corca-ai/charness/issues/629) is still broken and is
  S4's first item. [#633](https://github.com/corca-ai/charness/issues/633) was
  filed during S3 and is **scoped to S6 by owner ruling** — it lands before S7
  publishes. Still no checked-in classification ledger; the closeout floor
  requires one.

Non-claims: no push, tag, version bump, publish, hosted CI, installed-consumer
readback, or issue closure. S4-S7 have not started. `foreign-score-source` is
currently INERT on this repo's corpus — all 12 committed score events are
legacy-scalar and legacy is exempt by design; it arms when the first outcome
event lands — which it now has: four encounters are recorded and the gate reads
them clean.

## Next Session

1. **Before S4, confirm each scoped issue still reproduces on the current tree**
   (`gh issue view <id>`, then run the reproduction). The standing remedy; in S3
   it is what confirmed all four items were live before any code moved.
2. **S4** of the release contract: the docs graph. #629 at the handoff scaffold,
   then this repo's own `link_only_lines` count, then make `check_docs_graph.py`
   gate it. Read the contract's Constraints entry FIRST — S4 is larger than
   "assert the count it already parses", and it REVERSES a deliberately pinned
   decision at `tests/test_docs_graph_gate.py:168-170`, which must be retracted
   explicitly the way S3 retracted the archive-slot pin.
3. Then S5, then S6 — which now also carries
   [#633](https://github.com/corca-ai/charness/issues/633) — then S7 publishes and closes
   [#608](https://github.com/corca-ai/charness/issues/608) and
   [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627);
   the classification ledger commits BEFORE the prepared release record.

## Discuss

- **Three review rounds found 29 blockers.** That yield is a signal about the
  process upstream, not just about review: four false quantities were AUTHORED
  where S1 already built derivation for the one surface (release notes) that has
  it. Whether that containment should cover specs, comments, and contracts is the
  `quality` question this slice earned. See the S3 retro's Expert Counterfactuals.
- **Caps and ratchets fired at the commit gate again, after the work was done** —
  the Python file-length cap and the boundary-bypass ratchet. Length headroom WAS
  measured up front this time (794 of 800) and then spent by a review repair
  without re-checking. Whether the authoring path should surface remaining
  headroom continuously, not once, is a `quality` question.
- **S5 (structural umbrellas) is the least bounded slice**; decide its stopping
  rule before starting it, not during.

## References

- [Design north star](./design-north-star.md) — the P4 rule S3 leaned on: every
  disputed fact was re-measured from the ledger and git before the prose was
  rewritten, not re-read from the sentence that made the claim.
- [Operating contract](./conventions/operating-contract.md) — the two-round
  critique floor, which earned its keep a third time: round 2 caught three
  repairs carrying the class they repaired.
- [Parallel execution](./conventions/parallel-execution.md).
