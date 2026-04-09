# Integration Locks

`integrations/locks/*.json` is generated state.

Source policy still lives in [integrations/tools](/home/ubuntu/charness/integrations/tools).

## Purpose

Lock files record what one machine most recently observed or synced:

- detect and healthcheck results
- observed version text when available
- support capability state
- sync strategy and last sync timestamp
- last update attempt result

## Guardrails

- do not edit lock files by hand
- do not treat a lock file as portable source-of-truth policy
- do not require a host-specific path in the manifest just to make a lock file
  easier to write
