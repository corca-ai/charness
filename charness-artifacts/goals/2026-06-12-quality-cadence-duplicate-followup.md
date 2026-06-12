# Achieve Goal: Quality Cadence Duplicate Followup

Status: complete
Created: 2026-06-12
Activation: `/goal @charness-artifacts/goals/2026-06-12-quality-cadence-duplicate-followup.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: ready for slice 4 — final honest proof and next-candidate ledger.
- Next action: lock final/bundle verification, run broad proof once, then close with explicit non-claims and retro.
- Structural priority: closeout grammar must come from validator-owned
  templates or stubs with placeholders; operators fill values, not parser-shaped
  prose.
- Activation boundary: `/achieve`/Before-phase creates an inert draft artifact
  for the next session; only an explicit `/goal @...` pursuit may consume the
  host active-goal slot or start slices.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Improve the next Charness quality layer after the warn-band cleanup: first
repair the `achieve` authoring path so Before-phase goal shaping stays inert
until explicit `/goal` activation and closeout fixes use validator-backed
templates or stubs that operators fill through placeholders, then reduce
validation-churn waste with explicit slice-vs-bundle gate cadence, then run a
focused duplicate-family review if time remains.

## Non-Goals

- Do not push, publish, release, or depend on remote CI unless the operator
  explicitly asks.
- Do not rerun broad gates repeatedly during exploration; use focused probes
  until a slice boundary or final closeout.
- Do not fix goal closeout failures by manually reading validator grammar and
  hand-shaping prose as the normal workflow. That may diagnose a bug, but the
  productized path must be validator-owned templates or stubs.
- Do not activate, create a host active goal, or start slices while preparing a
  next-session goal artifact. Before-phase ends with a draft file and activation
  command only.
- Do not chase clone totals as the only success metric. A duplicate cleanup must
  name the specific family, owner surface, and maintainability benefit.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Local-only quality work is the default. Changes should be committed with their
  proof and closeout artifacts.
- If the first slice proposes changing validation policy, run a fresh-eye
  critique before locking the contract.

Discuss before activation: RESOLVED in-thread. The goal is local-only by default;
no push, release, remote CI, live proof, or host active-goal slot is authorized
until an explicit `/goal @...` pursuit or later operator instruction. Broad proof
is final/bundle-only, not per-slice.

## User Acceptance

- Inspect the committed slice(s) and confirm they reduce validation churn,
  duplicate-family pressure, or both.
- Re-run the focused tests named in the slice log.
- Confirm the final closeout distinguishes measured gate cost from proxy counts
  and does not claim broad duplication improvement from a metric-only change.
- Confirm achieve closeout authors no longer need to infer required grammar from
  validators for the common closeout fields; they receive a generated or
  documented placeholder surface that the validator accepts.
- Confirm `/achieve` preparation no longer confuses "shape a goal for later"
  with "activate or create a host-level active goal now."

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/check_changed_surfaces.py --repo-root . --json`
- Focused `ruff` and pytest for touched scripts/tests.
- `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing`
- If closeout templates/stubs are added, a focused regression that fills sample
  placeholders and proves `check_goal_artifact.py` accepts the result.
- A focused contract/test or skill instruction check that the Before-phase
  output remains `Status: draft`, includes the activation line, and does not
  instruct the agent to call host `create_goal` or execute slices.

### High-Confidence Checks

- Surface-recommended validators for touched docs, tests, artifacts, and policy
  files.
- Fresh-eye critique for validator-owned template/stub shape, validation-policy
  changes, or duplicate-family selection changes.
- Broad pytest at final/bundle boundary only:
  `pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py`.

### External Or Live Proof

