# Lane brief R2b: wire run-quality.sh to the engine and delete the shell queue (#769, Goal Run #765)

Read `gh issue view 769` (Owned scope third bullet; Acceptance third line:
"`run-quality.sh` length is under the `.sh` cap with no exemption") and
`charness-artifacts/goal-runs/765/briefs/map-769-runner.md` sections 1, 2,
5, 6, 7. On your base, lane R1 has landed `.agents/quality-gates.yaml`,
`scripts/quality_gates_extract.py`, and the data branch of
`scripts/quality_label_universe.py` with its shell-versus-data parity test;
lane R2a has landed `scripts/run_quality_engine.py` and its libraries. Read
both AS LANDED before editing.

Outcome: `scripts/run-quality.sh` is a thin wrapper (under 205 physical
lines, comments included) that validates flags, runs the preamble, and
execs the engine on `.agents/quality-gates.yaml`; the shell queue is gone;
`SHELL_LENGTH_EXEMPTIONS` in `scripts/check_code_lengths.py:262-278` is
deleted; the mirror is regenerated before the standing pytest; every reader
of the runner is green on the data file alone.

Design:

1. The wrapper keeps the exact CLI surface (flags, env, exit-2 refusals,
   receipt handoff) because adapters and hooks equality-check
   `./scripts/run-quality.sh` (map 7d). It computes nothing the engine can
   compute; if a preamble value must stay in shell (state root from
   `.githooks/runtime-env.sh`), pass it through an env var the engine
   documents.
2. Inline `bash -c` payloads (map 7b item 2) become small scripts under
   `scripts/` (or `tools/` if lane T1 has landed and the gate is a `tools`
   row) so every row is a clean argv; `coverage_relevant_changes_present`
   (`:447-473`) becomes a named `predicate` the engine implements.
3. Delete the shell branch of `quality_label_universe.py` ONLY if every
   consumer-facing reader still works without it (a consumer repo may keep a
   shell runner); otherwise keep it and delete the parity test's
   this-repo case with a one-line reason. Update `run-quality.sh` self-parse
   (`:226-241`) to a schema check of the data file.
4. `docs/validator-timing-layers.md`: generate the classification table from
   the `timing_layer` field (`python3 scripts/render_validator_timing_layers.py --check`
   or the name R1 chose); `check_timing_layer_completeness` compares the
   rendered table to the file.
5. The mirror regeneration lands as the engine preamble R2a wrote, on by
   default, with `--no-sync-mirror` to skip; `--read-only` does not skip it
   (`plugins/` is gitignored, so read-only's promise about tracked artifacts
   holds); say so in `docs/development.md` "Verification and export" in one
   sentence.
6. `.githooks/pre-push` `DOCS_ONLY_LABELS` (`:97`) reads the `docs_only`
   rows from the data file through the engine (`--print-docs-only-labels`)
   instead of its literal.

Scope: `scripts/run-quality.sh`, `scripts/run_quality_engine*.py`,
`scripts/quality_label_universe.py`, `scripts/check_code_lengths.py`,
`scripts/check_timing_layer_completeness.py`, `.agents/quality-gates.yaml`,
`.githooks/pre-push`, `docs/validator-timing-layers.md`,
`docs/development.md`, new payload scripts, `tests/quality_gates/**`, and
`tests/quality_gates/support.py` seeded-runner helpers. Do not touch
`plugins/**`. Do not spawn descendant agents.

Rules: tests in-process (`docs/development.md` "Verification and export");
every touched CLI gets `python3 <file> --help` from the repo root in the
verification; the engine's summary line and receipt must be byte-identical
in shape to the old runner's (the seeded-runner tests pin it).

Verification before you stop:

```
wc -l scripts/run-quality.sh                                   # under 205
python3 scripts/check_code_lengths.py --repo-root . --require-git-file-listing    # no NAMED EXEMPTION line
python3 scripts/quality_label_universe.py --repo-root . --parity
python3 scripts/check_timing_layer_completeness.py --repo-root .
python3 scripts/check_runtime_budget_universe.py --repo-root .
python3 scripts/check_unreferenced_scripts.py --repo-root . --strict   # or python3 -m tools.check_unreferenced_scripts if T1 landed
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/run_standing_pytest.py --repo-root .
./scripts/run-quality.sh
./scripts/run-quality.sh --full --read-only
CHARNESS_QUALITY_LABELS=check-docs ./scripts/run-quality.sh
./scripts/check-docs.sh
```

Commit in ONE commit with subject
`quality: make run-quality.sh a thin wrapper over the declared gate list and retire its length exemption (#769 R2b lane candidate)`
with a body listing each inline payload extracted, each reader re-pointed,
and the exact commands with verdicts. No close keyword. Stop after the
commit and report the hash.
