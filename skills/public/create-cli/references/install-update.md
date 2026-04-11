# Install And Update

CLI install/update UX is a product contract, not an afterthought.

Prefer:

- one canonical bootstrap path
- one canonical source of truth for installed state
- one documented update command

Be explicit about what the CLI can and cannot automate.

- If the host or package manager owns the final activation step, say so.
- If update depends on the original install method, persist that fact or leave
  enough structured guidance for the next agent.
- If a CLI can probe upstream releases or package metadata, do it to improve
  guidance, but do not claim mutation happened when it did not.

Homebrew note:

- Homebrew is officially supported on Linux.
- The supported Linux install path uses `/home/linuxbrew/.linuxbrew` and then
  adds `brew` to `PATH`.
- Treat Linuxbrew as Homebrew on Linux, not a separate product boundary.

Use the same install method for updates unless the product owns a safer
self-update path.
