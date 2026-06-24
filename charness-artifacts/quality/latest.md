# Quality Review
Date: 2026-06-25

## Scope

Review `retro` as the first skill in the handoff's #401 quality-led skill
improvement sequence. Scope includes the public `retro` skill package, its
persistence and memory seams, consumer dogfood expectations, focused retro tests,
and any deterministic repo-gate failures discovered while running quality.

No Cautilus evaluator run was performed. This was a deterministic skill-quality
pass plus a bounded fresh-eye review; the user request did not provide a
log-backed behavior source or maintained scenario-registry change.

## Current Gates

- `retro` core remains inside the skill ergonomics budget:
  `core_nonempty_lines=140`, `reference_file_count=8`, `script_file_count=18`,
  `unlisted_reference_files=[]`.
- Consumer dogfood classifies `retro` as a persisted repeat-trap workflow:
  expected skill `retro`, artifact `charness-artifacts/retro/recent-lessons.md`,
  tier `hitl-recommended`, adapter `required`.
- Focused retro/handoff proof passed after fixes: 27/27 focused tests.
- Standing quality passed after fixes: 79/79 in 40.3s after the mutation
  coverage producer refreshed the committed retro script change.
- Handoff pickup planning is repaired: `docs/handoff.md` is 56 lines, status
  `ok`, and pickup returns `follow_workflow_trigger`.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median, budget
  90.0s; `pytest` 23.4s latest / 24.2s median, budget 140.0s; `check-coverage`
  18.9s latest / 19.5s median, budget 55.0s; `check-duplicates` 10.0s latest /
  11.9s median, unbudgeted.
- coverage gate: `./scripts/run-quality.sh --read-only` passed 79/79 after the
  handoff, scaffold, and mutation-coverage producer fixes.
- evaluator depth: deterministic gates only; Cautilus was not triggered by this
  quality review.

## Healthy

- `retro` has a concise-enough public core with progressive disclosure into
  focused references for modes, section shape, phase-aware efficiency,
  persistence, expert lenses, weekly trends, and sibling scans.
- Persistence is script-owned through `persist_retro_artifact.py`, including
  artifact writes, snapshot writes when configured, recent-lessons refresh, and
  legacy summary protection.
- Behavior proof exists around persistence, auto-trigger policy, artifact
  validation, scaffold generation, host-log probing, and Codex session auditing.
- Host-surface findings are mostly intentional adapter/evidence seams:
  `.agents` is canonical, `.codex`/`.claude` are compatibility fallbacks, and
  Codex-specific audit is optional evidence with unavailable/proxy semantics.
- The handoff prune removed stale status lines already owned by quality,
  release, operating-contract, or durable artifacts; no current next-session
  queue item was lost.

## Weak

- Fresh-eye review found one real retro defect: the scaffold emitted `yes: TODO
  path` under `## Persisted`, while the skill/reference contract expects an
  explicit `Persisted: yes...` or `Persisted: no...` statement. Fixed in
  `scaffold_retro_artifact.py` and mirrored into `plugins/charness`.
- A post-commit broad gate initially reported stale changed-line mutation
  coverage for the retro script; `run_slice_closeout.py
  --produce-mutation-coverage` refreshed it with `pytest -q
  tests/test_retro_scaffold.py`, and the next broad gate passed
  `check-changed-line-mutation-coverage`.
- Existing length-band warnings remain outside this slice: `run_slice_closeout.py`,
  `goal_artifact_lib.py`, `route_public_fetch.py`, and six test files are near
  their hard line limits.

## Missing

- No missing retro gate requiring immediate implementation remains after the
  scaffold fix. A broader validator that enforces exact `Persisted:` prose for
  all new retros may be useful, but existing historical fixtures use shorter
  forms, so that would need a migration policy rather than this narrow fix.

## Deferred

- Do not replace the optional `audit_codex_session.py` helper with a
  provider-neutral wrapper in this slice. Defer until a third host needs the same
  deep audit path or the compatibility fallback vocabulary starts leaking into
  user-facing retro output.
- Do not add a new blocking floor for exact persisted-line wording now; the
  low-risk fix is scaffold training plus a targeted scaffold test.

## Advisory

- command: `inventory_skill_ergonomics.py --repo-root . --json` reports
  `retro` heuristic `portable_package_host_surface_reference` with eight hits.
  Prose disposition: intentional adapter/evidence seams for this slice.
- prose review result: the ergonomics inventory's `prose_review_status=required`
  was satisfied by reviewing trigger boundaries, progressive disclosure,
  persistence behavior, host-surface findings, and the fresh-eye scaffold issue.
- command: `suggest_public_skill_dogfood.py --repo-root . --skill-id retro`
  reports persisted repeat-trap dogfood through `recent-lessons.md` and
  `hitl-recommended` tier.
- command: `./scripts/run-quality.sh --read-only` reports doc duplicate and code
  clone advisories outside retro: one HITL/narrative Markdown family and one
  multi-script small helper clone family.

## Delegated Review

- executed: bounded fresh-eye reviewer `019efbed-24bc-7630-9b1b-3d4ca511fa9e`
  found the scaffold persisted-line defect, confirmed the host-surface advisory
  is intentional/deferred, and confirmed the handoff prune is legitimate with no
  obvious information loss.
- Slow-gate lenses: fixture-economics, parallel-critical-path, duplicated-proof
  were not re-delegated because this slice did not redesign slow gates; runtime
  data is reported as existing evidence only.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id retro`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `pytest -q tests/test_retro_scaffold.py tests/quality_gates/test_retro_skill.py tests/test_retro_artifact.py tests/quality_gates/test_retro_persistence.py tests/quality_gates/test_retro_auto_trigger.py tests/test_handoff_plan.py::test_handoff_plan_derives_refresh_and_pickup_from_invocation_text`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock --produce-mutation-coverage --mutation-coverage-command "pytest -q tests/test_retro_scaffold.py"`
- `./scripts/run-quality.sh --read-only`

## Recommended Next Gates

- passive until a third host or repeated confusion appears: consider a
  provider-neutral session-audit wrapper for optional deep host-log evidence.
- passive because it needs migration policy: consider exact `Persisted:` wording
  enforcement for future retro artifacts without breaking historical fixtures.

## History

- [2026-06-16 quality review](./history/2026-06-16-quality-review.md)
