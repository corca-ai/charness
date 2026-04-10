# Retro Modes

`retro` is one public skill with two modes.

## `session`

Use for:

- the work that just finished
- a single task, implementation pass, bug investigation, or review cycle
- handoff-quality reflection after a meaningful unit of work

Evidence bias:

- current conversation
- changed files
- recent commands, commits, or artifacts tied to the task

Adapter policy:

- adapter missing is non-blocking
- metrics are optional and usually unnecessary

## `weekly`

Use for:

- this week
- the recent sprint window
- repeated work patterns across several tasks or sessions

Evidence bias:

- durable artifacts under `output_dir`
- the most recent weekly retro in `output_dir` when it exists
- adapter `evidence_paths`
- adapter `metrics_commands`

Adapter policy:

- adapter is strongly preferred
- if metrics are missing, say the weekly retro is narrative-only
- if no prior weekly retro exists, say the trend baseline is missing instead of
  implying one
- if `snapshot_path` is configured, persist a compact weekly snapshot there

## Auto Selection

Use this order:

1. explicit user wording
2. strong contextual signal from the current request
3. adapter `default_mode` only when the first two are still ambiguous
4. fallback to `session`
