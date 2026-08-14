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

## What Each Exit Code Means

`evaluation_scope` is always emitted and is the key to read first. The verdict key
`required` exists ONLY when the triggers were actually evaluated.

| `evaluation_scope` | exit | `required` | meaning |
| --- | --- | --- | --- |
| `evaluated` | 0 | present | triggers were compared against N > 0 changed paths |
| `not-configured` | 0 | `false` | this repo declares no triggers; nothing to evaluate |
| `empty` | 3 | absent | triggers are configured and the changed scope was EMPTY |
| `not-established` | 1 | `false`, on stderr | the trigger configuration could not be resolved |

Exit 3 is `run-quality.sh`'s `UNESTABLISHED_EXIT`. An empty changed scope is not
evidence that real-host proof is not required: hand the check the release's
changed paths (`--paths` or `--changed-range`) to get a verdict.

## Broken Trigger Configuration

Each `real_host_required_surfaces` entry must resolve to a declared
`<repo-root>/.agents/surfaces.json` `surface_id`. An unresolved id is broken configuration
and fails loud instead of silently reporting `required: false`.

Prefer surface ids for shared seams. Use path globs only for narrow
repo-specific exceptions.
