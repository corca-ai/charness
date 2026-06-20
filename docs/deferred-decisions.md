# Deferred Decisions

This document is the canonical closure surface for the deferred product-boundary
items that were previously listed in [`docs/handoff.md`](./handoff.md) `Discuss`.

## Scope

- Decision window: pre-`cautilus` integration closure
- Closed date: 2026-04-10
- Owner: current `charness` maintainer session

## Record Shape

Use this shape when a closed decision needs to be reopened:

```text
Decision ID:
Question:
Current choice:
Why now:
Alternatives considered:
Impact surfaces:
Reopen trigger:
```

## Closed Decisions (2026-04-10)

### D1. Shared Packaging Canonical Source

- Question: Which shared packaging manifest is canonical for Claude/Codex dual support?
- Current choice: [`packaging/charness.json`](../packaging/charness.json) stays the single source of truth.
- Why now: This is already how the checked-in plugin install surface and root marketplace files are generated and validated.
- Impact surfaces: [`docs/host-packaging.md`](./host-packaging.md), [`scripts/sync_root_plugin_manifests.py`](../scripts/sync_root_plugin_manifests.py), [`scripts/validate_packaging.py`](../scripts/validate_packaging.py)
- Reopen trigger: If host-specific metadata can no longer be represented as generated output from one shared manifest.

### D2. Evaluator Engine ID

- Question: Keep a legacy evaluator alias or standardize on one active product id?
- Current choice: Standardize on `cautilus` as the active product id for extraction-facing work, with no legacy naming compatibility.
- Why now: Current handoff and adapter flow already use `cautilus`, and keeping legacy naming would only preserve ambiguity.
- Impact surfaces: [`docs/handoff.md`](./handoff.md), [`.agents/cautilus-adapter.yaml`](../.agents/cautilus-adapter.yaml), future integration manifest naming
- Reopen trigger: If upstream evaluator branding or repository identity changes.

### D3. Packaging Version Ownership

- Question: Should shared packaging manifest carry release version directly or rely on export-time override?
- Current choice: Shared manifest remains canonical for default version; export-time override is allowed for host-specific release workflows.
- Why now: Preserves reproducibility while keeping release operations flexible.
- Impact surfaces: [`packaging/charness.json`](../packaging/charness.json), [`scripts/export_plugin.py`](../scripts/export_plugin.py), [`docs/host-packaging.md`](./host-packaging.md)
- Reopen trigger: If release tooling requires immutable manifest-only versioning with no override path.

### D4. Generated Export Tree Storage

- Question: Store generated Claude/Codex export trees as fixtures or keep script+temp smoke canonical?
- Current choice: Keep script-driven temporary materialization canonical; do not commit generated export trees.
- Why now: Avoids drift and duplicate source-of-truth risk.
- Impact surfaces: [`scripts/export_plugin.py`](../scripts/export_plugin.py), [`scripts/sync_root_plugin_manifests.py`](../scripts/sync_root_plugin_manifests.py), packaging docs
- Reopen trigger: If a downstream installer requires committed generated trees as contract artifacts.

### D5. `profile.extends` Depth

- Question: Promote `extends` into merged-bundle runtime behavior now?
- Current choice: Keep `extends` as constrained metadata seam; no broad merged-bundle runtime expansion in this phase.
- Why now: Avoids broad behavior complexity before evaluator integration.
- Impact surfaces: [`profiles/profile.schema.json`](../profiles/profile.schema.json), [`scripts/validate_profiles.py`](../scripts/validate_profiles.py)
- Reopen trigger: If real profile composition demand appears in downstream consumer repos.

### D6. Integration Capability Depth

- Question: How deep should capability grants/authenticated binary/env fallback go beyond metadata?
- Current choice: Keep metadata + validation contracts (`access_modes`, `capability_requirements`, `readiness_checks`, `config_layers`) without automating secretful runtime orchestration in `charness`.
- Why now: Matches host-neutral product boundary.
- Impact surfaces: [`integrations/tools/manifest.schema.json`](../integrations/tools/manifest.schema.json), [`scripts/validate_integrations.py`](../scripts/validate_integrations.py), [`scripts/doctor.py`](../scripts/doctor.py)
- Reopen trigger: If multiple consumers need standardized executable orchestration beyond current manifest metadata.

### D7. `official` Terminology in Discovery Policy

