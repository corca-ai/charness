# Release Critique: Charness v8.14.9
Date: 2026-10-20

## Decision Under Review

Release the candidate at `a67dba3b7` as patch version 8.14.9. The candidate carries one fix since v8.14.8: Node test plans in the mutation reporters default to the TAP reporter, so the mutation baseline reader works under Node 24 where `node --test` defaults to the `spec` reporter, plus a test for the previously unused Node command path and a Node 22 and 24 CI matrix for the reporter tests.

## Release Scope

- Version: `8.14.9`
- Tag: `v8.14.9`
- Bump rationale: patch, because the change repairs an existing behavior of the mutation tooling and adds no public surface, command, or skill.
- Consumer change: none for installed operators beyond the repaired mutation tooling; the Node `PATH` workaround in the v8.14.8 Known issue is no longer needed.

## Surface-Lock Inventory

- Generated artifacts: materialized plugin and marketplace manifests produced by the release workflow; no CLI reference change.
- Consumer-visible behavior: `scripts/mutation/mutate_and_restore.py` and `scripts/mutation/mutation_test_reporters.py` command preparation for Node test plans.
- Documentation: the drafted v8.14.9 release notes.
- Adapter and integration surfaces: `.github/workflows/quality-core.yml` gains a Node 22 and 24 reporter-test job; no adapter changed.

## Verification Scope Decision

- Claim under test: the candidate is a coherent patch release; the TAP default is correct and tested at its stated level, and the drafted notes match the code range.
- Changed surfaces: the code and test paths in `9cf70ec21..a67dba3b7` (mutation reporters, their tests, the quality-core workflow) plus the drafted notes.
- Minimum sufficient proof: a verified committed-ref critique packet, one independent read-only file-backed reviewer over the exact range, and the parent's own run of the reporter test file under Node `v24.14.1` and Node `v22.23.2` (87 passed on each).
- Deliberately omitted checks: no CI run result is claimed, because the workflow change only runs once the release is pushed; the reviewer did not execute tests, so the parent's local runs stand in for that.
- Verifier contract: `skills/shared/references/bounded-review-result.schema.json` plus packet and worker-report identity readback; the verifier did not change in this release.
- Failure classification: none
- Negative control: none with rationale: the review judged a frozen committed candidate and produced no failure claim to reproduce.
- Subject identity: sha256:9309065160503efa3d3fda80843a3ab8b9ce82240f4e12fac21c3dacb66ca6a2
- Verifier identity: sha256:67288fc99eab9333366dfd0e07094b5b9dfec0f91f95b4e4cdc8a508a41c0304
- Input identity: sha256:1db1697d648fba69f3da433fdd011bad19fe43f60c4ba43991a8fdce6833f378
- Failure identity: stable:no-failure
- Evidence identity: sha256:33b82dbcbd5c1b6f4075c63f82fbafdd6408bdb97a9c546dae2c15d8dd6cbb46
- Retry disposition: first-attempt
- Retry key: sha256:57a6635a68149d47c568f0ee951460198b156ad0c7f97ab0351e98f70ba6d158

## Failure Angles

- Gawande / operational: whether the TAP default is operationally wrong or untested at its stated level. The reviewer found command preparation adds `--test-reporter=tap` unless a plan selects a reporter, covered by tests including a real Node mutation run.
- Minto / communication: whether the drafted notes match what the code range changes. The reviewer found no mismatch.
- Raskin / interface: whether operator-facing wording or behavior regresses. No regression was found; no operator-facing command changed.
- Single-reviewer exception: one reviewer covered three separately evidenced angles because the release is a patch of one small, already lane-reviewed unit, and a second reviewer would re-read the same bytes.

## Counterweight Pass

- Act Before Ship: none. The reviewer returned `pass` with no findings.
- Bundle Anyway: none.
- Over-Worry: that the reader's refusal of `spec` output leaves Node 24 unsupported; the TAP default addresses it, and the parent reproduced passing runs on both majors.
- Valid but Defer: the Node 22 and 24 CI matrix has no observed run until the release is pushed; the notes claim only that the workflow runs it.

## Structured Findings

- F1 | bin: valid-but-defer | evidence: moderate | ref: .github/workflows/quality-core.yml | action: defer | note: the reviewer asked that the Node 22 and 24 CI results be checked; they cannot exist before push, so the release records the matrix as configured and not as observed.

## Operator Action Required

No migration is required. Operators update with `charness update`.

## Upgrade Path

Run `charness update`, then use `charness version` to read back the installed version.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: run_review.py file-backed worker, adapter backend codex_exec, 900s timeout, read-only capability envelope
- Host exposure state: host-defaulted
- Application state: the worker report records model_application_state unverified-by-provider, so the requested model and effort are not host-confirmed; read-only boundary_ok true on the lifecycle
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: charness-artifacts/critique/workers/release-8149-candidate/worker-report.yaml
- Worker report identity: 7409b8b6c79fde80ab331661fd874418bc6cc5d611a40c75f7c4287f70f067a3
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: 9e4454fcb188438118d6122a5e302d59041f4bb338e5540578c9a8a3e08586d3
- Worker report input identity: 1db1697d648fba69f3da433fdd011bad19fe43f60c4ba43991a8fdce6833f378
- Worker report parent receipt identity: parent-818b560d1e50d79120ba641566346a6b1a8145e047b29b4c
- Worker report findings identity: 33b82dbcbd5c1b6f4075c63f82fbafdd6408bdb97a9c546dae2c15d8dd6cbb46

## Fresh-Eye Satisfaction

worker-delivered: one file-backed read-only worker delivered a `pass` verdict with no findings and an approval-eligible carrier bound to the committed-ref packet below.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release-8149-candidate-packet.md
- Packet path: charness-artifacts/critique/release-8149-candidate-packet.json
- Packet SHA256: 9e4454fcb188438118d6122a5e302d59041f4bb338e5540578c9a8a3e08586d3
- Identity SHA256: 1db1697d648fba69f3da433fdd011bad19fe43f60c4ba43991a8fdce6833f378
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8149-candidate-packet.json --packet-sha256 9e4454fcb188438118d6122a5e302d59041f4bb338e5540578c9a8a3e08586d3 --identity-sha256 1db1697d648fba69f3da433fdd011bad19fe43f60c4ba43991a8fdce6833f378`

## Boundary Ownership

- Producer: the mutation reporter command preparation in `scripts/mutation/`.
- Consumer: the mutation baseline reader, CI, and maintainers running the quality lane.
- Owning surface: the fix lives in the existing reporter owner; the CI matrix lives in the existing quality-core workflow.
- Verdict: owned-correctly
