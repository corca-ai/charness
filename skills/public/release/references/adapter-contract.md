# Release Adapter Contract

`release` stays portable by loading repo-specific version and install-surface
seams from a repo adapter.

## Canonical Path

Use `<repo-root>/.agents/release-adapter.yaml`.

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
- `materialized_plugin_root`
- `sync_command`
- `quality_command`
- `post_publish_install_refresh`
- `post_publish_version_readback`
- `post_publish_doctor_readback`
- `post_publish_distinct_channel_probe`
- `update_instructions`
- `requested_review_commands`
- `requested_review_policy`
- `review_unavailable_patterns`
- `review_waiver_phrases`
- `product_surfaces`
- `cli_skill_surface_probe_commands`
- `cli_skill_surface_command_docs`
- `cli_skill_surface_skill_paths`
- `cli_skill_surface_change_globs`
- `fresh_checkout_probes`
- `required_release_surfaces`
- `unpublished_release_surfaces`
- `require_derived_release_claims`
- `release_backend`
- `specialized_release_lanes`

## Executed fields

`sync_command` and `quality_command` are RUN by a subprocess; every other field in
this contract is READ. That split is why their defaults below are the one place a
placeholder would be wrong: a documentation placeholder in a read field is correct
and in an executed field is a broken command.

Both defaults name the AUTHORING repo's own tooling, so a consuming repo that never
wrote a release adapter inherits commands that cannot exist in its tree. Adapter
resolution warns when it can read the script path out of either value and that path
is missing, naming the field and whether the value was inferred or set. `bump_version`
goes further and REFUSES on a missing `sync_command` target before it writes the
version, because that command runs after the manifest is written and a failure there
would leave a bumped manifest with an unsynced plugin mirror.

The reader is narrow on purpose: it resolves only `python3 <relative-path>` and
`./<relative-path>` where the path uses `[A-Za-z0-9._/-]` and nothing else. Every other
shape is silent — a pipeline or chain in any spelling, a redirect, an env prefix, a
different interpreter, an interpreter option, a quoted, tilde, globbed or
brace-expanded path. Silence means it did not judge, not that the command is fine. Set
both fields to commands YOUR repo can run.

## Defaults

- `language`: `en`
- `output_dir`: `<repo-root>/charness-artifacts/release`
- `package_id`: repo directory name
- `packaging_manifest_path`: `<repo-root>/packaging/<repo>.json`
- `materialized_plugin_root`: `<repo-root>/plugins/<package_id>`
- `sync_command`: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `quality_command`: `<repo-root>/scripts/run-quality.sh`. Repos that gate
  release-time regression tests behind a pytest marker (e.g., `release_only`)
  should override this to include the marker — e.g.,
  `./scripts/run-quality.sh --release` — so publish covers update/install
  flow checks that standing pre-push intentionally skips.
  A repo may make one release's changed-line evidence an explicit non-claim with
  `./scripts/run-quality.sh --release --non-claim=release-changed-line-coverage`.
  This exact release-only label omits that lane rather than converting a failed
  verdict into success; all other release gates still run. Preserve the command
  in the tagged adapter and state the missing verdict in the release notes.
  When this repo-owned release command produces an established semantic receipt,
  the resume helper seals it to the exact clean HEAD/tree and materialized export.
  The child push may reuse that one-shot receipt for the pre-push broad lane; the
  close-keyword guard always runs, and any state drift falls back to the normal
  pre-push gate.
- `update_instructions`: empty list
- `requested_review_commands`: empty list
- `requested_review_policy`: `warn-if-unconfigured`
- `review_unavailable_patterns`: common release-record phrases such as
  `review unavailable`, `review gate unavailable`, and `executor_variants`
- `review_waiver_phrases`: `review waiver:`, `explicit review waiver:`, and
  `requested review waiver:`
- `specialized_release_lanes`: empty list. An optional list of mappings with
  `id`, `workflow`, `tag_pattern`, and `command` strings. A non-empty list is an
  explicit declaration that this repository's generic release route does not
  apply; the release planner reports the lane (or asks the operator to choose
  when several are declared) and does not execute its command. This is local
  declaration evidence only: hosted workflow state, tag triggers, and release
  approval remain outside this planner's claim.
