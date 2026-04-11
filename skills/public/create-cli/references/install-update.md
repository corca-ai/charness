# Install And Update

CLI install/update UX is a product contract, not an afterthought.

Prefer:

- one canonical bootstrap path
- one canonical source of truth for installed state
- one documented update command
- one honest story for what the installer owns vs what the operator or host
  package manager still owns

Be explicit about what the CLI can and cannot automate.

- If the host or package manager owns the final activation step, say so.
- If update depends on the original install method, persist that fact or leave
  enough structured guidance for the next agent.
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

Release-first note:

- A release-first contract can be more honest than a Homebrew-first contract
  while the runtime, artifact shape, or porting target is still moving.
- Homebrew becomes cleaner after the product ships stable release artifacts
  instead of source-oriented bootstraps.
