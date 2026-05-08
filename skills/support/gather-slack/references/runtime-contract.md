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
- a Slack token resolved through one of:
  - a host-provided runtime grant (preferred)
  - `charness capability env <logical-id>` against the consumer repo's
    `<repo-root>/.charness/local/capability.json`, where `<logical-id>`
    defaults to `slack.default` and may be overridden via
    `CHARNESS_SLACK_CAPABILITY`
  - a pre-set `SLACK_BOT_TOKEN` in an operator-local CLI shell only — this
    path exists for human-driven debugging and is not advertised to
    model-controlled agent runtimes

The wrapper never reads `SLACK_BOT_TOKEN` from a `.env` file or an unbound
process env on the agent's behalf. If neither a grant nor a repo-local
capability binding produces a token, the wrapper stops with an explicit
missing-capability message instead of silently falling through to ambient env.

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