- Question: Replace `official` with broader wording (`trusted`/`declared`) now?
- Current choice: Replace `official` with `trusted` now.
- Why now: The actual policy boundary is host trust, not brand-official status.
- Impact surfaces: [`docs/support-skill-policy.md`](./support-skill-policy.md), `skills/public/find-skills/*`
- Reopen trigger: If the trust policy later needs a more precise distinction than one `trusted` bucket.

### D8. Profile Inheritance Policy

- Question: Allow richer inheritance vs flattened bundles?
- Current choice: Favor flattened effective bundles for execution, with minimal inheritance metadata retained for authoring convenience only.
- Why now: Predictable runtime behavior beats expressive inheritance at this stage.
- Impact surfaces: `profiles/*.json`, [`scripts/validate_profiles.py`](../scripts/validate_profiles.py), profile docs
- Reopen trigger: If flattening causes repeated maintenance burden across real consumer profiles.

### D9. Preset Contract Format

- Question: Move presets to JSON schema now or keep markdown-first catalog?
- Current choice: Keep markdown-first preset contract with required frontmatter until first downstream organization preset matures.
- Why now: Current preset surface is maintainer-oriented and stable with markdown validation.
- Impact surfaces: `presets/*.md`, [`scripts/validate_presets.py`](../scripts/validate_presets.py)
- Reopen trigger: If org-install preset scale needs stronger machine-only schema guarantees.

### D10. `ideation` Core Boundary

- Question: How much entity/stage thinking belongs in public core vs references?
- Current choice: Keep lightweight entity/stage framing in public core; push detailed playbooks, examples, and edge handling into references.
- Why now: Preserves a short trigger contract and portable defaults while relying on reference discoverability and agent reference-following.
- Impact surfaces: [`skills/public/ideation/SKILL.md`](../skills/public/ideation/SKILL.md), `skills/public/ideation/references/*`
- Reopen trigger: If repeated user confusion shows core guidance is too thin.

### D11. `spec` Weight Control

- Question: How to keep `spec` strong without procedural bloat?
- Current choice: Keep heuristic core (`Fixed Decisions` / `Probe Questions` / `Deferred Decisions`) and keep procedural detail, examples, and edge handling in references.
- Why now: Aligns with option-minimalism and current public authoring discipline while relying on reference discoverability and agent reference-following.
- Impact surfaces: [`skills/public/spec/SKILL.md`](../skills/public/spec/SKILL.md), `skills/public/spec/references/*`
- Reopen trigger: If implementation handoff quality repeatedly fails due to underspecified core guidance.

### D12. `quality` Skill Identity

- Question: Is `quality` a proposal skill, gate skill, or both?
- Current choice: `quality` remains a strong public proposal/review skill; deterministic enforcement stays in repo-owned quality gates/scripts.
- Why now: Preserves separation between operator guidance and CI/runtime enforcement without weakening the proposal surface into soft advice.
- Impact surfaces: [`skills/public/quality/SKILL.md`](../skills/public/quality/SKILL.md), [`scripts/run-quality.sh`](../scripts/run-quality.sh), quality docs
- Reopen trigger: If users need one unified interface that both proposes and enforces without ambiguity.

### D13. Sample Preset Scope

- Question: Keep sample presets repo-agnostic vs move to host/profile seams?
- Current choice: Keep `charness`-shipped presets repo-agnostic maintainer examples; make those examples realistic and varied, but keep consumer-specific install surfaces in downstream repos.
- Why now: Maintains portable source-of-truth boundaries without forcing shipped examples to stay toy-like.
- Impact surfaces: `presets/*`
- Reopen trigger: If cross-host install UX requires shipping host-specific presets in-core.

### D14. Quality Dogfood Proposal Promotion

- Question: Where should Session 10+ gate proposals be implemented?
- Current choice: Implement only deterministic, repo-owned gates in `charness`; keep evaluator/HITL-heavy checks in `cautilus` or explicit HITL workflows.
- Why now: Keeps `charness` guarantees honest and runnable in isolation.
- Impact surfaces: [`scripts/run-quality.sh`](../scripts/run-quality.sh), [`scripts/run_evals.py`](../scripts/run_evals.py), [`docs/public-skill-validation.md`](./public-skill-validation.md)
- Reopen trigger: If current repo-owned gates prove insufficient for regression containment.

### D15. `spec` Mode Strategy

