# Charness - Corca Harness

It helps Claude Code and Codex turn repo instructions, skills, scripts, and
checks into a repeatable product-development workflow.

`charness` is a Claude Code / Codex plugin developed by
[Corca](https://www.corca.ai/), with agent skills, scripts, and a CLI packaged
as one harness.

It was built from the patterns Corca uses across the product-development loop,
from ideation to release, and reflects the core philosophy the Corca AX team
has developed around products and agents.

## Quick Start

Make sure your machine has Python 3. Then install the managed `charness` CLI
and host plugin with:

```bash
curl -fsSLo /tmp/charness-init.sh \
  https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh
```

If you prefer, inspect the install script before running it. `setup`
changes repo files by proposing ordinary diffs; review those diffs before
committing them.

Start a fresh Claude Code or Codex session in your repository and ask the
agent to initialize the repo:

```md
Use charness to initialize this repo.
```

The agent will load
[`charness:setup`](./skills/public/setup/SKILL.md) to update the
repo's [AGENTS.md](./AGENTS.md) and related settings. After that, you can keep
prompting the agent in your usual style, with `charness` giving the agent
routing context underneath instead of requiring you to name a skill every time.

The CLI is there so humans and agents can inspect local harness state instead
of guessing. For day-to-day operation, start with `charness --help`,
`charness doctor`, and `charness update`.

Use `charness update all` when you also want to refresh tracked external tools
and bundled support skills.

For the full command surface, see [CLI Reference](./docs/generated/cli-reference.md).

## Workflow Routes

After setup, ask for the work in normal product language. `charness` uses repo
instructions and skill metadata to route the agent underneath, so most prompts
do not need to name a skill.

- New project: shape the idea with `ideation`, initialize with `setup`, turn
  the direction into a `spec`, then build through `impl`.
- Existing repo: run `setup` if the repo is not initialized, then ask directly
  for implementation, debugging, quality review, story work, handoff, or
  release help.
- Long-running objective: use `achieve` to shape an auditable goal artifact,
  then activate it with `/goal` where your host provides it so progress, proof,
  and non-claims stay visible.
- Known workflow: call a skill directly when that is clearer. Claude uses
  `/charness:<skill>`; Codex uses `$charness:<skill>`.

For the longer route guide, including retros, Cautilus-backed review, and
long-running goal examples, see [Workflow Routes](./docs/workflow-routes.md).

## Core Concepts

These are the core concepts behind `charness`; for the concrete workflow
surface, see [Skill Map](#skill-map).

1. Less Is More: strong defaults and progressive disclosure beat long prompt
   menus.
2. Agents Are First-Class Users: CLIs, scripts, artifacts, and docs should be
   usable by agents as well as humans.
3. Reveal Intent, Hide Detail: public skills name user intent; support skills
   and integrations carry tool-specific detail underneath.
4. Human-Code-AI Symbiosis: humans keep judgment, code keeps repeatable proof,
   and AI handles exploration, synthesis, and implementation.
5. Long-Running Agents Need Quality Software: quality is a trust surface, not
   just a style pass.
6. Tacit Knowledge Becomes Workflow: debugging, review, product judgment, and
   communication patterns become reusable skills.
7. The System Should Get Smarter With Use: retros, adapters, validators, and
   artifacts preserve lessons across sessions.
8. Context Must Keep Flowing: narrative, release notes, handoff, and review
   loops move work across human and agent boundaries.

## Skill Map

`charness` keeps two skill surfaces: public and support. Public skills are
workflow names a human or agent may reasonably ask for; support skills and
integrations stay underneath to carry tool-specific detail.

Terminology:

- support skill: tool-use instructions that public workflows can consume
- support capability: `charness`-owned runtime/provider metadata for discovery
  and doctor context
- integration manifest: external tool lifecycle metadata for install, update,
  detect, healthcheck, readiness, and support-skill sync behavior

### Public Skills

Use [`setup`](./skills/public/setup/SKILL.md) when a repo needs its
first project overview, [AGENTS.md](./AGENTS.md), roadmap, or
operator-facing setup.

The rest of the public surface groups by intent:

- shape the work:
  [`gather`](./skills/public/gather/SKILL.md),
  [`ideation`](./skills/public/ideation/SKILL.md),
  [`spec`](./skills/public/spec/SKILL.md)
- build and repair:
  [`impl`](./skills/public/impl/SKILL.md),
  [`debug`](./skills/public/debug/SKILL.md),
  [`critique`](./skills/public/critique/SKILL.md)
- raise quality:
  [`quality`](./skills/public/quality/SKILL.md),
  [`retro`](./skills/public/retro/SKILL.md)
- run long goals:
  [`achieve`](./skills/public/achieve/SKILL.md) auditable goal lifecycle for
  autonomous objectives
- communicate across boundaries:
  [`narrative`](./skills/public/narrative/SKILL.md) durable truth and story alignment,
  [`announcement`](./skills/public/announcement/SKILL.md) audience/channel adaptation,
  [`handoff`](./skills/public/handoff/SKILL.md) agent -> agent,
  [`hitl`](./skills/public/hitl/SKILL.md) agent -> person,
  [`issue`](./skills/public/issue/SKILL.md) GitHub issue filing and resolution
- operate the harness:
  [`find-skills`](./skills/public/find-skills/SKILL.md),
  [`create-skill`](./skills/public/create-skill/SKILL.md),
  [`create-cli`](./skills/public/create-cli/SKILL.md),
  [`release`](./skills/public/release/SKILL.md)

[`gather`](./skills/public/gather/SKILL.md) is often a supporting move inside
[`ideation`](./skills/public/ideation/SKILL.md),
[`spec`](./skills/public/spec/SKILL.md), or
[`impl`](./skills/public/impl/SKILL.md), not necessarily a standalone stage in
every workflow.

### Support Skills And Integrations

Support skills are tool-use knowledge that helps public skills work. They are
not public workflow names. Integrations are external-tool manifests that carry
install, update, detection, healthcheck, readiness, and support-skill sync
behavior.

See [Support Skill Policy](./docs/support-skill-policy.md) for the boundary and
[Control Plane](./docs/control-plane.md) for integration lifecycle detail.

## Learn More

README is the first-touch orientation surface. Deeper contracts live in the
docs and artifacts that own them:

- CLI command reference: [docs/generated/cli-reference.md](./docs/generated/cli-reference.md)
- workflow route examples: [docs/workflow-routes.md](./docs/workflow-routes.md)
- repo-local development and dogfood paths:
  [docs/development.md](./docs/development.md)
- packaging and generated host layout:
  [docs/host-packaging.md](./docs/host-packaging.md),
  [packaging/charness.json](./packaging/charness.json)
- external tools, support materialization, and update/doctor state:
  [docs/control-plane.md](./docs/control-plane.md)
- public/support/integration boundaries:
  [docs/support-skill-policy.md](./docs/support-skill-policy.md)
- public skill validation policy:
  [docs/public-skill-validation.md](./docs/public-skill-validation.md)
- current dogfood quality posture:
  [charness-artifacts/quality/latest.md](./charness-artifacts/quality/latest.md)
