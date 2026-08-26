# Adapter Bootstrap Ownership Cutover Closeout

Date: 2026-08-27 Asia/Seoul
Status: implemented-uncommitted

## Implemented

The #730 friction cutover now gives the shared initializer ownership of the
first-use lifecycle for all 16 public adapter entrypoints. Skill wrappers still
declare their own low-risk fields, while `scripts/adapter_init_lib.py` owns:

- safe repository-local target resolution and symlink refusal;
- `absent`, `valid`, `invalid`, and `unestablished` state classification;
- idempotent initialization and no-op repetition;
- explicit `--dry-run` and `--force` behavior; and
- one `charness.adapter-bootstrap/v1` YAML receipt with mutation truth,
  hashes, reason, and next action.

The cutover preserves skill-specific resolver authority and does not silently
bootstrap high-risk policy, reviewer, delivery, release, or host capabilities.
The old per-wrapper path output was removed so the common receipt is the only
stdout carrier. The existing critique template and issue defaults remain their
own content sources behind the same lifecycle.

## Truth surfaces

- Source owner: `scripts/adapter_init_lib.py`
- Checked-in mirror: `plugins/charness/scripts/adapter_init_lib.py`
- Operator contract: `skills/shared/references/adapter-bootstrap.md`
- Contract coverage: `tests/quality_gates/test_adapter_bootstrap_contract.py`
- Impl regression coverage: `tests/test_impl_bootstrap.py`

## Verification

- `python3 -m pytest -q tests/quality_gates/test_adapter_bootstrap_contract.py` — `32 passed` across all 16 public entrypoints, covering dry-run, initialization, idempotent repeat, and invalid-version refusal.
- `python3 -m pytest -q tests/test_impl_bootstrap.py tests/test_announcement_adapter_lib.py tests/quality_gates/test_hotl_adapter.py tests/quality_gates/test_setup_adapter_scaffold_policy.py tests/quality_gates/test_reviewer_tier_policy.py tests/quality_gates/test_create_skill_adapter.py tests/quality_gates/test_narrative_scenario_blocks.py` — `75 passed`.
- `python3 scripts/run_evals.py --repo-root . --jobs 4` — all `20` scenarios passed, including adapter bootstrap and setup scenarios.
- `python3 -m pytest -q tests/test_public_skill_dogfood.py` — `13 passed` after synchronizing the achieve acceptance registry with its current scaffold.
- `python3 -m py_compile tests/quality_gates/test_adapter_bootstrap_contract.py scripts/adapter_init_lib.py $(rg --files skills/public | rg '/scripts/init_adapter\\.py$')` — passed.
- `python3 scripts/check_python_lengths.py --repo-root . --paths scripts/adapter_init_lib.py $(rg --files skills/public | rg '/scripts/init_adapter\\.py$')` — validated `17` files.
- `python3 scripts/check_staged_mirror_drift.py --repo-root .` — source/plugin mirror matched.
- `python3 scripts/validate_skills.py --repo-root .` — validated `22` skill packages; the compressed `critique/SKILL.md` is exactly `200` lines in source and mirror.
- `python3 scripts/check_skill_contracts.py --repo-root .` — `14` core, `9` package, and `2` forbidden-snippet contracts passed.
- `python3 scripts/check_adapter_consumer_classification.py --repo-root .` — `121` classifications across `118` files; all new consumers classified, with `67` explicit residual defects preserved.
- `python3 -m pytest -q tests/coverage_debt/test_batch5.py` — `26 passed` after deleting the obsolete `charness goal check` compatibility test exposed by the full-suite probe.
- `python3 -m pytest -q tests/quality_gates/test_check_public_doc_coupling.py tests/charness_cli/test_goal_helpers.py tests/charness_cli/test_yaml_output_branch_coverage.py` — `73 passed` for the generic issue-native CLI help, removal, and wrapper behavior.
- `python3 scripts/render_cli_reference.py --repo-root . --output docs/cli-reference.md` followed by `python3 scripts/check_command_docs.py --repo-root .` — generated CLI reference and command contract passed with no findings.
- `bash scripts/check-docs.sh` — passed; existing advisory inline-code warnings remain non-blocking.

## Goal Run child readback

The executed evidence was carried into child `corca-ai/charness#692` through
`goal-run-apply` operation `update-body-692-bootstrap.json`. The provider
returned `status: verified-write`, `body_verified: true`, and the exact issue
URL. A subsequent `issue_tool.py read` returned the same body and `state: OPEN`.
`goal-run-read` and clean `/goal #724` pickup still returned the exact 31-child
graph and selected `backlog-546`; neither read mutated state.

## Boundary and non-claims

`moved-to-owner`: adapter lifecycle and receipt shape belong to the shared
initializer; skill fields and high-risk resolver semantics remain with each
skill. A valid adapter is not evidence that any optional backend or external
boundary is configured.

This is local source/test/plugin verification only. No fresh-eye review,
`docs/handoff.md` update, issue closure, push, release, tag, remote CI, or
installed-host mutation is claimed, per the user-directed execution mode. A
full-suite probe reached `1,455` passing tests before exposing the removed
`goal check` compatibility test; its owning batch and all affected CLI/document
gates pass after the deletion, but a new full-suite completion is not claimed.
The wrapper forest is intentionally still present as thin declarations; the
cutover removes duplicated lifecycle behavior without pretending that all
skill-specific resolver code is interchangeable. The duplicated semantic review
operator prose was deleted from `critique/SKILL.md`; the detailed command and
carrier contract remains in its owning reference so the core skill stays at the
line cap.