- Question: Keep explicit mode menu or heuristic branch?
- Current choice: Stay with heuristic branch strategy; explicit mode menu remains retired.
- Why now: This direction is already implemented and reduces authoring overhead.
- Impact surfaces: [`skills/public/spec/SKILL.md`](../skills/public/spec/SKILL.md), [`skills/public/spec/references/contract-modes.md`](../skills/public/spec/references/contract-modes.md)
- Reopen trigger: If operators repeatedly request explicit mode selection for predictability.

### D16. `announcement` Delivery Kinds

- Question: How much delivery taxonomy belongs in `announcement` public core?
- Current choice: `announcement` is human-to-human communication. Public core covers draft shape, audience, and explicit human-facing delivery confirmation; actual delivery backends stay adapter-defined, and `command` is not a public core kind.
- Why now: `command` describes an implementation seam, not a communication concept.
- Impact surfaces: [`skills/public/announcement/SKILL.md`](../skills/public/announcement/SKILL.md), announcement references/examples
- Reopen trigger: If multiple consumers need the same additional human-facing delivery concept beyond draft style plus adapter-defined backend.

### D17. `hitl` Runtime State Depth

- Question: Keep portable minimum runtime state vs add richer queue/context tooling now?
- Current choice: Keep portable minimum runtime state model in public core for agent-to-human bounded review; consider richer queue and context tooling as future support-layer work.
- Why now: Keeps the public contract lean and host-neutral instead of turning `hitl` into a host-specific review product.
- Impact surfaces: [`skills/public/hitl/SKILL.md`](../skills/public/hitl/SKILL.md), support-layer roadmap
- Reopen trigger: If current state model cannot sustain real review-loop throughput.

## Open Deferrals (2026-05-07)

### D18. Workspace-Write Workflow Proof Carrier

- Question: Where does the workspace-write half of the read-only versus workspace-write proof split land — a new public-skill dogfood case, an existing dogfood entry, or a separate eval fixture?
- Current choice: Defer until the next dogfood slice picks the carrier; the no-write half is landed as `find-skills --read-only` ([skills/public/find-skills/SKILL.md](../skills/public/find-skills/SKILL.md), [skills/public/find-skills/scripts/list_capabilities.py](../skills/public/find-skills/scripts/list_capabilities.py)).
- Why now: Designing the workspace-write carrier needs a decision about whether it lives in [docs/public-skill-dogfood.json](./public-skill-dogfood.json) or in a new fixture under `evals/cautilus/`, and that decision is cleaner once the Cautilus adapter is re-enabled and the upstream eval runner is stable.
- Impact surfaces: [docs/public-skill-dogfood.json](./public-skill-dogfood.json), [evals/cautilus/](../evals/cautilus/), [charness-artifacts/spec/readme-proof-cautilus-eval-migration.md](../charness-artifacts/spec/readme-proof-cautilus-eval-migration.md), [.agents/cautilus-adapter.yaml](../.agents/cautilus-adapter.yaml), [scripts/agent-runtime/run-local-eval-test.mjs](../scripts/agent-runtime/run-local-eval-test.mjs)
- Reopen trigger: When the Cautilus adapter `run_mode` leaves `disabled` or when an unrelated workspace-write dogfood slice is started, whichever comes first; the next session that re-enables Cautilus must land both the workspace-write carrier and the routing-eval `--read-only` wiring before treating the read-only versus workspace-write split as closed.

### D19. Current-Pointer Write Scanner Generalization

- Question: Should [check_current_pointer_writes.py](../scripts/check_current_pointer_writes.py) detect adapter-resolved current-pointer writes via taint analysis, or rely on per-writer helper adoption?
- Current choice: Defer scanner generalization; rely on helper-adoption convention for adapter-resolved writers. The static scanner continues to catch string-literal `latest.md` / `latest.json` writes only.
- Why now: Only one adapter-resolved sibling ([hitl sync_review_artifact.py](../skills/public/hitl/scripts/sync_review_artifact.py)) was discovered, and it was closed in commit `0364886` by migrating to `write_current_pointer_text`. Adding taint analysis on a single sample is premature; the fixture matrix and false-positive surface are larger than the leak surface.
- Impact surfaces: [scripts/check_current_pointer_writes.py](../scripts/check_current_pointer_writes.py), [scripts/current_pointer_writer_lib.py](../scripts/current_pointer_writer_lib.py), future skill writers that resolve their durable artifact path through an adapter dictionary.
- Reopen trigger: When a second adapter-resolved current-pointer sibling that bypasses the string-literal scanner appears, or when more than one new skill adds a `latest.md` / `latest.json` writer through adapter-resolved paths without the helper.

### D20. Usage-Episodes Host-Hook State Per-Checkout Scope

