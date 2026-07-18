# Real-Host Proof

Some release claims should stay release-time host proof instead of standing CI.
This is especially true when the change touches:

- external tool onboarding or support sync
- install, update, reset, or PATH-sensitive flows
- support-backed tool readiness that fixtures can only approximate
- host cache or package manager state

## Adapter Triggers

The adapter declares real-host proof through:

- `real_host_required_surfaces`
- `real_host_required_path_globs`
- `real_host_checklist`

Use the helper to decide whether the current release slice hit those seams:

```bash
python3 "$SKILL_DIR/scripts/check_real_host_proof.py" --repo-root . --detail
```

The helper is a trigger detector. It does not replace the host proof itself.
For a release delta, use the planner-emitted full-object-ID
`--changed-range BASE..HEAD` command. The helper owns path resolution and emits only compact
range provenance plus actual trigger hits; do not expand the range into a large
`--paths` argv or duplicate every changed path in the plan. Object IDs are
resolved by Git rather than assuming SHA-1 width, and the path digest uses Git's
NUL-delimited bytes so unusual filenames cannot make the evidence ambiguous.

## Broken Trigger Configuration

Each `real_host_required_surfaces` entry must resolve to a declared
`.agents/surfaces.json` `surface_id`. An unresolved id is broken configuration
and fails loud instead of silently reporting `required: false`.

Prefer surface ids for shared seams. Use path globs only for narrow
repo-specific exceptions.
