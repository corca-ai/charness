# Release 8.4.1 docs-cut critique

Date: 2026-09-04

- Packet Consumed: charness-artifacts/critique/release-8-4-1-packet.md

## Decision Under Review

Release charness 8.4.1 (patch) carrying the post-8.4.0 docs identity-dump cut
and the deletion of the deferred-decisions register and how-to page.

## Release Scope

- Version 8.4.1, tag `v8.4.1`, patch: docs and skill references stop recopying
  mechanism identity; `docs/deferred-decisions.md` is deleted. No new public
  CLI, skill, or install surface. No issue closeout.
- For consumers: `charness update`, then restart the host. A bookmark to
  `docs/deferred-decisions.md` is a missing page. Closed choices live in owning
  mechanisms or the dated archive.

## Surface-Lock Inventory

- Generated: packaging and marketplace versions still `8.4.0` until the helper
  stamps; untracked `plugins/` is synced by the helper.
- Consumer-visible behavior: none registered. Doctor, CLI help, and install
  path unchanged.
- Documentation: `docs/` and public skill references; `docs/deferred-decisions.md`
  deleted. README and `AGENTS.md` point at owning pages.
- Adapter: `.agents/quality-adapter.yaml` tracking allowlist no longer names
  the deleted page.

## Verification Scope Decision

- Claim under test: current docs and first-touch surfaces do not teach adding
  a deferred-decisions row or recopying mechanism identity; the how-to page is
  gone, not redirected; patch not minor because no registered public surface
  moved.
- Changed surfaces: `docs/`, public skill references, `AGENTS.md`, `README.md`,
  T-signal catalog, quality-adapter allowlist, archive stamp; final consumer is
  an installed plugin after `charness update`.
- Minimum sufficient proof: `./scripts/check-docs.sh` PASS; focused T-signal
  and operator-acceptance tests; two parent-delegated bounded reviewers
  (Gawande, Raskin).
- Deliberately omitted checks: live consumer-repo dogfood of the 404; rewriting
  frozen `charness-artifacts/` history that still cites the old path.
- Verifier contract: `scripts/review/validate_critique_artifacts.py`,
  unchanged in this slice.
- Failure classification: none
- Negative control: command ./scripts/check-docs.sh | expected refusal: broken link to docs/deferred-decisions.md | observed result: PASS, orphans 0 | receipt: check-docs 2026-09-04
- Subject identity: sha256:380150284787723f9cdd46e82d95292c48b05617cc417202e6840e25c7be8982
- Verifier identity: sha256:fdae081f53f503cfc7eb37bd0790ab07ad0ee04855e2af9f0bf6d47f11c5ae08
- Input identity: sha256:1b35f452f6e01106fc572fd2f9b6be9ee4bc3ebf77ac1a5f15962e7c52133c15
- Failure identity: stable:none
- Evidence identity: none
- Retry disposition: first-attempt
- Retry key: sha256:2c396e78b944d5beca4640c4843007aede7b7913c549138e7b6ef197e09ea56f

## Failure Angles

- Unauthored notes recur: 8.4.0 shipped a generated changelog line only.
  Passing `--notes-file` with an authored Summary is the mitigation.
- Slice-reopen treated as a release-lane pass: it is the commit-msg exception;
  the helper runs `--release` before tag.
- Leftover live invitation: named leftovers were removed; spec/issue Deferred
  Decisions language is a different contract.

## Counterweight Pass

- Act Before Ship: none that hold starting the publish helper. Do not tag by
  hand. Do not treat Slice-reopen commits as `./scripts/run-quality.sh --release`.
- Bundle Anyway: authored GitHub notes that name the 404 (Gawande F1, Raskin
  F1). Pass `--notes-file`; do not rely on `--generate-notes` and a later
  `gh release edit`.
- Over-Worry: plugin mirror missing a cut (helper sync); doctor-on-clone
  (declared probe); leftover current-docs invitations (named leftovers gone);
  archive historical paste still looking like a how-to (stamp is enough).
- Valid but Defer: copy-held-by-test inventory row that still names the
  deleted page as a dump site (Raskin F2); historical comments and lessons
  that cite the old path; remaining over-budget teaching pages.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/latest.md | action: fix | note: 8.4.0 shipped unauthored notes; 8.4.1 passes --notes-file so the 404 is named (Gawande F1, Raskin F1).
- F2 | bin: over-worry | evidence: strong | ref: scripts/hooks/check_release_lane_receipt.py | action: document | note: Slice-reopen is the commit-msg exception, not a release-lane receipt; KEEP helper --release (Gawande F2).
- F3 | bin: over-worry | evidence: strong | ref: .agents/release-adapter.yaml | action: document | note: helper sync_command owns plugin/manifest stamp; do not tag by hand (Gawande F3).
- F4 | bin: over-worry | evidence: strong | ref: charness-artifacts/spec/2026-09-04-deferred-decisions-archive.md | action: document | note: named leftover invitations are gone from current docs; spec/issue Deferred Decisions language is KEEP (Gawande F5, Raskin).
- F5 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/spec/2026-09-04-copy-held-by-test.md | action: defer | note: inventory row still names the deleted page as a dump site; record-layer, not first-touch (Raskin F2).

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: typed host bounded-reviewer, unnamed spawn
- Host exposure state: requested_fields_sent
- Application state: n/a
- Delivery state: findings-received
- Execution mode: typed-subagent

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/release-8-4-1-packet.json
- Packet sha256: c9b323ac70ab7ac4e9c0699cb25c6ecabf872df9c65c595a034ba64c364181f8
- Identity sha256: 1b35f452f6e01106fc572fd2f9b6be9ee4bc3ebf77ac1a5f15962e7c52133c15

```bash
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8-4-1-packet.json --packet-sha256 c9b323ac70ab7ac4e9c0699cb25c6ecabf872df9c65c595a034ba64c364181f8 --identity-sha256 1b35f452f6e01106fc572fd2f9b6be9ee4bc3ebf77ac1a5f15962e7c52133c15
```

## Boundary Ownership

- Producer: current docs and skill references after the identity-dump cut.
- Consumer: installed plugin after `charness update`.
- Owning surface: documentation principles plus the deferred-decisions archive.
- Verdict: owned-correctly

## Operator Action Required

None that hold the helper. Authored notes are bundled in this publish via
`--notes-file`. After publish: `charness update` then `charness version`.

## Upgrade Path

`charness update`. No CLI or install migration. A bookmark to
`docs/deferred-decisions.md` 404s. Rollback: 8.4.0.
