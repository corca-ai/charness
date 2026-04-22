# Install And Update

CLI install/update UX is a product contract, not an afterthought.

Prefer:

- one canonical bootstrap path
- one canonical source of truth for installed state
- one documented update command
- one honest story for what the installer owns vs what the operator or host
  package manager still owns

When the product ships skills or plugins into a host, separate at least three
surfaces:

- source checkout or packaging manifest
- runtime binary actually executing `install` or `update`
- host-visible installed copy

Do not assume these move together just because the checkout version changed.

Be explicit about what the CLI can and cannot automate.

- If the host or package manager owns the final activation step, say so.
- If install or update may take noticeable time, surface phase progress so the
  operator can see which step is running before the command finishes.
- If update depends on the original install method, persist that fact or leave
  enough structured guidance for the next agent.
- If the runtime binary may lag the checkout, expose runtime capability through
  the command surface itself, such as new `--help` flags, JSON fields, or
  structured provenance, instead of inferring from source version alone.
- If a CLI can probe upstream releases or package metadata, do it to improve
  guidance, but do not claim mutation happened when it did not.
- If an installer script exists, prefer making it install only the product
  itself. Missing system prerequisites should fail with precise guidance rather
  than mutating host package managers on the operator's behalf.
- If an agent will run the bootstrap, keep the contract pasteable inside the
  entrypoint docs instead of requiring a remote documentation fetch as the
  first move.

Use the same install method for updates unless the product owns a safer
self-update path.

Host-visible plugin or skill propagation note:

- if the CLI owns plugin export or refresh, report whether that refresh was
  attempted and what surface it touched
- if the host still owns the last refresh step, classify it honestly as
  restart-only, re-enable, reinstall, or unclear
- keep standing local tests for deterministic source/runtime seams, and move
  host-interactive proof into explicit on-demand validation when that is the
  cheaper honest bar

Product-owned aggregate update note:

- if the product needs one operator command that refreshes both the product
  binary and tracked repo-local runtime surfaces, keep that command in product
  vocabulary, for example `product update all`
- make plain `update` vs aggregate `update all` semantics explicit so operators
  can tell whether they are refreshing only the product itself or also tracked
  external binaries, bundled skills, or generated local surfaces
- prefer aggregating existing honest subflows over inventing a second mutation
  engine; the aggregate path should reuse the same detect, doctor, and
  machine-readable state contracts
- if some tracked dependencies are manual-only, the aggregate command should
  preserve that honesty and report `manual` guidance instead of pretending the
  whole fan-out updated successfully
- if the aggregate flow refreshes repo-local materialized skills or plugins,
  report which tracked surfaces were refreshed and which were skipped

Wording boundary note:

- end-user docs and help text should stay in product vocabulary even when the
  implementation internally reuses harness helpers or shared lifecycle code
- do not leak internal platform names into the user-facing command surface
  unless the product is intentionally exposing them as a first-class operator
  concept

User-scoped registry note:

- when the product wants an opt-in list of repos or local surfaces to refresh,
  prefer an explicit user-scoped managed-install registry over machine-wide
  scanning
- record only installs the product explicitly manages
- make stale-entry cleanup and per-repo targeting possible
- keep the registry semantics product-owned; the shared pattern is the contract,
  not one hardcoded filename

Materialized install surface ownership note:

- when install or update lands exactly one host-visible copy, prefer one
  canonical target path plus direct proof over a registry or manifest layer
- add a registry or manifest only when the product intentionally manages
  multiple install targets and refresh, cleanup, or provenance cannot be
  recovered safely from one canonical target
- keep cleanup responsibility aligned with install responsibility: the product
  should clean up the targets or registry entries it creates, and it should not
  pretend to own uninstall of host-managed copies
- keep compatibility shims, migration aliases, and helper symlink layouts as
  implementation detail unless an operator must choose, repair, or verify them

Example boundary:

- one plugin export path or one installed binary path: model that as the
  canonical target and report whether it was refreshed
- multiple managed repo-local checkouts, plugin copies, or install channels:
  make the registry or manifest decision explicit and expose stale-entry
  cleanup honestly

Version provenance note:

- when update guidance depends on how the tool was installed, persist current
  version and install provenance in user-scoped state
- if the runtime probes for newer releases automatically, keep that check
  interactive-only, cached, non-fatal, and opt-out
- a 24 hour TTL is a strong default for latest-release cache reuse
- skip automatic checks in CI, non-TTY runs, obvious source-checkout paths, and
  other contexts where the operator did not ask for networked advice
- when provenance is unknown, degrade to honest manual guidance instead of
  guessing release-installer or package-manager commands

Authenticated upstream release probe note:

- when a GitHub-hosted upstream release probe is useful, prefer an already
  authenticated provider path such as `gh api` before public HTTP
- if `gh` is unavailable, attach `GH_TOKEN` or `GITHUB_TOKEN` to the HTTP
  fallback when present
- keep public unauthenticated HTTP as a final fallback only
- persist structured `status`, `reason`, and `error` fields so later agents can
  distinguish `no-release`, `github-forbidden`, invalid JSON, and network
  failure without rediscovering the machine state
- do not make `gh` a hard dependency for non-GitHub repos or machines that only
  need public metadata

Release-first note:

- A release-first contract can be more honest than a package-manager-first
  contract while the runtime, artifact shape, or porting target is still
  moving.
