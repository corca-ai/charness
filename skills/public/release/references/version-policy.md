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

Say it where the reader is. Pass the reason to the publish helper:

```bash
python3 "$SKILL_DIR/scripts/publish_release.py" --repo-root . --part patch \
  --bump-rationale "patch, not minor: the one feat is a validator repair, and no
registered public surface moved."
```

It is rendered into the release record's `## Bump Rationale` section, so an
outside reader gets it. Omit it and that section says so in as many words --
absence is recorded, not hidden. On `--resume` the payload is rebuilt from
arguments, so repeat the flag or the published record loses the rationale the
prepared one carried.
