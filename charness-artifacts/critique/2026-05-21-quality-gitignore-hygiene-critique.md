# Quality Gitignore Hygiene Critique
Date: 2026-05-21

## Execution

- status: executed
- Fresh-Eye Satisfaction: parent-delegated
- Packet Consumed: `charness-artifacts/critique/2026-05-21-075937-packet.md`
- Target: code/workflow critique for quality gate promotion

## Change

Promote quality gitignore scan hygiene from advisory inventory to a standing
`run-quality` phase after replacing raw broad scans with git-visible file
discovery, refreshing the quality artifact, syncing plugin exports, and removing
stale hard-coded quality phase counts from operator docs.

## Angles

- regression/compatibility
- maintainability/scope
- counterweight triage

## Act Before Ship

- Fixed: `inventory_gitignore_scan_hygiene.py` now has `--require-empty`, and
  `scripts/run-quality.sh` passes it so findings fail the standing phase.
- Fixed: detector context is now function-scoped instead of file-scoped, so a
  git-aware helper in one function no longer hides a raw broad scan elsewhere.
- Fixed: `tests/quality_gates/support.py` and `test_quality_runner.py` now cover
  the new runner label and required flag.
- Fixed: plugin export was re-synced after the root-side changes.
- Fixed: `inventory-consumer-fields.json` now records run-quality pass/fail as
  the consumer for `inventory_gitignore_scan_hygiene.py`.

## Bundle Anyway

- Direct `git ls-files --cached --others --exclude-standard` use in quality
  helper scripts is acceptable for this slice; centralizing it is useful but
  not needed for the gate outcome.
- The quality artifact archive and operator docs drift fix are appropriate to
  bundle with the gate promotion.

## Over-Worry

- Do not create a PR CI workflow in this slice; the artifact correctly frames
  that as maintainer policy, not an accidental implementation omission.
- Generated plugin export churn is expected and verified by the sync step.

## Valid But Defer

- Consider a shared git-visible discovery helper for quality skill scripts if
  more inventories copy the subprocess block.
- Revisit optional inventory fallback strictness separately; the immediate
  installed-surface issue was export parity.

## Next Move

Run the full quality gate after sync, then commit the source, plugin export,
quality artifacts, critique artifact, and generated SLOC/find-skills state
together.
