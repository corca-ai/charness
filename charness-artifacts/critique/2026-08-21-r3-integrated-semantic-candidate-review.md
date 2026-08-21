# R3 Integrated Semantic Candidate Review — blocked before version mutation

Date: 2026-08-21

## Decision Under Review

Whether the integrated semantic candidate at
`f98a4e8e2936ab60870018ec1b3722d475a458e7` can advance to version mutation.
This is a pre-version critique. It is not release approval and does not claim
an installed, hosted, published, tagged, pushed, or tracker-closed result.

## Candidate and Input Binding

- Candidate HEAD: `f98a4e8e2936ab60870018ec1b3722d475a458e7`
- Packet: `charness-artifacts/critique/2026-08-21-r3-integrated-semantic-candidate-full-packet.md`
- Packet SHA256: `b9200bb68fa427a6ed8d5307fbf418b65e07e78bf2322acbe5af5f2bac28b632`
- Reviewed-input identity SHA256: `68bc2b1028df796a0ad2167194fc0f757d202d0ffb4c49c0e62db7d47e9f2066`
- Parent receipt SHA256: `d41481a11d5f40137cda6abc6e13d74889f768bec6ffa9e7be6f9d4c8b898cf6`
- Boundary window: `r3-integrated-semantic-candidate-20260821`
- Boundary fingerprint: `85a1a16f5800cf85fd79be0ae970f52623fb102b896aa2dc6e2b7e0205c65cd7`
- Boundary verification: `ok: true`, `verdict: clean`, `drift: []`

The packet's `Shape validation ok` is only deterministic packet-shape
validation. Its `Release approval: not claimed` label is preserved here as a
non-claim, not upgraded to a reviewer verdict.

## Fresh-Eye Satisfaction

parent-delegated. Four independent Charness-owned
file-backed `codex_exec` workers delivered typed reports and matching
provenance. All four semantic verdicts were `block`; every receipt reported
`approval_eligible: false`. Process completion, receipt existence, and media
output are not approval.

### Delivered Reviewer Evidence

| Scope | Result SHA256 | Receipt SHA256 | Report SHA256 | Verdict |
| --- | --- | --- | --- | --- |
| operational-release-boundary | `d5ac374f99ec79c5f6ee6ddce3d12280b88866c90b38b12dbc24b61fe002a0a2` | `917cd70af10fc528d18d741f611aa701751c1df842423cf2b951654d85c44636` | `70db06cf9b45d11bd5049dc4df5b3dff6f64cd19cd66812bfc94f42d3712f911` | block |
| structure-and-communication | `837ea7b3646c38ad5248d521122675f415f0cdc9ddc3fe825d53ff3b4cc3f545` | `57b1f629780b1e515946a0c7bf7080604408d1a481d517071eb64ea44306ca0c` | `44de6a4682c74deccffe9b8ff0e0b68009c1f6c810c835e05d2beeec265bb394` | block |
| humane-operator-path | `45ca71ddfc9c111dd4ac756beb6de5cd5cdfcb53ca87ab780a6aa1d2b3dcddab` | `e50a44ca092259bab3fb5f1806d7715ab83cb2d0112d9da857d498edbce4270f` | `94587d09de84db86de83fca8fac3b53fc418920168b80d61eecd29ac879cf521` | block |
| counterweight | `65b7be4e87d35f0d380dca6bb51f131add581927b93b03ed81f3ce4f49ee701b` | `795279e7c0de66965b52b43bae1cbb72fe47f7d6df9fd345d352b63b12ec6dfe` | `12ff20f6b138ae491e6b4efbd11edc6201fef9714b036e4fde8f5964ee28a8b5` | block |

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model/effort/service-tier application was not
  exposed by the host adapter; no model id is claimed.
- Host exposure state: metadata-hidden
- Application state: unverified; the executed backend was `codex_exec`, but
  model/effort application was not claimed from hidden or incidental output.
- Delivery state: findings-received

## Blockers

1. Durable records did not identify one current candidate. The requalification,
   handoff, and goal still exposed older source/lock pointers beside `f98`.
   Bind `f98` as the sole current semantic candidate and label older commits as
   historical joins.
2. Older changed-line and semantic-lock receipts could be mistaken for current
   maintainer proof. Mark them historical and bind current non-claims to `f98`.
3. Target-bound packaging, clean-checkout, candidate install/update,
   version/doctor, and `#682/#683/#685/#686` readbacks were absent.
4. Init/update failure and retry behavior had source tests but no exact-candidate
   installed E2E proof.
5. Same-version cache readback had a blind class: a no-op was persisted as an
   unverified skip, and matching version labels were insufficient without
   payload identity. `update all` recovery also needed to retain its scope.

## Repair Input and Non-Claims

The findings are repair input. They do not authorize version mutation or
publication. Before any release decision, the repaired delivery boundary must
receive the required second bounded review, then the exact candidate must prove
packaging, clean-home install/update, version/doctor, failure-to-retry E2E, and
the carried issue probes. #687's host terminal-event attribution remains an
explicit non-claim; only the Charness-side prevention child may be evaluated.

- No version bump, tag, push, publication, or issue closure is claimed.
- No installed, hosted, public, rollback, or real-host readback is claimed.
- No fresh-eye approval or same-agent approval inference is claimed.
- Source tests, source/plugin parity, packet shape, and local receipts are not
  being promoted to installed or public proof.
- Cautilus is not run or claimed.

## Counterweight Triage

- Act before ship: same-version payload identity, invalid-manifest refusal,
  candidate-bound install/readback, and exact current-candidate joins.
- Bundle anyway: explicit update-all recovery scope and first-reader
  non-claims, because both prevent the same process-success/delivery-success
  confusion.
- Valid but defer: a host-side #687 terminal trace and full host/OS matrix.
- Over-worry: Cautilus execution before its separately authorized eval phase.

## Boundary Ownership

- Producer: root CLI delivery state, cache readback, release planners, and
  typed evidence carriers.
- Consumer: maintainers and operators deciding whether a candidate was
  actually delivered and safe to release.
- Owning boundary: source/export/install/readback/release surfaces remain
  distinct and are joined only by exact candidate identity.
- Verdict: owned-correctly
