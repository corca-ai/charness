# Lane brief U3: scanner, CI, config universes and the seeded-consumer proofs (#769, Goal Run #765)

Follow `charness-artifacts/goal-runs/765/briefs/brief-769-u-common.md` first.

Part A, port these labels:

- `inventory-gitignore-scan-hygiene`
  (`skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py:34-45`
  `DEFAULT_PATH_GLOBS`): `scanner_globs`; keep `--path-glob` as the override.
- `inventory-ci-local-gate-parity`
  (`skills/public/quality/scripts/ci_local_gate_parity_lib.py:33-41`
  `DEFAULT_CANONICAL_GATE_PATTERNS`): `ci_gate_patterns`; keep
  `--canonical-gate-pattern` as the override. An unmatched CI gate must not
  read as parity-clean when the patterns were declared.
- `specdown` (`scripts/specdown_ephemeral_config.py:70-71`, unguarded read):
  `specdown_config`; an absent file is a named refusal, not a traceback.
- `check-secrets` (`scripts/check-secrets.sh:91-106`, unguarded
  `.gitleaks.toml`): `secrets_config`; absent config is a named refusal.

Part B, for the six labels that ALREADY read an adapter key, add the
seeded-consumer proof that is missing (no production change unless the proof
fails, then the smallest fix):

- `validate-adapters`: a `repo: my-repo` quality adapter with non-charness
  `gate_commands` passes `validate_adapters.py` (the charness literals at
  `:198-202,228-235,285-288` sit behind the `repo: charness` guard at
  `:207-211`; prove the guard).
- `check-cli-skill-surface` (`product_surfaces` and the `cli_skill_surface_*`
  keys), `validate-skill-ergonomics` (`skill_ergonomics_*`),
  `check-command-dominance` (`.agents/command-dominance.yaml` of the analysed
  repo), `inventory-nose-clones` (`nose_inventory_paths`), `dup-ratchet`
  (`dup_ratchet.scope_paths`): one test each proving a consumer-shaped tmp
  repo with the key declared is scanned at the declared paths, unless such a
  test already exists (cite it in the body instead).

Scope: the four Part A scripts, `skills/public/quality/scripts/ci_local_gate_parity_lib.py`,
`tests/quality_gates/test_quality_gitignore_scan_hygiene.py`,
`test_inventory_ci_local_gate_parity.py`, `test_specdown_ephemeral_config.py`,
`test_python_and_security_gates.py`, `test_empty_scope_refusals.py`,
`tests/test_validate_adapters_integration_schema.py`,
`tests/quality_gates/test_profile_and_preset_validation.py`, and new tests
for Part B under `tests/quality_gates/`.

Commit subject:
`quality: read scanner, CI-parity, and config universes from the adapter and prove the six keyed gates on a consumer layout (#769 U3 lane candidate)`
