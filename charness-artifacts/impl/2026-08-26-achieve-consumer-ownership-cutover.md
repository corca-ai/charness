# Achieve Consumer Ownership Cutover Closeout

Date: 2026-08-26 Asia/Seoul
Status: implemented-uncommitted

## Implemented

This cutover resumes the approved issue-native Goal Run and folds the new
consumer-friction cluster (#728–#732) into the same ownership decision:

- `#726` now owns the adapter-resolved Goal Run provider boundary: preflight,
  exact read, guarded apply, observations, recovery, and close ingress.
- `#724` has the immutable draft/binding identity, exact current membership,
  and the verified `verified-target-roundtrip` marker. Its live graph is
  `31` children (`3` closed, `28` open).
- `#727` owns the clean `/goal #N` pickup path. It resolves repository and
  parent identity through provider truth, validates the binding and graph, and
  selects only an executable open child.
- `#733` owns one `goal_lineage` identity across slice, critique, prove, retro,
  host, closeout, and release consumers. Planning-only and not-goal-bound records
  are explicit rather than nullable execution claims. The optional premise-preflight
  adapter is intentionally left for the #733 successor instead of widening this
  cutover's preflight surface.
- #728/#731 lifecycle state is carried as typed preflight, started, delivery,
  verdict, failure, and next-move fields. #729's review command derives the
  packet, input identity, schema, capability, paths, and boundary from semantic
  inputs. #732's reversible-work path permits a reasoned
  `Critique: not-required <reason>` disposition.
- #730's 16 public adapter entrypoints now share one first-use lifecycle and
  typed YAML receipt. Skill-specific fields remain local; target safety,
  absent/valid/invalid/unestablished classification, idempotence, dry-run, and
  explicit force replacement belong to `adapter_init_lib`.
- Deletion-first cleanup removed the obsolete tracker-receipt bridge and the
  local closeout normalizer, including their now-dead tests and imports. No
  replacement local progress ledger was introduced.
- The obsolete top-level `charness goal check` compatibility surface and its
  stale helper-forwarding test were deleted. The supported CLI is now the
  issue-native `charness goal run --objective '/goal #N'`; direct artifact
  validation names the actual `check_goal_artifact.py` helper when required.

## Contract and truth surfaces

- Goal Run contract: `charness-artifacts/goal-runs/724/bodies/goal-run-provider.md`
- Orchestration contract: `charness-artifacts/goal-runs/724/bodies/achieve-orchestration.md`
- Evidence contract: `charness-artifacts/goal-runs/724/bodies/goal-evidence-lineage.md`
- Frozen draft: `charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.md`
- Binding: `charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.binding.json`
- Exact graph readback: `charness-artifacts/goal-runs/724/final-graph-readback.md`
- Target pickup readback: `charness-artifacts/goal-runs/724/target-roundtrip-readback.md`
- Adapter bootstrap closeout: `charness-artifacts/impl/2026-08-27-adapter-bootstrap-ownership-cutover.md`
- Operation observations: `charness-artifacts/goal-runs/724/observations/`
- Source and checked-in plugin mirrors remain synchronized for the changed
  provider, pickup, lineage, critique, and lifecycle surfaces.

## Verification

Executed locally in the shared repository:

- `python3 -m pytest -q tests/quality_gates/test_achieve_goal_run_pickup.py tests/quality_gates/test_achieve_interview_contract.py tests/quality_gates/test_goal_binding_v1.py tests/quality_gates/test_goal_evidence_lineage.py tests/quality_gates/test_goal_lineage_consumers.py tests/quality_gates/test_achieve_before_activation.py` — `58 passed`.
- `python3 -m pytest -q tests/quality_gates/test_issue_goal_run.py tests/quality_gates/test_semantic_review_command.py tests/test_critique_round_findings.py tests/quality_gates/test_public_skill_yaml_output_contract.py tests/quality_gates/test_goal_consumer_census.py` — `77 passed`.
- `python3 -m pytest -q tests/quality_gates/test_slice_manifest.py tests/quality_gates/test_premise_preflight.py tests/quality_gates/test_retro_persistence.py tests/quality_gates/test_retro_host_log_probe.py` — `102 passed`.
- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_runtime_budget_universe.py` — `32 passed` for the provider-selected `backlog-546` child.
- `python3 scripts/compileall` equivalent: `python3 -m compileall -q scripts skills/public plugins/charness/skills plugins/charness/scripts plugins/charness/shared` — pass.
- `bash scripts/check-docs.sh` — pass. Existing advisory inline-code warnings
  remain non-blocking.
- `python3 skills/public/critique/scripts/run_review.py --repo-root . --scope 'goal-lineage input path safety' --lens operability --reviewed-path scripts/goal_lineage.py --dry-run --attempt-id goal-run-729-dry-run-1` — exit `0`, one typed `dry-run-ready` carrier, no reviewer started, derived identities and paths present.
- `python3 skills/public/achieve/scripts/goal_run_pickup.py --repo-root . --objective '/goal #724'` — exit `0`, `status: selected`, `outcome: verified-read`, `mutation_invoked: false`, selected `backlog-546`.
- `./charness goal run --repo-root . --objective '/goal #724' --charness-checkout .` — exit `0` with the same selected-child readback. This is the direct CLI proof for the file-discovery boundary.
- `python3 scripts/classify_goal_consumers.py --repo-root . --format json --output .charness/goal-consumer-census.json` — receipt emitted with `810` matched rows, `0` unassigned rows, and `67` explicit defect rows; the command correctly exits `2` because residual owners remain.
- `python3 -m pytest -q tests/quality_gates/test_adapter_bootstrap_contract.py` — `32 passed` across all 16 public adapter entrypoints, including dry-run, initialize, idempotent repeat, and invalid-version refusal.
- `python3 -m pytest -q tests/test_impl_bootstrap.py tests/test_announcement_adapter_lib.py tests/quality_gates/test_hotl_adapter.py tests/quality_gates/test_setup_adapter_scaffold_policy.py tests/quality_gates/test_reviewer_tier_policy.py tests/quality_gates/test_create_skill_adapter.py tests/quality_gates/test_narrative_scenario_blocks.py` — `75 passed` for the shared bootstrap and representative skill adapter regressions.
- `python3 scripts/run_evals.py --repo-root . --jobs 4` — all `20` eval scenarios passed, including the adapter bootstrap scenarios.
- `python3 scripts/validate_skills.py --repo-root .` — `22` skill packages passed; source/plugin skill surfaces are within the `200`-line core limit.
- `python3 scripts/check_skill_contracts.py --repo-root .` — `14` core, `9` package, and `2` forbidden-snippet contracts passed.
- `python3 scripts/check_adapter_consumer_classification.py --repo-root .` — all new adapter consumers classified (`121` classifications across `118` files); `67` residual defects remain explicit.
- `python3 scripts/check_staged_mirror_drift.py --repo-root .` — source/plugin mirror matched.
- `python3 -m pytest -q tests/coverage_debt/test_batch5.py` — `26 passed` after deleting the obsolete `charness goal check` compatibility test.
- `python3 -m pytest -q tests/quality_gates/test_check_public_doc_coupling.py tests/charness_cli/test_goal_helpers.py tests/charness_cli/test_yaml_output_branch_coverage.py` — `73 passed` for the issue-native CLI and generic documentation surface.
- `python3 scripts/render_cli_reference.py --repo-root . --output docs/cli-reference.md` and `python3 scripts/check_command_docs.py --repo-root .` — generated command docs passed with no findings.

## Live provider evidence

- `goal-run-read` and `goal-run-preflight` both read `corca-ai/charness#724`
  as `OPEN`, with the exact binding, current membership, and 31-child graph.
- Updating live child `#546` with its executed verification returned
  `status: verified-write`, `body_verified: true`, exact URL
  `https://github.com/corca-ai/charness/issues/546`, and persisted started and
  terminal observations.
- Updating live child `#692` with the shared adapter-bootstrap evidence returned
  `status: verified-write`, `body_verified: true`, exact URL
  `https://github.com/corca-ai/charness/issues/692`; a separate issue read
  returned the same body while the child remained `OPEN`.
- The clean-process and installed-style CLI pickup reads were read-only; no
  issue was closed and no graph mutation occurred during either pickup.

## Lint gate

- `git diff --check` is not clean because the pre-existing
  `charness-artifacts/gather/latest.md:107` has an extra blank line at EOF. It
  is outside this cutover and remains unattributed; no `--no-verify` bypass was
  used.
- The classifier's `67` defects are recorded as open ownership work, not
  reclassified as green. The largest groups are 26 achieve-orchestration rows,
  35 handoff/goal-binding rows, and 6 evidence-lineage rows.
- A full-suite probe reached `1,455` passing tests before exposing one stale
  `goal check` compatibility test; the obsolete test was deleted and its batch,
  CLI, documentation, and mirror gates pass, but full-suite completion after
  that deletion remains unclaimed.

## Truth Surface Sync

Source public skills, root scripts, and checked-in `plugins/charness/` mirrors
were synchronized. The approved frozen Goal Draft and `docs/handoff.md` were
not rewritten. Live child bodies were changed only through file-backed
Goal-Run operations with exact provider readback.

## Boundary Ownership

`moved-to-owner`: provider state belongs to the issue backend; Goal Run identity
belongs to the binding/lineage consumers; pickup belongs to `achieve`; review
lifecycle belongs to the shared reviewer runner; reversible prove cadence is
owned by `prove`; external close remains guarded by the issue provider.

## Critique

`not-run operator-directed exception`: this execution follows the user's
explicit instruction to use the `impl` contract and closeout evidence shape
without forced fresh-eye review, handoff update, or micro-slice execution.

## Residuals and non-claims

- #730's shared adapter-bootstrap lifecycle is implemented and locally proven.
  The 16 thin wrappers and skill-specific resolver semantics remain as explicit
  declarations; their product fields were not incorrectly collapsed into one
  schema.
- The census still identifies legacy achieve and handoff consumers. Deleting
  those forests coherently requires a handoff-compatible migration, which is
  intentionally not claimed while the user-directed handoff freeze is active.
- `#724`, `#546`, `#725`, `#726`, `#727`, `#733`, and `#734` remain open. No
  issue closure, push, release, tag, remote CI, installed-host mutation, or
  hosted behavior is claimed.
- No fresh-eye result, handoff update, commit, or clean whole-tree closeout
  bundle is claimed. The two live bundle-readiness tests remain expectedly
  red while this shared worktree contains the current uncommitted artifacts.

## Next move

Continue from provider-selected `backlog-546` only after its owner decides
whether the verified local runtime-budget evidence warrants a separate issue
resolution. The #730 bootstrap lifecycle is now a shared owner; remaining
implementation work is bounded by the `67` explicit classifier defects and
the still-open provider children. Do not create another five-issue ceremony
for #728–#732.
