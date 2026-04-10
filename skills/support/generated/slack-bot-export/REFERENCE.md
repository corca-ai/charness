# slack-bot-export Support Reference

This generated reference records how `charness` consumes the upstream
support surface without copying it into the local taxonomy.

- upstream repo: `corca-ai/claude-plugins`
- upstream path: `plugins/cwf/skills/gather/SKILL.md`
- sync strategy: `reference`
- support state: `upstream-consumed`
- access modes: `grant, env, human-only, degraded`
- grant ids: `slack.conversations.history, slack.users.read, slack.files.read`
- env vars: `SLACK_BOT_TOKEN`
- permission scopes: `channels:history, channels:join, users:read, files:read`

## Config Layers

- `grant`: Prefer a runtime-granted Slack capability when the host can mediate access without exposing raw secrets.
- `env`: Fall back to `SLACK_BOT_TOKEN` for ordinary local operator setups.
- `operator-step`: The operator may still need to add the bot to the workspace or target channel before export succeeds.

## Reuse Notes

- Relevant upstream handlers: `plugins/cwf/skills/gather/scripts/slack-api.mjs` and `plugins/cwf/skills/gather/scripts/slack-to-md.sh`.
- See `plugins/cwf/skills/gather/references/slack-export.md` for token and scope requirements.

## Host Notes

- Current `charness` v1 sync materializes a support reference, not the upstream executable scripts themselves. Hosts still need an equivalent runtime path to execute Slack export.
- This manifest is transitional metadata only. The intended long-term model is `charness`-owned Slack gather provider runtime, not an external plugin runtime dependency.

Regenerate this file through `scripts/sync_support.py` instead of
editing it by hand.