- Question: Should `.charness/usage-episodes/host-hooks-state.json` be widened to detect side-by-side charness checkouts so `session-capture status` does not report "in sync" when a sibling checkout has also installed its own SessionStart hook?
- Current choice: Defer. State stays per-checkout; two checkouts each install their own command-path entry and both fire on each host session. Reporting reads only the local state.
- Why now: Two-checkout setups are rare and the spec's last-writer-wins semantics already permit duplicate `sessions/<id>/start.json` records. Adding cross-checkout discovery requires a machine-scoped registry that is out of scope for Slice B.
- Impact surfaces: [scripts/host_hook_install_lib.py](../scripts/host_hook_install_lib.py), [scripts/reconcile_usage_episodes_host_hooks.py](../scripts/reconcile_usage_episodes_host_hooks.py), [charness-artifacts/spec/usage-episodes-h-lam-t-completion.md](../charness-artifacts/spec/usage-episodes-h-lam-t-completion.md)
- Reopen trigger: When duplicate-recording on the same machine starts contaminating reporting, or when a maintainer reports confusion about which checkout installed an active hook.

### D21. Stale Host-Hook Entries After Checkout Path Change

- Question: How should charness recover the host-side SessionStart entry when the source checkout is moved to a new path so the recorded `command` string no longer matches any entry in host settings?
- Current choice: Defer cleanup tooling. Uninstall silently no-ops when the recorded command does not match; the maintainer must hand-edit `~/.claude/settings.json` or `~/.codex/config.toml` to remove the orphan.
- Why now: Slice B's success criteria are satisfied by the install/uninstall round-trip on a single canonical checkout path; orphan cleanup is a follow-up surface needing its own design.
- Impact surfaces: [scripts/host_hook_install_lib.py](../scripts/host_hook_install_lib.py), [scripts/reconcile_usage_episodes_host_hooks.py](../scripts/reconcile_usage_episodes_host_hooks.py)
- Reopen trigger: First report of an orphaned host hook after a checkout move, or when `session-capture status` starts reporting confusing drift caused by a stale path.

### D22. Hook Script Depth Cap for Repo-Root Discovery

- Question: Should [`scripts/usage_episode_session_start.py`](../scripts/usage_episode_session_start.py)'s `_discover_repo_root` add a hard depth cap on the parent-directory walk?
- Current choice: Defer. The existing `seen`-set already prevents infinite loops via symlink cycles, and typical walks resolve in 2–3 parent levels.
- Why now: No reported stalls on network mounts, and adding a constant adds friction without a forcing function.
- Impact surfaces: [scripts/usage_episode_session_start.py](../scripts/usage_episode_session_start.py)
- Reopen trigger: First report of a host session blocking on SessionStart due to slow parent traversal.

### D23. Codex Hook Block Representation Flip And Boundary Fragility

- Question: Should `install_codex_hook` / `uninstall_codex_hook` de-duplicate across the `codex-toml` and `codex-json` representations, and should the TOML block matcher tolerate hand edits between the `# charness:usage-episodes` marker and the `[[hooks.SessionStart]]` table header?
- Current choice: Defer for usage-episodes. `resolve_codex_target` picks the representation at install time, and the TOML block matcher requires the marker line to be immediately followed (modulo blank lines) by the table header. A user who later creates `~/.codex/hooks.json` can still get a second usage-episodes hook installed there without removing the original TOML block; hand-edited markers silently break uninstall.
- Find-skills exception: the find-skills SessionStart routing hook now cleans its known legacy TOML marker and removes charness-owned find-skills TOML blocks when Codex target selection moves to `hooks.json`, so `charness update` can converge that hook back to one user-level representation.
- Why now: Slice B closeout enables capture on a single canonical Codex layer; cross-representation churn and hand-edit recovery are not on the current dogfood path.
- Impact surfaces: [scripts/host_hook_install_lib.py](../scripts/host_hook_install_lib.py), [scripts/host_hook_codex_toml_lib.py](../scripts/host_hook_codex_toml_lib.py)
- Reopen trigger: First report of an orphaned Codex hook block after a representation flip, or a hand-edited Codex TOML hook block where uninstall reports `not_installed` while the block is still on disk.

### D24. Slice Closeout Emitter Best-Effort Posture

