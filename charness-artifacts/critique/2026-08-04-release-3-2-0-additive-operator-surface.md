# Release 3.2.0 additive operator surface
Date: 2026-08-04

## Decision Under Review

Whether to cut Charness 3.2.0 from the current 3.1.1 surfaces after the
#503 opt-in `retro --detail` operator receipt and the #496 hollow-refill repair
are locally proven. The release must synchronize all plugin/version surfaces,
preserve proof boundaries, and publish only after independent readback.

## Release Scope

Target `3.2.0`, tag `v3.2.0`. Minor is justified because `--detail` is a new
additive operator-facing capability; the #496 behavior repair is included in
the same compatible release. The default miner retains its prior handling of
non-finite elapsed values; only the opt-in detail receipt uses finite-only
summaries. No gate is weakened, no telemetry schema changes, and no remote
issue is closed by this release. The release also contains all unreleased
changes since `v3.1.1`, not only this goal's #503/#496 slices; the final
candidate inventory must be read from the frozen release diff.

## Surface-Lock Inventory

- Generated release surfaces: `packaging/charness.json`, Claude/Codex plugin
  manifests, marketplace version metadata, checked-in `plugins/charness`, and
  release notes/artifact.
- Consumer-visible behavior: opt-in retro detail output; quality bootstrap
  warning and mutation command refill semantics; default miner behavior and
  ordinary finite-stream output remain compatible, with non-finite default
  handling explicitly preserved.
- Documentation/operator surfaces: release notes, `charness update`,
  `charness version`, `charness doctor`, and `docs/handoff.md` baton state.
- Adapter/integration surfaces: `.agents/release-adapter.yaml` commands and
  declared fresh-checkout/real-host proof triggers.

## Failure Angles

- Gawande: a green local gate could precede an unsynchronized manifest, stale
  installed plugin, or unrun fresh-checkout probe. The release helper and final
  lock must prove each in order.
- Minto: release notes could turn local measurements into claims of runtime
  relief or describe #496 as a remote issue closure. The record needs explicit
  measured/non-claim language and a claims review after the notes exist.
- Raskin: an additive flag or warning repair can still surprise operators if
  update instructions, default output, or rollback expectations are unclear.
  The upgrade path must say `--detail` is opt-in and default behavior is
  unchanged.
- Jackson: the release should be framed by the operator problem solved—an
  actionable recurring-cost receipt and trustworthy customization warning—not
  by internal slice names alone.
- Weinberg: #503's cost report and #496's semantic predicate are distinct
  owners; bundling them in one version must not merge their claims.

## Counterweight Pass

- Act Before Ship: synchronize every required version surface; run final broad
  proof, fresh-checkout probes, and the release helper's dry-run; bind release
  critique and post-notes claims review; read back remote commit/CI and public
  release through distinct channels.
- Bundle Anyway: include concise operator update/rollback instructions, the
  `--detail` default-compatibility note, the #503 zero-relief non-claim, and
  the #496 remote-open non-claim in release notes.
- Over-Worry: do not add real-host nose/tool installation proof when the
  release trigger detector reports no matching changed surface; do not invent
  compatibility migrations for an opt-in flag and preserved defaults.
- Valid but Defer: deeper telemetry normalization, broad semantic-inertness
  taxonomy, and remote issue closure remain future work with their existing
  reopen triggers.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: packaging/charness.json and checked-in plugin manifests | action: fix | note: synchronize and verify every version surface before the release commit/tag; never hand-edit generated manifests.
- F2 | bin: act-before-ship | evidence: strong | ref: .agents/release-adapter.yaml and final verification lock | action: fix | note: run the broad final gate, fresh-checkout probes, release dry-run, and independent commit/CI readback before public release claims.
- F3 | bin: act-before-ship | evidence: strong | ref: release notes and charness-artifacts/issue/2026-08-04-goal-midpoint-claims-review.md | action: fix | note: bind a post-notes claims review that distinguishes measured #503 cost, zero relief, #496 repair scope, and remote non-claims.
- F4 | bin: bundle-anyway | evidence: moderate | ref: docs/handoff.md and .agents/release-adapter.yaml | action: document | note: record operator update commands, installed refresh/readback, and baton reconcile in the release artifact.
- F5 | bin: over-worry | evidence: strong | ref: release planner real-host trigger packet | action: defer | note: no configured real-host surface matches this release delta, so do not fabricate tool-install proof.
- F6 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/issue/2026-08-04-issue-503-local-closeout.md | action: defer | note: remote issue closure and runtime relief measurement remain out of scope with explicit reopen triggers.
- F7 | bin: act-before-ship | evidence: strong | ref: skills/public/retro/scripts/mine_closeout_telemetry.py:219 | action: fix | note: preserve legacy default non-finite elapsed handling while keeping finite-only filtering inside --detail; add a regression test and resynchronize the plugin mirror.
- F8 | bin: act-before-ship | evidence: moderate | ref: Upgrade Path and installed skill layout | action: document | note: use the skill-resolved `$SKILL_DIR/scripts/mine_closeout_telemetry.py --detail` form and document rollback from a v3.1.1 source checkout with version/doctor readback.
- F9 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_execute.py:164 | action: document | note: plan an explicit branch-push/remote-CI readback before the public release/tag step, or record the helper's ordering as an honest unresolved release-boundary limitation; do not imply the helper's terminal green proves CI.

