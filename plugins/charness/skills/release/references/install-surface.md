# Install Surface

For `charness`, release work is not complete when the packaging manifest alone
changes. The checked-in install surface and user update instructions must stay
aligned with the new version.

## Canonical Mutable Source

- [`packaging/charness.json`](../../../../packaging/charness.json)

## Generated Surfaces

- [`plugins/charness/.claude-plugin/plugin.json`](../../../../plugins/charness/.claude-plugin/plugin.json)
- [`plugins/charness/.codex-plugin/plugin.json`](../../../../plugins/charness/.codex-plugin/plugin.json)
- [`.claude-plugin/marketplace.json`](../../../../.claude-plugin/marketplace.json)
- [`.agents/plugins/marketplace.json`](../../../../.agents/plugins/marketplace.json)

## User Update Boundary

`release` should tell users how to refresh installed state, but it must not
edit host caches directly. Typical update steps remain CLI- or host-driven, for
example:

- run `charness update`
- restart Codex when host visibility still depends on marketplace rediscovery
- restart Claude Code when needed

If a repo treats a version bump as a published release boundary rather than a
private maintainer checkpoint, do not leave push, tag, and GitHub release as
separate ad hoc steps. Ship one repo-owned publish helper so maintainers do not
accidentally stop after bump+push and call the release done.

## Real-Host Proof

Some release claims should stay release-time human proof instead of standing CI.
This is especially true when the change touches:

- external tool onboarding or support sync
- install/update/reset flows that depend on host PATH, package managers, or
  host cache state
- support-backed tool readiness that a fixture can only approximate

When that seam moved, surface a short real-host checklist in the release
closeout instead of pretending repo-local tests replaced it.

The adapter can declare that checklist through:

- `real_host_required_surfaces`
- `real_host_required_path_globs`
- `real_host_checklist`

Use `scripts/check_real_host_proof.py` to decide whether the current slice hit
those seams.

## Drift Rule

If the generated surfaces disagree with the packaging manifest version, treat
that as release drift and repair it before closing the slice.
