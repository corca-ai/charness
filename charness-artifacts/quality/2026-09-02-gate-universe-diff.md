# Gate universe diff for #767 (2026-09-02)

Before/after file sets for every glob-driven gate whose `scripts/*.py`-family globs became recursive. Sets were produced through `scripts/repo_file_listing.iter_matching_repo_files` with `require_git=True`, the same iterator the gates use. The tree is flat today, so the `.py` sets are identical by construction; the only widened universe is the shell family newly entering the length gate.

| Gate | Before | After | Added | Removed |
| --- | --- | --- | --- | --- |
| `check_code_lengths.py GATED_GLOBS (.py part)` | 756 | 756 | none | none |
| `check_code_lengths.py GATED_GLOBS (.sh, new)` | 0 | 12 | `scripts/check-docs.sh`, `scripts/check-links-external.sh`, `scripts/check-links-internal.sh`, `scripts/check-markdown.sh`, `scripts/check-python-lint.sh`, `scripts/check-rust.sh`, `scripts/check-secrets.sh`, `scripts/check-shell.sh`, `scripts/exported-copy-guard.sh`, `scripts/install-git-hooks.sh`, `scripts/run-quality.sh`, `scripts/self-validate-install-update.sh` | none |
| `check_python_runtime_inheritance.py DEFAULT_SCAN_GLOBS` | 756 | 756 | none | none |
| `run-quality.sh py-compile list` | 756 | 756 | none | none |
| `sample_mutation_files.py MUTATION_POOLS` | 721 | 721 | none | none |
| `inventory_gitignore_scan_hygiene.py` | 101 | 101 | none | none |
| `inventory_adapter_gate_design.py DEFAULT_REVIEW_GLOBS / quality-adapter gate_design_review_globs (scripts part)` | 383 | 383 | none | none |

Already recursive (`rglob`), recorded not changed: `check_consumer_validator_catalog.py`, `check_export_self_sufficiency.py`, `export_self_sufficiency_lib.py`, `check_prose_pin.py`, `discovery_filter_scan_lib.py`, `skill_text_quality_lib.py`, `validate_attention_state_visibility.py`, `check_test_completeness.py`, `check_test_repo_copy_invariants.py`, `helper_provenance_lib.py` (its `anchor.parent.glob` became `rglob`), `suggest_mutation_coverage_command.py`.

Latent findings surfaced by the widened shell universe: `scripts/run-quality.sh` (1341 lines) exceeds the new shell cap and is entered as a named, dated exemption retired by #769. No other file changed verdict.
