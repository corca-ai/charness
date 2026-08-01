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
- Impact surfaces: [`docs/support-skill-policy.md`](./support-skill-policy.md), `scripts/capability_catalog*.py`
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
- Impact surfaces: [`skills/public/spec/SKILL.md`](../skills/public/spec/SKILL.md) (the contract-shaping heuristics, formerly `references/contract-modes.md`, are now inlined in the `## Contract Shaping` section)
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
- Current choice: Defer until the next dogfood slice picks the carrier; deterministic no-write inventory is now `charness catalog list --repo-root .` ([scripts/capability_catalog.py](../scripts/capability_catalog.py)).
- Why now: Designing the workspace-write carrier needs a decision about whether it lives in [docs/public-skill-dogfood.json](./public-skill-dogfood.json) or in a new fixture under `evals/cautilus/`, and that decision is cleaner once the Cautilus adapter is re-enabled and the upstream eval runner is stable.
- Impact surfaces: [docs/public-skill-dogfood.json](./public-skill-dogfood.json), [evals/cautilus/](../evals/cautilus/), [charness-artifacts/spec/readme-proof-cautilus-eval-migration.md](../charness-artifacts/spec/readme-proof-cautilus-eval-migration.md), [.agents/cautilus-adapter.yaml](../.agents/cautilus-adapter.yaml), [scripts/agent-runtime/run-local-eval-test.mjs](../scripts/agent-runtime/run-local-eval-test.mjs)
- Reopen trigger: When the Cautilus adapter `run_mode` leaves `disabled` or when an unrelated workspace-write dogfood slice is started, whichever comes first; the next session that re-enables Cautilus must land both the workspace-write carrier and the routing-eval `--read-only` wiring before treating the read-only versus workspace-write split as closed.
- Status (2026-07-05): reopen-trigger condition 1 has **FIRED** — the adapter is now `run_mode: ask` (eval-only re-enabled per corca-ai/cautilus#32), no longer `disabled`. The attached obligation (land the workspace-write carrier + the routing-eval `--read-only` wiring) was NOT completed at re-enablement and remains unlanded; disposition (land now vs. explicit re-defer) is pending operator decision. D18 stays open until dispositioned.

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
- Session-routing exception: the contextual SessionStart hook removes retired
  charness-owned TOML blocks when Codex target selection moves to `hooks.json`,
  so `charness update` can converge the hook back to one user-level representation.
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

### D28. Template-First Fill Guards And Report-All For Sibling Artifact Validators — POLARITY RESOLVED, FILL GUARDS STILL DEFERRED (2026-07-27)

- Question: Should the fill-time guard comments added to the quality scaffold be generalized to the other scaffold families (debug, critique, retro, handoff, ideation), should the sibling artifact validators share ONE one-pass control instead of per-family flag polarity, and should `emit_payload_main` in [scaffold_artifact_lib.py](../scripts/scaffold_artifact_lib.py) grow a `--write` mode so scaffold-first becomes the path of least resistance?
- Current choice (operator-decided, A+B+C): **the report-all half is fully resolved and the polarity split is closed.** (A) `validate_debug_artifact.py` and `validate_critique_artifacts.py` now default to one-pass, matching handoff/retro/ideation/quality. (B) `--fail-fast` is the only control across the family; `--report-all` survives as an accepted no-op so checked-in commands and older callers do not break on the flip, and `run-quality.sh` no longer passes it. (C) The flag pair is declared once in `add_one_pass_args`, and the four changed-path validators (critique, debug, retro, ideation) route their whole `main()` through `run_changed_artifact_validator` in [artifact_validator.py](../scripts/artifact_validator.py) — the two that previously justified a private `main()` now fit through hooks that model the real work: `extra_args` for critique's `--changed-ref` / `--changed-path` cross-surface probe, a `ChangedArtifactRun` context for its per-path `require_tier_evidence`, and `artifacts_fn` for debug's adapter-resolved output directory. The fill-guard and `--write` halves stay deferred on their original reasoning.
- Why now: **The original "report-all there is ceremony" premise was refuted by measurement, which is exactly this entry's reopen trigger.** The [lesson-recurrence retro](../charness-artifacts/retro/2026-07-26-lesson-recurrence-mechanism.md) measured ~8 validator rounds on a single handoff artifact — the one-rule-per-run report manufactured the retry loop that a separate checked-in lesson ("a counted limit is a planning input, not a retry loop") blames on the reader. Cost is not the rule count; it is that each round is a full gate run and the author re-reads the artifact each time. The flip reverses the explicit operator narrowing recorded in `a930cc5f`; that reversal is the operator's own call, made on this measurement. C is what stops the split re-forming: while each validator owned its own `main()`, matching defaults were a convention that the next artifact family could silently break.
- Impact surfaces: [scripts/artifact_validator.py](../scripts/artifact_validator.py), the debug/critique/retro/ideation/handoff/quality validators, [scripts/run-quality.sh](../scripts/run-quality.sh), [scripts/scaffold_artifact_lib.py](../scripts/scaffold_artifact_lib.py) and the five sibling scaffolds.
- Non-claims: the deprecated `--report-all` is accepted and ignored, NOT removed — a caller that passes it gets one-pass behavior, which is what it asked for. `--fail-fast` on debug and critique now also stops at the first failing ARTIFACT, not only the first rule; previously those two always collected across artifacts. That is the shared runner's semantics, adopted deliberately.
- Reopen trigger: `emit_payload_main --write`; fill guards for any family that accumulates observed n-fold rework evidence; or a new artifact validator that needs a hook `run_changed_artifact_validator` cannot express, since forking `main()` again is what re-opens the polarity risk.
- Trigger checked 2026-08-01: **not fired, stays deferred.** `emit_payload_main` in [scaffold_artifact_lib.py](../scripts/scaffold_artifact_lib.py) still has no `--write` argument; no family has accumulated recorded n-fold rework evidence; and no new artifact validator has forked `main()`. Checked, not assumed — the remainder was carried on the handoff as un-dispositioned work for weeks without anyone reading the trigger.

### D29. Quality-Signal Scorecard Helper Script And Metric-Only Closeout Guard

- Question: Should the quality-signal scorecard ([quality-signal-scorecard.md](../skills/public/quality/references/quality-signal-scorecard.md), the #356 resolution) gain a helper script that renders a candidate scorecard skeleton from known adapter gates, and a closeout guard validator that refuses metric-only rationale for structural cleanup?
- Current choice: Defer both; ship the reference plus mandatory wiring from the inventory-dispatch structural-signals path, the testability/duplicate-pressure path, and the quality SKILL anchor. The issue's Desired Outcome requires the scorecard judgment itself; the helper and guard are its "Possible Direction" items.
- Why now: The scorecard rows are repo-judgment fields (behavior value, ownership, stop condition) that a renderer cannot fill, so a skeleton helper saves little until the prose contract has consumer mileage; a rationale-classifying guard is a content classifier, which the repo's deterministic-floor philosophy avoids until an observed gaming instance shapes a narrow checkable form.
- Impact surfaces: [skills/public/quality/references/quality-signal-scorecard.md](../skills/public/quality/references/quality-signal-scorecard.md), [skills/public/quality/references/inventory-dispatch.md](../skills/public/quality/references/inventory-dispatch.md), quality closeout validators.
- Reopen trigger: A consumer-repo run skips the scorecard despite the wiring (discovery failure), or a quality closeout ships metric-only rationale past review (guard-shaped failure), or an operator asks for the rendered skeleton.

### D30. dup-ratchet id-rotation affordance (gate auto-downgrade) — RESOLVED (2026-06-27, Slice 4)

- Question: Should the boy-scout dup-ratchet gate recognize a pure `family_id`
  rotation (a "new" family whose position-independent member set matches a
  vanished baseline family) and downgrade it from hard-block to advisory, instead
  of forcing a manual re-baseline on every member-file edit that shifts a
  duplicated span?
- Resolution: Solved at the root rather than via a downgrade affordance. The gate
  and advisory now key code newness on a gate-computed, offset/path-INDEPENDENT
  **content fingerprint** (`nose_fingerprint_lib`) instead of nose's
  offset/path-folding `family_id`, so a pure line-shift no longer produces a "new"
  family at all (no hard-block to downgrade). See
  [spec Slice 4](../charness-artifacts/spec/boy-scout-dup-ratchet.md). The
  false-negative this decision blocked on is eliminated, not merely guarded: the
  fingerprint is content-derived, so a genuinely new clone that reuses the same
  member files still rotates the fingerprint (proven on live nose 0.15.0 — a real
  span edit `total=0 -> total=1` rotates it) — strictly dominating the path-set
  `(file, name)` fingerprint this decision rejected.
- Why deferral was right at the time: solution (a) (re-key on a content-only id)
  was read as "nose emits no position-independent content id" — true, but the
  resolution computes that identity gate-side from member spans rather than asking
  nose for it, behind a baseline schema migration (`dup_ratchet_baseline.v2` /
  `nose_baseline.v3`, `code_family_fingerprints`) and a member-preserving overlay
  remap. Residuals are honest and narrow (v1 rstrip-only rotates on in-place
  comment edits; membership-shrink still re-baselines) — see the spec's
  `S4-Defer-1..3`.
- Impact surfaces (migrated in lockstep): [skills/public/quality/scripts/nose_fingerprint_lib.py](../skills/public/quality/scripts/nose_fingerprint_lib.py) (new), [skills/public/quality/scripts/dup_ratchet_lib.py](../skills/public/quality/scripts/dup_ratchet_lib.py), [skills/public/quality/scripts/check_dup_ratchet.py](../skills/public/quality/scripts/check_dup_ratchet.py), [skills/public/quality/scripts/nose_report_lib.py](../skills/public/quality/scripts/nose_report_lib.py), [skills/public/quality/scripts/nose_baseline_lib.py](../skills/public/quality/scripts/nose_baseline_lib.py), [skills/public/quality/scripts/inventory_nose_clones.py](../skills/public/quality/scripts/inventory_nose_clones.py), [skills/public/quality/scripts/dup_review_lib.py](../skills/public/quality/scripts/dup_review_lib.py), [skills/public/quality/references/dup-ratchet.md](../skills/public/quality/references/dup-ratchet.md), the gate + advisory fingerprint baselines and the [dup-review.json](../charness-artifacts/quality/dup-review.json) overlay (originally omitted from this list), [integrations/tools/nose.json](../integrations/tools/nose.json), [charness-artifacts/debug/2026-06-21-dup-ratchet-family-id-rotation.md](../charness-artifacts/debug/2026-06-21-dup-ratchet-family-id-rotation.md)
- Residual reopen trigger (UPDATED 2026-07-08, goal `2026-07-08-retro-informed-improvement-5pack`
  Slice D): **S4-Defer-1 RESOLVED** — `nose_fingerprint_lib` algo v2 tokenizes each
  Python member span and drops comment/pure-whitespace-structure tokens, so an
  in-place comment or internal-whitespace edit no longer rotates the fingerprint (a
  span that fails to tokenize standalone falls back per-member to v1 rstrip-only);
  `FINGERPRINT_ALGO_VERSION` bumped to `"2"`. **S4-Defer-3 RESOLVED** — the gate
  baseline moved to schema v3 (`code_families`: `{fingerprint, member_hashes}`) and
  `check_dup_ratchet.py` runs a `classify_reductions` pre-pass: a candidate-new
  family whose member multiset is a PROPER sub-multiset of a vanished baseline
  family's is an advisory membership REDUCTION (never silent — one
  `--accept-rotation`-naming line per reduction), not a hard block; a membership
  GROW still hard-blocks and re-baselines (S4-D9 unchanged). **S4-Defer-2
  narrowed**: once a reduction is accepted via `--accept-rotation`, the baseline
  holds only the shrunk family, so the original full member set recurring under a
  different identity is no longer a superset of anything vanished and hard-blocks
  (the shrink-then-recur adversary is covered by a fixture test); the residual now
  applies only while a printed reduction advisory sits unaccepted. See
  [spec Slice 4](../charness-artifacts/spec/boy-scout-dup-ratchet.md) (the
  S4-Defer-1/2/3 entries) and
  [references/dup-ratchet.md](../skills/public/quality/references/dup-ratchet.md).

### D31. Handoff chunker should reconcile against recent commits

- Question: Should the `handoff` chunked-routing pipeline consume recent commits
  (`origin/main..HEAD` or last-N) in addition to handoff entries + open issues, so a
  pickup automatically reconciles the backlog against just-committed work?
- Current choice: Defer the pipeline change; for now the handoff `Workflow Trigger`
  carries a "body-read the issues, don't trust the list flat" directive and the
  refresh commands already include `git log`. The chunker itself does not yet read
  commits.
- Why now: A 2026-06-21 session demonstrated the gap — #395's closeout satisfied the
  overhaul-sweep R2 live proof, and chunk-2's multi-root change altered #391's
  surface, but both were caught only by manual commit reading, not the chunker. The
  correct form is NOT a candidate union (commits are *done work*, not *to-do*): it is
  a **reconcile/enrich pass** that (a) flags candidates a recent commit likely
  closed/obviated (de-stale), and (b) harvests commit-body `Close #N` / `deferred X`
  / `follow-up Y` markers as new signals. Designing that pass — and its precision
  (avoid false "already done" suppression) — is its own slice, not a drive-by.
- Impact surfaces: [chunked-routing.md](../skills/public/handoff/references/chunked-routing.md),
  [parse_handoff_entries.py](../skills/public/handoff/scripts/parse_handoff_entries.py)
  (and the proposer/ranker), [handoff-chunked-routing.md](./handoff-chunked-routing.md)
  (authoring-repo-internal contract).
- Reopen trigger: A pickup again misses a backlog item already resolved/obviated by a
  recent commit, or the chunker's issue-union is extended for another reason.

### D32. Capture observation metrics still trust the session tree (the #409 Gap-2 channel)

- Question: Should [`build-skill-execution-observation.mjs`](../scripts/agent-runtime/build-skill-execution-observation.mjs) stop deriving per-run METRICS (token/tool counts) from the session-tree `*.jsonl` glob, the same channel #409 Gap 2 proved can drop the final assistant block on a clean natural-completion exit?
- Current choice: PARTIALLY RESOLVED, remainder deferred. The SHARP facet — the non-advisory `requiredSummaryFragments` floor-match, which reads the run CLOSEOUT — is now CLOSED: `build-skill-execution-observation.mjs` sources the summary from the authoritative `stream.jsonl` (`--stream`, else the sibling auto-detect) instead of the tree, so a dropped closeout block no longer produces a false RSF MISS on a passing run. What REMAINS deferred is only the ADVISORY efficiency METRICS (token/tool counts) that still glob the tree (`build-skill-execution-observation.mjs` `listSessionTreeJsonl`); a truncated tree under-counts them, but those metrics never gate and read the [min–max] range, so a single dropped block is low-impact.
- Why now: The summary/floor-match reroute shipped as its own slice (the mjs `finalTextEvents` source + `run_one` `--stream` wiring + tests) because that path is gating-relevant. Rerouting the advisory METRICS onto `stream.jsonl` would need the metrics counters to read the stream shape too (a separate parser + self-test) and is not gating, so it stays deferred rather than widening this fix.
- Impact surfaces: [scripts/agent-runtime/build-skill-execution-observation.mjs](../scripts/agent-runtime/build-skill-execution-observation.mjs) (metrics counters only — the summary path is done), [scripts/run_skill_efficiency_ab.py](../scripts/run_skill_efficiency_ab.py), the advisory `output_lines`/token/tool metrics.
- Reopen trigger: A capture's ADVISORY metrics are observed to misread because the session tree dropped a block, or the metrics counters are touched for another reason. (The summary-path truncation this D was opened around is resolved.)

### D33. Split run_skill_efficiency_ab.py at the next module-growing change

- Question: [scripts/run_skill_efficiency_ab.py](../scripts/run_skill_efficiency_ab.py) sits at 479 tokei code lines (hard limit 480, **1 left** after the D32 summary-path fix added the `--stream` observe arg). Should it be split now or at the next change?
- Current choice: Defer the split ONE more time — but the runway is gone. The file is still a single cohesive harness (aggregate/compare → live orchestration → self-test → CLI), an honest cohesive unit near its limit, not a grab-bag to split reactively; splitting mid-bugfix (twice now) would be the reactive churn the length advisory itself warns against. The **next** code-line addition exceeds the hard limit, so the following change MUST extract a module first (candidate seam: the live-capture orchestration `run_one`/`_capture_base`/`preserve_outputs` block into a `skill_capture.py` sibling), not append. RESOLVED 2026-07-09 by the #423 slice: the pure aggregation/report section was extracted to [scripts/skill_efficiency_report.py](../scripts/skill_efficiency_report.py) (384 code lines remain), a different seam than the self-test candidate named below — chosen because it was the cleanest pure boundary and test-compat re-exports kept the harness intact.
- Why now: Splitting touches the custom `load_script_module` test harness and risks a circular import between the main module and an extracted self-test module (`selftest` imports `ranks_worse`/`_metrics_from_packet`; `main` imports `selftest`) — real risk that does not belong in a correctness bugfix.
- Extraction candidate: the self-test section (`_event`/`_result`/`_ts`/`_write_lean`/`_write_wasteful`/`_dump`/`_SELFTEST_SPEC`/`SELFTEST_KEYS`/`_observe`/`selftest`, ~100 lines) into a sibling module, importing the shared pure helpers explicitly.
- Impact surfaces: [scripts/run_skill_efficiency_ab.py](../scripts/run_skill_efficiency_ab.py), [tests/test_skill_efficiency_ab.py](../tests/test_skill_efficiency_ab.py), [scripts/check_python_lengths.py](../scripts/check_python_lengths.py) warn band.
- Reopen trigger: The next change that adds net code lines to this file (it will hard-fail the 480 gate), or the self-test section is touched for another reason. Fired and satisfied on 2026-07-09: the #423 slice added net code lines and the 480 gate hard-failed, resolved by the extraction above.

### D34. Announcement delivery `confirmed` accepts a same-observer self-attestation

- Question: Should [`record_announcement.py`](../skills/public/announcement/scripts/record_announcement.py) accept `--verification-status confirmed` for an external write (e.g. `human-backend`) on a caller self-attestation, or require an *independent* channel/observer (the north-star P4 distinct-channel test) before a delivery may be recorded `confirmed`?
- Current choice: DECLINED (2026-07-04, operator decision) — not pursuing; accept the disclosed presence-floor residual as-is. Surfaced by the PR #419 adversarial verification and confirmed by an independent verifier: the floor enforces the *presence* of a typed verification record, not its *independence*, so a same-observer `confirmed` passes. The code openly frames itself as a presence/typed-disposition floor, so this is a disclosed residual, not a regression. Tightening it would change what passes at an irreversible boundary and would need its own critique cycle (likely an adapter-contract seam for the independent readback); the operator judged that cost not worth it for a disclosed presence floor.
- Impact surfaces: [record_announcement.py](../skills/public/announcement/scripts/record_announcement.py), [announcement_verification_lib.py](../scripts/announcement_verification_lib.py), [delivery-seams.md](../skills/public/announcement/references/delivery-seams.md), [adapter-contract.md](../skills/public/announcement/references/adapter-contract.md).
- Reopen trigger: An announcement is recorded `confirmed` on a self-attestation that later proves wrong, or the delivery-verification seam is touched for another reason.

### D35. Release distinct-channel probe shape-match is loose against same-proxy commands

- Question: Should [`publish_release_post_create.py`](../skills/public/release/scripts/publish_release_post_create.py) `_probe_matches_release_view_shape` tighten its leading-token match so a near-identical *same-proxy* command (extra whitespace, trailing args) cannot satisfy the "distinct-channel" behavioral probe?
- Current choice: DECLINED (2026-07-04, operator decision) — not pursuing; accept the same-proxy-guard residual as-is. Surfaced by the PR #419 adversarial verification (independent verifier: minor, disclosed): the prefix match flags leading-token same-proxy forms, but a `gh release view` variant with args before the tag can evade the flag and be recorded as the distinct-channel confirmation. Tightening the shlex match risks rejecting legitimate probe forms and is a boundary-semantics change; the operator judged it not worth pursuing, especially as the default HTTPS-fetch channel (used when no adapter probe is configured) is already genuinely distinct.
- Impact surfaces: [publish_release_post_create.py](../skills/public/release/scripts/publish_release_post_create.py), [publication-boundary.md](../skills/public/release/references/publication-boundary.md).
- Reopen trigger: A release records a same-proxy probe as a distinct-channel confirmation, or the probe-matching logic is touched for another reason.

### D36. Surface the question/decision-needed exemption on the commit-msg close carrier

- Question: Should [`check_issue_closeout_commit_msg.py`](../scripts/check_issue_closeout_commit_msg.py) surface a non-blocking REVIEW advisory when a close self-classifies `question`/`decision-needed` (mirroring [`issue_close_comment_floor.review_advisory_for_classification`](../skills/public/issue/scripts/issue_close_comment_floor.py)), so the floor exemption is not the silent path on the commit-message carrier the way it already is not on `close-with-comment`?
- Resolution: RESOLVED (2026-07-04, this session) exactly as the deferral named.
  `review_advisory_for_classification` now has a single carrier-neutral owner in
  `issue_verify_closeout_body.py` (`FLOOR_EXEMPT_CLASSIFICATIONS` + a unified
  `(classification, *, numbers=None, source=None)` signature), re-exported through
  `issue_verify_closeout.py`, with `issue_close_comment_floor.py` reduced to a
  re-export (no duplicated body). `check_issue_closeout_commit_msg.py` surfaces the
  advisory via `_exemption_advisories` + `_emit_human_output` and a `review_advisory`
  JSON field — non-blocking, exit stays 0. The classification-only close-with-comment
  call is byte-identical to before (scope suffix empty when `numbers` is None). No new
  authored duplication: dup-ratchet stayed clean for the changed files; the one accepted
  baseline family (`97ac3e8f904686f5`, scoped `--accept-family`) is a collateral nose
  global-clustering rotation among UNTOUCHED files (`check_prose_pin`/`check_skill_cut_safety`
  gained `render_critique_section_changed_surfaces` as a third member) triggered because the
  `main()` thinning removed a pre-existing clone — verified by fingerprint set-diff and an
  independent fresh-eye subagent (SHIP, all six angles execution-confirmed). Critique:
  [d36-close-exemption-advisory-single-source](../charness-artifacts/critique/2026-07-04-d36-close-exemption-advisory-single-source.md).
- Why deferral was right at the time: doing it as a pre-release ride-along on PR #419 would
  have shipped either the dup-ratchet-blocked copy or a rushed shared-owner refactor at an
  irreversible boundary; the shared-owner seam + its fresh-eye pass earned their own slice.
- Impact surfaces (migrated in lockstep): [check_issue_closeout_commit_msg.py](../scripts/check_issue_closeout_commit_msg.py), [issue_close_comment_floor.py](../skills/public/issue/scripts/issue_close_comment_floor.py), [issue_verify_closeout_body.py](../skills/public/issue/scripts/issue_verify_closeout_body.py), [issue_verify_closeout.py](../skills/public/issue/scripts/issue_verify_closeout.py), their plugin mirrors, the gate baseline [dup-ratchet-baseline.json](../charness-artifacts/quality/dup-ratchet-baseline.json), and tests ([test_issue_close_exemption_advisory.py](../tests/test_issue_close_exemption_advisory.py), the commit-msg in-process + hook suites).
- Residual reopen trigger: a commit-message close self-classifies `question`/`decision-needed`
  and skips the behavioral/critique floors with no reviewer noticing, or the shared close
  advisory is touched for another reason. Orphan baseline fingerprints (`3d4af4`, `d38941`)
  left by the additive scoped-accept were the known D30 residual churn, not a D36
  regression; both were pruned from the gate baseline by the nose 0.18.0→0.19.0
  re-baseline that rode release v1.0.10 (commit `51dfc479`), so they no longer
  exist on disk (verified 2026-07-16).

### D37. Post-capture identity-leak assertion in the scoring path

- Question: should the scoring path ([`build-skill-execution-observation.mjs`](../scripts/agent-runtime/build-skill-execution-observation.mjs) / [`run_skill_efficiency_ab.py`](../scripts/run_skill_efficiency_ab.py) outcome grading) hard-assert that the captured transcript contains no eval-identity tokens (out-dir basename, grader filenames), rather than relying on the capture script's advisory stderr canary?
- Current choice: DEFER. #423 closed the leak structurally (neutral mktemp run base; behavioral pytest executes the script and asserts the invariant from outside) and the in-script canary is advisory by floor-addition restraint (promote only on recorded recurrence). A scoring-path floor would need a token list contract and risks false-fires on legitimate repo content.
- Why now: bundling a new blocking floor into the leak fix is the validator-post-hoc-churn reflex; the behavioral test covers the regression class the floor would target.
- Impact surfaces: [capture-skill-run.sh](../scripts/agent-runtime/capture-skill-run.sh) (canary), [build-skill-execution-observation.mjs](../scripts/agent-runtime/build-skill-execution-observation.mjs), [run_skill_efficiency_ab.py](../scripts/run_skill_efficiency_ab.py), [test_skill_efficiency_ab.py](../tests/test_skill_efficiency_ab.py) (behavioral test).
- Reopen trigger: a capture is observed reasoning from its eval identity DESPITE the neutral run base (canary fires or transcript shows it), or the scoring path is reworked for another reason.

### D38. Promotion gate for decaying retro lessons

- Question: should a correct retro lesson that never reaches a durable contract be
  detectable, rather than depending on the same rolling digest that let it decay?
- Current choice: DEFER the class; the single instance is fixed. The reviewer
  result-delivery rule now lives in [fresh-eye-subagent-review.md](../skills/shared/references/fresh-eye-subagent-review.md)
  `## Result Delivery`, pinned by [test_reviewer_result_delivery.py](../tests/quality_gates/test_reviewer_result_delivery.py)
  and enforced at closeout by the `Delivery state` floor in [validate_critique_artifacts.py](../scripts/validate_critique_artifacts.py).
  What is NOT addressed is the mechanism: nothing detects a retro
  "Next Improvement" that never became a contract.
- Why now: the lineage is concrete rather than hypothetical. The correct spawn
  shape was recorded in [2026-06-20-north-star-phase4-boundary-non-terminality.md](../charness-artifacts/retro/2026-06-20-north-star-phase4-boundary-non-terminality.md)
  (`:36-41`, `:89-91`), aged out of [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
  (generated from [lesson-selection-index.json](../charness-artifacts/retro/lesson-selection-index.json) under a 14-day recency
  half-life), and two later sessions re-derived a wrong attribution
  ("host-runtime behavior, not repo fixable") instead of running the cheap
  falsifier. Cost: five weeks and a blocked spec. Full lineage in
  [the debug artifact](../charness-artifacts/debug/2026-07-25-bounded-reviewer-result-delivery.md).
- Why deferral is right at the time: a promotion gate needs a contract for what
  "promoted" means and a way to tell a lesson that *should* decay from one that
  should not; guessing that taxonomy while fixing one instance is the
  validator-post-hoc-churn reflex. The decay mechanism stays live for every
  other current Next Improvement, which is the accepted residual.
- Impact surfaces: [build_retro_lesson_selection_index.py](../scripts/build_retro_lesson_selection_index.py),
  [lesson-selection-index.json](../charness-artifacts/retro/lesson-selection-index.json),
  [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md), the `retro` skill.
- Reopen trigger: a third recurrence of any lesson previously recorded in a retro
  and since decayed, or a session that re-derives a wrong attribution the repo
  already refuted.

### D39. Changed-line coverage freshness fingerprint is blind to `tests/`

- Question: Should the coverage freshness marker the pre-push changed-line gate trusts digest the test files whose presence the coverage actually depends on, or stay scoped to mutation-pool files only?
- Current choice: Defer. The marker stays pool-scoped; the risk is recorded rather than repaired inside an issue-resolution slice.
- Why now: [changed_pool_fingerprint](../scripts/mutation_changed_files_lib.py) digests only `changed_pool_files_vs_base(...)`, and the mutation pool globs in [sample_mutation_files.py](../scripts/sample_mutation_files.py) do not include `tests/`. A tests-only slice therefore moves the fingerprint by zero bits, so a `reports/mutation/test-coverage.json` produced BEFORE the new tests existed still satisfies `--require-fresh-coverage` and is accepted as fresh. Surfaced as finding C6 of [the #464 resolution critique](../charness-artifacts/critique/2026-07-28-issue-464-changed-line-coverage-recurrence.md).
- Why deferral is right at the time: for a slice that ADDS tests the failure direction is self-announcing — stale coverage shows the changed lines still uncovered, so the consumer raises a loud false FAIL, not a false pass. The dangerous direction is a slice that DELETES or renames tests while the marker still matches, which is a gate design question (what content the freshness claim is actually about) rather than a one-line widening, and widening the digest to all of `tests/` would invalidate the marker on every unrelated test edit and push authors back toward the ~10-minute producer they already skip.
- Impact surfaces: [mutation_changed_files_lib.py](../scripts/mutation_changed_files_lib.py), [check_changed_line_mutation_coverage.py](../scripts/check_changed_line_mutation_coverage.py), [run-quality.sh](../scripts/run-quality.sh) (the `--require-fresh-coverage` consumer), [mutation_coverage_producer.py](../scripts/mutation_coverage_producer.py).
- Reopen trigger: a changed-line gate verdict that passes against coverage produced before the tests it credits, or any slice that removes tests from a mutation-pool file's proof set.

### D40. No pre-landing lane BLOCKS an unproven changed line

- Question: Should a lane that runs before a landing refuse a push whose changed lines were never proven — and if so, which one pays: a mandatory ~10-minute local coverage producer, or branch protection forcing the PR path?
- Current choice: Defer. This is a cost decision for the repo owner, not an agent's call inside an issue closeout.
- Why now: the class is eight instances deep (#219 -> #251 -> #260 -> #320 -> #321 -> #335 -> #453 -> #464, named in [quality-core.yml](../.github/workflows/quality-core.yml)) and the usual explanations are already falsified. The remote push-arm mirror is NOT missing — it has been live since `69941efb` and went RED on all three pushes preceding #464's latest comment (runs 30269197950, 30314842348, 30317036462). The local advisory is NOT silent — [check_changed_line_mutation_coverage.py](../scripts/check_changed_line_mutation_coverage.py) `_surface_skip` writes a `WARNING (changed-line mutation gate):` line and [run-quality.sh](../scripts/run-quality.sh) `print_phase_output` surfaces it. What is missing is teeth: the lane that runs before a landing exits 0 by construction, and the lane with teeth runs after the push and cannot unland it.
- Why deferral is right at the time: every available repair charges a real toll — a blocking local producer costs ~10 minutes per push, branch protection ends direct-to-main work, and a push-time remote-red check adds a network dependency to every push. Adding a ninth advisory is the one option that is definitely useless, since the eighth was already read and walked past. Choosing among the tolls is the owner's, and picking one inside a tests-only issue resolution would smuggle a workflow change in under a coverage-repair banner.
- Impact surfaces: [run-quality.sh](../scripts/run-quality.sh) (the `--skip-if-no-coverage` flag set), [check_changed_line_mutation_coverage.py](../scripts/check_changed_line_mutation_coverage.py), [quality-core.yml](../.github/workflows/quality-core.yml), [mutation-tests.yml](../.github/workflows/mutation-tests.yml), repository branch-protection settings (not in tree).
- Reopen trigger: a ninth instance of the class, or an operator decision to pay one of the tolls above.

### D41. The coverage mapper cannot see a bare top-level import of a repo script

- Question: Should `tests_referencing_paths` resolve a changed script from a bare `import <stem>` / `from <stem> import ...`, or should the repo require the dotted `from scripts import <stem>` form in tests?
- Current choice: Defer the mapper change; fix the call sites. The two tests found this way now use the dotted form, and the convention is the cheaper half.
- Why now: surfaced by dogfooding the armed lane on its own slice. [test_degradation_branch_coverage.py](../tests/test_degradation_branch_coverage.py) covered `scripts/changed_line_run_trust.py:103-104` and the gate still reported those lines uncovered, because the test imported the module as a bare top-level name. [suggest_mutation_coverage_command.py](../scripts/suggest_mutation_coverage_command.py) builds its module map from `_module_name(path)` (`scripts.changed_line_run_trust`), so a bare import matches none of its patterns — not the quoted path, not the dotted module, not an import statement, not the stem-as-call-argument form. The blind spot is repo-wide: a conftest puts `scripts/` on `sys.path`, so the bare form works at runtime and several existing tests already use it.
- Why deferral is right at the time: the obvious widening (match `import <stem>` for every pool file's stem) is a mapper change on a surface that now feeds a BLOCKING gate, so it owes its own two-round review — and it over-matches in a way the existing patterns do not, since a bare stem can collide with a real top-level package name. The direction is safe (an extra test only adds measured coverage) but the cost lands on every push, and the same effect is available for free by writing the import the way the rest of the repo does.
- Impact surfaces: [suggest_mutation_coverage_command.py](../scripts/suggest_mutation_coverage_command.py), [prepush_focused_changed_line_coverage.py](../scripts/prepush_focused_changed_line_coverage.py), any test importing a `scripts/` module by bare name.
- Reopen trigger: a third changed file reported uncovered while a test demonstrably covers it, or a slice where converting the call sites is not available (a vendored or generated test).

### D42. Should a claim-time proof gate that established nothing exit 3 rather than 0?

- Question: `check_mutation_run_proof.py --claim changed-line --base-sha <sha>` with no sample manifest establishes that the run's TRIGGER could evaluate the claim, never that it evaluated any file. Should that exit 3 (`UNPROVEN`, non-blocking) instead of 0 with a stderr warning?
- Current choice: Defer the exit-code change; make the gap audible. The verdict now carries `range_established` and the hedge prints to stderr on both the range and the conclusion. **Operator-confirmed 2026-07-30**: asked directly at goal closeout with the reviewer's exit-3 argument in hand, and the answer was to keep exit 0. The deferral is now a decision the owner made, not one an agent left standing.
- Why now: a bounded round-2 review showed the earlier deferral cited [the empty-scope critique](../charness-artifacts/critique/2026-07-27-empty-scope-family.md) F9 backwards. F9's reasoning is that `conclusion_established` "is read by nothing in the repo except its own tests, so the exit code remains the whole signal" — an argument that the EXIT CODE must carry the meaning, cited as license to leave the exit code alone. The same review established that adopting exit 3 here is unusually cheap: this gate is not a `run-quality.sh` label, is absent from `UNESTABLISHED_CAPABLE_LABELS`, and no runner, workflow, or script in the repo executes it, so its only consumer is the agent citing proof.
- Why deferral is right at the time: the sibling gate's own contract records why an always-UNPROVEN verdict backfires — "marking every such run UNPROVEN would train the reader to skip the word" ([check_changed_line_mutation_coverage.py](../scripts/check_changed_line_mutation_coverage.py) exit-code docstring) — and the flag-only invocation is the documented primary one. Choosing between "scope exit 3 to the manifest-less path" and "leave exit 0 and rely on the warning" is an operator-facing contract call about a tool whose reader is a human citing proof, not a runner. Picking it inside a slice scoped to the empty-range refusal would smuggle a contract change in under a defect-repair banner.
- Impact surfaces: [check_mutation_run_proof.py](../scripts/check_mutation_run_proof.py), [mutation-testing.md](../skills/public/quality/references/mutation-testing.md), [run-quality.sh](../scripts/run-quality.sh) `UNESTABLISHED_CAPABLE_LABELS` if it ever becomes a queued label.
- Reopen trigger: a citation of a `range_established: false` or `conclusion_established: false` run as changed-line proof in any closeout, issue, or release note; or this gate becoming a queued `run-quality.sh` label.

### D43. Should the loose-bar advisory be per-label rather than one global factor?

- Question: `BUDGET_SLACK_FACTOR = 3.0` in [runtime_budget_lib.py](../skills/public/quality/scripts/runtime_budget_lib.py) is a single module constant applied to every label on every profile. Should it become per-label or per-profile so a bar that cannot fail is reported?
- Current choice: Defer. The constant stays global and the bars it cannot see are named in the adapter where they sit. **Operator-confirmed 2026-07-30**: asked directly at goal closeout, with the corrected count (one real blind spot, not three) in hand.
- Why now: the advisory divides by `max_recent_elapsed_ms`, not the median — a fact a slice in this session got backwards and had to correct — so a bar sized from a documented range cost rather than an observed worst run is structurally invisible to it. **Corrected count, after review:** the adapter reads as recording three such blind spots, but only ONE is a live bar. The `pytest` note at 90000/41826 is a stale survivor of the 2026-07-26(b) retighten (the live bar is 58500), and the aarch64 "2.0x case" describes a drafted 270000 bar that was REJECTED — on a profile with zero samples, where the advisory cannot fire at any factor. `run-quality-full: 420000` is the only real one.
- Why deferral is right at the time: the one real blind spot is a bar sized deliberately, by a recorded decision, from a documented cost — so lowering the factor to see it would fire on exactly the looseness that is intentional. Making it per-label needs a contract for who sets each label's factor and on what evidence, and guessing that taxonomy while fixing a different lane's teeth is the validator-post-hoc-churn reflex. One blind spot is a thinner basis for deferring than three, and that is recorded here rather than left as an inflated count.
- Impact surfaces: [runtime_budget_lib.py](../skills/public/quality/scripts/runtime_budget_lib.py), [quality-adapter.yaml](../.agents/quality-adapter.yaml), [check_runtime_budget.py](../skills/public/quality/scripts/check_runtime_budget.py).
- Reopen trigger: a bar that was NOT a recorded decision goes unreported by the advisory and is later found to be unfailable; OR a bar goes stale in the TIGHT direction and hard-fails with nothing regressed. The second clause exists because this session's actual discovery was tight, not loose (`run-quality-read-only` at 58500 against a post-lane latest of 90618), and the original trigger would not have caught it.

### D44. `blocking_targets` should name a blocked line's subprocess-only coverage path — DECLINED (2026-08-01)

- Question: Should the changed-line gate's `blocking_targets` payload report, per blocked line, that the file's existing tests reach it only via `subprocess`/`run_script`? Raised as a capability in the [2026-07-30 retro](../charness-artifacts/retro/2026-07-30-session-retro.md) after four consecutive identical BLOCKs, carried unapplied through the [07-31](../charness-artifacts/retro/2026-07-31-session-retro.md) and [08-01](../charness-artifacts/retro/2026-08-01-session-retro.md) retros.
- Current choice: **DECLINED as asked, because its premise was falsified and its honest residue already shipped.** Landing the literal ask would print false reassurance onto a blocking gate.
  1. **The premise is false here.** The ask assumes "reached only via subprocess" explains a BLOCK. It does not: this repo's coverage producer ([mutation_sampling_lib.py](../scripts/mutation_sampling_lib.py)) writes a `sitecustomize` calling `coverage.process_startup()` and exports `COVERAGE_PROCESS_START`, so a child that inherits the environment and runs the script at its real in-repo path **is** attributed. Measured 2026-07-30 with a purpose-built control (a first attempt was CONFOUNDED and caught by a round-2 review); the 07-30 retro's own Waste entry carries the correction, and some of the four motivating BLOCKs were TRUE blocks on genuinely unexercised branches. A payload line saying "subprocess-only" on such a block tells the reader to doubt a correct verdict.
  2. **The honest residue is already in the payload.** #465 shipped [subprocess_only_coverage_advisory.py](../scripts/subprocess_only_coverage_advisory.py), which names the two mechanisms that DO lose the measurement (`env-replaces`, `copies-this-script`), bound to the spawn call whose command names the script. It is emitted from `_blocking_report` beside `blocking_targets`, keyed on the union of `blocking_targets` and `blocking`, carries the blocked line numbers, and states its own scope so silence is a statement rather than an absence. Verified by execution 2026-08-01, on a **synthetic** `blocking_targets` input (no live gate BLOCK was available on this range): `subprocess_coverage_advisory_report` on [validate_maintainer_setup.py](../scripts/validate_maintainer_setup.py) names [test_maintainer_hooks.py](../tests/quality_gates/test_maintainer_hooks.py) via `copies-this-script` with `blocked_lines: [42]`, examining 7 candidate tests. Disclosed weakness of that demo, per the bounded review: the named test ALSO loads the module in-process at nine sites, so it is the least informative firing the advisory can produce — the `established` field says so, but the demo proves the payload is wired, not that it discriminates well.
  3. **Line granularity is not available to buy.** Neither candidate source (the boundary-bypass ratchet, the test-reference map) records which LINE a test reaches, so the per-line form the ask names cannot be established at all without a new producer.
- What DID land with this decision: the gate's `blocking_detail` string for an untracked file no longer reads "(subprocess-only or untested)" — the wording asserted exactly the cause the measurement narrowed — and now reads "(untested, or exercised only where coverage was never attributed -- see subprocess_coverage_advisory)". Text only; no verdict changes.
- **Residual this decline does NOT cover, found by the bounded review (STILL OPEN):** the ask's ORIGIN form ([2026-07-30 retro](../charness-artifacts/retro/2026-07-30-session-retro.md) Engelbart counterfactual) named a different surface and a different payload — `suggest_mutation_coverage_command.py` reporting, per blocked file, WHICH test files reference it and how they exercise it. That is **remedy** information ("add the in-process case here"), not verdict-doubt information, so ground 1 does not falsify it, ground 2 has not shipped it, and ground 3's line-granularity limit does not bite. [subprocess_only_coverage_advisory.py](../scripts/subprocess_only_coverage_advisory.py) `_advisory` already computes the candidate NAMES per blocked path and reduces them to a count (`candidate_tests_examined`); "0 lines attributed while N named tests reference this path" is exactly the discriminator the repaired `blocking_detail` disjunction leaves unresolved. Not landed here because surfacing it changes an advisory payload on a blocking gate and owes its own review rounds, which a decision slice should not smuggle. Second, narrower note for the next toucher: a path that reaches the advisory via `blocking` alone gets `blocked_lines: []` even though `_blocking_report` computed those numbers and discarded them, and the two single-key entrypoints (`subprocess_coverage_advisory`, `advisory_scope`) take no `blocking` argument, so a future caller reaching for the obvious entrypoint silently reverts to targets-only keying.
- Non-claims: declining does NOT claim every BLOCK is a genuinely untested line, and it does not upgrade the advisory. The advisory remains file-granular, non-exhaustive, and explicitly silent on a spawn whose command is a variable, an `env=` passed as a bare name, and a cross-module `copytree` — see its `silence_means`. No new measurement was taken for this decision; the 2026-07-30 control is cited, not re-run.
- Impact surfaces: [check_changed_line_mutation_coverage.py](../scripts/check_changed_line_mutation_coverage.py), [subprocess_only_coverage_advisory.py](../scripts/subprocess_only_coverage_advisory.py) and their plugin mirrors, [docs/handoff.md](./handoff.md).
- Reopen trigger: a measured case where a blocked line's only exercise is an environment-inheriting, in-repo spawn and coverage still misses it (a THIRD mechanism, not a re-argument of the two known ones); or a BLOCK the advisory stayed silent on that is later diagnosed as an unattributed-child artifact; or a test→line map that makes the per-line claim establishable; or the candidate-NAME residual above is wanted by a session that has just spent a cycle re-deriving it by hand. **Honest weakness of these triggers, named rather than left implicit:** nothing counts advisory silences, and `advisory_scope_line` prints only on a blocking exit, so every trigger here depends on a human noticing and writing it down — the same channel D38 records as the one that let a correct lesson decay. This entry is an instance of that class, not an exception to it.

### D45. Should `run-quality.sh` arm `--require-evaluated-scope` on the CI/local parity gate?

- Question: charness's own two workflows BOTH carry a `# charness:gate-policy` exemption marker, so [inventory_ci_local_gate_parity.py](../skills/public/quality/scripts/inventory_ci_local_gate_parity.py) evaluates **zero jobs** in this repo while [run-quality.sh](../scripts/run-quality.sh) asserts `--require-empty-parity-issues` and reports PASS. Should the runner also pass the new `--require-evaluated-scope`, turning that green into a refusal?
- Current choice: **Defer — the flag ships, unwired.** The S26/S30 slice made the zero-denominator legible (`workflows_not_exempt`, `jobs_evaluated`, a NOTE line, and the flag), and pinned the posture in `test_real_repo_workflows_or_zero_parity_issues` so a third workflow fires a test. It did not arm the refusal.
- Why now: found while closing sweep rows S26/S30 on 2026-08-01, verified by running the gate against this repo (`--detail`: two workflows, both `exempt: true`, `jobs: []`). This is S31's consequence rather than S31 itself — S31 is that a comment INSIDE the audited file grants the exemption, which stays open.
- Why deferral is right at the time: arming it makes this repo's broad quality lane permanently red with no honest remediation short of deleting a legitimate `scheduled-deeper-check` exemption, and the alternative repair — moving the exemption declaration out of the audited file into the adapter, which is the north-star "different channel" answer — is a contract change for every consumer repo and deserves its own slice, not a ride-along on a defect repair. Choosing which toll to pay is the same class of call as [D40](#d40-no-pre-landing-lane-blocks-an-unproven-changed-line), and it is the owner's.
- Non-claims: the NOTE line is legibility, not teeth — it is one line in an ~82-gate run, and the slice does not claim anyone will read it. Nothing here narrows S31's self-declaration defect. A second new flag, `--require-established-gate-match`, is NOT part of this deferral: round 2 established it is a no-op on this repo today (every workflow is exempt, so the bucket is empty), so it was armed at the commit boundary in [staged_commit_gate_plan.py](../scripts/staged_commit_gate_plan.py) rather than deferred. `run-quality.sh` still does not pass it, for the same reason it does not pass `--require-evaluated-scope`: the broad lane runs in consumer repos too, and a composite-action CI is an honest shape there.
- Impact surfaces: [run-quality.sh](../scripts/run-quality.sh), [inventory_ci_local_gate_parity.py](../skills/public/quality/scripts/inventory_ci_local_gate_parity.py), [ci_local_gate_parity_lib.py](../skills/public/quality/scripts/ci_local_gate_parity_lib.py), [maintainer-local-enforcement.md](../skills/public/quality/references/maintainer-local-enforcement.md), `.github/workflows/*.yml`.
- Reopen trigger: a CI/local parity escape that this repo's own green did not catch; or S31 being worked, since moving the exemption to the adapter changes what "evaluated" can mean; or a third charness workflow landing.

### D46. Should an uninterpreted adapter-YAML line REFUSE the adapter, or only warn?

- Question: [adapter_lib](../scripts/adapter_lib.py) now reports the lines its mini
  parser could not interpret, and both [the issue
  adapter](../skills/public/issue/scripts/resolve_adapter.py) and the shared
  [load_adapter_contract](../scripts/simple_skill_adapter_lib.py) surface them. They
  surface as **warnings**. Should they be errors, so `valid: false` and the skill's CLI
  exits 1?
- Current choice: **Defer — warn, do not refuse.** The report ships; the refusal does
  not. **Operator call 2026-08-01: deferral CONFIRMED, and the recorded consumer defect
  repaired.** The refusal stays unarmed for the reason below (the population it would
  judge cannot be enumerated), but the "nothing reads the warning" half of the
  non-claim is now closed: `build_issue_entries` records the issue adapter's `valid`,
  `errors`, and `warnings` in `LAST_ISSUE_ADAPTER_REPORT`, and the field is forwarded
  through all three documented pipeline stages —
  `parse_handoff_entries.py --with-issues` emits `issue_adapter_report`, and
  `propose_merges.py` and `prepare_chunk_packet.py` forward it, as they already do for
  `staleness`. It carries `errors`, not only `warnings`: the two lists are disjoint in
  that loader and the parse-failure branch returns `errors=[...]` with `warnings=[]`, so
  a `valid: false` with no reason would be worse legibility than the case being repaired.
  An adapter that was not FOUND is deliberately not reported — its two "create one"
  warnings are unconditional boilerplate in the ordinary no-adapter case. It is reporting
  only: nothing branches on `valid`, because refusing the listing would empty the issue
  backlog from pickup indistinguishably from the documented trackerless fallback.
  Pinned by eleven tests across
  [test_handoff_chunker_issue_source.py](../tests/test_handoff_chunker_issue_source.py)
  (including two that drive the REAL `resolve_adapter.load_adapter` — one over a
  colon-less `default_org` line, D46's own example) and
  [test_handoff_chunker_adapter_report.py](../tests/test_handoff_chunker_adapter_report.py)
  (CLI emission, clean-adapter omission, and survival through both downstream stages).
- Why now: found while closing sweep row S24 on 2026-08-01. The first cut of that slice
  DID arm the refusal, and the round-1 bounded review caught that it violates the goal's
  own stop condition: an adapter YAML is consumer-authored, so refusing it turns a
  consumer's entire issue lane red — [issue_tool.py](../skills/public/issue/scripts/issue_tool.py)
  and [issue_create.py](../skills/public/issue/scripts/issue_create.py) both exit 1 on
  `valid: false` — for a missing colon.
- Why deferral is right at the time: the measurement that would authorize arming does not
  and cannot exist. [measure_adapter_yaml_uninterpreted.py](../scripts/measure_adapter_yaml_uninterpreted.py)
  reports 0 uninterpreted lines over the 44 checked-in YAML files under this repo's
  top level plus `.agents/`, `skills/`, and `integrations/`
  ([recorded run](../charness-artifacts/probe/2026-08-01-adapter-yaml-uninterpreted.json)),
  but the population a refusal would judge is consumer-authored `.agents/*-adapter.yaml`,
  which this repo has never seen and cannot enumerate. A 0 here proves arming costs this
  repo nothing and proves nothing about the population that matters. Round 1 also showed
  the refusal firing on legal YAML the mini parser merely does not support — a document
  marker was refused before that was fixed, and a 4-space indent step still records
  `over-indented line` — so "malformed" and "unsupported-by-us" are not yet separable.
- Non-claims: the warning is legibility, not teeth — that half is unchanged and
  deliberate. **Superseded 2026-08-01:** "Nothing reads it today" was true when this
  entry was written and is no longer; the handoff chunker's issue-source path
  ([chunked_routing_issue_source.py](../skills/public/handoff/scripts/chunked_routing_issue_source.py))
  consumed `adapter["data"]` without checking `valid` OR `warnings`, so a typo'd
  `default_org` was never surfaced there. It is now reported. The consequence was
  always conditional, not certain: `issue_runtime.resolve_target` only reaches
  `default_org` when the target argument is empty AND the git remote yields nothing AND
  `default_repo` is unset, so in a repo with an `origin` remote the typo has no effect on
  that path — the repair makes the typo *visible*, it does not make it *matter* more.
  Still non-claims: only the handoff chunker's three-stage pipeline reads the report; the
  other nine skills sharing the contract loader were not audited, and a warning that
  reaches an agent-facing packet is legibility, not enforcement — nothing obliges the
  reading agent to act on it.
- Impact surfaces: [adapter_lib.py](../scripts/adapter_lib.py),
  [simple_skill_adapter_lib.py](../scripts/simple_skill_adapter_lib.py),
  [issue resolve_adapter.py](../skills/public/issue/scripts/resolve_adapter.py), and the
  nine skills sharing the contract loader (release, hotl, hitl, debug, retro, impl,
  gather, handoff, setup).
- Reopen trigger: a consumer repo reporting a silently-defaulted adapter field; or a rule
  that separates "attempted assignment with a missing colon" from "legal YAML this parser
  does not support", since that is what makes the refusal safe; or the mini parser gaining
  real YAML coverage.

### D47. Should inventory-field engagement require a value marker?

- Question: `_engages` in [validate_inventory_consumption.py](../scripts/validate_inventory_consumption.py)
  now requires a field mention to carry ≥5 alphanumerics beyond every declared field name.
  That closes the stub shapes, but a field whose NAME is an ordinary English word —
  `scope`, `status`, `notes`, `paths`, `ranking`, `advisory`, `command`, `families` — is
  engaged by incidental prose. Should a mention additionally require a value marker
  (`field=`, `field:`, or `` `field` ``)?
- Current choice: **Defer — measure recorded, refusal not armed.** **Operator call
  2026-08-01: still not armed, and the repair this entry named is WITHDRAWN as
  unbuildable. The hand counts are replaced by an executed measurement.**
- Why now: found by round-1 bounded review while closing sweep row S10 on 2026-08-01, and
  measured rather than argued. Those first numbers were 51 of 169 field mentions unmarked
  across the 105 checked-in quality artifacts, hand-counted; see the executed measurement
  bullet below, which supersedes them.
- Why deferral is right at the time: arming the marker refuses **5 checked-in reviews** that cite
  `inventory_nose_clones` or `inventory_doc_duplicates` (2026-06 and 2026-07, not all
  2026-06 as a first draft of this entry said), all of which were only ever passing on incidental prose. The remedy is either
  rewriting frozen artifacts to satisfy a later gate — the Goodhart move this validator's
  own docstring exists to refuse — or accepting a standing red. Choosing that toll is the
  owner's, as in [D45](#d45-should-run-qualitysh-arm---require-evaluated-scope-on-the-cilocal-parity-gate).
  The hand count put that at 5 reviews; the executed measurement below puts it at 5
  refused CITATIONS across **4** artifacts, which is the same argument at a slightly lower
  price. There is also a better repair available: qualify the generic tokens in
  [inventory-consumer-fields.json](../skills/public/quality/references/inventory-consumer-fields.json)
  so a field declares whether its name is distinctive, which is a contract change
  deserving its own slice.
- **Withdrawn, do not retry — the named better repair cannot be built as described.**
  "Qualify the generic tokens in inventory-consumer-fields.json so a field declares
  whether its name is distinctive" cannot both impose a real marker rule and spare the
  cited reviews, because the fields the corpus actually engages ARE the ordinary-English
  ones: `inventory_nose_clones.py` declares `status, advisory, family_count, families,
  excludes, ignore_file, paths, ranking, scope, notes`, and the citing reviews engage the
  ordinary ones on incidental prose. Declaring them non-distinctive refuses those
  reviews; declaring them distinctive makes the marker rule apply to no field the corpus
  ever engages — a measured-zero no-op that would read here as a repair. It is also a
  STRONGER self-declaration than the `required_release_surfaces` list [D48](#d48-should-an-absent-release-surface-be-drift-without-a-self-authored-declaration)
  objects to: it would decide whether the gate may fire on a field at all, from inside
  the audited repo. Found by the 2026-08-01 bounded plan critique before it was built.
- **Executed measurement replacing the hand counts (2026-08-01).** New script
  [measure_inventory_marker_rule.py](../scripts/measure_inventory_marker_rule.py), recorded
  at [2026-08-01-inventory-marker-rule.json](../charness-artifacts/probe/2026-08-01-inventory-marker-rule.json)
  and pinned against today's tree by
  [test_inventory_marker_rule_measurement.py](../tests/test_inventory_marker_rule_measurement.py).
  Over this entry's own denominator (105 top-level artifacts, 28 citing a declared
  inventory): the presence-only mention total reproduces **169** exactly, **161** of those
  clear today's residual floor, **114** carry a value marker and **47** do not, and a
  marker rule would refuse **5 citations across 4 artifacts**
  (`2026-06-25-skill-ergonomics-yaml-summary`, `2026-06-25-test-speed-token-efficiency`,
  `2026-06-26-five-pass-boundary`, `2026-07-13`). Marker kinds are reported per mention and
  overlap: 110 backticked, 74 `field=`, 4 `field:`. With `--recursive`, which reaches the
  `history/` directory the sibling script's non-recursive glob silently excludes: 123
  artifacts (252 presence-only), 244 floor-clearing mentions, 179 marked, 65 unmarked, 7
  citations across 5 artifacts. Both variants are recorded in the probe and pinned by the
  test, so neither number is an unrecorded assertion sitting beside recorded ones.
- **The first executed number was WRONG, and how it was wrong is the point.** The initial
  marker test used `` `[^`]*field[^`]*` ``, which matches the GAP BETWEEN two adjacent code
  spans — so a bare English mention sitting between two unrelated spans scored as marked.
  The bias ran one way: it inflated "marked" and deflated the cost, reporting 42 unmarked
  and 4 citations across 3 artifacts, which supported a tidy conclusion that the toll was
  smaller than this entry had recorded. It is not. Corrected, the refusal count lands on
  5 refused citations across 4 artifacts, up from 3 artifacts. **Units matter here and an
  earlier draft of this entry got them wrong:** the hand count's unit was REVIEWS (5);
  the script's units are CITATIONS (an artifact-inventory pair) and ARTIFACTS. On the hand
  count's own unit the executed answer is **4, not 5** — so the hand count was close and
  slightly high, not vindicated, and the earlier claim that it was "substantially right"
  rested on reading "5 reviews" as "5 citations". Caught by the round-1 bounded review
  before the number was trusted, and the unit swap by round 2. Both runs are recorded in
  the probe's `_provenance`.
- Non-claims: the floor as shipped refuses a stub, not a lie, and not incidental prose
  about an ordinary word. Nothing here narrows sweep row S11. The new measurement counts
  mentions that clear TODAY's residual floor (161), while the presence-only population is
  169 — both are reported, and the marker split is measured over the 161 only, so the 47
  is NOT directly comparable to the hand count's 51 over 169; the 8 sub-floor mentions were
  never marker-split. It does not
  model the gate's `prose_review_status` skill-ergonomics arm; that arm looks inert here
  (every corpus mention of that field is backticked or `=`-assigned) but it was not
  measured. It measures this repo's corpus and says nothing about a consumer's. The
  refused artifacts are not all ones the default runner reaches — the gate is normally
  handed `latest.md` only — so "would refuse 5 citations" is not "would redden the next
  quality run". Known and unrepaired, raised by the round-2 review and recorded because
  round 2 is the review cap: a field name inside a backticked PATH or flag
  (`advisory-interpretation-contract.md`, `--paths`) scores as marked — the same one-way
  bias as the bug that was fixed, verified inert on today's corpus but able to flip a
  refusal silently on the next artifact; lines with an odd number of backticks and fenced
  code blocks are unmodelled; and marker attribution is per LINE, not per occurrence.
  The gate's pre-contract skip is modelled but is measured-zero in both modes. Nothing was
  armed, and no frozen artifact was rewritten.
- Impact surfaces: [validate_inventory_consumption.py](../scripts/validate_inventory_consumption.py),
  [measure_inventory_consumption_floor.py](../scripts/measure_inventory_consumption_floor.py),
  [inventory-consumer-fields.json](../skills/public/quality/references/inventory-consumer-fields.json).
- Reopen trigger: a quality artifact passing the floor on incidental prose and later found
  not to have consumed the inventory; or the declaration file gaining per-field
  distinctiveness; or those five reviews being rewritten for another reason. **Both numbers
  are now output of a recorded probe command** — the hand-measurement caveat this line used
  to carry is retired; re-derive with
  [measure_inventory_marker_rule.py](../scripts/measure_inventory_marker_rule.py) against
  [the recorded probe](../charness-artifacts/probe/2026-08-01-inventory-marker-rule.json).

### D48. Should an absent release surface be drift without a self-authored declaration?

- Question: [current_release.py](../skills/public/release/scripts/current_release.py) turns
  an ABSENT generated release surface into drift only for surfaces the repo's own
  `required_release_surfaces` names, and that field defaults to empty. Should absence be
  drift by default, or derived from a channel the audited repo does not author?
- Current choice: **Defer — declared-only, default empty.** **Operator call 2026-08-01:
  drift-by-default still REFUSED; the disarm-by-deletion direction CLOSED.** The question
  as posed ("should absence be drift by default?") is answered no. But the defect this
  entry actually recorded — *deleting those four adapter lines disarms it with nothing
  corroborating them* — is closed, in two parts:
  - `current_release.py` reports `absence_corroboration` (`not-applicable` / `declared` /
    `uncorroborated`) plus `undeclared_absent_surfaces`, and
    `publish_release_preflight.release_surface_blocker` REFUSES a publish while it reads
    `uncorroborated`. `drift` is deliberately unchanged, so the read-only status call
    still reddens nobody's un-shipped lane; the teeth sit at the irreversible boundary.
  - A surface that is PRESENT but `unreadable` / `no-version` is now drift without
    `required_release_surfaces`. Those are the states a failed sync actually leaves (a
    plugin.json truncated mid-write), they never entered `absent_surfaces`, and the
    declared-only arm let them through whenever the declaration was deleted — the disarm
    fully alive in its most likely state. It IS exemptable via
    `unpublished_release_surfaces`, and the first cut of this arm was wrong to claim
    otherwise ("a repo that does not ship the lane has no file at all"). Round 2 showed
    that is false for the two MARKETPLACE surfaces, which are per-repo files rather than
    per-package: a codex marketplace file ([.agents/plugins/marketplace.json](../.agents/plugins/marketplace.json)) listing some other product parses
    fine and yields nothing for this package, i.e. `no-version`, with nothing corrupt.
    Unexempted, those consumers would have been permanently red through `drift` — which
    `plan_release_run_packets` has always routed on — with no adapter line able to clear
    it. That is the toll this entry refuses, and the first cut reintroduced it through a
    channel the planner revert had not closed.
  The remedy is a SECOND adapter field, `unpublished_release_surfaces`, not an overload
  of the first: `required_release_surfaces` means "these must exist", so naming a surface
  you do not publish there makes it drift and cannot be the remedy for not publishing it.
  The first cut of this repair got that wrong and shipped unpublishable advice — round 1
  of the bounded review proved no declaration existed that let a claude-only repo publish.
  Cost, stated rather than hidden: a consumer with a genuinely absent surface declares it
  once, in one line, before it can publish. Pinned by nine tests in
  [test_absent_input_is_not_a_matching_input.py](../tests/quality_gates/test_absent_input_is_not_a_matching_input.py).
- **Not warned earlier, and it cannot be:** `plan_release_run` runs BEFORE the sync
  command, so an absent generated surface at plan time is the ordinary fresh-checkout
  state rather than evidence — routing the planner on it refused every pre-sync plan
  (four planner tests). The gate therefore sits immediately after sync, where an absent
  surface means the sync did not write it. Accepted cost: the refusal lands after the
  version bump has already rewritten the worktree.
- **Known gap, not closed:** `publish_release_resume.py` reaches `create_release` without
  the release-surface check, so a surface deleted or corrupted between a failed attempt
  and the resume still reaches publish unchecked. Pre-existing for `drift` too. Adding
  the gate there was attempted and reverted: every resume fixture exercises a repo with
  no generated tree, so it is a contract change with its own blast radius rather than a
  line this slice was entitled to add.
- **Withdrawn, do not retry:** the "derive the expected set from the repo's own sync
  command output" repair named below is NOT buildable as described.
  `sync_root_plugin_manifests.py` reports `written_paths` carrying the plugin root as a
  *directory* (`plugins/charness`), so two of the four surfaces — `claude_plugin` and
  `codex_plugin` — never appear in it; `current_release.py`'s vocabulary is symbolic keys
  rather than paths, so a derivation would additionally need a path→key map with nowhere
  portable to live; and the listing-mode variant puts the channel behind a NEW
  self-declared adapter field, so it could not have broken the class it claimed to break.
  Found by the 2026-08-01 bounded plan critique before any of it was built.
- Why now: found while closing sweep row S35 on 2026-08-01. The repair is an instance of
  the class the sweep catalogues: a self-declared field inside the repo being judged
  decides whether the floor fires, and deleting those four adapter lines disarms it with
  nothing corroborating them. Its one defense is that the declaration lives in the adapter
  rather than in the audited file, which is the channel [D45](#d45-should-run-qualitysh-arm---require-evaluated-scope-on-the-cilocal-parity-gate)
  names as S31's correct repair.
- Why deferral is right at the time: defaulting to drift-on-absence would turn every
  consumer that publishes only some surfaces permanently red for a surface it never
  intended to publish, with no local remedy short of declaring an exemption — the same
  toll D45 refuses to pay unilaterally. The better repair derives the expected set from
  the repo's own sync command output rather than from a hand-written list, which is a
  contract change deserving its own slice.
- Non-claims: the declaration is unverified against reality; nothing checks that a
  declared surface is one the sync command actually produces. This entry does not narrow
  S31.
- Impact surfaces: [current_release.py](../skills/public/release/scripts/current_release.py),
  [release resolve_adapter.py](../skills/public/release/scripts/resolve_adapter.py),
  [adapter-contract.md](../skills/public/release/references/adapter-contract.md),
  [release-adapter.yaml](../.agents/release-adapter.yaml).
- Reopen trigger: a release published with a surface missing that the declaration did not
  cover; or the sync command gaining a machine-readable list of what it writes; or S31
  being worked, since moving a declaration out of the audited surface is the same question.

### D49. Should the `## Final Verification` figure-form floor REFUSE, or stay a captured observable?

- Question: [goal_artifact_figure_form.py](../skills/public/achieve/scripts/goal_artifact_figure_form.py)
  reads every figure stated under a goal artifact's `## Final Verification` and reports
  which cite no path/command/URL and carry no `— unbacked: <why>`. Should it refuse the
  flip to `complete`?
- Current choice: **Defer — the floor ships, unwired.** It answers the form question and
  publishes `figure_lines` as its denominator; it never touches `report["ok"]`.
- Why now: opened, withdrawn, and re-opened on 2026-08-01 across two bounded review
  rounds, and only the third measurement means anything. **The history is the point.**
  - The first cut deferred on: a `2026-08-01` rule date refuses 2 of 23 in-scope
    artifacts, both frozen same-day closeouts.
  - Round 1 refuted that and armed the floor at `2026-08-02`: **20 in scope, 0 refused.**
  - Round 2 refuted THAT: all 20 of those artifacts have no parseable `Created:` line and
    are in scope only because the grandfather predicate fails closed. **Zero dated
    artifacts were in scope.** "0 refused" was a green over an empty denominator — the
    exact class this floor exists to make visible, produced inside the floor, by the
    round that was fixing the same class elsewhere.
- Why deferral is right at the time, on the honest denominator: measured over all **127
  dated** checked-in goal artifacts, the separator-mandatory form refuses **90**. The form
  was then relaxed — a source cited anywhere on the line counts, because
  ``- `bash scripts/run-quality.sh` full: 82 passed, 1 failed`` names the exact command
  that produced the number and was being refused for lacking a punctuation mark. Relaxed,
  it still refuses **41 of 127**. A floor that would refuse a third of every closeout this
  repo has written is not describing a defect; it is describing a house style it disagrees
  with. Arming it yields mass false refusals or mass artifact edits, and a false refusal
  is the expensive direction: it teaches padding.
- Non-claims: nothing refuses an unsourced figure today. The floor checks FORM only —
  whether a cited source actually says the number is not machine-decidable and stays
  author judgment plus the fresh-eye round. The 41 refusals are NOT claimed to be 41 real
  defects; they are 41 artifacts whose prose does not match a form invented after them.
  Moving the rule date does not "green" the refused artifacts, it removes them from the
  question — which is what made round 1's arming unearned.
- Impact surfaces: [goal_artifact_figure_form.py](../skills/public/achieve/scripts/goal_artifact_figure_form.py),
  [goal_artifact_closeout_evidence.py](../skills/public/achieve/scripts/goal_artifact_closeout_evidence.py),
  [describe_goal_closeout_shape.py](../skills/public/achieve/scripts/describe_goal_closeout_shape.py),
  [goal-artifact lifecycle-after.md](../skills/public/achieve/references/lifecycle-after.md),
  [test_goal_closeout_record_floors.py](../tests/quality_gates/test_goal_closeout_record_floors.py).
- Reopen trigger: the refusal rate over DATED artifacts reaching zero — pinned by
  `test_the_corpus_measurement_the_non_arming_rests_on`, which fails both when nothing
  refuses (arm it) and when the dated denominator collapses (the measurement stopped
  meaning anything). Any future arming must state its denominator in DATED artifacts;
  a count that includes undatable ones is the defect this entry records.

## Next Action Contract

After these closures, the next major workstream is `cautilus` integration and
contract wiring, not further pre-`cautilus` product-boundary debate unless a
reopen trigger fires.
