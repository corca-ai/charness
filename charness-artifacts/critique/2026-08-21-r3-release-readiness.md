# R3 Release Readiness Critique — blocked before version mutation

Date: 2026-08-21

## Decision Under Review

Whether the integrated semantic candidate at `22ea27d7847d7f44d8258cae19fea7bf0ee5c4d5`
can be versioned as the next Charness patch release. This is a pre-version,
pre-publish critique. It is not a release approval and it does not select a
version, tag, publication channel, issue closeout, or host-runtime claim.

The candidate carries structural repairs for typed fresh-eye delivery,
post-commit evidence basis, boundary continuation, artifact persistence, and
installed-layout planning. The user-visible promise is narrower and more
important than the issue count: an operator must not mistake process success,
source parity, a clean fingerprint, or a stale installed copy for delivered
behavior or reviewer approval.

## Release Scope

The lightest currently plausible bump is a patch (`6.2.0` to `6.2.1`) because
the observed work is primarily reliability, validation, packaging, and evidence
boundary repair. The target remains unselected until the release planner binds
the exact candidate, rationale, generated surfaces, and post-bump proof. No
version surface was mutated in this review.

## Surface-Lock Inventory

- Source behavior: reviewer delivery state machine, typed result/receipt joins,
  timeout and path/cwd boundaries, retro basis and artifact persistence.
- Checked-in export and package surfaces: Claude/Codex plugin mirrors,
  packaging manifest, marketplace/version metadata, generated CLI and skill
  references.
- Consumer behavior: root CLI init/update status and exit semantics, installed
  `#685` artifact persistence, installed `#686` retro planner path, version and
  doctor readback.
- Evidence surfaces: current-open issue table, current requalification packet,
  goal, handoff, release ledger, critique packet, delivery ledger, receipts,
  and claims review.
- External boundaries: clean checkout, managed install/update, real-host
  checklist, public/tag readback, and per-issue tracker closeout.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium,
  service_tier=priority, fork_turns=none
- Host exposure state: metadata-hidden
- Application state: unverified; worker logs report model=gpt-5.6-luna and
  reasoning effort=max, with service-tier/fork application unreported
- Delivery state: findings-received

## Fresh-Eye Delivery Evidence

- Packet consumed:
  `charness-artifacts/critique/2026-08-21-r3-semantic-candidate-packet.md`
- Packet SHA256:
  `80d8bee2d001bbee87544c865c94375201bd9f2eab5cd9d6e940f6106782f40e`
- Reviewed-input identity:
  `8c19268780e88e3890b26e07aa952d7a048a0510cd4eeff5e02f9b2834faebb9`
- Boundary snapshot SHA256:
  `1a0bb3bffe000aa9d293eb6561ea0279aed701f475c0b4b987d3ca84f20e4f67`
- Boundary window:
  `r3-release-critique-20260821b`
- Boundary verification after each worker: `ok: true`, `drift: []`.
- Execution: four independent Charness-owned file-backed `codex_exec`
  workers; three operational angles plus a separate counterweight.
- Delivery: all four typed receipts were terminal `succeeded`, their delivery
  ledger states were `findings-received`, provenance and result schemas matched,
  and each report was `approval_eligible: false` because the semantic verdict
  was `block`.
- Requested tier: `high-leverage`; requested fields were
  `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`,
  `fork_turns=none`.
- Host exposure: worker logs exposed `gpt-5.6-luna` and `reasoning effort: max`;
  application of the adapter-requested model/effort/service tier is therefore
  unverified and not claimed.

Fresh-Eye Satisfaction: parent-delegated. Four independent file-backed workers
delivered typed findings, but this artifact records no approval: all four
semantic verdicts were `block` and `approval_eligible` was false.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-21-r3-semantic-candidate-packet.md`
- Packet path: `charness-artifacts/critique/2026-08-21-r3-semantic-candidate-packet.json`
- Packet SHA256: `80d8bee2d001bbee87544c865c94375201bd9f2eab5cd9d6e940f6106782f40e`
- Identity SHA256: `8c19268780e88e3890b26e07aa952d7a048a0510cd4eeff5e02f9b2834faebb9`

## Angle Findings

### Gawande — operational release path

- `R3-ACT-01`: the historical `#682`–`#687` release-blocker rows are not yet
  converted into candidate-bound dispositions. Hold the cut and append one
  evidence-backed ledger amendment per exception.
- `R3-ACT-02`: source and checked-in export repairs exist, but installed 6.2.0
  still reproduces the `#685` warning and `#686` unavailable source-layout
  path. A candidate managed install/update and semantic readback are required.
- `R3-ACT-03`: candidate packaging and clean-clone/install proof are not yet
  established. The worker's inability to obtain a writable temporary directory
  is an environment limitation, not product evidence; it must remain unproven,
  not become green by omission.
- `R3-ACT-04`: the no-target planner's `real_host.required: false` is worktree
  scope, not target release scope. A target-bound plan may require the declared
  real-host checklist.
- `R3-ACT-05`: no target-bound release record, claims review, post-bump proof,
  or publication dry-run exists.

