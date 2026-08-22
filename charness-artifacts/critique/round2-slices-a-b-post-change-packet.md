# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-11T13:56:05Z
- **Prepared for**: round-2 slices A and B post-change review
- **Adapter**: `.agents/critique-adapter.yaml`
- **Sections**: 2
- **Overall ok**: True

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `pending-parent-spawn`
- **Application state**: `unverified-by-packet`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths for working tree:
- charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release-round-2.md
- plugins/charness/scripts/record_usage_feedback.py
- plugins/charness/scripts/run_slice_closeout.py
- plugins/charness/scripts/slice_closeout_command_executor.py
- scripts/record_usage_feedback.py
- scripts/run_slice_closeout.py
- scripts/slice_closeout_command_executor.py
- tests/quality_gates/test_slice_closeout_broad_gate.py
- tests/test_usage_feedback.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/record_usage_feedback.py, scripts/run_slice_closeout.py, scripts/slice_closeout_command_executor.py
  derived matches: plugins/charness/scripts/record_usage_feedback.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_command_executor.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release-round-2.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/record_usage_feedback.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_command_executor.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/record_usage_feedback.py, scripts/run_slice_closeout.py, scripts/slice_closeout_command_executor.py, tests/quality_gates/test_slice_closeout_broad_gate.py, tests/test_usage_feedback.py
  derived matches: plugins/charness/scripts/record_usage_feedback.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_command_executor.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/record_usage_feedback.py, scripts/run_slice_closeout.py, scripts/slice_closeout_command_executor.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

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
- Retro owns its own prepare-packet slot through retro-adapter.yaml packet_sections; critique packets do not substitute for retro lesson judgment.
```

## Post-Change Critique Result

- **Target**: Slice A verification-lock sync-drift preflight and Slice B
  usage-feedback concurrent replay serialization.
- **Fresh-eye satisfaction**: parent-delegated bounded reviewer, requested
  `model=gpt-5.5` and `reasoning_effort=medium`; host accepted the requested
  fields but did not expose provider-side application metadata.
- **Valid reviewer**: `final_combined_slice_review` returned **APPROVE** after
  using only `git diff`, `rg`, `sed`, and `cmp` over the bounded files.
- **Boundary proof**:
  `.charness/reviewer-boundary/round2-final-slice-review.json` <!-- reproduction-source --> verified with
  `ok=true` and zero worktree/index drift after the review.
- **Quarantined reviews**: two earlier Slice A/B attempts ran forbidden sync or
  test/subagent commands. Their substantive observations were not counted as
  approval even though fingerprint verification reported zero tracked drift.
- **Parent countercheck fixed before approval**: an earlier unlock handler used
  `sys.exc_info()` inside the unlock exception handler, which could silently
  swallow a clean-body unlock failure. The final code uses explicit
  `body_failed` state and tests both error-precedence branches.

### Findings and counterweight

- **Blocker / important**: none in the final bounded review.
- **Advisory**: a git-inspection failure in Slice A raises fail-closed rather
  than attaching a structured closeout payload. This is acceptable for the
  normal repository precondition and does not weaken the lock.
- **Non-claim**: Slice B serializes cooperating feedback writers only. Mixed
  delivery/feedback writers were not reproduced as an escape and are not
  claimed covered.
- **Counterweight judgment**: keep both changes. Slice A removes repeated broad
  verification waste without weakening final cleanliness; Slice B adds a lock
  only around a reproduced duplicate-append escape. Do not add a public sync
  CLI, generated-path allowlist, mixed-writer lock protocol, or new broad gate.
