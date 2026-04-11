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
- upstream release installer is the recommended bootstrap path
- Homebrew and `go install` are valid secondary paths, but consumer repos should
  not hardcode them unless they can prove provenance
- without a built-in self-update surface, consumer repos should avoid guessing
  how the operator originally installed it

`cautilus`

- release-first distribution with one checked-in `install.sh`
- installer is intentionally scoped to the product itself, not OS dependency
  managers
- future Homebrew support is deferred until the artifact/runtime surface settles

Design takeaway:

- the difference is not “brew or not”
- the difference is whether the tool exposes a trustworthy self-managed update
  seam or whether the host package manager remains the source of truth
- when the host package manager stays authoritative, agent-readable provenance
  should survive install and doctor flows so later updates can reuse that route
