# Lane brief U0: one `universes:` adapter family for gate scopes (#769, Goal Run #765)

Read `gh issue view 769` (Owned scope, first and fourth bullets) and the
"Running count of conditional `ship` rows" paragraph plus the table in
`charness-artifacts/quality/2026-09-02-gate-classification-769.md`. Then read
`charness-artifacts/goal-runs/765/briefs/map-769-conditional.md`, which names,
for each of the 27 conditional `ship` gates, the file:line where its scan
universe is hardcoded and how it behaves on an empty match (five different
behaviours today). This lane builds the ONE shape those 27 gates will read;
it ports no gate itself (lanes U1 to U3 do that next, in parallel).

Outcome: a consumer adapter can declare, in one place, the file families its
gates scan; a declared family that matches nothing REFUSES; an undeclared
family falls back to the same default the gate carries today; and a repo can
mark a family `deliberately_absent` like any other path-bearing field.

## Design (the parent's; cite the row when you deviate and say why)

Add a `universes:` block to the quality adapter, grouped by FILE FAMILY (not
by gate label), with the owning labels named in comments. Sub-keys and their
charness defaults (each default is the literal the gate carries today; copy
it from the file:line in the map, do not retype from memory):

| sub-key | default source | owning labels |
| --- | --- | --- |
| `pytest_targets` | `scripts/run_standing_pytest.py:78-91` | pytest, pytest-release, check-test-completeness |
| `python_sources` | `scripts/run-quality.sh:1157-1166` (py-compile array) | py-compile, ruff, check-python-lengths, check-python-runtime-inheritance |
| `shell_sources` | `scripts/check-shell.sh:52-61` | check-shell |
| `test_roots` | `scripts/check_test_production_ratio.py:20-34` (`tests`) | check-test-production-ratio |
| `doc_surfaces` | `scripts/doc_file_population.py:16-25` | check-doc-links, docs-graph (scan root = first entry's top dir), doc-duplicates |
| `artifact_roots` | the literal `charness-artifacts/<family>` prefixes in `check_spec_evidence_durability.py:30-60`, `check_artifact_referents.py:229-232`, `critique_artifact_paths.py:13-14`, `validate_ideation_artifact.py:20`, `check_lesson_ledger.py:22-23` | check-spec-evidence-durability, check-artifact-referents, validate-critique-artifacts, validate-ideation-artifact, validate-lesson-ledger |
| `scanner_globs` | `skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py:34-45` | inventory-gitignore-scan-hygiene |
| `ci_gate_patterns` | `skills/public/quality/scripts/ci_local_gate_parity_lib.py:33-41` | inventory-ci-local-gate-parity |
| `mutation_pool` | `scripts/sample_mutation_files.py:53-69` | release-changed-line-coverage |
| `specdown_config` | `specdown.json` (`scripts/specdown_ephemeral_config.py:70`) | specdown |
| `secrets_config` | `.gitleaks.toml` (`scripts/check-secrets.sh:91-106`) | check-secrets |

`artifact_roots` is a mapping `{spec: charness-artifacts/spec, retro: ..., ...}`
so each validator asks for its own family; the other sub-keys are string lists
except the two `*_config` strings.

Ship the reader as `scripts/quality_universes_lib.py` (root `scripts/` is
exported wholesale, so it reaches consumers). Its public surface:

- `resolve_universe(adapter_payload, key, *, default) -> Universe` where
  `Universe` carries `patterns`, `declared: bool`, `source: "adapter" | "default" | "deliberately-absent"`.
- `matching_files(repo_root, universe, *, git_listing=True) -> list[Path]`
  sourcing candidates from `git ls-files --cached --others --exclude-standard`
  through `scripts/subprocess_guard.py` (never a direct `subprocess` call; the
  standing `check_subprocess_form.py` refuses one), falling back to the raw
  glob when git is unavailable, exactly like
  `skills/public/quality/scripts/check_regenerable_facts.py:234-259`.
- `refuse_if_declared_and_empty(universe, files, gate_label) -> str | None`
  returning the refusal text when `declared` and `files` is empty, `None`
  otherwise. The rule is the one `regenerable_facts_lib.declared_surfaces`
  (`skills/public/quality/scripts/regenerable_facts_lib.py:192-215`) states:
  a declared scope matching nothing is a broken config and fails; an
  undeclared scope matching nothing is a discovered empty and is reported,
  not failed.

Wire it: `infer_quality_defaults` (`scripts/quality_adapter_lib.py:92-143`)
gains `universes` with the defaults above; `validate_quality_adapter_data`
(`:453-501`) gains a `validate_universes` block validator beside `dup_ratchet`
in `skills/public/quality/scripts/adapter_validators.py` (unknown sub-key
refused, wrong shape refused, empty list allowed and meaning "declared
empty"); `PATH_BEARING_ABSENCE_FIELDS` (`:323-326`) gains `universes`.
Keep `quality_adapter_lib.py` under the root length cap by putting the
defaults table in the new module and importing it.

Declare the block in `.agents/quality-adapter.yaml` with charness's own
values (so this repo becomes the first declared consumer) and in
`skills/public/quality/adapter.example.yaml` with a `src/`-layout example.
Document it in `skills/public/quality/references/adapter-contract.md` under
`## Fields` as `### universes`, following the `### regenerable_facts` section's
shape. Do not touch any gate script or `run-quality.sh`; the porting lanes own
those.

## Scope

You may edit: `scripts/quality_adapter_lib.py`, new `scripts/quality_universes_lib.py`,
`skills/public/quality/scripts/adapter_validators.py`, `.agents/quality-adapter.yaml`,
`skills/public/quality/adapter.example.yaml`,
`skills/public/quality/references/adapter-contract.md`,
`skills/public/quality/references/index.md` (only if the contract page's
listing needs it), and tests: new `tests/quality_gates/test_quality_universes.py`,
plus `tests/quality_gates/test_quality_bootstrap_absence_paths.py` and any
adapter-validation test that enumerates the field vocabulary. Do not touch
`plugins/**` (generated). Do not spawn descendant agents.

## Rules

1. Tests are in-process through `tests/script_loader.py` / `script_main.py`;
   no `subprocess` in a new test. Cover: default when undeclared; declared
   list wins; declared-empty refuses with the gate label in the text; unknown
   sub-key refused by the validator; `deliberately_absent: [universes]`
   reports the phantom paths; git listing versus raw-glob fallback parity on a
   seeded tree.
2. `validate_adapters.py` runs `load_quality_adapter_strict` on this repo's
   adapter; the declared block must validate. Run it.
3. Read `docs/development.md` "Verification and export" for the in-process
   rule before writing any loader.

## Verification before you stop

```
python3 -m ruff check <touched .py>; python3 -m ruff format --check <touched .py>
python3 scripts/quality_universes_lib.py --help        # from the repo root; the module must be runnable as a CLI that prints the resolved universes for --repo-root .
python3 scripts/validate_adapters.py --repo-root . --require-git-file-listing
python3 scripts/check_subprocess_form.py --repo-root . --require-git-file-listing
python3 scripts/check_code_lengths.py --repo-root . --require-git-file-listing
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/run_standing_pytest.py --repo-root . --pytest-target tests/quality_gates
./scripts/run-quality.sh
./scripts/check-docs.sh
```

Commit in ONE commit with subject
`quality: declare gate scan universes in one adapter family with a shared refusal rule (#769 U0 lane candidate)`
and a body naming each sub-key with the file:line its default was copied from
and the exact commands with verdicts. No close keyword. Stop after the commit
and report the hash.
