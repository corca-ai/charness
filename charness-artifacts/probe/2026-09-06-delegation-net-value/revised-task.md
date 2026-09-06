# Delegated Catalog change — revision 2

Complete `src.catalog.Catalog` with `Catalog(mapping, aliases=None)`, where
aliases is an ordered list of `(alias, target_name)` pairs. This revision
supersedes revision 1 where they conflict.

Canonical lookup and unknown-name `KeyError` remain compatible. An alias resolves
to the same value as its terminal canonical target. Alias-to-alias chains are now
required, including forward references. Add `canonical_key(name)`: canonical
input returns itself; an alias returns its terminal canonical key; unknown input
raises `KeyError`.

Validate in two stages. First scan all declarations in input order, rejecting
canonical-name collisions or duplicate alias names with `ValueError` containing
that invalid alias name. Only after structural checks succeed, resolve each
declared alias in input order. A cycle or missing terminal target raises
`ValueError` containing the initiating alias name for the first failed chain,
not merely the repeated or missing target. Thus an early dangling chain does not
hide a later duplicate declaration. Self-cycles are invalid. Unused canonical
keys are valid. Never mutate the caller's mapping or alias list. Names are
nonempty strings; malformed pair shapes or other name types are outside scope.
No third-party dependencies.

Own this task through completion: reconcile the durable design with this current
revision, implement, test both preserved and new behavior, and leave an honest
completion/checkpoint record. Keep existing baseline tests intact; additions
are allowed. This file is authoritative and may not be edited.
