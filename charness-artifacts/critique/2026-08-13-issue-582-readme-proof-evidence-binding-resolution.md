# Issue 582 README Proof Evidence Binding Resolution Critique
Date: 2026-08-13

## Decision Under Review

Make the existing Specdown reader reject a `README-*` Claim Ledger row whose
Evidence cell is not path-backed, without pretending that a path proves a claim.

## Failure Angles

- Generic document-link validation can pass an empty, malformed, or prose-only
  required Evidence cell because it has no ledger schema to enforce.
- A validator that scans every `README-*` line can turn examples or a future
  table outside Claim Ledger into an unrelated verdict input.
- A fragment path can appear precise while a file-presence checker cannot prove
  the named heading exists.

## Counterweight Pass

- The change validates only the exact Claim Ledger's Evidence field: existing
  relative files/directories, standard quoted titles, and no prose residue.
- Fragment links are rejected rather than receiving a partial heading parser.
- Semantic support for a claim, #524's taxonomy, #535's generic rebind rule,
  and #514's closeout assembly remain out of scope.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: specs/readme-proof.spec.md | action: fix | note: The final Specdown reader now uses the exact Claim Ledger row parser, not a document-wide README prefix scan.
- F2 | bin: bundle-anyway | evidence: strong | ref: scripts/readme_proof_ledger_lib.py | action: fix | note: Evidence cells fail closed for empty, malformed, prose-only, external, escaping, fragment, and missing-target references while allowing intentional directories and quoted titles.
- F3 | bin: over-worry | evidence: strong | ref: scripts/check_doc_links.py | action: defer | note: General document-link policy already owns well-formed markdown target checks and should not acquire one ledger's required-field schema.
- F4 | bin: valid-but-defer | evidence: moderate | ref: docs/readme-proof.md | action: defer | note: Path binding does not establish that cited artifacts semantically prove the claim.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer.
- Requested spawn fields: task_name `issue582_r1` and `issue582_r2`; read-only scope; no model override.
- Host exposure state: metadata-hidden
- Application state: n/a — host returns findings but has no typed reviewer-tier confirmation.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; R1 repaired table scope, fragments, and standard title handling. R2 found the final Specdown consumer still used a document-wide row scan; its repair is accepted-unreviewed under the two-round verdict-logic cap.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-160936-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-160936-packet.json
- Packet SHA256: 3c351024b849b103dbc044a131eb1b22e74eab72382acdb6ffe0926f5a5982e1
- Identity SHA256: 1033e972e64ff102634840e6f8c0b6397d2bfb6cd178574aaa3ff634220cc5cc

## Boundary Ownership

- Producer: `docs/readme-proof.md` authors the Claim Ledger Evidence cells.
- Consumer: `specs/readme-proof.spec.md` executes the final path-binding verdict through Specdown.
- Owning surface: README proof-ledger Specdown contract.
- Verdict: owned-correctly
