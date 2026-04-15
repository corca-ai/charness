# Recent Retro Lessons

## Current Focus

- The user challenged the prior aggregate-only coverage posture: every tracked control-plane file should have an immediate `80.0%` floor, and weak coverage should be fixed by simplifying production code before adding tests.

## Repeat Traps

- The previous slice accepted an "unfloored advisory" state that should have been treated as a structural gap once the coverage target set was known.
- The first instinct was to add inventory and scenarios; the better sequence was to delete duplication, enforce the floor, and use scenarios to cover remaining real branches.

## Next-Time Checklist

- workflow: when a quality target set is explicit, enforce floor completeness immediately instead of reporting an "unfloored" advisory state.
- capability: keep the ratio gate simple for now; revisit only if the `1.00` ceiling blocks valuable behavior tests.
- memory: next coverage work should start with `sync_support.py`, which is exactly on the `80.0%` floor.

## Sources

- `charness-artifacts/retro/2026-04-15-per-file-coverage-floor.md`
