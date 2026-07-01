---
name: setup
description: "Use when a repo needs its initial operating surface created or normalized. Bootstrap README, AGENTS.md, CLAUDE.md symlink policy, roadmap, and operator-acceptance docs from minimal ideation for greenfield repos, or realign those same surfaces for partially-initialized repos without pretending quality review or deep product ideation already happened."
---

# Setup

Use this when a repo needs its basic operating surface created, repaired, or
normalized.

`setup` is one public concept:

- detect whether the repo is greenfield or already partially initialized
- run a short ideation pass when the concept is still too thin for honest docs
- scaffold or realign the basic durable surfaces a maintainer needs
- normalize `<repo-root>/AGENTS.md` and `CLAUDE.md` into one explicit host-facing policy
- leave deeper quality review, long-range planning, and baton-pass work to
  adjacent skills once the operating surface exists

Keep the concept narrow. `setup` is not the whole product-definition skill, not the long-range planning skill, and not the repo-wide quality audit.

## Bootstrap

Resolve the adapter first, then read the smallest context that reveals the repo
state.

Before any host-capability question, honor the repo's
`<repo-root>/AGENTS.md` `Subagent Delegation` clause: required bounded review is already
delegated.

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

By default, `setup` writes any durable normalization note to
`<repo-root>/charness-artifacts/setup/latest.md`. Repos can override the directory with
`<repo-root>/.agents/setup-adapter.yaml`.

If the repo is mature and only `<repo-root>/docs/operator-acceptance.md` is missing,
synthesize a first draft from existing checks before hand-writing a template:

```bash
python3 "$SKILL_DIR/scripts/synthesize_operator_acceptance.py" --repo-root .
```

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
# 1. current repo surface
python3 "$SKILL_DIR/scripts/inspect_repo.py" --repo-root .
python3 "$SKILL_DIR/scripts/render_skill_routing.py" --repo-root . --json
python3 "$SKILL_DIR/scripts/normalize_host_docs.py" --repo-root .
git status --short
rg --files . | sed -n '1,200p'

