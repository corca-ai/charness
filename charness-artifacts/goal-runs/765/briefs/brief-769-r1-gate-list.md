# Lane brief R1: the declarative gate list and its readers (#769, Goal Run #765)

Read `gh issue view 769` (Owned scope, third bullet: "Replace the 1341-line
`run-quality.sh` queue with a declarative gate list (label, command, lane,
budget) and a thin runner"). Then read
`charness-artifacts/goal-runs/765/briefs/map-769-runner.md` in full: it
inventories every queue call by phase, the selection model, every reader that
parses the shell file as text, and a recommended row schema (section 7). This
lane lands the DATA FILE and every Python reader of it. It does NOT rewrite
the shell runner (lane R2 does that on top of this lane) and does not touch
the Rust extractor under `native/` (lane R3).

Outcome: `.agents/quality-gates.yaml` is the single declaration of what
`run-quality.sh` can queue; `scripts/quality_label_universe.py` reads it and
proves, on this tree, that the declared labels equal the labels the shell
parser still finds (so the two cannot drift while R2 is in flight); every
Python reader that keyed on the shell text now keys on the rows.

## Design (the parent's; cite the map section when you deviate and say why)

1. File: `.agents/quality-gates.yaml`, per map section 7a (a file under
   `scripts/` would drop the reference edges `check_unreferenced_scripts.py`
   counts). Schema per 7b: `schema: charness/quality-gates/v1`, `phases:` in
   runner order (pytest alone fail-fast; agent-browser baseline alone
   fail-fast; main concurrent; inventory-declaration alone; post-pytest-tree
   batch; runtime budget alone; agent-browser hygiene alone; release-final
   alone), each with `id`, `isolation`, `fail_fast`, optional `fail_message`,
   and `gates:` rows. Row fields exactly as 7b names them: `label`,
   `command` (argv list; a `${VAR[@]}` or `$VAR` token names a runner-computed
   variable, listed in a top-level `runner_variables:` with a one-line meaning
   each), `lane` (`core | standard | release-only | label-only | opt-in`),
   optional `condition` (`env`, `file_exists`, `mode_in`, `predicate`),
   `variant_of`, `unestablished_capable`, `native_preflight`, `timing_layer`,
   `docs_only`, `note`. Carry the load-bearing shell comments the map names
   (`:1134-1143`, `:1260-1274`, `:475-479`) into `note:` fields, not into the
   void. Inline `bash -c` payloads (map 7b item 2) stay as a single
   `command: [bash, -c, "..."]` row in THIS lane; R2 extracts them.
2. Populate the rows from the live shell file by a script, not by hand:
   ship `scripts/quality_gates_extract.py` that parses `run-quality.sh` with
   the existing `quality_label_universe` regexes and emits the YAML, then
   check the emitted file in. Keep the extractor: it is the migration proof
   and the parity oracle below.
3. `scripts/quality_label_universe.py`: add the data branch (`label_universe`
   `:255`, `queue_call_labels` `:143`) that reads the YAML and returns the
   same shape; keep the shell branch for consumer repos that have no data
   file. Add `parity(repo_root)` that returns the two label sets and their
   symmetric difference, and a standing test asserting it is empty on this
   repo (this is what stops drift until R2 deletes the shell queue). Map 7e:
   land this in the FIRST commit of the lane, with a test that the universe
   is non-empty for this repo.
4. Rewrite the readers map 7c lists (items 2, 3, 5, 8, 9, 10, 11) to key on
   the rows: `check_timing_layer_completeness.py`, `check_runtime_budget_universe.py`
   (re-scope the zero-call-sites disarm at `:335-347`),
   `validate_current_pointer_freshness.py:93-100`,
   `standing_gate_discovery_lib.py` and `standing_gate_verbosity_lib.py`,
   `check_command_dominance.py` (read commands from rows; drop the
   wrapper-program heuristic and its `.agents/command-dominance.yaml:77-82`
   entries), `staged_commit_gate_plan.py` and `classify_t_signal.py` trigger
   lists, `tests/quality_gates/support.py` `make_quality_runner_repo()`.
   Leave `run-quality.sh` self-parse (`:226-241`) and the Rust reader alone.
5. Update the tests map 7c names as literal greps against the shell source
   so they read the rows instead; assertions keep their meaning.
6. `docs/validator-timing-layers.md`: do not regenerate it here; add one
   sentence under its intro saying the `timing_layer` field of
   `.agents/quality-gates.yaml` is now the source and R2 will generate the
   table. Add the file to `.agents/surfaces.json` only if a validator
   requires it (say which).

## Scope

You may edit: new `.agents/quality-gates.yaml`, new `scripts/quality_gates_extract.py`,
`scripts/quality_label_universe.py`, `scripts/check_timing_layer_completeness.py`,
`scripts/check_runtime_budget_universe.py`, `scripts/validate_current_pointer_freshness.py`,
`scripts/check_command_dominance.py`, `.agents/command-dominance.yaml`,
`scripts/staged_commit_gate_plan.py`, `scripts/classify_t_signal.py`,
`skills/public/quality/scripts/standing_gate_discovery_lib.py`,
`skills/public/quality/scripts/standing_gate_verbosity_lib.py`,
`docs/validator-timing-layers.md`, `.agents/surfaces.json`, and tests under
`tests/quality_gates/` that the map names plus new ones. Do not edit
`scripts/run-quality.sh` (R2), anything under `native/` (R3), or
`scripts/quality_adapter_lib.py` and `skills/public/quality/scripts/adapter_validators.py`
(lane U0 is editing them now). Do not touch `plugins/**` (generated). Do not
spawn descendant agents.

## Rules

1. Tests are in-process through `tests/script_loader.py` / `script_main.py`;
   no `subprocess` in a new test. Read `docs/development.md` "Verification
   and export" first: swap argv before import, script directory first on
   `sys.path`, never load a module under a bare name the code under test
   imports lazily.
2. Every reader keeps a loud refusal when the data file is present but
   parses to zero gates (map 7e). A missing data file falls back to the
   shell branch with a `source: shell` line in the payload.
3. YAML is read with the repo's own loader (`yaml_output` / the loader the
   adapters use); block-style lists only, no inline `[a, b]` arrays
   (`docs/worktree-prepare.md` records that limit).

