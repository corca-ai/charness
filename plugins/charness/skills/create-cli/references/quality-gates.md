# Quality Gates

A repo-owned CLI should usually have:

- parser smoke tests for representative commands
- `--help` smoke for stable public subcommands
- JSON-shape tests when agents consume the output
- JSON-shape tests for command discovery output when wrappers or agents probe
  the command registry
- file-mutation tests for install/update/reset commands
- validation for any persisted lock or manifest schema
- cheap syntax smoke such as `py_compile` for Python entrypoints

When the CLI owns lifecycle state, test both:

- happy path
- degraded or manual path

Quality review should ask:

- do stable public subcommands expose a no-side-effect `--help` contract
- is machine-readable command discovery distinct from help text when agents or
  wrappers need to probe the surface
- is binary health distinct from repo or install readiness
- if local plugin or skill discoverability matters, does it have its own
  readiness probe
- does `doctor` stay read-only
- does `update` report drift honestly
- does the CLI keep one source of truth for installed state
- can a later agent tell what changed without re-running everything
