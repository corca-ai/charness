# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <date-slug>`
  BEFORE any brief or reviewer spawn. `--session-id` and `--seed` are both required and
  take the SAME value, so the selection is reproducible and citable.
- Then run `## Next Session` item 1.

## Continuation Capability

- The [last session retro](../charness-artifacts/retro/2026-08-16-session-retro-7f96d281-13a0-42bc-8471-ec0edf00eae0.md) carries the 5/5 fix-carries-its-class measurement, five anchored lesson scores, and
  three sibling-search axes with two deferred follow-up anchors.
- The executed [real-host checklist record](../charness-artifacts/probe/2026-08-16-v6.0.0-real-host-checklist.json) is
  at `v5` with ten raw transcripts beside it; read its `non_claims` before citing it.
- The digest a session reads before work is [recent lessons](../charness-artifacts/retro/recent-lessons.md).

## Current State

- **The released tag's real-host checklist is fully executed** — 3 confirmed, 1 REFUTED, 3
  precondition-unmet or partial, each with a raw transcript beside the
  record: [real-host checklist](../charness-artifacts/probe/2026-08-16-v6.0.0-real-host-checklist.json).
- **The `nose` doctor item demanded an unreachable disposition and is now corrected.**
  A missing `nose` reports `blocking-install-needed`; `scripts/doctor_lib.py:237` emits
  advisory only for `mode: manual` or `doctor_policy: advisory`. Reproduce the missing
  arm without uninstalling: `env PATH=/usr/bin:/bin $(command -v charness) tool doctor nose --no-write-locks`.
- **Three release-checklist items were unexecutable as written**; all three are repaired
  in the [release adapter](../.agents/release-adapter.yaml). Re-read that block before trusting any item.
- **`<plugin-dir>/` is a DOC placeholder no runtime substitutes**, as its owner
  [check_plugin_dir_references.py](../scripts/check_plugin_dir_references.py) states. Never
  put it in a field an executor runs. Only release declares its RUN fields; critique/retro
  `command:` and `integrations/tools/*.json` `checks.*.commands` do not — follow-up 3.
- **The export instruction arm blocks on consumer `.md` and inventories the rest.** Re-measure
  with `python3 scripts/check_export_self_sufficiency.py --repo-root .`; expect
  `consumer_doc_repo_root_instructions: []` and ~79 advisory module-prose entries.
- **The installed-vs-repo skew is CLOSED**, which only the push could do: the managed
  checkout at `~/.agents/src/charness` fast-forwards from origin and nothing else moves it.
  Re-check with `diff -rq ~/.agents/src/charness/plugins/charness plugins/charness`.
- Re-prove with `python3 scripts/run_standing_pytest.py` after
  `python3 scripts/sync_root_plugin_manifests.py`, then
  `python3 -m ruff check --no-cache scripts skills tests`.
- **COMMIT the slice, THEN run the changed-line proof** — `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  reads `base..HEAD`, so running it on a dirty pool proves nothing.

## Next Session

1. **Give `prove`'s stop gate the blind-class question** for detector-touching slices — a
   question, not a gate. Two measured instances stand behind it, recorded in the
   session retro: [2026-08-16 retro](../charness-artifacts/retro/2026-08-16-session-retro-7f96d281-13a0-42bc-8471-ec0edf00eae0.md).
2. **Follow-up `export-instruction-spellings`.** The new arm matches ONE spelling. Live misses
   include the dot-slash and `bash`-prefixed forms in the quality skill's
   [catalog](../skills/public/quality/references/catalog.yaml); `.sh` and `.mjs` are unscanned.
3. **Follow-up `executed-field-declaration`.** Declare executed adapter fields the way
   [resolve_adapter.py](../skills/public/release/scripts/resolve_adapter.py) already does
   with `EXECUTED_COMMAND_FIELDS`, so a classifier can key on the FIELD, not the file type.
4. **[#546](https://github.com/corca-ai/charness/issues/546) residual** — separating
   "legitimately conditional" from "abandoned behind an opt-in" still needs an
   adapter-declared expectation; a prior repair was measured defective and reverted.
5. **Unowned residuals** — the seeder cold-start re-prompt and file mode in
   [#625](https://github.com/corca-ai/charness/issues/625), graduated lessons held `active`
   against the budget in [#626](https://github.com/corca-ai/charness/issues/626), and the
   deferred Sibling Search item where
   `test_a_bare_shipped_directory_reference_is_still_not_reported` passes at an earlier
   `.exists()` branch. Inspect it with
   `rg -n -A12 'def test_a_bare_shipped_directory' tests/quality_gates/test_export_self_sufficiency.py`.

## Discuss

- **The two-round critique cap now has a number against it: 5/5.** Every bounded round
  last session found the defect inside the REPAIR, one layer down each time — prose claim,
  evidence marker, wrong command, machine-readable field, exemption reason. All three
  slices hit the cap, so all three shipped round-2 repairs accepted-unreviewed. Does a
  proof-surface slice owe review until a round returns clean?
- **A bulk rewrite of command-shaped strings owes a written executor check first.** Two of
  five rounds trace to one blanket regex that broke five working commands.
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
