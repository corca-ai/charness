# Deferred Decisions

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-02

This document is the canonical closure surface for deferred product-boundary
decisions that were previously carried in session state.

## Scope

- Decision window: pre-integration cleanup closure
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

## Named Remedy Premise Contract

A remedy recorded in a deferred decision is a hypothesis, not an implementation
plan. Before shaping work around a named remedy, the next resolver must inspect
the current owner and first reader of the channel the remedy assumes, then run
or read the smallest evidence that can establish whether that channel exists
and behaves as described. A historical sentence is not a current capability.

Record the result in the decision entry before implementation begins:

```text
Named remedy premise:
- Remedy: <the proposed repair, quoted or named>
- Premise: <the current fact the repair depends on>
- Evidence channel: <file read, command, fixture, or live readback>
- Observation: <what the current channel actually establishes>
- Downstream decision delta: <the later remedy, scope, order, or stop decision changed by this result>
- Status: verified | falsified | narrowed | withdrawn | not-run
```

`Downstream decision delta` is the acceptance boundary: if the observation
does not change or falsify a later remedy decision, the premise check has not
yet earned a slice. `not-run` is an explicit non-claim, not permission to
implement the named remedy. This is a review convention, not a new mechanical
blocking floor; the owning issue, reviewer, and closeout record decide whether
the evidence is sufficient for the boundary at hand.

## Closed Decisions (2026-04-10)

### D1. Shared Packaging Canonical Source

- Question: Which shared packaging manifest is canonical for Claude/Codex dual support?
- Current choice: [`packaging/charness.json`](../packaging/charness.json) stays the single source of truth.
- Why now: This is already how the checked-in plugin install surface and root marketplace files are generated and validated.
- Impact surfaces: [`docs/host-packaging.md`](./host-packaging.md), [`scripts/sync_root_plugin_manifests.py`](../scripts/sync_root_plugin_manifests.py), [`scripts/validate_packaging.py`](../scripts/validate_packaging.py)
- Reopen trigger: If host-specific metadata can no longer be represented as generated output from one shared manifest.

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
- Impact surfaces: [`profiles/profile.schema.json`](../profiles/profile.schema.json), [`tools/validate_profiles.py`](../tools/validate_profiles.py)
- Reopen trigger: If real profile composition demand appears in downstream consumer repos.

### D6. Integration Capability Depth

- Question: How deep should capability grants/authenticated binary/env fallback go beyond metadata?
- Current choice: Keep metadata + validation contracts (`access_modes`, `capability_requirements`, `readiness_checks`, `config_layers`) without automating secretful runtime orchestration in `charness`.
- Why now: Matches host-neutral product boundary.
- Impact surfaces: [`integrations/tools/manifest.schema.json`](../integrations/tools/manifest.schema.json), [`tools/validate_integrations.py`](../tools/validate_integrations.py), [`scripts/doctor.py`](../scripts/doctor.py)
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
- Impact surfaces: `profiles/*.json`, [`tools/validate_profiles.py`](../tools/validate_profiles.py), profile docs
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
- Current choice: Implement only deterministic, repo-owned gates in `charness`; keep evaluator/HITL-heavy checks in an explicit consumer-owned workflow.
- Why now: Keeps `charness` guarantees honest and runnable in isolation.
- Impact surfaces: [`scripts/run-quality.sh`](../scripts/run-quality.sh), [`tools/run_evals.py`](../tools/run_evals.py), [`docs/public-skill-validation.md`](./public-skill-validation.md)
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

### D19. Current-Pointer Write Scanner Generalization

- Question: Should [check_current_pointer_writes.py](../tools/check_current_pointer_writes.py) detect adapter-resolved current-pointer writes via taint analysis, or rely on per-writer helper adoption?
- Current choice: Defer scanner generalization; rely on helper-adoption convention for adapter-resolved writers. The static scanner continues to catch string-literal `latest.md` / `latest.json` writes only.
- Why now: Only one adapter-resolved sibling ([hitl sync_review_artifact.py](../skills/public/hitl/scripts/sync_review_artifact.py)) was discovered, and it was closed in commit `0364886` by migrating to `write_current_pointer_text`. Adding taint analysis on a single sample is premature; the fixture matrix and false-positive surface are larger than the leak surface.
- Impact surfaces: [tools/check_current_pointer_writes.py](../tools/check_current_pointer_writes.py), [scripts/current_pointer_writer_lib.py](../scripts/current_pointer_writer_lib.py), future skill writers that resolve their durable artifact path through an adapter dictionary.
- Reopen trigger: When a second adapter-resolved current-pointer sibling that bypasses the string-literal scanner appears, or when more than one new skill adds a `latest.md` / `latest.json` writer through adapter-resolved paths without the helper.

### D27. markdownlint-cli2 Verbose Banner Filter

- Question: Should [`check-markdown.sh`](../scripts/check-markdown.sh) keep the local `sed` `Finding:` filter forever, or replace it once markdownlint-cli2 adds a `--quiet` flag or equivalent upstream knob?
- Current choice: Defer. v0.21.0 has no quiet flag; the banner line listing every linted path is the only source of the per-commit ~50KB stdout flood that #230 Waste 2 targeted. The filter is anchored, load-bearing-space, and verified against a known-failing fixture (slice 6 critique, agentId `a28af53807ad5aef1`, F1+F3 confirmed Over-Worry).
- Why now: Local one-line fix is correct today and saves ~350x stdout bytes per commit; rewriting it under a future upstream flag would just be ceremony until the upgrade actually lands.
- Impact surfaces: [scripts/check-markdown.sh](../scripts/check-markdown.sh)
- Reopen trigger: markdownlint-cli2 ships a documented quiet/verbosity flag, OR the per-error line format changes such that legitimate errors now begin with the same prefix the filter drops (caught by slice 6 stop condition on every fixture run).

### D28. Template-First Fill Guards And Report-All For Sibling Artifact Validators — POLARITY RESOLVED, FILL GUARDS STILL DEFERRED (2026-07-27)

