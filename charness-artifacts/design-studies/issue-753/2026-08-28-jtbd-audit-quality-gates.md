# Issue #753: JTBD audit of tests/quality_gates

> Date: 2026-08-28. Operator direction: this JTBD audit replaces the
> issue's originally-recorded mutation-driven pass (step 2). Step 1
> (island/orphan inventory, same directory) found zero deletion
> candidates. Method: 12 parallel sonnet auditors, one cold
> jobs-to-be-done verdict per file (is the test needed; is the tested
> code needed), subject-consumer checks via `repograph explain`.
> Coverage: ALL 371 tracked files (79,000+ lines); an earlier draft of
> this artifact covered 234 files due to a synthesis truncation — the
> parent re-merged the complete batch data from the workflow journal.
> Dispositions are CANDIDATES; final disposition is parent-owned.

## Totals

| klass | files | lines |
| --- | --- | --- |
| behavioral-contract | 311 | 109,359 |
| meta-process-gate | 27 | 9,551 |
| mixed | 11 | 4,594 |
| fixture-support | 14 | 2,019 |
| change-detector-pin | 7 | 623 |
| duplicate-oracle | 1 | 117 |

| disposition | files | lines |
| --- | --- | --- |
| keep | 358 | 123,082 |
| trim-partial | 8 | 2,727 |
| convert-pin | 2 | 232 |
| delete-code-and-test | 1 | 127 |
| delete-test | 2 | 95 |

Reading: 358 of 371 files (96.5%) are clean keeps under a deliberately
cold standard; the candidate scope is 13 files / ~3,181 lines. The
load-bearing conclusion for #753: the meta-layer concentration named in
the issue is NOT deletable mass — by the audit's own standard the
checking machinery largely earns its keep, and the pin/prose problem is
concentrated in the 13 files below plus payload-pin conversion work.

## Deletion/conversion candidates (parent review pending)

### delete-code-and-test

- `tests/quality_gates/test_issue_audit_brief.py` (127 lines, meta-process-gate)
  - jtbd: The file's own docstring discloses this: audit_brief.py 'has no caller in the issue workflow today (the skill never invokes it)' - these tests pin the checker's own verdict logic (classification-before-mutation ordering), not an enforced repo boundary. Real defect class exists (omission disarming the contract) but nothing ships broken today if this file is deleted, since nothing currently runs the checker.
  - subject: skills/public/issue/scripts/audit_brief.py; subject needed: no (currently) - audit_brief.py is read only via runpy for a constant (KNOWN_CLASSIFICATIONS) by scripts/check_closeout_classification_parity.py and tests/coverage_debt/test_batch5.py; it is not invoked as a functioning checker by any skill workflow, and multiple charness-artifacts entries (2026-07-31 release notes, 2026-07-31 critique, 2026-07-31 goal S5) explicitly record the operator 'Rejected wiring audit_brief.py into the issue flow' as a deliberate, repeated decision
  - evidence: tests/quality_gates/test_issue_audit_brief.py:3-5 (explicit non-claim); charness-artifacts/critique/2026-07-31-release-3-0-1.md:155 ('audit_brief.py has no caller in that flow, so it cannot [prove production correctness]'); charness-artifacts/goals/2026-07-31-repair-the-sweep-s-remaining-high-rows-s5-density-exemption.md:208,258 (operator explicitly rejected wiring it in); tests/coverage_debt/test_batch5.py:390-468 also independently exercises audit_brief.py CLI shape, making part of this file's coverage a duplicate-oracle candidate as well

### delete-test

- `tests/quality_gates/test_prescribed_path_self_test_guidance.py` (30 lines, change-detector-pin)
  - jtbd: Cannot name a defect class distinct from 'someone reworded these three markdown docs': the single test asserts that specific literal substrings/phrases and a relative-link string appear across three prose documents; no production code is exercised.
  - subject: skills/public/create-skill/SKILL.md, skills/public/impl/SKILL.md, skills/shared/references/prescribed-path-self-test.md (documentation prose only, no code); subject needed: no code subject exists -- the 'subject' is documentation prose, not a script; the docs themselves are consumed by skill authors but no code behavior is verified
  - evidence: tests/quality_gates/test_prescribed_path_self_test_guidance.py:8-30 entire test body is `assert "<phrase>" in <doc text>` with no code import, no subprocess, no behavioral fixture
