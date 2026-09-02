# Lane brief U2: doc and artifact universes (#769, Goal Run #765)

Follow `charness-artifacts/goal-runs/765/briefs/brief-769-u-common.md` first.

Your labels and the universes key each reads:

- `check-doc-links` (`scripts/doc_file_population.py:16-25` `DOC_GLOBS`),
  `docs-graph` (`scripts/check_docs_graph.py:52` `DEFAULT_SCAN_ROOT`, keep
  `--scan-root` as the override), `doc-duplicates`
  (`skills/public/quality/scripts/inventory_doc_duplicates.py:31-36`: scan
  `.` with charness-literal excludes becomes scanning the declared surfaces):
  `doc_surfaces`. `check_doc_links.py:562` prints "Validated markdown links."
  with no count; print the count and refuse per the contract when declared
  and empty.
- `check-spec-evidence-durability` (`scripts/check_spec_evidence_durability.py:30-60`),
  `check-artifact-referents` (`scripts/check_artifact_referents.py:229-232`,
  keep `--path`), `validate-critique-artifacts`
  (`scripts/critique_artifact_paths.py:13-14`), `validate-ideation-artifact`
  (`scripts/validate_ideation_artifact.py:20`): `artifact_roots.<family>`.
  Where a skill adapter already owns the directory
  (`.agents/critique-adapter.yaml` output dir, read by
  `validate_adapters.py:361-365`), the universes default for that family is
  derived from it, not duplicated; say which families derive.
- `validate-lesson-ledger` (`scripts/check_lesson_ledger.py:22-23`): read the
  retro adapter's `output_dir` and `summary_path` the way
  `scripts/build_retro_lesson_selection_index.py:32-48` does; an absent ledger
  is a discovered empty (the ledger is optional consumer memory), not an
  exception. `artifact_roots.retro` is the fallback when no retro adapter
  exists.

Scope: the files above plus `tests/quality_gates/test_check_doc_links.py`,
`tests/test_docs_graph_gate.py`, `tests/quality_gates/test_quality_doc_duplicates.py`,
`tests/quality_gates/test_check_spec_evidence_durability.py`,
`tests/quality_gates/test_artifact_referents.py`,
`tests/test_critique_artifact_validation.py`, `tests/test_ideation_artifact.py`,
`tests/quality_gates/test_empty_scope_refusals.py`, `tests/test_lesson_ledger.py`,
`tests/test_lesson_ledger_refusals.py`, and new tests. `scripts/artifact-referent-local-context.json`
stays charness-only; say so in the body.

Commit subject:
`quality: read doc and artifact universes from the adapter and the owning skill adapters (#769 U2 lane candidate)`
