# R3 Delivery Provenance Repair Review — blocked after second bounded round

Date: 2026-08-21

## Decision Under Review

Whether semantic candidate `7676ec51aeed99e215106dd8490332e57db80d07` can advance
from its pre-version exact packet to version mutation. This is a second
bounded review of the repaired delivery-verdict surface. It is not release
approval and does not claim an installed, hosted, published, tagged, pushed,
or tracker-closed result.

## Candidate and Input Binding

- Candidate semantic SHA: `7676ec51aeed99e215106dd8490332e57db80d07`
- Candidate range: `f98a4e8e2936ab60870018ec1b3722d475a458e7..7676ec51aeed99e215106dd8490332e57db80d07`
- Packet: `charness-artifacts/critique/2026-08-21-r3-delivery-provenance-repair-exact-packet.json`
- Packet SHA256: `90d89c6721f86aeaeccfc8ffaacaa90471c03a6b93936cd89ae12b71070220ee`
- Reviewed-input identity SHA256: `21b105b641d5f5aabfe7c02469b7daf531676bdb8cc17ab63814c631cec4bc79`
- Parent receipt SHA256: `8610eaea866c581c5896e138aa2a7dd139becaa12be7ab4889cb6ada49b0d45c`
- Boundary window: `r3-delivery-provenance-repair-20260821`
- Boundary fingerprint SHA256: `c0c392ff475e2cb2d6361d537ff0351de992a1945a9f1b96c6a72ff6251f74f8`
- Boundary verification: `ok: true`, `verdict: clean`, `drift: []`

Packet shape and delivery are separate from semantic approval. Every delivered
worker report below has `findings-received`, matching provenance, and
`approval_eligible: false` because its typed semantic verdict is `block`.

## Fresh-Eye Satisfaction

parent-delegated. Four independent Charness-owned file-backed `codex_exec`
workers delivered typed reports, receipts, and matching delivery-ledger
entries. All four semantic verdicts were `block`; no approval is claimed from
process completion, receipt existence, boundary cleanliness, or media output.

### Delivered Reviewer Evidence

| Scope | Result SHA256 | Receipt SHA256 | Report SHA256 | Verdict |
| --- | --- | --- | --- | --- |
| operational-release-boundary | `b7fcb3faaae32c3d1054f81d9cff12776dc49404ab38d4e6285c98b2cca9bee3` | `a24cff63b5b0d2d8a2b3b6a2d6a603f68b967261dffc6edaeb2922c113e39bba` | `da0ee0ad3f698a5aa38b5636026ce5c2efc2ece6c86cd66c2eec85fc85a4c9bf` | block |
| structure-and-communication | `ab01780302c0bde26ba641c7e4f501aa9562b5bd872956c9f3750911ca74957d` | `d84a0ab4dbb41c74ed60e482dda55f7c9dcfb1acec44601302786a072b0db09e` | `3f0f1498f10882a40cdd68597763b627898d361038f48a5850dc292a42455609` | block |
| humane-operator-path | `6bd2689dcfff3c3101532efec2a92966105e21f87a83414cf3fd08b5abe7d76c` | `70062918c6e6ba7ada010a5c6d6b11a54c917f7a5979a48aee5ce3fea625ac0a` | `4f1b8af5b573258bf26eaf9018be9c920660a2f70196a1f456016d7175221970` | block |
| counterweight | `98bef8119a28780d202822d8b9f912660c1cbe403fc207fc4c5fff9fdf86861e` | `f4fd9300fbd5044697d7cb7927fdfd990a37d5e1487021cc355d0a4a3e91434a` | `15f2a719777713421bf01e6593e72234f11251269bd290f8a32078d57bcd6291` | block |

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model/effort/service-tier application was not exposed by the host adapter; no model id is claimed.
- Host exposure state: metadata-hidden
- Application state: unverified; the executed backend was `codex_exec`, but model/effort application was not claimed from hidden or incidental output.
- Delivery state: findings-received

## Blockers

1. Invalid or unreadable cache manifests can still flow to successful
   installed/refreshed guidance. The repair must preserve an explicit invalid
   sentinel and require cache directory/version, manifest version, and
   post-refresh content readback before a delivery success.
2. Same-version content identity currently guards only the already-current
   skip; attempted init/install and update/refresh success still trust version
   labels. A fake-success/no-op must fail closed with `delivery_verified: false`,
   `operation_status: failed`, nonzero exit, and no `DONE` message.
3. `doctor --detail` can hide a recorded failed same-version operation and show
   stale delivery as installed; it must consume the latest operation record and
   expose typed failure/scope/recovery state.
4. `update all` can emit success-looking completion and operation success when
   an external-tool doctor result is blocking. Aggregate failure IDs, scope,
   recovery command, persisted status, and `DONE` suppression must be tested.
5. The current docs claim a clean changed-line proof for `7676ec...` without a
   durable candidate-bound receipt path; the cited current receipt was older.
   Create and bind a fresh receipt with exact base/head, mapped files,
   `blocking_targets`, and standing-test result.
6. Current prose needs explicit semantic-candidate versus release-candidate
   roles, historical supersession labels, exact packet scope, and an explicit
   auto-excluded-path explanation. Local quality/parity remains distinct from
   installed/public proof.

## Command-Boundary Smell Evidence

The counterweight worker first used an unsupported `importlib` loader shape for
the extensionless root `charness` path and then used an unsupported `scope`
keyword for `run_tool_update_flow`; it corrected both calls with the owned
loader and inspected signature. These are retained as structural command/API
boundary evidence, not silently counted as successful probes.

## Repair Input and Non-Claims

These findings are repair input. The two-round verdict-surface cap is consumed;
repairs made after this review are accepted-unreviewed under that cap and owe
strong executable proof plus exact candidate/install evidence. Do not claim a
third bounded review or substitute a same-agent pass.

- No version bump, release-candidate mutation, tag, push, publication, or issue closure is claimed.
- No installed, hosted, public, real-Codex-host, rollback, or Cautilus evidence is claimed.
- Source tests, packet shape, clean boundary verification, and local parity are not installed/public proof.
- Installed 6.2.0 observations are not evidence for candidate `7676ec...`.
- Host-side `#687` terminal-event behavior remains explicitly unproven; only the Charness-side prevention child is in scope.

## Counterweight Triage

- Act before ship: invalid-manifest refusal, post-attempt content verification,
  latest doctor operation status, update-all aggregate failure, exact current
  proof receipt, and role-qualified candidate joins.
- Bundle after repair: scoped recovery and first-reader non-claims, once the
  failure state and evidence carrier are structurally consistent.
- Valid but defer: host-side `#687` terminal trace and a full host/OS matrix.
- Over-worry: Cautilus before its separately authorized evaluation phase.

## Boundary Ownership

- Producer: root CLI host-delivery state, cache/manifest readback, aggregate
  tool status, changed-line proof receipts, and release truth surfaces.
- Consumer: maintainers and operators deciding whether a semantic or release
  candidate was actually delivered and safe to publish.
- Owning boundary: source, export, package, install/readback, host, and public
  surfaces remain distinct and join only by exact candidate identity.
- Verdict: owned-correctly
