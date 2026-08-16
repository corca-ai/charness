# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <date-slug>`
  BEFORE any brief or reviewer spawn. `--session-id` and `--seed` are both required and
  take the SAME value, so the selection is reproducible and citable.
- Then run `## Next Session` item 1. The tag the real-host work is about is whatever
  `git describe --tags --abbrev=0` prints; compare it to `charness version` in item 1.

## Continuation Capability

- [Last session retro](../charness-artifacts/retro/2026-08-16-session-retro-09ff8e62-ba16-4350-a2aa-72f50e6dd988.md) —
  the five reviewer rounds, the flat fix-carries-its-class trend, and five anchored lesson scores.
- [Release record](../charness-artifacts/release/latest.md) — the real-host checklist,
  and which of its steps already executed at publish with their measured status.
- [Prepared claims review](../charness-artifacts/release-review/2026-08-16-v6.0.0-prepared-claims-review.md) —
  the two should-fix claims and the note that they are now repaired in the tree.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — the digest a session reads before work.

## Current State

- **CORRECTION to the previous handoff's non-claim.** `charness update`, `charness version`
  and `charness doctor` all RAN at publish and are recorded with return codes and
  `status: confirmed` in the
  [release observer probe](../charness-artifacts/probe/2026-08-16-v6.0.0-release-observer.json).
  The previous handoff said none had run. Genuinely unexecuted: the cited-check == repo
  spot check, and all six `nose` steps.
- **The installed plugin is behind this tree.** Read-only recheck:
  `diff -q ~/.agents/src/charness/plugins/charness/skills/retro/scripts/scaffold_retro_artifact.py skills/public/retro/scripts/scaffold_retro_artifact.py`.
  Item 1's `charness update` is what closes it; do not use a helper that WRITES as the probe.
- **Nothing in the last range is pushed, and part of it is accepted-unreviewed**; see
  `## Discuss`. List it with `git log --oneline origin/main..HEAD`.
- **The shared close-keyword scanner matches `GH-N` and issue URLs case-insensitively now**,
  so every consumer of
  [iter_close_keyword_refs](../skills/public/issue/scripts/issue_verify_closeout_body.py)
  sees what only the pre-push guard saw.
- **`EXECUTED_COMMAND_FIELDS` names the release adapter's only two RUN fields**, every other
  field being READ —
  [resolve_adapter.py](../skills/public/release/scripts/resolve_adapter.py).
- Re-prove with `python3 scripts/run_standing_pytest.py --include-release-only` after
  `python3 scripts/sync_root_plugin_manifests.py`, then
  `python3 -m ruff check --no-cache scripts skills tests`.
- **COMMIT the slice, THEN run the changed-line proof** — `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  reads `base..HEAD`, so running it on a dirty pool proves nothing. Amends the digest's ordering.

## Next Session

1. **Run the release's unrun real-host steps.** List them with
   `rg -n -A8 '^real_host_checklist:' .agents/release-adapter.yaml` — SEVEN items: one
   update/doctor line plus six `nose` steps. Unexecuted: that line's cited-check == repo
   spot check, and all six `nose` steps. Re-run `charness update` and `charness doctor`
   anyway (they ran at publish, but this tree has moved since).
2. **Give `prove`'s stop gate the blind-class question** for detector-touching slices, per
   [the retro's Next Improvements](../charness-artifacts/retro/2026-08-16-session-retro-09ff8e62-ba16-4350-a2aa-72f50e6dd988.md).
   A question, not a gate. Two measured instances stand behind it.
3. **[#634](https://github.com/corca-ai/charness/issues/634) remainder.** The consumer-config
   half landed; the exported doc/reference sites did not, and no detector exists. Re-measure with
   `rg -n 'python3 scripts/[a-zA-Z_0-9-]+\.(py|sh)' plugins/charness/skills`.
4. **Two latent traps the scanner widening opens**, named in
   [the retro](../charness-artifacts/retro/2026-08-16-session-retro-09ff8e62-ba16-4350-a2aa-72f50e6dd988.md).
   The original sweep covered the worktree AND stored commit messages, so re-sweep both with
   `PAT='(close[sd]?|fix(e[sd])?|resolve[sd]?)[ :]+(GH-[0-9]+|https?://)'; rg -n -i "$PAT" docs skills charness-artifacts; git log --format=%B HEAD | rg -n -i "$PAT"`
   — `HEAD`, not `origin/main`, or the unpushed range is invisible. At handoff the only hit
   was the scanner's own explanatory comment; a hit in a closeout body is the real trap.
5. **[#546](https://github.com/corca-ai/charness/issues/546) residual.** Untouched; separating
   "legitimately conditional" from "abandoned behind an opt-in" needs an adapter-declared
   expectation, and a prior repair was measured defective and reverted.
6. **Unowned residuals** — [#625](https://github.com/corca-ai/charness/issues/625)'s seeder
   cold-start re-prompt and file mode, [#626](https://github.com/corca-ai/charness/issues/626)'s
   graduated lessons held `active` against the budget, and the retro's deferred Sibling Search
   follow-up: `test_a_bare_shipped_directory_reference_is_still_not_reported` passes at an
   earlier `.exists()` branch and never reaches the depth rule it claims to pin. Inspect with
   `rg -n -A12 'def test_a_bare_shipped_directory' tests/quality_gates/test_export_self_sufficiency.py`.

## Discuss

- **Push grant — ASK THE OPERATOR; never infer one from a green gate.** The range is
  unpushed and its last review round's repairs are accepted-unreviewed at the two-round cap,
  so "reviewed" is not what a grant would be approving.
- **The two-round critique cap is holding, not improving.** Three more boundaries last
  range had the defect inside the repair. Is the cap the right ceiling, or does a
  proof-surface slice owe a third round?
- **This bullet IS an SC14 anchor — do not tidy it away.**
  [The dominance test](../tests/quality_gates/test_command_dominance.py)
  substitutes into the real handoff and needs the bare backticked
  `python3 scripts/run_standing_pytest.py`, with no flags inside the backticks, present here.

## References

- [Design north star](./design-north-star.md) — P4's different-observer rule and the
  proof-surface reading of the irreversible boundary.
- [Operating contract](./conventions/operating-contract.md) — the two-round critique floor
  and the write-capable isolation rule.
- [Implementation discipline](./conventions/implementation-discipline.md) — the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
