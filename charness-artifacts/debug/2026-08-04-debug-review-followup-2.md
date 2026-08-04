# #496 Hollow Refill Debug
Date: 2026-08-04

## Problem

The quality customization warning reports inert nested defaults such as
`mutation_testing.commands.dry_run` and `.sample` as refilled after #493
recursion, then recommends dropping the whole block even when real commands
were supplied.

## Correct Behavior

Given a partially written `mutation_testing.commands` block with real `full`
and `summary` commands, when the policy merge compares defaults, the report
must distinguish a value that contributes no operator intent from a value that
does. The warning must not recommend discarding real configuration merely to
silence an inert-default report. The capability restored is trustworthy
customization guidance; this issue is a report/repair decision, not yet a
predicate change.

## Observed Facts

- Gathered GitHub issue #496 is OPEN and records the exact `mutation_testing`
  reproduction, reported leaves, warning remedy, and candidate owners.
- Defaults for `commands.dry_run` and `commands.sample` are empty strings;
  supplied `full` and `summary` commands are real configuration.
- The issue says the claim is value-level true but meaning-level hollow, and
  leaves open whether to change `refilled_policy_subkeys` or warning text.
- The local producer reproduction returns
  `['auto_issue', 'changed_quota', 'commands.dry_run', 'commands.sample',
  'declined', 'max_executable_mutants', 'max_executable_mutants_per_file',
  'max_files', 'max_test_nodeids', 'report_paths', 'schedule_cron',
  'score_break', 'workflow_path']` for the partial block.
- The real `bootstrap_adapter.py` reproduction emits a
  `customization_warning` that names the two command leaves and says the
  closest move is to “drop the WHOLE block” and declare it absent.
- A partial `prompt_asset_policy` with only `min_multiline_chars` reports
  `source_globs` and `exemption_globs`; its empty exemption list is consumed as
  the “no files exempt” scan boundary, so empty collection shape alone is not
  a safe inertness predicate.
- #503 is locally closed separately; it contributes no predicate recommendation.

## Reproduction

Minimal input from the issue:

    mutation_testing:
      commands:
        full: pytest --mutate
        summary: python3 scripts/summarize.py

Observed output is `commands.dry_run` and `commands.sample` in
`refilled_policy_subkeys`, with empty-string defaults, and a warning advising
removal of the entire commands block. The real bootstrap was run against a
temporary adapter carrying the issue's exact `full` and `summary` commands;
the temporary adapter was not used as product state.

## Candidate Causes

- Predicate cause: recursive comparison reports every nested default difference
  without asking whether the default carries operator intent.
- Merge-state cause: the nested block is partially written, so the comparison
  sees inherited leaves as refills even though the merge supplied no new intent.
- Consumer/remedy cause: `customization_warning` turns a true low-level report
  into advice to drop a block containing real commands.
- Contract cause: empty-string, empty-list, and empty-map defaults do not share
  one semantic meaning; top-level and nested behavior intentionally differ.

## Hypothesis

- Candidate: the recursion creates a hollow refill by treating inherited inert
  defaults as operator-supplied intent, while the generic warning remedy
  escalates a nested report into whole-block deletion. If true, the minimal
  partial block reports inert command leaves, the final warning recommends
  dropping real configuration, and the same empty-value shape has a different
  meaning in a scope list. disconfirmer: run the smallest issue fixture through
  both the producer and final warning consumer, then compare the empty-string
  command slot with the empty-list exemption scope before changing code.

## Verification

- confirmed and repaired — the real bootstrap issue fixture now suppresses only
  omitted `commands.dry_run` and `commands.sample`, preserves supplied
  `full`/`summary`, and emits no whole-block deletion advice. Missing `summary`
  remains reportable; explicit empty command slots are not reclassified; an
  empty exemption list remains a meaningful scan boundary. Fresh bootstrap is
  silent. The source and shipped plugin entrypoints produce identical complete
  JSON payloads and stderr for the fixture. Focused standing proof passed 85
  tests; the second repaired-surface review required the complete-payload
  comparison, which was added as a cap-limited round-2 repair accepted-
  unreviewed.

## Root Cause

The recursion has a value-level contract but no semantic inertness policy, and
the warning consumer turns any nested refill into advice to drop the whole
block. The repair must be field-aware: suppress only the known inert mutation
command slots, retain non-inert empty scopes, and change the nested remedy so it
cannot discard a block containing real configuration.

## Invariant Proof

- Invariant: the warning must name only configuration changes that can carry
  operator intent, and its remedy must preserve supplied real configuration.
- Producer Proof: the direct issue fixture and temporary real-adapter bootstrap
  reproduce the reported leaves and retain supplied full/summary commands.
- Final-Consumer Proof: the bootstrap JSON/stderr warning reproduces the
  whole-block deletion advice; prompt-asset scope code consumes an empty
  exemption list as a real exclusion boundary.
- Interface-Shape Sibling Scan: mutation command slots and prompt-asset scope
  lists share empty-value syntax but differ in semantic effect; the repair must
  vary the policy axis, not just the Python value.
- Non-Claims: this does not yet prove top-level symmetry, that every empty
  command slot is semantically inert in every future consumer, or that warning
  text alone is sufficient without a producer filter.

## Detection Gap

- Existing quality tests | detect value-level refill names but do not pin the
  semantic intent of the remedy | add positive/negative controls for inert
  mutation command slots and meaningful empty scope lists.
- Existing #493 recursion proof | proves nested discovery, not whether an
  inherited inert leaf carries intent | add the axis-varying counterexample
  and end-to-end warning assertion. Resolved by the Slice F regression matrix.

## Sibling Search

- Mental model: a syntactically real inherited value is treated as meaningful
  operator customization, then a nested report is mistaken for whole-block
  absence.
- same layer: `refilled_policy_subkeys` nested recursion | decision: repair the
  producer with an explicit mutation-command inertness policy | proof: direct
  fixture plus focused regression tests.
- abstraction up: `customization_warning` remedy construction | decision: fix
  now so nested findings never advise discarding real config | proof: exact
  bootstrap warning assertion.
- specialization down: empty defaults in `mutation_testing.commands` versus
  empty `prompt_asset_policy.exemption_globs` | decision: same value shape,
  different semantic outcome | proof: producer code read and local fixture.
- cross-file: `scripts/quality_policy_merge.py`,
  `scripts/quality_bootstrap_lib.py`, and `scripts/quality_bootstrap_absence.py`
  | decision: generated/source owners must move together | proof: source/export
  parity and end-to-end bootstrap.
- Valid follow-up outside this slice: if the semantic predicate remains
  ambiguous after reproduction, `follow-up: #496-predicate-contract` stays
  with the quality maintainer rather than being silently folded into #503.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: local quality-policy merge into operator warning text
- Disproving Observation: direct and end-to-end reproductions agree on the
  hollow command leaves and harmful remedy; no external seam is involved.
- What Local Reasoning Cannot Prove: host-specific rendering or operator
  interpretation beyond the repo warning consumer
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this dated debug record

## Prevention

Keep semantic inertness field-aware rather than value-only: empty mutation
command slots may be omitted from intent-loss reporting, while empty exclusion
scopes remain reportable because they affect scan scope. Change nested warning
remedies to review individual leaves and preserve blocks containing real
configuration. Pin both decisions through the real bootstrap and source/export
parity tests.