- `product_surfaces`: empty list
- `cli_skill_surface_*`: empty lists
- `fresh_checkout_probes`: empty list
- `required_release_surfaces`: empty list. Names the generated release surfaces the
  repo asserts it publishes, so an ABSENT one becomes drift instead of reading like a
  matching one. Known names: `claude_plugin`, `codex_plugin`,
  `claude_marketplace_version`, `codex_marketplace_source_path`. The packaging
  manifest is NOT declarable — its absence is drift whether or not anyone declares it.
- `unpublished_release_surfaces`: empty list. The OPT-OUT channel, and deliberately not
  an overload of the field above: because `required_release_surfaces` means "these must
  exist", naming a surface you do not publish there makes it drift, so it cannot be the
  remedy for not publishing it. Name here the generated surfaces this repo does not
  ship. Same known names.
- `require_derived_release_claims`: `true`. Notes handed to publish via
  `--notes-file` must carry a generated derived-claim block that agrees with the tree
  being shipped, and their authored prose must not carry an ungrounded quantity.
  Generate and check with
  `python3 "$SKILL_DIR/scripts/generate_release_notes.py" --repo-root . --notes-file <notes.md> --sync|--check`.
  **The default is `true` on purpose, and the direction is the point.** A gate armed by
  an opt-IN line is disarmed by deleting that line with nothing red; defaulting to true
  inverts it, so deleting the key — or the whole adapter — RE-ARMS the gate and the only
  way to publish unguarded notes is to write the opt-out down where a reviewer sees it.
  Setting it `false` disarms BOTH arms: the derived-block requirement and prose
  containment. Two things it does not do: it never runs on the resume lane (the window
  between the prepared stop and the resume is closed to worktree changes, so a refusal
  there would have no legal remedy), and it is never reached by a `--generate-notes`
  publish, which supplies no notes file for it to read.

- **Absence is still never drift on its own.** A read-only `current_release` run never
  reddens a lane a consumer chose not to publish. What changed (D48) is that an absent
  surface named by NEITHER field makes `absence_corroboration` read `uncorroborated`,
  and `publish_release_preflight.release_surface_blocker` refuses the PUBLISH — the
  irreversible boundary — rather than letting a deleted declaration buy a silent green.
- A surface that is present but `unreadable` or missing its version IS drift without
  `required_release_surfaces`, because that is the state a failed sync leaves and a
  deleted declaration must not disarm it. It is still exemptable via
  `unpublished_release_surfaces`, and that matters more than it looks: the two
  marketplace surfaces are per-REPO files, not per-package, so a marketplace listing
  some other product parses fine, yields nothing for this package, and reads as
  `no-version` with nothing corrupt anywhere. `version` is likewise optional in an
  upstream plugin manifest.
- Honest residual: both fields are self-authored, and nothing checks that a declared
  surface is one the sync command actually produces. Deriving that from the sync channel
  was tried and withdrawn as unbuildable (the sync report names the plugin root as a directory, so two of the four surfaces never appear in it). The authoring repo's own D48 record of that is authoring-repo-internal and does not ship with this skill.

## Artifact Rule

The durable release artifact filename is fixed:

- `latest.md`

Dated release records should use `<repo-root>/charness-artifacts/release/YYYY-MM-DD-<slug>.md`.

### Drafted release notes filename

Release notes drafted ahead of publish must carry `notes` as a whole
`-`/`_`-delimited token in the filename, alongside the version:

- `<date>-<tag>-notes.md`
- `notes-<tag>.md` (the token may lead or trail)
- `<date>-<tag>-public-notes.md` (dash-separated version tokens are recognised)

This is the shape the pre-publish refusal looks for when it checks whether notes
were drafted for the target tag and something else is being published. A draft
that omits the token — `v1.2.3.md`, `<date>-<version>-release.md` — is INVISIBLE
to that arm, and publish will proceed with a generated body while the drafted
notes sit unshipped. That is the v2.11.0 escape, and the convention is the part
of it a filename can fix.

Deliberately narrow: the role word is matched as a whole token, not a substring,
and no other word is recognised. A wider match once made a dated
`<date>-<version>-release-record.md` read as drafted notes, and the refusal's
remedy asks the operator to rename or delete the file — advice that must never
point at durable evidence.

