# Release Critique
Date: 2026-07-09

## Execution

- Target reference: `skills/public/critique/references/release-critique.md`
- Release skill references read: `version-policy.md`, `critique-boundary.md`,
  `publication-boundary.md`, `install-refresh.md`, and `real-host-proof.md`.
- Planner command: `python3 skills/public/release/scripts/plan_release_run.py --repo-root . --json`
- Update-instructions prep:
  `python3 skills/public/release/scripts/publish_release.py --repo-root . --part minor --prep-update-instructions`

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

Transient prepare packet generated at `2026-07-09T11:25:12Z` for
`v0.63.0 release critique`; consumed by parent before reviewer spawn and
summarized in this artifact. The generated packet file is not committed because
the release critique artifact is the durable proof.

## Target

Release critique.

## Change

Publish Charness `v0.63.0` as a minor release from `0.62.0`, using the
repo-owned release helper.

## Capability At Stake

Operators should receive the new advisory prompt-mutation and friction-reducer
surfaces without a misleading release story, stale install metadata, or a
publish that skips required release-time proof.

## Release Scope

- Current version before release helper mutation: `0.62.0`
- Target version: `0.63.0`
- Tag: `v0.63.0`
- Bump rationale: minor, because the release adds maintained operator-facing
  evaluation helpers and policy surfaces without breaking existing callers.

## Surface-Lock Inventory

- Generated/install surfaces: `packaging/charness.json`,
  `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`,
  `plugins/charness/.claude-plugin/plugin.json`,
  `plugins/charness/.codex-plugin/plugin.json`.
- Consumer-visible behavior: advisory prompt-mutation helpers, blind workspace
  preparation, clean-proof/blinding scans, duplicate-ratchet triage helper, goal
  closeout normalization helper, and plugin-sync change summaries.
- Documentation surfaces: `docs/prompt-mutation-policy.md` and release notes
  `charness-artifacts/release/v0.63.0-notes.md`.
- Adapter/integration surfaces: integration/control-plane changes in the release
  delta trigger real-host proof recording.

## Angles

- Atul Gawande / operational checklist: checked release cleanliness, version
  bump sequencing, fresh-checkout probes, and real-host proof trigger scope.
- Barbara Minto / structure: checked release notes against the full tag delta
  and required non-claims.
- Jef Raskin / humane interface: checked first-touch helper behavior and update
  instructions.
- Counterweight: separate subagent triage after the preflight-helper fix.

## Findings

- Operational review found the release must not publish while only the critique
  packet is untracked; the critique packet and artifact are now part of the
  release-prep commit before dry-run.
- Operational review confirmed version bump and manifest sync must be performed
  by the release helper before tag push.
- Operational review confirmed fresh-checkout probes are configured and must be
  recorded by the publish path.
- Operational review found the actual release delta triggers real-host proof;
  the release artifact must record that proof or the post-publish refresh
  disposition.
- Structure review found release notes must cover the full `v0.62.0..HEAD` tag
  delta without claiming prompt deletion, clean blinding, or a new gate.
- Humane-interface review found `prompt_mutation_clean_proof_preflight.py`
  previously looked clean with no inputs and returned nonzero for advisory
  findings. The helper now reports `no_inputs` as a no-claim and exits zero for
  advisory findings while setting `clean_proof_claim: false`.
- Update-instructions prep emitted a generic suggestion even though
  `update_instructions_stale: false`; the existing adapter text is clearer and
  is intentionally preserved.

## Counterweight Triage

- Act Before Ship: commit tracked critique proof and release notes; run release
  helper dry-run and execute path so version bump, sync, fresh-checkout probes,
  tag push, public release verification, and install refresh are recorded.
- Bundle Anyway: include explicit non-claims in release notes and keep
  prompt-mutation helpers described as advisory/read-only.
- Over-Worry: do not enumerate every capture artifact or historical commit in
  release notes; a concise grouped narrative is enough.
- Valid but Defer: a longer prompt-mutation operator guide can follow later.

## Operator Action Required

- Before publish: use the release helper with
  `--part minor --notes-file charness-artifacts/release/v0.63.0-notes.md` and
  this critique artifact.
- After publish: run or record the helper-managed install refresh and tell
  operators to run `charness update`.

## Upgrade Path

Run `charness update`. No migration is required for existing users. Active host
sessions may need restart after cache rotation.

## Deliberately Not Doing

- Not changing `.agents/release-adapter.yaml` update instructions; current
  concrete `charness update` guidance is better than the generic prep
  suggestion.
- Not turning prompt-mutation helpers into blocking gates.

## Next Move

Commit this critique proof, release notes, and the advisory-preflight fix; then
run the release helper dry-run followed by execute after the plan is clean.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `charness-artifacts/critique/2026-07-09-112512-packet.md` | action: fix | note: critique packet and release critique must be tracked before publish helper can run from a clean tree.
- F2 | bin: act-before-ship | evidence: strong | ref: `skills/public/release/scripts/publish_release.py --repo-root . --part minor` | action: fix | note: version bump, manifest sync, fresh-checkout probes, tag push, and public verification must run through the release helper.
- F3 | bin: act-before-ship | evidence: strong | ref: `scripts/prompt_mutation_clean_proof_preflight.py` | action: fix | note: no-input clean-looking run and advisory nonzero exit were fixed before release.
- F4 | bin: bundle-anyway | evidence: strong | ref: `charness-artifacts/release/v0.63.0-notes.md` | action: document | note: release notes record advisory/read-only status and prompt-mutation non-claims.
- F5 | bin: valid-but-defer | evidence: moderate | ref: `docs/prompt-mutation-policy.md` | action: defer | note: a fuller end-to-end operator guide is useful but not required for this release.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: host accepted requested reviewer fields; reviewers returned bounded findings through `multi_agent_v1`.

## Boundary Ownership

- Producer: release helper and release notes produce version/publication facts.
- Consumer: operators updating Charness and future maintainers reading the
  release ledger.
- Owning surface: release artifact plus GitHub release notes.
- Verdict: owned-correctly