- Not planned. No push/release/remote-CI proof is claimed unless explicitly run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Make achieve Before/After authoring path explicit: Before-phase drafts only, `/goal` pursues only, and closeout fields are template-first via validator-owned stubs. | The operator corrections are right: shaping a next-session goal must not activate it, and closeout authoring must not rely on opening grammar and hand-matching it. | Contract/helper change, focused tests that draft artifacts stay inert and filled closeout placeholders pass `check_goal_artifact.py`, plus clear instructions for both operator paths. | committed `ac7d37ea` |
| 2 | Reduce validation-churn waste by making slice-vs-bundle gate cadence explicit and testable. | The prior goal's host metrics showed repeated broad gates; the retro named this as the next workflow-quality problem. | Contract or helper change, focused tests, surface validators, and a before/after explanation of when broad proof runs. | committed in this slice commit |
| 3 | Run one focused duplicate-family review and cleanup if earlier slices leave time. | Length warn-band pressure is now zero, so duplicate-family cleanup can be selected on cohesion rather than emergency line limits. | Nose or equivalent family selection evidence, a targeted cleanup, and proof that behavior/assertions did not move into opaque helpers. | committed `75eed2fb` |
| 4 | Close with honest proof and next-candidate ledger. | Avoid repeating the previous low-yield closeout complaint. | Goal artifact complete, retro, host metric/proxy summary, and final validators. | active |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing: find-skills recommended `quality` for the active goal continuation; slices 1-2 used `impl` for code/test/doc changes and `critique` for fresh-eye review.
Gather: n/a — no external URL or private source context was used; slices 1-2 used local repo artifacts and docs only.
Release: n/a — slices 1-2 changed no version, release record, install manifest, or publication surface.
Issue closeout: n/a — slices 1-2 resolved no tracked GitHub issue and carry no close-intended issue.

## Slice Log

### Slice 1: Validator-backed goal-closeout stub

- Objective: Prove the goal-closeout authoring path is template/stub first and that a filled emitted stub passes the real complete-state goal validator without parser spelunking.
- Why this approach: The helper already rendered live validator-owned forms; the missing proof was an end-to-end regression against the documented dispatcher --emit-stub path.
- Commits: `ac7d37ea` Prove goal closeout stub authoring path
- What changed: Added a dispatcher-stub round-trip regression in tests/quality_gates/test_check_artifact_surface_preflight.py, documented the goal-closeout --emit-stub operator command in docs/conventions/authoring-preflight.md, aligned --emit-stub help text for shape-source emitters, synced plugins/charness/scripts/check_artifact_surface_preflight.py, and corrected this goal's active frame/coordination cues.
- Alternatives rejected: Did not change validator grammar, add a slug/date-aware emitter, broaden into validation-cadence gates, or run duplicate-family cleanup in this slice.
- Targeted verification: pytest -q tests/quality_gates/test_check_artifact_surface_preflight.py tests/quality_gates/test_achieve_before_activation.py tests/quality_gates/test_goal_artifact_lib.py tests/charness_cli/test_goal_helpers.py (117 passed); python3 scripts/check_artifact_surface_preflight.py --type goal-closeout --emit-stub; ruff check ...; python3 scripts/check_boundary_bypass_ratchet.py --repo-root .; python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest (completed; broad pytest skipped under pre-lock rehearsal policy).
- Test duplication pressure: Added one focused regression in an existing artifact-preflight test file; duplicate-pressure sampled through check_boundary_bypass_ratchet after the first subprocess version failed and was converted to in-process.
- Critique: Fresh-eye parent-delegated review recorded in charness-artifacts/critique/2026-06-12-goal-closeout-stub-roundtrip-critique.md; two angle reviewers and one counterweight found no remaining Act Before Ship findings after fixes.
- Off-goal findings: N/A — no off-goal findings filed.
- Lessons carried forward: When proving an operator command path, test the dispatcher output directly; helper-level proof alone can leave the authoring path unproven.
- Metrics: Broad pytest intentionally deferred to final/bundle boundary per this goal's validation-cadence contract; no live/external proof run.

### Slice 2: Slice-vs-bundle gate cadence

