# Issue #581 Adapter Example Placeholder Debug
Date: 2026-08-12

## Problem

The shipped `issue/adapter.example.yaml` puts `--reason` and `{reason}` in its
`create` command although the create operation does not accept that placeholder.
A consumer copying the documented adapter is refused before an issue is created.

## Correct Behavior

Given the shipped example, when every declared operation is resolved through
the real issue-backend grammar, then every template resolves with only its
operation's allowed placeholders. The example must not prescribe an argument
with no create-operation meaning.

## Observed Facts

- GitHub #581 is open, has `comments_read: true`, and has no comments.
- Its recorded reproduction resolves the shipped `create` template and receives
  `unknown placeholders ['reason']; allowed for create: ['body_file', 'repo', 'title']`.
- `{reason}` is allowed for close and comment, but the adapter's per-operation
  validation makes it invalid for create.
- The issue explicitly leaves open whether other example operations have the
  same drift; the repair must test the whole example, not only delete one pair.

## Reproduction

- Resolve `commands.create` from the shipped example with the production
  issue-backend resolver; it refuses `{reason}` before invoking any host command.

## Candidate Causes

- A close/comment argument pair was copied into the create block.
- The example is manually maintained without an executable contract test.
- Existing tests exercise individual operation grammars but not the complete
  shipped YAML artifact.

## Hypothesis

- Confirmed provisionally: the example drift is a copy-paste error that a test
  resolving every example operation against its production allowlist will
  expose; disconfirmer: inspect the example and the same resolver used by
  consumer adapter loading, then run the full-example regression before repair.

## Verification

- The production resolver reproduces the pre-fix refusal: create allowed only
  `repo`, `title`, and `body_file`, while the source example supplied `reason`.
- `python3 -m pytest tests/quality_gates/test_issue_skill.py -q` — 30 passed
  before the critique pass. The new regression parses the source YAML, requires
  its operation keys to match the audit map, and resolves create, view, close,
  comment, and search_newest_open through the production owner and module-owned
  allowlists.
- The plugin projection was regenerated from source; final packaging and lint
  verification remain the slice closeout checks.

## Root Cause

A close/comment-only argument pair was copied into the create template, and no
test consumed the complete shipped YAML through operation-specific production
allowlists. The parser checked that commands were lists of strings, while the
owner rejected the semantic mismatch only when a consumer tried create.

## Invariant Proof

- Invariant: every placeholder in a shipped adapter template is valid for its
  named operation under the same resolver a consumer executes.
- Producer Proof: `CREATE_PLACEHOLDERS` excludes reason, and create's template
  now contains only the permitted substitutions.
- Final-Consumer Proof: the regression resolves every declared source-example
  command with the same `resolve_op` owner that rejects consumer templates.
- Interface-Shape Sibling Scan: source and generated plugin example carry the
  same correction; packaging validation is the final projection proof.
- Non-Claims: no consumer repository or host-mediated backend has been run.

## Detection Gap

- Shipped adapter example | individual grammar checks did not consume the whole
  example | added an artifact-level regression that resolves each declared op.

## Sibling Search

- Mental model: a worked configuration example is treated as prose rather than
  an executable input contract.
- same layer: every operation in the example | decision: validate all now |
  proof: local payload proof through production resolver.
- cross-file: plugin projection of the public issue skill | decision: keep in
  sync | proof: source-to-plugin regeneration; final packaging validation pending.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: YAML example to issue-backend placeholder resolver.
- Disproving Observation: the production resolver accepts `{reason}` for create.
- What Local Reasoning Cannot Prove: behavior of an uninspected external host backend.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Critique Scope: shipped public adapter input and its consumer-facing grammar.
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

Treat shipped adapter examples as executable compatibility fixtures: parse the
same artifact a consumer copies and resolve every declared operation through
the production grammar.
