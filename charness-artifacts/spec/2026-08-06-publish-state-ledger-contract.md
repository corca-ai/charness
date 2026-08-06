# Post-Push Publish-State Ledger Contract

Date: 2026-08-06
Source: `2026-08-06-post-push-operational-proof-runtime-evidence` Slice 6

## Problem

The repository has a frozen post-push manifest and handoff/goal prose, but no
executable record that reconciles one immutable published SHA across the
captured remote evidence and the reader-facing continuation claims. A later
reader can therefore see stale `OPEN`/pending wording beside a successful
remote readback without a single refusal boundary.

## Capability Contract

Given a checked-in ledger, the existing Slice 1 manifest, and two explicitly
marked JSON claim blocks embedded in the named goal and handoff documents, the
validator must return `reconciled_captured_snapshot` only when the ledger's
manifest path and SHA-256 match the checked-in manifest; the manifest's
captured CI readback has the target SHA, overall success, and every listed job
completed/successful at that SHA; the manifest's captured repository-wide issue
readback has zero open issues; and both source-owned claim blocks have the same
full 40-character published SHA, manifest path/digest,
`claim_state: reconciled_captured_snapshot`,
`issue_scope: repository_open_issues_empty`, and `pending_publish: false`.

It must return a structured refusal for stale SHA, `OPEN`, pending, missing,
malformed, digest-mismatched, or otherwise inconsistent state. The validator
reads only the marked JSON blocks; it does not parse arbitrary surrounding
Markdown prose.

The ledger is a read-only reconciliation record. It does not call GitHub, push,
close issues, edit the goal, or rewrite the handoff.

## Current Slice

Add one repo-owned JSON ledger, a validator CLI/library, two source-owned claim
blocks, and deterministic fixtures/tests. Bind the ledger to the existing
manifest by path plus content digest, derive CI/issue facts from that manifest,
and bind the ledger to the two marked source blocks by path plus stable block
ID. Keep the ledger repo-local; generated plugin export parity may carry the
script because the packaging surface exports `scripts/**`, but no portable
plugin workflow or consumer claim is added.

## Fixed Decisions

- The published identity is the manifest target SHA, not current local `HEAD`;
  a local draft cannot satisfy the ledger by moving the target.
- The ledger contains only `kind`, `schema_version`, a manifest `{path,
  sha256}`, and source claim locators `{path, block_id, sha256}`. It does not
  copy CI, issue, goal, or handoff outcomes.
- A source locator's `sha256` is the SHA-256 of the marked claim's canonical
  sorted compact JSON object, not the surrounding Markdown file. This keeps
  the binding at the source-owned claim boundary while allowing ordinary
  continuation prose to evolve.
- Each source claim block is a fenced JSON object with exactly the fixed fields
  `kind`, `schema_version`, `block_id`, `manifest_path`, `manifest_sha256`,
  `published_sha`, `claim_state`, `issue_scope`, `pending_publish`, and
  `captured_at`. `claim_state` has one value in this slice:
  `reconciled_captured_snapshot`; `issue_scope` has one value:
  `repository_open_issues_empty`.
- The manifest predicate is derived from its actual shape: top-level
  `ci_readback.status == captured`, matching target/head SHA, conclusion
  `success`, and every listed job `status == completed`, `conclusion == success`,
  and matching head SHA. The issue predicate is captured repository-wide
  `open_count == 0`, associated with the manifest's repository/ref/target
  identity; it is not a causal claim that issue state belongs to a commit.
- Any mismatch refuses before emitting a reconciled verdict. Refusal is
  deterministic: validate shape, manifest binding, source blocks, then derived
  CI/issue predicates in that order and return the first failure with both a
  stable `code` and `field`.

## Source Claim Block

The validator recognizes only the following bounded marker shape in the named
goal and handoff files; it does not scan historical prose:

`<!-- charness-publish-state-claim:post-push-operational-proof -->` followed by
a fenced `json` object whose `block_id` is
`post-push-operational-proof` and whose fields match the Fixed Decisions above.
The ledger names the two source paths and this block ID. A missing marker,
duplicate marker, malformed JSON, wrong block ID, or extra/missing field refuses.

## Refusal Matrix

