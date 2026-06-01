# Reviewer Tier Sibling Scan Debug
Date: 2026-06-01

## Problem

The `critique` skill now has a Codex high-leverage reviewer tier in its live and
scaffolded adapter, but other skills that directly spawn bounded fresh-eye
reviewers could still rely on the host default reviewer because they did not
name the tier or apply the adapter-resolved spawn fields.

## Correct Behavior

Given a skill directly spawns a bounded fresh-eye reviewer for high-leverage
judgment, when the host exposes subagent spawn overrides, then the skill should
request the portable `high-leverage` tier and apply
`reviewer_tiers.high-leverage` without copying provider model names into
portable skill prose.

## Observed Facts

- `skills/shared/references/fresh-eye-subagent-review.md` defines
  `high-leverage` for critique angles, release, issue, and quality closeout
  review, and keeps concrete provider values in adapters.
- `skills/public/critique/SKILL.md` told agents to apply
  `reviewer_tiers.high-leverage`, but `quality`, issue causal review, and
  `setup` direct reviewer spawns did not.
- Subagent Bohr found `quality`, issue causal review, and `setup` as direct
  fresh-eye reviewer siblings.
- Subagent Fermat found the setup adapter scaffold omitted review-policy fields
  that the setup example and resolver consume.
- Subagent Cicero found that enabling the delegated-review recommendation in
  the scaffold would be too aggressive for plain consumer repos with no review
  evidence.
- `handoff`, `impl`, release full critique, and issue resolution critique
  delegate through standalone `critique`, so they inherit the fixed critique
  path instead of owning direct tier application.

## Reproduction

Static scan before the fix:

```bash
rg -n "reviewer_tiers.high-leverage|high-leverage|bounded fresh-eye|spawn bounded" \
  skills/public/{quality,issue,setup}
```

The scan showed direct reviewer spawn instructions without the tier-application
line outside `critique`.

## Candidate Causes

- The first fix made `critique` adapter-aware but did not generalize to skills
  that spawn reviewers directly instead of delegating to `critique`.
- Existing tests checked provider-model portability and the critique adapter
  example, not whether direct reviewer instructions apply the portable tier.
- Setup adapter initialization used only base adapter fields even though the
  example and resolver had accumulated policy-bearing review fields.

## Hypothesis

If direct reviewer spawn instructions name `high-leverage` and
`reviewer_tiers.high-leverage`, and setup initialization scaffolds the same
review-policy fields consumed by the resolver, then the immediate sibling class
is fixed without making adapter-less or non-Codex hosts inherit provider-specific
models.

## Verification

- `pytest -q tests/quality_gates/test_reviewer_tier_policy.py
  tests/quality_gates/test_setup_adapter_scaffold_policy.py
  tests/quality_gates/test_setup_inspect_policy.py
  tests/quality_gates/test_quality_skill_docs.py
  tests/quality_gates/test_docs_and_misc.py::test_quality_skill_carries_blind_spot_policy_and_critique_refs`
  passed (`68 passed`).
- `python3 scripts/validate_skills.py --repo-root .` passed.
- `python3 -m py_compile skills/public/setup/scripts/init_adapter.py
  plugins/charness/skills/setup/scripts/init_adapter.py` passed.
- `ruff check skills/public/setup/scripts/init_adapter.py
  tests/quality_gates/test_reviewer_tier_policy.py
  tests/quality_gates/test_setup_inspect_policy.py` passed.
- `pytest -q tests/quality_gates tests/control_plane tests/test_*.py
  tests/charness_cli/test_doctor_cache_selection.py
  tests/charness_cli/test_tool_lifecycle.py` passed (`1955 passed, 4 skipped`).
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` refreshed the
  checked-in plugin mirror.

## Root Cause

Reviewer-tier ownership was treated as a `critique` adapter detail even though
the shared fresh-eye policy is reused by other direct reviewer spawns. The
detection surface proved the central mapping and provider-portability rule but
not the downstream instruction that tells agents to apply the resolved tier.

## Detection Gap

- direct reviewer spawn instructions | no test asserted that non-critique direct
  fresh-eye reviewers name `high-leverage` and `reviewer_tiers.high-leverage` |
  added reviewer-tier policy coverage for quality, setup, and issue causal
  review.
- setup adapter scaffold | no test asserted that setup `init_adapter.py`
  includes the policy fields consumed by setup inspection | added setup init
  scaffold coverage and a plain-repo no-forced-review-policy regression.
- adapter parity in general | validators mostly checked adapter shape, not
  every policy-bearing field across example/init/live surfaces | diagnostic-only
  for this slice; proof: subagent scan and targeted setup regression.

## Sibling Search

- Mental model: fixing the central adapter mapping meant every bounded reviewer
  would automatically use it.
- same layer: `skills/public/quality/SKILL.md`, `skills/public/issue/SKILL.md`,
  `skills/public/issue/references/causal-review.md`, and
  `skills/public/setup/SKILL.md` directly spawn bounded reviewers without tier
  application; decision: same bug, fix now; proof: static scan plus regression
  tests.
- same layer: `skills/public/setup/scripts/init_adapter.py` omitted review
  policy fields consumed by setup resolver/example; decision: same bug, fix now;
  proof: scaffold and no-forced-review-policy regression tests.
- abstraction up: `skills/public/gather/scripts/init_adapter.py` omits the
  provider-policy field shown in its example, and `issue` init omits
  `default_repo`; decision: same class, diagnostic-only for this slice; proof:
  static scan only.
- mental-model siblings: `achieve` disposition review and `create-skill`
  success-criteria review mention fresh-eye review but have less clear execution
  ownership; decision: same class, diagnostic-only for this slice; proof: static
  scan only.
- intentional boundary: `handoff`, `impl`, release full critique, and issue
  resolution critique delegate to standalone `critique`; decision: intentional
  plain-text or non-rendering boundary; proof: static scan only.

## Seam Risk

- Interrupt ID: reviewer-tier-sibling-scan
- Risk Class: none
- Seam: repo-local public skill instructions and adapter scaffolds
- Disproving Observation: targeted tests now fail if the named direct reviewer
  surfaces drop the portable tier application line.
- What Local Reasoning Cannot Prove: actual host spawn payloads until a runtime
  bridge records tier-to-spawn-field application.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Direct high-leverage reviewer spawns now name the portable tier and the
host-exposed adapter field to apply. Setup adapter initialization now preserves
the review-policy evidence surface that downstream setup inspection consumes
without enabling delegated-review recommendations unless evidence or explicit
adapter opt-in exists, and tests cover both behaviors.

## Related Prior Incidents

- `charness-artifacts/debug/2026-05-21-bug-pattern-sibling-scan.md`: prior
  sibling scan where a fixed exemplar did not mean the whole pattern was fixed.