# 2. adjacent durable docs when they exist
sed -n '1,220p' README.md 2>/dev/null || true
sed -n '1,220p' AGENTS.md 2>/dev/null || true
sed -n '1,220p' docs/roadmap.md 2>/dev/null || true
sed -n '1,220p' docs/operator-acceptance.md 2>/dev/null || true
sed -n '1,220p' docs/handoff.md 2>/dev/null || true
```

Then load only the references needed for the detected state:

- greenfield or under-shaped repo: `references/greenfield-flow.md`
- partially initialized repo: `references/normalization-flow.md`
- any `<repo-root>/AGENTS.md` / `CLAUDE.md` ambiguity: `references/agent-docs-policy.md`
- scaffolding or rewriting the basic docs: `references/default-surfaces.md`
- installable CLI / plugin / agent-facing local surface: `references/probe-surface.md`
- repo wants durable retrospective pickup: `references/retro-memory-seam.md`
- optional adapter, policy, or runtime seams: `references/bootstrap-seams.md`

## Workflow

1. Detect the current repo mode.
   - `GREENFIELD`: little or no durable operating surface exists yet
   - `PARTIAL`: some surface exists, but key files are missing or inconsistent
     - if only one core operating surface is missing, treat this as a targeted
       missing-surface repair instead of a broad scaffold rewrite
   - `NORMALIZE`: the core files exist, but their boundaries or ownership are drifting
   - if a mature repo uses equivalent local names, prefer
     `<repo-root>/.agents/setup-adapter.yaml` `surfaces` overrides over asking the repo
     to rename docs only to satisfy the inspector
   - if the run is read-only, classify artifact refresh, commit closeout, and bounded reviewers as unproven
2. Stabilize the host-facing instruction surface first.
   - for a narrow "host docs only" or "AGENTS.md only" request, run
     `normalize_host_docs.py --repo-root .` as the dry-run plan, then rerun with
     `--execute` only after that narrow host-docs path is the intended mutation
     so the deterministic AGENTS/CLAUDE cases stay intact instead of
     hand-writing only one file
   - if both `<repo-root>/AGENTS.md` and `CLAUDE.md` are missing, create `<repo-root>/AGENTS.md` and
     make `CLAUDE.md` a symlink to it
   - if `<repo-root>/AGENTS.md` exists and `CLAUDE.md` is missing, create the symlink
   - if `CLAUDE.md` already symlinks to `<repo-root>/AGENTS.md`, keep it
   - if `CLAUDE.md` is a real file with meaningful content, stop and ask the
     user before promoting or merging it into `<repo-root>/AGENTS.md`
3. Run a short ideation pass when needed.
   - if the repo has no honest concept surface yet, ask the minimum
     high-leverage questions needed to write real docs
   - name the maintainer or operator capability the operating surface must enable
   - capture verified facts, assumptions, open questions, and the next concrete
     direction before scaffolding
   - do not dump generic templates into a concept vacuum
4. Scaffold or realign the default operating surfaces.
   - `<repo-root>/README.md`
   - `<repo-root>/AGENTS.md`
   - `<repo-root>/docs/roadmap.md`
   - `<repo-root>/docs/operator-acceptance.md`
   - optionally separate bootstrap and uninstall docs only when the repo
     actually ships an installable surface
   - when optional Charness seams are requested or detected, use
     `references/bootstrap-seams.md` for probe surfaces, retro memory, artifact
     policy, review delegation that is already delegated by repo contract,
     skill routing, worktree, T-events, and usage episodes; keep runtime
     ownership with the owning skill or integration
   - preserve runtime ownership in the owning skill or integration when setup
     only seeds an adapter or starter artifact
5. Keep the boundaries honest.
   - `<repo-root>/README.md`: current repo story and user-facing orientation
   - `<repo-root>/AGENTS.md`: agent operating contract for this repo
   - `<repo-root>/docs/roadmap.md`: near-term work direction and ordered priorities
   - `<repo-root>/docs/operator-acceptance.md`: what a human maintainer must do to take over
   - optional bootstrap docs: install/update/probe semantics for repos with an install contract
   - do not create `<repo-root>/docs/handoff.md` by default; use `handoff` only when the
     next session truly needs a baton-pass artifact
6. End with a quality-style sanity pass.
   - check for missing or duplicated operating surfaces
   - check that generated guidance is not contradicting itself
   - check that the next human operator can tell what to read and what to do
   - for nontrivial source trees, recommend a dead-file advisory detector
     (`vulture` for Python, `knip` for JavaScript/TypeScript)
   - for task-completing normalization, spawn `high-leverage` bounded reviewers
     for host policy, adapter fit, operator takeover, and any broad new gate surface
   - apply host-exposed `reviewer_tiers.high-leverage` fields and use
     `../../shared/references/fresh-eye-subagent-review.md` before reporting blocked
   - use deterministic inspection as reviewer evidence and emit queued
     `recommendations[]` separately from `normalization.findings`
   - if deeper repo-wide posture review is still needed, hand off to `quality`
     instead of inflating `setup`
7. Close with the canonical normalization vocabulary.
   - emit `Repo mode: <mode>`, then a per-surface status line for each operating
     surface using the `## Closeout Vocabulary` tokens (what was realigned versus
     left already-aligned), and end with an explicit `Normalization non-claims:` line
   - never report a bare "normalized"/"done": the per-surface CHANGED-versus-LEFT
     accounting plus honest non-claims are the closeout's substance

## Closeout Vocabulary

Emittable-verbatim closeout tokens (validator substring-matches these); WHY-prose
stays in `references/normalization-flow.md`.

- `Repo mode` is one of `GREENFIELD` / `NORMALIZE` / `PARTIAL` / `read-only <reason>`.
- Per operating surface (README / AGENTS / roadmap / operator-acceptance, plus any
  optional surface actually touched), the closeout status is one of
  `realigned <drift>` / `already-aligned` / `scaffolded` / `suppressed <reason>` /
  `unverified <reason>`.
- End with `Normalization non-claims:` naming what was NOT proven (pre-existing
  failures, deferred advisories, unpushed state), or `Normalization non-claims: none`.

## Guardrails

- Do not write generic boilerplate without first checking whether the repo
  already has an honest concept or operating surface.
- Stay narrow: setup creates and normalizes the operating surface only — it does
  not do product-definition (`ideation`), repo-wide quality posture (`quality`),
  or truth-surface narrative alignment (`narrative`); route those out. (The
  merge-`CLAUDE.md`-ask and don't-create-`handoff.md` rules live in Workflow
  steps 2 and 5.)
- Do not invent a full evaluator regime for repos that do not actually keep
  repo-owned skills; skill-proof policy belongs only where the repo really
  maintains skills as a first-class surface.
- Do not leave repo-mandated bounded fresh-eye or critique review as an implicit
  convention. If the repo relies on that stop gate, make the delegation rule
  explicit in `<repo-root>/AGENTS.md`.

## References

- `references/greenfield-flow.md`
- `references/normalization-flow.md`
- `references/agent-docs-policy.md`
- `references/default-surfaces.md`
- `references/probe-surface.md`
- `references/retro-memory-seam.md`
- `references/bootstrap-seams.md`
- `references/github-actions-defaults.md`
- `references/operator-acceptance-synthesis.md`
- `../../shared/references/agent-assessment-invariant.md`
