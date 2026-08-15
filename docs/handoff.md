# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1 and only then invoke the workflow it names.
  S1-S6c, S6b-2 and **S7's preparation** are committed, both review rounds run.

## Continuation Capability

- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md) — the owner-approved wide scope,
  its sequence, `## Owner Rulings`, the S7 entry's "What S7 MEASURED" block, and the findings carried rather than fixed.
- [S7 release critique](../charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md) — both rounds' findings,
  F1-F30 and G1-G14, and the per-issue premise verdicts the closeout ledger binds to.
- [Closeout ledger](../charness-artifacts/issue/2026-08-16-6-0-0-closeout-ledger.md) — the `bug` carrier body for
  #618-#627, whose `Jtbd:` names the five narrowed closes clause by clause.
- [S7 retro](../charness-artifacts/retro/2026-08-16-s7-6-0-0-release.md) — the three red-at-HEAD gates, the stash that
  cost a quality run, and the blast-radius lesson a wrong repair earned.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique floor,
  the write-capable isolation rule, and the Claim Fidelity clause S6 skipped.

## Current State

- **The release is PREPARED, not published.** The packaging manifest still carries
  the previous version; read both it and the target with
  `python3 skills/public/release/scripts/current_release.py --repo-root .`.
- **The notes are generated over the final tree and gated clean.** Re-prove:
  `python3 skills/public/release/scripts/generate_release_notes.py --repo-root . --notes-file charness-artifacts/release/2026-08-16-v6.0.0-notes.md --check --version v6.0.0`.
- **Three gates were RED AT HEAD before S7 and are repaired here** — `check-markdown`
  (MD040 on markdown S6b-2 introduced), `check-python-lengths` (the dominance owner
  split into registry/carriers), and `check-boundary-bypass-ratchet` (two crossings
  exempted with their own recorded reasons). Re-prove with `./scripts/run-quality.sh --release`.
- **Four publish-path defects are repaired**, the worst being a resume lane that could
  not classify its own artifact commit and so had no recovery after a pushed tag. All
  are G1-G14 in the [S7 release critique](../charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md).
- **The close set is SPLIT**: #618-#627 close as `bug` through the release carrier,
  #608 closes separately afterwards as `feature`. The release CLI applies one
  classification to every number and the eleven do not share one.
- Re-prove the suite with `python3 scripts/run_standing_pytest.py`; add
  `--include-release-only` for the release-marked tests.
  Run `python3 scripts/sync_root_plugin_manifests.py` FIRST; the generated mirror is a
  repair surface, and a run begun before its re-sync burns a cycle.
- Ruff is clean only cache-free: `ruff check --no-cache .`, never `ruff check .`.
- [#634](https://github.com/corca-ai/charness/issues/634) STAYS OPEN, and so do
  #628/#629/#630/#631 with their dispositions recorded in the contract's S7 entry.

Non-claims: no push, tag, version bump, publish, hosted CI, installed-consumer
readback, or issue closure at the time this was written. Round-2 repairs ship
accepted-unreviewed at the two-round cap. The changed-line proof over S7's own
changed lines is NOT yet obtained — the gate refuses a dirty pool, so it runs after
the preparation commit.

## Next Session

1. **Obtain the changed-line proof over S7's commit** before anything else:
   `python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha 6416e7023 --head-sha HEAD --test-command "python3 scripts/run_standing_pytest.py --repo-root ."`.
   Close whatever it reports, then re-run the release quality lane.
2. **Publish**: `--execute` to the prepared stop, commit the claims-review artifact as
   the DIRECT child of that record, `--resume`. Pass `--notes-file charness-artifacts/release/2026-08-16-v6.0.0-notes.md`
   on BOTH lanes and write down the prepared and claims-record shas before starting.
3. **Close #608 separately** as `feature` through the `issue` skill, against the same
   critique artifact, after the publish.
4. Run the adapter's real-host checklist (`charness update`, `charness doctor`, the
   `nose` tool arms) and record its output as executed proof.

## Discuss

- **Three consecutive slices recorded "gates clean" while three gates were red.**
  The claim is written from memory rather than from a receipt. A closeout that
  cannot state it without citing the run would have caught all three at the slice
  that introduced them, not at the release.
- **A repair to a text-scanning gate needs a blast-radius measurement**, not just the
  case that motivated it. This session's quote-awareness fix corrected one wrong
  carrier and silently dropped the flags of ~130 correct ones, cutting a blocking
  gate's probe count by 17% until a reviewer noticed the number.
- **Two more compensating claims.** A docstring asserting "one reader" while a second
  reader kept the defective spelling, and a critique asserting residuals were "stated
  in the ledger" when the ledger carried none. Both made a pair of documents
  internally consistent and jointly false.

## References

- [Design north star](./design-north-star.md) — P4, the different-observer rule that earned
  every blocker this session.
- [Parallel execution](./conventions/parallel-execution.md) — the disjoint-writer rule the
  reviewer fan-out ran under, and the proof floor a fan-out still owes.
- [Implementation discipline](./conventions/implementation-discipline.md) — the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