- Objective: Make the pre-lock slice proof versus final/bundle broad-proof boundary visible in generated goal frames and achieve lifecycle guidance.
- Why this approach: The prior goal's repeated broad gates created validation churn; the least disruptive fix is to put the cadence in the active frame that resumed sessions read first and pin it with a focused scaffold regression.
- Commits: this slice commit, `Document slice validation cadence`
- What changed: Added a Gate cadence bullet to the goal artifact template and canonical shape sample, documented the Charness-maintained repo cadence in the achieve lifecycle reference, synced the plugin mirrors, strengthened `test_check_goal_passes_on_scaffold_and_reports_gaps` to assert the full two-line bullet inside `## Active Operating Frame`, recorded fresh-eye critique, and fixed a stale markdown-link reference in `docs/conventions/validator-timing-layers.md` that blocked the doc gate.
- Alternatives rejected: Did not change `run_slice_closeout.py` behavior, genericize the command wording into an adapter abstraction, run broad pytest, or broaden into duplicate-family cleanup.
- Targeted verification: `pytest -q tests/quality_gates/test_goal_artifact_lib.py tests/quality_gates/test_achieve_before_activation.py tests/quality_gates/test_slice_closeout_broad_gate.py` (69 passed); `python3 scripts/check_changed_surfaces.py --repo-root . --json`; `python3 scripts/validate_skills.py --repo-root .`; `python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py`; `python3 scripts/check_skill_ownership_overlap.py --repo-root .`; `python3 scripts/validate_skill_ergonomics.py --repo-root .`; `python3 scripts/validate_public_skill_validation.py --repo-root .`; `python3 scripts/validate_public_skill_dogfood.py --repo-root .`; `python3 scripts/sync_root_plugin_manifests.py --repo-root .`; `python3 scripts/validate_packaging.py --repo-root .`; `python3 scripts/validate_packaging_committed.py --repo-root .`; `python3 scripts/check_doc_links.py --repo-root .`; `python3 scripts/check_command_docs.py --repo-root .`; `./scripts/check-markdown.sh`; `./scripts/check-secrets.sh`; `python3 scripts/validate_cautilus_proof.py --repo-root .`; `python3 scripts/validate_critique_artifacts.py --repo-root . --all`; `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`; `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing`; `python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support`; `python3 scripts/check_test_repo_copy_invariants.py --repo-root .`; `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`; `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest --ack-cautilus-skill-review` (completed; broad pytest skipped under pre-lock rehearsal policy).
- Public-skill review decision: `python3 scripts/check_skill_surface_preflight.py --path skills/public/achieve/references/goal-artifact.md --run-checks` passed; `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id achieve --json` showed the checked-in `achieve` dogfood contract already freezes the inert draft artifact and explicit `/goal @...` activation boundary, so no dogfood registry edit was needed for this cadence-only slice.
- Test duplication pressure: Added no new test file; strengthened one existing scaffold assertion to bind the cadence relationship in-place.
- Critique: Fresh-eye parent-delegated review recorded in `charness-artifacts/critique/2026-06-12-validation-cadence-critique.md`; two angle reviewers and one counterweight found no remaining Act Before Ship or Bundle Anyway findings after fixes.
- Off-goal findings: `docs/conventions/validator-timing-layers.md` had a stale backticked `validate_adapters.py` reference; fixed as a link-only markdown-gate repair.
- Lessons carried forward: Cadence rules belong in the active operating frame where resumed sessions start, and focused tests should assert the whole timing relationship rather than command-token presence.
- Metrics: Broad pytest intentionally deferred to final/bundle boundary per this goal's validation-cadence contract; no live/external proof run.

### Slice 3: Adapter scalar helper duplicate cleanup