- `tests/quality_gates/test_retro_skill.py` (65 lines, change-detector-pin)
  - jtbd: Asserts specific phrases exist in SKILL.md/reference docs; does not verify the described CLI flags or behavior actually match the scripts, so a wording rewrite (not a defect) is what most reliably breaks it.
  - subject: skills/public/retro/SKILL.md and its references/*.md; subject needed: partial — SKILL.md is read by the skill-loading mechanism, but this test checks no loading behavior, only static prose substrings
  - evidence: tests/quality_gates/test_retro_skill.py:10-44 (pure substring assertions on markdown prose, no cross-check against the scripts they describe)

### convert-pin

- `tests/quality_gates/test_narrative_adapter.py` (45 lines, change-detector-pin)
  - jtbd: Cannot name a defect class distinct from 'this repo's own narrative-adapter.yaml prose changed shape': the single test asserts exact literal list/string values (brief_template, scenario_block_template, source_documents) read from THIS repo's live config file, so an intentional wording edit to that config breaks the test with no code-defect signal.
  - subject: skills/public/narrative/scripts/resolve_adapter.py; subject needed: yes - resolve_adapter.py is exercised, but its parsing logic is already covered with synthetic fixtures in test_narrative_scenario_blocks.py:83 (test_narrative_resolve_adapter_preserves_scenario_surface_fields)
  - evidence: tests/quality_gates/test_narrative_adapter.py:26-40 asserts exact equality on payload["data"]["brief_template"]/["scenario_block_template"] read from the live .agents/narrative-adapter.yaml; test_narrative_scenario_blocks.py:83-122 already exercises the same resolver logic against a synthetic fixture -- convert this to a smoke check (valid is True, expected keys present) rather than full literal-value pinning of live repo prose
- `tests/quality_gates/test_quality_tool_recommendations.py` (187 lines, mixed)
  - jtbd: Catches the tool-recommendation filter mis-scoping by recommendation-role/next-skill-id and the runtime-route recommendation payload's shape breaking for consumers.
  - subject: skills/public/quality/scripts/list_tool_recommendations.py, skills/public/narrative/scripts/list_tool_recommendations.py; subject needed: yes - documented as consumed via skills/public/quality/references/bootstrap-escalations.md
  - evidence: tests/quality_gates/test_quality_tool_recommendations.py:155-187 asserts full-dict equality on the recommendation payload, which breaks on any intended additive field the way the operator's named 'native_core' convert-pin class describes; the role-filter test at line 79-116 is a genuine behavioral-contract worth keeping as-is

### trim-partial

- `tests/quality_gates/test_critique_skill.py` (667 lines, mixed)
  - jtbd: Mixed: lines 1-178 are pure prose-substring pins on SKILL.md/reference content (weak, re-describes current doc wording); lines 213-667 drive the real validator against fixtures and catch genuine defects (e.g. missing-delegation-blocker phrase matching, structured findings bin/field validation, file-issue follow-up requirement).
  - subject: skills/public/critique/SKILL.md and references (mostly prose assertions); scripts/validate_critique_artifacts.py (structured-findings + subagent-delegation-blocker behavioral tests, lines 213-667); subject needed: yes for the validator half; docs half only partially needed (agent-consumed prose, but tests don't prove behavior)
  - evidence: tests/quality_gates/test_critique_skill.py:12-120 (pure prose assertions, no code exercised) vs :213-667 (real validator fixtures with genuine defect classes, e.g. :237-241, :567-579)
- `tests/quality_gates/test_issue_closeout_discipline.py` (245 lines, mixed)
  - jtbd: Mixed: most tests assert doc prose is present (weak, presence-only); one test (test_the_ledger_keys_the_docs_name_are_keys_the_create_helper_actually_emits) statically diffs documented ledger keys against issue_create.py's actual emitted keys, catching a real doc/code drift that would cause an agent to report nulls on a successful create and file a duplicate issue.
  - subject: skills/public/issue/SKILL.md + references docs, skills/public/issue/scripts/issue_create.py, publish_release_args.py; subject needed: yes: SKILL.md and issue_create.py are both live/consumed
  - evidence: tests/quality_gates/test_issue_closeout_discipline.py:47-110 is the real contract (keep); tests like :36-45 and :113-134 are pure 'assert substring in doc text' pins with no distinct defect class named beyond prose presence
- `tests/quality_gates/test_narrative_scenario_blocks.py` (206 lines, mixed)
  - jtbd: 4 of 6 tests catch real adapter-reading defects (scenario_surfaces dropped, volatile/missing paths not flagged, docs/index.md wrongly seeded as default source). The remaining 2 tests (scenario-block guidance wording, landing-rewrite-loop wording) only assert that specific prose phrases exist in SKILL.md/reference docs -- a doc reword breaks them with no code-defect signal.
  - subject: skills/public/narrative/scripts/resolve_adapter.py, review_adapter.py, init_adapter.py, plus SKILL.md/reference doc prose; subject needed: yes for the 4 behavioral tests (resolve/review/init_adapter.py are live narrative-skill scripts); the 2 prose tests exercise no code
  - evidence: tests/quality_gates/test_narrative_scenario_blocks.py:47-77 (test_narrative_skill_carries_scenario_block_guidance, test_narrative_skill_carries_landing_rewrite_contract) assert markdown substrings only; lines 83-206 (scenario_surfaces preservation, review_adapter volatile-path flagging, init_adapter default-source seeding) are genuine behavioral-contract tests -- trim the two prose-pin tests, keep the rest
- `tests/quality_gates/test_quality_bootstrap.py` (566 lines, mixed)
  - jtbd: Catches the bootstrap/resolve pipeline mis-merging preset defaults with explicit adapter customization (wrong preset lineage, dropped explicit commands, wrong field-status classification), which would silently reset or corrupt a consumer repo's quality-adapter configuration.
  - subject: scripts/quality_adapter_lib.py, scripts/quality_bootstrap_lib.py, scripts/quality_policy_defaults.py, scripts/simple_skill_adapter_lib.py; subject needed: yes: quality_adapter_lib/quality_bootstrap_lib drive every consumer repo's .agents/quality-adapter.yaml generation
  - evidence: tests/quality_gates/test_quality_bootstrap.py:41-77 asserts full-dict equality over ~35 field_statuses keys at once — an intended additive field to the adapter schema breaks this whole assertion with no localized signal (same convert-pin shape as the named native_core KeyError class); trim to targeted per-field checks, keep the rest of the file's behavioral coverage (e.g. :128-153 conflict detection, :200-218 preserves explicit commands) as-is
- `tests/quality_gates/test_quality_skill_docs.py` (472 lines, mixed)
  - jtbd: Mixed: most assertions pin that specific prose/keywords exist across cross-referencing SKILL.md/reference docs, which mostly re-describes current doc wording rather than a distinct defect class; but a minority (the step-8 tests) pin real doc/code consistency defects that shipped (e.g. #538: workflow step instructed --intent record while naming only a script that does not accept it).
  - subject: skills/public/quality/SKILL.md and references/*.md, skills/public/create-cli, skills/public/create-skill, skills/public/retro (documentation content); subject needed: yes - the docs are the live routing surface agents read (skills/public/quality/SKILL.md and references), not dead prose
  - evidence: tests/quality_gates/test_quality_skill_docs.py:390-471 (step-8 doc/code consistency tests, real defect class) is worth keeping; tests/quality_gates/test_quality_skill_docs.py:35-374 (bulk 'assert phrase X in doc Y' assertions with no distinct defect narrative) are prose change-detector pins worth trimming
- `tests/quality_gates/test_retro_memory.py` (69 lines, change-detector-pin)
  - jtbd: Ensures the retro-memory doc surfaces (AGENTS.md routing cue and dogfood detail split) stay in the intended shape; if AGENTS.md ever regrows the detail meant to live only in development.md, this is the only check that would catch it.
  - subject: AGENTS.md, docs/development.md, skills/public/retro/SKILL.md, references/adapter-contract.md, charness-artifacts/retro/recent-lessons.md; subject needed: partial — AGENTS.md/docs are read by humans and by charness:setup tooling, not by production code
  - evidence: tests/quality_gates/test_retro_memory.py:50-69 (prose substring pins with no executable behavior under test)
- `tests/quality_gates/test_skill_docs_contracts.py` (461 lines, mixed)
  - jtbd: Catches unrelated edits to skill instruction files silently deleting operator-critical guidance (e.g. the live-spawn execution contract, the HITL 'never edit mid-chunk' rule, the source/plugin-mirror byte-identity requirement) that downstream agent sessions rely on as their actual operating contract.
  - subject: skills/public/{setup,quality,critique,debug,prove,impl,hitl}/SKILL.md and their references/ files; docs/development.md, docs/control-plane.md, docs/public-skill-validation.md; subject needed: yes — these SKILL.md/reference files are the executable prompt surface consumed directly by agent sessions running the skills
  - evidence: most assertions (e.g. lines 128-194 for hitl) are exact-substring pins on natural-language prose across ~10 unrelated skills bundled into one 461-line module; an intentional rewording (not a behavior regression) breaks the test while telling the author only 'string not found', the change-detector-pin failure mode — recommend splitting per-skill and loosening substring matches to key concepts rather than exact wording, while keeping the byte-identity mirror checks (e.g. lines 259-266, 62, 410-413) which are genuine behavioral contracts
- `tests/quality_gates/test_source_bound_records_guidance.py` (41 lines, mixed)
  - jtbd: The cross-file wiring asserts (lines 39-41: reference link present in spec/impl/create-cli docs) catch an orphaned shared-reference regression; the ~10 exact-vocabulary asserts (lines 27-38: 'SourceRecord', 'ExtractionCandidate', etc.) only catch a doc author rewording the concept, which is a shape change not a defect distinct from the doc simply being edited.
  - subject: skills/shared/references/source-bound-records.md, and its links from create-skill/create-cli/spec/impl SKILL.md docs (documentation content, no production code); subject needed: yes for the shared doc itself (linked from 4 public skills); the exhaustive vocabulary pinned within it is not separately load-bearing
  - evidence: tests/quality_gates/test_source_bound_records_guidance.py:26-38 (11 literal substring pins on prose) vs :39-41 (real cross-file link contract)

## Parent verification of top candidates (2026-08-28)

- `test_issue_audit_brief.py` (delete-code-and-test): REFUTED as stated.
  `scripts/check_closeout_classification_parity.py` (a standing run-quality
  gate) reads `audit_brief.py`'s `KNOWN_CLASSIFICATIONS` /
  `REQUIRE_BRIEF_CLASSIFICATIONS` module attributes as a parity surface
  (check_closeout_classification_parity.py:92,238-240), so the subject is
  not caller-free. Downgraded to: needs its own disposition (the CLI may be
  dead while the constants are live); no deletion on this audit alone.
- `test_prescribed_path_self_test_guidance.py` (delete-test): CONFIRMED —
  the entire body is doc-prose substring asserts, no code exercised.
  DELETED in this pass.
- `test_retro_skill.py` (delete-test): CONFIRMED — 27 prose-substring
  asserts over SKILL.md/reference text, no code exercised. DELETED in this
  pass.
- convert-pin (2) and trim-partial (8) candidates: recorded as follow-up
  work items; each needs an editing pass, not a deletion, and stays pending
  parent execution.

## Full per-file table

| path | lines | klass | disposition |
| --- | --- | --- | --- |
| tests/quality_gates/__init__.py | 1 | fixture-support | keep |
| tests/quality_gates/fixtures/release_publish_distinct_channel_probe.py | 19 | fixture-support | keep |
| tests/quality_gates/fixtures/release_publish_fake_gh.py | 55 | fixture-support | keep |
| tests/quality_gates/fixtures/release_publish_sync_root_plugin_manifests.py | 34 | fixture-support | keep |
| tests/quality_gates/issue_closeout_support.py | 95 | fixture-support | keep |
| tests/quality_gates/mutation_coverage_producer_fixtures.py | 26 | fixture-support | keep |
| tests/quality_gates/quality_bootstrap_support.py | 226 | fixture-support | keep |
| tests/quality_gates/release_publish_fixtures.py | 407 | fixture-support | keep |
| tests/quality_gates/release_script_loading.py | 11 | fixture-support | keep |
| tests/quality_gates/reviewer_capability_support.py | 110 | fixture-support | keep |
| tests/quality_gates/skill_ergonomics_support.py | 35 | fixture-support | keep |
| tests/quality_gates/support.py | 764 | fixture-support | keep |
| tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py | 573 | behavioral-contract | keep |
| tests/quality_gates/test_a_refused_verdict_states_its_refusal.py | 270 | behavioral-contract | keep |
| tests/quality_gates/test_absent_input_is_not_a_matching_input.py | 989 | behavioral-contract | keep |
| tests/quality_gates/test_achieve_adapter_policy.py | 107 | behavioral-contract | keep |
| tests/quality_gates/test_achieve_before_activation.py | 50 | behavioral-contract | keep |
| tests/quality_gates/test_achieve_goal_run_pickup.py | 352 | behavioral-contract | keep |
| tests/quality_gates/test_achieve_interview_contract.py | 111 | behavioral-contract | keep |
| tests/quality_gates/test_adapter_lib_yaml.py | 307 | behavioral-contract | keep |
| tests/quality_gates/test_adapter_version_reconciliation.py | 566 | behavioral-contract | keep |
| tests/quality_gates/test_adapter_version_refusal_is_loud.py | 396 | behavioral-contract | keep |
| tests/quality_gates/test_announcement_version_refusal.py | 303 | behavioral-contract | keep |
| tests/quality_gates/test_argparse_surface_lib.py | 350 | behavioral-contract | keep |
| tests/quality_gates/test_artifact_naming.py | 670 | behavioral-contract | keep |
| tests/quality_gates/test_artifact_path_refuses_an_unhonored_adapter.py | 114 | behavioral-contract | keep |
| tests/quality_gates/test_artifact_producer_order.py | 67 | behavioral-contract | keep |
| tests/quality_gates/test_artifact_referents.py | 593 | behavioral-contract | keep |
| tests/quality_gates/test_artifact_validator_units.py | 295 | behavioral-contract | keep |
| tests/quality_gates/test_attention_state_visibility.py | 292 | behavioral-contract | keep |
| tests/quality_gates/test_bootstrap_visibility.py | 82 | behavioral-contract | keep |
| tests/quality_gates/test_boundary_bypass_payload_validator.py | 76 | behavioral-contract | keep |
| tests/quality_gates/test_bounded_reviewer_envelope.py | 40 | behavioral-contract | keep |
| tests/quality_gates/test_changed_line_coverage_gate.py | 543 | behavioral-contract | keep |
| tests/quality_gates/test_changed_line_mutation_coverage.py | 1058 | behavioral-contract | keep |
| tests/quality_gates/test_changed_line_proof_cost.py | 307 | behavioral-contract | keep |
| tests/quality_gates/test_changed_line_reviewer_consumer_gaps.py | 228 | behavioral-contract | keep |
| tests/quality_gates/test_changed_line_scope_counts.py | 268 | behavioral-contract | keep |
| tests/quality_gates/test_changed_line_verdict_codes.py | 59 | behavioral-contract | keep |
| tests/quality_gates/test_check_artifact_surface_preflight.py | 804 | behavioral-contract | keep |
| tests/quality_gates/test_check_bootstrap_shim_consistency.py | 167 | behavioral-contract | keep |
| tests/quality_gates/test_check_coverage_inventory.py | 383 | behavioral-contract | keep |
| tests/quality_gates/test_check_doc_links.py | 835 | behavioral-contract | keep |
| tests/quality_gates/test_check_git_identity.py | 167 | behavioral-contract | keep |
| tests/quality_gates/test_check_markdown_inline_code.py | 60 | behavioral-contract | keep |
| tests/quality_gates/test_check_mutation_run_proof.py | 443 | behavioral-contract | keep |
| tests/quality_gates/test_check_mutation_score_partial.py | 170 | behavioral-contract | keep |
| tests/quality_gates/test_check_plugin_doc_links.py | 346 | behavioral-contract | keep |
| tests/quality_gates/test_check_prose_pin.py | 111 | behavioral-contract | keep |
| tests/quality_gates/test_check_public_doc_coupling.py | 131 | behavioral-contract | keep |
| tests/quality_gates/test_check_skill_cut_safety.py | 331 | behavioral-contract | keep |
| tests/quality_gates/test_check_spec_evidence_durability.py | 397 | behavioral-contract | keep |
| tests/quality_gates/test_check_staged_reversion.py | 295 | behavioral-contract | keep |
| tests/quality_gates/test_check_staged_worktree_consistency.py | 492 | behavioral-contract | keep |
| tests/quality_gates/test_check_symbol_residue.py | 90 | behavioral-contract | keep |
| tests/quality_gates/test_check_test_completeness.py | 143 | behavioral-contract | keep |
| tests/quality_gates/test_ci_recoverable_gates.py | 221 | behavioral-contract | keep |
| tests/quality_gates/test_claims_review_scope.py | 561 | behavioral-contract | keep |
| tests/quality_gates/test_classify_push_diff.py | 159 | behavioral-contract | keep |
| tests/quality_gates/test_claude_session_jsonl_audit.py | 106 | behavioral-contract | keep |
| tests/quality_gates/test_cli_skill_surface.py | 777 | behavioral-contract | keep |
| tests/quality_gates/test_closeout_authorization_coverage.py | 448 | behavioral-contract | keep |
| tests/quality_gates/test_closeout_authorization_ingress.py | 446 | behavioral-contract | keep |
| tests/quality_gates/test_closeout_discipline_propagation.py | 146 | change-detector-pin | keep |
| tests/quality_gates/test_closeout_headroom_and_mirror_gate.py | 191 | behavioral-contract | keep |
| tests/quality_gates/test_codex_session_audit_tokens.py | 204 | behavioral-contract | keep |
| tests/quality_gates/test_codex_session_jsonl_audit.py | 143 | behavioral-contract | keep |
| tests/quality_gates/test_command_docs_gate.py | 415 | behavioral-contract | keep |
| tests/quality_gates/test_command_dominance.py | 672 | behavioral-contract | keep |
| tests/quality_gates/test_command_plan_preflight.py | 506 | behavioral-contract | keep |
| tests/quality_gates/test_coverage_builder_policy_parity.py | 285 | behavioral-contract | keep |
| tests/quality_gates/test_coverage_floor_inventory_reference.py | 334 | behavioral-contract | keep |
| tests/quality_gates/test_create_skill_adapter.py | 210 | behavioral-contract | keep |
| tests/quality_gates/test_critique_boundary_ownership_presence.py | 279 | behavioral-contract | keep |
| tests/quality_gates/test_critique_delivery_state_floor.py | 186 | behavioral-contract | keep |
| tests/quality_gates/test_critique_enforcement_scope.py | 945 | behavioral-contract | keep |
| tests/quality_gates/test_critique_first_reader_lens.py | 54 | change-detector-pin | keep |
| tests/quality_gates/test_critique_fresh_eye_presence.py | 370 | behavioral-contract | keep |
| tests/quality_gates/test_critique_skill.py | 667 | mixed | trim-partial |
| tests/quality_gates/test_current_pointer_freshness.py | 437 | behavioral-contract | keep |
| tests/quality_gates/test_current_pointer_writers.py | 556 | behavioral-contract | keep |
| tests/quality_gates/test_current_pointer_writes.py | 791 | behavioral-contract | keep |
| tests/quality_gates/test_current_release_version_refusal.py | 76 | behavioral-contract | keep |
| tests/quality_gates/test_debug_rca_reference_cite_chain.py | 214 | change-detector-pin | keep |
| tests/quality_gates/test_debug_seam_risk_index.py | 327 | behavioral-contract | keep |
| tests/quality_gates/test_distinct_mutation_coverage.py | 220 | behavioral-contract | keep |
| tests/quality_gates/test_docs_and_misc.py | 240 | behavioral-contract | keep |
| tests/quality_gates/test_documented_command_flags.py | 971 | behavioral-contract | keep |
| tests/quality_gates/test_documented_subcommands.py | 391 | behavioral-contract | keep |
| tests/quality_gates/test_dup_family_lineage.py | 82 | behavioral-contract | keep |
| tests/quality_gates/test_dup_ratchet.py | 1095 | behavioral-contract | keep |
| tests/quality_gates/test_dup_ratchet_baseline.py | 141 | behavioral-contract | keep |
| tests/quality_gates/test_dup_ratchet_edit_advisory.py | 499 | behavioral-contract | keep |
| tests/quality_gates/test_dup_ratchet_lineage.py | 180 | behavioral-contract | keep |
| tests/quality_gates/test_dup_ratchet_reductions.py | 97 | behavioral-contract | keep |
| tests/quality_gates/test_dup_ratchet_scope_coverage.py | 645 | behavioral-contract | keep |
| tests/quality_gates/test_dup_ratchet_scoped_rebaseline.py | 431 | behavioral-contract | keep |
| tests/quality_gates/test_dup_ratchet_triage.py | 137 | behavioral-contract | keep |
| tests/quality_gates/test_dup_ratchet_triage_draft.py | 348 | behavioral-contract | keep |
| tests/quality_gates/test_dup_ratchet_unestablished_inputs.py | 149 | behavioral-contract | keep |
| tests/quality_gates/test_dup_review_seed.py | 409 | behavioral-contract | keep |
| tests/quality_gates/test_empty_scope_refusals.py | 718 | behavioral-contract | keep |
| tests/quality_gates/test_every_resolver_answers_a_refused_document.py | 181 | behavioral-contract | keep |
| tests/quality_gates/test_export_self_sufficiency.py | 845 | behavioral-contract | keep |
| tests/quality_gates/test_gate_summary_names_failures.py | 240 | behavioral-contract | keep |
| tests/quality_gates/test_gather_provider.py | 132 | behavioral-contract | keep |
| tests/quality_gates/test_gather_symlink_safety.py | 352 | behavioral-contract | keep |
| tests/quality_gates/test_goal_artifact_lib.py | 103 | behavioral-contract | keep |
| tests/quality_gates/test_goal_artifact_producers.py | 38 | behavioral-contract | keep |
| tests/quality_gates/test_goal_artifact_scaffold.py | 42 | behavioral-contract | keep |
| tests/quality_gates/test_goal_binding_v1.py | 581 | behavioral-contract | keep |
| tests/quality_gates/test_goal_evidence_lineage.py | 119 | behavioral-contract | keep |
| tests/quality_gates/test_goal_lineage_consumers.py | 116 | behavioral-contract | keep |
| tests/quality_gates/test_hardcoded_discovery.py | 124 | behavioral-contract | keep |
| tests/quality_gates/test_helper_provenance_guard.py | 726 | behavioral-contract | keep |
| tests/quality_gates/test_hitl_bootstrap_version_refusal.py | 97 | behavioral-contract | keep |
| tests/quality_gates/test_hitl_chunk_contract.py | 286 | behavioral-contract | keep |
| tests/quality_gates/test_hitl_report_mode.py | 584 | behavioral-contract | keep |
| tests/quality_gates/test_hot_path_import_weight.py | 59 | behavioral-contract | keep |
| tests/quality_gates/test_hotl_adapter.py | 229 | behavioral-contract | keep |
| tests/quality_gates/test_inference_interpretation_meta_validator.py | 292 | meta-process-gate | keep |
| tests/quality_gates/test_inventory_ci_local_gate_parity.py | 837 | behavioral-contract | keep |
| tests/quality_gates/test_inventory_consumption.py | 336 | behavioral-contract | keep |
| tests/quality_gates/test_issue_audit_brief.py | 127 | meta-process-gate | delete-code-and-test |
| tests/quality_gates/test_issue_close_comment_floor.py | 546 | behavioral-contract | keep |
| tests/quality_gates/test_issue_close_preflight_readback.py | 68 | behavioral-contract | keep |
| tests/quality_gates/test_issue_closeout_commit_msg_hook.py | 777 | behavioral-contract | keep |
| tests/quality_gates/test_issue_closeout_discipline.py | 245 | mixed | trim-partial |
| tests/quality_gates/test_issue_closeout_draft_validation.py | 277 | behavioral-contract | keep |
| tests/quality_gates/test_issue_closeout_ledger_counts.py | 252 | behavioral-contract | keep |
| tests/quality_gates/test_issue_closeout_rung1_floors.py | 485 | behavioral-contract | keep |
| tests/quality_gates/test_issue_closeout_verifier.py | 786 | behavioral-contract | keep |
| tests/quality_gates/test_issue_closeout_verifier_critique.py | 524 | behavioral-contract | keep |
| tests/quality_gates/test_issue_consolidated_closeout.py | 425 | behavioral-contract | keep |
| tests/quality_gates/test_issue_consolidation_readback.py | 442 | behavioral-contract | keep |
| tests/quality_gates/test_issue_create.py | 834 | behavioral-contract | keep |
| tests/quality_gates/test_issue_create_failure_branches.py | 66 | behavioral-contract | keep |
| tests/quality_gates/test_issue_critique_observer.py | 718 | behavioral-contract | keep |
| tests/quality_gates/test_issue_goal_run.py | 338 | behavioral-contract | keep |
| tests/quality_gates/test_issue_preflight.py | 214 | behavioral-contract | keep |
| tests/quality_gates/test_issue_proposal_fields.py | 152 | behavioral-contract | keep |
| tests/quality_gates/test_issue_provider_selection.py | 121 | behavioral-contract | keep |
| tests/quality_gates/test_issue_read.py | 188 | behavioral-contract | keep |
| tests/quality_gates/test_issue_skill.py | 873 | behavioral-contract | keep |
| tests/quality_gates/test_issue_source_preservation.py | 219 | behavioral-contract | keep |
| tests/quality_gates/test_issue_tool_runners.py | 493 | behavioral-contract | keep |
| tests/quality_gates/test_issue_tracker.py | 593 | behavioral-contract | keep |
| tests/quality_gates/test_issue_tracker_observation.py | 159 | behavioral-contract | keep |
| tests/quality_gates/test_issue_worker_carrier.py | 684 | behavioral-contract | keep |
| tests/quality_gates/test_js_mutation_tooling.py | 358 | meta-process-gate | keep |
| tests/quality_gates/test_maintainer_hooks.py | 227 | behavioral-contract | keep |
| tests/quality_gates/test_manage_mutation_reports.py | 296 | behavioral-contract | keep |
| tests/quality_gates/test_markdown_doc_scan.py | 95 | behavioral-contract | keep |
| tests/quality_gates/test_markdown_lint_resolution.py | 245 | behavioral-contract | keep |
| tests/quality_gates/test_measure_evidence_residual.py | 155 | meta-process-gate | keep |
| tests/quality_gates/test_mutate_and_restore.py | 1065 | behavioral-contract | keep |
| tests/quality_gates/test_mutation_annotation_filter.py | 179 | behavioral-contract | keep |
| tests/quality_gates/test_mutation_baseline_abort.py | 891 | behavioral-contract | keep |
| tests/quality_gates/test_mutation_changed_line_targets.py | 118 | behavioral-contract | keep |
| tests/quality_gates/test_mutation_coverage_probe.py | 68 | behavioral-contract | keep |
| tests/quality_gates/test_mutation_coverage_producer.py | 316 | behavioral-contract | keep |
| tests/quality_gates/test_mutation_issue_report_body.py | 502 | behavioral-contract | keep |
| tests/quality_gates/test_mutation_recovery.py | 611 | mixed | keep |
| tests/quality_gates/test_mutation_sampling_line_coverage.py | 271 | behavioral-contract | keep |
| tests/quality_gates/test_mutation_test_reporters.py | 717 | behavioral-contract | keep |
| tests/quality_gates/test_mutation_workflow_install.py | 162 | behavioral-contract | keep |
| tests/quality_gates/test_narrative_adapter.py | 45 | change-detector-pin | convert-pin |
| tests/quality_gates/test_narrative_impl_version_refusal.py | 176 | behavioral-contract | keep |
| tests/quality_gates/test_narrative_scenario_blocks.py | 206 | mixed | trim-partial |
| tests/quality_gates/test_native_gate_lib.py | 202 | behavioral-contract | keep |
| tests/quality_gates/test_nose_fingerprint.py | 244 | behavioral-contract | keep |
| tests/quality_gates/test_packaging_support_capabilities.py | 20 | behavioral-contract | keep |
| tests/quality_gates/test_packaging_validation.py | 668 | behavioral-contract | keep |
| tests/quality_gates/test_parents_index_layout_invariant.py | 172 | behavioral-contract | keep |
| tests/quality_gates/test_parity_harness.py | 620 | behavioral-contract | keep |
| tests/quality_gates/test_plugin_asset_command_carriers.py | 180 | behavioral-contract | keep |
| tests/quality_gates/test_plugin_dir_references.py | 282 | behavioral-contract | keep |
| tests/quality_gates/test_portable_json_artifacts.py | 447 | behavioral-contract | keep |
| tests/quality_gates/test_premise_preflight.py | 672 | behavioral-contract | keep |
| tests/quality_gates/test_prepush_close_keyword_guard.py | 1004 | behavioral-contract | keep |
| tests/quality_gates/test_prepush_runtime_regime.py | 194 | behavioral-contract | keep |
| tests/quality_gates/test_prescribed_path_self_test_guidance.py | 30 | change-detector-pin | delete-test |
| tests/quality_gates/test_prescribed_skill_executed.py | 722 | behavioral-contract | keep |
| tests/quality_gates/test_probe_record_corpus_replays.py | 76 | meta-process-gate | keep |
| tests/quality_gates/test_probe_record_floor.py | 467 | behavioral-contract | keep |
| tests/quality_gates/test_profile_and_preset_validation.py | 734 | behavioral-contract | keep |
| tests/quality_gates/test_prompt_bulk_version_refusal.py | 142 | behavioral-contract | keep |
| tests/quality_gates/test_proof_mismatch.py | 149 | behavioral-contract | keep |
| tests/quality_gates/test_proof_receipt.py | 174 | behavioral-contract | keep |
| tests/quality_gates/test_proof_semantics_adapter.py | 237 | behavioral-contract | keep |
| tests/quality_gates/test_provider_boundary.py | 199 | behavioral-contract | keep |
| tests/quality_gates/test_public_skill_dogfood.py | 89 | mixed | keep |
| tests/quality_gates/test_public_skill_yaml_output_contract.py | 620 | behavioral-contract | keep |
| tests/quality_gates/test_python_and_security_gates.py | 669 | meta-process-gate | keep |
| tests/quality_gates/test_python_filename_convention.py | 24 | behavioral-contract | keep |
| tests/quality_gates/test_python_length_gates.py | 303 | behavioral-contract | keep |
| tests/quality_gates/test_python_length_interpretation.py | 126 | behavioral-contract | keep |
| tests/quality_gates/test_quality_adapter_block_rejections.py | 690 | behavioral-contract | keep |
| tests/quality_gates/test_quality_adapter_gate_design.py | 98 | meta-process-gate | keep |
| tests/quality_gates/test_quality_artifact_date_coherence.py | 150 | behavioral-contract | keep |
| tests/quality_gates/test_quality_bootstrap.py | 566 | mixed | trim-partial |
| tests/quality_gates/test_quality_bootstrap_absence.py | 970 | behavioral-contract | keep |
| tests/quality_gates/test_quality_bootstrap_lifecycle.py | 328 | behavioral-contract | keep |
| tests/quality_gates/test_quality_brittle_source_guards.py | 255 | meta-process-gate | keep |
| tests/quality_gates/test_quality_cli_ergonomics.py | 150 | meta-process-gate | keep |
| tests/quality_gates/test_quality_cli_side_effect_probes.py | 322 | meta-process-gate | keep |
| tests/quality_gates/test_quality_dead_code_advisory.py | 829 | meta-process-gate | keep |
| tests/quality_gates/test_quality_declaration_path_resolution.py | 589 | behavioral-contract | keep |
| tests/quality_gates/test_quality_doc_duplicates.py | 218 | meta-process-gate | keep |
| tests/quality_gates/test_quality_dual_implementation.py | 79 | behavioral-contract | keep |
| tests/quality_gates/test_quality_entrypoint_docs_ergonomics.py | 203 | meta-process-gate | keep |
| tests/quality_gates/test_quality_ergonomics_interpretation.py | 37 | behavioral-contract | keep |
| tests/quality_gates/test_quality_gitignore_scan_hygiene.py | 166 | meta-process-gate | keep |
| tests/quality_gates/test_quality_lint_ignores.py | 372 | meta-process-gate | keep |
| tests/quality_gates/test_quality_markdown_preview_bootstrap.py | 180 | behavioral-contract | keep |
| tests/quality_gates/test_quality_mutation_coverage.py | 130 | behavioral-contract | keep |
| tests/quality_gates/test_quality_mutation_sampling.py | 785 | behavioral-contract | keep |
| tests/quality_gates/test_quality_mutation_score_validity.py | 680 | behavioral-contract | keep |
| tests/quality_gates/test_quality_mutation_testing.py | 847 | behavioral-contract | keep |
| tests/quality_gates/test_quality_nose_advisory.py | 459 | behavioral-contract | keep |
| tests/quality_gates/test_quality_nose_scope_inprocess.py | 174 | behavioral-contract | keep |
| tests/quality_gates/test_quality_policy_merge.py | 232 | behavioral-contract | keep |
| tests/quality_gates/test_quality_policy_merge_import.py | 57 | behavioral-contract | keep |
| tests/quality_gates/test_quality_public_spec_quality.py | 659 | behavioral-contract | keep |
| tests/quality_gates/test_quality_readers_version_refusal.py | 194 | behavioral-contract | keep |
| tests/quality_gates/test_quality_run_gate_packets.py | 31 | behavioral-contract | keep |
| tests/quality_gates/test_quality_run_planner.py | 953 | behavioral-contract | keep |
| tests/quality_gates/test_quality_run_planner_adapter_scope.py | 80 | behavioral-contract | keep |
| tests/quality_gates/test_quality_run_read_measurement.py | 63 | behavioral-contract | keep |
| tests/quality_gates/test_quality_runner.py | 847 | behavioral-contract | keep |
| tests/quality_gates/test_quality_runner_coverage_selection.py | 110 | behavioral-contract | keep |
| tests/quality_gates/test_quality_runner_exit_status.py | 199 | behavioral-contract | keep |
| tests/quality_gates/test_quality_runner_label_universe.py | 72 | behavioral-contract | keep |
| tests/quality_gates/test_quality_runner_nose_scope.py | 48 | behavioral-contract | keep |
| tests/quality_gates/test_quality_runner_progress.py | 43 | behavioral-contract | keep |
| tests/quality_gates/test_quality_runner_release_order.py | 225 | behavioral-contract | keep |
| tests/quality_gates/test_quality_runner_runtime_aggregate.py | 620 | behavioral-contract | keep |
| tests/quality_gates/test_quality_runner_unproven.py | 112 | behavioral-contract | keep |
| tests/quality_gates/test_quality_runtime_recorder.py | 533 | behavioral-contract | keep |
| tests/quality_gates/test_quality_skill_docs.py | 472 | mixed | trim-partial |
| tests/quality_gates/test_quality_skill_ergonomics.py | 781 | behavioral-contract | keep |
| tests/quality_gates/test_quality_skill_ergonomics_summary.py | 132 | behavioral-contract | keep |
| tests/quality_gates/test_quality_sloc_inventory.py | 125 | behavioral-contract | keep |
| tests/quality_gates/test_quality_standing_gate_verbosity.py | 342 | behavioral-contract | keep |
| tests/quality_gates/test_quality_tool_fixtures.py | 402 | behavioral-contract | keep |
| tests/quality_gates/test_quality_tool_recommendations.py | 187 | mixed | convert-pin |
| tests/quality_gates/test_real_host_proof_version_refusal.py | 102 | behavioral-contract | keep |
| tests/quality_gates/test_recent_lessons_refresh.py | 143 | behavioral-contract | keep |
| tests/quality_gates/test_regenerable_facts.py | 565 | behavioral-contract | keep |
| tests/quality_gates/test_release_backend.py | 499 | behavioral-contract | keep |
| tests/quality_gates/test_release_backend_agrees_with_the_owner.py | 160 | behavioral-contract | keep |
| tests/quality_gates/test_release_changed_line_coverage.py | 702 | behavioral-contract | keep |
| tests/quality_gates/test_release_claims_in_process.py | 117 | duplicate-oracle | keep |
| tests/quality_gates/test_release_claims_review.py | 971 | behavioral-contract | keep |
| tests/quality_gates/test_release_closeout_authorization_coverage.py | 359 | behavioral-contract | keep |
| tests/quality_gates/test_release_distinct_channel.py | 1015 | behavioral-contract | keep |
| tests/quality_gates/test_release_failure_record.py | 154 | behavioral-contract | keep |
| tests/quality_gates/test_release_fresh_checkout_probes.py | 201 | behavioral-contract | keep |
| tests/quality_gates/test_release_issue_closeout_behavioral_floor.py | 462 | behavioral-contract | keep |
| tests/quality_gates/test_release_issue_closeout_preflight.py | 482 | behavioral-contract | keep |
| tests/quality_gates/test_release_issue_ledger.py | 632 | behavioral-contract | keep |
| tests/quality_gates/test_release_narrative_audit.py | 827 | behavioral-contract | keep |
| tests/quality_gates/test_release_narrative_containment.py | 272 | behavioral-contract | keep |
| tests/quality_gates/test_release_narrative_gate.py | 274 | behavioral-contract | keep |
| tests/quality_gates/test_release_notes_claims.py | 552 | behavioral-contract | keep |
| tests/quality_gates/test_release_observer.py | 508 | behavioral-contract | keep |
| tests/quality_gates/test_release_only_sentinel_inventory.py | 264 | meta-process-gate | keep |
| tests/quality_gates/test_release_planner_version_refusal.py | 119 | behavioral-contract | keep |
| tests/quality_gates/test_release_publish.py | 843 | behavioral-contract | keep |
| tests/quality_gates/test_release_publish_critique_artifact.py | 173 | behavioral-contract | keep |
| tests/quality_gates/test_release_publish_fake_git.py | 92 | fixture-support | keep |
| tests/quality_gates/test_release_publish_provenance.py | 88 | behavioral-contract | keep |
| tests/quality_gates/test_release_publish_real_host_delta.py | 725 | behavioral-contract | keep |
| tests/quality_gates/test_release_publish_resilience.py | 1049 | mixed | keep |
| tests/quality_gates/test_release_publish_rollback.py | 256 | behavioral-contract | keep |
| tests/quality_gates/test_release_publish_tag_history.py | 203 | behavioral-contract | keep |
| tests/quality_gates/test_release_quality_gate_visibility.py | 134 | behavioral-contract | keep |
| tests/quality_gates/test_release_quality_status_binding.py | 165 | behavioral-contract | keep |
| tests/quality_gates/test_release_real_host.py | 637 | behavioral-contract | keep |
| tests/quality_gates/test_release_resume_edge_coverage.py | 949 | behavioral-contract | keep |
| tests/quality_gates/test_release_resume_publish_integration.py | 91 | behavioral-contract | keep |
| tests/quality_gates/test_release_resume_state_validation.py | 161 | behavioral-contract | keep |
| tests/quality_gates/test_release_resume_surface_revalidation.py | 70 | behavioral-contract | keep |
| tests/quality_gates/test_release_run_planner.py | 872 | behavioral-contract | keep |
| tests/quality_gates/test_removed_name_consumers.py | 457 | behavioral-contract | keep |
| tests/quality_gates/test_repo_copy_invariants.py | 476 | behavioral-contract | keep |
| tests/quality_gates/test_requested_review_gate_version_refusal.py | 132 | behavioral-contract | keep |
| tests/quality_gates/test_retention_refusal_coverage.py | 246 | behavioral-contract | keep |
| tests/quality_gates/test_retro_artifact_validation.py | 461 | behavioral-contract | keep |
| tests/quality_gates/test_retro_auto_trigger.py | 340 | behavioral-contract | keep |
| tests/quality_gates/test_retro_codex_session_audit.py | 333 | behavioral-contract | keep |
| tests/quality_gates/test_retro_host_log_probe.py | 156 | behavioral-contract | keep |
| tests/quality_gates/test_retro_installed_plan_path.py | 75 | behavioral-contract | keep |
| tests/quality_gates/test_retro_lesson_selection_index.py | 323 | behavioral-contract | keep |
| tests/quality_gates/test_retro_memory.py | 69 | change-detector-pin | trim-partial |
| tests/quality_gates/test_retro_persistence.py | 553 | behavioral-contract | keep |
| tests/quality_gates/test_retro_skill.py | 65 | change-detector-pin | delete-test |
| tests/quality_gates/test_reviewer_boundary_fingerprint.py | 475 | behavioral-contract | keep |
| tests/quality_gates/test_reviewer_boundary_portability.py | 80 | behavioral-contract | keep |
| tests/quality_gates/test_reviewer_capability.py | 335 | behavioral-contract | keep |
| tests/quality_gates/test_reviewer_delivery_integration.py | 146 | behavioral-contract | keep |
| tests/quality_gates/test_reviewer_delivery_state_machine.py | 285 | behavioral-contract | keep |
| tests/quality_gates/test_reviewer_result.py | 413 | behavioral-contract | keep |
| tests/quality_gates/test_reviewer_result_delivery.py | 90 | behavioral-contract | keep |
| tests/quality_gates/test_reviewer_runner.py | 309 | behavioral-contract | keep |
| tests/quality_gates/test_reviewer_tier_policy.py | 222 | behavioral-contract | keep |
| tests/quality_gates/test_reviewer_worker.py | 363 | behavioral-contract | keep |
| tests/quality_gates/test_reviewer_worker_capability.py | 89 | behavioral-contract | keep |
| tests/quality_gates/test_reviewer_worker_report.py | 311 | behavioral-contract | keep |
| tests/quality_gates/test_run_cosmic_ray_mutation_resilience.py | 446 | behavioral-contract | keep |
| tests/quality_gates/test_runtime_budget_consumer_universe.py | 163 | behavioral-contract | keep |
| tests/quality_gates/test_runtime_budget_gate.py | 783 | behavioral-contract | keep |
| tests/quality_gates/test_runtime_budget_gate_profiles.py | 193 | behavioral-contract | keep |
| tests/quality_gates/test_runtime_budget_unenforceable.py | 113 | behavioral-contract | keep |
| tests/quality_gates/test_runtime_budget_universe.py | 705 | behavioral-contract | keep |
| tests/quality_gates/test_runtime_summary_render.py | 272 | behavioral-contract | keep |
| tests/quality_gates/test_runtime_timing_log_ingest.py | 312 | behavioral-contract | keep |
| tests/quality_gates/test_s6_changed_line_gaps.py | 227 | behavioral-contract | keep |
| tests/quality_gates/test_s6b2_changed_line_gaps.py | 866 | behavioral-contract | keep |
| tests/quality_gates/test_scaffold_changed_line_coverage.py | 137 | behavioral-contract | keep |
| tests/quality_gates/test_scaffold_version_refusal.py | 224 | behavioral-contract | keep |
| tests/quality_gates/test_script_inprocess_behaviors.py | 311 | behavioral-contract | keep |
| tests/quality_gates/test_seed_cache_eviction.py | 144 | fixture-support | keep |
| tests/quality_gates/test_seed_fixture_budget_gate.py | 749 | behavioral-contract | keep |
| tests/quality_gates/test_seed_worktree_adapter.py | 350 | behavioral-contract | keep |
| tests/quality_gates/test_semantic_review_command.py | 329 | behavioral-contract | keep |
| tests/quality_gates/test_setup_adapter_scaffold_policy.py | 36 | behavioral-contract | keep |
| tests/quality_gates/test_setup_hook_failure_guidance.py | 304 | behavioral-contract | keep |
| tests/quality_gates/test_setup_inspect_adapters.py | 208 | behavioral-contract | keep |
| tests/quality_gates/test_setup_inspect_approval_identity.py | 41 | behavioral-contract | keep |
| tests/quality_gates/test_setup_inspect_policy.py | 192 | behavioral-contract | keep |
| tests/quality_gates/test_setup_normalize_host_docs.py | 97 | behavioral-contract | keep |
| tests/quality_gates/test_setup_operating_surface_plan.py | 68 | behavioral-contract | keep |
| tests/quality_gates/test_setup_retro_memory.py | 100 | behavioral-contract | keep |
| tests/quality_gates/test_setup_seed_dependencies.py | 119 | behavioral-contract | keep |
| tests/quality_gates/test_setup_source_guard_scan.py | 78 | behavioral-contract | keep |
| tests/quality_gates/test_shared_script_gate_scope.py | 86 | behavioral-contract | keep |
| tests/quality_gates/test_shell_gate_root_resolution.py | 499 | behavioral-contract | keep |
| tests/quality_gates/test_skill_bootstrap_vars.py | 113 | behavioral-contract | keep |
| tests/quality_gates/test_skill_contracts_validation.py | 218 | behavioral-contract | keep |
| tests/quality_gates/test_skill_docs_contracts.py | 461 | mixed | trim-partial |
| tests/quality_gates/test_skill_ergonomics_gate.py | 876 | meta-process-gate | keep |
| tests/quality_gates/test_skill_gate_report_render.py | 94 | behavioral-contract | keep |
| tests/quality_gates/test_skill_issue_anchor_scan.py | 181 | behavioral-contract | keep |
| tests/quality_gates/test_skill_lesson_durability.py | 112 | behavioral-contract | keep |
| tests/quality_gates/test_skill_ownership_overlap.py | 468 | meta-process-gate | keep |
| tests/quality_gates/test_skill_reference_index.py | 182 | behavioral-contract | keep |
| tests/quality_gates/test_skill_surface_preflight.py | 754 | meta-process-gate | keep |
| tests/quality_gates/test_skill_validation.py | 666 | behavioral-contract | keep |
| tests/quality_gates/test_source_bound_records_guidance.py | 41 | mixed | trim-partial |
| tests/quality_gates/test_spec_critique.py | 45 | behavioral-contract | keep |
| tests/quality_gates/test_specdown_ephemeral_config.py | 281 | behavioral-contract | keep |
| tests/quality_gates/test_staged_commit_gate_plan.py | 624 | behavioral-contract | keep |
| tests/quality_gates/test_standalone_imports.py | 388 | behavioral-contract | keep |
| tests/quality_gates/test_standing_doc_provenance.py | 267 | meta-process-gate | keep |
| tests/quality_gates/test_standing_pytest_run_execution.py | 388 | behavioral-contract | keep |
| tests/quality_gates/test_standing_pytest_runner.py | 946 | behavioral-contract | keep |
| tests/quality_gates/test_standing_test_discovery.py | 235 | meta-process-gate | keep |
| tests/quality_gates/test_standing_test_economics.py | 822 | meta-process-gate | keep |
| tests/quality_gates/test_startup_probe_measure.py | 190 | meta-process-gate | keep |
| tests/quality_gates/test_structural_waste_inventory.py | 420 | meta-process-gate | keep |
| tests/quality_gates/test_subprocess_only_coverage_advisory.py | 705 | behavioral-contract | keep |
| tests/quality_gates/test_subprocess_settlement_inventory.py | 527 | meta-process-gate | keep |
| tests/quality_gates/test_success_criteria_review.py | 31 | behavioral-contract | keep |
| tests/quality_gates/test_suggest_mutation_coverage_command.py | 671 | behavioral-contract | keep |
| tests/quality_gates/test_surface_obligations.py | 450 | behavioral-contract | keep |
| tests/quality_gates/test_test_production_ratio.py | 188 | meta-process-gate | keep |
| tests/quality_gates/test_timing_layer_completeness.py | 250 | meta-process-gate | keep |
| tests/quality_gates/test_upsert_goal_input_channel.py | 74 | behavioral-contract | keep |
| tests/quality_gates/test_web_fetch_route_version_refusal.py | 135 | behavioral-contract | keep |
| tests/quality_gates/test_workflow_safety_docs.py | 33 | behavioral-contract | keep |
