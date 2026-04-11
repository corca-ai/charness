# Deferred Decisions

This document is the canonical closure surface for the deferred product-boundary
items that were previously listed in `docs/handoff.md` `Discuss`.

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
- Current choice: `packaging/charness.json` stays the single source of truth.
- Why now: This is already how the checked-in plugin install surface and root marketplace files are generated and validated.
- Impact surfaces: `docs/host-packaging.md`, `scripts/sync_root_plugin_manifests.py`, `scripts/validate-packaging.py`
- Reopen trigger: If host-specific metadata can no longer be represented as generated output from one shared manifest.

### D2. Evaluator Engine ID

- Question: Keep a legacy evaluator alias or standardize on one active product id?
- Current choice: Standardize on `cautilus` as the active product id for extraction-facing work, with no legacy naming compatibility.
- Why now: Current handoff and adapter flow already use `cautilus`, and keeping legacy naming would only preserve ambiguity.
- Impact surfaces: `docs/handoff.md`, `.agents/cautilus-adapter.yaml`, future integration manifest naming
- Reopen trigger: If upstream evaluator branding or repository identity changes.

### D3. Packaging Version Ownership

- Question: Should shared packaging manifest carry release version directly or rely on export-time override?
- Current choice: Shared manifest remains canonical for default version; export-time override is allowed for host-specific release workflows.
- Why now: Preserves reproducibility while keeping release operations flexible.
- Impact surfaces: `packaging/charness.json`, `scripts/export-plugin.py`, `docs/host-packaging.md`
- Reopen trigger: If release tooling requires immutable manifest-only versioning with no override path.

### D4. Generated Export Tree Storage

- Question: Store generated Claude/Codex export trees as fixtures or keep script+temp smoke canonical?
- Current choice: Keep script-driven temporary materialization canonical; do not commit generated export trees.
- Why now: Avoids drift and duplicate source-of-truth risk.
- Impact surfaces: `scripts/export-plugin.py`, `scripts/sync_root_plugin_manifests.py`, packaging docs
- Reopen trigger: If a downstream installer requires committed generated trees as contract artifacts.

### D5. `profile.extends` Depth

- Question: Promote `extends` into merged-bundle runtime behavior now?
- Current choice: Keep `extends` as constrained metadata seam; no broad merged-bundle runtime expansion in this phase.
- Why now: Avoids broad behavior complexity before evaluator integration.
- Impact surfaces: `profiles/profile.schema.json`, `scripts/validate-profiles.py`
- Reopen trigger: If real profile composition demand appears in downstream consumer repos.

### D6. Integration Capability Depth

- Question: How deep should capability grants/authenticated binary/env fallback go beyond metadata?
- Current choice: Keep metadata + validation contracts (`access_modes`, `capability_requirements`, `readiness_checks`, `config_layers`) without automating secretful runtime orchestration in `charness`.
- Why now: Matches host-neutral product boundary.
- Impact surfaces: `integrations/tools/manifest.schema.json`, `scripts/validate-integrations.py`, `scripts/doctor.py`
- Reopen trigger: If multiple consumers need standardized executable orchestration beyond current manifest metadata.

### D7. `official` Terminology in Discovery Policy

- Question: Replace `official` with broader wording (`trusted`/`declared`) now?
- Current choice: Replace `official` with `trusted` now.
- Why now: The actual policy boundary is host trust, not brand-official status.
- Impact surfaces: `docs/support-skill-policy.md`, `skills/public/find-skills/*`
- Reopen trigger: If the trust policy later needs a more precise distinction than one `trusted` bucket.

### D8. Profile Inheritance Policy

- Question: Allow richer inheritance vs flattened bundles?
- Current choice: Favor flattened effective bundles for execution, with minimal inheritance metadata retained for authoring convenience only.
- Why now: Predictable runtime behavior beats expressive inheritance at this stage.
- Impact surfaces: `profiles/*.json`, `scripts/validate-profiles.py`, profile docs
- Reopen trigger: If flattening causes repeated maintenance burden across real consumer profiles.