`release` should treat the packaging manifest as the canonical mutable version
source. Generated plugin manifests and marketplace files are derived surfaces
and should be rewritten by the declared sync command, not edited by hand.

`update_instructions` should name the canonical operator-facing refresh path for
already published installs. Keep them evergreen: describe how to install the
latest published release, not what changed in one release. Put release-specific
behavior changes, migration notes, rollback advice, and rationale in release
notes or the generated release artifact. Avoid host-internal compatibility detail
unless operators truly need it to complete the update.

`requested_review_commands` is optional and exists for release workflows where
the maintainer asks for a concrete review gate before publish. If any command
fails, `check_requested_review_gate.py` blocks publish/tag instead of treating
the missing review surface as a caveat. The same helper scans release records
for configured unavailable-review phrases; those records need a fix or an
explicit review waiver phrase before release.

`requested_review_policy` controls the empty-command posture. The default
`warn-if-unconfigured` keeps legacy repos noisy when no requested-review command
is wired. Repos that intentionally treat requested review as advisory declare
`advisory-only`; the checker then records `configuration_status: advisory_only`
without a warning. A configured command still blocks on failure under either
policy.

`fresh_checkout_probes` is optional command data owned by the repo adapter.
Each entry is a bash shell string executed from the temporary clone root. Use
it for release evidence that can pass in a maintainer worktree but fail from a
fresh checkout because of clone depth, generated artifact determinism, or other
checkout-shape assumptions.

`check_fresh_checkout_probes.py` reports `passed`/`blocked` (exit 0/1) only when
it actually ran the probes, which it does only under `--run-probes`. Declared but
not run is `not_established` at exit 3 (`run-quality.sh`'s `UNESTABLISHED_EXIT`),
carrying no `probe_results` key, because a listing is not a pass. A repo that
declares no probes is `not_configured` at exit 0 — a genuine opt-out that never
refuses. `current_release.py` embeds the listing, so its fresh-checkout block is
always `not_established` or `not_configured`, never a probe verdict.

`publish_release.py --execute` runs declared probes in a temporary
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

`release_backend` mirrors the `issue_backend` shape — with ONE measured exception, in the
position that matters most for a template author: a `release_backend` command template
**includes the binary as its first element**, and `backend_command` never reads
`release_backend.binary`. (`issue_backend` templates exclude it and the issue backend prepends
`issue_backend.binary`.) That difference is why the two rules are not one function, and it is
executed rather than argued in
`<authoring-repo>/tests/quality_gates/test_release_backend_agrees_with_the_owner.py`.

A template part containing a literal brace that is not a placeholder (a JSON payload, say)
is rendered through `str.format`, so double the braces (`{{"q":1}}`) or it fails fast.

Otherwise `release_backend` mirrors `issue_backend` so release auth probes,
release-existence checks, and release-create calls can route through the
adapter-resolved CLI binary. Default is `{id: gh, binary: gh, commands: null}`,
which keeps the existing `gh release ...` shape. Hosts that resolve releases
through a different binary supply `commands` templates for `auth_check`,
`release_view` (uses `{tag}` substitution), `release_create` (uses `{tag}` and
`{title}` substitution), and optionally `release_view_body` (uses `{tag}`).
Without commands, a non-`gh` backend errors at runtime instead of falling back
to `gh`.

`release_view_body` reads the PUBLISHED release body back so the post-create
notes audit can inspect it — the pre-publish audit only runs when a notes FILE
is supplied, so `--generate-notes` otherwise publishes a body nothing has seen.
It is the one op a backend may omit safely: it runs after the release exists,
its result is advisory, and a missing template is recorded as
`published_notes_audit: not-configured` rather than raising. Declaring it means
the audit actually inspects your published notes.

The placeholder set is enforced per op at runtime by
`publish_release_helpers.backend_command`: `release_view` accepts `{tag}`,
`release_create` accepts `{tag}` and `{title}`, and `auth_check` accepts no
placeholders. An adapter template using an unknown placeholder fails fast with
the offending placeholder named, matching the issue-backend close-with-comment
pattern (`issue_close._resolve_op` per-op allowlist) so both backend surfaces
share the same hardening shape. Adding a new placeholder requires updating
`OP_PLACEHOLDERS` in `publish_release_helpers.py` plus the call site and a
regression test.
