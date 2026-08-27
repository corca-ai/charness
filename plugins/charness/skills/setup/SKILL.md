---
name: setup
description: "Use when a repo needs its initial operating surface created or normalized. Bootstrap the README, AGENTS.md, CLAUDE.md symlink policy, and documentation index from minimal ideation for greenfield repos, conditionally add roadmap or operator-acceptance docs when evidence warrants them, or realign those surfaces for partially-initialized repos without pretending quality review or deep product ideation already happened."
---

# Setup

Use this when a repository needs its basic operating surface created, repaired, or
normalized. `setup` owns the minimum durable path an agent or maintainer needs:
README, `AGENTS.md`, `CLAUDE.md` compatibility, the documentation index, probe
surfaces, and evidence-triggered optional surfaces. It is not product definition, long-range
planning, or a repo-wide quality audit.

## Bootstrap

Resolve the adapter and inspect only the current repo surface:

```bash
# Required Tools: rg
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/inspect_repo.py" --repo-root .
python3 "$SKILL_DIR/scripts/render_skill_routing.py" --repo-root . --detail
python3 "$SKILL_DIR/scripts/normalize_host_docs.py" --repo-root .
git status --short
rg --files .
```

The tool declaration follows the lazy binary-preflight contract in
`../../shared/references/binary-preflight.md`.

By default, setup records its plan under
`<repo-root>/charness-artifacts/setup/latest.md`; a repo may override that location in
`<repo-root>/.agents/setup-adapter.yaml`. `<repo-root>/docs/operator-acceptance.md` is conditional: create
it only when a real install, deployment, or takeover path exists.

Read `AGENTS.md`, `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path -->, and only the owner page needed for the current
surface. There is no required session-start hook, handoff artifact, or second
progress channel: active Goal Runs resume from the exact `/goal #<parent>`
objective and provider cursor, and ordinary work follows installed skill metadata
through the normal progressive-disclosure path.

## References

Load references only when their trigger is present:

- `references/greenfield-flow.md` — greenfield or under-shaped repo
- `references/normalization-flow.md` — partial or drifting docs
- `references/agent-docs-policy.md` — AGENTS/CLAUDE ambiguity
- `references/default-surfaces.md` — basic docs and flat wiki
- `references/craken-like-profile.md` — alternative flat-wiki profile
- `references/github-actions-defaults.md` — GitHub Actions defaults
- `references/operator-acceptance-synthesis.md` — conditional operator acceptance
- `references/probe-surface.md` — installable CLI/plugin surface
- `references/retro-memory-seam.md` — durable retrospective memory
- `references/bootstrap-seams.md` — optional adapters, artifacts, or worktree seams
- `references/hook-failure-visibility.md` — hook output visibility

## Workflow

1. Classify the repo as `GREENFIELD`, `PARTIAL`, or `NORMALIZE` from README,
   AGENTS/CLAUDE, `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path -->. Treat roadmap and operator acceptance as
   conditional, not missing core surfaces.
2. Preserve existing authored instructions. For a narrow host-doc request, use
   `normalize_host_docs.py`; it creates a new `AGENTS.md` and a `CLAUDE.md ->
   AGENTS.md` symlink, or reports a real-file merge decision. It does not rewrite
   an existing `AGENTS.md`.
3. Build the smallest plan that closes the observed surface gap. `quality` owns
   exact quality gates, ratchets, and hook scope; setup may consume its read-only
   snapshot but must not invent a parallel quality regime.
4. Require explicit approval before writing, moving, installing, registering a
   hook, or changing a ratchet. Re-read the plan identity immediately before an
   approved mutation.
5. Apply only the approved surface changes. Prefer consolidation and deletion of
   duplicate or stale docs over adding another parallel page. Keep host behavior
   in adapters and presets.
6. Verify with the narrowest relevant checks: docs/link checks for docs changes,
   focused probes for an installable surface, and quality's core lane when a
   broader sanity check is useful. Stronger review belongs to the owning skill and
   is conditional on risk; it is not a universal setup stop gate.
7. Close with per-surface accounting (`realigned`, `already-aligned`,
   `scaffolded`, `suppressed`, or `unverified`) and explicit non-claims. Commit
   meaningful changes after verification; do not push, release, tag, or install
   without an explicit request.

## Guardrails

- Do not dump generic templates into a concept vacuum.
- Do not overwrite or silently merge a meaningful user-authored `CLAUDE.md`.
- Do not call an adapter configured or a plan approved a green quality result.
- Do not add a new policy, gate, reviewer, or artifact when an existing owner can
  answer the question with a focused check.
- Source-of-truth docs live under `<authoring-repo>/skills/public/`; plugin files are generated
  exports. Export once after source changes and validate the host layout.

## Closeout vocabulary

Emit `Repo mode: <mode>`, one status per touched operating surface, and end with
`Normalization non-claims:` naming unproven failures, deferred advisories, or
unpublished state. `Normalization non-claims: none` is valid only when those
claims were actually checked.
