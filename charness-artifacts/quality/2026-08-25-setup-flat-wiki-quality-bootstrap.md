# Quality Review
Date: 2026-08-25

Title: Setup flat-wiki quality bootstrap review

## Scope

Target boundary: the setup flat-wiki proposal and its quality handoff: setup
inspector payload, setup adapter/profile, public setup and quality skills,
references, source/plugin mirrors, and focused tests.

Ambient repo findings: the earlier critique/debug evidence slice and its
dup-ratchet changes are not re-judged here. The broad gate's ambient mutation,
eval, shell, and duplication findings are reported separately and are not
called setup findings.

## Surface Contract Review

- semantic coverage: observed — this is a plan/projection surface, not a claim
  that a consumer repository was modified.
- surface: setup inspection JSON plus setup/quality skill instructions and the
  flat-wiki profile reference.
- owner: `setup` owns proposal and approval routing; `quality` owns the adapter,
  exact gates, ratchets, and quality verdict.
- projections: README, AGENTS/CLAUDE, documentation index, conditional roadmap
  and operator acceptance, hook/tooling policy, and quality status.
- state scope: plan-only before approval; apply only after explicit approval;
  then quality verification is a separate state.
- transitions: inspect -> named approval -> apply -> quality verify.
- proof boundary: deterministic validators, focused tests, mirror comparison,
  reviewer evidence, and live inspector output. Consumer apply, awiki graph
  execution, hook installation, and hook-failure readback are unexamined.
- unexamined axes: consumer approval, live tool installation, awiki behavior,
  hook failure diagnostics, exact executable hook scope, and post-apply quality.

## Current Gates

- Healthy: `validate_skills.py`, `check_skill_contracts.py`, 86 focused setup
  and skill-contract tests, `git diff --check`, and source/plugin mirror checks
  all passed.
- The inspector emitted `profile.id: flat-wiki`, `approval_required: true`,
  `plan_only: true`, a quality owner/status, existing-hook evidence, and the
  staged/related-file scope policy. The approval identity includes resolved
  adapter surface paths, recursive `.md` docs inventory (including `.MD`), and
  all detected tooling/hook inputs.
- Quality bootstrap dry-run and detailed plan completed with `rc=0`; the
  configured/unconfigured state is separate from a gate verdict and all
  mutation/live commands remain `not-run`.

## Runtime Signals

- runtime source: `.charness/quality/runtime-signals.json` rendered by
  `render_runtime_summary.py`; no new setup-specific timing sample was added. <!-- reproduction-source -->
- runtime hot spots: latest `run-quality-full-release` 199.5s and `pytest-release`
  176.3s, both within configured budgets; stale samples are advisory only.
- coverage gate: not rerun for this slice; prior broad-run failures remain
  ambient non-claims.
- evaluator depth: deterministic gates only; no live Cautilus, awiki, or
  consumer hook installation was claimed.

## Healthy

- Approval is an explicit transition. A detected binary, green command, or
  inferred language cannot authorize writes, installs, hook registration, or
  ratchet migration.
- Lefthook is a recommendation only when no hook manager is detected; existing
  Git-native, Husky, simple-git-hooks, and Lefthook surfaces are preserved and
  integrated. Hook scope is staged/related-file first, with whole-repo work
  reserved for pre-push/CI or approval.
- Quality state is visible as configured/plan-only/blocked/unavailable and is
  explicitly not a green verdict.
- Conditional roadmap and operator-acceptance surfaces are explicitly
  `applicability: unproven — operator decision`, rather than silently treated
  as missing core setup.
- Existing hook managers are detected in common file and package forms,
  including package `pre-commit` arrays and `.githooks/pre-push`; Lefthook is
  only proposed when no manager exists.

## Weak

- Tool and hook discovery is a cheap proposal inventory, not proof that a
  consumer's formatter/linter or failure diagnostics are runnable.
- Tool and hook discovery is still a proposal inventory, not proof that a
  consumer's formatter/linter, exact related-file command, or failure receipt
  is runnable; `lint-staged` remains a fallback note.

## Missing

- No consumer-repository approval/apply proof exists for `docs/index.md`, flat
  wiki creation, or language-specific hook commands.
- No live hook-failure visibility or installed-tool readback proves the proposed
  boundary in a fresh consumer checkout.

## Deferred

- Consumer dogfood, awiki lint, Lefthook installation, and dead-file advisories
  are deferred until a consumer repo explicitly approves the rendered plan.

## Advisory

- structural review result: [command: inspect_repo.py] the next capability is an approval packet that lets
  a maintainer see conflicts, quality ownership, and the exact fast hook scope
  before mutation. The current centers are the inspector payload and quality
  planner; strengthen them with consumer dogfood after approval.
- prose review result: [artifact: setup-flat-wiki-quality-bootstrap] setup stays progressive-disclosure (profile/reference
  details are loaded after inspection), while quality retains verdict ownership;
  no new prose ritual is required by this slice.
- `inventory_skill_ergonomics.py --summary`: 15 heuristic findings across the
  repo, chiefly intentional host-surface references and missing argparse help;
  no setup-specific core-overfill or reference-discoverability finding.

## Delegated Review

- Delegated Review: runtime `APPROVED`; artifact `APPROVED` after fixing the
  resolved-surface identity and case-insensitive docs inventory findings;
  counterweight `PASS` for the explicitly plan-only slice. Parent fingerprint
  verification was clean. All reviewers agree consumer apply/live hook/awiki
  proof remains unclaimed.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): not_applicable — this slice changes plan/report surfaces,
  not a standing slow gate.

## Commands Run

- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/check_skill_contracts.py --repo-root .`
- `pytest -q tests/quality_gates/test_setup_inspect_policy.py tests/quality_gates/test_setup_inspect_adapters.py tests/quality_gates/test_skill_docs_contracts.py`
- `python3 skills/public/setup/scripts/inspect_repo.py --repo-root .`
- `python3 skills/public/quality/scripts/bootstrap_adapter.py --repo-root . --dry-run`
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --detail`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --detail`
- `git diff --check`; source/plugin `cmp` mirror checks
- `python3 skills/shared/scripts/reviewer_boundary_fingerprint.py verify ...`

## Recommended Next Quality Moves

- active capability_needed=consumer can apply the approved operating packet;
  next_center=consumer dogfood; transformation=run one fresh consumer plan,
  approval, and readback round without replacing its existing hook manager;
  proof_boundary=record plan identity, approval, changed surfaces, and quality
  readback; enforcement_posture=existing-gate-reuse.
- passive capability_needed=live hook diagnostics because consumer opt-in is absent; next_center=hook failure
  visibility; transformation=until a consumer explicitly opts in, keep
  Lefthook/awiki installation as a non-claim; proof_boundary=live failing-hook
  receipt and visible log pointer; enforcement_posture=advisory.
- passive capability_needed=consumer-bound approval enforcement because this
  slice is plan-only; next_center=apply adapter; transformation=make the
  consumer mutator re-check `--expect-plan-identity` immediately before writes;
  proof_boundary=changed-surface readback after approval; enforcement_posture=
  deferred until a consumer apply contract exists.

## History

- [2026-08-18 quality review](history/2026-08-18-quality-review.md)
