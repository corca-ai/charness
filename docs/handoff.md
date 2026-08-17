# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <date-slug>`
  BEFORE any brief or reviewer spawn. `--session-id` and `--seed` are both required and
  take the SAME value, so the selection is reproducible and citable. The command now
  prints the frozen bundle path on stderr; cite it in this session's durable artifact.
- Then run `## Next Session` item 1.

## Continuation Capability

- The [last session retro](../charness-artifacts/retro/2026-08-17-612-and-the-uncounted-count.md)
  carries five anchored lesson scores and the three-count defect this session repeated.
- The digest a session reads before work is [recent lessons](../charness-artifacts/retro/recent-lessons.md).

## Current State

- **#612's blocking signal is closed; the lane is NOT proven green.**
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha 1c1acd9`
  exits 4 (PARTIAL): every MAPPED file's changed lines are covered, and 24 unmapped
  files were never judged. Mutation CI samples on a fresh seed each run.
- **The mutation lane does not run on push.** [mutation-tests.yml](../.github/workflows/mutation-tests.yml)
  fires on `schedule` (`17 */12 * * *`) and `workflow_dispatch` only, and it holds
  `issues: write`, so a manual dispatch can file or update an issue.
- **Quality Core failed on `1240348b7` in the push mirror, and the cause is not in that
  commit.** Four tests failed there (three in [doc authoring preflight](../tests/test_doc_authoring_preflight.py),
  one in [mutate and restore](../tests/quality_gates/test_mutate_and_restore.py)); all 92 pass locally, the failures read as markdownlint
  resolving to nothing in CI, and no failing test's subject was touched. Suspected the
  registry-dependent `npm exec` path in
  [#630](https://github.com/corca-ai/charness/issues/630). Confirm against the run on
  `5db3df78a` before treating it as flaky.
- **A proof-surface slice now costs two review rounds and finds defects in both.**
  Round 2 found the class inside round 1's repair again, 6/6 for this repo. The floor is
  in [operating contract](./conventions/operating-contract.md) Critique Discipline, and
  the [session retro](../charness-artifacts/retro/2026-08-17-612-and-the-uncounted-count.md)
  records both instances with the reviewer findings that produced them.
- **[#617](https://github.com/corca-ai/charness/issues/617) is closed; its third surface
  is not done.** The command and retro reference the bundle; the work workflow does not,
  filed as [#635](https://github.com/corca-ai/charness/issues/635).
- Re-prove with `python3 scripts/run_standing_pytest.py` after
  `python3 scripts/sync_root_plugin_manifests.py`, then
  `python3 -m ruff check --no-cache scripts skills tests`, then `-m release_only`.
- **COMMIT the slice, THEN run the changed-line proof** —
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  reads `base..HEAD`, so a dirty pool proves nothing. Run it BEFORE the broad lane.

## Next Session

1. **Confirm or refute the CI flake** named in `## Current State` before any new slice;
   a red main that nobody owns is worse than a known-red one.
2. **Verify-and-close sweep for [#633](https://github.com/corca-ai/charness/issues/633),
   [#631](https://github.com/corca-ai/charness/issues/631),
   [#632](https://github.com/corca-ai/charness/issues/632), and
   [#630](https://github.com/corca-ai/charness/issues/630).** All four look repaired in
   main but are still open. #617's closeout is the worked template: run each issue's own
   reproduction, then the closeout floor. Do NOT close on code that merely looks right —
   the #617 reviewer refused exactly that premise.
3. **Follow-up `export-instruction-spellings`.** The arm matches ONE spelling. Live
   misses include the dot-slash and `bash`-prefixed forms in the quality skill's
   [catalog](../skills/public/quality/references/catalog.yaml); `.sh` and `.mjs` are unscanned.
4. **Follow-up `executed-field-declaration`.** Declare executed adapter fields the way
   [resolve_adapter.py](../skills/public/release/scripts/resolve_adapter.py) already does
   with `EXECUTED_COMMAND_FIELDS`, so a classifier can key on the FIELD, not the file type.
5. **[#546](https://github.com/corca-ai/charness/issues/546) residual** — separating
   "legitimately conditional" from "abandoned behind an opt-in" still needs an
   adapter-declared expectation; a prior repair was measured defective and reverted.

## Discuss

- **Nothing asks "was this counted?"** Three unenumerated counts landed in durable
  artifacts this session, one transcribed from another artifact and asserted as an own
  measurement. Is that a validator question or only a lesson?
- **`release_only` is invisible to the gate.** The coverage producer runs
  `-m 'not release_only'`, so any refusal proven solely there is unmeasured. Two lines
  read as uncovered for exactly this reason. Widen the producer, or accept and document?
- **This bullet IS an SC14 anchor — do not tidy it away.** The
  [dominance test](../tests/quality_gates/test_command_dominance.py) substitutes into the
  real handoff and needs the bare backticked `python3 scripts/run_standing_pytest.py`, with no flags inside
  the backticks, present here.

## References

- The [design north star](./design-north-star.md) holds the different-observer rule and
  the proof-surface reading of the irreversible boundary.
- The [operating contract](./conventions/operating-contract.md) holds the two-round
  critique floor and the write-capable isolation rule.
- [Implementation discipline](./conventions/implementation-discipline.md) holds the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