- Question: Should the fill-time guard comments added to the quality scaffold be generalized to the other scaffold families (debug, critique, retro, handoff, ideation), should the sibling artifact validators share ONE one-pass control instead of per-family flag polarity, and should `emit_payload_main` in [scaffold_artifact_lib.py](../scripts/core/scaffold_artifact_lib.py) grow a `--write` mode so scaffold-first becomes the path of least resistance?
- Current choice (operator-decided, A+B+C): **the one-pass half is fully resolved and the polarity split is closed.** (A) [`validate_debug_artifact.py`](../scripts/validate_debug_artifact.py) and [`validate_critique_artifacts.py`](../scripts/validate_critique_artifacts.py) default to one-pass, matching handoff/retro/ideation/quality. (B) `--fail-fast` is the only control across the family; the obsolete `--report-all` no-op has been removed. (C) The control is declared once in `add_one_pass_args`, and the four changed-path validators (critique, debug, retro, ideation) route their whole `main()` through `run_changed_artifact_validator` in [artifact_validator.py](../scripts/artifact_validator.py) — the two that previously justified a private `main()` now fit through hooks that model the real work: `extra_args` for critique's `--changed-ref` / `--changed-path` cross-surface probe, a `ChangedArtifactRun` context for its per-path `require_tier_evidence`, and `artifacts_fn` for debug's adapter-resolved output directory. The fill-guard and `--write` halves stay deferred on their original reasoning.
- Why now: **The original "report-all there is ceremony" premise was refuted by measurement, which is exactly this entry's reopen trigger.** The [lesson-recurrence retro](../charness-artifacts/retro/2026-07-26-lesson-recurrence-mechanism.md) measured ~8 validator rounds on a single handoff artifact — the one-rule-per-run report manufactured the retry loop that a separate checked-in lesson ("a counted limit is a planning input, not a retry loop") blames on the reader. Cost is not the rule count; it is that each round is a full gate run and the author re-reads the artifact each time. The flip reverses the explicit operator narrowing recorded in `a930cc5f`; that reversal is the operator's own call, made on this measurement. C is what stops the split re-forming: while each validator owned its own `main()`, matching defaults were a convention that the next artifact family could silently break.
- Impact surfaces: [scripts/artifact_validator.py](../scripts/artifact_validator.py), the debug/critique/retro/ideation/handoff/quality validators, [scripts/run-quality.sh](../scripts/run-quality.sh), [scripts/core/scaffold_artifact_lib.py](../scripts/core/scaffold_artifact_lib.py) and the five sibling scaffolds.
- Non-claims: `--fail-fast` on debug and critique stops at the first failing artifact, not only the first rule; previously those two always collected across artifacts. That is the shared runner's semantics, adopted deliberately.
- Reopen trigger: `emit_payload_main --write`; fill guards for any family that accumulates observed n-fold rework evidence; or a new artifact validator that needs a hook `run_changed_artifact_validator` cannot express, since forking `main()` again is what re-opens the polarity risk.
- Trigger checked 2026-08-01: **not fired, stays deferred.** `emit_payload_main` in [scaffold_artifact_lib.py](../scripts/core/scaffold_artifact_lib.py) still has no `--write` argument; no family has accumulated recorded n-fold rework evidence; and no new artifact validator has forked `main()`. Checked, not assumed — the remainder was carried on the handoff as un-dispositioned work for weeks without anyone reading the trigger.

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
- Impact surfaces (migrated in lockstep): [skills/public/quality/scripts/nose_fingerprint_lib.py](../skills/public/quality/scripts/nose_fingerprint_lib.py) (new), [skills/public/quality/scripts/dup_ratchet_lib.py](../skills/public/quality/scripts/dup_ratchet_lib.py), [skills/public/quality/scripts/check_dup_ratchet.py](../skills/public/quality/scripts/check_dup_ratchet.py), [skills/public/quality/scripts/nose_report_lib.py](../skills/public/quality/scripts/nose_report_lib.py), [skills/public/quality/scripts/nose_baseline_lib.py](../skills/public/quality/scripts/nose_baseline_lib.py), [skills/public/quality/scripts/inventory_nose_clones.py](../skills/public/quality/scripts/inventory_nose_clones.py), [skills/public/quality/scripts/dup_review_lib.py](../skills/public/quality/scripts/dup_review_lib.py), [skills/public/quality/references/dup-ratchet.md](../skills/public/quality/references/dup-ratchet.md), the then-checked-in gate and advisory fingerprint baselines plus review overlay, [integrations/tools/nose.json](../integrations/tools/nose.json), [charness-artifacts/debug/2026-06-21-dup-ratchet-family-id-rotation.md](../charness-artifacts/debug/2026-06-21-dup-ratchet-family-id-rotation.md). The local baseline and overlay are now intentionally absent; the generic gate remains opt-in for consumer repos and must be bootstrapped from a fresh scope.
- Residual reopen trigger (UPDATED 2026-07-08, goal `2026-07-08-retro-informed-improvement-5pack`
  Slice D): **S4-Defer-1 RESOLVED** — `nose_fingerprint_lib` algo v2 tokenizes each
  Python member span and drops comment/pure-whitespace-structure tokens, so an
  in-place comment or internal-whitespace edit no longer rotates the fingerprint (a
  span that fails to tokenize standalone falls back per-member to v1 rstrip-only);
  `FINGERPRINT_ALGO_VERSION` bumped to `"2"`. **S4-Defer-3 RESOLVED** — the gate
  baseline moved to schema v3 (`code_families`: `{fingerprint, member_hashes}`) and
  [`check_dup_ratchet.py`](../skills/public/quality/scripts/check_dup_ratchet.py) runs a `classify_reductions` pre-pass: a candidate-new
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
  [`issue_closeout_rung1_floors.py`](../skills/public/issue/scripts/issue_closeout_rung1_floors.py) (`FLOOR_EXEMPT_CLASSIFICATIONS` + a unified
  `(classification, *, numbers=None, source=None)` signature), re-exported through
  [`issue_verify_closeout.py`](../skills/public/issue/scripts/issue_verify_closeout.py), with [`issue_close_comment_floor.py`](../skills/public/issue/scripts/issue_close_comment_floor.py) reduced to a
  re-export (no duplicated body). [`check_issue_closeout_commit_msg.py`](../scripts/check_issue_closeout_commit_msg.py) surfaces the
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
- Impact surfaces (migrated in lockstep): [check_issue_closeout_commit_msg.py](../scripts/check_issue_closeout_commit_msg.py), [issue_close_comment_floor.py](../skills/public/issue/scripts/issue_close_comment_floor.py), [issue_verify_closeout_body.py](../skills/public/issue/scripts/issue_verify_closeout_body.py), [issue_verify_closeout.py](../skills/public/issue/scripts/issue_verify_closeout.py), their plugin mirrors, and tests ([test_issue_close_exemption_advisory.py](../tests/test_issue_close_exemption_advisory.py), the commit-msg in-process + hook suites). The former local duplicate-ratchet baseline was an incidental collateral surface and is no longer maintained here.
- Residual reopen trigger: a commit-message close self-classifies `question`/`decision-needed`
  and skips the behavioral/critique floors with no reviewer noticing, or the shared close
  advisory is touched for another reason. Orphan baseline fingerprints (`3d4af4`, `d38941`)
  left by the additive scoped-accept were the known D30 residual churn, not a D36
  regression; both were pruned from the gate baseline by the nose 0.18.0→0.19.0
  re-baseline that rode release v1.0.10 (commit `51dfc479`), so they no longer
  exist on disk (verified 2026-07-16).

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
  (`:36-41`, `:89-91`), aged out of the former compact lesson digest
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
  [lesson-selection-index.json](../charness-artifacts/retro/lesson-selection-index.json), the `retro` skill.
