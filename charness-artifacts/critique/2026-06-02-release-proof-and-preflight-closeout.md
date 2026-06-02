# Critique: Release Proof And Adapter Preflight Closeout

Date: 2026-06-02
Fresh-Eye Satisfaction: parent-delegated
Packet Consumed: `charness-artifacts/critique/2026-06-02-020158-packet.md`
Target: release / workflow preflight

## Scope

Closeout critique for two follow-ups after `v0.14.0`:

- capture and record the remaining `tokei` real-host proof;
- make release adapter changes run focused preflight before publish mutation.

## Angles

- Release proof and checklist correctness.
- Release-helper compatibility and pre-mutation automation.
- Counterweight triage after fixes.

## Counterweight Triage

### Act Before Ship

- Fixed: proof was initially partial. It now captures missing-binary doctor
  behavior, a real temp-home `cargo install tokei --root ... --force`,
  `tokei --version`, doctor detection of the temp-home binary, and non-dry-run
  `charness tool sync-support tokei --json` returning `skipped`.
- Fixed: `tokei` is integration-only, so the release checklist and latest
  release artifact now expect sync-support `skipped` with
  `integration has no support_skill_source` instead of materialized support.
- Fixed: adapter preflight originally only watched `.agents/release-adapter.yaml`.
  It now watches all release adapter candidate paths supported by the resolver.
- Fixed: minimal-repo fallback could reference `test_release_backend.py` when
  only `test_release_real_host.py` existed. The fallback now requires both files.
- Fixed: publish CLI ordering is covered; a focused preflight failure blocks
  before bumping the packaging manifest or running quality.

### Bundle Anyway

- Applied: fallback-path preflight tests now assert the resolver command is in
  the planned focused command list, not only the real-host test command.

### Valid But Defer

- Multiple adapter files present at once can still be conceptually tricky: a
  lower-priority adapter file may change while a higher-priority canonical
  adapter remains active. The current behavior is acceptable because `.agents`
  is the canonical adapter path and fallback files are compatibility paths.

### Over-Worry

- Requiring `charness tool install tokei` specifically would be too narrow. The
  release checklist permits cargo, brew, or an upstream binary; the captured
  temp-home cargo install plus PATH-scoped doctor-ok result is sufficient proof.

## Result

No remaining Act Before Ship findings.
