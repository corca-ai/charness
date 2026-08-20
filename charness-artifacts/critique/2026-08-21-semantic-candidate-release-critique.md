# Semantic Candidate Release Critique

Date: 2026-08-21

Execution: parent-delegated read-only Codex bounded reviews completed in
separate process contexts. The host exposes no typed Agent/spawn/Ceal worker
envelope, so the reviews used unnamed `codex exec --sandbox read-only` channels
and parent boundary fingerprints. The final owner-bound round consumed the
current repaired packet and found the verdict logic sound, while identifying a
proof-identity binding gap and one diagnostic wording drift. The diagnostic
repair was made in `3cc29d5ea`; a parent reproduction then found that embedded
target markers could still escape the exact owner-token contract. That escape
is repaired in `a1aeb90ed`, with focused coverage in `19e62aea8`. Exact-HEAD
changed-line and broad receipts now bind `19e62aea8`; a replacement packet must
read that truth surface before semantic lock.

## Decision Under Review

Whether to lock the integrated semantic candidate at `19e62aea8` before version
mutation, tag, publication, or external readback.

Success requires a bounded fresh-eye release critique with separate angle and
counterweight passes, followed by a durable four-bin disposition. The original
semantic-candidate packet was reviewed by the retry recorded in
`charness-artifacts/critique/rounds/2026-08-21-2026-08-21-goal-codex-review.md`.
The command-plan repair was separately reviewed in rounds 1 and 2 below. This
does not authorize version mutation, publication, hosted readback, or issue
closure.

## Release Scope

Version remains 6.2.0; no tag or release candidate is being locked. The consumer-visible change under consideration is the repaired release/quality/evidence workflow, including fresh-checkout timeout ownership, changed-line coverage measurement, and lesson-session continuity.

## Surface-Lock Inventory

- Generated/plugin surfaces: root/plugin source parity, packaging manifests, and release planner inputs.
- Consumer behavior: fresh-checkout probes, changed-line quality verdicts, lesson-session continuity, and CLI/operator proof commands.
- Documentation/evidence: the active goal, debug/spec/RCA records, release/quality receipts, critique packet, and retro dispositions.
- External boundaries: version/tag/push/publication, install or update refresh, hosted readback, and issue closeout.

## Failure Angles

The retry executed Gawande (operator checklist and clean checkout), Minto
(release/evidence communication), and Raskin (consumer-facing proof path) as a
bounded fresh-eye read, followed by the requested counterweight disposition. It
found no release-blocking defect in the reviewed packet. The command-plan
repair then received a first round that found ref/help/short-flag continuation
gaps and a second round that read the repairs. The final owner-bound round found
no remaining owner-binding blocker, but caught stale proof identity and a
diagnostic-label mismatch. The diagnostic label was repaired; the replacement
packet review caught the remaining current-HEAD evidence drift, which is now
being repaired through exact-HEAD receipts and synchronized truth surfaces.

## Counterweight Pass

