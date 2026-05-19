# Quality Review
Date: 2026-05-19

## Scope

Repo-wide repair for quality advisory visibility: skipped usage-episode
validation and required skill prose review must not disappear behind green gates.

## Current Gates

- `./scripts/run-quality.sh`: 61 passed / 0 failed in 77.8s; `validate-usage-episodes`
  now replays the exit-zero `no_adapter` warning in green quality runs.
- `validate-skill-ergonomics` still enforces five configured Charness rules:
  `long_core`, `mode_option_pressure_terms`, `progressive_disclosure_risk`,
  `code_fence_without_helper_script`, and `portable_helper_path_ambiguity`.
- `inventory_skill_ergonomics.py` now reports `scope_status=scanned`,
  `finding_status=zero_heuristic_findings`, `prose_review_status=still_required`,
  `checked_skill_count=22`, and `heuristic_finding_count=0` for this repo.
- Advisory inventories now surface `adapter_valid`, `adapter_errors`,
  `adapter_warnings`, and `adapter_load_mode=permissive`; strict validators use
  `adapter_load_mode=strict` and fail on invalid adapters.
- Generated quality adapters now default `skill_ergonomics_gate_rules` to all
  five supported rules; existing explicit `[]` remains an opt-out that must
  emit a visible warning.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`, <!-- reproduction-source -->
  recorded by `scripts/record_quality_runtime.py`, rendered by
  `render_runtime_summary.py`.
- runtime hot spots: latest full gate: `pytest` 55.8s,
  `check-coverage` 40.6s, `validate-inventory-consumption-declaration` 14.4s,
  `check-duplicates` 6.9s, and `specdown` 3.6s.
- coverage gate: `check-coverage` passed in 40.6s.
- evaluator depth: `run-evals` passed in 2.2s; no live Cautilus proof was run
  for this deterministic quality-contract repair.

## Healthy

- Empty skill inventory scope is now explicit: `scope_status` separates
  `scanned`, `empty_requested_scope`, `configured_scope_empty`, and
  `unconfigured_no_skill_surface`. A configured path that resolves empty no
  longer falls through to default fallback scanning.
- Zero heuristic findings are now separate from health judgment:
  `finding_status=zero_heuristic_findings` and
  `prose_review_status=still_required` prevent the quality artifact from
  treating script silence as sufficient proof of skill structure.
- The quality artifact consumer contract now declares and must engage with
  `scope_status`, `finding_status`, `prose_review_status`,
  `checked_skill_count`, and `heuristic_finding_count` when
  `inventory_skill_ergonomics.py` is cited.
- Invalid `skill_ergonomics_gate_rules` stay fail-closed for strict gates while
  advisory inventories continue as best-effort and mark `adapter_valid=false`.
- New or bootstrapped quality adapters now inherit the standing skill
  ergonomics rule set instead of silently disabling enforcement.
- Plugin export and find-skills inventory were refreshed after public skill and
  script changes.

## Weak

- `prose_review_status=still_required` is a forcing function in artifacts, not
  an automatic semantic reviewer. Human or subagent critique still owns trigger
  overlap, progressive-disclosure honesty, and judgment-only skill risks.
- prose review result: issue #175 review confirmed the skill ergonomics inventory
  result is advisory input only; trigger-boundary and progressive-disclosure
  judgment must be recorded separately from script fields.
- The skill ergonomics inventory remains heuristic-based. It now tells the
  consumer where the heuristic boundary is, but it does not replace a focused
  review of public skill prose.

## Missing

- No maintained Cautilus scenario-registry edit was added. This slice changes
  validation output and packet preparation semantics, not a model behavior
  scenario.
- No CI lane is present in this checkout; security and quality proof remain
  local runner / maintainer-machine enforced.

## Deferred

- Consider a future low-noise rule for hidden workflow prose inside
  `## References`; the current patch only keeps prose review required.
- Downstream repos should dogfood the stronger generated default and file
  issues for noisy rules instead of Charness keeping the default disabled.

## Advisory

- Fresh-eye critique evidence: found no blockers and one actionable advisory in
  `inventory_skill_ergonomics.py`: configured empty adapter paths could still
  fallback to default scanning. That was fixed and covered by a regression test
  for `scope_status=configured_scope_empty`.
- Fresh-eye critique evidence: found the `critique` bootstrap snippet visually indented;
  the snippet is now flush and `validate-skills` passes.
- `inventory_skill_ergonomics.py` evidence: `scope_status=scanned`,
  `finding_status=zero_heuristic_findings`, `prose_review_status=still_required`,
  `checked_skill_count=22`, and `heuristic_finding_count=0`.
- `validate_usage_episodes.py` evidence: skipped `no_adapter` and `disabled`
  states now remain exit-zero but carry structured warning payloads.
- Default-policy evidence: `DEFAULT_SKILL_ERGONOMICS_GATE_RULES` now lists all
  supported rule ids, and `adapter.example.yaml` shows the same default list.

## Delegated Review

- status: executed.
- reviewer: `Harvey` audited the uncommitted diff for empty-vs-zero inventory
  semantics, prose-review preservation, quality skill checkability, critique
  changed-ref behavior, and strict/permissive adapter load split.
- actionable reviewer finding that landed: configured empty adapter skill paths
  no longer silently fall back to default skill discovery.

## Commands Run

- `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root .`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `pytest -q tests/quality_gates/test_quality_skill_ergonomics.py tests/quality_gates/test_inventory_consumption.py tests/quality_gates/test_quality_bootstrap.py tests/quality_gates/test_skill_ergonomics_gate.py tests/test_critique_prepare_packet.py`
- `python3 scripts/validate_inventory_consumption_declaration.py --repo-root .`
- `python3 scripts/validate_inventory_consumption.py --repo-root .`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 scripts/validate_skills.py --repo-root .`
- `ruff check tests/quality_gates/test_quality_bootstrap.py`
- `pytest -q tests/quality_gates/test_quality_bootstrap.py tests/quality_gates/test_skill_ergonomics_gate.py tests/quality_gates/test_quality_skill_ergonomics.py tests/quality_gates/test_profile_and_preset_validation.py`
- `./scripts/run-quality.sh`

## Recommended Next Gates

- passive `AUTO_CANDIDATE` because prose review is now required in artifacts:
  add a low-noise check that `## References` remains link inventory rather than
  hidden workflow prose.
- passive `AUTO_CANDIDATE` because generated adapters now enforce skill
  ergonomics by default: collect downstream dogfood issues before changing the
  rule set again.

## History

- [2026-05-14 mutation testing dogfood](history/2026-05-14-mutation-testing-dogfood.md)
- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
