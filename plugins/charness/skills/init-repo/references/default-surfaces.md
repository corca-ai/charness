# Default Surfaces

`init-repo` uses these as the default operating surfaces.

Existing repos may already keep equivalent surfaces under local names. Declare
those names in `.agents/init-repo-adapter.yaml` instead of renaming mature repo
docs only to satisfy the inspector:

```yaml
surfaces:
  roadmap: docs/master-plan.md
  install: install.md
  uninstall: null
```

The inspector matches default paths case-insensitively. A `null` surface value
means the repo deliberately does not carry that surface and should not be
reported as missing.

## README

The repo root [README.md](../../../../README.md) should answer:

- what the repo is
- who it is for
- what the current scope is
- where the next planning and operator docs live
- when the repo ships an installable surface, where the canonical install and
  probe-surface guidance lives

## AGENTS

The repo root [AGENTS.md](../../../../AGENTS.md) should answer:

- how an agent should operate in this repo
- language or collaboration expectations
- core repo memory surfaces
- when retro memory is enabled, include `charness-artifacts/retro/recent-lessons.md`
  in those memory surfaces
- validation and commit discipline when the repo has them
- a compact `Skill Routing` block for installed charness skills, using
  concrete request shapes such as Slack thread, named support helper,
  unexpected behavior, or quality gate review rather than abstract capability
  labels
- selection rules in the core file, with deeper rationale pushed into linked
  docs instead of turning `AGENTS.md` into a second handbook
- avoid blanket external-link ignore defaults; if the repo later adopts
  `lychee`, prefer optional or tightly scoped checks before adding broad ignore
  rules

Use `scripts/render_skill_routing.py` to render the block. On a mature repo
whose `AGENTS.md` lacks it, propose adding the block instead of rewriting the
whole instruction file.

## Roadmap

The repo roadmap document, usually `docs/roadmap.md`, should answer:

- current priorities
- ordering of the next work items
- near-term exit criteria
- what is intentionally deferred

Prefer short-horizon execution direction over a grand long-range thesis.

## Operator Acceptance

The operator takeover document, usually
[docs/operator-acceptance.md](../../../../docs/operator-acceptance.md), should answer:

- what a human operator should read first
- what commands to run first
- what takeover or acceptance tasks remain
- what counts as done for each item

When the repo already has real functional checks, synthesize operator
acceptance from them instead of inventing a disconnected checklist:

- split machine-runnable checks from human judgment or external-system checks
- separate cheap local commands from expensive or account-dependent runs
- name environment prerequisites explicitly when a command needs credentials,
  services, seeded data, or another repo state
- prefer one honest "run this first" sequence over a long unordered dump

## Optional Install Docs

Only scaffold `INSTALL.md` and `UNINSTALL.md` when the repo really exposes an
installable surface such as a plugin, package, or operator-facing setup path.

When `INSTALL.md` exists for that reason, it should also keep a small explicit
probe surface honest:

- install or update path
- binary healthcheck
- machine-readable discovery if it exists
- repo or install readiness
- local discoverability or materialization step when agents or plugins depend
  on it

## Optional Retro Memory Seam

Only scaffold retro memory when the repo actually wants durable retrospective
pickup between sessions.

When enabled, keep the seam small and explicit:

- `.agents/retro-adapter.yaml`
- `charness-artifacts/retro/recent-lessons.md`
- one stable `summary_path` instead of many ad hoc notes

## GitHub Actions Defaults

When the repo scaffolds GitHub-hosted workflows, pin maintained GitHub Actions
to current Node 24-ready majors by default. Keep the maintained baseline in
[`github-actions-defaults.md`](github-actions-defaults.md) and prefer direct
major upgrades over compatibility env vars.
