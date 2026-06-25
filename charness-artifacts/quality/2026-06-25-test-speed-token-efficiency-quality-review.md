# Quality Review
Date: 2026-06-25

## Scope

Target boundary: repo-wide quality slice for standing test speed and
agent-facing inventory token efficiency; no single public skill target.

Ambient repo findings: existing `hitl` / `narrative` doc duplicate advisory and
Python near-limit warnings are not caused by this slice. The
`test_quality_skill_ergonomics.py` near-limit warning improved from 732 to 706
Python code lines by extracting a shared test helper.

## Current Gates

- `./scripts/run-quality.sh --read-only` passed 79/79 after the slice.
- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`
  passed 3574 tests in 24.38s with the default worker cap.
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root .`
  passed after updating both code id-set baselines:
  `nose-baseline.json` and `dup-ratchet-baseline.json`.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile
  `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  `pytest` 24.6s latest / 26.5s median in the runtime summary; direct
  baseline quality run showed `pytest` 34.6s before the cap.
- coverage gate: `./scripts/run-quality.sh --read-only` passed 79/79 after the
  slice; `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`
  passed 3574 tests in 24.38s.
- measured worker probe: direct standing target run with `-n 16` passed in
  23.81s; `-n 8` passed in 45.36s; default wrapper after the change passed in
  24.38s.
- token payload probe: `inventory_skill_ergonomics.py --json` emitted 96643 bytes;
  `--summary` emitted 12201 bytes for the same repo scan.
- evaluator depth: deterministic gates only. No Cautilus run was in scope
  because this slice changed runner/helper mechanics, not a prompt behavior
  claim needing evaluator-backed proof.

## Healthy

- Standing pytest now caps default xdist workers at 16, reducing oversubscription
  on high-core machines while keeping `CHARNESS_PYTEST_WORKERS` as an explicit
  escape hatch for `auto`, `logical`, or a positive integer.
- The summary mode preserves the review-critical fields:
  `prose_review_status`, advisories, interpretation, subcheck counts, and
  per-skill heuristic hits, without emitting every finding and prompt.
- The new ergonomics summary tests use a shared in-process CLI harness instead
  of copying loader boilerplate into another near-limit test file.

## Weak

- Runtime gains were measured on one local `local-linux-x86_64-36cpu` machine.
  The cap is configurable, but other hardware profiles may prefer a different
  worker count.
- The changed-line mutation gate warned during read-only quality because
  mutation-pool files were still uncommitted, so that specific clean verdict is
  not claimed as proof until after commit.

## Missing

- No missing deterministic gate is justified by this slice. Existing runtime
  budgets and `check-runtime-budget` cover the standing-gate drift path.

## Deferred

- `specdown` still appears as a runtime hot spot in some samples, but this slice
  did not investigate executable-spec economics.
- The ambient `hitl` / `narrative` doc duplicate advisory remains a separate
  quality follow-up, not part of this test-speed/token-efficiency repair.

## Advisory

- structural review result: command:
  `plan_quality_run.py --repo-root . --json`; this was a repo-wide quality
  slice, not a target skill review. The next structural move was implemented:
  cap pytest workers, add compact inventory output, and extract duplicated test
  harness code.
- prose review result: command:
  `inventory_skill_ergonomics.py --repo-root . --summary`; compact output still
  exposes `prose_review_status=required`, `heuristic_finding_count=17`, and
  advisories, so it does not hide the required human/model judgment packet.
- runtime interpretation: command: `render_runtime_summary.py --repo-root . --json`;
  the top-ranked runtime opportunity fit this repo's current state because the
  standing suite uses xdist across many subprocess-heavy tests on a 36 CPU host;
  capping workers improved measured wall time without removing proof.
- skill ergonomics interpretation: command:
  `inventory_skill_ergonomics.py --repo-root . --json`; host-surface references
  remain mostly package-portability advisories, and this slice did not
  reclassify them as debt.
- dup-ratchet interpretation: command:
  `inventory_nose_clones.py --repo-root . --write-baseline` and
  `check_dup_ratchet.py --repo-root . --write-baseline`; the refresh updated
  both code id-set baselines together after the edited scanner changed family
  ids. This is a reviewed baseline accept, not a duplicate-reduction claim.
- fresh-eye review result: artifact:
  bounded reviewer `019efdee-b58d-7893-bb55-ea634b96211c`; it found one
  hermetic env bug and one incomplete dup-baseline-policy record. Both were
  addressed before final validation.
- dogfood decision: command:
  `suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`;
  `quality` remains `hitl-recommended`; no Cautilus run.

## Delegated Review

- Delegated Review: executed — bounded fresh-eye reviewer
  `019efdee-b58d-7893-bb55-ea634b96211c` found two issues. The env override
  helper now distinguishes `None` from `{}`; both `nose-baseline.json` and
  `dup-ratchet-baseline.json` were refreshed together and documented.
- Slow-gate lenses: fixture-economics, parallel-critical-path, and
  duplicated-proof were covered by same-slice measurements and the bounded
  reviewer prompt; no separate fan-out was run.

## Commands Run

- `python3 skills/public/quality/scripts/resolve_adapter.py --repo-root .`
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --summary`
- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --write-baseline`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --write-baseline`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`
- `./scripts/run-quality.sh --read-only`

## Recommended Next Gates

- active none — the deterministic gate path already covers this slice and the
  implemented changes passed it.
- passive keep watching `specdown` runtime because it remains a recurring hot
  spot in runtime summaries but was outside this slice.
- passive keep the ambient doc duplicate advisory until a docs/skill prose
  cleanup slice can classify or remove that family.

## History

- [spec/impl skill quality review](history/2026-06-25-critique-skill-quality-review.md)