### D9. Preset Contract Format

- Question: Move presets to JSON schema now or keep markdown-first catalog?
- Current choice: Keep markdown-first preset contract with required frontmatter until first downstream organization preset matures.
- Why now: Current preset surface is maintainer-oriented and stable with markdown validation.
- Impact surfaces: `presets/*.md`, `scripts/validate-presets.py`
- Reopen trigger: If org-install preset scale needs stronger machine-only schema guarantees.

### D10. `ideation` Core Boundary

- Question: How much entity/stage thinking belongs in public core vs references?
- Current choice: Keep lightweight entity/stage framing in public core; push detailed playbooks, examples, and edge handling into references.
- Why now: Preserves a short trigger contract and portable defaults while relying on reference discoverability and agent reference-following.
- Impact surfaces: `skills/public/ideation/SKILL.md`, `skills/public/ideation/references/*`
- Reopen trigger: If repeated user confusion shows core guidance is too thin.

### D11. `spec` Weight Control

- Question: How to keep `spec` strong without procedural bloat?
- Current choice: Keep heuristic core (`Fixed Decisions` / `Probe Questions` / `Deferred Decisions`) and keep procedural detail, examples, and edge handling in references.
- Why now: Aligns with option-minimalism and current public authoring discipline while relying on reference discoverability and agent reference-following.
- Impact surfaces: `skills/public/spec/SKILL.md`, `skills/public/spec/references/*`
- Reopen trigger: If implementation handoff quality repeatedly fails due to underspecified core guidance.

### D12. `quality` Skill Identity

- Question: Is `quality` a proposal skill, gate skill, or both?
- Current choice: `quality` remains a strong public proposal/review skill; deterministic enforcement stays in repo-owned quality gates/scripts.
- Why now: Preserves separation between operator guidance and CI/runtime enforcement without weakening the proposal surface into soft advice.
- Impact surfaces: `skills/public/quality/SKILL.md`, `scripts/run-quality.sh`, quality docs
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
- Impact surfaces: `scripts/run-quality.sh`, `scripts/run-evals.py`, `docs/public-skill-validation.md`
- Reopen trigger: If current repo-owned gates prove insufficient for regression containment.

### D15. `spec` Mode Strategy

- Question: Keep explicit mode menu or heuristic branch?
- Current choice: Stay with heuristic branch strategy; explicit mode menu remains retired.
- Why now: This direction is already implemented and reduces authoring overhead.
- Impact surfaces: `skills/public/spec/SKILL.md`, `skills/public/spec/references/contract-modes.md`
- Reopen trigger: If operators repeatedly request explicit mode selection for predictability.

### D16. `announcement` Delivery Kinds

- Question: How much delivery taxonomy belongs in `announcement` public core?
- Current choice: `announcement` is human-to-human communication. Public core covers draft shape, audience, and explicit human-facing delivery confirmation; actual delivery backends stay adapter-defined, and `command` is not a public core kind.
- Why now: `command` describes an implementation seam, not a communication concept.
- Impact surfaces: `skills/public/announcement/SKILL.md`, announcement references/examples
- Reopen trigger: If multiple consumers need the same additional human-facing delivery concept beyond draft style plus adapter-defined backend.

### D17. `hitl` Runtime State Depth

- Question: Keep portable minimum runtime state vs add richer queue/context tooling now?
- Current choice: Keep portable minimum runtime state model in public core for agent-to-human bounded review; consider richer queue and context tooling as future support-layer work.
- Why now: Keeps the public contract lean and host-neutral instead of turning `hitl` into a host-specific review product.
- Impact surfaces: `skills/public/hitl/SKILL.md`, support-layer roadmap
- Reopen trigger: If current state model cannot sustain real review-loop throughput.

## Next Action Contract

After these closures, the next major workstream is `cautilus` integration and
contract wiring, not further pre-`cautilus` product-boundary debate unless a
reopen trigger fires.
