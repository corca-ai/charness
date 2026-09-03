# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-03T09:41:09Z
- **Prepared for**: release 8.0.3 lock-in
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `8d225218ebcc395c607cd788845641f907ec21674b88347aa60d378db6b01d68`
- **Reviewed paths**: 54
  - `.agents/claude-host.md`
  - `.agents/quality-gates.yaml`
  - `.agents/release-adapter.yaml`
  - `AGENTS.md`
  - `README.md`
  - `charness`
  - `docs/agent-task-runs.md`
  - `docs/artifact-policy.md`
  - `docs/authoring-preflight.md`
  - `docs/capability-resolution.md`
  - `docs/cli-reference.md`
  - `docs/control-plane.md`
  - `docs/deferred-decisions.md`
  - `docs/design-north-star.md`
  - `docs/development.md`
  - `docs/docs-graph-checks.md`
  - `docs/documentation-principles.md`
  - `docs/export-boundary.md`
  - `docs/external-integrations.md`
  - `docs/gather-provider-ownership.md`
  - `docs/goal-lifecycle.md`
  - `docs/harness-composition.md`
  - `docs/host-packaging.md`
  - `docs/implementation-discipline.md`
  - `docs/index.md`
  - `docs/narrative-announcement-boundary.md`
  - `docs/operating-contract.md`
  - `docs/operator-acceptance.md`
  - `docs/operator-progressive-path.md`
  - `docs/parallel-execution.md`
  - `docs/prescribed-skill-closeout-contract.md`
  - `docs/proof-semantics-adapter.md`
  - `docs/provenance-placement.md`
  - `docs/public-skill-dogfood.md`
  - `docs/public-skill-validation.md`
  - `docs/runtime-capability-contract.md`
  - `docs/support-skill-policy.md`
  - `docs/surface-driven-adapter-triggers.md`
  - `docs/validator-timing-layers.md`
  - `docs/workflow-routes.md`
  - `docs/worktree-prepare.md`
  - `scripts/gates/check_timeout_bound_form.py`
  - `scripts/gates_support/runtime_root_retention.py`
  - `scripts/runtime_bootstrap.py`
  - `scripts/task_run/task_run_changed_line.py`
  - `scripts/task_run/task_run_completion.py`
  - `skills/public/achieve/SKILL.md`
  - `skills/public/achieve/scripts/goal_run_pickup.py`
  - `skills/public/impl/SKILL.md`
  - `skills/public/issue/SKILL.md`
  - `skills/public/quality/SKILL.md`
  - `skills/public/release/scripts/plan_release_run.py`
  - `skills/public/retro/SKILL.md`
  - `skills/shared/references/bootstrap-resolution.md`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8-0-3-gawande-1-packet.json --packet-sha256 a53035cbc3a4607867243910d7ef236895ece4340d7db8140e061b0c9894501d --identity-sha256 8d225218ebcc395c607cd788845641f907ec21674b88347aa60d378db6b01d68
```

Raw sha256sum is not the contract; the verifier owns the domain-separated packet identity check.
- **Sections**: 3
- **Shape validation ok**: True
- **Release approval**: not claimed

_This packet reports deterministic prepare-packet shape validation only; it is not a release-readiness or reviewer-verdict approval._

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `pending-parent-spawn`
- **Application state**: `unverified-by-packet`
- **Execution mode**: `file-backed-worker`
- **Reviewer runner**: `backend=codex_exec, mode=file-backed-worker, timeout_seconds=900`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed. Consume the worker receipt and delivery ledger; do not infer approval from a file or exit code.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/review/render_critique_section_changed_surfaces.py`
- **Section shape validation ok**: True

```text
Changed paths for working tree:
- charness-artifacts/critique/2026-09-03-release-8-0-3-reviewed-paths.txt
- charness-artifacts/critique/review-20260903T184044Z-184228-packet.json
- charness-artifacts/critique/review-20260903T184044Z-184228-packet.md

Owning surfaces:
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/review-20260903T184044Z-184228-packet.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-09-03-release-8-0-3-reviewed-paths.txt, charness-artifacts/critique/review-20260903T184044Z-184228-packet.json, charness-artifacts/critique/review-20260903T184044Z-184228-packet.md
  verify: python3 scripts/review/validate_critique_artifacts.py --repo-root . --all
```

## Non-Goals For This Contract

- **Section id**: `critique-prepare-non-goals`
- **Content kind**: `static`
- **Producer**: `static-config (inline)`
- **Section shape validation ok**: True

```text
- Charness does not classify section roles (source/derived/audit-only/rewrite). Roles stay consumer-defined.
- Charness does not enforce packet content correctness — the validator owns shape only.
- Retro owns its own prepare-packet slot through retro-adapter.yaml packet_sections; critique packets do not substitute for retro lesson judgment.
```

## Semantic Reviewer Question

- **Section id**: `reviewer-packet-semantic-question`
- **Content kind**: `static`
- **Producer**: `static-config (content_path: skills/shared/references/reviewer-packet-semantic-question.md)`
- **Section shape validation ok**: True

```text
# Reviewer-Packet Semantic Question

Use this question when a slice changes a guard, reference, claim, or verdict
surface. It keeps a reviewer packet anchored to what a reader or control must
know, rather than to the observable form that happened to expose the problem.

## Ask Before Broad Sampling

The packet author and reviewer should use all four parts when they apply. If a
part is not applicable or cannot be established, record `not applicable` or
`insufficient evidence` with the reason; do not silently claim the control is
proven.

1. **Semantic fact or invariant:** what must be true, independently of the
   current representation or failure spelling?
2. **Owning boundary:** which source, helper, renderer, reference, or workflow
   boundary carries or derives that fact, and who reads it?
3. **Recorded instance:** which concrete observed instance must this slice catch,
   explain, or preserve?
4. **Axis-varying counterexample:** what changes the semantic axis while keeping
   the observed form similar enough to expose a proxy-based control?

The question is a review aid, not a packet-readiness predicate. A clean tree is
not evidence that the selected control catches a recorded instance.

## Compare the Proposed Control

After naming the four parts, state the proposed predicate, claim, or surface
change and compare it with the counterexample:

- If the observed form changes while the semantic fact does not, reject or
  repair a control that changes its verdict with that form.
- If the semantic fact changes while the observed form stays similar, reject or
  repair a control that cannot distinguish the changed outcome.
- If the comparison cannot be made, record `unproven — defer`; do not approve it
  as though a clean-tree result were proof.
- For a behavior-changing helper or command, first record the bounded candidate
  search and scope. When that change has a reader-facing or copy-paste reference
  in scope, identify the first reader and verify that its demonstrated invocation
  preserves the claimed behavior. Disposition each discovered reference as
  updated, not applicable, or insufficient evidence with a reason. If no such
  reference is in scope, record `not applicable` with the search scope; if the
  reader cannot be checked, record `insufficient evidence` or `unproven — defer`
  rather than treating the helper's own tests as proof of reference safety.

These are reviewer dispositions, not an automated semantic gate.

## Decision Boundary

- Prefer a surface fix when the owning surface can carry or derive the semantic
  fact and prove the recorded instance.
- Keep the control as a reviewer question when the fact is judgment-bound or
  cannot be mechanically observed without guessing.
- Add a gate only when the predicate is mechanically observable, its false-fire
  cost is understood, and a recorded escape supports the addition.

This is a reviewer question, not a semantic meta-gate. It does not claim that a
host renders the packet, that a reviewer reaches the right judgment, or that a
clean-tree run proves the control.
```
