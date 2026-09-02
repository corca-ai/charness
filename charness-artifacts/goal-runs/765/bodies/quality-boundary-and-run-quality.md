<!-- charness-work-item-key: quality-boundary-and-run-quality -->

## Objective

Make the `quality` skill export only what checks a consumer repo's health via gates and intelligence, move repo-only gates to a non-exported root `tools/` tree, and turn `run-quality.sh` into a declarative gate list with a thin runner.

## Owned scope

- Classify all 97 queued gates by one question: which consumer rework does this prevent? Each answer names the consumer failure mode or the repo failure mode. A fresh-eye reviewer reads the list before any move.
- Create root `tools/` for repo-only gates and dev tooling; the export rule becomes "everything under `scripts/` ships" and `SOURCE_ONLY_PLUGIN_SCRIPTS` is retired. The 32 quality-lane-only scripts are the first candidates.
- Replace the 1341-line `run-quality.sh` queue with a declarative gate list (label, command, lane, budget) and a thin runner; retire the dated `.sh` length exemption from gate-scope-repair.
- Re-scope `skills/public/quality/SKILL.md` and `.agents/quality-adapter.yaml` to the consumer definition.
- Changing the export boundary is authoring a proof surface: distinct-observer review recorded in a critique artifact, plus a clean-export probe.

## Acceptance

- A clean export contains no `tools/` file and no gate classified repo-only.
- Every gate still runs from its new home; one seeded failure per moved gate turns red.
- `run-quality.sh` length is under the `.sh` cap with no exemption.

## Focused verification

Read-only and release lanes green; `scripts/export_plugin.py` clean-export diff; critique artifact for the boundary.

## Dependencies

gate-scope-repair, subprocess-retroactive-removal.

## Non-claims

No gate deleted for being repo-only; repo-only gates move, they do not die. No redesign of what a consumer `quality` run proposes.
