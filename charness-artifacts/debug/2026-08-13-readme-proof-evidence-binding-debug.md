# README Proof Evidence Binding Debug
Date: 2026-08-13

## Problem

The README proof ledger names evidence, but its executable Specdown reader
checks only row shape and proof-owner text. Empty, malformed, or prose-only
evidence can therefore pass while presenting a claim as path-backed.

## Correct Behavior

Given a `README-*` ledger row, when Specdown validates it, then its Evidence
cell must contain one or more well-formed relative Markdown references with
existing repository targets and no unparsed prose residue; this proves path
binding, not claim satisfaction.

## Observed Facts

- `docs/readme-proof.md:63-73` has 11 reader-facing ledger rows. Its Evidence
  column has 51 Markdown references but three cells also retain free text.
- `specs/readme-proof.spec.md:42-66` checks eight cells and proof owner only;
  it never reads Evidence (`cells[4]`).
- The repair scope is the exact `## Claim Ledger` table, so `README-*` text in
  another document section or a code example cannot accidentally become a
  verdict input.
- Global `check_doc_links.py` rejects a well-formed missing relative target but
  does not make an empty or unparsed Evidence cell a ledger failure.
- Fragments are deliberately out of the narrow file-presence contract: a
  fragment-bearing Evidence link is refused rather than pretending a local path
  check validates its heading; Markdown link titles remain accepted.

## Reproduction

- Replace one Evidence cell with an empty value, `[]()`, or plain
  `missing/path`; the current executable Specdown fence remains green because
  it does not inspect that cell.

## Candidate Causes

- The ledger spec treated row shape as enough evidence binding.
- General document-link checking was incorrectly assumed to validate this
  ledger-specific required-field contract.
- The ledger allowed illustrative free-text residue beside concrete links.

## Hypothesis

- A ledger-local Evidence parser in the existing Specdown reader will reject
  empty, malformed, prose-only, and absent targets without broadening generic
  document-link policy | disconfirmer: run the fence with each minimal bad
  Evidence cell and observe a nonzero failure.

## Verification

- confirmed — static reader inspection shows the existing fence accesses
  `cells[3]` but not `cells[4]`; the causal review independently enumerated the
  three free-text cells and current valid targets.

## Root Cause

The final ledger reader had no required Evidence-cell invariant. General link
validation cannot supply it because a required field may contain no parsed link
at all.

## Invariant Proof

- Invariant: when the README proof ledger publishes an evidence cell, its
  Specdown reader must refuse non-path-backed evidence before reporting the
  ledger surface green.
- Producer Proof: `docs/readme-proof.md` authors the eight-cell ledger rows.
- Final-Consumer Proof: `specs/readme-proof.spec.md` is executed by the
  Specdown quality lane in `scripts/run-quality.sh`.
- Interface-Shape Sibling Scan: global document-link checking owns valid-link
  targets but not this required ledger-field semantics.
- Non-Claims: target presence does not prove cited evidence semantically
  supports the reader-facing claim.

## Detection Gap

- `specs/readme-proof.spec.md` | its row-shape fence omitted Evidence | require
  one-or-more parseable existing relative targets and no residue in `cells[4]`.
- `scripts/check_doc_links.py` | catches valid broken links only | intentional
  plain-document boundary; do not broaden it for one ledger schema.

## Sibling Search

- Mental model: a generic link checker proves a schema-required evidence field.
- same layer: `specs/readme-proof.spec.md` | decision: same bug, fix now |
  proof: static final-reader trace.
- abstraction up: `scripts/check_doc_links.py` | decision: intentional
  plain-text or non-rendering boundary | proof: current parser contract.
- cross-file: `docs/readme-proof.md` | decision: same bug, fix now | proof:
  three observed Evidence residues.
- valid follow-up outside the slice: proof-taxonomy, generic digest rebind, and
  semantic claim validation | follow-up: deferred docs/handoff.md#next-session.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: ledger Markdown -> Specdown executable fence -> quality verdict.
- Disproving Observation: a malformed Evidence cell already fails the fence.
- What Local Reasoning Cannot Prove: that a cited target semantically proves its claim.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

Keep the narrow Evidence-cell invariant at its existing final reader and retain
global link checking as the independent well-formed-link validator.