## Verification before you stop

```
python3 -m ruff check <touched .py>; python3 -m ruff format --check <touched .py>
python3 scripts/quality_gates_extract.py --repo-root . --check      # emitted YAML equals the checked-in file
python3 scripts/quality_label_universe.py --repo-root . --parity      # symmetric difference empty
python3 scripts/check_timing_layer_completeness.py --repo-root .
python3 scripts/check_runtime_budget_universe.py --repo-root .
python3 scripts/validate_current_pointer_freshness.py --repo-root .
python3 scripts/check_command_dominance.py --repo-root .
python3 scripts/check_unreferenced_scripts.py --repo-root . --strict
python3 scripts/check_subprocess_form.py --repo-root . --require-git-file-listing
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/run_standing_pytest.py --repo-root . --pytest-target tests/quality_gates
./scripts/run-quality.sh
./scripts/check-docs.sh
```

For every touched CLI file run `python3 <file> --help` from the repo root and
paste any failure: a module that only passes under the pytest loader is the
defect class this repo had 39 files of last session.

Commit in TWO commits: first `quality: declare the gate list in .agents/quality-gates.yaml and read it from quality_label_universe (#769 R1 lane candidate)`
(data file, extractor, universe data branch, parity test), then
`quality: key the gate-list readers on the declared rows (#769 R1 lane candidate)`
(readers and tests). Bodies carry the exact commands with verdicts. No close
keyword. Stop after the second commit and report both hashes.
