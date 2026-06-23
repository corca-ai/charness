# Quality Follow-Up Closeout Critique

## Decision

Ship the follow-up slice after closeout validation.

This slice completes the remaining quality-track work before moving to other
skills:

- catalog/index drift validator
- reduced exact-prose test coupling on the changed quality surfaces
- gate health and cost review with a top-level read-only runtime budget

## Findings

Two bounded angle reviewers inspected the change.

Act-before-ship findings:

- The first validator draft compared only path sets. That would allow an index
  `On-Demand Review Detail` entry to be cataloged as `required-primer`, changing
  planner behavior by forcing every quality run to read a conditional reference.
  Fixed by making `validate_quality_reference_catalog.py` compare index section
  roles against catalog roles, with a negative role-mismatch test.
- The plugin mirror became stale after the role-aware validator edit. Fixed by
  rerunning `python3 scripts/sync_root_plugin_manifests.py --repo-root .` and
  revalidating packaging.

Bundle findings addressed:

- Added direct catalog validator and prose-pin commands to the quality review's
  command log.
- Added focused pytest proof to the same log.
- Added the symmetric catalog-only negative test.

## Counterweight

The counterweight reviewer found no remaining source-level blocker after the
role-aware validator fix. It explicitly rejected expanding this slice into
`parallel_group` scheduling or duplicate-entry enforcement.

## Deliberately Not Doing

- No executable scheduler for `parallel_group`. The field remains judgment
  metadata until a separate design proves applicability, env expansion,
  dependency ordering, and failure aggregation.
- No duplicate catalog/index entry validator. Duplicate entry handling is real
  but outside the drift class caught here.

## Floor-Addition Restraint

Floor-Addition Restraint: keep — recorded recurrence, cheap changed-scoped gate.

Call: keep.

`validate_quality_reference_catalog.py` is a new blocking floor, but it catches
a recorded recurrence from this work: human-visible quality references can be
absent from, or misclassified in, the executable planner catalog. The gate is
cheap, deterministic, changed-scoped to the quality reference/planner surface,
and pulled to commit-time for the same surface so authors see the verdict before
the broad gate.
