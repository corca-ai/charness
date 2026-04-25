# Gather Slack Provenance

This support runtime was informed by the Slack gather implementation in
`corca-ai/claude-plugins`, but `claude-plugins` is not the runtime owner for
`charness`.

The copied vendor helpers live in this package so consumer repos do not need to
install a second plugin or recreate Slack export scripts themselves.

Local adjustments from the reference implementation:

- the wrapper lives in `<repo-root>/scripts/export-thread.sh`
- credential discovery is reduced to process-environment input instead of
  scanning shell profile files
- the public `gather` skill remains the only user-facing concept
