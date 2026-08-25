---
name: setup
description: "Use when a repo needs its initial operating surface created or normalized. Bootstrap the README, AGENTS.md, CLAUDE.md symlink policy, and documentation index from minimal ideation for greenfield repos, conditionally add roadmap or operator-acceptance docs when evidence warrants them, or realign those surfaces for partially-initialized repos without pretending quality review or deep product ideation already happened."
---

# Setup

Use this when a repo needs its basic operating surface created, repaired, or
normalized.

`setup` is one public concept:

- detect whether the repo is greenfield or already partially initialized
- run a short ideation pass when the concept is still too thin for honest docs
- scaffold or realign the basic durable surfaces and probe surfaces a maintainer needs
- normalize `<repo-root>/AGENTS.md` and `CLAUDE.md` into one explicit host-facing policy
- leave deeper quality review, long-range planning, and baton-pass work to
  adjacent skills once the operating surface exists

Keep the concept narrow. `setup` is not product definition, long-range planning, or the repo-wide quality audit.

## Bootstrap

Resolve the adapter first, then read the smallest context that reveals the repo
state.

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

Before any host-capability question, resolve who authorized this repo's bounded
review. `setup` frequently runs in a repo that has no `AGENTS.md` yet, so the
`Subagent Delegation` clause alone cannot answer — walk the ladder in
`../../shared/references/fresh-eye-subagent-review.md` (*Where The Delegation
Request Comes From*): `AGENTS.md`, else the structured record, else ask once and
persist. Resolve it, do not assume it:

```bash
python3 "$SKILL_DIR/../../shared/scripts/resolve_subagent_delegation.py" resolve --repo-root .
```

By default, `setup` writes `<repo-root>/charness-artifacts/setup/latest.md`; repos can override this in `<repo-root>/.agents/setup-adapter.yaml`.

Only synthesize `<repo-root>/docs/operator-acceptance.md` for a real install, deployment, or takeover path; use `synthesize_operator_acceptance.py` from quality-backed checks and never make it a default file.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
# 1. current repo surface
python3 "$SKILL_DIR/scripts/inspect_repo.py" --repo-root .
python3 "$SKILL_DIR/scripts/render_skill_routing.py" --repo-root . --detail
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
- Craken-like flat wiki/profile proposal: `references/craken-like-profile.md`
- installable CLI / plugin / agent-facing local surface: `references/probe-surface.md`
- repo wants durable retrospective pickup: `references/retro-memory-seam.md`
- optional adapter, policy, or runtime seams: `references/bootstrap-seams.md`
- detected Lefthook configuration or hook-failure visibility request:
  `references/hook-failure-visibility.md`; read `inspect_repo.py`'s
  `hook_failure_visibility`; resolve `action-required`, then intentionally fail the hook because `live-verification-required` is not a pass

## Workflow

1. Detect the current repo mode.
   - classify `repo_mode` from the flat-wiki core (README, AGENTS/CLAUDE, and
     docs/index); inspect `conditional_surfaces` for roadmap and
     operator-acceptance without treating their absence as a defect
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
     `--execute` only after that narrow host-docs path is the intended
     mutation; its `actions`/`blocked` output owns every deterministic
     AGENTS/CLAUDE create-or-keep-symlink case, so do not hand-write those
     cases in prose
   - if `CLAUDE.md` is a real file with meaningful content, stop and ask the
     user before promoting or merging it into `<repo-root>/AGENTS.md`
3. Run a short ideation pass when needed.
   - if the repo has no honest concept surface yet, ask the minimum
     high-leverage questions needed to write real docs
   - name the maintainer or operator capability the operating surface must enable
   - capture verified facts, assumptions, open questions, and the next concrete
     direction before scaffolding
   - do not dump generic templates into a concept vacuum
4. Build a plan before any write, install, move, hook registration, or ratchet change.
   - use the `flat-wiki` profile and show README, AGENTS/CLAUDE, current docs inventory,
     the repository documentation index, flat-doc policy, awiki, detected language/code
     shape, nested-doc conflicts, and other plan inputs
   - run quality's read-only bootstrap and plan; quality owns the adapter, exact
     gates, and ratchets, while setup only carries the approved plan into docs
   - show hook policy: prefer Lefthook when no manager exists; preserve and
     integrate Git-native hooks, Husky, simple-git-hooks, or existing Lefthook
   - require staged/related-file scope for fast hooks; whole-repo scans belong to
     pre-push/CI or an explicit approval, and `lint-staged` is only a fallback