- Objective: Select one focused duplicate family with an owner surface and reduce it without hiding behavior or chasing the whole clone backlog.
- Why this approach: `nose` showed the largest backlog is intentional portable skill boilerplate; repo-owned adapter scalar validation helpers were a smaller extractable family with a shared helper already present in `scripts/adapter_lib.py`.
- Commits: `75eed2fb` Reduce adapter scalar helper duplication
- What changed: Replaced local `_string` / `_string_list` helpers in `scripts/critique_adapter_lib.py`, `scripts/proof_semantics_adapter_lib.py`, `scripts/quality_adapter_lib.py`, and `scripts/simple_skill_adapter_lib.py` with `optional_string` / `optional_string_list`, synced plugin mirrors, and added direct scalar rejection assertions for proof verifier refs and simple adapter fields.
- Alternatives rejected: Did not refactor portable skill-local adapter resolver copies, change adapter semantics, alter `nose` ranking, or chase all clone families.
- Targeted verification: `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root . --recommend-for-task "focused duplicate-family review and cleanup for active achieve goal slice 3" --read-only --summary`; `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --top 20 --json`; `pytest -q tests/test_critique_prepare_packet.py tests/quality_gates/test_reviewer_tier_policy.py tests/quality_gates/test_quality_bootstrap.py tests/quality_gates/test_quality_mutation_testing.py tests/quality_gates/test_proof_semantics_adapter.py tests/quality_gates/test_proof_mismatch.py` (131 passed); `ruff check scripts/critique_adapter_lib.py scripts/proof_semantics_adapter_lib.py scripts/quality_adapter_lib.py scripts/simple_skill_adapter_lib.py tests/quality_gates/test_proof_semantics_adapter.py tests/quality_gates/test_quality_bootstrap.py`; `python3 scripts/sync_root_plugin_manifests.py --repo-root .`; `python3 scripts/check_changed_surfaces.py --repo-root . --json`; `python3 scripts/validate_packaging.py --repo-root .`; `python3 scripts/validate_packaging_committed.py --repo-root .`; `python3 scripts/validate_adapters.py --repo-root .`; `python3 scripts/validate_integrations.py --repo-root .`; `python3 scripts/sync_support.py --repo-root . --json`; `python3 scripts/update_tools.py --repo-root . --json`; `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`; `python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing`; `python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support`; `python3 scripts/check_test_repo_copy_invariants.py --repo-root .`; `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`; `python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing`; `python3 scripts/validate_critique_artifacts.py --repo-root . --all`; `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest` (completed; broad pytest skipped under pre-lock rehearsal policy).
- Test duplication pressure: Added two narrow assertions in existing adapter test files; no new test helper or fixture layer.
- Critique: Fresh-eye parent-delegated review recorded in `charness-artifacts/critique/2026-06-12-adapter-scalar-duplicate-cleanup-critique.md`; two angle reviewers plus one counterweight found no remaining Act Before Ship findings after the folded tests and wording correction.
- Off-goal findings: Remaining top `nose` families are mostly intentional portable skill bootstrap/resolver boilerplate; they are candidates for future portability-aware review, not this slice.
- Lessons carried forward: Treat `nose` as advisory selection evidence: pick a family with owner surface and extraction boundary, then record measured movement without claiming broad duplication health.
- Metrics: `nose` advisory moved from 524 to 523 total ranked families and from 3073 to 3045 duplicated lines in the top report; the selected scalar helper-shaped family moved from 15 files / 112 duplicated lines to 11 files / 84 duplicated lines. Broad pytest intentionally deferred to final/bundle boundary.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- Completed prior goal:
  `charness-artifacts/goals/2026-06-12-quality-duplication-workflow-improvement-6h.md`.
- Early-close report:
  `charness-artifacts/goals/2026-06-12-quality-duplication-workflow-improvement-early-close.md`.
- Retro:
  `charness-artifacts/retro/2026-06-12-quality-goal-closeout.md`.
- Recent lessons:
  `charness-artifacts/retro/recent-lessons.md`.
- Operator correction in 2026-06-12 session: closeout syntax should be
  validator-backed templates with placeholders, not prose hand-matched after
  opening validator grammar.
