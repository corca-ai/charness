# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-06T01:19:52Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `47140a7074272918d9ae4bfd052a6501a1fa9c5b964a3dfd1b9f60f8f7d97ea0`
- **Reviewed paths**: 27
  - `charness-artifacts/create-skill/2026-09-06-impl-evidence-reuse.md`
  - `charness-artifacts/debug/2026-09-06-critique-preview-live-collision.md`
  - `charness-artifacts/debug/2026-09-06-release-advisory-meaning.md`
  - `charness-artifacts/debug/2026-09-06-staged-owner-universe.md`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/alias-baseline-acceptance.json`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/alias-candidate-acceptance.json`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/check_alias.py`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/check_cli.py`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/cli-baseline-acceptance.json`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/cli-candidate-acceptance.json`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/consumer-comparison.md`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias-baseline-spec.md`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias-candidate-spec.md`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias_baseline_catalog.py`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias_baseline_tests.py`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias_candidate_catalog.py`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias_candidate_tests.py`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli-baseline-readme.md`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli-candidate-readme.md`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli_baseline_repoctl.py`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli_baseline_tests.py`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli_candidate_repoctl.py`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli_candidate_tests.py`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/package-identities.json`
  - `charness-artifacts/probe/2026-09-06-consumer-journeys/protocol.md`
  - `docs/operating-contract.md`
  - `skills/public/impl/SKILL.md`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/goal798-final-consumer-release-packet.json --packet-sha256 8fe925ea438785dc2ff91219e5c51cf2a3dbb6f33714d1329e2ffd7569122cfc --identity-sha256 47140a7074272918d9ae4bfd052a6501a1fa9c5b964a3dfd1b9f60f8f7d97ea0
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
- charness-artifacts/retro/lesson-selection-index.json
- skills/public/critique/scripts/run_review.py
- skills/public/critique/scripts/run_review_packet.py
- skills/public/quality/SKILL.md
- charness-artifacts/critique/goal798-final-packet-extraction-packet.json
- charness-artifacts/critique/goal798-final-packet-extraction-packet.md
- charness-artifacts/critique/workers/goal798-final-packet-extraction/worker-report.yaml
- charness-artifacts/probe/2026-09-06-consumer-journeys/alias-candidate-acceptance.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/consumer-comparison.md
- charness-artifacts/probe/2026-09-06-consumer-journeys/final-review-paths.txt
- charness-artifacts/probe/2026-09-06-consumer-journeys/integration-full-refusal.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias_candidate_catalog.py
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias_candidate_tests.py
- charness-artifacts/retro/2026-09-06-session-retro.md
- charness-artifacts/retro/goal798-session-packet.json
- charness-artifacts/retro/goal798-session-packet.md

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/quality/SKILL.md
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: skills/public/quality/SKILL.md, charness-artifacts/critique/goal798-final-packet-extraction-packet.md, charness-artifacts/probe/2026-09-06-consumer-journeys/consumer-comparison.md, charness-artifacts/retro/2026-09-06-session-retro.md, charness-artifacts/retro/goal798-session-packet.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/quality/SKILL.md
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/quality/SKILL.md
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/quality/SKILL.md
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/goal798-final-packet-extraction-packet.json, charness-artifacts/critique/goal798-final-packet-extraction-packet.md, charness-artifacts/critique/workers/goal798-final-packet-extraction/worker-report.yaml
  verify: python3 scripts/review/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-09-06-consumer-journeys/alias-candidate-acceptance.json, charness-artifacts/probe/2026-09-06-consumer-journeys/integration-full-refusal.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-09-06-session-retro.md, charness-artifacts/retro/goal798-session-packet.json, charness-artifacts/retro/goal798-session-packet.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/lessons/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/lessons/build_retro_lesson_selection_index.py --repo-root . --check
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/lessons/build_retro_lesson_selection_index.py --repo-root . --write
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
