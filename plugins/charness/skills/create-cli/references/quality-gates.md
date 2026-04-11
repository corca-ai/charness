# Quality Gates

A repo-owned CLI should usually have:

- parser smoke tests for representative commands
- JSON-shape tests when agents consume the output
- file-mutation tests for install/update/reset commands
- validation for any persisted lock or manifest schema
- cheap syntax smoke such as `py_compile` for Python entrypoints

When the CLI owns lifecycle state, test both:

- happy path
- degraded or manual path

Quality review should ask:

- does `doctor` stay read-only
- does `update` report drift honestly
- does the CLI keep one source of truth for installed state
- can a later agent tell what changed without re-running everything
