# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1 — the premise check over S3's scoped issues —
  and only then invoke `impl` on slice **S3** of the release contract. S1 and S2
  are committed; S3 has not started.

## Continuation Capability

- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md)
  — the owner-approved wide scope, its S1-S7 sequence, and `## Owner Rulings`.
- [S2 retro](../charness-artifacts/retro/2026-08-15-session-retro-s2.md)
  — what S2 cost, and the measured claim that two review rounds were not one too
  many: round 2 found the round-1 repair carrying the class it repaired.
- [S1 retro](../charness-artifacts/retro/2026-08-15-session-retro.md)
  — the earlier slice, and the lesson-digest defect S3 inherits.
- [Contract critique](../charness-artifacts/critique/2026-08-15-release-scope-contract.md)
  — the findings behind the contract's revision 2.
- [Release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md)
  — prepared, and still **false for the tree they would ship**; S7 regenerates
  them, and the S1 gate refuses them until it does.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
  — the digest a session reads before work.

## Current State

- **S2 is committed.** Artifact scaffolds resolve their write path by SUBJECT
  IDENTITY: only a confirmed match writes in place, and a mismatch, an unreadable
  target subject, or an undeclared invocation all route somewhere that destroys
  nothing and report what was declined. `debug` gained `--subject`; the debug
  planner no longer routes a run into the record the scaffold declined. Identity
  and scope: `git show --stat f2ad8498b`.
- **The two red gates the owner assigned to S2 are green**, each in its own
  commit — `check-shell` cleared with no suppression, and twenty pre-existing
  duplicate families accepted into the revocable baseline rather than the
  permanent overlay: `git show --stat 7e2278e9c 87fce80fc`.
- **A THIRD pre-existing red was found and is cleared by this rewrite**:
  `python3 -m pytest tests/quality_gates/test_regenerable_facts.py -q` refused a
  transcribed count on this file, identically at `0f4f47b0c` on a throwaway
  worktree — so S1's "full suite green at that commit" was not true.
- Full suite GREEN at `a7e3bb636`: 9422 passed, 0 failed, 21m07s. Re-prove with
  `python3 -m pytest tests/ -q --no-header`, BACKGROUNDED, and do not edit under
  an open collection.
- Ruff is clean only cache-free: `ruff check --no-cache .`, never `ruff check .`.
- The release is still PREPARED: no bump, tag, or publish. Confirm with
  `python3 skills/public/release/scripts/current_release.py --repo-root .`.
- `plan_risk_interrupt.py` is still **blocked** on interrupt
  `lesson-presentation-compaction-2026-08-14`; this is S3's first item. Confirm
  with `python3 scripts/plan_risk_interrupt.py --repo-root .`.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#632](https://github.com/corca-ai/charness/issues/632):
  #620 and #628 are now fixed in-repo and unreleased.
  [#629](https://github.com/corca-ai/charness/issues/629) and
  [#631](https://github.com/corca-ai/charness/issues/631) are still broken. Still
  no checked-in classification ledger; the closeout floor requires one.

Non-claims: no push, tag, version bump, publish, hosted CI, installed-consumer
readback, or issue closure. S3-S7 have not started. **S2's round-2 repairs are
accepted-unreviewed** — the two-round cap was reached, and the code that fixes
round 2's blockers has not itself been read by a fresh reviewer.

## Next Session

1. **Before S3, confirm each scoped issue still reproduces on the current tree**
   (`gh issue view <id>`, then run the reproduction). The standing remedy; in S2
   it is what established that all three producer-scaffold instances were live.
2. **S3** of the release contract: the lesson loop. Refresh the #617 spec and
   close its debug interrupt, then the score outcome vocabulary, #631, #626,
   #627. Note that the debug scaffold now needs `--subject
   lesson-presentation-lost-across-compaction` to continue that open record —
   without it the run is treated as a new investigation, which is S2's fix
   working as designed on the very artifact S3 must continue.
3. Then S4-S6 in order, then S7 publishes and closes
   [#608](https://github.com/corca-ai/charness/issues/608) and
   [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627);
   the classification ledger commits BEFORE the prepared release record.

## Discuss

- **The digest injected at session open still shows completed focuses and drops
  the live one**, and this session inherited that unchanged from S1. Same family
  as S3's SC6 — the loop weights what RECURRED over what was just learned.
  Compare [recent lessons](../charness-artifacts/retro/recent-lessons.md) against
  `python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check`.
- **Four caps fired at the commit gate in S2, after the work was done**: Python
  file length twice, SKILL body length, SKILL core headroom. Each forced a real
  split or deletion, and each was knowable before implementation. Whether the
  authoring path should surface remaining headroom the way the scaffold surfaces
  `size_budget` is a `quality` question.
- S5 (structural umbrellas) is the least bounded slice; decide its stopping rule
  before starting it, not during.

## References

- [Design north star](./design-north-star.md) — the P4 rule S2 leaned on hardest:
  every pre-existing-red attribution came from a throwaway worktree at the older
  commit, not from a re-read.
- [Operating contract](./conventions/operating-contract.md) — the two-round
  critique floor, which earned its keep again: round 2 found the round-1 repair
  writing in place for the two states it had just introduced.
- [Parallel execution](./conventions/parallel-execution.md).
