# Gather Slack Runtime Contract

This support package turns a Slack thread URL into a local markdown artifact.

## Inputs

- Slack thread URL:
  - `https://{workspace}.slack.com/archives/{channel_id}/p{timestamp}`
- output markdown path
- optional human-friendly title

## Runtime

- `node`
- `jq`
- `perl`
- `SLACK_BOT_TOKEN` in the process environment when the host does not provide a
  stronger mediated grant path
- if the runtime token name is repo- or workspace-specific, use
  `charness capability env slack.default` to alias the runtime env name from a
  machine-local source env name before invoking the wrapper

## Behavior

1. Parse the Slack thread URL into workspace, channel id, and canonical
   `thread_ts`.
2. Fetch the thread plus user metadata.
3. Download attachments next to the markdown artifact.
4. Convert the fetched JSON into readable markdown with source provenance.

## Degradation

- If runtime dependencies are missing, stop with an explicit install hint.
- If Slack private access is missing, stop cleanly and name the missing
  capability.
- If the bot is not in the target channel, attempt the normal join-and-retry
  path before failing.
