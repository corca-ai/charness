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

If you prefer, inspect the install script before running it. `init-repo`
changes repo files by proposing ordinary diffs; review those diffs before
committing them.

Start a fresh Claude Code or Codex session in your repository and ask the
agent to initialize the repo:

```md
Use charness to initialize this repo.
```

The agent will load
[`charness:init-repo`](./skills/public/init-repo/SKILL.md) to update the
repo's [AGENTS.md](./AGENTS.md) and related settings. After that, you can keep
prompting the agent in your usual style, with `charness` giving the agent
routing context underneath instead of requiring you to name a skill every time.

The CLI is there so humans and agents can inspect local harness state instead
of guessing. For day-to-day operation, start with `charness --help`,
`charness doctor`, and `charness update`.

Use `charness update all` when you also want to refresh tracked external tools
and bundled support skills.

For the full command surface, see [CLI Reference](./docs/cli-reference.md).

## How You Use It

If you have just installed `charness` and the repo has not been initialized
yet, it is safer to call the workflow skill directly. Once `init-repo` has
updated [AGENTS.md](./AGENTS.md) and related settings, use normal
product-development prompts; `charness` gives the agent routing context
underneath.

### Starting A New Project

1. Start with `ideation`: describe the rough idea, then let the agent help
   you brainstorm, challenge, and clarify it. It can also route to `gather`
   when you provide URLs, threads, or other outside context that would sharpen
   the concept.
2. Once the concept is concrete enough, ask the agent to create a directory
   and use `init-repo`. It should propose the first repo surface, including
   [AGENTS.md](./AGENTS.md), so future sessions can use `charness` more
   naturally.
3. Start a fresh session in the new directory. Ask the agent to turn the
   direction into a buildable contract. Routes: `spec`, with premortem-style
   review when the decision is risky enough.
4. Ask for the first real implementation slice. Routes: `impl`, with
   verification, debugging, and premortem review pulled in as needed.
5. If the agent moved in a frustrating direction, or if it found a pattern you
   want future sessions to repeat, ask for a retro. Routes: `retro`.
6. Once enough code or docs exist, ask for a quality check. Routes: `quality`,
   covering repo posture such as missing gates, brittle tests, duplicate code,
   security risks, documentation drift, and skill or script ergonomics.

