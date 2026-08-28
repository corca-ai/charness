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

## Derived raw-glob exclusion

The declared-surface arm remains owned by `match_surfaces`. For the separate
raw-glob arm, the helper first finds positive candidate hits with the adapter's
`real_host_required_path_globs`, then asks the native topology owner to classify
those candidates in one call:

```text
repograph classify --surfaces-optional --repo-root <repo-root> --path <hit>...
```

The optional flag is important for consumer repositories: a missing
`<repo-root>/.agents/surfaces.json` is reported as `surfaces: absent`, while an existing
invalid manifest still produces an unestablished report. A candidate is
excluded only when its role is exactly `test`. `production`, `doc`, `generated`,
`unestablished`, and `unestablished-absent` remain positive hits. This is
fail-safe because `generated` membership is manifest-configured; dropping it
would let a surfaces-manifest edit silently remove a release-relevant
generated-mirror hit.

Role ownership is the topology layer: built-in language conventions and the
consumer's optional `<repo-root>/.agents/topology.json` declaration, with
derived-surface membership supplied by `<repo-root>/.agents/surfaces.json`.
Resolution precedence is:

| precedence | role owner | examples |
| --- | --- | --- |
| 1 | consumer topology declaration | `test_globs`, `production_globs`, or `generated_globs` |
| 2 | derived-surface membership | a path in a surface's `derived_paths` is `generated` |
| 3 | built-in language conventions | `tests/**`, `test_*.py`, `*_test.go`, `testdata/**`, `__tests__/**`, and JS/TS `*.test.*` or `*.spec.*` |
| 4 | built-in file/package rules | Markdown is `doc`; a package member is `production` |
| 5 | typed fallback | paths with no applicable rule are `unestablished` (deleted paths may be `unestablished-absent`) |

A consumer may declare its own topology without adding release-adapter keys:

```json
{
  "topology": {
    "test_globs": ["specimens/**"],
    "production_globs": ["cmd/**"],
    "generated_globs": ["build/**"]
  }
}
```

Native resolution or report parsing can be unavailable. In that case the fold
keeps every raw-glob candidate and records the typed degradation:

```yaml
test_exclusion:
  status: unavailable
  native_core:
    status: unavailable
    reason: <resolver or report failure>
```

This over-triggers rather than creating a false negative. Exit 0 and exit 3
reports from `classify` are both consumed because exit 3 can still carry the
per-path report. A zero-candidate raw-glob arm makes no native call and does
not degrade; its evaluated payload records
`test_exclusion: {status: applied, native_core: not-needed}` so every evaluated
payload has the same exclusion key.

### Payload keys by evaluation scope

The existing four-state vocabulary and the absent-`required` rule remain
unchanged. Only `evaluated` gains derived-exclusion keys:

| `evaluation_scope` | payload contract |
| --- | --- |
| `evaluated` | Existing `required`, `changed_paths`, `surface_hits`, `path_hits`, `checklist`, and `reason`, plus `excluded_path_hits: [{path, role}]` and `test_exclusion`. `path_hits` is post-exclusion and still drives `required == bool(surface_hits or path_hits)`. |
| `not-configured` | Existing payload only, including `required: false`; no `excluded_path_hits` or `test_exclusion`. |
| `empty` | Existing payload only; `required` remains absent and no derived-exclusion keys are added. |
| `not-established` | Existing broken-configuration or surface-error payload only; no derived-exclusion keys are added and the existing exit-1 behavior is unchanged. |

The release adapter continues to declare only positive host-proof triggers.
Negative syntax for test paths and any new adapter key are deliberately not
part of this contract.
