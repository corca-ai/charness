# Debug: Release claims review derived-fact authoring and state-contraction residue
Date: 2026-08-30

## Problem

At the v8 prepared release stop, the claims-review contract required an operator to
hand-author exact record hashes and a 2,627-path delta partition. While repairing that
friction, the scope policy changed from “pass with completeness not established” to
“refuse or record unproven,” but the retired completeness state remained in transport
and rendering code until the tokei length gate caused a later scan.

## Correct Behavior

Reviewer judgment stays explicit. Prepared identity, target/tag, complete scope, base,
and digest are derived once by a repo-owned authoring capability and independently
re-derived by the validator. Removing a state removes its producer, transport, and final
consumer in the same contract transition; unknown record fields refuse.

## Observed Facts

- The prepared v7-to-v8 delta contained 2,446 blocking and 181 advisory paths.
- No production scaffold owned the v3 record shape; examples were stale by contract.
- The validator previously required every blocking path but permitted omitted advisory paths.
- After converting absent/shallow/non-ancestor scope bases to refusal, `_record_stand_down`
  had no caller while `scope_completeness` still crossed two downstream modules.
- The official tokei gate, not the semantic change, prompted the first complete residue scan.

## Reproduction

- Prepare a release, then follow the old critique-boundary instructions: exact hash and
  path lists must be copied manually.
- Change scope-base failure from stand-down to refusal and search for
  `scope_completeness`: transport and renderer consumers remain despite no producer.

## Candidate Causes

- Derived facts were modeled as reviewer-authored evidence.
- The scope schema was an open dictionary, so obsolete fields were silently accepted.
- Contract-transition verification followed the new producer path but did not enumerate
  removed states through final consumers.

## Hypothesis

- If the root cause is open authoring and open schema, then a post-prepare scaffold plus
  exact-key validator will eliminate manual scope assembly and refuse any retired field. |
  disconfirmer: scaffold a real prepared fixture, commit only its JSON+narrative, and run
  the actual resume validator; inject the retired field and require refusal.

## Verification

- confirmed — three real prepared-fixture scaffold tests pass, including resume acceptance,
  read-only preview, dirty-state refusal, and absent-base refusal.
- confirmed — a v4 record carrying `scope_completeness` refuses as a non-canonical field.
- confirmed — 123 focused release/claims tests, Python lint, and the tokei length gate pass.

## Root Cause

The release boundary mixed judgment with derivation and represented a versioned proof
record as an extensible dictionary. That combination made copying the normal authoring
path and let a removed state remain readable after its semantics disappeared. The local
process error was treating the new validator branch as completion instead of tracing the
removed state through every producer, carrier, and final consumer.

## Invariant Proof

- Invariant: a passing claims record binds the exact complete release delta and contains
  only v4 fields.
- Producer Proof: `scaffold_claims_review.py` derives prepared facts, both scope lists,
  base ref, digest, and count after prepare.
- Final-Consumer Proof: `validate_claims_review` re-derives the delta and
  `claims_review_schema` refuses unknown/missing fields before rendering.
- Interface-Shape Sibling Scan: pass and unproven shapes, nested observer/scope/basis
  objects, shallow history, missing tag, non-ancestor base, target mismatch, tag collision,
  unrelated dirty paths, and generated plugin export were inspected.
- Non-Claims: the scaffold does not prove reviewer distinctness or author the narrative.

## Detection Gap

- Contract state contraction | no gate required removed fields to disappear from all
  consumers | closed-world versioned schema now makes residue a validation failure.
- Prepared authoring | planner emitted only resume commands | planner now emits the
  scaffold command before resume.

## Sibling Search

- Mental model: irreversible-boundary records should derive facts and close their schema.
- claims record axis: authoring, validator, resume transport, public renderer, docs, planner,
  source/export mirror | decision: unified under scaffold + v4 schema | proof: focused tests.
- cross-file: `publish_release_resume_publish.py` and
  `publish_release_artifact_sections.py` were the stale final consumers removed.

## Seam Risk

- Interrupt ID: release-claims-v4
- Risk Class: none
- Seam: prepared commit to claims evidence child
- Disproving Observation: actual fixture resume accepts the generated direct child.
- What Local Reasoning Cannot Prove: the free-text observer signal names a real distinct reviewer.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this record

## Prevention

For a contract transition that removes or collapses a state, enumerate its producer,
serialized field, transport, renderer, docs, and tests before calling the transition
complete. Versioned proof records use exact field sets; derived release facts are produced
by an authoring command and independently checked, never copied into reviewer judgment.
