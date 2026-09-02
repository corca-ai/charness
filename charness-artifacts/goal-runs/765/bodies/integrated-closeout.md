<!-- charness-work-item-key: integrated-closeout -->

## Objective

Prove the composition once and close the parent through its guarded readback path.

## Owned scope

- Clean consumer install from the exported plugin on a throwaway repository: `charness doctor`, `charness update`, and a `quality` run complete without referencing any `tools/` file. Recorded by the operator or a task run, not asserted from the source checkout.
- Release lane (`run-quality.sh --release`) green on the integrated tree with the skip list read.
- Distinct-observer review of the export boundary and the gate classification, recorded.
- Parent Goal Run closed only through `issue_tool.py goal-run-close` after exact readback.

## Acceptance

- The live install proof artifact exists and names the export commit.
- Every child is provider-closed with behavioural evidence before the parent close is attempted.

## Dependencies

docs-as-code, gate-scope-repair, subprocess-retroactive-removal, quality-boundary-and-run-quality, scripts-packaging, rework-instrument.

## Non-claims

Push, tag, release publish, and installed-host mutation on the operator's machines remain separately authorised.
