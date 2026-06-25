# Release 0.55.1 Critique

## Execution

Fresh-Eye Satisfaction: `parent-delegated`.
Packet Consumed: `charness-artifacts/critique/release-0-55-1-packet.md`.
Target: `release-critique.md`.

## Reviewer Tier Evidence

- requested tier: `high-leverage`
- requested spawn fields: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
- host exposure state: requested_fields_sent
- application state: unverified-by-packet

## Release Scope

Version: `0.55.1`.
Tag: `v0.55.1`.
Change: patch release for #401 closeout after the `critique` packet ownership
fix and the `spec` / `impl` quality-led review record.

## Surface-Lock Inventory

- Public skill text: `skills/public/critique/SKILL.md`,
  `skills/public/critique/references/prepare-packet.md`.
- Checked-in plugin export: `plugins/charness/skills/critique/SKILL.md`,
  `plugins/charness/skills/critique/references/prepare-packet.md`.
- Quality artifacts: `charness-artifacts/quality/history/2026-06-25-critique-skill-quality-review.md`,
  `charness-artifacts/quality/2026-06-25-spec-impl-skill-quality-review.md`,
  `charness-artifacts/quality/latest.md`.
- Release and pickup surfaces: `charness-artifacts/release/v0.55.1-notes.md`,
  `docs/handoff.md`.
- Issue closeout: GitHub issue `corca-ai/charness#401`.

## Findings

### Act Before Ship

- Do not pass the prepare packet as the release critique proof. This artifact is
  the final critique proof; the packet is only input evidence.
- Publish with the explicit closeout and notes inputs:
  `--part patch`, `--notes-file charness-artifacts/release/v0.55.1-notes.md`,
  `--close-issue 401`, and `--close-issue-repo corca-ai/charness`.

### Bundle Anyway

- The stale `docs/handoff.md` queue line that said #401 continued with
  `critique` / `spec` / `impl` was corrected before release.
- The notes wording was tightened so the `critique` change names packet
  ownership behavior, not only wording.
- Commit this critique artifact, the prepare packet, the release notes, and the
  handoff correction before invoking the publish helper.

### Over-Worry

- Version surfaces still showing `0.55.0` before publish is expected. The release
  helper should own the patch bump and manifest sync.
- Fresh-checkout probes not being manually run before the helper is acceptable;
  the helper owns running and recording them before tag push.
- Real-host proof is not required for this slice because configured real-host
  triggers did not match the changed skill/artifact surfaces.

### Valid But Defer

- The release planner does not surface `--notes-file` and `--close-issue` in its
  command model. That is a future helper UX improvement, not a v0.55.1 blocker.

## Operator Action Required

- Run publish dry-run with the same command shape intended for execute.
- Execute only after the dry-run succeeds and this artifact is tracked.

## Upgrade Path

- No migration is required.
- Operators run `charness update`.
- Active sessions should be restarted or refreshed before relying on the
  updated installed skill text.

## Deliberately Not Doing

- No live evaluator-backed dogfood proof for `spec` or `impl` is claimed in this
  release. That stays a follow-up when a concrete behavior log or regression
  prompt exists.