5. Ask the user to approve the named plan and its `approval_plan.identity`. Immediately
   re-run inspection with `--expect-plan-identity <digest>` before applying; stop if
   approval is absent or the plan changes. Never treat a green command, detected
   binary, or inferred language as approval.
6. Apply only approved changes, preserving runtime ownership for optional Charness seams; validate through `quality` and report its configured/unconfigured state separately from gate pass/fail.
7. Keep the boundaries honest.
   - `<repo-root>/README.md`: current repo story and user-facing orientation
   - `<repo-root>/AGENTS.md`: agent operating contract for this repo
   - the repository documentation index: one entry point for the flat documentation wiki
   - `<repo-root>/docs/roadmap.md`: only when active ordered planning is evidenced or requested
   - `<repo-root>/docs/operator-acceptance.md`: only when a real operator takeover path exists
   - optional bootstrap docs: install/update/probe semantics for repos with an install contract
   - do not create `<repo-root>/docs/handoff.md` by default; use `handoff` only when the
     next session truly needs a baton-pass artifact
   - treat `docs/` as evergreen, code-like current-state notes: each page owns one
     question, names its source of truth, and is classified as current, conditional,
     or generated; move dated history and stale proposals to `charness-artifacts/`
8. End with a quality-style sanity pass.
   - check for missing or duplicated operating surfaces
   - check that generated guidance is not contradicting itself
   - check that the next human operator can tell what to read and what to do
   - for nontrivial source trees, recommend a dead-file advisory detector (`vulture` for Python, `knip` for JavaScript/TypeScript)
   - for task-completing normalization, spawn the repo-delegated (`already delegated`)
     `high-leverage` bounded reviewers; read
     `../../shared/references/fresh-eye-subagent-review.md` before spawning, apply
     host-exposed `reviewer_tiers.high-leverage` fields
   - use deterministic inspection as reviewer evidence; keep queued
     `recommendations[]` separate from `normalization.findings`
   - if deeper repo-wide posture review is still needed, hand off to `quality`
     instead of inflating `setup`
9. Close with the canonical normalization vocabulary.
   - emit `Repo mode: <mode>`, then a per-surface status line for each operating
     surface using the `## Closeout Vocabulary` tokens (what was realigned versus
     left already-aligned), and end with an explicit `Normalization non-claims:` line
   - never report a bare \"normalized\"/\"done\": per-surface CHANGED-versus-LEFT accounting plus honest non-claims are the closeout's substance

## Closeout Vocabulary

Emittable-verbatim closeout tokens (validator substring-matches these); WHY-prose
stays in `references/normalization-flow.md`.

- `Repo mode` is one of `GREENFIELD` / `NORMALIZE` / `PARTIAL` / `read-only <reason>`.
- Per operating surface (README / AGENTS / docs/index / roadmap / operator-acceptance, plus any
  optional surface actually touched), the closeout status is one of
  `realigned <drift>` / `already-aligned` / `scaffolded` / `suppressed <reason>` /
  `unverified <reason>`.
- End with `Normalization non-claims:` naming what was NOT proven (pre-existing
  failures, deferred advisories, unpushed state), or `Normalization non-claims: none`.

## Guardrails

- Do not write generic boilerplate without first checking whether the repo
  already has an honest concept or operating surface.
- Do not write or install anything before explicit approval of the rendered plan.
- Stay narrow: setup creates and normalizes the operating surface only — it does
  not do product-definition (`ideation`) or truth-surface narrative alignment
  (`narrative`); route those out. Quality owns quality posture and verdicts. (The
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
- `references/craken-like-profile.md`
- `references/probe-surface.md`
- `references/retro-memory-seam.md`
- `references/bootstrap-seams.md`
- `references/hook-failure-visibility.md`
- `references/github-actions-defaults.md`
- `references/operator-acceptance-synthesis.md`
- `../../shared/references/agent-assessment-invariant.md`
