# Probe Record: `<plugin-dir>/` placeholder live resolution (2026-08-04, moved from docs/deferred-decisions.md D50 on 2026-09-03)

- **Live probe, and its bounds.** Two `claude -p` runs against a temp tree holding
  only the installed-layout package: a fresh agent resolved
  `<plugin-dir>/skills/hitl/scripts/check_chunk_contract.py` to the correct
  concrete path and confirmed it exists, and the negative control correctly
  refused the `skills/public/...` spelling and diagnosed the stale kind segment.
  Notably the agent did not need the documented procedure — it inferred the
  plugin root from the tree shape. Bounds: one host (Claude Code 2.1.220), one
  model, two prompts, whole tree visible. **No host was observed to substitute
  `<plugin-dir>/` textually; the placeholder remains agent-resolved**, and that
  original non-claim stands.
