# Install Surface

For `charness`, release work is not complete when the packaging manifest alone
changes. The checked-in install surface and user update instructions must stay
aligned with the new version.

## Canonical Mutable Source

- `<repo-root>/packaging/charness.json`

## Generated Surfaces

- `<repo-root>/plugins/charness/.claude-plugin/plugin.json`
- `<repo-root>/plugins/charness/.codex-plugin/plugin.json`
- `<repo-root>/.claude-plugin/marketplace.json`
- `<repo-root>/.agents/plugins/marketplace.json`

## User Update Boundary

`release` should tell users how to refresh installed state, but it must not
edit host caches directly. Typical update steps remain CLI- or host-driven, for
example:

- run `charness update`
- restart Codex when host visibility still depends on marketplace rediscovery
- restart Claude Code when needed

If the repo adapter declares `update_instructions`, treat those as the
canonical operator-facing refresh path for already published installs instead of
guessing product-specific commands in the helper output.

If a repo treats a version bump as a published release boundary rather than a
private maintainer checkpoint, do not leave push, tag, and GitHub release as
separate ad hoc steps. Ship one repo-owned publish helper so maintainers do not
accidentally stop after bump+push and call the release done.

## Publication Closure Boundary

For repos with asynchronous publication, keep three states distinct:

- local/tag state complete
- workflow publication complete
- public release surface verified

If tag push only starts a later workflow, `release` should not call the release
complete at tag push alone.

If the real product boundary is an externally consumed GitHub release, package
index, tap, or similar public surface, the canonical closure point is
verification that the public surface is actually visible.

Bounded retry/backoff is normal here. Eventual consistency after a successful
workflow is not the same thing as flaky publication, and the closeout should
say whether the public surface was verified or is still pending.

## Real-Host Proof

Some release claims should stay release-time human proof instead of standing CI.
This is especially true when the change touches:

- external tool onboarding or support sync
- install/update/reset flows that depend on host PATH, package managers, or
  host cache state
- support-backed tool readiness that a fixture can only approximate

When that seam moved, surface a short real-host checklist in the release
closeout instead of pretending repo-local tests replaced it.

If the repo declares release-class `startup_probes`, use those as the startup
proof surface for launcher or packaging-sensitive changes. Keep those probes
distinct from standing local startup budgets.

The adapter can declare that checklist through:

- `real_host_required_surfaces`
- `real_host_required_path_globs`
- `real_host_checklist`

Use `<repo-root>/scripts/check_real_host_proof.py` to decide whether the current slice hit
those seams.

## Drift Rule

If the generated surfaces disagree with the packaging manifest version, treat
that as release drift and repair it before closing the slice.
