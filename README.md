# charness

`charness` is the portable Corca harness layer.

It defines reusable agent skills, support integrations, profiles, adapter
conventions, and validation flows that downstream hosts can adopt without
copying host-specific policy into public skills.

## Who It Is For

- teams maintaining repo-owned agent workflows or skill packs across Claude,
  Codex, or adjacent host surfaces
- maintainers who want portable workflow concepts instead of host-specific
  prompt bundles
- operators who want install, update, doctor, and support-sync seams without
  turning `charness` into the runtime owner of every external tool

Day-1 trigger: your repo has recurring agent work such as repo bootstrap,
external-source gathering, concept shaping, implementation, quality review,
handoff, or release work, and you want those workflows to stay portable across
hosts instead of re-explaining them in each prompt surface.

Not for: repos whose main problem is evaluator-driven behavior regression or
prompt optimization. That boundary belongs in `cautilus` or an explicit HITL /
evaluation workflow, not in `charness`.

## Why `charness`

The stance, in four contrasts:

- Unlike a host-specific prompt pack, `charness` keeps public workflow concepts
  portable and pushes host-specific policy into adapters, presets, and
  generated install surfaces.
- Unlike a scaffold scrapbook, `charness` ships reusable skills, support
  integrations, profiles, and validators as one harness bundle instead of
  asking each repo to recopy the same operational lore.
- Unlike an eval harness, `charness` keeps deterministic repo-owned gates local
  and routes evaluator-heavy or comparison-heavy behavior review into
  `cautilus`, `hitl`, or explicit operator review.
- Unlike a raw tool wrapper collection, `charness` separates workflow concepts
  from tool-use knowledge: public skills express user-facing work, while
  support skills and integration manifests teach the harness how to use
  specialized tools.

## What To Use When

- starting or normalizing a repo operating surface: `init-repo`
- gathering outside source material into durable local artifacts: `gather`
- shaping an idea before contract or code exists: `ideation`
- turning a direction into an executable implementation contract: `spec`
- changing code, config, tests, or operator-facing artifacts: `impl`
- investigating a bug, regression, or confusing behavior: `debug`
- aligning README, handoff, or source-of-truth docs: `narrative`
- adapting aligned truth into human-facing delivery copy: `announcement`
- reviewing current quality posture and next gates: `quality`
- inserting bounded human judgment into a review loop: `hitl`
- preparing the next session or leaving pickup state: `handoff`
- reflecting on a work unit and repeat traps: `retro`
- finding hidden or support capabilities before ad hoc search: `find-skills`
- creating harness-owned skills or CLIs: `create-skill`, `create-cli`
- cutting or verifying a release surface: `release`

If you are deciding between surfaces:

- public skill: user-facing workflow concept
- support skill: repeated tool-usage knowledge shared by multiple workflows
- integration manifest: external ownership boundary for install, update,
  detect, healthcheck, and readiness

## One Concrete Workflow

Start here if you want one picture before reading the rest of the surface.

Scenario: you want to add a new repo-owned workflow, and the shape is still
forming.

- `ideation`: sharpen the workflow concept, user path, and system boundary
- `spec`: turn that direction into the current executable contract
- `impl`: make the code, config, tests, and operator-facing artifacts match the contract
- `quality`: review whether the local proof bar is strong enough and what gate
  should move next
- `handoff`: leave the next session a precise pickup point if the slice is not done

If the work starts from an unshaped or partially initialized repo, begin with
`init-repo`. If the real uncertainty is behavior regression under prompt or
workflow changes, hand that boundary to `cautilus` instead of stretching
`charness` into an eval harness.

## One Bootstrap Workflow

Scenario: the repo exists, but its operating surface is still thin or uneven.

- `init-repo`: create or normalize the README, operating docs, and takeover
  surfaces without pretending deep product design already exists
- `narrative`: tighten the durable story once the repo has enough real shape to
  align source-of-truth docs
- `quality`: check whether the local proof bar matches the repo's actual risk
- `handoff`: leave the next maintainer a precise starting point instead of
  rediscovery work

This path is for making a repo operable. It is not the same as evaluator
hardening, prompt optimization, or host-specific packaging work.

## Scope

`charness` owns:

- public workflow skills
- support skills for specialized tools
- profiles, presets, and adapter conventions
- integration manifests for external binaries and upstream support skills
- self-validation scenarios for bootstrap quality and intent fidelity

`charness` does not own host-specific product logic, downstream-specific
prompts, or external binaries that already live in their own repos. Install it
as one harness bundle; downstream hosts can narrow exposure with host-owned
adapters and presets instead of partially installing public skills.

## Public Surface

Public skills are user-facing concepts: `init-repo`, `gather`, `ideation`,
`spec`, `impl`, `debug`, `retro`, `quality`, `narrative`, `announcement`,
`handoff`, `hitl`, `create-skill`, `find-skills`, and `release`.

Support skills stay non-user-facing and help those workflows use specialized
tools consistently. Current profile examples are `constitutional`,
`collaboration`, `engineering-quality`, and `meta-builder`. Current
integration examples are `agent-browser`, `specdown`, and `cautilus`.

## External Tool Policy

If a specialized tool already exists upstream, `charness` should not vendor the
binary. It should provide the manifest, install/update guidance, capability and
access-mode guidance, detection, version expectations, health checks, and a
wrapper only when harness-specific knowledge is required locally.

