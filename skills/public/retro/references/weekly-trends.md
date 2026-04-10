# Weekly Evidence And Trends

This reference captures what `charness` should and should not borrow from
`gstack`'s heavier weekly retro flow.

## Useful Imports

- name the weekly window explicitly instead of implying "recently"
- state which evidence sources were actually used
- compare against the last durable weekly retro when one exists
- persist a compact snapshot only when the adapter defines an explicit durable path

## Premortem

If `weekly` borrows too much from `gstack` without a portability filter, the
likely failure modes are:

- host-specific state leaks into the public skill
- the retro pretends to have metrics it does not really have
- outputs become too long to be used in normal repos
- persistence becomes ambiguous because the skill writes hidden files

## Portable Design Decisions

- `weekly` should prefer durable repo artifacts over live host state.
- `weekly` should name the current window and the evidence set it relied on.
- If a prior weekly retro exists under `output_dir`, compare against it.
- If no prior weekly retro exists, say "First weekly retro recorded" or
  equivalent instead of inventing a trend.
- If `metrics_commands` are missing or weak, the retro may stay narrative-only,
  but it must say so explicitly.
- A machine-readable weekly snapshot is allowed only when the adapter gives an
  explicit `snapshot_path`.

## What Not To Copy

- session-dir or live-state orchestration
- telemetry and usage logging
- host-specific prompt injection or startup hooks
- giant global dashboards that require non-portable infrastructure
