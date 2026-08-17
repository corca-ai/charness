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

The value is quoted verbatim as a blockquote, which makes it inert to the
line-anchored readers of that record. What quoting does not bound is refused at
argument time: `<script>`, `<style>`, `<textarea>`, the opaque legacy elements, and
an unterminated tag or comment. Those put every line below them inside something the
HTML parser does not read as markup, so the state ledger and the record's negative
sentences vanish from the document a reader sees while the bytes stay intact.
Angle-bracket placeholders like `<path>` and `<ref>` are accepted; so are `<details>`
and `<div>`, which the blockquote does bound. Both directions were measured against a
renderer rather than reasoned about.

**This flag was rejected once, on 2026-07-27, and that decision is superseded.**
The rejection read "the policy says 'say why', not 'add a CLI surface'", and
priced the flag at "a permanent surface plus a validator obligation to stop it
being filled with 'n/a'". Both halves of that price were paid, and the argument
that overturned it is that prose could not carry the sentence to the reader who
needs it: a later release's patch-vs-minor reasoning had to live in a separate
review artifact because the record's template emitted no field for it, and
re-running the helper could not add one. What the rejection got right is
unaddressed -- nothing stops a rationale reading "n/a", and no validator is
proposed for that. It is a human explanation judged by human readers.
