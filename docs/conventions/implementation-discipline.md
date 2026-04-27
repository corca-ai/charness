# Implementation Discipline

This document owns the validation and mutation rules that are too detailed for
the root instruction file but still apply to Charness maintenance work.

## Validation Discipline

- Repo-owned diff obligations live in [.agents/surfaces.json](../../.agents/surfaces.json);
  use `python3 scripts/check_changed_surfaces.py --repo-root .` to inspect them.
- Run `python3 scripts/run_slice_closeout.py --repo-root .` before commit when
  the slice spans generated surfaces or multiple validator families.
- Run and record the premortem required by
  [operating-contract.md](./operating-contract.md) before final closeout for
  task-completing repo work.
- `python3 scripts/sync_support.py --json` and
  `python3 scripts/update_tools.py --json` are dry-run sanity checks.
- Use `python3 scripts/doctor.py --json` only when intentionally collecting
  real machine-state diagnostics.
- Route evaluator-backed validation through `quality` before `hitl` or
  same-agent manual review.

## Change Discipline

- Prefer deleting drift over documenting drift.
- Current-pointer helpers should be no-op when canonical content has not
  changed. If a startup or inventory command rewrites an artifact without a
  canonical change, treat that as invocation drift or a helper bug.
- Treat `mutate -> sync -> verify -> publish` as hard phase barriers.
- After a command rewrites generated surfaces, plugin exports, versioned
  manifests, or git state, finish that phase before starting validators or
  publish steps.
- Use parallel tool calls only for read-only inventory or file inspection;
  never run sync, export, bump, install, update, or git mutation commands in
  parallel with validators, closeout, or publish steps.

## Generated And Installed Surfaces

- When a repo-local structural fix can also improve the installed Charness user
  surface, inspect whether a public skill, reference, packaging contract, or
  [AGENTS.md](../../AGENTS.md) should absorb the lesson before stopping.
- If a public skill needs repeated bootstrap, adapter resolution, artifact
  naming, or recovery behavior, ship a helper script instead of leaving it as
  prose-only guidance.
- When tool install, update, or support-sync work is partly manual or mutates
  the operator surface, emit structured output and persist machine-readable
  state so a later agent can continue without rediscovering the machine.

## Sync Before Validation

- Repo-owned diff obligations and closeout stay downstream of generated-surface
  sync.
- If checked-in plugin export is touched, run
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` before
  validators.
- Machine-local discovery output under `.agents/charness-discovery/` is not a
  checked-in surface; generated local stubs should not be committed as drift.
