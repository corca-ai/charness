# Recent Retro Lessons

## Current Focus

- Treat adjacent install surfaces as separate contracts, not as implied mirrors.
- Sync generated/plugin surfaces before packaging or closeout verification.
- Declare vendored-surface policy at intake time, not after standing validation fails.

## Repeat Traps

- Source checkout, managed checkout, installed CLI, checked-in plugin export, and host cache can drift independently.
- A lint/config change is incomplete until the checked-in plugin export has been regenerated.
- A gate exclusion only counts if it is wired into the command that actually gathers the file list.

## Latest Concrete Misses

- Running `run-quality` and `run-slice-closeout` in parallel corrupted the plugin export view and created false broken-import noise.
- Excluding vendored `specdown` docs in `.markdownlint-cli2.jsonc` was insufficient because `scripts/check-markdown.sh` decides the tracked file set first.
- Changing `scripts/check-markdown.sh` without resyncing the checked-in plugin export caused late packaging drift and managed-install test failures.

## Next-Time Checklist

- For install/update/support slices, check source checkout, managed checkout, installed CLI, plugin export, PATH visibility, and host cache separately.
- After editing any exported script or root marketplace artifact, run `python3 scripts/sync_root_plugin_manifests.py --repo-root .` before broad validation.
- Keep sync-producing commands out of parallel closeout/packaging runs.
- If a surface still needs human interpretation to know the next step, push that guidance into structured output before calling it done.

## Sources

- `skill-outputs/retro/weekly-2026-04-14.md`
- `skill-outputs/retro/weekly-latest.json`
- `docs/handoff.md`
