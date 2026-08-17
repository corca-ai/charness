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

Nothing in the value is refused for how it might render, and nothing is rewritten.
It is quoted verbatim as a blockquote, which makes it inert to every line-anchored
reader of the record, and the section is emitted LAST, so an unterminated construct
in it has nothing below to swallow. Position is the mechanism: a refusal that
enumerated hazardous HTML was tried three times and was wrong in both directions each
time, because it decided what a rendered document shows while nothing here can see a
renderer. Write `<path>`, `<details>` or a stray `<` freely.

One value is still refused: a release-state sentinel. Other surfaces prove release
state by substring-matching this record, so that one cannot be neutralised by position
or by quoting without changing what you wrote.

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
