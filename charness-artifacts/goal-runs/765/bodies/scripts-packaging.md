<!-- charness-work-item-key: scripts-packaging -->

## Objective

Organise `scripts/` into concept packages so a reader finds a script by what it owns, with every gate reporting the same universe before and after.

## Owned scope

- Add `scripts/__init__.py` and dotted-name support in `runtime_bootstrap.import_repo_module`.
- Move by concept: gates (check_/validate_, ~106), mutation (15), coverage (12), worktree (14), review (14), lessons (14), hooks (10), packaging (7), and the `_lib` core. One package per commit, with the universe-parity check from gate-scope-repair as the blocking check.
- Update `check_export_self_sufficiency.py` path strings and every `python3 scripts/<name>` carrier in SKILL.md, adapters, and hooks.
- Record that the 2026-08-07 critique's "scripts/ has no subdirectories" premise is invalidated as of this Work Item; do not edit the historical artifact.

## Acceptance

- Every gate's file set is identical before and after each package move.
- Clean export and installed-consumer import smoke green.
- No `scripts/<stdlib-name>.py` shadowing; `pyproject.toml` `pythonpath` comment updated or removed.

## Focused verification

Standing lane per package; release lane once at the end.

## Dependencies

quality-boundary-and-run-quality.

## Non-claims

No behaviour change in any moved script.