- Question: Should [`scripts/run_slice_closeout.py`](../scripts/run_slice_closeout.py) treat `emit_usage_episode_for_slice_closeout` failure (`invalid_adapter`, `invalid_records_path`, `emit_failed`) as a soft warning instead of a slice-fatal `payload["status"] = "failed"`?
- Current choice: Defer. Current behavior fails the slice on emitter error so a malformed adapter or full disk surfaces loudly. The maintainer accepts that trade-off on the current dogfood path.
- Why now: SC5/SC6 needs an actual emit to land for verification; a best-effort posture before that signal exists would mask the very evidence the slice is trying to capture.
- Impact surfaces: [scripts/run_slice_closeout.py](../scripts/run_slice_closeout.py), [scripts/slice_closeout_usage_episode.py](../scripts/slice_closeout_usage_episode.py)
- Reopen trigger: First time a verified slice fails closeout solely because the local emitter could not append (e.g. full disk, locked JSONL, gitignored path missing); revisit whether emitter errors should warn instead of fail.

### D25. Per-Host Install Exit Code

- Question: Should `cmd_session_capture_install` exit non-zero when one host installs and the other reports a `HostHookError`?
- Current choice: Defer. `reconcile_host_hooks` swallows per-host `HostHookError` into the JSON payload and the CLI returns 0 as long as the runner produced any payload. The operator must read the JSON to notice partial drift.
- Why now: First-time install on the maintainer's box succeeded for both hosts; a partial-failure exit code is not on the critical path for SC5/SC6.
- Impact surfaces: [scripts/host_hook_install_lib.py](../scripts/host_hook_install_lib.py), [`charness`](../charness) `cmd_session_capture_install`
- Reopen trigger: First time install succeeds on one host and silently fails on the other and the operator misses it because exit code is 0.

### D26. Hook Command Python Interpreter Resolution

- Question: Should the installed SessionStart command use `sys.executable` (or a `which python3` snapshot at install time) instead of the bare string `python3`?
- Current choice: Defer. `build_command` emits `python3 <abs-path>`; if a host session's PATH lacks `python3`, the host surfaces the failure noisily.
- Why now: The maintainer's machine has `python3` on PATH for every host session; pinning an interpreter would also complicate venv-based dogfood.
- Impact surfaces: [scripts/host_hook_install_lib.py](../scripts/host_hook_install_lib.py)
- Reopen trigger: First report of a Claude/Codex session surfacing `python3: command not found` from the installed SessionStart hook.

### D27. markdownlint-cli2 Verbose Banner Filter

- Question: Should [`check-markdown.sh`](../scripts/check-markdown.sh) keep the local `sed` `Finding:` filter forever, or replace it once markdownlint-cli2 adds a `--quiet` flag or equivalent upstream knob?
- Current choice: Defer. v0.21.0 has no quiet flag; the banner line listing every linted path is the only source of the per-commit ~50KB stdout flood that #230 Waste 2 targeted. The filter is anchored, load-bearing-space, and verified against a known-failing fixture (slice 6 critique, agentId `a28af53807ad5aef1`, F1+F3 confirmed Over-Worry).
- Why now: Local one-line fix is correct today and saves ~350x stdout bytes per commit; rewriting it under a future upstream flag would just be ceremony until the upgrade actually lands.
- Impact surfaces: [scripts/check-markdown.sh](../scripts/check-markdown.sh)
- Reopen trigger: markdownlint-cli2 ships a documented quiet/verbosity flag, OR the per-error line format changes such that legitimate errors now begin with the same prefix the filter drops (caught by slice 6 stop condition on every fixture run).

### D28. Template-First Fill Guards And Report-All For Sibling Artifact Validators

- Question: Should the fill-time guard comments added to the quality scaffold be generalized to the other scaffold families (debug, critique, retro, handoff, ideation), should the remaining low-rule-count validators (retro 3 rules, handoff 2, ideation 6) get `--report-all`, and should `emit_payload_main` in [scaffold_artifact_lib.py](../scripts/scaffold_artifact_lib.py) grow a `--write` mode so scaffold-first becomes the path of least resistance?
- Current choice: Defer the rest; `--report-all` was extended to the two high-rule-count siblings (critique 14 rules, debug 14) via the shared `run_validation_checks` helper in [artifact_validator.py](../scripts/artifact_validator.py) and wired into [run-quality.sh](../scripts/run-quality.sh). Quality remains the only family with fill-time guard comments because it is the only one with observed n-fold rework evidence; the doctrine in [adapter-gate-review.md](../skills/public/quality/references/adapter-gate-review.md) names the pattern so reviews can classify sibling gaps as `AUTO_CANDIDATE` instead of rediscovering them.
- Why now: Fail-fast on a 2-6 rule validator costs at most one or two extra runs, so report-all there is ceremony; fill guards designed without observed failure modes risk template alarm-fatigue; and `--write` needs its own overwrite/rotation semantics design across heterogeneous write paths (current-pointer vs dated record).
- Impact surfaces: [scripts/scaffold_artifact_lib.py](../scripts/scaffold_artifact_lib.py), [scripts/artifact_validator.py](../scripts/artifact_validator.py), the retro/handoff/ideation validators and the five sibling scaffolds, [scripts/run-quality.sh](../scripts/run-quality.sh).
- Reopen trigger: A session hits multi-run post-hoc validator rework on any sibling artifact family, or a slice already touches `emit_payload_main` for another reason.

