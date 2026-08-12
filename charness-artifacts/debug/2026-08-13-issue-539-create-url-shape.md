# Issue 539 Create URL Shape Debug
Date: 2026-08-13

## Problem

Successful non-default create backends may print a bare issue number. The create
payload exposes that raw text as canonical `url`, falsely claiming a link.

## Correct Behavior

Create output supplies a URL only when it is a complete HTTP(S) URL. A normal
readback may supply a validated structured URL; skipped readback preserves the
number but leaves the URL absent.

## Observed Facts

- `_parse_created_number` intentionally accepts a bare final number.
- `create_issue` assigns the raw stdout to `url` and `created_url`.
- Normal readback asks only for `body`, so it cannot repair a missing URL.

## Reproduction

- A successful backend create response of `538` produces `number: 538` and
  `url: "538"`.

## Candidate Causes

- Backend stdout was treated as a URL rather than an untrusted transport field.
- Readback validation checked body fidelity but did not request identity data.
- Default `gh` URL output kept the invalid alternate backend path invisible.

## Hypothesis

- Validate stdout as HTTP(S), then use only a validated readback URL as fallback;
  disconfirmer: bare output can still reach either URL field after a skipped
  readback.

## Verification

- Result: confirmed by causal review and the existing create payload path.

## Root Cause

One raw backend field was assigned two semantic roles: diagnostic create output
and canonical URL identity.

## Invariant Proof

- Invariant: a create payload's URL fields are navigable HTTP(S) links or null.
- Producer Proof: issue-create validates create stdout and structured readback.
- Final-Consumer Proof: closeout readers consume canonical `url` without a
  malformed bare-number link.
- Interface-Shape Sibling Scan: issue read/close use structured backend JSON,
  not create stdout.
- Non-Claims: no repository-plus-number URL synthesis or backend URL convention.

## Detection Gap

- Create tests covered only default URL stdout; add bare-number with and without
  readback controls.

## Sibling Search

- Mental model: transport output is not identity until shape-validated.
- create flow: issue_create.py | decision: own fix here | proof: end-to-end fake backend.
- structured readers: issue_read.py and issue_close.py | decision: no change | proof: static call-path scan.
- cross-file: closeout-discipline tests | decision: preserve canonical key contract | proof: existing suite.

## Seam Risk

- Interrupt ID: issue-539-create-url-shape
- Risk Class: none
- Seam: backend create stdout to canonical payload to closeout reader.
- Disproving Observation: non-default stdout cannot be a bare number.
- What Local Reasoning Cannot Prove: every external backend's URL conventions.
- Generalization Pressure: none

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep canonical identity fields shape-validated and retain raw transport only in
explicit diagnostic fields when it is needed.
