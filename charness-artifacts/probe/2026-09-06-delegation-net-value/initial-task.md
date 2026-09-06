# Delegated Catalog change — revision 1

Extend `src.catalog.Catalog` with optional aliases supplied as an ordered list
of `(alias, canonical_name)` pairs: `Catalog(mapping, aliases=None)`.

Canonical lookup and unknown-name `KeyError` must remain compatible. An alias
resolves to the same value as its canonical target. Alias chains are forbidden
in this revision: every target must be a canonical mapping key. Reject a name
that collides with a canonical key, duplicate alias declarations, or a dangling
target with `ValueError` whose string contains the invalid alias name. Validate
pairs in input order and report the first invalid pair. Never mutate the caller's
mapping or alias list. Names are nonempty strings; handling malformed pair shapes
or other name types is outside scope. No third-party dependencies.

Own this task through completion, including current design documentation and
tests. Keep the existing baseline tests intact; add tests as needed. Use ordinary
repository files to preserve decisions and next actions across fresh contexts.
The authoritative task is this file; a later revision supersedes conflicting
earlier requirements. You may not edit this task file.

For this first context, produce the design and a useful durable checkpoint only.
Do not change source or tests yet. A second fresh context will continue from the
workspace and the then-current task. Do not assume conversation memory survives.
