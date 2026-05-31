# Critique: #264 Portability Guard And Sweep

Execution: parent-delegated fresh-eye review with two code critique angles and
one separate counterweight pass.

Fresh-Eye Satisfaction: parent-delegated

Packet Consumed: `charness-artifacts/critique/2026-05-31-122851-packet.md`

Target: `code-critique`

## Change

Extend the public-skill portability validator so `validate_skills.py` rejects
bare author-repo-only cites to docs, tests, and source-tree skill paths unless
they are skill-relative to vendored content or marker-qualified as
authoring-repo-internal. Sweep existing public-skill references to satisfy the
new guard.

## Angles

- Angle 1: false positives/negatives, marker handling, and allowlist
  correctness.
- Angle 2: public-skill portability semantics and readability for downstream
  vendored users.
- Counterweight: triaged the repaired diff after angle blockers were fixed.

## Findings

### Act Before Ship

- Initial path matching missed pytest node IDs such as
  `tests/test_x.py::test_case`. Fixed by normalizing `::...` and `#...`
  suffixes, and adding regression coverage.
- Initial matching missed extensionless source-tree skill paths such as
  `<repo-root>/skills/public/other`. Fixed by recognizing backticked
  `skills/public|support|shared/...` paths, while ignoring placeholder-only
  examples and trailing namespace examples.
- Initial sweep marker-qualified sibling public-skill references that ship in
  the same plugin. Fixed by converting those to exported-layout relative paths,
  such as `../../impl/references/verification-ladder.md`.
- Two retro references still used authoring-only sibling public-skill wording
  after the first repair. Fixed by converting them to
  `../../critique/references/angle-selection.md` and
  `../../debug/references/sibling-search.md`.

### Bundle Anyway

- Added allowlist tests for `docs/roadmap.md`, `docs/operator-acceptance.md`,
  `docs/release-notes.md`, `charness-artifacts/...`, `docs/*-adapter.yaml`,
  `.agents/*-adapter.yaml`, and sibling skill-relative references.
- Added negative tests for `tests/*.py::nodeid`,
  `<repo-root>/skills/public/...`, and non-conventions author-only docs such as
  `docs/prescribed-skill-closeout-contract.md`.
- Improved validator errors so author-repo cite failures include the offending
  markdown filename.
- Expanded portable-authoring guidance from docs/tests to docs, tests, and
  source-tree skill paths.

### Over-Worry

- The nearby marker escape remains intentionally broad enough to cover about
  three lines, matching #264.
- Fenced code blocks remain ignored to avoid recreating the reverted
  over-broad scan that flagged examples and operator surfaces.

### Valid But Defer

- Root `scripts/...` references are an adjacent portability class but outside
  this issue's explicit docs/tests/source-tree skill boundary. If they need
  policy, file a separate install-surface issue instead of widening #264.
- Non-backticked prose paths and markdown link targets remain outside this
  guard. The current corpus and #264 examples are backtick-shaped; broad prose
  parsing risks the old overreach.

## Next Move

Run aggregate closeout, then commit the validator, sweep, critique packet, and
goal slice evidence together. Do not claim live GitHub issue closure.
