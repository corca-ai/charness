# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then run `## Next Session` item 1. S1-S6c, S6b-2 and S7's preparation are
  committed; **the release is DEFERRED by owner decision** pending those five items.

## Continuation Capability

- [Release scope contract](../charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md) — the owner-approved scope,
  its sequence, and the S7 entry's "What S7 MEASURED" block.
- [S7 release critique](../charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md) — both rounds,
  F1-F30 and G1-G14, plus the per-issue premise verdicts the ledger binds to.
- [Closeout ledger](../charness-artifacts/issue/2026-08-16-6-0-0-closeout-ledger.md) — the `bug` carrier body whose
  `Jtbd:` names five narrowed closes clause by clause.
- [S7 retro](../charness-artifacts/retro/2026-08-16-s7-6-0-0-release.md) — the three red-at-HEAD gates, the stash that
  cost a quality run, and the review frame that missed the consumer.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.

## Current State

- **Prepared, not published.** Read the manifest and the target with
  `python3 skills/public/release/scripts/current_release.py --repo-root .`.
- **Notes generated over the final tree and gated clean**; they need REGENERATING
  if the items below change the tree. Re-prove with
  `python3 skills/public/release/scripts/generate_release_notes.py --repo-root . --notes-file charness-artifacts/release/2026-08-16-v6.0.0-notes.md --check --version v6.0.0`.
- **The changed-line proof over S7 is OBTAINED and closed.** Re-run
  `python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha 6416e7023 --head-sha HEAD`.
- **Three gates were RED AT HEAD before S7 and are repaired here**; which ones and
  why is the [S7 retro](../charness-artifacts/retro/2026-08-16-s7-6-0-0-release.md)'s
  evidence summary. Re-prove with `./scripts/run-quality.sh --release`.
- **Four publish-path defects are repaired**, the worst a resume lane that could
  not classify its own artifact commit and so had no recovery after a pushed tag;
  each is G1-G14 in the [S7 release critique](../charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md).
- **The close set is SPLIT**: #618-#627 close as `bug` through the release
  carrier, #608 separately as `feature`. One classification per invocation. The
  [closeout ledger](../charness-artifacts/issue/2026-08-16-6-0-0-closeout-ledger.md)
  carries BARE `#N` refs on purpose and derives its carrier at `--execute` time.
- Re-prove the suite with `python3 scripts/run_standing_pytest.py` (add
  `--include-release-only`), after `python3 scripts/sync_root_plugin_manifests.py`;
  ruff is clean only cache-free.

Non-claims: no push, tag, bump, publish, hosted CI, installed-consumer readback,
or issue closure. Round-2 repairs ship accepted-unreviewed at the two-round cap.
Every consumer-facing judgement below is from reading the export's layout against
the instruction text — NO consuming repo has run this tree.

## Next Session

Fix these five before reconsidering the publish. Only the first blocks; the rest
ship visible to consumers and the owner grouped them together.

1. **[#632](https://github.com/corca-ai/charness/issues/632) — BLOCKER, amplified
   by this release.** `scripts/recent_lessons_lib.py:482,500,508,513` name
   [build_retro_lesson_selection_index.py](../scripts/build_retro_lesson_selection_index.py) and
   [refresh_recent_lessons.py](../skills/public/retro/scripts/refresh_recent_lessons.py); the export ships them
   under `plugins/charness/`, and `skills/public/` does not exist there at all.
   The release advertises that a consuming repo can opt into the lesson lifecycle,
   and that path dead-ends here. Same class `seed_lesson_next_step()` already
   repairs for #625 — resolve against the READING tree — surviving four messages
   away in the same file.
2. **[#528](https://github.com/corca-ai/charness/issues/528)** — a consuming repo
   cannot declare a `coverage_floor_policy` sub-key absent; deletions silently
   refill from defaults. Reported from a real consuming repo.
3. **[#546](https://github.com/corca-ai/charness/issues/546)** — a budgeted
   runtime label with no sample is a WARN, so an unenforceable bar reads as
   protection forever.
4. **[#634](https://github.com/corca-ai/charness/issues/634)** — deliberately
   open: the cwd-relative instruction sites and unguarded shell gates are neither
   fixed nor detectable by what shipped.
5. **[#618](https://github.com/corca-ai/charness/issues/618)'s residual** —
   [default-surfaces.md](../skills/public/setup/references/default-surfaces.md) still points consumers at
   an exported `check-links-internal.sh` that refuses inside a consumer repo. This
   issue IS in the closing set, so either fix the residual or narrow the close.

Then, only on an explicit grant: regenerate the notes, re-run the release quality
lane, `--execute` to the prepared stop, commit the claims-review artifact as the
DIRECT child of that record, `--resume`, close #608 separately, and run the
adapter's real-host checklist.

## Discuss

- **Eight reviewers, none pointed at the consumer frame.** Two rounds covered the
  notes, the contract, and the publish path well. #632 came from the owner asking
  one outside-the-frame question — and it is an error I hit twice this session and
  read as my own repo's staleness, because here the files exist.
- **A doc rewrite can break a gate whose subject is that doc.** SC14 substitutes
  into the real `docs/handoff.md` and needs the bare backticked
  `python3 scripts/run_standing_pytest.py` as its anchor.
- **Three consecutive slices recorded "gates clean" while three gates were red**,
  and a text-gate repair needs a blast-radius measurement — both worked through in
  the [S7 retro](../charness-artifacts/retro/2026-08-16-s7-6-0-0-release.md).

## References

- [Design north star](./design-north-star.md) — P4, the different-observer rule that earned
  every blocker this session.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique floor
  and the write-capable isolation rule.
- [Implementation discipline](./conventions/implementation-discipline.md) — the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
