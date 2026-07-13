# Debug: Quality Scaffold Reproduction Source Omission
Date: 2026-07-13

## Problem

A quality artifact filled from the canonical scaffold passed the quality
artifact validator but failed the final broad evidence-durability test because
the scaffold cited a gitignored runtime-signal file without marking it as a
reproduction source.

## Correct Behavior

The generated Runtime Signals source line must carry the canonical same-line
`<!-- reproduction-source -->` marker so the artifact tells readers how to
reproduce evidence without pretending the ignored metrics file is durable.

## Observed Facts

- `scaffold_quality_artifact.py` emits
  `.charness/quality/runtime-signals.json` <!-- reproduction-source --> on its Runtime Signals source line.
- `check_spec_evidence_durability.py` rejects that gitignored citation unless
  the same line carries the reproduction marker.
- The final lock failed one test with this exact diagnostic; adding the marker
  to the generated artifact made the focused durability test pass.

## Reproduction

- Fill and persist the quality scaffold, then run
  `python3 scripts/check_spec_evidence_durability.py --repo-root .`; the
  generated source line is rejected before the producer fix.

## Candidate Causes

- Consumer validator incorrectly classifies `.charness` as ignored evidence.
- Hand editing moved a valid marker away from the citation.
- Scaffold producer omits the marker from its canonical template.

## Hypothesis

- The scaffold producer is the cause: its literal Runtime Signals line lacks
  the marker, so every unchanged scaffold consumer inherits the invalid
  citation; adding the marker to that literal makes generated output pass the
  durability contract.
- disconfirmer: inspect the source/plugin scaffold literals and generate the
  template; if either already contains a same-line marker, the hypothesis is
  false.

## Verification

- confirmed — both source and plugin literals lacked the marker, while the
  durability validator's focused marker tests established the required
  same-line grammar.

## Root Cause

The quality scaffold and evidence-durability contracts evolved independently:
the scaffold began naming the ignored runtime metrics as a useful reproduction
input but did not encode the consumer validator's durability marker.

## Invariant Proof

- Invariant: every scaffold-emitted gitignored evidence citation identifies
  itself as a reproduction source on the citing line.
- Producer Proof: generated quality template contains the marker beside the
  runtime-signal path.
- Final-Consumer Proof: evidence-durability validation accepts a persisted
  scaffold-derived quality artifact.
- Interface-Shape Sibling Scan: all scaffold scripts were searched for
  `.charness` citations; only quality source and its plugin mirror matched.
- Non-Claims: no broader ignored-path grammar or validator behavior changes.

## Detection Gap

- quality scaffold regression | its focused tests checked shape but not the
  generated citation's durability | assert the marker in generated template
  output and retain the final consumer gate.

## Sibling Search

- Mental model: generated artifact templates that cite ignored evidence must
  encode the consumer's reproduction-source grammar.
- same layer: all public/support scaffold scripts | decision: diagnostic-only |
  proof: repo search found no other `.charness` citation.
- abstraction up: evidence-durability validator | decision: intentional
  boundary | proof: it correctly rejected the unsafe generated citation.
- specialization down: installed quality plugin mirror | decision: same waste,
  fix now | proof: byte-parity sync carries the producer repair.
- mental-model siblings: runtime summary renderer | decision: intentional
  boundary | proof: it emits reproduction text, while the persisted artifact
  producer owns the durability annotation.
- cross-file: plugin mirror and `tests/test_quality_scaffold.py` own installed
  parity and regression proof.

## Seam Risk

- Interrupt ID: quality-scaffold-durability-2026-07-13
- Risk Class: contract-freeze-risk
- Seam: scaffold output -> persisted quality artifact -> durability validator
- Disproving Observation: a generated template with the marker still fails the
  final consumer on the runtime-signal citation
- What Local Reasoning Cannot Prove: whether unrelated hand-authored ignored
  paths are honestly reproducible
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Fix the producer literal and add one generated-template regression. Do not add
a duplicate quality gate: the existing durability validator remains the final
consumer and correctly caught the escape.
