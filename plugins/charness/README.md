<!--
generated_file: true
source_path: README.md
derived_path: plugins/charness/README.md
generator: python3 scripts/sync_root_plugin_manifests.py --repo-root .
sync_command: python3 scripts/sync_root_plugin_manifests.py --repo-root .
-->

# Charness - Corca Harness

`charness` is a Claude Code / Codex plugin developed by [Corca](https://www.corca.ai/).

Most agent frameworks get noisier as repositories grow. `charness` goes the
other way: it keeps the public workflow surface small, pushes repo-specific
rules into adapters and checks, and keeps install, update, and discovery
legible to both humans and agents.

`charness` combines public workflow skills, repo-local adapters, support
integrations, and a managed install/update path into one system for teams that
want agents to do more real work without turning every repository into a
one-off prompt maze.

## Quick Start

Prerequisites:

- `bash`
- `git`
- `curl`
- Python 3.10+ available as `python3` or `python`
- outbound network access to `github.com`

Zero-state bootstrap:

```bash
curl -fsSLo /tmp/charness-init.sh \
  https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh
~/.local/bin/charness doctor --next-action
```

[init.sh](./init.sh) bootstraps a repo-owned isolated Python runtime under the managed
checkout before it runs `charness init`, so global `pip install jsonschema`,
`packaging`, or similar bootstrap packages should not be required.

If you want an agent to do it for you, paste the contract directly instead of
telling it to fetch a remote doc and follow it:

```md
Install charness on this machine.

Prerequisites:
- bash
- git
- curl
- Python 3.10+ available as `python3` or `python`
- outbound network access to github.com

Run:
curl -fsSLo /tmp/charness-init.sh https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh

Then run `~/.local/bin/charness doctor --next-action`.
Do exactly that next action.
When it finishes, run `~/.local/bin/charness doctor --next-action` again.
Repeat until no manual host action is required.

Use `~/.local/bin/charness doctor --json` only when you need more detail.
This machine should work in Claude Code and Codex.
After installation, use `charness update` for refreshes.
```

Once the binary is available, these are the main commands users and agents will
keep seeing:

- `charness init` to bootstrap or refresh the managed local install surface
- `charness doctor` to inspect current host state and read `next_action`
- `charness update` to refresh the installed surface later
- `charness update all` when you also want tracked external tools and bundled
  support skills refreshed in the same pass
- `charness reset` when you need to remove host plugin state while keeping the
  managed checkout and CLI
- `charness uninstall` when you want the host-facing uninstall path while
  preserving the source checkout and CLI unless explicit delete flags are passed

## Core Concepts

These are the core concepts `charness` uses to tackle common problems plugin
developers run into.

### 1. Less Is More

If you assume the agent is weak, the system grows extra modes, options,
explanations, and ceremony until users have to learn the framework before they
can use it. `charness` assumes a capable agent, prefers strong defaults and a
small public interface, and moves deeper rules into adapters, helpers, and
repo-owned checks only when they are actually needed. Connected areas:
`find-skills`, `init-repo`, `quality`, `create-skill`.

### 2. Human-Code-AI Symbiosis

Automation gets brittle when people, deterministic checks, and AI all try to
do the same job badly instead of each doing what they are best at. Humans keep
judgment, authority, physical action, and external-machine control. Code keeps
the deterministic gates. AI handles exploration, drafting, implementation, and
synthesis. Connected areas: `impl`, `quality`, `hitl`, validators, hooks.

### 3. Shared Logic, Local Growth

A skill written directly from one team's habits often works in one repository
and feels wrong everywhere else. `charness` keeps shared workflow concepts
public, then lets each repository define its own docs, rules, checks, and
operating patterns through adapters. Connected areas: public skills, adapters,
`create-skill`, `narrative`.

### 4. Agents Are First-Class Users

If install, update, and health checks only make sense to a human operator,
agents end up guessing local state and repeating recovery work every session.
`charness` ships as both plugin and CLI so the same path can install it,
verify readiness, update it later, and tell both people and agents what to do
next. Connected areas: install / update / doctor flows, `release`,
`find-skills`.

### 5. Concepts First, Tools Second

When public skills mix user-facing workflow ideas with tool-specific
instructions, every tool change becomes a workflow rewrite. `charness` keeps
workflow concepts in public skills and pushes tool-specific know-how into
support skills and integrations. Connected areas: `gather`, support skills,
integrations.

### 6. Quality Makes Autonomy Trustworthy

As repositories get larger and agents work longer, weak code, tests, design,
docs, skills, or binaries become the first place trust breaks down.
`charness` treats quality as a system-wide trust problem, not just a code-style
problem. Connected areas: `init-repo`, `quality`, `debug`, `premortem`.

### 7. Communication Depends On Who Speaks To Whom

Work only stays alive when it can move between people and agents, but the
right format changes depending on who is talking to whom. `charness` treats
communication as part of the system and separates announcement, narrative,
handoff, and HITL review accordingly. Connected areas: `announcement`,
`narrative`, `handoff`, `hitl`.

### 8. Expert Tacit Knowledge Becomes Workflow

Great debugging and review often live inside a few experts' heads, so teams
keep relearning the same patterns by trial and error. `charness` turns that
tacit knowledge into reusable workflow patterns, sometimes with sparse anchors
that recall the right move faster than extra prose. Connected areas: `debug`,
`quality`, `narrative`, `find-skills`, adjacent skills.

### 9. The System Should Get Smarter With Use

Repeated mistakes and good decisions are wasted if they disappear when the
session ends. `charness` keeps lessons alive through retro, auto-retro,
adapters, validators, and durable artifacts so both people and agents can
improve the system while using it. Connected areas: `retro`, `quality`,
`handoff`.

## Skill Map

The concepts above show up in the skill map below.

Public skills are user-facing workflow concepts. Support skills and
integrations teach the harness how to use specialized tools without turning
those tools into the product's philosophy.

### Public Skills

`init-repo` is a special entrypoint for repos that still need their initial
operating surface created or normalized. It is not just another implementation
step.

For the rest of the surface, the public skills group by intent:

- shape the work: `ideation`, `spec`, `gather`
- build and repair: `impl`, `debug`, `premortem`
- raise quality: `quality`, `retro`
- communicate across boundaries:
  `announcement` person -> organization,
  `narrative` person -> person,
  `handoff` agent -> agent,
  `hitl` agent -> person
- operate the harness: `find-skills`, `create-skill`, `create-cli`, `release`

`gather` is often a supporting move inside `ideation`, `spec`, or `impl`, not
necessarily a standalone stage in every workflow.

### Support Skills And Integrations

Support skills are non-public tool-use knowledge shared by multiple workflows.
They teach the harness how to use specialized tools consistently.

Current local support examples include:

- `web-fetch`
- `gather-slack`
- `gather-notion`

Integrations describe external ownership boundaries for install, update,
detect, healthcheck, readiness, and sync behavior.

Current integration examples include:

- `agent-browser`
- `specdown`
- `cautilus`
- `gws-cli`

This is where `cautilus` belongs in the README: as an upstream integration
boundary and evaluator-facing support tool, not as a public workflow concept.

Profiles and presets stay alongside this skill surface as default bundles and
host/repo-specific configuration seams rather than user-facing workflow
concepts.

## Example Flows

### New Repo Or Thin Operating Surface

This is the common path when the repo shape still needs to be established.

1. Start with `ideation` and let `gather` pull in outside context only when it
   sharpens the concept.
2. Once the concept is concrete enough, create or move into the right repo and
   run `init-repo`.
3. If `init-repo` changes [AGENTS.md](./AGENTS.md) or the operating surface materially,
   prefer starting a fresh session before continuing.
4. Use `spec` to turn the direction into the current executable contract.
5. Move into `impl` for the first real slice.
6. Bring in `debug` for bugs, `premortem` for before-the-fact review, and
   `quality` / `retro` when the next problem is quality improvement rather than
   raw implementation.

### Existing Repo, "Implement This"

This is the common path when the repo already has an operating surface and the
user simply wants work done.

1. Start with `find-skills` once so the current capability inventory is explicit, then route to the durable work skill from repo context, [AGENTS.md](./AGENTS.md), and installed skill metadata.
2. Go straight to `impl` when the task is already concrete enough.
3. Pull in `spec` only when the contract still needs to be shaped.
4. Use `debug` when the slice turns into root-cause work.
5. Use `premortem` when a non-trivial change needs a before-the-fact failure
   review.
6. Treat `quality` and `retro` as separate quality-raising loops for people
   and agents, not only as post-implementation cleanup.
7. Fold in communication or meta skills when the slice needs them:
   `narrative`, `announcement`, `handoff`, `hitl`, `release`,
   `create-skill`, or `create-cli`.

## Boundaries

Keep the surface ownership clear:

- the README is the first-touch orientation surface
- [docs/host-packaging.md](./docs/host-packaging.md) owns packaging truth and
  the generated host-layout contract
- [docs/operator-acceptance.md](./docs/operator-acceptance.md) owns the
  operator-facing takeover checklist
- [docs/control-plane.md](./docs/control-plane.md) and integration manifests
  own external tool contracts
- [docs/support-skill-policy.md](./docs/support-skill-policy.md) explains the
  public-skill vs support-skill vs integration boundary
- [charness-artifacts/quality/latest.md](./charness-artifacts/quality/latest.md)
  is the current dogfood quality view, not a replacement for the README

`charness` installs as one managed bundle. It should not be treated as a menu
of partially installed public skills, and skill execution itself should stay
read-only with respect to install/update state.

The checked-in install surface still lives under `plugins/charness/` and is
generated from [packaging/charness.json](./packaging/charness.json) via
`python3 scripts/sync_root_plugin_manifests.py --repo-root .`.

## Read This Next

- install or refresh the managed host surface:
  the Quick Start above and [docs/host-packaging.md](./docs/host-packaging.md)
- pick the right public/support boundary:
  [docs/support-skill-policy.md](./docs/support-skill-policy.md) and
  [docs/public-skill-validation.md](./docs/public-skill-validation.md)
- understand current rollout and takeover state:
  [docs/operator-acceptance.md](./docs/operator-acceptance.md) and
  [docs/handoff.md](./docs/handoff.md)
- inspect current quality posture:
  [charness-artifacts/quality/latest.md](./charness-artifacts/quality/latest.md)
- work on this repo itself:
  [docs/development.md](./docs/development.md)
