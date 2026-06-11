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

## Maintainer Dev-Machine Install Refresh

For `charness`, refreshing the maintainer/authoring machine's own installed copy
is a **required release-closeout step**, not optional hygiene — and it is now
**auto-run by the publish helper**, not a manual ask. The release adapter
declares `post_publish_install_refresh: charness update`; after publish verifies,
`publish_release.py` auto-runs that command on the authoring machine so the
installed plugin at `~/.agents/src/charness` ends `== repo`, and records the
result in the release payload under `install_refresh`
(`refreshed`/`failed`/`not_configured`). It is opt-in (a repo declaring no
command is skipped `not_configured`) and never aborts the already-published
release. The maintainer only re-verifies (`charness doctor` /
`python3 scripts/doctor.py --repo-root . --json` plus a cited-check == repo-gate
spot check) and steps in manually if `install_refresh` reports `failed`. The
refresh runs on both the normal and `--resume` publish paths; a hang is bounded
by the shared command timeout (recorded as `failed`), so it can never block the
already-published release.

This closes the **installed-vs-repo version-skew class**. The motivating miss:
the `debug`/`critique` scaffolds cited the *installed* plugin's
`validate_debug_artifact.py`, which was looser than the repo's own, so a
scaffold-blessed artifact passed locally but failed the broad gate. Keeping the
installed surface `== repo` after every release stops the cited check from
drifting away from the gate. (The deeper root — scaffolds preferring the
repo-local `scripts/` validator when present — is fixed separately; this step is
the standing belt-and-suspenders.)

This step subsumes prior one-off real-host smoke checks: they are folded into
the standing real-host checklist below rather than tracked as perpetually-open
release-specific tasks.

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

Each `real_host_required_surfaces` id must resolve to a declared `surface_id`
in `.agents/surfaces.json`; an unresolved id is a broken adapter contract and
the proof check exits non-zero with a `configuration_status: "broken"`
payload, not a silent `required: false`. Prefer surface ids for shared seams;
reserve `real_host_required_path_globs` for narrow repo-specific exceptions.
The charness-maintained authoring-repo-internal contract and the 4-fixture
shape every trigger consumer ships live at
`docs/conventions/surface-driven-adapter-triggers.md`.

## Drift Rule

If the generated surfaces disagree with the packaging manifest version, treat
that as release drift and repair it before closing the slice.
