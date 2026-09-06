# Consumer fixture instructions

This is a dependency-free consumer repository. Keep the baseline small and
run its tests with the standard-library command documented in `README.md`.

`CHARNESS_FIXTURE_PLUGIN_ROOT` identifies the canonical EXPORTED installed
package for this journey. Before using a Charness skill:

1. Read `$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/SKILL.md` for the spec
   phase and `$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/SKILL.md` for the
   implementation phase.
2. Resolve every reference named by those files from the corresponding
   `$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/<skill>/` directory. Do not use a
   source checkout or host-installed Charness as a substitute.
3. Report the exact consumed skill path and the package version. Read the
   version from `$CHARNESS_FIXTURE_PLUGIN_ROOT/.codex-plugin/plugin.json`, or
   from `.claude-plugin/plugin.json` when that is the installed host manifest;
   do not infer it from the host environment.

The seed is the baseline input. Do not put acceptance results, candidate
patches, or copied plugin/skills trees in it.