The release retry's counterweight classified the missing executable command-plan
seam as `Bundle Anyway`, runtime above the #668 advisory budget as `Valid but
Defer`, hypothetical unobserved consumer-host concerns as `Over-Worry`, and no
current `Act Before Ship` blocker. The command-plan first round changed the
implementation: ref/help/flag failures now stop later probes, and both long
and short flags are checked. The second repair-read round found no blocker.
Round-2 test additions are explicitly accepted-unreviewed under the repository
two-round cap.

## Public-Skill Scenario Review

The closeout planner required a deterministic review of the public-skill
validation and scenario-registry decision before its acknowledgment could be
recorded. That review was completed without invoking live Cautilus:

- `validate_public_skill_dogfood.py`: 20 cases, 20 required cases.
- `validate_scenario_conditional_reads.py`: passed; one planner-covered
  `docs/handoff.md` read and advisories for the other extractor/stale-allowlist
  cases.
- `validate_cautilus_scenarios.py`: passed; 8 evaluator-required skills.
- `validate_cautilus_call_provenance.py`: passed; 5 grandfathered calls.
- `validate_cautilus_proof.py`: passed with no Cautilus proof artifact changed.
- `suggest_public_skill_dogfood.py` for `achieve`, `critique`, `impl`,
  `quality`, and `release`: applicable cases reported; `impl` remains
  evaluator-required and the other four remain HITL-recommended.

The maintained `evals/cautilus/scenarios.json` mapping and
`evals/cautilus/impl-claim-fidelity/spec.json` were inspected. The existing
`impl-adapter-bootstrap` scenario remains the applicable evaluator scenario;
this candidate changes release/quality/evidence contracts and does not add or
alter the impl adapter-bootstrap behavior that would justify a registry
mutation. Decision: keep the registry unchanged and acknowledge the
deterministic scenario review. Cautilus remains ask-before-run, and no live
evaluation, evaluator verdict, or evaluator-backed claim is made here.

## Closeout Advisory Dispositions

The closeout detector found an intentional helper move and new proof-surface
families in the already-integrated slice. `scripts/slice_closeout_advisories.py`
imports `_added_diff_lines` from `slice_closeout_repair_parity.py`; the two
remaining readers are therefore not a dangling-name defect. The helper move is
covered by the existing in-process and removed-name tests; no compatibility
alias is added merely to silence a textual detector.

The following are proof-surface decisions. Each fresh-eye pass is explicitly
skipped because the host still exposes no bounded reviewer context; these are
not same-agent approvals:

- Fresh-eye pass: `scripts/adapter_key_usage.py` — proof-surface helper,
  skipped, no Agent/spawn/Ceal reviewer context available.
- Fresh-eye pass: `scripts/check_artifact_citations.py` — proof surface,
  skipped, no Agent/spawn/Ceal reviewer context available.
- Fresh-eye pass: `scripts/check_consumer_validator_catalog.py` — proof
  surface, skipped, no Agent/spawn/Ceal reviewer context available.
- Fresh-eye pass: `scripts/check_release_issue_ledger.py` — proof surface,
  skipped, no Agent/spawn/Ceal reviewer context available.
- Fresh-eye pass: `scripts/release_issue_ledger_contract.py` — proof-surface
  helper, skipped, no Agent/spawn/Ceal reviewer context available.
- Fresh-eye pass: `scripts/release_issue_ledger_evidence.py` — proof-surface
  helper, skipped, no Agent/spawn/Ceal reviewer context available.
- Fresh-eye pass: `scripts/slice_closeout_repair_parity.py` — proof-surface
  helper, skipped, no Agent/spawn/Ceal reviewer context available.
- Fresh-eye pass: `scripts/what_reads_this_fallback.py` — not a proof surface;
  fallback analysis is consumed by the parent reporter, skipped fresh-eye
  review because the host has no bounded reviewer context.
- Fresh-eye pass: `skills/public/achieve/scripts/goal_artifact_portability_gate.py`
  — proof surface, skipped, no Agent/spawn/Ceal reviewer context available.
- Fresh-eye pass: `skills/public/achieve/scripts/goal_path_portability.py` —
  proof surface, skipped, no Agent/spawn/Ceal reviewer context available.
- Fresh-eye pass: `skills/public/critique/scripts/record_round_findings.py` —
  proof-surface recording boundary, skipped, no Agent/spawn/Ceal reviewer
  context available.

Floor-Addition Restraint: retain the three new blocking floors in
`check_artifact_citations.py`, `check_consumer_validator_catalog.py`, and
`check_release_issue_ledger.py`. Advisory or describe-first absorption is not
enough here: each protects a distinct recurring release escape (stale evidence
citations, package consumer drift, or an incomplete issue train), and the
checks are path/snapshot scoped with their semantic blind spots disclosed.
This is a keep decision for the existing gates, not authorization to add a
fourth floor.

## Command-Surface and Runtime Advisory

Several operator-issued commands in this goal were rejected before their
intended subject ran: guessed validator paths (`scripts/check_critique_artifacts.py`,
`scripts/check_goal_artifact.py`), a guessed test path (`tests/test_release_issue_ledger.py`),
the wrong release-script owner (`scripts/current_release.py`), an unsupported
`--detail` flag on the release reader, and an unresolvable abbreviated ref. These
are one command-surface smell: execution began before the owning path, accepted
argv, and ref identity were resolved. They are not test or code failures.

The structural repair is now executable in
`scripts/command_plan_preflight.py`, driven by
`charness-artifacts/critique/command-plans/2026-08-21-goal-fanout.json`. It
resolves five exact script/test targets through `rg --files`, verifies the full
base SHA with `git rev-parse --verify`, and probes four owner `--help` surfaces
before checking planned long and short flags. The corrected plan passed.
Target/ref failures stop all owner probes; owner-help/flag failures stop later
owner probes and return exit 2. A missing target or rejected help surface stops
the fan-out and repairs the command plan first. The first implementation's
fresh-eye finding and repair are recorded in rounds 1 and 2; the initial
recorder rejection of an out-of-repo `/tmp` boundary snapshot was also
preserved as a path-contract smell and repaired by using a repo-owned snapshot.

The final owner-bound round also found that `fanout-stopped` over-described
malformed/token/help failures as owner/flag failures; `3cc29d5ea` now emits the
general preflight-failure diagnosis and tests it.

The parent then reproduced a second wrong-owner form: `--input={target:other}`
was expanded by the generic token expander without being counted by the exact
owner-token check. The owning seam now refuses embedded and nested target
markers as `target-token` errors in both `argv` and `help_argv`; the 25-test
focused suite and the durable targeted-mutant receipt cover those branches.

During evidence assembly, an operator inspection also guessed the unsupported
`git status --staged` flag. It was rejected before changing state and corrected
to `git diff --cached --name-only`; this is recorded as a command-surface
inspection smell, not as proof or a repository mutation.

The serialized current-head changed-line proof is `23/23`, `blocking=[]`, at
`19e62aea8`, with the durable receipt at
`charness-artifacts/quality/2026-08-21-command-plan-changed-line-proof.md`.
The serialized broad quality run is `96 passed, 0 failed` in `166.9s`, with
the durable receipt at
`charness-artifacts/quality/2026-08-21-command-plan-broad-quality-proof.md`. An
earlier concurrent broad/changed-line attempt produced a no-verdict race through
shared mutation state; it is not used as proof. The final runs were serialized.
Runtime remains an explicit #668 advisory, not a clean-budget claim or a version
blocker.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: final owner-bound review and current-head proof binding | action: defer | note: semantic lock may proceed only after the replacement packet is reviewed and the current serialized verification is bound; do not infer version/publication approval
- F2 | bin: valid-but-defer | evidence: strong | ref: /tmp/charness-s5-quality-read-only-final2.log | action: defer | note: local quality, fresh-checkout, duplicate-ratchet, and real-host trigger checks do not establish external release truth
- F3 | bin: over-worry | evidence: weak | ref: hypothetical unobserved consumer hosts | action: document | note: speculative host concerns without a current reproducer remain outside this critique's proven findings

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded-reviewer
- Requested spawn fields: read-only one-shot bounded reviewer; inherited session model; no host addressing/name
- Host exposure state: unsupported
- Application state: parent-delegated read-only Codex review delivered after one interrupted attempt
- Delivery state: findings-received; final owner-bound round found the owner logic sound but blocked on stale proof identity; the parent repaired and reran it

## Fresh-Eye Satisfaction

parent-delegated: the semantic retry returned Gawande/Minto/Raskin plus
counterweight findings; command-plan rounds 1 and 2 were recorded, and the
final owner-bound packet review returned findings. It found no owner-binding
verdict escape, but required current-HEAD proof rebinding and diagnostic repair;
the parent performed those repairs and serialized the reruns. No same-agent
substitute or Cautilus evaluation is claimed.

## Reviewed Input Identity

- Packet consumed by the latest replacement review:
  `charness-artifacts/critique/2026-08-21-semantic-candidate-final-v9-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-21-semantic-candidate-final-v9-packet.json`
- Packet SHA256: `42f2cbdee4bc8a5dc9e951af1c9d7be012d054814f303f556967f85dea9f012a`
- Identity SHA256: `06d40fe77d56d483fb73ad1caadb156a769d2807fc2fb5d3048530fc697291bb`
- The v5 review bound the packet itself to `ea6737b30`, but found that the
  changed-line and broad-quality receipts cited older proof trees. Those
  receipts are now rebound. A new packet and fresh-eye round must consume the
  synchronized `19e62aea8` surfaces, including the standalone target-token
  refusal and its focused coverage.

## Operator Action Required

- Do not mutate version or release surfaces until the replacement packet for
  `19e62aea8` has its own fresh-eye read and integrated verification lock.
- Re-run the exact post-critique verification lock before any external-boundary
  action; hosted/install readback, issue closure, publication, and Cautilus
  remain unrun.

## Upgrade Path

None is authorized: no version bump, tag, publication, install refresh, or rollback instruction is being issued from this blocked critique.

## Boundary Ownership

- Producer: quality/release evidence producers and the integrated semantic candidate.
- Consumer: release planner, bounded critique, version/release mutation, and external readback operators.
- Owning surface: parent-owned release boundary and the corresponding executable proof packets.
- Verdict: owned-correctly