## Current Plan

Current planning and takeover surfaces live in
[docs/external-integrations.md](./docs/external-integrations.md) and
[docs/operator-acceptance.md](./docs/operator-acceptance.md).

## Read This Next

Use the README as the entrypoint, not as the only rollout or install contract.

- picking the right skill or boundary:
  [docs/support-skill-policy.md](./docs/support-skill-policy.md) and
  [docs/public-skill-validation.md](./docs/public-skill-validation.md)
- evaluating internal rollout readiness:
  [docs/operator-acceptance.md](./docs/operator-acceptance.md) and
  [charness-artifacts/quality/latest.md](./charness-artifacts/quality/latest.md)
- installing or verifying the managed host surface:
  [INSTALL.md](./INSTALL.md) and [docs/host-packaging.md](./docs/host-packaging.md)

## Plugin Install Surface

`charness` installs as one managed plugin bundle that includes public skills,
support skills, profiles, presets, and integration manifests. It does not
bundle external binaries or third-party plugin repos referenced only through
integration manifests.

The checked-in install surface lives under `plugins/charness/`. Root-level
compatibility artifacts are generated from
[packaging/charness.json](./packaging/charness.json) via
`python3 scripts/sync_root_plugin_manifests.py --repo-root .`. Diff obligations
for that surface live in [`.agents/surfaces.json`](./.agents/surfaces.json).

## Local Development

Use [`./scripts/run-quality.sh`](./scripts/run-quality.sh) as the canonical local quality gate,
`python3 scripts/check-changed-surfaces.py --repo-root .` for diff-aware
obligations, and `python3 scripts/run-slice-closeout.py --repo-root .` for the
repo-owned closeout path. Install `.githooks/pre-push` with
[`./scripts/install-git-hooks.sh`](./scripts/install-git-hooks.sh) so the clone's `core.hooksPath` points at the
checked-in hook.

Use `charness doctor` for shared startup advice and version/install drift. It
prints current version state, host update hints, and last observed integration
readiness from lock state. It stays read-only.

## Install And Update

Canonical install documents live in [INSTALL.md](./INSTALL.md),
[UNINSTALL.md](./UNINSTALL.md), [docs/host-packaging.md](./docs/host-packaging.md),
and [docs/development.md](./docs/development.md) for proof-only or repo-local
flows.

All official install paths converge on `charness init`. The managed local
install is the canonical operator contract, and `charness init` is the host
detector when the machine state is still unknown.

Primary operator path once the binary is available: `charness init`,
`charness doctor`, `charness update`, `charness update all`,
`charness task claim slice-1 --summary "..."`, `charness reset`,
`charness uninstall`.

If the machine starts in a zero-state posture with no PATH binary and no local
checkout, bootstrap once from the raw script:

```bash
curl -fsSLo /tmp/charness-init.sh \
  https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh
```

Use [`./init.sh`](./init.sh) only as a checkout convenience wrapper when the repo already
exists locally. The managed install keeps its checkout under
`~/.agents/src/charness`; the installed surface still excludes external
binaries such as `cautilus` and other host-owned prompts or product logic.

Follow `next_action` from `charness init`, `charness doctor`, or
`charness update` instead of guessing which host step is still missing.
`charness doctor --write-state` lets you persist a proof snapshot to
`~/.local/state/charness/host-state.json`.

Adjacent command anchors:
`charness task claim slice-1 --summary "Implement the first slice"`,
`charness task submit slice-1 --summary "Finished with tests" --artifact
tests/example_test.py`, `charness task abort slice-1 --reason "blocked by
missing fixture"`, `.charness/tasks/`, `charness capability init`,
`charness capability resolve slack.default`,
`charness capability doctor slack.default`, `charness tool doctor cautilus`,
`charness tool install cautilus`, `charness tool update agent-browser`,
`charness tool sync-support cautilus`, `charness update all`.

Machine-local capability config lives under `~/.config/charness/`. Manual-mode
tool flows persist manual install guidance plus refreshed doctor state instead
of pretending the host was mutated.

Command intent stays stable even when host details evolve: `init` bootstraps or
refreshes the managed local install surface, `doctor` inspects host state and
emits `next_action`, `update` means run `charness update` to refresh the
installed surface for `charness` itself, `update all` adds `tool update`
fan-out for tracked external binaries plus bundled support-skill refresh,
`reset` means remove host plugin state while keeping the managed checkout and
CLI, and skill execution must stay read-only with respect to install/update
state.

Removal details stay in [UNINSTALL.md](./UNINSTALL.md), including
`charness uninstall --delete-checkout`, `charness uninstall --delete-cli`, and
the default behavior of preserving the source checkout and CLI unless explicit
delete flags are passed.

Detailed owner docs: [docs/agent-task-envelope.md](./docs/agent-task-envelope.md)
owns the `task` surface, [docs/capability-resolution.md](./docs/capability-resolution.md)
owns the `capability` surface, and [docs/control-plane.md](./docs/control-plane.md)
plus integration manifests own the `tool` surface.

## Repository Shape

Top-level areas: `skills/`, `integrations/`, `packaging/`, `profiles/`,
`presets/`, `docs/`, `evals/`, `scripts/`, and `plugins/`.