| Condition | Code | Field |
| --- | --- | --- |
| ledger shape or required field invalid | `invalid_ledger` | `ledger` |
| manifest missing/unreadable | `manifest_missing` | `manifest.path` |
| manifest content digest differs | `manifest_digest_mismatch` | `manifest.sha256` |
| manifest captured record invalid | `manifest_invalid` | `manifest` |
| source marker absent/duplicate/malformed | `source_claim_invalid` | `sources.<owner>` |
| source claim SHA/path/digest differs | `source_claim_mismatch` | `sources.<owner>.claim` |
| source claim pending or not reconciled | `source_claim_pending` / `source_claim_state` | `sources.<owner>.claim.pending_publish` / `claim_state` |
| captured CI is incomplete or unsuccessful | `ci_not_success` | `manifest.ci_readback` |
| captured CI job identity/status differs | `ci_job_mismatch` | `manifest.ci_readback.jobs` |
| captured issue observation is not repository-empty | `issues_not_empty` | `manifest.remote_readback.open_issues.open_count` |

## Probe Questions

- Does the ledger validator detect each stale/pending class independently
  without accepting a partial payload? Answer with parameterized fixtures and
  structured error codes.
- Can the validator bind its ledger to the existing manifest without copying
  or reinterpreting CI/issue fields? Answer with a manifest-identity fixture.
- Is the goal/handoff claim shape sufficient for a later session to read the
  ledger without parsing prose? Answer with the checked-in ledger and a
  `--json` readback.

## Deferred Decisions

- Live provider refresh and external writes are deferred to a separately
  authorized publish phase; reopen when a new push SHA is approved.
- Automatic goal/handoff rewriting is deferred; reopen only if repeated manual
  claim drift remains after this validator exists.
- A general multi-publish history database is deferred; the first contract
  validates one immutable published target per ledger file.

## Non-Goals

- No new push, release, tag, version bump, PR, issue close, Cautilus run, or
  provider/install roundtrip.
- No parser for arbitrary handoff or goal prose and no replacement for GitHub
  or GitHub Actions as state owners.
- No new portable plugin workflow or public-skill surface for this repo-local
  post-push record; generated script parity is only a packaging obligation.

## Constraints

- The ledger and validator must be deterministic and offline.
- Errors must identify the failed field and a stable refusal code; human and
  JSON output are two renderings of one validator result.
- The source manifest remains the only owner of captured CI/issue identity.
- Acceptance evidence must live under `charness-artifacts/`; temporary command
  output is reproduction detail only.

## Success Criteria

- A valid ledger bound to the captured manifest and two source blocks returns
  `reconciled_captured_snapshot` and names one published SHA across the
  manifest, goal claim, and handoff claim.
- Each refusal-matrix row returns its specified stable code and field; it never
  returns a reconciled verdict.
- The CLI's compact human and machine-readable JSON modes render the same
  validator result.
- The checked-in ledger exposes manifest/source locators and the reconciliation
  result so a later operator need not reconstruct state from handoff prose.

## Acceptance Checks

- `pytest -q tests/quality_gates/test_publish_state_ledger.py` (unit: valid
  reconciliation, source-block binding, every refusal-matrix row, and human/
  JSON parity).
- `python3 scripts/publish_state_ledger.py --repo-root .`
  (integration: checked-in ledger readback in human mode).
- `python3 scripts/publish_state_ledger.py --repo-root . --json`
  (integration: same checked-in readback in JSON mode; result must match the
  human mode).
- `python3 -m json.tool charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json`
  (integration: durable ledger locator shape; semantic content is covered by
  the focused validator test).
- `python3 scripts/check_doc_links.py --repo-root .` (integration: contract
  and handoff references remain valid).

## Boundary Ownership

- `manifest`: owns captured target, CI, and issue observer identity.
- `goal` and `handoff`: own their marked continuation claim blocks.
- `publish-state-ledger`: owns only source locators and the offline
  reconciliation verdict; it does not own or mutate external state.
- `GitHub` and `GitHub Actions`: remain external state owners; no provider
  freshness is claimed by an offline validation run.
- `goal` and `handoff`: remain human-facing continuation surfaces and provide
  explicit claims for the ledger to check.

## Critique

- Interrupt Source: none; the Slice 6 contract is unrelated to the resolved
  Markdown external-seam interrupt, whose carry-forward is recorded in its
  canonical spec.
- Seam Summary: captured manifest -> offline reconciliation ledger -> goal and
  handoff continuation claims.
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: three bounded angle reviews and a separate counterweight
  found and repaired the source-binding, manifest-derived predicate, refusal
  matrix, and acceptance-coverage gaps before implementation.
- What Disproving Observation Is Resolved: a stale or pending human-state
  claim must be refused even when the captured CI/issue fields are green.

## Canonical Artifact

- `charness-artifacts/spec/2026-08-06-publish-state-ledger-contract.md`

## First Implementation Slice

Add the marked goal/handoff claim blocks, the offline validator/library, the
checked-in ledger, and one-factor invalid fixtures. Then run the focused suite.
The first green is still provisional until the repaired verdict surface
receives its required second implementation review and final closeout proof.