### Minto — structure and first-reader communication

- `M1`: `current-open-surface.md` contains historical pre-admission language
  beside the later post-lock exception admission, so one reader can derive
  incompatible scope answers.
- `M2`: source, export, installed, host, and release-cleared states are
  compressed into dispositions that read too much like success.
- `M3`: “R3 semantic candidate” is not visibly pre-version and can be mistaken
  for the post-bump release candidate.
- `M4`: older receipts and the `331c4a230` requalification endpoint can be
  mistaken for fresh proof of `22ea`. The `331c4a230..22ea` range is
  documentation/evidence-only, which must be stated as an explicit no-source-
  diff join rather than implied.
- `M5`: the first reader cannot yet recover one consumer problem statement or a
  concrete upgrade/rollback action from the evidence surfaces.

### Raskin — humane operator boundary

- `RASKIN-001`: root `init`/`update` can return exit 0 while a failed Codex host
  installation or cache refresh is present in the nested YAML status. This is
  the same core failure class as process/media success being confused with
  delivery success. The top-level exit contract and regression coverage need a
  source repair before release.
- `RASKIN-002`: candidate managed install/update and installed version, doctor,
  persistence, and planner readback are absent.
- `RASKIN-003`: persistence can succeed while a protected lessons summary is
  not refreshed; keep the primary artifact success split, but make the
  `summary_refreshed: false` next action more visible.

### Counterweight

The counterweight confirmed that `#681` is already satisfied, the bare `#682`
post-commit invocation is intentionally `not-established` rather than a false
negative, the supported `#683` continuation is the emitted `verify --before`
form, and host-side `#687` terminal-event reconstruction is not required for a
Charness-owned child when the non-claim is explicit. It nevertheless classified
the installed `#685/#686` boundary, complete current candidate inventory, and
target-bound release plan as Act Before Ship.

## Operator Action Required

Before version mutation:

1. Repair the root CLI top-level exit contract for explicit host-delivery
   failure, preserving distinct `skipped`/`unavailable` optional-host outcomes,
   and add focused regression cases.
2. Replace contradictory current-open prose with one authoritative table whose
   independent fields distinguish source, export, installed, host, and release
   status. Mark the earlier pre-admission observations as historical.
3. Rebind the requalification to the exact current head. Since
   `331c4a230..22ea` is documentation/evidence-only, record that no-source-diff
   join explicitly; do not call the old command outputs fresh candidate proof.
4. Rename this pre-version critique/packet role clearly and add the first-reader
   consumer outcome, plus explicit “not actionable before publication”
   upgrade/rollback wording.
5. Rerun focused and changed-line proof over the CLI repair and documentation
   contract, then run a target-bound release planner with the exact changed
   range.

At the versioned candidate boundary:

1. Synchronize all source/export/package/version/marketplace surfaces and commit
   the candidate and release record.
2. Run fresh-checkout and packaging validators in a usable writable environment.
3. Run a managed candidate install/update and bind `charness version`,
   `charness doctor --detail`, installed `#685`, and installed `#686` semantic
   readbacks. Keep `#687` host behavior explicitly unclaimed.
4. Execute the target-bound real-host checklist if the planner requires it,
   then run the claims review and publication dry-run from the unchanged,
   verified candidate.

## Upgrade Path and Rollback

No upgrade or rollback action is currently actionable because no version or
publication exists. Once a candidate is published, operators should run the
repo-owned `charness update`, then `charness version` and
`charness doctor --detail`; release notes must name the candidate version and
the semantic `#685/#686` checks. A failed managed refresh remains an open
release/readback risk. Rollback means returning to the prior published Charness
version and rerunning version/doctor; it must not be described as complete until
the distinct readback succeeds.

## Counterweight Triage

- Act Before Ship: contradictory status source, installed candidate readback,
  top-level host-delivery exit semantics, target-bound release plan, and
  candidate claims/install proof.
- Bundle Anyway: clearer summary-refresh action, first-reader grouping, and the
  explicit no-source-diff join.
- Over-Worry: a full host/OS matrix, Cautilus execution, or a host-side #687
  event trace when the release makes no host-resolution claim.
- Valid but Defer: deeper host event-channel repair and historical issue tracker
  closeout until public/readback evidence exists.

## Non-Claims

- No version mutation, tag, push, publication, issue closure, or hosted readback
  is claimed.
- No fresh-eye PASS or release approval is claimed; all four worker verdicts are
  typed `block` and approval eligibility is false.
- Source/plugin parity and local receipts do not prove installed or host
  behavior.
- The existing 6.2.0 installed observations are not candidate observations.
- No host terminal trace for #687 and no Cautilus evaluation are claimed.

## Boundary Ownership

- Producer: source/plugin/release planners and their typed evidence carriers.
- Consumer: maintainers and operators deciding whether an installed release
  actually delivered the repaired behavior.
- Owning boundary: source/export/install/readback/release surfaces must remain
  distinct and be joined only by candidate-bound evidence.
- Verdict: owned-correctly
