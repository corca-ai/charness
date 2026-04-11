# Case Studies

Use nearby repos and tools as comparison points, not as cargo-cult templates.

`charness`

- thin lifecycle CLI around managed install state
- explicit `doctor`, `update`, and `reset`
- lock and generated-support artifacts for agent-readable continuation

`agent-browser`

- upstream CLI includes a built-in `upgrade` command
- this makes scripted update automation safer from a consumer repo

`specdown`

- upstream binary is installable through multiple host-controlled paths
- without a built-in self-update surface, consumer repos should avoid guessing
  how the operator originally installed it

Design takeaway:

- the difference is not “brew or not”
- the difference is whether the tool exposes a trustworthy self-managed update
  seam or whether the host package manager remains the source of truth