Retros can trigger automatically when a correction exposes a real workflow miss
or when repo adapter rules require one, but asking for one explicitly gives the
agent a stronger improvement loop. For prompt- or behavior-affecting changes,
[`cautilus`](https://github.com/corca-ai/cautilus) can provide evaluator-backed
scenario review when installed and configured.

### Working In An Existing Repo

1. If the repo has not been initialized with `charness`, ask the agent to use
   `init-repo` first. It should normalize [AGENTS.md](./AGENTS.md) and related
   operating surfaces without turning the repo into a generic template.
2. Ask for the concrete work directly: `Implement this`, `Fix this failing
   test`, or `Debug this behavior`. Routes: `impl` or `debug`.
3. If the task is under-specified, ask the agent to shape the contract before
   coding. Routes: `spec`, with premortem review when the change is risky.
4. When you want to explain progress, rewrite the repo story, or prepare a
   human-facing update, ask for that communication. Routes: `narrative` or
   `announcement`.
5. When the agent has done enough that the next session needs context, or when
   you want to review what it did and why, ask for a handoff or review loop.
   Routes: `handoff` or `hitl`.
6. When the repo needs a stronger quality bar, ask for quality review or
   follow-up gates. Routes: `quality`, with `retro` when the lesson should
   persist.

Of course, you can call a skill directly when you already know the workflow you
want. For example, `/charness:quality` should start a broad quality pass, and
`/charness:narrative` should focus the agent on README or repo-story work. In
Codex, use `$` instead of `/` for direct skill invocation.

## Core Concepts

These are the core concepts behind `charness`: the philosophy Corca uses to
tackle common problems that harness and agent-app developers run into. For what
each plugin skill does, see [Skill Map](#skill-map).

### 1. Less Is More

Agents are already capable enough to follow intent when the repo tells them
what exists, why it exists, and where to look next. `charness` leans on
progressive disclosure instead of packing every workflow with step-by-step
prompt instructions.

It also treats modes and options as design debt unless they carry a real
distinction the user should control. Strong defaults are better than making
every operator choose from a menu before work can begin.

Connected areas:
[`find-skills`](./skills/public/find-skills/SKILL.md),
[`init-repo`](./skills/public/init-repo/SKILL.md),
[`quality`](./skills/public/quality/SKILL.md),
[`create-skill`](./skills/public/create-skill/SKILL.md).

### 2. Agents Are First-Class Users

Docs and tools should assume agents will use them often, sometimes more often
than humans. `charness` treats CLIs, scripts, generated artifacts, and repo
instructions as agent-facing interfaces, not just maintainer conveniences.

Commands should emit useful state, name the next action, and compose with other
commands. Docs should point to the next surface, and artifacts should preserve
decisions another agent can resume. Skills teach agents when and why to use
those surfaces, so repo docs do not have to repeat the same operational
playbook.

Connected areas:
[`find-skills`](./skills/public/find-skills/SKILL.md),
[`create-cli`](./skills/public/create-cli/SKILL.md),
[`handoff`](./skills/public/handoff/SKILL.md),
[`release`](./skills/public/release/SKILL.md), CLI commands, helper scripts,
repo docs.

### 3. Reveal Intent, Hide Detail

The public surface should name the intent a human or agent actually has.
Tool-specific detail should stay underneath that surface unless the user is
debugging or extending the harness.

That is why `gather` is public while `web-fetch` is not: the user wants
context, not a fetch strategy. `spec` is public while `specdown` is not: the
user wants a buildable contract, not an executable-spec tool. The workflow
stays stable even when the tool path changes.

Connected areas:
[`gather`](./skills/public/gather/SKILL.md),
[`spec`](./skills/public/spec/SKILL.md), support skills, integrations.

### 4. Human-Code-AI Symbiosis

Humans, code, and AI are good at different things. `charness` avoids
pretending that better prompts can replace human judgment, deterministic gates,
or real tool feedback.

Humans keep judgment, authority, physical action, and external-machine
control. Code keeps repeatable checks such as linters and tests. AI handles
exploration, drafting, implementation, and synthesis, then hands decisions or
verification back to the right owner when needed.

Connected areas:
[`impl`](./skills/public/impl/SKILL.md),
[`quality`](./skills/public/quality/SKILL.md),
[`hitl`](./skills/public/hitl/SKILL.md).

### 5. Long-Running Agents Need Quality Software

Agents do not magically make messy repositories safe; they are signal
amplifiers. The longer they run, the more the repo's existing structure, tests,
docs, and scripts shape what they notice, trust, and repeat.

`charness` treats quality as a first-class trust surface, not a code-style
pass. It looks for missing gates, brittle tests, duplicate logic, security
risk, documentation drift, skill ergonomics, tool health, runtime cost, and
places where repeated judgment should become a validator or script.

Connected areas:
[`init-repo`](./skills/public/init-repo/SKILL.md),
[`quality`](./skills/public/quality/SKILL.md),
[`debug`](./skills/public/debug/SKILL.md),
[`premortem`](./skills/public/premortem/SKILL.md).

### 6. Tacit Knowledge Becomes Workflow

Good debugging, review, product judgment, and communication often live as
tacit knowledge inside a few expert heads. `charness` turns that knowledge into
reusable workflow moves instead of making every agent rediscover it by trial
and error.

Sometimes a sparse expert anchor guides the agent into a better reasoning space
by retrieving the right pattern from the model's pretrained knowledge: Daniel
Jackson for concept discipline, Jef Raskin for discoverability, Gerald
Weinberg for systems thinking, Atul Gawande for checklists, Barbara Minto for
structured communication, and more.

Connected areas:
[`debug`](./skills/public/debug/SKILL.md),
[`quality`](./skills/public/quality/SKILL.md),
[`narrative`](./skills/public/narrative/SKILL.md),
[`find-skills`](./skills/public/find-skills/SKILL.md),
[`create-skill`](./skills/public/create-skill/SKILL.md).

### 7. The System Should Get Smarter With Use

A harness should not be a frozen snapshot of one team's habits. `charness`
keeps shared workflow concepts public, then uses repo-local adapters to
connect those concepts to each repo's own docs, rules, checks, and durable
artifacts.

When an agent repeats a mistake, finds a useful pattern, or receives a
correction, that lesson should not disappear with the session. `retro` turns
retrospective review into a workflow: session retros capture what should change
after a meaningful work unit, while weekly retros can summarize broader
patterns. Those lessons can then become better repo instructions, validators,
quality gates, handoffs, adapters, or skill behavior.

Connected areas:
[`retro`](./skills/public/retro/SKILL.md),
[`quality`](./skills/public/quality/SKILL.md),
[`handoff`](./skills/public/handoff/SKILL.md),
[`create-skill`](./skills/public/create-skill/SKILL.md), adapters.

### 8. Context Must Keep Flowing

Thousands of lines of code are worthless if the work stays trapped where no one
can understand, evaluate, or use it. Information becomes valuable only when it
is properly shaped for the customer, maintainer, or next agent who needs to
act on it.

`charness` treats communication as part of the core workflow, not cleanup. A
repo story, release update, next-session handoff, and human review loop all
need different shapes because they move context across different boundaries.

Connected areas:
[`announcement`](./skills/public/announcement/SKILL.md),
[`narrative`](./skills/public/narrative/SKILL.md),
[`handoff`](./skills/public/handoff/SKILL.md),
[`hitl`](./skills/public/hitl/SKILL.md).

## Skill Map

`charness` keeps two skill surfaces: public and support. Public skills are
workflow names a human or agent may reasonably ask for; support skills and
integrations stay underneath to carry tool-specific detail.

### Public Skills

Use [`init-repo`](./skills/public/init-repo/SKILL.md) when a repo needs its
first [README.md](./README.md), [AGENTS.md](./AGENTS.md), roadmap, or
operator-facing setup.

The rest of the public surface groups by intent:

- shape the work:
  [`gather`](./skills/public/gather/SKILL.md),
  [`ideation`](./skills/public/ideation/SKILL.md),
  [`spec`](./skills/public/spec/SKILL.md)
- build and repair:
  [`impl`](./skills/public/impl/SKILL.md),
  [`debug`](./skills/public/debug/SKILL.md),
  [`premortem`](./skills/public/premortem/SKILL.md)
- raise quality:
  [`quality`](./skills/public/quality/SKILL.md),
  [`retro`](./skills/public/retro/SKILL.md)
- communicate across boundaries:
  [`announcement`](./skills/public/announcement/SKILL.md) person -> organization,
  [`narrative`](./skills/public/narrative/SKILL.md) person -> person,
  [`handoff`](./skills/public/handoff/SKILL.md) agent -> agent,
  [`hitl`](./skills/public/hitl/SKILL.md) agent -> person
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
not meant to be invoked as public workflow names; they are closer to tool-call
playbooks that public skills can use.

Representative support skills:

- [`agent-browser`](./skills/support/agent-browser/SKILL.md): browser
  automation support
- [`markdown-preview`](./skills/support/markdown-preview/SKILL.md): rendered
  Markdown review support
- [`specdown`](./plugins/charness/support/specdown/SKILL.md): executable-spec
  support
- [`web-fetch`](./skills/support/web-fetch/SKILL.md): public-web fetch routing
  support

Integrations are manifests for external tools, usually CLI binaries, that
`charness` does not own directly. They declare install, update, detection,
healthcheck, readiness, and sync behavior; some integrations also point at
upstream support skills that can be materialized locally.

Current integrations:

- [`agent-browser`](./integrations/tools/agent-browser.json)
- [`cautilus`](./integrations/tools/cautilus.json)
- [`github-gh`](./integrations/tools/github-gh.json)
- [`gitleaks`](./integrations/tools/gitleaks.json)
- [`glow`](./integrations/tools/glow.json)
- [`gws-cli`](./integrations/tools/gws-cli.json)
- [`ruff`](./integrations/tools/ruff.json)
- [`specdown`](./integrations/tools/specdown.json)

`charness update all` is the operator path for refreshing the installed
`charness` surface together with tracked external tools and materialized
support skills.

## Learn More

README is the first-touch orientation surface. Deeper contracts live in the
docs and artifacts that own them:

- CLI command reference: [docs/cli-reference.md](./docs/cli-reference.md)
- repo-local development and dogfood paths:
  [docs/development.md](./docs/development.md)
- packaging and generated host layout:
  [docs/host-packaging.md](./docs/host-packaging.md)
- external tools, support materialization, and update/doctor state:
  [docs/control-plane.md](./docs/control-plane.md)
- public/support/integration boundaries:
  [docs/support-skill-policy.md](./docs/support-skill-policy.md)
- public skill validation policy:
  [docs/public-skill-validation.md](./docs/public-skill-validation.md)
- current dogfood quality posture:
  [charness-artifacts/quality/latest.md](./charness-artifacts/quality/latest.md)

`charness` installs as one managed bundle, not a menu of partially installed
public skills. The checked-in host plugin surface lives under
[`plugins/charness/`](./plugins/charness/) and is generated from
[`packaging/charness.json`](./packaging/charness.json).
