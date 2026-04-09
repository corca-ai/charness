# Delivery Seams

Drafting and delivery are separate responsibilities.

`announcement` should always produce draft value first.

Delivery happens only after the user explicitly confirms.

## Supported Portable Delivery Shapes

### `none`

Draft only. No posting or file update.

### `release-notes`

Append or update a checked-in markdown file such as `docs/release-notes.md`.

### `command`

Run a repo-owned command template from the adapter.

Supported placeholders:

- `{message_file}`
- `{message_file_q}`
- `{delivery_target}`
- `{delivery_target_q}`

If a host wants a chat or SaaS backend, keep the public skill generic and route
through a repo-owned command seam.
