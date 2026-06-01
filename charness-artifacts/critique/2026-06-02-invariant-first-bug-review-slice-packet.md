# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-06-01T23:01:44Z
- **Prepared for**: workflow-review Slice 3 invariant-first bug review
- **Adapter**: `.agents/critique-adapter.yaml`
- **Sections**: 3
- **Overall ok**: True

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths for working tree:
- docs/public-skill-dogfood.json
- plugins/charness/scripts/validate_debug_artifact.py
- plugins/charness/skills/debug/SKILL.md
- plugins/charness/skills/debug/scripts/scaffold_debug_artifact.py
- plugins/charness/skills/issue/references/causal-review.md
- scripts/validate_debug_artifact.py
- skills/public/debug/SKILL.md
- skills/public/debug/scripts/scaffold_debug_artifact.py
- skills/public/issue/references/causal-review.md
- tests/quality_gates/test_debug_rca_reference_cite_chain.py
- tests/test_debug_artifact.py
- tests/test_debug_scaffold.py
- charness-artifacts/critique/2026-06-02-invariant-first-bug-review-slice-packet.json
- charness-artifacts/critique/2026-06-02-invariant-first-bug-review-slice-packet.md
- plugins/charness/skills/debug/references/invariant-first-review.md
- skills/public/debug/references/invariant-first-review.md

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/validate_debug_artifact.py, skills/public/debug/SKILL.md, skills/public/debug/scripts/scaffold_debug_artifact.py, skills/public/issue/references/causal-review.md, skills/public/debug/references/invariant-first-review.md
  derived matches: plugins/charness/scripts/validate_debug_artifact.py, plugins/charness/skills/debug/SKILL.md, plugins/charness/skills/debug/scripts/scaffold_debug_artifact.py, plugins/charness/skills/issue/references/causal-review.md, plugins/charness/skills/debug/references/invariant-first-review.md
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: skills/public/debug/SKILL.md, skills/public/issue/references/causal-review.md, charness-artifacts/critique/2026-06-02-invariant-first-bug-review-slice-packet.md, skills/public/debug/references/invariant-first-review.md
  derived matches: plugins/charness/skills/debug/SKILL.md, plugins/charness/skills/issue/references/causal-review.md, plugins/charness/skills/debug/references/invariant-first-review.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/debug/SKILL.md, skills/public/issue/references/causal-review.md, skills/public/debug/references/invariant-first-review.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/debug/SKILL.md, skills/public/debug/scripts/scaffold_debug_artifact.py, skills/public/issue/references/causal-review.md, skills/public/debug/references/invariant-first-review.md
  derived matches: plugins/charness/skills/debug/SKILL.md, plugins/charness/skills/debug/scripts/scaffold_debug_artifact.py, plugins/charness/skills/issue/references/causal-review.md, plugins/charness/skills/debug/references/invariant-first-review.md
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/debug/SKILL.md, skills/public/debug/scripts/scaffold_debug_artifact.py, skills/public/issue/references/causal-review.md, skills/public/debug/references/invariant-first-review.md
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/debug/SKILL.md, skills/public/debug/scripts/scaffold_debug_artifact.py, skills/public/issue/references/causal-review.md, skills/public/debug/references/invariant-first-review.md
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-06-02-invariant-first-bug-review-slice-packet.json, charness-artifacts/critique/2026-06-02-invariant-first-bug-review-slice-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/validate_debug_artifact.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: tests/quality_gates/test_debug_rca_reference_cite_chain.py, tests/test_debug_artifact.py, tests/test_debug_scaffold.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
```

## Non-Goals For This Contract

- **Section id**: `critique-prepare-non-goals`
- **Content kind**: `static`
- **Producer**: `static-config (inline)`
- **Section ok**: True

```text
- Charness does not classify section roles (source/derived/audit-only/rewrite). Roles stay consumer-defined.
- Charness does not enforce packet content correctness — the validator owns shape only.
- The retro skill does not consume this packet today. A retro-side prepare slot (retro-adapter.yaml packet_sections) is a separate follow-up.
```

## Slice Review Contract

- **Section id**: `slice-review-contract`
- **Content kind**: `static`
- **Producer**: `manual slice context after packet render`
- **Section ok**: True

```text
- Intent: encode a general invariant-first bug review pattern for workflow-boundary bugs without coupling to #275/#276 filenames or issue numbers.
- Expected invariant: when a producer emits a propagated diagnostic, readiness decision, closeout claim, or status value, the final operator-facing consumer must surface, refuse, or act on that signal before workflow success is claimed.
- Changed files and owning surfaces: use the packet's changed-files-and-owning-surfaces section; source, plugin mirrors, debug validator, scaffold, tests, dogfood, and this packet are in scope.
- Tests/proof: focused debug artifact/scaffold/RCA tests require current debug artifacts to include `## Invariant Proof` with producer proof, final-consumer proof, interface-shape sibling scan, and non-claims; focused packet, markdown, skill, dogfood, and debug tests passed after folded edits.
- Non-claims: Slice 3 does not complete the broader sibling-pattern audit or disposition matrix; that remains Slice 4. It also does not claim provider/runtime proof beyond local deterministic validators.
- Out of scope: weakening the root startup `find-skills` rule, adding per-commit fresh-eye critique, or filing/closing new public GitHub issues.
- Reviewer questions: does standalone `debug` now consume the invariant proof; does `issue` causal review consume it cite-only; are tests semantic rather than brittle prose guards; are plugin/generated surfaces synchronized.
```
