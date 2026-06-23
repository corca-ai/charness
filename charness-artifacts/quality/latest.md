# Quality Review
Date: 2026-06-23

## Scope

After publishing `v0.54.1`, evaluate one next skill candidate through the
`quality` lens. Candidate selected: `release`, because it owns irreversible
tag/publish/GitHub-release/issue-close/install-refresh boundaries where helper-
owned evidence and concise progressive disclosure matter more than raw prose
volume.

No Cautilus evaluator run was performed. This was a deterministic quality pass
plus bounded fresh-eye review; no live behavior fixture was needed to choose the
next planning target.

## Current Gates

- Release surface: `current_release.py` reports all checked-in release versions
  at `0.54.1`, `git_status: []`, and `drift: []`.
- Public release: `v0.54.1` is published at
  `https://github.com/corca-ai/charness/releases/tag/v0.54.1`; helper recorded
  public release verification, distinct-channel HTTP confirmation, and
  `charness update` install refresh.
- Fresh-checkout probes: `check_fresh_checkout_probes.py --run-probes --json`
  passed all three declared probes.
- Narrative audit: `audit_public_release_narrative.py --target-tag v0.54.1`
  passed for `charness-artifacts/release/latest.md`.
- Requested-review gate: `check_requested_review_gate.py` returned `ok` with a
  warning that `requested_review_commands` is empty, so this adapter surface is
  advisory-only.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median, budget
  90.0s; `pytest` 23.2s latest / 23.9s median, budget 140.0s;
  `check-coverage` 18.8s latest / 19.5s median, budget 55.0s;
  `check-duplicates` 10.0s latest / 11.9s median; `check-markdown` 4.8s median.
- coverage gate: not rerun as part of this candidate-only review; the just-run
  release helper already executed `./scripts/run-quality.sh --release`.
- evaluator depth: deterministic gates and fresh-eye review only; live evaluator
  proof is deferred until a concrete release dogfood fixture is designed.

## Healthy

- `release` already has strong helper-owned evidence. The publish helper owns
  fresh checkout probes, release visibility verification, distinct-channel
  confirmation, issue-close preflight, and post-publish install refresh.
- `skills/public/release/references/install-surface.md` clearly separates
  local/tag state, workflow publication, and public release surface verification,
  which matches the design north star for irreversible boundaries.
- Progressive-disclosure mechanics are structurally present: `SKILL.md` lists
  all four release references, and `inventory_skill_ergonomics.py` reports no
  unlisted release references.

## Weak

- `skills/public/release/SKILL.md` is under the hard core budget but still carries
  too much evidence sequencing inline: bootstrap command list, critique handling,
  fresh-checkout proof, narrative audit, issue closeout, and install refresh are
  all in the core workflow around lines 38-126.
- `release` has helper mechanics, but no `plan_release_run.py` equivalent to the
  new `quality` planner. The model still has to infer which helper outputs are
  required reads, pre-mutation checks, publish-boundary checks, and closeout
  evidence.
- Requested-review enforcement is adapter-advisory for this repo because
  `.agents/release-adapter.yaml` leaves `requested_review_commands` empty. This
  should not block the transition because critique and distinct-channel proof are
  separately enforced, but it is real evidence posture to keep visible.

## Missing

- Missing planner/helper packet: a release planning command should emit
  `required_reads`, current release state, pre-mutation blockers, publish-boundary
  packets, closeout evidence requirements, trust/cost notes, and next action.
- Missing dogfood fixture: `suggest_public_skill_dogfood.py --skill-id release`
  recommends a HITL-backed scenario for "verify and advance the checked-in
  release surface without hand-editing generated packaging artifacts." That is
  the right proof shape before compressing the core aggressively.

## Deferred

- Do not add a blocking gate for release core length. The current weakness is
  sequencing ergonomics and judgment load, not a low-noise line-count invariant.
- Do not make requested-review commands mandatory in this slice. First decide
  whether the existing critique gate and distinct-channel release verification
  already cover the meaningful release-closeout risk.
- Do not choose a raw line-count outlier instead of `release` only because it is
  longer. `release` has higher consequence per loaded line than many longer
  skills because it governs irreversible publish boundaries.

## Advisory

- command: `inventory_skill_ergonomics.py --json` reports release core lines:
  140; code fences: 8; bootstrap fences: 4;
  `host_surface_reference_count: 10`, `unlisted_reference_count: 0`. Interpreted
  finding: the host references are mostly legitimate adapter/package surfaces;
  the actionable signal is core sequencing pressure.
- command: `suggest_public_skill_dogfood.py --skill-id release --json` reports
  `validation_tier: hitl-recommended` and `adapter_requirement: required`.

## Delegated Review

- Delegated Review: executed — fresh-eye explorer agreed `release` is the right
  next candidate despite not being the worst raw ergonomics outlier, because its
  irreversible boundary risk makes planner/helper-owned evidence high leverage.
- Slow-gate lenses: fixture-economics, parallel-critical-path, and
  duplicated-proof were not the target; this review is skill-transition
  planning, not slow-gate redesign.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id release --json`
- `python3 skills/public/release/scripts/current_release.py --repo-root .`
- `python3 skills/public/release/scripts/check_real_host_proof.py --repo-root .`
- `python3 skills/public/release/scripts/check_requested_review_gate.py --repo-root .`
- `python3 skills/public/release/scripts/check_fresh_checkout_probes.py --repo-root . --run-probes --json`
- `python3 skills/public/release/scripts/audit_public_release_narrative.py --repo-root . --target-tag v0.54.1 --artifact-path charness-artifacts/release/latest.md --json`
- bounded fresh-eye subagent review over `skills/public/release`

## Recommended Next Gates

- active Add a `plan_release_run.py` helper that emits a report-first release
  packet: required reads, release state, pre-mutation blockers, publish-boundary
  evidence packets, closeout evidence, and `next_action`.
- active Use that planner to shrink `skills/public/release/SKILL.md` to trigger,
  phase order, and hard guardrails; move detailed bullets from workflow steps 3,
  6, 7, and 8 into existing references or planner output.
- passive until the planner exists and one dogfood prompt has run: compress other
  high-consequence skills with the same pattern.

## History

- [2026-06-16 quality review](./history/2026-06-16-quality-review.md)
