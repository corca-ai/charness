---
name: init-repo
description: "Use when a repo needs its initial operating surface created or normalized. Bootstrap README, AGENTS.md, CLAUDE.md symlink policy, roadmap, and operator-acceptance docs from minimal ideation for greenfield repos, or realign those same surfaces for partially-initialized repos without pretending quality review or deep product ideation already happened."
---

# Init Repo

Use this when a repo needs its basic operating surface created, repaired, or
normalized.

`init-repo` is one public concept:

- detect whether the repo is greenfield or already partially initialized
- run a short ideation pass when the concept is still too thin for honest docs
- scaffold or realign the basic durable surfaces a maintainer needs
- normalize `AGENTS.md` and `CLAUDE.md` into one explicit host-facing policy
- leave deeper quality review, long-range planning, and baton-pass work to
  adjacent skills once the operating surface exists

Keep the concept narrow. `init-repo` is not the whole product-definition skill,
not the long-range planning skill, and not the repo-wide quality audit.

## Bootstrap

Resolve the adapter first, then read the smallest context that reveals the repo
state.

Resolve `SKILL_DIR` to the directory that contains this `SKILL.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

By default, `init-repo` writes any durable normalization note to
`skill-outputs/init-repo/init-repo.md`. Repos can override the directory with
`.agents/init-repo-adapter.yaml`.

If the repo is mature and only `docs/operator-acceptance.md` is missing,
synthesize a first draft from existing checks before hand-writing a template:

```bash
python3 "$SKILL_DIR/scripts/synthesize_operator_acceptance.py" --repo-root .
```

```bash
# Required Tools: rg
# Missing-binary protocol: create-skill/references/binary-preflight.md
# 1. current repo surface
python3 "$SKILL_DIR/scripts/inspect_repo.py" --repo-root .
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
- any `AGENTS.md` / `CLAUDE.md` ambiguity: `references/agent-docs-policy.md`
- scaffolding or rewriting the basic docs: `references/default-surfaces.md`

## Workflow

1. Detect the current repo mode.
   - `GREENFIELD`: little or no durable operating surface exists yet
   - `PARTIAL`: some surface exists, but key files are missing or inconsistent
     - if only one core operating surface is missing, treat this as a targeted
       missing-surface repair instead of a broad scaffold rewrite
   - `NORMALIZE`: the core files exist, but their boundaries or ownership are drifting
2. Stabilize the host-facing instruction surface first.
   - if both `AGENTS.md` and `CLAUDE.md` are missing, create `AGENTS.md` and
     make `CLAUDE.md` a symlink to it
   - if `AGENTS.md` exists and `CLAUDE.md` is missing, create the symlink
   - if `CLAUDE.md` already symlinks to `AGENTS.md`, keep it
   - if `CLAUDE.md` is a real file with meaningful content, stop and ask the
     user before promoting or merging it into `AGENTS.md`
3. Run a short ideation pass when needed.
   - if the repo has no honest concept surface yet, ask the minimum
     high-leverage questions needed to write real docs
   - capture verified facts, assumptions, open questions, and the next concrete
     direction before scaffolding
   - do not dump generic templates into a concept vacuum
4. Scaffold or realign the default operating surfaces.
   - `README.md`
   - `AGENTS.md`
   - `docs/roadmap.md`
   - `docs/operator-acceptance.md`
   - optionally `INSTALL.md` and `UNINSTALL.md` only when the repo actually
     ships an installable surface
5. Keep the boundaries honest.
   - `README.md`: current repo story and user-facing orientation
   - `AGENTS.md`: agent operating contract for this repo
   - `docs/roadmap.md`: near-term work direction and ordered priorities
   - `docs/operator-acceptance.md`: what a human maintainer must do to take over
   - do not create `docs/handoff.md` by default; use `handoff` only when the
     next session truly needs a baton-pass artifact
   - do not create `docs/master-plan.md` unless the user explicitly asks for it
6. End with a quality-style sanity pass.
   - check for missing or duplicated operating surfaces
   - check that generated guidance is not contradicting itself
   - check that the next human operator can tell what to read and what to do
   - if deeper repo-wide posture review is still needed, hand off to `quality`
     instead of inflating `init-repo`

## Output Shape

The result should usually include:

- `Repo Mode`
- `Agent Docs State`
- `Verified Facts`
- `Assumptions`
- `Scaffolded Surfaces`
- `Normalized Surfaces`
- `Open Questions`
- `Next Step`

## Guardrails

- Do not write generic boilerplate without first checking whether the repo
  already has an honest concept or operating surface.
- Do not silently merge `CLAUDE.md` into `AGENTS.md` when both contain real
  content; ask the user first.
- Do not let `init-repo` expand into deep product ideation when a short
  clarification loop is enough.
- Do not let `init-repo` become a substitute for `quality`; use `quality` when
  the user wants repo-wide gate posture, security, or broad quality review.
- Do not let `init-repo` become a substitute for `narrative` when the repo
  already has a rich truth surface that mainly needs alignment.
- Do not create `docs/master-plan.md` by default.
- Do not create `docs/handoff.md` unless the user explicitly wants a baton pass
  or the next-step coordination burden is real enough to justify `handoff`.

## References

- `references/greenfield-flow.md`
- `references/normalization-flow.md`
- `references/agent-docs-policy.md`
- `references/default-surfaces.md`
- `references/github-actions-defaults.md`
- `references/operator-acceptance-synthesis.md`
- `scripts/inspect_repo.py`
- `scripts/synthesize_operator_acceptance.py`
