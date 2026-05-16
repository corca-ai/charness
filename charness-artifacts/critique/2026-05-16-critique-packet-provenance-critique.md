# Critique Packet Provenance Critique

Date: 2026-05-16
Target: code critique for `e8b4094 Preserve committed diff context in critique packets`
Fresh-Eye Satisfaction: parent-delegated
Packet Consumed: `charness-artifacts/critique/2026-05-16-critique-packet-fix-review-packet.md`

## Change

The reviewed change added committed-diff support for critique prepare packets
so reviewers can inspect the actual commit or range instead of a clean working
tree.

## Angles

- Michael Jackson / problem framing: confirmed the change solves the intended
  committed-diff packet context problem rather than a broad adjacent workflow.
- Gerald Weinberg / diagnostic: checked root-cause coverage for argument
  passing, git ref semantics, environment leakage, and generated exports.
- Atul Gawande / operational checklist: checked packet auditability, stale
  artifact risk, CLI evidence, and portable paths.
- Counterweight: separated auditability blockers from later semantic expansion.

## Counterweight Triage

### Act Before Ship

1. Packet envelope must record the actual reviewed ref.
   - Resolution: implemented.
   - `changed_ref` is now part of the JSON envelope and markdown render, and
     `validate_critique_packet.py` requires the key.
2. Default working-tree packets must not inherit ambient
   `CHARNESS_CRITIQUE_CHANGED_REF`.
   - Resolution: implemented.
   - Script section execution now clears the env var unless the runner received
     an explicit `--changed-ref`.
3. Default-section docs must not advertise unsupported producer flags.
   - Resolution: implemented.
   - The stale `--json` producer example was removed.
4. Operator-facing CLI behavior needs an end-to-end regression.
   - Resolution: implemented.
   - Tests now invoke `prepare_packet.py --json --changed-ref HEAD` against the
     real changed-surface producer.
5. Packet `adapter_path` must be portable.
   - Resolution: implemented.
   - Packet JSON and markdown now use repo-relative adapter paths.
6. Review packets used as closeout evidence must be tracked.
   - Resolution: implemented.
   - The current review packet JSON/Markdown sidecars are included in this
     follow-up slice.

### Bundle Anyway

1. Single-ref git handling should cover root and merge commits.
   - Resolution: bundled.
   - `diff-tree` now uses `--root -m`.
2. Range semantics should be explicit.
   - Resolution: bundled.
   - The prepare-packet reference now states `A..B` is an endpoint diff, not
     every touched-and-reverted file in the range.

### Valid But Defer

1. A future "all files touched by every commit in range" mode is valid but a
   separate contract from the current endpoint-diff mode.

### Over-Worry

1. No concerns were pure style-only objections; the accepted fixes were all
   tied to auditability, portability, or realistic command behavior.

## Next Move

Run targeted packet tests, regenerate plugin exports, run slice closeout, then
commit the provenance repair.
