# Impl phase: build the exact repoctl contract

Work in the same consumer repository after the create-cli context. Read
`AGENTS.md` and use the installed `impl` skill identified by
`CHARNESS_FIXTURE_PLUGIN_ROOT`. Resolve its references from the exported
package, not host-installed Charness, and report the exact consumed skill path
and package version.

Consume the exact command contract recorded by the preceding `create-cli`
context in `README.md`. Treat it as the implementation contract; do not
redesign the command names, relax parser refusal rules, or drop the legacy
script path. If the handoff is absent or ambiguous, report that instead of
guessing.

Carry the requested build through now. Add an executable standard-library-only
repository-root `repoctl` with `refresh`, `doctor`, and `version`, explicit
`--json` structured output, concise help, read-only help/doctor/dry-run paths,
exact `.state/cache.json` refresh behavior, and pre-write rejection of unknown,
duplicate, missing, and option-looking inputs. Preserve and test the old
`python3 scripts/refresh_cache.py SOURCE` invocation. Update
`tests/test_current_scripts.py` with minimal meaningful checks and keep the
README concise.

Run the full dependency-free fixture command from the consumer root:

```text
python3 -m unittest discover -s tests -v
```

Do not add an evaluator, registry/runner integration, copied plugin/skills, or
unrelated repository changes.
