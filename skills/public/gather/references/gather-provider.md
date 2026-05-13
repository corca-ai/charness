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
    mode: direct-cli
  notion:
    mode: direct-cli
```

`mode` accepts:

- `direct-cli` (default): use the maintainer-local CLI or token-backed
  integration (`gh`, `gws`, Slack bot token, Notion token). This matches
  prior behavior in maintainer-local repos.
- `host-mediated`: the host advertises a `<provider>` capability command;
  the skill instructs the agent to use the host's shape rather than
  invoking the direct CLI/token path.
- `none`: the source is unavailable in this runtime. The skill stops with
  a missing-capability explanation instead of attempting a fallback.

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

- `scripts/advise_google_workspace_path.py` reads
  `gather_provider.google_workspace.mode`. When the mode is `host-mediated`
  or `none`, the script returns the corresponding operator prompt without
  invoking `doctor` for `gws-cli`.
- Support skills (`gather-slack`, `gather-notion`) are only invoked by the
  public `gather` skill when the matching `gather_provider.<source>.mode`
  is `direct-cli`. Under `host-mediated` or `none`, the gather body
  instead names the missing or host-routed capability.
- The `support/web-fetch` routing table treats `github.com` per
  `gather_provider.github.mode` — direct `gh` is only the right path when
  the adapter selected `direct-cli`.

## Why Adapter-Driven

In maintainer-local repos the default `direct-cli` preserves the prior
authenticated `gh`/`gws`/Slack/Notion paths. In worker-runtime hosts that
gate provider access behind a host-mediated capability surface (such as
`ceal github`), the adapter declares the relevant sources as
`host-mediated` (or `none`) and the public `gather` skill stops teaching
agents to reach for a direct CLI or token. The same skill body works
across both host modes without baking host-specific identifiers into
charness.

## Adapter Slot Boundary

`gather_provider.<source>.mode` is a per-source read-mode enum
(`direct-cli`/`host-mediated`/`none`). It is intentionally a different
shape from the write-action backend slots used by other skills (`issue`'s
`issue_backend` and `release`'s `release_backend`), which are
`{id, binary, commands}` descriptors that name the executable and the
commands the skill is allowed to invoke. The same host capability — for
example `ceal github` — can be declared in both shapes without drifting
because each slot answers a different question: gather asks "which read
path is reachable for this source?", while issue/release ask "which
binary and commands run the write action?". Do not collapse them into one
slot; cross-skill consistency comes from each shape staying honest about
what its consumer actually needs to know.
