# Impl phase: consume the alias-resolution spec

Work in the same consumer repository after the spec phase. Read `AGENTS.md`
and use the installed `impl` skill identified by
`CHARNESS_FIXTURE_PLUGIN_ROOT`. Resolve its references from the exported
package, not host-installed Charness, and report the exact consumed skill path
and package version.

Consume the exact `docs/alias-resolution.md` produced by the preceding spec
context. Treat it as the implementation contract: do not silently redesign
the API, loosen a rejection, or replace the list-of-pairs input with a dict.

Implement the requested slice in `src/catalog.py` and
`tests/test_catalog.py`. Preserve the original `Catalog(mapping)` canonical
lookup and existing tests, then add the spec's alias success and deterministic
rejection checks. Use only the standard library. Run:

```text
python3 -m unittest discover -s tests -v
```

Update the spec only if implementation exposes a real, previously unknown
constraint. If that happens, record the observed constraint in the spec before
continuing and report why the contract changed; otherwise leave the spec
untouched. Do not add an evaluator, copy a plugin/skills tree, or broaden the
fixture.
