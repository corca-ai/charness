# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-25T22:28:46Z
- **Prepared for**: f59869c6b reduction-first verification consumer binding
- **Substrate mode**: `committed-ref`
- **Changed ref**: `HEAD^..HEAD`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `8c455f03055dfa3799da13693c7a80dd0e7c8ef50e6c8ad85dec8d3e05741c07`
- **Reviewed paths**: 27
  - `plugins/charness/scripts/critique_verification_scope.py`
  - `plugins/charness/scripts/validate_critique_artifacts.py`
  - `plugins/charness/skills/critique/references/cadence.md`
  - `plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py`
  - `plugins/charness/skills/critique/scripts/verification_retry.py`
  - `plugins/charness/skills/quality/SKILL.md`
  - `plugins/charness/skills/release/SKILL.md`
  - `plugins/charness/skills/release/scripts/publish_release_artifact_sections.py`
  - `plugins/charness/skills/release/scripts/publish_release_cli.py`
  - `plugins/charness/skills/release/scripts/publish_release_common.py`
  - `plugins/charness/skills/release/scripts/publish_release_post_create.py`
  - `plugins/charness/skills/release/scripts/publish_release_verification_state.py`
  - `scripts/critique_verification_scope.py`
  - `scripts/validate_critique_artifacts.py`
  - `skills/public/critique/references/cadence.md`
  - `skills/public/critique/scripts/scaffold_critique_artifact.py`
  - `skills/public/critique/scripts/verification_retry.py`
  - `skills/public/quality/SKILL.md`
  - `skills/public/release/SKILL.md`
  - `skills/public/release/scripts/publish_release_artifact_sections.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_common.py`
  - `skills/public/release/scripts/publish_release_post_create.py`
  - `skills/public/release/scripts/publish_release_verification_state.py`
  - `tests/quality_gates/test_release_distinct_channel.py`
  - `tests/test_critique_scaffold.py`
  - `tests/test_verification_retry.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/reduction-first-verification-r3-packet.json --packet-sha256 e4d9fe43aa8a031e3a070245d7e1abb968b1a468bd74aa299ec937897347bb91 --identity-sha256 8c455f03055dfa3799da13693c7a80dd0e7c8ef50e6c8ad85dec8d3e05741c07
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
- **Reviewer runner**: `backend=codex_exec, mode=file-backed-worker, timeout_seconds=900`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed. Consume the worker receipt and delivery ledger; do not infer approval from a file or exit code.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section shape validation ok**: True

```text
Changed paths for ref `HEAD^..HEAD`:
- plugins/charness/scripts/critique_verification_scope.py
- plugins/charness/scripts/validate_critique_artifacts.py
- plugins/charness/skills/critique/references/cadence.md
- plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py
- plugins/charness/skills/critique/scripts/verification_retry.py
- plugins/charness/skills/quality/SKILL.md
- plugins/charness/skills/release/SKILL.md
- plugins/charness/skills/release/scripts/publish_release_artifact_sections.py
- plugins/charness/skills/release/scripts/publish_release_cli.py
- plugins/charness/skills/release/scripts/publish_release_common.py
- plugins/charness/skills/release/scripts/publish_release_post_create.py
- plugins/charness/skills/release/scripts/publish_release_verification_state.py
- scripts/critique_verification_scope.py
- scripts/validate_critique_artifacts.py
- skills/public/critique/references/cadence.md
- skills/public/critique/scripts/scaffold_critique_artifact.py
- skills/public/critique/scripts/verification_retry.py
- skills/public/quality/SKILL.md
- skills/public/release/SKILL.md
- skills/public/release/scripts/publish_release_artifact_sections.py
- skills/public/release/scripts/publish_release_cli.py
- skills/public/release/scripts/publish_release_common.py
- skills/public/release/scripts/publish_release_post_create.py
- skills/public/release/scripts/publish_release_verification_state.py
- tests/quality_gates/test_release_distinct_channel.py
- tests/test_critique_scaffold.py
- tests/test_verification_retry.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/critique_verification_scope.py, scripts/validate_critique_artifacts.py, skills/public/critique/references/cadence.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/critique/scripts/verification_retry.py, skills/public/quality/SKILL.md, skills/public/release/SKILL.md, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/publish_release_verification_state.py
  derived matches: plugins/charness/scripts/critique_verification_scope.py, plugins/charness/scripts/validate_critique_artifacts.py, plugins/charness/skills/critique/references/cadence.md, plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py, plugins/charness/skills/critique/scripts/verification_retry.py, plugins/charness/skills/quality/SKILL.md, plugins/charness/skills/release/SKILL.md, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py, plugins/charness/skills/release/scripts/publish_release_post_create.py, plugins/charness/skills/release/scripts/publish_release_verification_state.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: skills/public/critique/references/cadence.md, skills/public/quality/SKILL.md, skills/public/release/SKILL.md
  derived matches: plugins/charness/skills/critique/references/cadence.md, plugins/charness/skills/quality/SKILL.md, plugins/charness/skills/release/SKILL.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/critique/references/cadence.md, skills/public/quality/SKILL.md, skills/public/release/SKILL.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/references/cadence.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/critique/scripts/verification_retry.py, skills/public/quality/SKILL.md, skills/public/release/SKILL.md, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/publish_release_verification_state.py
  derived matches: plugins/charness/skills/critique/references/cadence.md, plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py, plugins/charness/skills/critique/scripts/verification_retry.py, plugins/charness/skills/quality/SKILL.md, plugins/charness/skills/release/SKILL.md, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py, plugins/charness/skills/release/scripts/publish_release_post_create.py, plugins/charness/skills/release/scripts/publish_release_verification_state.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/references/cadence.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/critique/scripts/verification_retry.py, skills/public/quality/SKILL.md, skills/public/release/SKILL.md, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/publish_release_verification_state.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/critique/references/cadence.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/critique/scripts/verification_retry.py, skills/public/quality/SKILL.md, skills/public/release/SKILL.md, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/publish_release_verification_state.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/critique_verification_scope.py, plugins/charness/scripts/validate_critique_artifacts.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/critique_verification_scope.py, scripts/validate_critique_artifacts.py, tests/quality_gates/test_release_distinct_channel.py, tests/test_critique_scaffold.py, tests/test_verification_retry.py
  derived matches: plugins/charness/scripts/critique_verification_scope.py, plugins/charness/scripts/validate_critique_artifacts.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/critique_verification_scope.py, scripts/validate_critique_artifacts.py, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/critique/scripts/verification_retry.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/publish_release_verification_state.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
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
