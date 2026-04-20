<!--
generated_file: true
source_path: README.md
derived_path: plugins/charness/README.md
generator: python3 scripts/sync_root_plugin_manifests.py --repo-root .
sync_command: python3 scripts/sync_root_plugin_manifests.py --repo-root .
-->

# charness

`charness` is the portable Corca harness layer for repo-owned agent work.

It packages public workflow skills, support skills, profiles, presets,
integration manifests, and repo-owned validation flows so a host can adopt one
coherent harness surface instead of rebuilding the same operating lore in each
prompt surface.

Use it when your repo has recurring agent work such as concept shaping,
implementation, review, handoff, or release work, and you want those workflows
to stay portable across Claude Code, Codex, or adjacent host surfaces.

In a normal task-oriented session, `charness` now starts from a capability map:
run `charness:find-skills` first, then choose the public skill or supporting
capability that fits the task.

## Who It Is For

- teams maintaining repo-owned agent workflows or skill packs across Claude
  Code, Codex, or adjacent host surfaces
- maintainers who want portable workflow concepts instead of host-specific
  prompt bundles
- operators who want install, update, doctor, and support-sync seams without
  turning `charness` into the runtime owner of every external tool

## Quick Start

If you want an agent to install `charness`, give it the install contract
instead of paraphrasing the steps:

```md
Read and follow: https://raw.githubusercontent.com/corca-ai/charness/main/INSTALL.md

Install charness on this machine.
Then verify the setup with `charness init` and `charness doctor`.
This repo should work in Claude Code and Codex.
After installation, use `charness update` for refreshes.
```

Primary operator path once the binary is available:

- `charness init` to bootstrap or refresh the managed local install surface
- `charness doctor` to inspect current host state and read `next_action`
- `charness update` to refresh the installed surface later
- `charness update all` when you also want tracked external tools and bundled
  support skills refreshed in the same pass
- `charness reset` when you need to remove host plugin state while keeping the
  managed checkout and CLI
- `charness uninstall` when you want the host-facing uninstall path while
  preserving the source checkout and CLI unless explicit delete flags are passed
- `charness task claim <task-id> --summary "<summary>"` when you want a
  machine-readable task handoff record under `.charness/tasks/`

[INSTALL.md](./INSTALL.md) remains the canonical install contract. The README is the
entrypoint, not the full operator manual.

## Skill Map

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

This is where `cautilus` belongs in the README: as an upstream-owned support
binary / skill surface that `charness` can integrate with, not as a public
workflow concept.

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

1. Start with `find-skills` so the session begins with the current capability
   map.
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