- Operator correction in 2026-06-12 session: `/achieve` preparation should create
  and discuss a draft goal artifact for the next session; it should not activate
  the goal or consume the host active-goal slot.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Goal mode: draft next-goal artifact now because the host `create_goal` slot
  refused a new goal in this thread even after the previous goal was complete.
- Scope priority: achieve activation-boundary and validator-backed closeout
  template/stub path first, validation-churn cadence second, focused
  duplicate-family review third, release execution context cleanup deferred
  unless the first three prove exhausted.
- Proof budget: focused gates during slices, broad pytest only at bundle/final
  boundary, because the prior retro identified repeated broad gates as waste.
- Authoring model: validators own accepted closeout shapes; the agent should fill
  placeholders in a generated or documented stub instead of reverse-engineering
  the grammar from failures.
- Activation model: `/achieve` Before-phase is artifact-only and inert; `/goal`
  is the only pursuit boundary that may create or resume host-level active goal
  execution.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Folded blocker: avoid metric-only success; the slice plan requires a concrete
  contract/helper/test or duplicate-family cleanup.
- Folded blocker: avoid repeating validation churn while trying to reduce it;
  broad proof is reserved for the final/bundle boundary.
- Folded blocker: avoid normalizing parser spelunking as the authoring path; the
  first slice must make the accepted closeout shape available from the validator
  or a validator-owned helper.
- Folded blocker: avoid normalizing accidental activation during preparation; the
  first slice must make the draft-vs-pursue boundary visible and mechanically
  hard to miss.
- Over-worry not folded: release execution context cleanup is valid but not the
  first slice because it is a design cleanup after a just-proven behavior split.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- Final proof initially used `origin/main` and pulled older, unrelated local commits into the proof range. Rerun with the goal-specific base `b300c8bf`.
- Remaining `nose` clone families are not all actionable debt; many are intentional portable skill boilerplate. Future cleanup should keep naming owner surfaces before editing.

## Final Verification

Verification lock: `python3 scripts/run_slice_closeout.py --repo-root . --base b300c8bf --verification-lock --ack-cautilus-skill-review --refresh-broad-pytest-proof` completed. Broad pytest ran once at final/bundle lock and passed in 230.1s.
Broad proof command: `pytest -q -m 'not release_only' tests/quality_gates tests/control_plane tests/test_*.py`
Final proof base: `b300c8bf` (`Mark followup goal activation discussion resolved`); proven range includes `ac7d37ea`, `21bd45e5`, and `75eed2fb`.
Outcome sufficiency check: sufficient — the three intended slices landed, the final bundle gate passed, no external/live proof was planned, and remaining duplicate-family backlog is explicitly not claimed fixed.

Retro: charness-artifacts/retro/2026-06-12-quality-cadence-duplicate-followup.md
Host log probe: charness-artifacts/probe/2026-06-12-quality-cadence-duplicate-followup-host-log-probe.json
Disposition review: charness-artifacts/critique/2026-06-12-quality-cadence-duplicate-followup-disposition-review.md

## User Verification Instructions

- Re-run `python3 scripts/run_slice_closeout.py --repo-root . --base b300c8bf --verification-lock --ack-cautilus-skill-review` if you want to recheck the final bundle without refreshing the already-written broad pytest proof.
- Inspect the three slice commits: `ac7d37ea`, `21bd45e5`, and `75eed2fb`.
- Confirm the duplicate cleanup claim is scoped: `nose` moved one scalar helper-shaped family, not the whole clone backlog.

## Auto-Retro

Retro dispositions: applied: final verification now records the goal-specific proof base `b300c8bf`, and the slice 3 records use the scalar helper-shaped family label instead of claiming broad clone health.
Structural follow-up: No new gate/tool follow-up — `run_slice_closeout.py --base` already provides the needed mechanism; this run needed disciplined base selection and scoped wording, not a new gate.
