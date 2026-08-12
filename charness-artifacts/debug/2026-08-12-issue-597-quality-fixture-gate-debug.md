# Issue 597 Quality Fixture Gate Debug
Date: 2026-08-12

## Problem

The quality-fixture checker passed when the required fixture corpus was empty
and the standing quality runner never invoked it.

## Correct Behavior

Given this repository's checked-in external-tool fixture contract, when the
fixture set is missing or empty, then the checker and the standing quality gate
must refuse; a valid checked-in corpus must still pass.

## Observed Facts

- #597 records one checked-in fixture and its captured stream.
- The prior empty branch printed “nothing to verify” and exited 0.
- `run-quality.sh` had no `check_quality_tool_fixtures.py` entry.
- The checker is a repo quality proof surface, so empty corpus is an unproven
  contract rather than a valid consumer configuration.

## Reproduction

- Run the checker with a fixture-free temporary repo: pre-fix exit is 0 and the
  standing gate has no label that would run it.

## Candidate Causes

- Empty input was treated as harmless evidence absence.
- Surface metadata only routed fixture-file changes, not fixture deletion.
- The standing runner never owned the fixture verifier.

## Hypothesis

- Changing the empty branch to a refusal and queueing the verifier will make
  both missing and empty corpora observable; disconfirmer: the live fixture
  corpus then fails the same verifier or its selected quality-run label.

## Verification

- `python3 -m pytest tests/quality_gates/test_quality_tool_fixtures.py -q`:
  27 passed, including empty/missing corpus, empty JSON, required provenance,
  nullable final-consumer, and stream integrity cases.
- `CHARNESS_QUALITY_LABELS=quality-tool-fixtures ./scripts/run-quality.sh --read-only`:
  one selected gate passed in 66ms.

## Root Cause

A repository-owned evidence contract was modeled as optional input and was not
wired to the final quality consumer, leaving an empty corpus indistinguishable
from a verified corpus.

## Invariant Proof

- Invariant: when the fixture verifier claims the repository evidence contract
  holds, the standing quality consumer must run it and it must observe at least
  one fixture.
- Producer Proof: empty/missing fixture tests now return 1.
- Final-Consumer Proof: selected `quality-tool-fixtures` run-quality label
  executed and passed on the live corpus.
- Interface-Shape Sibling Scan: `.agents/surfaces.json` remains change-routing
  metadata; `run-quality.sh` is the final consumer for deletion detection.
- Non-Claims: this does not re-run awiki or prove external-tool behavior.

## Detection Gap

- fixture checker and runner | empty pass plus unwired verifier | refusal tests
  and a standing gate label.

## Sibling Search

- Mental model: an empty evidence corpus can prove a repository-required claim.
- same layer: fixture directory missing and empty | decision: same bug, fix now
  | proof: local payload proof.
- abstraction up: other optional evidence checkers | decision: valid follow-up
  outside the slice | proof: static scan only | follow-up: deferred docs/handoff.md#next-session
- cross-file: `scripts/run-quality.sh` | decision: same bug, fix now | proof:
  selected standing-gate run.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: checked-in fixture corpus to verifier to quality runner.
- Disproving Observation: live corpus or selected quality label fails after wiring.
- What Local Reasoning Cannot Prove: external tool recapture correctness.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Critique Scope: fixture-verdict semantics and quality-runner wiring.
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

Treat a repository-required evidence corpus as required input at its final
consumer, not only as a file-change surface.
