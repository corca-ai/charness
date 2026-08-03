# Gather Provider

The `gather` skill resolves a per-source provider mode from the adapter before
routing a source. The body never assumes a specific provider binary or auth env
is agent-reachable; the adapter selects which path the agent may take.

Plain `gather` is **public-source only**. Credentialed organizational data —
Slack, Notion, private Google Workspace, Drive, or similar — is not a gather
source. It flows through the consuming runtime's own capability/connector
surface, never a charness-owned provider CLI or raw token route. When a gather
request names such a source, the skill hands it off to the runtime capability or
stops with a missing-capability explanation rather than reaching for a
credentialed provider path.

## Adapter Field

Set `gather_provider` in `<repo-root>/.agents/gather-adapter.yaml`:

```yaml
version: 1
gather_provider:
  github:
    mode: direct-cli
  google_workspace:
    mode: none        # public-only default; set host-mediated to route private content through a host capability
```

`mode` accepts:

- `direct-cli`: use standard dev tooling that reaches public content (`gh`).
  This is the default only for `github`.
- `host-mediated`: the host advertises a `<provider>` capability command;
  the skill instructs the agent to use the host's shape rather than
  invoking a direct CLI/token path.
- `none`: the source is not reachable as a public gather in this runtime. The
  skill stops with a missing-capability explanation instead of attempting a
  credentialed fallback.

## Sources

- `github` — gather from public GitHub content
- `google_workspace` — gather from Google Docs/Drive/Sheets. Has no repo-owned
  direct CLI: private content routes to a host-mediated capability, an operator
  export, or a browser-mediated fallback, never a checked-in provider token.

Unknown source names are rejected by the adapter parser. Credentialed org
providers (Slack, Notion, private Drive) are intentionally **not** valid gather
sources; declaring one is a parser error, because acquiring that data is the
consuming runtime's capability/connector responsibility, not gather's.

## Runtime Consumption

- `scripts/advise_google_workspace_path.py` reads
  `gather_provider.google_workspace.mode`. The script returns host-mediated,
  none, or missing-direct-provider guidance without invoking a local Google
  Workspace CLI.
- `gather_plan.py` detects a Slack URL and reports
  `credentialed_source_out_of_scope`: public-only gather does not acquire it;
  the runtime capability/connector owns credentialed org data. Google Workspace
  URLs route to the workspace path adviser.
- The `support/web-fetch` routing table treats `github.com` per
  `gather_provider.github.mode` — direct `gh` reaches public content when the
  adapter selected `direct-cli`.

## Why Adapter-Driven

Plain gather stays public-source only so an installed skill never teaches agents
to reach for a credentialed provider CLI or raw token a consuming runtime did
not authorize. A worker-runtime host that gates provider access behind a
capability surface (such as `acme github`) declares the relevant source as
`host-mediated`; the same skill body works across host modes without baking
host-specific identifiers into charness. Credentialed org data is out of gather's
scope entirely — the consuming runtime owns that boundary.

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
