# Acceptance Checks

Acceptance checks connect the contract to verification.

## Rule

Every important success criterion should imply at least one acceptance check.

Good acceptance checks usually specify:

- verification type
- triggering condition
- expected behavior
- failure behavior when relevant

## Common Verification Types

- `manual`
- `unit`
- `integration`
- `e2e`
- `eval`
- `specdown`

Pick the lightest check that still proves the behavior honestly.

If the repo uses executable specs such as `specdown`:

- keep them at the acceptance boundary, not as a duplicate unit suite
- prefer direct adapters, check tables, or source-level guards before broad
  shell-driven commands
- name the expected scope and cost when one acceptance check is substantially
  slower than the rest of the bar

## Negative Cases

For important paths, include at least one negative case.

Examples:

- invalid input is rejected cleanly
- partial setup does not corrupt state
- retry or fallback behavior is reachable
- malformed model output is surfaced clearly

## Executable Promotion

If the repo already uses executable specs or acceptance-heavy tests:

- prefer turning important checks into executable artifacts
- keep the prose contract synchronized with those checks
- do not introduce a new executable framework unless the repo already wants it
- do not let executable-spec convenience hide repeated broad commands that
  should move down into unit tests or adapter-level checks
