# Version Provenance And Cached Update Checks

When a CLI's update guidance depends on install channel, version provenance is
part of the product contract.

Prefer:

- user-scoped durable state for current version, install provenance, and the
  last successful latest-version check
- one explicit inspection surface such as `version --verbose` or `doctor`
- one clear opt-out knob for automatic checks

Automatic checks can improve operator ergonomics, but only when they stay
honest.

- run them only for interactive usage
- skip them in CI, non-TTY runs, obvious source-checkout paths, and unknown
  version states
- cache latest-version results instead of probing on every invocation
- 24 hours is a strong default TTL
- failures must never fail the main command
- update notices should reuse recorded install provenance when suggesting the
  next command

Do not:

- add network traffic to automation by default
- pretend the runtime knows whether the operator used Homebrew, npm, or a raw
  release install when it does not
- hide provenance or cache state in a temp directory that later agents cannot
  inspect
