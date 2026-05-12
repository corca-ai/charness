# Support Skills

`skills/support/` is for harness-owned tool-usage guidance, not public workflow
concepts.

## Current Layout

- local harness-owned support skills, for example provider runtime that public
  skills consume under the hood
- colocated capability metadata at `skills/support/<skill-id>/capability.json`
  when `charness` owns the runtime surface
Checked-in plugin exports flatten public skills for host discovery and copy
Charness-owned support assets into `<repo-root>/plugins/charness/support/`.
Upstream-consumed support skills are not checked into this source tree or the
checked-in plugin tree; they are materialized into the installed plugin under
`support/<tool-id>/` during `charness init`, `charness update`, or
`charness tool sync-support`.

## Rules

- do not put public workflow concepts here
- keep the public surface stable even when support/runtime lives here
- prefer upstream consumption plus manifests when the external repo already
  ships a usable support surface
- generated wrappers or references should be regenerated through
  [`scripts/sync_support.py`](../../scripts/sync_support.py) instead of edited by hand
