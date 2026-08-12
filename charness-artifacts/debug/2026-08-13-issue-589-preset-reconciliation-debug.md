# Issue 589 Preset Reconciliation Debug
Date: 2026-08-13

## Problem

Each declared `preset_lineage` entry had the permanent `declared-only` state
and an unconditional gap, even when its detected technology signal existed.

## Correct Behavior

Lineage remains provenance unless a repo-owned preset front matter contract
declares observable adoption requirements. A prescribed lineage is reconciled
only when its required adapter commands exist; legacy/sample-only lineage is
typed metadata rather than a permanent action-required gap.

## Observed Facts

- The old branch wrote `declared-only` and `preset_not_reconciled` for every
  string lineage item.
- `detect_preset_lineage()` observes technology files and tool configuration,
  not declared command adoption.
- Charness's active `python-quality` and `specdown-quality` lineage has no
  machine-readable prescription, so treating detection as reconciliation would
  be a false green.
- The focused planner now renders both active entries as `metadata-only`.

## Reproduction

- A validated fixture preset with two
  `reconciliation.required_adapter_commands` values is reconciled when both
  exact adapter commands exist and becomes `missing` with one named gap per
  absent command.

## Candidate Causes

- Preset gate vocabulary was prose-only.
- Technology inference was adjacent to, but not evidence of, adoption.
- The test suite pinned the single unavailable state instead of a state model.

## Hypothesis

- A repo-local, validator-accepted front matter contract can separate
  reconciled, missing, unavailable, and metadata-only lineage without inferring
  policy from prose; disconfirmer: a missing required command still renders
  reconciled, or a detected signal alone changes the result.

## Verification

- `python3 -m pytest tests/quality_gates/test_quality_declaration_path_resolution.py tests/quality_gates/test_profile_and_preset_validation.py tests/quality_gates/test_quality_run_planner.py -q`:
  84 passed, including validated nested front matter, reconciled, per-command
  missing, metadata-only, malformed-fence, CRLF, external-file-symlink, and
  symlinked-directory states.
- `python3 scripts/validate_presets.py --repo-root .`: 6 preset files passed.
- `plan_quality_run.py --repo-root . --detail`: active Python and Specdown
  lineage render `metadata-only`, with no permanent preset gap.

## Root Cause

The lifecycle used a provenance list as if it were an adoption contract, while
the only adjacent detector measured repository technology rather than policy;
the prior front-matter validator had no accepted nested prescription shape.

## Invariant Proof

- Invariant: a lifecycle clean state means every declared machine-readable
  requirement is observed, never merely that a repository looks like a language.
- Producer Proof: `_preset_contract()` rejects a path outside the canonical
  `presets/` directory and consumes the same validator-accepted, strict-fenced
  front matter as `validate_presets.py`; `_preset_rows()` compares its
  requirements to declared adapter commands.
- Final-Consumer Proof: `plan_quality_run.py` embeds lifecycle rows and the
  run-plan renderer exposes their state and gaps.
- Interface-Shape Sibling Scan: shipped plugin lifecycle code is mirrored; other
  bootstrap lineage inference remains provenance-only and is out of this slice.
- Non-Claims: no consumer preset migration or automatic adapter rewrite is proven.

## Detection Gap

- lifecycle planner tests | permanent declared-only state was asserted | fixtures
  now assert reconciled, per-command missing, unavailable, and metadata-only
  transitions; human output carries the metadata advisory reason.

## Sibling Search

- Mental model: metadata adjacent to a policy is evidence that policy applied.
- same layer: shipped lifecycle mirror | decision: same bug, fix now | proof: mirror sync.
- abstraction up: bootstrap lineage inference | decision: diagnostic-only | proof: static scan.
- cross-file: preset prose vocabulary | decision: contract source for repo-local
  presets | proof: fixture front matter.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: preset front matter to lifecycle report to quality planner.
- Disproving Observation: detected technology produces reconciled without a satisfied requirement.
- What Local Reasoning Cannot Prove: external consumer migration behavior.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Critique Scope: preset-state semantics and report-to-planner propagation.
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

Keep prescriptions machine-readable and local to the repository; leave prose
recommendations and technology detection as advisory provenance.
