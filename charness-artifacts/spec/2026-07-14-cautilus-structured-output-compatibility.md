# Cautilus Structured-Output Compatibility Contract

Date: 2026-07-14

## Problem

Charness parses selected Cautilus command output as JSON, but a Cautilus update
changed the default structured format to YAML and tightened the proposal
evidence-kind enum. Relying on dependency defaults made the adapter fail even
though the required JSON surface remained supported.

## Capability Contract

When a Charness adapter parses Cautilus stdout as JSON, the adapter explicitly
requests JSON from the installed command. Checked proposal fixtures use only
evidence kinds accepted by the supported Cautilus schema. A dependency default
format change must therefore fail a command-shape test before it reaches the
release gate.

## Current Slice

- Request `--json` from `discover scenarios propose` and
  `evaluate comparison prepare`.
- Record the explicit format flag in proposal proof metadata.
- Replace the unsupported fixture evidence kind with the supported
  `skill_evaluation` kind.
- Cover both command shapes and the live installed-tool consumers.

## Fixed Decisions

- The parsing adapter owns output-format selection; Cautilus defaults do not.
- Repository fixtures follow the installed supported schema rather than
  preserving an obsolete enum spelling.
- Existing adapter return shapes and operator commands remain unchanged.

## Probe Questions

- None for this slice. The installed 0.19.3 command and repository-wide quality
  gate exercise both repaired consumers.

## Deferred Decisions

- A future Cautilus major-version policy may centralize structured-output flags
  if more stdout-parsing consumers appear.

## Non-Goals

- Running a Cautilus evaluation.
- Changing evaluation semantics, scenario selection, or public CLI behavior.
- Pinning Charness to one Cautilus patch release.

## Deliberately Not Doing

- Do not add a YAML fallback: accepting two wire formats would widen the local
  parser surface without operator value.
- Do not infer JSON from stdout content: the producer exposes an explicit
  contract, so the consumer should select it.

## Constraints

- Keep host/tool-specific behavior in the integration scripts.
- Preserve summary schemas and existing callers.
- Treat installed-tool proof as environment-specific and the checked tests as
  the durable contract.

## Success Criteria

1. Both JSON-parsing Cautilus subprocess consumers pass `--json` explicitly.
2. Proposal fixtures validate against the supported evidence-kind enum.
3. Focused command-shape tests and the full read-only quality gate pass with
   Cautilus 0.19.3 installed.
4. No Cautilus evaluation is needed to prove this adapter compatibility fix.

## Acceptance Checks

- `unit`: command-shape tests assert `--json` for proposal and comparison
  subprocesses.
- `integration`: installed-Cautilus proposal and comparison tests parse their
  final output successfully.
- `integration`: `./scripts/run-quality.sh --read-only` accepts the fixture,
  command output, and generated/plugin mirrors.
- `manual`: sibling scan confirms no other live Cautilus subprocess parses
  stdout as JSON without selecting JSON.

## Boundary Ownership

owned-correctly

The Cautilus CLI owns serialization; each parsing Charness adapter owns selecting
the serialization it consumes. Tests own the command-shape regression guard.

## Critique

- Interrupt Source: pre-release-advisory-integration
- Seam Summary: installed Cautilus schema and output defaults consumed by integration scripts
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the explicit-format adapter slice is implemented; focused tests and the 81-gate full quality consumer pass.
- What Disproving Observation Is Resolved: the contract now treats the output default and supported enum as an external boundary rather than stable local facts.
- Rejected alternative: a permissive JSON/YAML parser would hide producer
  contract drift and double the accepted wire surface.

The release critique is the bounded fresh-eye review for this task-completing
contract and covers dependency-seam ownership and non-claims.

## Canonical Artifact

This file is the current compatibility contract. Durable executable proof lives
in `tests/test_cautilus_eval_commands.py`,
`tests/test_cautilus_chatbot_compare.py`, and the repository quality gate.

## First Implementation Slice

Complete: explicit JSON selection, supported fixture enum, command-shape tests,
sibling-consumer scan, and the authoritative 81-gate full quality pass. Release
critique remains the publication boundary.
