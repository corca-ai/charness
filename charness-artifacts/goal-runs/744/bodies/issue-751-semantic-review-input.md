## Situation

The Charness v8 canonical `critique` runner can bind an exact `--reviewed-path` yet give the file-backed reviewer no semantic content or explicit instruction to read that path.

This appeared while reviewing a mutable pre-binding Achieve Goal Draft in Ceal with the installed Charness `8.0.0` `run_review.py` path and an adapter with no `packet_sections`.

## Observed experience

The generated packet correctly captured the Goal Draft path, SHA-256, and reviewed-input identity, but emitted `section_count: 0` and `sections: []`. The generated worker prompt said the packet was the authoritative review input and embedded only that packet. It did not include the draft bytes or tell the read-only worker to open the exact reviewed path.

Two parallel, distinct-lens reviewers therefore treated the draft as unavailable. One returned a valid typed `defer`; the other attempted a similar defer but violated the bounded-result enum and was correctly rejected as `schema-invalid`. No semantic Goal Draft critique occurred.

## Evidence

- Charness source: `533f24dad3` and installed plugin cache `8.0.0`.
- Invocation shape: `run_review.py --repo-root . --reviewed-path charness-artifacts/goals/2026-08-28-ceal-1-0-release-convergence.md --scope ceal-1-0-stage5-goal-draft --lens ...`.
- Packet: exact reviewed path and content hash, but no content sections.
- Valid worker result: blocker `The authoritative packet contains no draft content to review`, verdict `defer`, delivered through a current packet and `findings-received` worker report.
- A second attempt whose lens explicitly instructed the worker to read the hash-bound path was required to make the semantic input reachable.

## Impact

The advertised semantic wrapper has a false-ready state: packet verification passes and the isolated reviewer runs, but ordinary `--reviewed-path` usage with an empty adapter cannot review the selected artifact. Consumers either pay a failed reviewer round, add one-off packet sections tied to a particular draft, or discover an undocumented prompt workaround.

## Expected behavior

The canonical runner should make every declared reviewed path semantically reachable while preserving its content identity. A reviewer should not have to infer that it may ignore the phrase `authoritative packet` and separately open a path that the generated prompt never asks it to read.

## Weak solution direction

Either include bounded reviewed-file content in the packet, or make the generated prompt explicitly require read-only opening of every hash-bound reviewed path and explain that the packet owns identity while the path owns bytes. Keep large-file and deletion behavior explicit rather than silently truncating.

---

<!-- charness-work-item-key: issue-751-semantic-review-input -->
# Work Item #751 — Refuse empty semantic review input

## Purpose and premise

Ensure a reviewer is launched only when the prepared packet contains semantic review input, not merely path or packet ceremony.

## Acceptance and proof

A semantic packet launches; empty or deletion-only semantic input refuses/skips explicitly; a deliberately wrong path-count proxy fails. Focused proof and resolution critique remain issue-owned.

## Non-claims

No meta-gate shared as a substitute for #752 or #709 behavior.
