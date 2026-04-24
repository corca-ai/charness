# Taxonomy-Axis Checkpoint

Use this before adding a new user-facing mode, kind, strategy, profile, target,
or similar enum value to a spec, CLI, API, adapter, or skill contract.

## Checkpoint

Ask these questions before naming or implementing the new value:

- Are the existing enum values on the same conceptual axis?
- Is the new value truly a new kind, or is it a common objective, evidence
  focus, trigger/reason, selection policy, mutation behavior, or internal
  preset?
- Should this be user-facing CLI/API vocabulary, or should the agent infer it
  behind a strong default?
- Would adding the option reduce user burden, or expose avoidable choice?
- Would the contract be clearer by merging mixed-axis values or splitting
  purpose, method, evidence, and policy into separate internal fields?

## Mixed-Axis Signals

Call out mixed axes explicitly. Common categories are:

- `purpose/state`: why the workflow is running, such as fixing a known failure
- `method`: how revision happens, such as reflection or review
- `evidence source`: what evidence receives priority, such as history or a
  current report
- `trigger/reason`: what event caused this run, such as runtime drift
- `objective`: what tie-breaker applies across runs, such as shorter output
- `selection policy`: how candidates are ranked
- `internal preset`: a bundled default that should not become operator-facing
  vocabulary

For example, if an optimizer proposes `simplification` as a new kind beside
values like `repair`, `reflection`, and `history_followup`, first test whether
those values are one axis. A better contract may separate `revisionReason`,
`evidenceFocus`, and `selectionObjective`, then keep compression as a shared
selection objective instead of a new user-facing mode.

Treat that as a diagnostic example, not a directive to change any existing
Cautilus optimizer taxonomy. The checkpoint is about testing the axis before a
contract hardens.

## When A New Enum Is Honest

A user-facing enum is still appropriate when it creates real safety, clarity,
interoperability, or compatibility:

- different values require materially different acceptance checks
- operators must choose because the default would be unsafe or irreversible
- external APIs or file formats already expose the vocabulary
- hiding the distinction would make failure recovery less legible

Otherwise prefer strong defaults, inference, internal presets, or separate
implementation fields over an expanded public choice surface.
