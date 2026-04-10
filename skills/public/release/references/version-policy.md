# Version Policy

Use the lightest honest semantic-version bump that matches the user-visible
effect of the release surface.

## Patch

Use `patch` for:

- bug fixes
- validation or packaging repairs
- wording or metadata fixes that should propagate to installed users
- runtime corrections that preserve the same public shape

## Minor

Use `minor` for:

- new additive public skills or support capabilities
- new operator-facing commands, adapters, or install surfaces that do not
  break existing callers
- meaningful new behavior that existing users can adopt without migration

## Major

Use `major` for:

- renamed public skills or package ids
- changed invocation expectations that break existing automation
- removed or incompatible install surfaces
- forced migration steps for existing users

## Guardrail

If the bump level is debatable, say why. `release` should not silently turn a
human judgment call into a hidden default.
