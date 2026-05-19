# Release Closeout Evidence Recritique

Date: 2026-05-19

## Target

Post-fix review of the issue closeout verifier, critique artifact validator, and
release helper proof changes after the `v0.7.4` release repair.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

`charness-artifacts/critique/2026-05-19-085848-packet.md`

## Findings

### Act Before Ship

- None after the final post-fix recritique. The prior blockers were closed:
  `--critique-artifact` now validates tracked repo-relative critique markdown
  before rendering review proof, and blocked critique signal validation rejects
  empty or marker-only signal sections.

### Bundle Anyway

- Keep the final prepare packet pair as closeout evidence for the delegated
  recritique run.
- Add the intentional `release -> critique artifact` ownership overlap to the
  allowlist because the release helper only reads a tracked critique proof path.

### Over-Worry

- Re-validating critique artifact content inside the release helper would
  duplicate `scripts/validate_critique_artifacts.py`; the helper only needs to
  prove the path is a tracked critique artifact.
- The release artifact wording is now separated enough: GitHub publication
  verification remains under public release verification, while real-host proof
  absence is recorded separately.

### Valid But Defer

- `post_publish_proof_lines()` still emits a concise `gh release view <tag>`
  command instead of the richer `--repo ... --json ...` command. This is
  acceptable for this slice because the current release backend is already
  GitHub-backed.

## Applied Decision

Ship the validator and release-proof hardening with the ownership allowlist
entry, final recritique artifact, generated plugin export, and full closeout
proof.
