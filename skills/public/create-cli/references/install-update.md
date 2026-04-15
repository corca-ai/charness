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
- If update depends on the original install method, persist that fact or leave
  enough structured guidance for the next agent.
- If the runtime binary may lag the checkout, expose runtime capability through
  the command surface itself, such as new `--help` flags, JSON fields, or
  structured provenance, instead of inferring from source version alone.
- If a CLI can probe upstream releases or package metadata, do it to improve
  guidance, but do not claim mutation happened when it did not.
- If an installer script exists, prefer making it install only the product
  itself. Missing system prerequisites should fail with precise guidance rather
  than mutating `brew`, `apt`, `npm`, or other host package managers.

Homebrew note:

- Homebrew is officially supported on Linux.
- The supported Linux install path uses `/home/linuxbrew/.linuxbrew` and then
  adds `brew` to `PATH`.
- Treat Linuxbrew as Homebrew on Linux, not a separate product boundary.

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

Version provenance note:

- when update guidance depends on how the tool was installed, persist current
  version and install provenance in user-scoped state
- if the runtime probes for newer releases automatically, keep that check
  interactive-only, cached, non-fatal, and opt-out
- a 24 hour TTL is a strong default for latest-release cache reuse
- skip automatic checks in CI, non-TTY runs, obvious source-checkout paths, and
  other contexts where the operator did not ask for networked advice
- when provenance is unknown, degrade to honest manual guidance instead of
  guessing `brew`, `npm`, release-installer, or package-manager commands

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

- A release-first contract can be more honest than a Homebrew-first contract
  while the runtime, artifact shape, or porting target is still moving.
- Homebrew becomes cleaner after the product ships stable release artifacts
  instead of source-oriented bootstraps.
