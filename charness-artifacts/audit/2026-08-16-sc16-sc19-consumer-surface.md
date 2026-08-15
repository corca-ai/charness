# SC16 / SC19 Consumer-Surface Acceptance Record

Date: 2026-08-16

Owns the `manual + exported-surface` half of SC16 and SC19 in
[the 6.0.0 release scope](../spec/2026-08-15-6-0-0-release-scope.md). Written
because both criteria are typed `manual` in `## Acceptance Checks` and the only
evidence on the tree was executable — fixture tests proving the surface ships and
answers, which is not the same claim. A bounded reviewer named the gap during the
S7 critique; this record closes it by stating what was actually run, over what
tree, and what it does not establish.

## What SC16 asks

> The cost-dominance angle appears in the shipped critique surface, and a
> consuming repo running the quality skill is told when its prescribed test
> command sits outside its own budgeted universe.

## What SC19 asks

> A consuming repo gets the cost DIRECTION it currently lacks, not only the
> budget ledger.

## Executed, on this tree, at the commit that carries this file

| Command | Observed |
| --- | --- |
| `python3 skills/public/quality/scripts/inventory_command_dominance.py --repo-root .` | exit `0`; `registry_state: loaded` with the repo's one rule; the scan loop runs over a tree WITH findings |
| `python3 scripts/check_command_dominance.py --repo-root .` | exit `0`; `armed: true`, `scanned_sites` naming `cosmic-ray.toml:test-command` and the standing-gate surfaces |
| `python3 scripts/check_runtime_budget_universe.py --repo-root .` | exit `0`; both directions answered — a budgeted label with no command, and a queued or prescribed command with no budget |
| `grep -c cost-dominance plugins/charness/skills/critique/references/angle-selection.md` | non-zero; the angle is in the EXPORTED critique lineup, not only in this repo's prompts |
| Import of `plugins/charness/skills/quality/scripts/command_dominance_lib.py` in a fresh namespace | succeeds and answers `parse_registry` / `split_chunks`, so the exported family loads its own siblings |

## What this record does NOT establish

- **No consuming repo has run either surface.** Every row above executed in the
  authoring repo. The exported artifact is byte-identical to its source and it
  imports from the export path, which is strictly more than "the file is
  present" — and strictly less than a consumer observing the answer on their own
  tree. That remains unproven and is stated in the release notes' evidence
  limits.
- **SC19's consumer half is structurally narrower than its criterion text**, and
  this record does not repair that. The budget question is asked only of
  already-registered commands; queue labels resolve only for wrapper-shaped
  runners; the scanner recognises a fixed program list over a fixed set of
  surface kinds. A consumer whose expensive command is none of those gets a clean
  answer that means "not looked at", not "not dominated".
- **The registry is authored memory, not measurement.** `replacement` is a claim
  nobody executes, so a registry naming a slower replacement is accepted in
  silence. SC16's "is there a cheaper path to the same evidence" is a question
  the surface ASKS; it does not answer it for the operator.
- Nothing here establishes that the angle changes a reviewer's behavior. It
  establishes that the angle is reachable from the exported critique surface.

## Remainder

The honest next step for both criteria is one consuming repo authoring a registry
and reporting what the two surfaces said — the observation neither this record
nor any test in this repo can make.
