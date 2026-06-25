# Release Adapter Contract

`release` stays portable by loading repo-specific version and install-surface
seams from a repo adapter.

## Canonical Path

Use `<repo-root>/.agents/release-adapter.yaml` for new repos.

Search order:

1. `<repo-root>/.agents/release-adapter.yaml`
2. `<repo-root>/.codex/release-adapter.yaml`
3. `<repo-root>/.claude/release-adapter.yaml`
4. `<repo-root>/docs/release-adapter.yaml`
5. `<repo-root>/release-adapter.yaml`

## Shared Core

- `version`
- `repo`
- `language`
- `output_dir`
- `preset_id`
- `preset_version`
- `customized_from`

## Release Fields

- `package_id`
- `packaging_manifest_path`
- `checked_in_plugin_root`
- `sync_command`
- `quality_command`
- `update_instructions`
- `real_host_required_surfaces`
- `real_host_required_path_globs`
- `real_host_checklist`
- `requested_review_commands`
- `review_unavailable_patterns`
- `review_waiver_phrases`
- `product_surfaces`
- `cli_skill_surface_probe_commands`
- `cli_skill_surface_command_docs`
- `cli_skill_surface_skill_paths`
- `cli_skill_surface_change_globs`
- `fresh_checkout_probes`
- `release_backend`

## Defaults

- `language`: `en`
- `output_dir`: `<repo-root>/charness-artifacts/release`
- `package_id`: repo directory name
- `packaging_manifest_path`: `<repo-root>/packaging/<repo>.json`
- `checked_in_plugin_root`: `<repo-root>/plugins/<package_id>`
- `sync_command`: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `quality_command`: `<repo-root>/scripts/run-quality.sh`. Repos that gate
  release-time regression tests behind a pytest marker (e.g., `release_only`)
  should override this to include the marker — e.g.,
  `./scripts/run-quality.sh --release` — so publish covers update/install
  flow checks that standing pre-push intentionally skips.
- `update_instructions`: empty list
- `real_host_required_surfaces`: empty list
- `real_host_required_path_globs`: empty list
- `real_host_checklist`: empty list
- `requested_review_commands`: empty list
- `review_unavailable_patterns`: common release-record phrases such as
  `review unavailable`, `review gate unavailable`, and `executor_variants`
- `review_waiver_phrases`: `review waiver:`, `explicit review waiver:`, and
  `requested review waiver:`
- `product_surfaces`: empty list
- `cli_skill_surface_*`: empty lists
- `fresh_checkout_probes`: empty list

## Artifact Rule

The durable release artifact filename is fixed:

- `latest.md`

Dated release records should use `<repo-root>/charness-artifacts/release/YYYY-MM-DD-<slug>.md`.

`release` should treat the packaging manifest as the canonical mutable version
source. Generated plugin manifests and marketplace files are derived surfaces
and should be rewritten by the declared sync command, not edited by hand.

`update_instructions` should name the canonical operator-facing refresh path for
already published installs. Keep them evergreen: describe how to install the
latest published release, not what changed in one release. Put release-specific
behavior changes, migration notes, rollback advice, and rationale in release
notes or the generated release artifact. Avoid host-internal compatibility detail
unless operators truly need it to complete the update.

`real_host_checklist` is optional and exists for proofs that should stay
release-time and human-run rather than standing CI. Use it for support-tool or
install/update smokes on a second machine or clean temp-home, not for generic
repo validation already covered by `quality_command`.

`requested_review_commands` is optional and exists for release workflows where
the maintainer asks for a concrete review gate before publish. If any command
fails, `check_requested_review_gate.py` blocks publish/tag instead of treating
the missing review surface as a caveat. The same helper scans release records
for configured unavailable-review phrases; those records need a fix or an
explicit review waiver phrase before release.

`fresh_checkout_probes` is optional command data owned by the repo adapter.
Each entry is a bash shell string executed from the temporary clone root. Use
it for release evidence that can pass in a maintainer worktree but fail from a
fresh checkout because of clone depth, generated artifact determinism, or other
checkout-shape assumptions. `current_release.py` reports whether probes are
configured. `publish_release.py --execute` runs declared probes in a temporary
shallow fresh clone after the release commit is created and before tag push or
release creation, records passing status in the release artifact, and reruns
the probes against that amended release commit. A failing probe blocks publish.

When `product_surfaces` contains both `installable_cli` and `bundled_skill`,
release runs the CLI plus bundled-skill disclosure gate only for matching CLI,
skill, plugin, package, or install-surface changes. Use
`cli_skill_surface_probe_commands` to point at binary-owned help, registry,
catalog, example, version, install-smoke, doctor, or readiness probes. Keep
these probes local and deterministic; latest-release, network, or upstream
freshness checks belong in the release-specific proof that is intentionally
checking freshness. Use
`cli_skill_surface_skill_paths` when the shipped skill does not live under
`skills/public/*` or `skills/support/*`.

`release_backend` mirrors the `issue_backend` shape so release auth probes,
release-existence checks, and release-create calls can route through the
adapter-resolved CLI binary. Default is `{id: gh, binary: gh, commands: null}`,
which keeps the existing `gh release ...` shape. Hosts that resolve releases
through a different binary supply `commands` templates for `auth_check`,
`release_view` (uses `{tag}` substitution), and `release_create` (uses `{tag}`
and `{title}` substitution). Without commands, a non-`gh` backend errors at
runtime instead of falling back to `gh`.

The placeholder set is enforced per op at runtime by
`publish_release_helpers.backend_command`: `release_view` accepts `{tag}`,
`release_create` accepts `{tag}` and `{title}`, and `auth_check` accepts no
placeholders. An adapter template using an unknown placeholder fails fast with
the offending placeholder named, matching the issue-backend close-with-comment
pattern (`issue_close._resolve_op` per-op allowlist) so both backend surfaces
share the same hardening shape. Adding a new placeholder requires updating
`OP_PLACEHOLDERS` in `publish_release_helpers.py` plus the call site and a
regression test.
