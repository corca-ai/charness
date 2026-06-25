# Quality Review
Date: 2026-06-25

## Scope

Review `retro` as the first #401 quality-led skill improvement: public skill
core, persistence/memory seams, dogfood, focused tests, and gate failures found
during quality.

Target boundary: `retro` public skill quality.
Ambient repo findings: handoff near-limit pruning was an ambient broad-gate
repair, not retro skill quality.

No Cautilus evaluator run was performed: this was deterministic skill-quality
plus bounded fresh-eye review, with no log-backed behavior source.

## Current Gates

- `retro` core remains inside the skill ergonomics budget:
  `core_nonempty_lines=146`, `reference_file_count=9`, `script_file_count=20`,
  `unlisted_reference_files=[]`.
- Consumer dogfood classifies `retro` as persisted repeat-trap workflow:
  `recent-lessons.md`, `hitl-recommended`, adapter `required`.
- Focused retro/handoff/packet proof passed after fixes: 52/52 focused tests;
  handoff pickup is repaired at 59 lines.

## Runtime Signals

- runtime source: `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median, budget
  90.0s; `pytest` 23.4s latest / 24.2s median, budget 140.0s; `check-coverage`
  18.9s latest / 19.5s median, budget 55.0s; `check-duplicates` 10.0s latest /
  11.9s median, unbudgeted.
- coverage gate: `./scripts/run-quality.sh --read-only` passed 79/79 after the
  retro packet fix, dup-ratchet re-baseline, and handoff near-limit fix.
- evaluator depth: deterministic gates only; Cautilus was not triggered by this
  quality review.

## Healthy

- `retro` has a concise-enough public core with focused references for modes,
  section shape, phase-aware efficiency, persistence, expert lenses, weekly
  trends, and sibling scans.
- Persistence is script-owned through `persist_retro_artifact.py`, including
  artifact writes, snapshot writes when configured, recent-lessons refresh, and
  legacy summary protection.
- Behavior proof exists around persistence, auto-trigger policy, artifact
  validation, scaffold generation, prepare packets, host-log probing, and Codex
  session auditing.
- Host-surface findings are mostly intentional adapter/evidence seams:
  `.agents` is canonical, `.codex`/`.claude` are compatibility fallbacks, and
  Codex-specific audit is optional evidence with unavailable/proxy semantics.
- The handoff prune removed stale status lines already owned by quality,
  release, operating-contract, or durable artifacts; no current next-session
  queue item was lost.

## Weak

- Prior closeout overstated the scaffold persisted-line finding: current scaffold
  uses allowed form `Persisted: yes: TODO path`; exact enforcement stays deferred.
- Current broad gate still reports stale changed-line mutation coverage for 13
  changed mutation-pool files; warning is non-blocking and remains active.
- This rerun initially failed the handoff pickup planner test at 70 lines
  (`near_limit`); pruning stale status detail restored pickup routing.
- Existing length-band warnings remain outside this slice: `run_slice_closeout.py`,
  `goal_artifact_lib.py`, `route_public_fetch.py`, and six test files are near
  their hard line limits.
- First quality closeout missed #401's explicit retro prepare-packet follow-up
  until challenged. Fixed here and treated as quality evidence.
- Dup-ratchet re-baseline was needed after adding retro packet/adapter boilerplate;
  `check_dup_ratchet.py --json` then returned `status=clean`.

## Missing

- No missing #401 retro gate requiring immediate implementation remains after the
  scaffold and prepare-packet fixes. Exact `Persisted:` prose enforcement may be
  useful later, but needs migration policy for historical fixtures.

## Deferred

- Do not replace optional `audit_codex_session.py` with a provider-neutral wrapper
  until a third host or user-facing compatibility leak appears.
- Do not add a new blocking floor for exact persisted-line wording now; the
  low-risk fix is scaffold training plus a targeted scaffold test.

## Advisory

- command: `inventory_skill_ergonomics.py --repo-root . --skill-path skills/public/retro/SKILL.md --json`
  reports `portable_package_host_surface_reference` with eight hits.
  Prose disposition: intentional adapter/evidence seams for this slice.
- prose review result: the ergonomics inventory's `prose_review_status=required`
  was satisfied by reviewing trigger boundaries, progressive disclosure,
  persistence behavior, host-surface findings, and the fresh-eye scaffold issue.
- structural review result: the prior run exposed two `quality` gaps: weak
  target-vs-ambient forcing and a missed #401 prepared-packet follow-up.
- command: `suggest_public_skill_dogfood.py --repo-root . --skill-id retro`
  reports persisted repeat-trap dogfood through `recent-lessons.md` and
  `hitl-recommended` tier.
- command: `./scripts/run-quality.sh --read-only` reports one HITL/narrative
  Markdown duplicate family outside retro.
- command: `inventory_nose_clones.py --repo-root . --json` reports code clone
  `status=clean` for scope paths `scripts`, `skills/public`, and
  `skills/support`: `family_count=0` after the accepted baseline, with
  `ranking.total_families=541` kept behind that baseline.

## Delegated Review

- executed: bounded fresh-eye reviewers reviewed the scaffold persisted-line concern
  (`019efbed-24bc-7630-9b1b-3d4ca511fa9e`) and confirmed the clone patch; current
  reviewer `019efcb0-840b-7c92-b587-a1d1c026311f` flagged the live mutation
  coverage warning above.
- Slow-gate lenses: fixture-economics, parallel-critical-path, duplicated-proof
  were not re-delegated because this slice did not redesign slow gates; runtime
  data is reported as existing evidence only.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id retro`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- focused retro/handoff/packet proof: 52/52; packet tests cover adapter
  validation, `charness.retro_prepare_packet`, markdown, and empty-section wording.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `run_slice_closeout.py --verification-lock --ack-cautilus-skill-review --refresh-broad-pytest-proof --produce-mutation-coverage` with retro packet/adapter/critique/quality focused mutation coverage.
- dup baselines: `check_dup_ratchet.py --write-baseline --json`; `inventory_nose_clones.py --write-baseline --json`
- `./scripts/run-quality.sh --read-only`

## Recommended Next Gates

- passive until a third host or repeated confusion appears: consider a
  provider-neutral session-audit wrapper for optional deep host-log evidence.
- passive because it needs migration policy: consider exact `Persisted:` wording
  enforcement for future retro artifacts without breaking historical fixtures.
- active for #401 next targets: a quality review must explicitly map issue text
  and prepared evidence to the target skill before declaring "good enough."

## History
- [2026-06-16 quality review](./history/2026-06-16-quality-review.md)