## Operator Action Required

Before ship: run final verification lock and fresh-checkout probes, sync and
inspect release surfaces, run release dry-run, create release notes, and
complete the release claims review. The pre-version-bump bundle is now bound by
`charness-artifacts/release/v3.2.0-candidate-scope.md`; the final release
commit must still record its exact SHA after the version bump. Push the branch, then
independently verify the exact remote commit and CI before tag/public release;
if the repo helper cannot interpose that readback, stop and record the
limitation rather than calling the release complete. After publication,
independently verify public visibility, installed refresh/readback, and handoff
baton reconciliation.

## Frozen Candidate Scope

The pre-version-bump bundle is frozen at `e7bc7eaf780e7ce89d9866c450d3bc7107907c75`
against base `v3.1.1` (`7fa4a776909241bda02949fd851edfb54212b259`). The exact
14-commit log and 118-path name-status inventory, plus the operator summary,
are recorded in `charness-artifacts/release/v3.2.0-candidate-scope.md`. This
scope includes every unreleased change since `v3.1.1`, not only this goal's
two slices. The subsequent version-bump/release-content commit is a separate
candidate and must be bound by the generated release evidence before tag/public
publication.

## Upgrade Path

Operators update with `charness update`, then use `charness version` (expecting
`3.2.0`) and `charness doctor` for readback. The new telemetry receipt is
opt-in through the retro skill's resolved script path:
`python3 "$SKILL_DIR/scripts/mine_closeout_telemetry.py" --repo-root . --detail`;
the default miner output and proof gates remain unchanged. To roll back, use a
source checkout at the prior `v3.1.1` tag and run
`charness update --repo-root <v3.1.1-checkout> --no-pull --skip-cli-install`,
then verify the rollback checkout itself with
`charness version --repo-root <v3.1.1-checkout>` and
`charness doctor --repo-root <v3.1.1-checkout>`. Release notes must state that
remote issue closure and measured runtime relief are not claimed.

## Local / Remote Proof Status

- Local: focused #496/#503 proof, final deterministic closeout, and the final
  broad verification lock are green; durable broad-proof record:
  `.charness/closeout/broad-pytest-proof.json`, latest lock
  `2026-08-04T02:25:42Z`, 46.31 seconds.
- Source-tree startup probes: the three declared probes passed in the current
  source tree; this is not yet a durable clean-checkout receipt.
- Remote branch/CI: not yet pushed or independently read back.
- Public release/tag: not yet created or independently verified.
- Installed refresh/baton: not yet run; the release helper's post-publish tail
  must record both without treating a non-blocking refresh failure as success.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: unverified — host returned findings but exposed no provider-application confirmation
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — the clean delegated release critique round is complete:
Gawande, Minto, Raskin,
and the counterweight observer returned findings with clean boundary windows
`release2-gawande`, `release2-minto`, `release2-raskin`, and
`release2-counterweight`. Their required repairs are recorded above and remain
the pre-version-bump scope is now frozen in the candidate-scope record. The
separate claims review is recorded
at `charness-artifacts/issue/2026-08-04-release-3.2.0-claims-review.md`; it
accepted the claims with four explicit pre-ship conditions. The first release
critique round is quarantined:
all four boundary verifies reported `boundary-drift` because the parent repaired
the miner while those reviewers were still reading; none of those findings is
counted as release approval.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-04-release-3-2-0-additive-operator-surface-packet.md
- Packet path: charness-artifacts/critique/2026-08-04-release-3-2-0-additive-operator-surface-packet.json
- Packet SHA256: d3b64cec6422c9d763a4a6e56b944910237238b73d4c4566210db94848651da2
- Identity SHA256: 96d5dd884089d5b99f6cc128e2c06810be77db985c80e20e8a4f80da1498083c

## Boundary Ownership

- Producer: release helper, version/manifests, release notes, and the two repaired source surfaces.
- Consumer: operators upgrading Charness, maintainers reading the release record, remote CI, and public release surface.
- Owning surface: release contract plus synchronized plugin/install surfaces.
- Verdict: owned-correctly
