<!--
generated_file: true
source_path: README.md
derived_path: plugins/charness/README.md
generator: python3 scripts/sync_root_plugin_manifests.py --repo-root .
sync_command: python3 scripts/sync_root_plugin_manifests.py --repo-root .
-->

# Charness - Corca Harness

`charness` is a Claude Code / Codex plugin developed by [Corca](https://www.corca.ai/).

It helps plugin developers keep shared workflow logic separate from
repo-specific rules, so skills can grow with each repository instead of
hard-coding one team's assumptions everywhere.

`charness` combines public workflow skills, repo-local adapters, support
integrations, and a managed install/update path into one system for teams that
want agents to do more real work without turning every repository into a
one-off prompt maze.

## Core Concepts

These are the core concepts `charness` uses to tackle common problems plugin
developers run into.

| Concept | Common problem | How `charness` handles it | Connected skills and areas |
| --- | --- | --- | --- |
| Less is more | If you assume the agent is not very capable, the system grows extra modes, options, explanation, and ceremony until users have to learn the framework before they can use it. | `charness` assumes a capable agent. It prefers strong defaults, a small public interface, and progressive disclosure, then moves deeper rules into adapters, helpers, and repo-owned checks only when they are actually needed. | `find-skills`, `init-repo`, `quality`, `create-skill` |
| Human-code-AI symbiosis | Automation gets brittle when people, deterministic checks, and AI all try to do the same job badly instead of each doing what they are best at. | Humans keep the decisions that require judgment, authority, physical action, or another machine. Code keeps the deterministic gates: linters, tests, validators, hooks. AI handles exploration, drafting, implementation, and synthesis. `charness` is designed to keep those roles aligned instead of blurred together. | `impl`, `quality`, `hitl`, validators, hooks |
| Shared logic, local growth | A skill written directly from one team's habits often works in one repository and feels wrong everywhere else. | `charness` keeps shared workflow concepts public, then lets each repository define its own docs, rules, checks, and operating patterns through adapters. The workflow stays recognizable, but it can still grow in ways that fit the repo using it. | public skills, adapters, `create-skill`, `narrative` |
| Agents are first-class users | If install, update, and health checks only make sense to a human operator, agents end up guessing local state and repeating recovery work every session. | `charness` ships as both plugin and CLI. The same path can install it, verify what is ready, update it later, and tell both people and agents what to do next. | install / update / doctor flows, `release`, `find-skills` |
| Concepts first, tools second | When public skills mix user-facing workflow ideas with tool-specific instructions, every tool change becomes a workflow rewrite. | `charness` keeps workflow concepts in public skills and pushes tool-specific know-how into support skills and integrations. That way a repo can swap tools without losing the workflow shape users learned. | `gather`, support skills, integrations |
| Quality makes autonomy trustworthy | As repositories get larger and agents work longer, weak code, tests, design, docs, skills, or binaries become the first place trust breaks down. | `charness` treats quality as a system-wide trust problem, not just a code-style problem. It helps repos build reliable foundations early, then improve code, tests, skills, binaries, design, docs, and operating checks together as automation grows more ambitious. | `init-repo`, `quality`, `debug`, `premortem` |
| Communication depends on who speaks to whom | Work only stays alive when it can move between people and agents, but the right format changes depending on who is talking to whom. | `charness` treats communication as part of the system. It separates announcement, narrative, handoff, and HITL review because the best shape for person -> organization, person -> person, agent -> agent, and agent -> person communication is not the same. | `announcement`, `narrative`, `handoff`, `hitl` |
| Expert tacit knowledge becomes workflow | Great debugging and review often live inside a few experts' heads, so teams keep relearning the same patterns by trial and error. | `charness` turns that tacit knowledge into reusable workflow patterns. Some skills are built from deep interviews with expert practitioners, and when a name usefully recalls the right thinking pattern, the expert's name stays in the skill. | `debug`, `premortem`, `retro`, adjacent skills |
| The system should get smarter with use | Repeated mistakes and good decisions are wasted if they disappear when the session ends. | `charness` keeps lessons alive through retro, auto-retro, adapters, validators, and durable artifacts, so both people and agents can improve the system while using it. | `retro`, `quality`, `handoff` |

## Quick Start

If you are installing `charness` yourself, start with [INSTALL.md](./INSTALL.md).
If you want an agent to do it for you, give it the install contract instead of
paraphrasing the steps:

```md
Read and follow: https://raw.githubusercontent.com/corca-ai/charness/main/INSTALL.md

Install charness on this machine.
Then verify the setup with `charness init` and `charness doctor`.
This repo should work in Claude Code and Codex.
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

[INSTALL.md](./INSTALL.md) remains the canonical install contract. The README is the
entrypoint, not the full operator manual.

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

1. Let the agent route itself from repo context, [AGENTS.md](./AGENTS.md), and installed skill metadata; use `find-skills` when discovery is unclear or the repo needs an explicit capability inventory.
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
- [INSTALL.md](./INSTALL.md), [UNINSTALL.md](./UNINSTALL.md), and
  [docs/host-packaging.md](./docs/host-packaging.md) own install and packaging
  truth
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
  [INSTALL.md](./INSTALL.md) and [docs/host-packaging.md](./docs/host-packaging.md)
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
