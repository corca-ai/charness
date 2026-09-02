# Lane brief R2a: the thin runner's Python engine (#769, Goal Run #765)

Read `gh issue view 769` (Owned scope, third bullet) and
`charness-artifacts/goal-runs/765/briefs/map-769-runner.md` sections 1, 2, 4
and 7 in full. Lane R1 is producing `.agents/quality-gates.yaml` in parallel
with the row schema of map section 7b (also restated in
`charness-artifacts/goal-runs/765/briefs/brief-769-r1-gate-list.md`, Design
item 1). This lane builds the engine that will execute that file; lane R2b
wires `scripts/run-quality.sh` to it afterwards. You do NOT edit
`run-quality.sh`, `quality_label_universe.py`, or the readers R1 owns.

Outcome: `scripts/run_quality_engine.py` (plus split libraries under the
root length cap) executes a gate list with the SAME observable behaviour the
shell runner has today, proven by tests against a fixture gate list and
seeded gate stubs: selection, phases, concurrency, fail-fast, heartbeat,
per-phase output rules, exit-status vocabulary, runtime records, the final
summary line, and the receipt.

## Design (the parent's; cite the map line when you deviate and say why)

Read the shell functions the map names and port their contract, not their
prose: `label_is_core/selected/explicitly_selected` (`run-quality.sh:575-624`),
`queue_timed` and the phase monitor (`:533-575`, `:679-870`),
`print_phase_output` rules including the `WARN|WEAK|ADVISORY` surfacing regex
(`:696`), `consume_phase_result`, `print_phase_heartbeat`, `flush_phase`,
`print_final_summary` (`:871`), `record_runtime` and `flush_runtime_batch`
(`:480-532`), `UNESTABLISHED_EXIT=3` / `PARTIAL_EXIT=4` rendering as UNPROVEN
only for `unestablished_capable` rows (`:370-383`), `native_gate_preflight`
(`:664-677`) for `native_preflight` rows, the regime derivation
(`CHARNESS_RUNTIME_REGIME`, `:280-298`), the aggregate labels
(`run-quality-{read-only,full}[-release]`), the `--receipt-json` handoff to
`scripts/proof_receipt.py` (`:924-926`), and the exit-2 refusals (unknown
argument, `--release` with labels, `--non-claim` without `--release`, zero
selected labels, a heartbeat that is not a non-negative integer).

CLI: `python3 scripts/run_quality_engine.py --repo-root . --gates .agents/quality-gates.yaml [--full] [--read-only] [--release] [--review] [--non-claim=...] [--receipt-json=...] [--labels a,b]`
reading the same environment variables the shell reads (map section 2,
"Environment variables" table) with the same defaults. Commands are argv
lists; a `${VAR[@]}` or `$VAR` token is substituted from `runner_variables`
the engine computes (expanded pytest targets via
`run_standing_pytest.py --print-expanded-targets`, temp root, critique
changed ref, changed-line base sha, state-root args; read how the shell
computes each at the lines the map cites) and never passed to a shell.
Spawn through `scripts/subprocess_guard.py` only (`check_subprocess_form.py`
refuses a direct `subprocess` call); phases run gates concurrently with the
same per-phase isolation the rows declare. Preamble step: when
`plugins/` exists and the mode is not read-only, run
`python3 scripts/sync_root_plugin_manifests.py --repo-root <root>` before
the first phase (map section 6: two standing tests byte-compare the mirror;
regenerating it in the runner is part of #769's declarative runner). Write
the preamble so R2b can also expose it as a single flag.

Tests: `tests/quality_gates/test_run_quality_engine*.py`, in-process
(`tests/script_loader.py`), driving the engine's `main` on a tmp repo whose
gate list names stub gates seeded by `tests/quality_gates/support.py`
helpers (`make_quality_runner_repo` shapes at `:545-660`; reuse, do not
fork). Cover every contract above with at least one case, including: core
lane by default, `--full` selects every `standard` row, `release-only` rows
only under `--release` or by name, `label-only` rows only by name, `opt-in`
rows only under their env condition, `variant_of` pairs never both queued,
fail-fast phase stops the run with the phase's `fail_message`, UNPROVEN
rendering only for `unestablished_capable`, runtime samples written in the
existing signals shape, summary line format identical to today's
(`Quality summary: N passed, M failed ...`), receipt JSON handed to
`proof_receipt.py` with the same fields.

## Scope

You may add: `scripts/run_quality_engine.py`, `scripts/run_quality_engine_*.py`
libraries, tests under `tests/quality_gates/`, a fixture gate list under
`tests/quality_gates/fixtures/`, and an entry in
`docs/validator-timing-layers.md` only if a validator requires a new script
to be listed (say which). You may edit `tests/quality_gates/support.py` to
add helpers (never change an existing helper's behaviour). Do not edit
`scripts/run-quality.sh`, `scripts/quality_label_universe.py`,
`.agents/quality-gates.yaml`, `.agents/quality-adapter.yaml`, or anything
under `native/`. Do not touch `plugins/**`. Do not spawn descendant agents.

## Rules

1. Read `docs/development.md` "Verification and export" before writing a
   loader or a test. No `subprocess` in tests except one `boundary_contract`
   case proving the engine's own exit codes from the CLI shape.
2. Every new module stays under the root script cap
   (`scripts/check_code_lengths.py` reports it); split by concern
   (selection, phase execution, output, runtime records, receipt).
3. `check_unreferenced_scripts.py --strict` must stay green: the new engine
   is referenced from a test and from this brief's future runner row; if the
   graph refuses it, add the reference the gate documents rather than an
   exemption.

## Verification before you stop

```
python3 -m ruff check <touched .py>; python3 -m ruff format --check <touched .py>
python3 scripts/run_quality_engine.py --help                                       # from the repo root
python3 scripts/run_quality_engine.py --repo-root . --gates tests/quality_gates/fixtures/<fixture>.yaml --full   # on the fixture, paste the summary
python3 scripts/check_subprocess_form.py --repo-root . --require-git-file-listing
python3 scripts/check_code_lengths.py --repo-root . --require-git-file-listing
python3 scripts/check_unreferenced_scripts.py --repo-root . --strict
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/run_standing_pytest.py --repo-root . --pytest-target tests/quality_gates
./scripts/run-quality.sh
```

Commit in ONE commit with subject
`quality: add the declarative gate-list engine behind run-quality.sh (#769 R2a lane candidate)`
and a body mapping each shell function ported to the engine module that owns
it, plus the exact commands with verdicts. No close keyword. Stop after the
commit and report the hash.
