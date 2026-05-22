<!--
generated_file: true
source_path: README.md
derived_path: plugins/charness/README.md
generator: python3 scripts/sync_root_plugin_manifests.py --repo-root .
sync_command: python3 scripts/sync_root_plugin_manifests.py --repo-root .
-->

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
[`charness:setup`](./skills/setup/SKILL.md) to update the
repo's [AGENTS.md](https://github.com/corca-ai/charness/blob/main/AGENTS.md) and related settings. After that, you can keep
prompting the agent in your usual style, with `charness` giving the agent
routing context underneath instead of requiring you to name a skill every time.

The CLI is there so humans and agents can inspect local harness state instead
of guessing. For day-to-day operation, start with `charness --help`,
`charness doctor`, and `charness update`.

Use `charness update all` when you also want to refresh tracked external tools
and bundled support skills.

For the full command surface, see [CLI Reference](https://github.com/corca-ai/charness/blob/main/docs/generated/cli-reference.md).

## Workflow Routes

After setup, ask for the work in normal product language. `charness` uses repo
instructions and skill metadata to route the agent underneath, so most prompts
do not need to name a skill.

- New project: shape the idea with `ideation`, initialize with `setup`, turn
  the direction into a `spec`, then build through `impl`.
- Existing repo: run `setup` if the repo is not initialized, then ask directly
  for implementation, debugging, quality review, story work, handoff, or
  release help.
- Known workflow: call a skill directly when that is clearer. Claude uses
  `/charness:<skill>`; Codex uses `$charness:<skill>`.

For the longer route guide, including retros, Cautilus-backed review, and
existing-repo examples, see [Workflow Routes](https://github.com/corca-ai/charness/blob/main/docs/workflow-routes.md).

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

Use [`setup`](./skills/setup/SKILL.md) when a repo needs its
first project overview, [AGENTS.md](https://github.com/corca-ai/charness/blob/main/AGENTS.md), roadmap, or
operator-facing setup.

The rest of the public surface groups by intent:

- shape the work:
  [`gather`](./skills/gather/SKILL.md),
  [`ideation`](./skills/ideation/SKILL.md),
  [`spec`](./skills/spec/SKILL.md)
- build and repair:
  [`impl`](./skills/impl/SKILL.md),
  [`debug`](./skills/debug/SKILL.md),
  [`critique`](./skills/critique/SKILL.md)
- raise quality:
  [`quality`](./skills/quality/SKILL.md),
  [`retro`](./skills/retro/SKILL.md)
- communicate across boundaries:
  [`narrative`](./skills/narrative/SKILL.md) durable truth and story alignment,
  [`announcement`](./skills/announcement/SKILL.md) audience/channel adaptation,
  [`handoff`](./skills/handoff/SKILL.md) agent -> agent,
  [`hitl`](./skills/hitl/SKILL.md) agent -> person,
  [`issue`](./skills/issue/SKILL.md) GitHub issue filing and resolution
- operate the harness:
  [`find-skills`](./skills/find-skills/SKILL.md),
  [`create-skill`](./skills/create-skill/SKILL.md),
  [`create-cli`](./skills/create-cli/SKILL.md),
  [`release`](./skills/release/SKILL.md)

[`gather`](./skills/gather/SKILL.md) is often a supporting move inside
[`ideation`](./skills/ideation/SKILL.md),
[`spec`](./skills/spec/SKILL.md), or
[`impl`](./skills/impl/SKILL.md), not necessarily a standalone stage in
every workflow.

### Support Skills And Integrations

Support skills are tool-use knowledge that helps public skills work. They are
not public workflow names. Integrations are external-tool manifests that carry
install, update, detection, healthcheck, readiness, and support-skill sync
behavior.

See [Support Skill Policy](https://github.com/corca-ai/charness/blob/main/docs/support-skill-policy.md) for the boundary and
[Control Plane](https://github.com/corca-ai/charness/blob/main/docs/control-plane.md) for integration lifecycle detail.

## Learn More

README is the first-touch orientation surface. Deeper contracts live in the
docs and artifacts that own them:

- CLI command reference: [docs/generated/cli-reference.md](https://github.com/corca-ai/charness/blob/main/docs/generated/cli-reference.md)
- workflow route examples: [docs/workflow-routes.md](https://github.com/corca-ai/charness/blob/main/docs/workflow-routes.md)
- repo-local development and dogfood paths:
  [docs/development.md](https://github.com/corca-ai/charness/blob/main/docs/development.md)
- packaging and generated host layout:
  [docs/host-packaging.md](https://github.com/corca-ai/charness/blob/main/docs/host-packaging.md),
  [packaging/charness.json](https://github.com/corca-ai/charness/blob/main/packaging/charness.json)
- external tools, support materialization, and update/doctor state:
  [docs/control-plane.md](https://github.com/corca-ai/charness/blob/main/docs/control-plane.md)
- public/support/integration boundaries:
  [docs/support-skill-policy.md](https://github.com/corca-ai/charness/blob/main/docs/support-skill-policy.md)
- public skill validation policy:
  [docs/public-skill-validation.md](https://github.com/corca-ai/charness/blob/main/docs/public-skill-validation.md)
- current dogfood quality posture:
  [charness-artifacts/quality/latest.md](https://github.com/corca-ai/charness/blob/main/charness-artifacts/quality/latest.md)
