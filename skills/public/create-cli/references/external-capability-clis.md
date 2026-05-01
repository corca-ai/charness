# External Capability CLIs

Use this when a repo-owned CLI is called by agents and may read from or request
writes to a third-party system such as Notion, Linear, GitHub, Google Drive, or
Slack.

Keep these boundaries explicit:

- model the target registry or alias contract separately from credentials
- expose read-only preflight states such as `ready`, `missing_setup`, and
  `needs_credentials`
- keep real tokens, raw requests, and provider sessions host-side; the worker
  CLI requests capability instead of receiving credentials
- require operation-specific scopes such as `allowed_methods`,
  `allowed_path_prefixes`, and host allowlists before execution
- distinguish preflight/audit events from host-executor events so a dry slice
  does not overclaim real external execution

Audit-safe output should be designed before implementation. Prefer counts,
lengths, redacted hints, stable aliases, and idempotency keys. Do not print raw
query text, raw request bodies, secrets, full external identifiers, or provider
reason strings that may contain sensitive content.

Quality gates should prove:

- preflight-only slices return `missing_setup` or `needs_credentials` without
  touching the external provider
- stdout, JSON payloads, bridge logs, and debug logs redact sensitive fields
- docs name the host-only executor boundary and do not imply the worker CLI owns
  credentials
- provider API-version drift was checked before freezing public nouns, payload
  fields, or status names