- Reopen trigger: a third recurrence of any lesson previously recorded in a retro
  and since decayed, or a session that re-derives a wrong attribution the repo
  already refuted.

### D39. Changed-line proof freshness fingerprint is blind to `tests/`

- Question: Should the coverage freshness marker the release-final changed-line gate trusts digest the test files whose presence the coverage actually depends on, or stay scoped to mutation-pool files only?
- Current choice: Defer. The marker stays pool-scoped; the risk is recorded rather than repaired inside an issue-resolution slice.
- Why now: [changed_pool_fingerprint](../scripts/mutation_changed_files_lib.py) digests only `changed_pool_files_vs_base(...)`, and the mutation pool globs in [sample_mutation_files.py](../scripts/sample_mutation_files.py) do not include `tests/`. A tests-only slice therefore moves the fingerprint by zero bits, so a `reports/mutation/test-coverage.json` produced BEFORE the new tests existed still satisfies `--require-fresh-coverage` and is accepted as fresh. Surfaced as finding C6 of [the #464 resolution critique](../charness-artifacts/critique/2026-07-28-issue-464-changed-line-coverage-recurrence.md).
- Why deferral is right at the time: for a change that ADDS tests the failure direction is self-announcing — stale coverage shows the changed lines still uncovered, so the consumer raises a loud false FAIL, not a false pass. The dangerous direction is a change that DELETES or renames tests while the marker still matches, which is a gate design question (what content the freshness claim is actually about) rather than a one-line widening, and widening the digest to all of `tests/` would invalidate the marker on every unrelated test edit and make the release-final producer pay again.
- Impact surfaces: [mutation_changed_files_lib.py](../scripts/mutation_changed_files_lib.py), [check_changed_line_mutation_coverage.py](../scripts/check_changed_line_mutation_coverage.py), [run-quality.sh](../scripts/run-quality.sh) (the `--require-fresh-coverage` consumer), [mutation_coverage_producer.py](../scripts/mutation_coverage_producer.py).
- Reopen trigger: a changed-line gate verdict that passes against coverage produced before the tests it credits, or any slice that removes tests from a mutation-pool file's proof set.

### D40. Changed-line proof has one release-final owner

**UPDATED 2026-08-28:** Charness now gives changed-line coverage and mutation
proof one owner: `run-quality.sh --release` runs the release-named producer once,
after release pytest and all other release checks, with the portable consumer
reading its result. Ordinary, default, and full lanes do not pay this cost.
The scheduled mutation capability remains available for its separate deeper
check.

- Question: Should a lane that runs before a landing refuse a push whose changed lines were never proven — and if so, which one pays: a mandatory ~10-minute local coverage producer, or branch protection forcing the PR path?
- Current choice: the release-final lane owns the blocking proof; ordinary
  implementation and the default/full lanes do not claim to have run it.
- Why now: the class is eight instances deep (#219 -> #251 -> #260 -> #320 -> #321 -> #335 -> #453 -> #464, named in [quality-core.yml](../.github/workflows/quality-core.yml)) and the usual explanations are already falsified. The remote push-arm mirror is NOT missing — it has been live since `69941efb` and went RED on all three pushes preceding #464's latest comment (runs 30269197950, 30314842348, 30317036462). The local advisory is NOT silent — [check_changed_line_mutation_coverage.py](../scripts/check_changed_line_mutation_coverage.py) `_surface_skip` writes a `WARNING (changed-line mutation gate):` line and [run-quality.sh](../scripts/run-quality.sh) `print_phase_output` surfaces it. What was missing is teeth: at the time of deferral the lane that ran before a landing exited 0 by construction, and the lane with teeth ran after the push and could not unland it. **UPDATED 2026-08-02:** that sentence is now partly falsified and the remaining gap is narrower and sharper — see the residual below.
- Why deferral is right at the time: every available repair charges a real toll — a blocking local producer costs ~10 minutes per push, branch protection ends direct-to-main work, and a push-time remote-red check adds a network dependency to every push. Adding a ninth advisory is the one option that is definitely useless, since the eighth was already read and walked past. Choosing among the tolls is the owner's, and picking one inside a tests-only issue resolution would smuggle a workflow change in under a coverage-repair banner.
- Impact surfaces: [run-quality.sh](../scripts/run-quality.sh) (the `--skip-if-no-coverage` flag set), [check_changed_line_mutation_coverage.py](../scripts/check_changed_line_mutation_coverage.py), [quality-core.yml](../.github/workflows/quality-core.yml), [mutation-tests.yml](../.github/workflows/mutation-tests.yml), repository branch-protection settings (not in tree).
- Reopen trigger: a ninth instance of the class, or an operator decision to pay one of the tolls above.
- **Residual inherited from [#469](https://github.com/corca-ai/charness/issues/469), 2026-08-02.** #469 was closed on its DISCLOSURE half only; its refusal half lands here, because this is the entry that owns "which pre-landing lane pays a toll", and #469 named D45 by mistake (D45 is the CI/local parity gate — a different gate entirely; the misattribution came from D45's own text calling its call "the same class of call as D40" and was caught by the pre-close bounded review).
  - What is now TRUE: [release_changed_line_coverage.py](../scripts/release_changed_line_coverage.py) is the release-final producer — it exits non-zero when the blocking proof is unestablished or uncovered, and `--refuse-unestablished` keeps that result blocking.
  - What is STILL open, and is #469's title: with changed pool files that map to no standing test, the consumer's clean payload carries **no `reason`**, so `_verdict_from_consumer` derives status `clean` and `--refuse-unestablished` is never reached. The gate returns PASS while its own warning says it analyzed N of M. #469's observed instance was 49 of 51, and the CI run on that same push then blocked on one of the two unanalyzed files.
  - Why it stays deferred rather than being armed: files legitimately map to no standing test, so mapping "unanalyzed non-empty" to `unestablished` could turn this repo's own pre-push lane red on ordinary work. That toll is the owner's, and it needs a before/after measurement over real pushes first — arming teeth on an unmeasured population is a mistake this repo has already made.
  - Cheapest honest first step, if reopened: measure how many of the last N pushes carried a non-empty `unanalyzed_changed_pool_files`, and state that count with its denominator, before deciding. The count pair (`changed_pool_file_counts`) shipped in `cf88b750` exists to make exactly that measurement cheap.
  - **RESOLVED IN PART, operator decision 2026-08-06 ([#488](https://github.com/corca-ai/charness/issues/488)).** The consumer retains a distinct partial/unestablished state so an incomplete population is not read as a clean pass. The release-final producer invokes it with `--refuse-unestablished`, so an unestablished result fails the release rather than being silently accepted.
  - What remains open here, unchanged: whether a pre-landing lane should ever BLOCK an unproven changed line. The 2026-08-06 decision was explicitly the non-blocking option; the operator declined both "refuse at push time" and "refuse only the partial case" with the reasoning recorded in the goal's `## Operator Decision Queue` ([2026-08-06 goal](../charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md)). The reopen trigger below still stands for that half.
  - Non-claim: this repairs the SIGNAL, not the coverage. A changed pool file that maps to no standing test is still unanalyzed before the push, and remote CI is still the thing that catches it. What changed is that the local lane no longer reports that as a pass.

### D41. The coverage mapper cannot see a bare top-level import of a repo script

- Question: Should `tests_referencing_paths` resolve a changed script from a bare `import <stem>` / `from <stem> import ...`, or should the repo require the dotted `from scripts import <stem>` form in tests?
- Current choice: Defer the mapper change; fix the call sites. The two tests found this way now use the dotted form, and the convention is the cheaper half.
- Why now: surfaced by dogfooding the armed lane on its own slice. [test_degradation_branch_coverage.py](../tests/test_degradation_branch_coverage.py) covered `scripts/changed_line_run_trust.py:103-104` and the gate still reported those lines uncovered, because the test imported the module as a bare top-level name. [suggest_mutation_coverage_command.py](../scripts/suggest_mutation_coverage_command.py) builds its module map from `_module_name(path)` (`scripts.changed_line_run_trust`), so a bare import matches none of its patterns — not the quoted path, not the dotted module, not an import statement, not the stem-as-call-argument form. The blind spot is repo-wide: a conftest puts `scripts/` on `sys.path`, so the bare form works at runtime and several existing tests already use it.
- Why deferral is right at the time: the obvious widening (match `import <stem>` for every pool file's stem) is a mapper change on a surface that now feeds a BLOCKING gate, so it owes its own two-round review — and it over-matches in a way the existing patterns do not, since a bare stem can collide with a real top-level package name. The direction is safe (an extra test only adds measured coverage) but the cost lands on every push, and the same effect is available for free by writing the import the way the rest of the repo does.
- Impact surfaces: [suggest_mutation_coverage_command.py](../scripts/suggest_mutation_coverage_command.py), [release_changed_line_coverage.py](../scripts/release_changed_line_coverage.py), any test importing a `scripts/` module by bare name.
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
- Why now: the advisory divides by `max_recent_elapsed_ms`, not the median — a fact a slice in this session got backwards and had to correct — so a bar sized from a documented range cost rather than an observed worst run is structurally invisible to it. **Corrected count, after review:** the adapter reads as recording three such blind spots, but only ONE was the live `pytest`/aggregate bar described by the earlier note. The `pytest` bar was refreshed under #503 on 2026-08-05 from the current 20-sample cohort (latest 60356ms, median 61816ms, max 69353ms) to 97500ms, so it is no longer the stale 58500ms case. The aarch64 "2.0x case" describes a drafted 270000 bar that was REJECTED — on a profile with zero samples, where the advisory cannot fire at any factor. The current local summary's remaining slack finding is the deliberate `run-quality-read-only: 420000` aggregate bar; `quality` owns its runtime record and #505 owns the matched-cost remeasurement/decision rather than silently inheriting it into the `pytest` retune.
- Why deferral is right at the time: the one real blind spot is a bar sized deliberately, by a recorded decision, from a documented cost — so lowering the factor to see it would fire on exactly the looseness that is intentional. Making it per-label needs a contract for who sets each label's factor and on what evidence, and guessing that taxonomy while fixing a different lane's teeth is the validator-post-hoc-churn reflex. One blind spot is a thinner basis for deferring than three, and that is recorded here rather than left as an inflated count.
- Impact surfaces: [runtime_budget_lib.py](../skills/public/quality/scripts/runtime_budget_lib.py), [quality-adapter.yaml](../.agents/quality-adapter.yaml), [check_runtime_budget.py](../skills/public/quality/scripts/check_runtime_budget.py).
- Reopen trigger: a bar that was NOT a recorded decision goes unreported by the advisory and is later found to be unfailable; OR a bar goes stale in the TIGHT direction and hard-fails with nothing regressed. The second clause exists because this session's actual discovery was tight, not loose (`run-quality-read-only` at 58500 against a post-lane latest of 90618), and the original trigger would not have caught it.

### D44. `blocking_targets` should name a blocked line's subprocess-only coverage path — DECLINED (2026-08-01)

- Question: Should the changed-line gate's `blocking_targets` payload report, per blocked line, that the file's existing tests reach it only via `subprocess`/`run_script`? Raised as a capability in the [2026-07-30 retro](../charness-artifacts/retro/2026-07-30-session-retro.md) after four consecutive identical BLOCKs, carried unapplied through the [07-31](../charness-artifacts/retro/2026-07-31-session-retro.md) and [08-01](../charness-artifacts/retro/2026-08-01-session-retro.md) retros.
- Current choice: **DECLINED as asked, because its premise was falsified and its honest residue already shipped.** Landing the literal ask would print false reassurance onto a blocking gate.
  1. **The premise is false here.** The ask assumes "reached only via subprocess" explains a BLOCK. It does not: this repo's coverage producer ([mutation_sampling_lib.py](../scripts/mutation_sampling_lib.py)) writes a `sitecustomize` calling `coverage.process_startup()` and exports `COVERAGE_PROCESS_START`, so a child that inherits the environment and runs the script at its real in-repo path **is** attributed. Measured 2026-07-30 with a purpose-built control (a first attempt was CONFOUNDED and caught by a round-2 review); the 07-30 retro's own Waste entry carries the correction, and some of the four motivating BLOCKs were TRUE blocks on genuinely unexercised branches. A payload line saying "subprocess-only" on such a block tells the reader to doubt a correct verdict.
  2. **The honest residue is already in the payload.** #465 shipped [subprocess_only_coverage_advisory.py](../scripts/subprocess_only_coverage_advisory.py), which names the two mechanisms that DO lose the measurement (`env-replaces`, `copies-this-script`), bound to the spawn call whose command names the script. It is emitted from `_blocking_report` beside `blocking_targets`, keyed on the union of `blocking_targets` and `blocking`, carries the blocked line numbers, and states its own scope so silence is a statement rather than an absence. Verified by execution 2026-08-01, on a **synthetic** `blocking_targets` input (no live gate BLOCK was available on this range): `subprocess_coverage_advisory_report` on [validate_maintainer_setup.py](../scripts/validate_maintainer_setup.py) names [test_maintainer_hooks.py](../tests/quality_gates/test_maintainer_hooks.py) via `copies-this-script` with `blocked_lines: [42]`, examining 7 candidate tests. Disclosed weakness of that demo, per the bounded review: the named test ALSO loads the module in-process at nine sites, so it is the least informative firing the advisory can produce — the `established` field says so, but the demo proves the payload is wired, not that it discriminates well.
  3. **Line granularity is not available to buy.** Neither candidate source (the live boundary inventory, the test-reference map) records which LINE a test reaches, so the per-line form the ask names cannot be established at all without a new producer.
- What DID land with this decision: the gate's `blocking_detail` string for an untracked file no longer reads "(subprocess-only or untested)" — the wording asserted exactly the cause the measurement narrowed — and now reads "(untested, or exercised only where coverage was never attributed -- see subprocess_coverage_advisory)". Text only; no verdict changes.
- **Residual this decline does NOT cover, found by the bounded review (STILL OPEN):** the ask's ORIGIN form ([2026-07-30 retro](../charness-artifacts/retro/2026-07-30-session-retro.md) Engelbart counterfactual) named a different surface and a different payload — [`suggest_mutation_coverage_command.py`](../scripts/suggest_mutation_coverage_command.py) reporting, per blocked file, WHICH test files reference it and how they exercise it. That is **remedy** information ("add the in-process case here"), not verdict-doubt information, so ground 1 does not falsify it, ground 2 has not shipped it, and ground 3's line-granularity limit does not bite. [subprocess_only_coverage_advisory.py](../scripts/subprocess_only_coverage_advisory.py) `_advisory` already computes the candidate NAMES per blocked path and reduces them to a count (`candidate_tests_examined`); "0 lines attributed while N named tests reference this path" is exactly the discriminator the repaired `blocking_detail` disjunction leaves unresolved. Not landed here because surfacing it changes an advisory payload on a blocking gate and owes its own review rounds, which a decision slice should not smuggle. Second, narrower note for the next toucher: a path that reaches the advisory via `blocking` alone gets `blocked_lines: []` even though `_blocking_report` computed those numbers and discarded them, and the two single-key entrypoints (`subprocess_coverage_advisory`, `advisory_scope`) take no `blocking` argument, so a future caller reaching for the obvious entrypoint silently reverts to targets-only keying.
- Non-claims: declining does NOT claim every BLOCK is a genuinely untested line, and it does not upgrade the advisory. The advisory remains file-granular, non-exhaustive, and explicitly silent on a spawn whose command is a variable, an `env=` passed as a bare name, and a cross-module `copytree` — see its `silence_means`. No new measurement was taken for this decision; the 2026-07-30 control is cited, not re-run.
- Impact surfaces: [check_changed_line_mutation_coverage.py](../scripts/check_changed_line_mutation_coverage.py), [subprocess_only_coverage_advisory.py](../scripts/subprocess_only_coverage_advisory.py) and their plugin mirrors.
- Reopen trigger: a measured case where a blocked line's only exercise is an environment-inheriting, in-repo spawn and coverage still misses it (a THIRD mechanism, not a re-argument of the two known ones); or a BLOCK the advisory stayed silent on that is later diagnosed as an unattributed-child artifact; or a test→line map that makes the per-line claim establishable; or the candidate-NAME residual above is wanted by a session that has just spent a cycle re-deriving it by hand. **Honest weakness of these triggers, named rather than left implicit:** nothing counts advisory silences, and `advisory_scope_line` prints only on a blocking exit, so every trigger here depends on a human noticing and writing it down — the same channel D38 records as the one that let a correct lesson decay. This entry is an instance of that class, not an exception to it.

### D45. Should `run-quality.sh` arm `--require-evaluated-scope` on the CI/local parity gate?

- Question: charness's own two workflows BOTH carry a `# charness:gate-policy` exemption marker, so [inventory_ci_local_gate_parity.py](../skills/public/quality/scripts/inventory_ci_local_gate_parity.py) evaluates **zero jobs** in this repo while [run-quality.sh](../scripts/run-quality.sh) asserts `--require-empty-parity-issues` and reports PASS. Should the runner also pass the new `--require-evaluated-scope`, turning that green into a refusal?
- Current choice: **Defer — the flag ships, unwired.** The S26/S30 slice made the zero-denominator legible (`workflows_not_exempt`, `jobs_evaluated`, a NOTE line, and the flag), and pinned the posture in `test_real_repo_workflows_or_zero_parity_issues` so a third workflow fires a test. It did not arm the refusal.
- Why now: found while closing sweep rows S26/S30 on 2026-08-01, verified by running the gate against this repo (`--detail`: two workflows, both `exempt: true`, `jobs: []`). This is S31's consequence rather than S31 itself — S31 is that a comment INSIDE the audited file grants the exemption, which stays open.
- Why deferral is right at the time: arming it makes this repo's broad quality lane permanently red with no honest remediation short of deleting a legitimate `scheduled-deeper-check` exemption, and the alternative repair — moving the exemption declaration out of the audited file into the adapter, which is the north-star "different channel" answer — is a contract change for every consumer repo and deserves its own slice, not a ride-along on a defect repair. Choosing which toll to pay is the same class of call as [D40](#d40-changed-line-proof-has-one-release-final-owner), and it is the owner's.
- Non-claims: the NOTE line is legibility, not teeth — it is one line in an ~82-gate run, and the slice does not claim anyone will read it. Nothing here narrows S31's self-declaration defect. A second new flag, `--require-established-gate-match`, is NOT part of this deferral: round 2 established it is a no-op on this repo today (every workflow is exempt, so the bucket is empty), so it was armed at the commit boundary in [staged_commit_gate_plan.py](../scripts/staged_commit_gate_plan.py) rather than deferred. `run-quality.sh` still does not pass it, for the same reason it does not pass `--require-evaluated-scope`: the broad lane runs in consumer repos too, and a composite-action CI is an honest shape there.
- Impact surfaces: [run-quality.sh](../scripts/run-quality.sh), [inventory_ci_local_gate_parity.py](../skills/public/quality/scripts/inventory_ci_local_gate_parity.py), [ci_local_gate_parity_lib.py](../skills/public/quality/scripts/ci_local_gate_parity_lib.py), [maintainer-local-enforcement.md](../skills/public/quality/references/maintainer-local-enforcement.md), `.github/workflows/*.yml`.
- **Named remedy's premise, ANSWERED 2026-08-01 (by reading, before any S31 work).** This
  entry calls the alternative repair "moving the exemption declaration out of the audited
  file into the adapter", which reads as a rewire. It is not. Verified in
  [ci_local_gate_parity_lib.py](../skills/public/quality/scripts/ci_local_gate_parity_lib.py):
  `read_gate_policy(raw_text, workflow_label)` takes **only the workflow's own text**, and
  `evaluate_workflow(path, workflow, gate_patterns, ci_only_marker)` receives no adapter,
  no external exemption source, and no seam for one. **There is no adapter-declared
  exemption channel to move the declaration INTO.** The remedy requires BUILDING that seam
  — a new parameter threaded through `evaluate_workflow`, a declared-exemption source, and
  a precedence rule between the two channels for consumer repos that use neither. Two facts
  keep it buildable rather than speculative: the quality adapter is a real resolvable
  surface that ALREADY carries `ci_workflow_glob`, a key for this very gate, and it already
  hosts an exemption-list pattern for a different gate (`exemption_list_path`). The shape is
  precedented; the wiring is absent. This does not change the deferral — it corrects what
  the deferred work COSTS, which is the thing a future session would have mis-scoped.
- Named remedy premise:
  - Remedy: move the exemption declaration from the workflow into the adapter.
  - Premise: an adapter-declared exemption channel already exists for this reader.
  - Evidence channel: read [`ci_local_gate_parity_lib.py`](../skills/public/quality/scripts/ci_local_gate_parity_lib.py) and the quality adapter contract.
  - Observation: the reader accepts workflow text only; the adapter has related fields but no exemption input.
  - Downstream decision delta: keep the deferral, but reshape the remedy from a rewire into a new adapter seam with precedence rules.
  - Status: falsified
- Reopen trigger: a CI/local parity escape that this repo's own green did not catch; or S31 being worked, since moving the exemption to the adapter changes what "evaluated" can mean; or a third charness workflow landing.

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
  The dated 2026-08-12 snapshot below records the executed refusal toll; the 2026-08-01
  measurement recorded 5 citations across 4 artifacts. There is also a better repair available: qualify the generic tokens in
  [inventory-consumer-fields.json](../skills/public/quality/references/inventory-consumer-fields.json)
  so a field declares whether its name is distinctive, which is a contract change
  deserving its own slice.
- **Withdrawn, do not retry — the named better repair cannot be built as described.**
  "Qualify the generic tokens in inventory-consumer-fields.json so a field declares
  whether its name is distinctive" cannot both impose a real marker rule and spare the
  cited reviews, because the fields the corpus actually engages ARE the ordinary-English
  ones: [`inventory_nose_clones.py`](../skills/public/quality/scripts/inventory_nose_clones.py) declares these fields: `status`, `advisory`,
  `family_count`, `families`, `excludes`, `ignore_file`, `paths`, `ranking`, `scope`,
  and `notes`. The citing reviews engage the ordinary ones on incidental prose.
  Declaring them non-distinctive refuses those
  reviews; declaring them distinctive makes the marker rule apply to no field the corpus
  ever engages — a measured-zero no-op that would read here as a repair. It is also a
  STRONGER self-declaration than the `required_release_surfaces` list [D48](#d48-should-an-absent-release-surface-be-drift-without-a-self-authored-declaration)
  objects to: it would decide whether the gate may fire on a field at all, from inside
  the audited repo. Found by the 2026-08-01 bounded plan critique before it was built.
- Named remedy premise:
  - Remedy: qualify generic inventory tokens with a distinctiveness field in [`inventory-consumer-fields.json`](../skills/public/quality/references/inventory-consumer-fields.json).
  - Premise: the declaration can distinguish the fields whose incidental prose caused the false engagement.
  - Evidence channel: read the inventory declaration and the cited consumer citations (5 across 4 artifacts when this remedy was assessed on the 2026-08-01 corpus; the dated snapshot below is the later evidence).
  - Observation: every cited engagement uses ordinary-English field names; declaring them non-distinctive spares the reviews, while declaring them distinctive makes the rule a measured-zero no-op.
  - Downstream decision delta: withdraw this remedy, keep the marker refusal unarmed, and require a different contract if the issue is reopened.
  - Status: withdrawn
- **Immutable executed measurement (captured 2026-08-12).** The headline figures are
  dated: **196** presence-only field mentions; **188** clear the then-current residual
  floor; **153** carry a value marker; and **35** do not. The complete shallow and
  recursive payloads — scan scope, denominator, marker kinds, and refused
  citations/artifacts — are the immutable
  [2026-08-12 snapshot](../charness-artifacts/probe/2026-08-12-inventory-marker-rule-snapshot.json)
  (`sha256: ac63f8a54a558217cebde320f02d4915d10e6bab538c3df22ff6e1397083f62d`).
  [test_inventory_marker_rule_measurement.py](../tests/test_inventory_marker_rule_measurement.py)
  verifies that hash and the payload's source invariants, not equality with the
  later corpus. Therefore unrelated quality-corpus growth does not rewrite D47 or
  regenerate its evidence.
- **Historical live-pin maintenance (superseded 2026-08-12).** The 2026-08-07 and
  2026-08-09 refreshes recorded how the old mutable probe turned ordinary corpus
  writes into a standing tax. That diagnosis is preserved in the old probe's
  provenance; [#596](https://github.com/corca-ai/charness/issues/596) replaces the
  mutable equality pin with the dated snapshot above. Nothing about D47's unarmed
  policy choice changes.
- **The first executed number was WRONG, and how it was wrong is the point.** The initial
  marker test used `` `[^`]*field[^`]*` ``, which matches the GAP BETWEEN two adjacent code
  spans — so a bare English mention sitting between two unrelated spans scored as marked.
  The bias ran one way: it inflated "marked" and deflated the cost, reporting 42 unmarked
  and 4 citations across 3 artifacts, which supported a tidy conclusion that the toll was
  smaller than this entry had recorded. It is not. Corrected, the refusal count landed on
  5 refused citations across 4 artifacts on the 2026-08-01 corpus, up from 3 artifacts.
  (Every figure in this bullet describes that 2026-08-01 run; later captured evidence is
  the immutable 2026-08-12 snapshot above.) **Units matter here and an
  earlier draft of this entry got them wrong:** the hand count's unit was REVIEWS (5);
  the script's units are CITATIONS (an artifact-inventory pair) and ARTIFACTS. On the hand
  count's own unit the executed answer is **4, not 5** — so the hand count was close and
  slightly high, not vindicated, and the earlier claim that it was "substantially right"
  rested on reading "5 reviews" as "5 citations". Caught by the round-1 bounded review
  before the number was trusted, and the unit swap by round 2. Both runs are recorded in
  the probe's `_provenance`.
- Non-claims: the floor as shipped refuses a stub, not a lie, and not incidental prose
  about an ordinary word. Nothing here narrows sweep row S11. The dated snapshot measures
  only mentions that cleared its capture-time residual floor; its marker split is not
  directly comparable to the hand count's 51 over 169. It does not
  model the gate's `prose_review_status` skill-ergonomics arm; that arm looks inert here
  (every corpus mention of that field is backticked or `=`-assigned) but it was not
  measured. It measures this repo's corpus and says nothing about a consumer's. The
  refused artifacts are not all ones the default runner reaches — the gate is normally
  handed `latest.md` only — so "would refuse 4 citations" is not "would redden the next
  quality run". Known and unrepaired, raised by the round-2 review and recorded because
  round 2 is the review cap: a field name inside a backticked PATH or flag
  ([`advisory-interpretation-contract.md`](../skills/shared/references/advisory-interpretation-contract.md), `--paths`) scores as marked — the same one-way
  bias as the bug that was fixed, verified inert in the 2026-08-12 snapshot but able to flip a
  refusal silently on a later artifact; lines with an odd number of backticks and fenced
  code blocks are unmodelled; and marker attribution is per LINE, not per occurrence.
  The gate's pre-contract skip is modelled but is measured-zero in both modes. Nothing was
  armed, and no frozen artifact was rewritten.
- Impact surfaces: [validate_inventory_consumption.py](../scripts/validate_inventory_consumption.py),
  [measure_inventory_consumption_floor.py](../scripts/measure_inventory_consumption_floor.py),
  [inventory-consumer-fields.json](../skills/public/quality/references/inventory-consumer-fields.json).
- Reopen trigger: a quality artifact passing the floor on incidental prose and later found
  not to have consumed the inventory; or the declaration file gaining per-field
  distinctiveness; or the currently-refused artifacts being rewritten for another reason.
  **The dated snapshot is output of the recorded probe command** — the hand-measurement
  caveat this line used to carry is retired. A new decision must run
  [measure_inventory_marker_rule.py](../scripts/measure_inventory_marker_rule.py) on its
  then-current corpus and record a new dated snapshot with its own SHA-256; it must not
  overwrite or recompute this immutable snapshot.

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
  - [`current_release.py`](../skills/public/release/scripts/current_release.py) reports `absence_corroboration` (`not-applicable` / `declared` /
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
- **Known gap, not closed:** [`publish_release_resume.py`](../skills/public/release/scripts/publish_release_resume.py) reaches `create_release` without
  the release-surface check, so a surface deleted or corrupted between a failed attempt
  and the resume still reaches publish unchecked. Pre-existing for `drift` too. Adding
  the gate there was attempted and reverted: every resume fixture exercises a repo with
  no generated tree, so it is a contract change with its own blast radius rather than a
  line this slice was entitled to add.
- **Withdrawn, do not retry:** the "derive the expected set from the repo's own sync
  command output" repair named below is NOT buildable as described.
  [`sync_root_plugin_manifests.py`](../scripts/sync_root_plugin_manifests.py) reports `written_paths` carrying the plugin root as a
  *directory* (`plugins/charness`), so two of the four surfaces — `claude_plugin` and
  `codex_plugin` — never appear in it; [`current_release.py`](../skills/public/release/scripts/current_release.py)'s vocabulary is symbolic keys
  rather than paths, so a derivation would additionally need a path→key map with nowhere
  portable to live; and the listing-mode variant puts the channel behind a NEW
  self-declared adapter field, so it could not have broken the class it claimed to break.
  Found by the 2026-08-01 bounded plan critique before any of it was built.
- Named remedy premise:
  - Remedy: derive the expected release-surface set from sync command output.
  - Premise: the sync output names every generated surface in the vocabulary consumed by [`current_release.py`](../skills/public/release/scripts/current_release.py).
  - Evidence channel: read [`sync_root_plugin_manifests.py`](../scripts/sync_root_plugin_manifests.py) output fields and [`current_release.py`](../skills/public/release/scripts/current_release.py) surface vocabulary.
  - Observation: sync reports the plugin root as a directory, omits two surfaces, and uses no path-to-key mapping for the release vocabulary.
  - Downstream decision delta: withdraw the derivation repair; retain declared-only status with explicit uncorroborated publish refusal.
  - Status: withdrawn
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

## Next Action Contract

### D50. Should `<plugin-dir>/` get a real user, or a bootstrap variable, or neither? — RESOLVED (2026-08-04)

- Question: `<plugin-dir>/` is a recognised portable placeholder in
  [check_doc_links.py](../scripts/check_doc_links.py), and it has **zero usage** —
  it appears only in the placeholder list in
  [authoring-preflight.md](./authoring-preflight.md), never in a skill.
  #478 considered it for seven sites and rejected it. Should it be adopted, upgraded,
  or removed?
- Current choice: **Defer — and the honest reason is that nobody has shown what it
  buys.** The operator asked directly on 2026-08-02 and the agent could not name a
  clear benefit, which is itself the finding.
- What it WOULD buy, stated so a later session does not re-derive it: it is the only
  spelling that means "the installed plugin's own tree", which is where exported
  scripts actually live for a consumer. Without it, a charness script a consumer
  COULD run has no correct spelling — `<repo-root>/` means their tree (wrong),
  `<authoring-repo>/` means ours (correct but unusable), and
  `$SKILL_DIR/../../shared/<name>` works only via a per-script shim. So its value is
  exactly: **avoid writing one shim per script.**
- Why that is not yet worth it: three shims exist
  ([authoring_script_shim.py](../skills/shared/scripts/authoring_script_shim.py) plus
  its two consumers), and the shared module made the third nearly free. The
  break-even is somewhere above that, and nobody has hit it.
- **The sharper reading, and the reason adopting it as-is would be a mistake.**
  `$SKILL_DIR` is a RESOLVED bootstrap variable an agent can expand;
  `<plugin-dir>/` is a doc placeholder with nothing behind it, so a reader must
  work out the plugin directory themselves. That is the worst of both — the
  ambiguity of a placeholder without the resolution of a variable. If this is
  ever worth doing, the thing to add is a `$PLUGIN_DIR` bootstrap variable
  alongside `$SKILL_DIR`, and `<plugin-dir>/` becomes its documentation rather
  than a substitute for it.
- Reopen trigger: the shim count passing roughly five, OR
  [#479](https://github.com/corca-ai/charness/issues/479)'s
  `<repo-root>/skills/public/...` family needing a spelling — those references
  need the installed LAYOUT, not just a different prefix, and that is the case
  `<plugin-dir>/` was invented for.
- Non-claim (as recorded at deferral): nobody has tested whether any host
  substitutes `<plugin-dir>/`. It is assumed to be agent-resolved, and that
  assumption is unverified.
- **RESOLUTION (2026-08-04): adopted, for the reopen trigger this entry named.**
  The trigger fired exactly as written — [#479](https://github.com/corca-ai/charness/issues/479)'s
  `<repo-root>/skills/public/...` family needed the installed LAYOUT, not a
  different prefix. Three of those sites were worked around with prose in the same
  goal, which was the third avoidance and the signal that the deferral had started
  costing more than the decision.
- **What changed the answer: a measurement this entry did not have.**
  `$SKILL_DIR/../..` lands on a DIFFERENT directory in each tree and only two
  entries exist at both positions — `shared/` and `support/`. So
  `$SKILL_DIR/../../shared/...` is correct in both trees by the same exporter
  cancellation that makes a packaged `parents[3]` correct in both, and for
  ANYTHING else under that root there is no both-trees relative spelling at all.
  That is the gap `<plugin-dir>/` fills, and it is narrower and more concrete than
  "avoid writing one shim per script".
- **The sharper objection is answered by resolution, not by a variable.** This
  entry's strongest argument was "the ambiguity of a placeholder without the
  resolution of a variable". `<authoring-repo>/scripts/native_gate_lib.py ... plugin-refs`
  now resolves every `<plugin-dir>/...` reference against the generated
  `plugins/<pkg>/` package and refuses a dangling one — including the
  kind-flattened `skills/public/...` spelling that is the #479 defect. That is a
  property `<repo-root>/` can never have, since it means the READER's tree and is
  unverifiable from here by construction, which is what let the class accumulate.
  A `$PLUGIN_DIR` export is documented in the shared bootstrap reference for the
  shell case; the checker is what makes the doc placeholder honest.
- **Live probe, and its bounds.** Two `claude -p` runs against a temp tree holding
  only the installed-layout package: a fresh agent resolved
  `<plugin-dir>/skills/hitl/scripts/check_chunk_contract.py` to the correct
  concrete path and confirmed it exists, and the negative control correctly
  refused the `skills/public/...` spelling and diagnosed the stale kind segment.
  Notably the agent did not need the documented procedure — it inferred the
  plugin root from the tree shape. Bounds: one host (Claude Code 2.1.220), one
  model, two prompts, whole tree visible. **No host was observed to substitute
  `<plugin-dir>/` textually; the placeholder remains agent-resolved**, and that
  original non-claim stands.

After these closures, the next major workstream is reducing the remaining
consumer friction in the active command and documentation surfaces. Removed
provider-specific integrations are not current execution authority.

### D51. Release branch/CI barrier and quality-gate runtime

- Question: How should the release helper preserve the branch-push → different
  observer CI barrier before tag/public publication, while making the measured
  quality-gate runtime actionable without weakening proof floors?
- Current choice: Defer the helper state-machine repair and runtime treatment
  as one explicit follow-up. The v3.2.0 closeout used a manually split
  branch-push, remote CI readback, tag/publication, and independent public
  readback sequence. The local release quality gate measured 168.19 seconds
  and the pre-push gate measured 162.8 seconds; those are quality debt signals,
  not permission to remove or narrow proof.
- Why now: The release helper's natural ordering would otherwise allow tag
  publication before the remote branch's CI result, and the recurring runtime
  signal needs an owner that can optimize structure rather than ask operators
  to accept a terminal green.
- Impact surfaces: [publish_release_execute.py](../skills/public/release/scripts/publish_release_execute.py),
  [run-quality.sh](../scripts/run-quality.sh), [design-north-star.md](./design-north-star.md),
  and release closeout artifacts.
- Reopen trigger: the next release-helper change, or a measured quality-gate
  runtime regression that supplies a concrete optimization candidate.

### D54. Should a per-gate runtime budget measure the gate's own work rather than contended wall clock?

- Question: A budget grades the recorded wall-clock of a queued command
  ([record_quality_runtime.py](../scripts/record_quality_runtime.py) stores
  `elapsed_ms`; the verdict reads `median_recent_elapsed_ms`). Since the 2026-07-26
  barrier removal the runner executes gates concurrently, so that number is contended
  wall time, not isolated gate time. `check-seed-fixture-budget` does ~0.06s of work and
  carries a 1795ms bar on the 36-CPU profile — roughly 19x, of which ~1.1s is python
  startup plus scheduling contention against the other ~90 gates. Should the sample
  measure the gate's own work instead?
- Current choice: **Keep wall-clock samples as telemetry, but do not block local push or
  release on a timing violation.** [`check_runtime_budget.py`](../skills/public/quality/scripts/check_runtime_budget.py) remains blocking by
  default for an explicit owner invocation; `run-quality.sh` passes `--advisory` so a
  recent-median overrun stays visible without rejecting an otherwise correct change.
  Adapter, profile, and label-universe configuration errors remain blocking.
- Why now: the #668 measurements showed that the value being graded is dominated by
  `run-quality.sh` contention, not by the standing test set. A 12% reduction in test
  CPU bought 0.6% of in-gate wall time, and the same tree changed from passing to
  failing with unrelated processes on the host. Speed is an operability signal; it is
  not a correctness claim that should prevent delivery.
- Non-claims: the mismatch is **not** fixed. The bar still grades fan-out, and no CPU
  time or contention-normalized metric was introduced. The 4-core and aarch64 profile
  values were not re-derived. Advisory timing output is not evidence that a release or
  hosted run is healthy.
- Impact surfaces: [quality-adapter.yaml](../.agents/quality-adapter.yaml) (four
  `runtime_budgets` blocks), [record_quality_runtime.py](../scripts/record_quality_runtime.py),
  [runtime_budget_lib.py](../skills/public/quality/scripts/runtime_budget_lib.py),
  and [run-quality.sh](../scripts/run-quality.sh)'s concurrent queue.
- Reopen trigger: a real correctness or safety decision becomes dependent on latency;
  a machine-independent timing metric becomes available; or an owner explicitly
  chooses to introduce a separately scoped performance SLO.
