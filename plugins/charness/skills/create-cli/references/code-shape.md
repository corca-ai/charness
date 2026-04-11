# Code Shape

Boring code is usually better CLI code.

Prefer:

- stdlib parser first
- small command handlers
- shared helpers for repeated lifecycle logic
- explicit path resolvers and mutation helpers

Avoid:

- giant single-command handlers that mix parsing, filesystem mutation,
  subprocess execution, and rendering
- multiple copied branches for install/update/reset with tiny differences
- hidden global state that changes behavior depending on cwd without saying so

If a helper appears twice, factor it before a third use.
