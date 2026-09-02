<!-- charness-work-item-key: docs-as-code -->

## Objective

Restore `docs/` to a single current-state wiki that is treated like code, and make AGENTS.md and README serve their readers.

## Owned scope

- AGENTS.md already carries the four docs-as-code principles (commit `2360b7a6d`, operator-approved 2026-09-02). Expand `docs/documentation-principles.md` with the detail: reduce duplication, link related pages like a wiki, keep README a minimal user guide, keep AGENTS.md minimal and pointing at `docs/index.md`.
- Retire `docs/north-star-overhaul-roadmap.md` (complete since 2026-06-20), `docs/readme-proof.md` (cites README sections that no longer exist), and the six self-described working records (`testability-dsl-initiative.md`, `support-tool-followup.md`, `retro-self-improvement-spec.md`, `duplicate-detection-strategy.md`, `capability-resolution.md`, `ai-ml-engineering-patterns.md`) to `charness-artifacts/`. Fix `docs/index.md` and `docs/operator-acceptance.md`, which call the roadmap active.
- Add `Last verified` to every `docs/` page and make `scripts/check-docs.sh` refuse a page without it; prove with a seeded page.
- Keep the irreversible-boundary definition only in `docs/design-north-star.md`; replace the restatements in `docs/operating-contract.md` and `skills/public/impl/SKILL.md` with links.
- Fix the three dead script citations (`run_pre_push.py`, `tool.py`, `x.py`).
- Rewrite README as a user guide: supported hosts, prerequisites (Python 3, git, curl; gh for the issue skill), what install writes and how to undo it, the public skills and how they are invoked, what the first initialization prompt does. Link README from `docs/index.md`; no content duplicated with a `docs/` page.

## Acceptance

- `scripts/check-docs.sh` green, including the new rule, and a seeded page without `Last verified` turns it red.
- `docs/index.md` lists only current contracts, generated references, and README.
- Every inbound link to a moved page is updated; `check_export_self_sufficiency.py` green.

## Focused verification

`scripts/check-docs.sh`, `python3 scripts/check_export_self_sufficiency.py --repo-root .`, standing pytest lane with the skip list read.

## Dependencies

rework-instrument, goal-run-binding-simplification (order only; no code dependency).

## Non-claims

No script, test, or gate changes beyond `check-docs.sh`. No AGENTS.md change beyond the approved four principles.
