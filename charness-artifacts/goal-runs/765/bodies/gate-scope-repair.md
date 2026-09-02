<!-- charness-work-item-key: gate-scope-repair -->

## Objective

Make every gate's file universe survive subdirectories and cover shell files, and give the repo a file-level unreferenced-script check, before any file under `scripts/` moves.

## Owned scope

- Replace every single-star `scripts/*.py` glob (about 50, including `GATED_GLOBS` in `scripts/check_code_lengths.py`) with a recursive form. Record the before/after file set of each gate; a widened universe surfaces latent findings that are fixed or exempted by name, never landed silently.
- Add `.sh` to `check_code_lengths.py` with a cap and a seeded failing fixture. `scripts/run-quality.sh` at 1341 lines enters the gated universe as a named, dated exemption that slice 4 retires.
- Add a standing file-level unreferenced-script check: a reference graph over skills, adapters, hooks, presets, profiles, integrations, packaging, the CLI, `scripts/`, and `tests/`. Delete `scripts/atomic_write_lib.py` and `scripts/setup_markdown_section_lib.py` (referenced only by historical artifacts). Disposition the 12 tests-only scripts by name: keep with a consumer, move to tests, or delete.

## Acceptance

- For every glob-driven gate, `--list` (or equivalent) emits the identical sorted set before and after, plus `.sh` files for the length gate.
- A seeded oversize `.sh` and a seeded unreferenced `.py` each turn their gate red.
- The 2026-07-28 triage S40 failure (zero-file glob reads as pass) is impossible: a gate given an out-of-glob path reports the empty universe as a refusal.

## Focused verification

Standing pytest lane, `run-quality.sh` read-only lane, the per-gate universe diff recorded in the closeout.

## Dependencies

docs-as-code.

## Non-claims

No file moves. No gate deletion.