### D29. Quality-Signal Scorecard Helper Script And Metric-Only Closeout Guard

- Question: Should the quality-signal scorecard ([quality-signal-scorecard.md](../skills/public/quality/references/quality-signal-scorecard.md), the #356 resolution) gain a helper script that renders a candidate scorecard skeleton from known adapter gates, and a closeout guard validator that refuses metric-only rationale for structural cleanup?
- Current choice: Defer both; ship the reference plus mandatory wiring from the inventory-dispatch structural-signals path, the testability/duplicate-pressure path, and the quality SKILL anchor. The issue's Desired Outcome requires the scorecard judgment itself; the helper and guard are its "Possible Direction" items.
- Why now: The scorecard rows are repo-judgment fields (behavior value, ownership, stop condition) that a renderer cannot fill, so a skeleton helper saves little until the prose contract has consumer mileage; a rationale-classifying guard is a content classifier, which the repo's deterministic-floor philosophy avoids until an observed gaming instance shapes a narrow checkable form.
- Impact surfaces: [skills/public/quality/references/quality-signal-scorecard.md](../skills/public/quality/references/quality-signal-scorecard.md), [skills/public/quality/references/inventory-dispatch.md](../skills/public/quality/references/inventory-dispatch.md), quality closeout validators.
- Reopen trigger: A consumer-repo run skips the scorecard despite the wiring (discovery failure), or a quality closeout ships metric-only rationale past review (guard-shaped failure), or an operator asks for the rendered skeleton.

### D30. dup-ratchet id-rotation affordance (gate auto-downgrade)

- Question: Should the boy-scout dup-ratchet gate recognize a pure `family_id`
  rotation (a "new" family whose position-independent member set matches a
  vanished baseline family) and downgrade it from hard-block to advisory, instead
  of forcing a manual re-baseline on every member-file edit that shifts a
  duplicated span?
- Current choice: Defer the affordance. Resolve the documentation half (correct
  the false "stable across sibling churn" claim) and document the
  verify-then-`--write-baseline` recovery as expected maintenance. The blocking
  behavior is unchanged; rotation-driven re-baselines remain manual.
- Why now: Solution (a) (re-key on a content-only id) is empirically impossible —
  nose's schema-v4 query output exposes no position-independent content id. The
  affordance needs a baseline schema migration (store a per-family
  position-independent member fingerprint) AND carries a false-negative tradeoff:
  a sorted member `(file, name)` fingerprint masks a genuinely new clone that
  reuses the same member files, which would be wrongly downgraded. That tradeoff
  deserves its own design + critique slice, not a rushed addition to a doc fix.
- Impact surfaces: [skills/public/quality/scripts/dup_ratchet_lib.py](../skills/public/quality/scripts/dup_ratchet_lib.py), [skills/public/quality/scripts/check_dup_ratchet.py](../skills/public/quality/scripts/check_dup_ratchet.py), [skills/public/quality/references/dup-ratchet.md](../skills/public/quality/references/dup-ratchet.md) ("Re-Baseline Triggers"), the gate + advisory id-set baselines, [charness-artifacts/debug/2026-06-21-dup-ratchet-family-id-rotation.md](../charness-artifacts/debug/2026-06-21-dup-ratchet-family-id-rotation.md)
- Reopen trigger: An operator hits rotation-driven re-baseline friction often
  enough to justify the schema migration, OR nose ships a position-independent
  content identity (which would enable solution (a) and flip the
  `test_real_nose_family_id_rotates_on_member_line_shift` characterization test).

## Next Action Contract

After these closures, the next major workstream is `cautilus` integration and
contract wiring, not further pre-`cautilus` product-boundary debate unless a
reopen trigger fires.
