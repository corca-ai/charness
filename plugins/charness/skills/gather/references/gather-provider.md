# Gather Provider

The `gather` skill resolves a per-source provider mode from the adapter
before invoking any provider CLI, token-backed integration, or support
skill. The body never assumes a specific provider binary or auth env is
agent-reachable; the adapter selects which path the agent may take.

## Adapter Field

Set `gather_provider` in `.agents/gather-adapter.yaml`:

```yaml
version: 1
gather_provider:
  github:
    mode: direct-cli
  google_workspace:
    mode: direct-cli
  slack:
    mode: none        # credentialless default; set host-mediated or direct-cli to enable
  notion:
    mode: none        # credentialless default; set host-mediated or direct-cli to enable
```

`mode` accepts:

- `direct-cli`: use the maintainer-local CLI or checked-in support runtime when
  one exists (`gh`, Slack, Notion). This is the default only for `github`
  (standard dev tooling); Google Workspace intentionally has no repo-owned
  direct CLI provider.
- `host-mediated`: the host advertises a `<provider>` capability command;
  the skill instructs the agent to use the host's shape rather than
  invoking the direct CLI/token path.
- `none`: the source is unavailable in this runtime. The skill stops with
  a missing-capability explanation instead of attempting a fallback.

Plain gather is credentialless by default: the credentialed org providers that
ship a charness-owned wrapper (`slack`, `notion`) default to `none`, so an
installed skill never advertises a provider CLI route until a repo adapter opts
in. Enable a credentialed provider by declaring `host-mediated` (route through
the runtime's own capability) or `direct-cli` (only when the maintainer owns the
grant).

## Sources

- `github` — gather from GitHub content
- `google_workspace` — gather from Google Docs/Drive/Sheets
- `slack` — gather from Slack threads (consumed via the `gather-slack`
  support skill when mode is `direct-cli`)
- `notion` — gather from Notion pages (consumed via the `gather-notion`
  support skill when mode is `direct-cli`)

Unknown source names are rejected by the adapter parser. Modes that the
host does not expose should be declared `none` so the skill never reaches
for a direct CLI under a worker runtime.

## Runtime Consumption

- `scripts/advise_slack_path.py` reads `gather_provider.slack.mode`. When the
  mode is `direct-cli`, it points at the checked-in `gather-slack` support
  wrapper and runtime contract before browser-mediated or unrelated
  private-source fallbacks. When the mode is `host-mediated` or `none`, it
  returns the corresponding operator prompt without invoking the wrapper.
- `scripts/advise_google_workspace_path.py` reads
  `gather_provider.google_workspace.mode`. The script returns host-mediated,
  none, or missing-direct-provider guidance without invoking a local Google
  Workspace CLI.
- Support skills (`gather-slack`, `gather-notion`) are only invoked by the
  public `gather` skill when the matching `gather_provider.<source>.mode`
  is `direct-cli`. Under `host-mediated` or `none`, the gather body
  instead names the missing or host-routed capability.
- The `support/web-fetch` routing table treats `github.com` per
  `gather_provider.github.mode` — direct `gh` is only the right path when
  the adapter selected `direct-cli`.

## Why Adapter-Driven

Plain gather stays credentialless by default so an installed skill never
teaches agents to reach for a credentialed provider CLI a consuming runtime did
not authorize. A maintainer-local repo that owns the grants opts into
`direct-cli` for `slack`/`notion` in its own adapter; a worker-runtime host that
gates provider access behind a capability surface (such as `acme github`)
declares the relevant sources as `host-mediated`. Either way the credentialed
route is a repo-declared opt-in, and the same skill body works across host modes
without baking host-specific identifiers into charness.

## Adapter Slot Boundary

`gather_provider.<source>.mode` is a per-source read-mode enum
(`direct-cli`/`host-mediated`/`none`). It is intentionally a different
shape from the write-action backend slots used by other skills (`issue`'s
`issue_backend` and `release`'s `release_backend`), which are
`{id, binary, commands}` descriptors that name the executable and the
commands the skill is allowed to invoke. The same host capability — for
example `acme github` — can be declared in both shapes without drifting
because each slot answers a different question: gather asks "which read
path is reachable for this source?", while issue/release ask "which
binary and commands run the write action?". Do not collapse them into one
slot; cross-skill consistency comes from each shape staying honest about
what its consumer actually needs to know.
