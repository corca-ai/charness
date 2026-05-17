# Quality Review
Date: 2026-05-17

## Scope

Repo-wide skill ergonomics cleanup after the setup repair: remove remaining
public skill pressure findings, keep schema/taxonomy language honest, and turn
Charness' own skill ergonomics policy from warning-only into configured
enforcement.

## Current Gates

- `./scripts/run-quality.sh`: 60 passed / 0 failed in 87.6s on the current
  local runner.
- `validate-skill-ergonomics` now runs five configured rules:
  `long_core`, `mode_option_pressure_terms`, `progressive_disclosure_risk`,
  `code_fence_without_helper_script`, and `portable_helper_path_ambiguity`.
- `inventory_skill_ergonomics.py` reports zero heuristics across 22 checked
  skills; the largest remaining core is `release` at 160 non-empty lines.
- Cautilus planner returned `next_action: none`; this prompt-affecting
  preserve slice required scenario review but no live evaluator run.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`, <!-- reproduction-source -->
  recorded by `scripts/record_quality_runtime.py`, rendered by
  `render_runtime_summary.py`.
- runtime hot spots: latest full gate: `pytest` 63.0s,
  `check-coverage` 40.7s, `validate-inventory-consumption-declaration` 17.1s,
  `check-duplicates` 7.1s, and `specdown` 3.5s.
- coverage gate: `check-coverage` passed in 40.7s.
- evaluator depth: `run-evals` passed in 2.0s; live Cautilus proof was not
  required because the planner returned `next_action: none`.

## Healthy

- All public/support skills are now under the pressure threshold or otherwise
  clean by the current inventory. `core_nonempty_lines` tops out at 160
  (`release`), and previously flagged `announcement`, `critique`, `debug`,
  `hitl`, `impl`, `issue`, `release`, and `spec` no longer carry `long_core`.
- `reference_file_count` and `script_file_count` remain non-zero on the larger
  public skills, so the cleanup did not fake concision by deleting their support
  surfaces; it reduced core pressure and preserved progressive disclosure.
- Previously flagged mode/option pressure in `create-cli`, `create-skill`,
  `find-skills`, `gather`, `hitl`, `ideation`, `retro`, and `spec` is gone.
- `gather` no longer carries `portable_helper_path_ambiguity`; schema literals
  such as `gather_provider.<source>.mode` remain exact because inline code spans
  are excluded from pressure-term counting.
- Empty `skill_ergonomics_gate_rules` no longer describes this repo. Charness
  now opts into the low-noise skill pressure rules while defaults for other
  repos remain advisory-only unless explicitly configured.
- Plugin export and find-skills inventory were refreshed after public skill
  source changes.

## Weak

- `## References` is now exempt from core pressure counting. That matches its
  intended role as a link inventory, but a future rule could verify that the
  section does not become hidden workflow prose.
- `code_fence_without_helper_script` overlaps existing package-validity smells.
  The current split is acceptable: package validation protects broad structure,
  while the configured ergonomics rule makes Charness' own policy fail on the
  same pressure signal.

## Missing

- No maintained Cautilus scenario-registry edit was added for this slice. The
  scenario review decision is recorded in
  [skill pressure cleanup critique](../critique/2026-05-17-skill-pressure-cleanup-critique.md);
  the planner did not request a live evaluator run.
- No CI lane is present in this checkout; security and quality proof remain
  local runner / maintainer-machine enforced.

## Deferred

- Add a specific `References`-section shape check if future skill compression
  starts moving workflow decisions there.
- Consider whether default Charness-generated adapters should eventually opt
  into some ergonomics rules after downstream noise is measured.

## Advisory

- Fresh-eye critique found one blocker before commit: the initial `gather`
  wording hid the real `.mode` adapter key. That was repaired by preserving the
  exact inline code literal and teaching the pressure inventory to ignore inline
  code for mode/option counts. Evidence:
  [skill pressure cleanup critique](../critique/2026-05-17-skill-pressure-cleanup-critique.md).
- The `find-skills` artifact changed semantically after public skill reference
  cleanup and was refreshed as part of the slice. Evidence:
  [find-skills latest](../find-skills/latest.md).

## Delegated Review

- status: executed.
- reviewer: `Dalton` audited the current git diff for semantic drift,
  validator coherence, adapter-policy risk, and generated export sync.
- actionable reviewer finding that landed: restore exact `gather_provider.<source>.mode`
  wording and avoid pressure-counting inline schema literals.

## Commands Run

- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/validate_skill_ergonomics.py --repo-root .`
- `pytest -q tests/quality_gates/test_skill_ergonomics_gate.py tests/quality_gates/test_quality_skill_ergonomics.py tests/quality_gates/test_quality_bootstrap.py tests/quality_gates/test_quality_skill_docs.py tests/test_gather_google_workspace.py tests/quality_gates/test_docs_and_misc.py`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.5.34/skills/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-task "verify improved pressure skill ergonomics"`
- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `python3 scripts/validate_cautilus_proof.py --repo-root .`
- `python3 scripts/validate_adapters.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`
- `./scripts/run-quality.sh`

## Recommended Next Gates

- passive `AUTO_CANDIDATE` because current `References` sections are clean link
  inventories: add a low-noise check that `## References` contains link
  inventory rather than hidden workflow prose.
- passive `AUTO_CANDIDATE` because this slice only proves Charness' own
  configured surface: after downstream dogfood, decide whether generated
  quality adapters should opt into a subset of skill ergonomics rules by
  default.

## History

- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
