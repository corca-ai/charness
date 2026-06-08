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
is a **required release-closeout step**, not optional hygiene. After publish
verifies, run `charness update` on this dev machine so the installed plugin at
`~/.agents/src/charness` stays `== repo`, then re-verify (`charness doctor` /
`python3 scripts/doctor.py --repo-root . --json` plus a cited-check == repo-gate
spot check) and record the `charness update` output as executed proof in
`charness-artifacts/release/latest.md`.

This closes the **installed-vs-repo version-skew class**. The motivating miss:
the `debug`/`critique` scaffolds cited the *installed* plugin's
`validate_debug_artifact.py`, which was looser than the repo's own, so a
scaffold-blessed artifact passed locally but failed the broad gate. Keeping the
installed surface `== repo` after every release stops the cited check from
drifting away from the gate. (The deeper root — scaffolds preferring the
repo-local `scripts/` validator when present — is fixed separately; this step is
the standing belt-and-suspenders.)

This step subsumes the previously open v0.27.0/v0.28.0 real-host smoke: it is
folded into the standing real-host checklist below rather than tracked as a
perpetually-open one-off.

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
