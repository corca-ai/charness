# External Worker Capability Envelope — First Implementation Slice

Date: 2026-08-24
Status: round-2 repairs and hard-gate ownership repair implemented; accepted-unreviewed under the mandatory two-round cap

## Implemented

- Extracted the worker-facing lifecycle into the cohesive
  reviewer_worker_capability.py owner and its plugin mirror. It owns launch
  refusal, collection revalidation, structured result non-claim validation,
  typed capability-failure adaptation, and worker capability receipt fields;
  canonical envelope semantics remain delegated to reviewer_capability.py.

- Added the host-neutral typed capability classifier in
  `skills/shared/scripts/reviewer_capability.py`, the cohesive typed preflight
  helper in `reviewer_capability_preflight.py`, and their generated plugin copies.
- Added explicit filesystem-write, external-read, and external-effect axes;
  empty lists do not establish denial, and sandbox labels remain provenance.
- Added ordered, same-attempt preflight classification for ready,
  transport-unestablished, credential-invalid, authorization-insufficient, and
  provider-unavailable observations. Malformed, contradictory, missing, stale,
  duplicate, and unrequested observations refuse as `probe-invalid`.
- Required ready preflight before the existing backend launch. Optional
  unavailable reads are launchable only with the exact target-bound structured
  non-claim frozen in the capability envelope. The existing
  worker receipt now carries the structured capability fields and launch and
  collection envelope hashes; semantic envelope drift between those points is
  refused before output publication.
- Revalidated the copied capability fields at the existing combined reviewer
  report and installed carrier boundaries. The combined report remains the
  only owner of `approval_eligible`.

## Hard-Gate Repair

The prior closeout misclassified reviewer_worker_runtime.py at 364 tokei
Python code lines as an advisory. The configured 360-line limit is hard; that
was a gate failure. The repair moved the capability-specific worker lifecycle
out of the runtime into reviewer_worker_capability.py, leaving the runtime
as the owner of generic backend process lifecycle, result/schema validation,
and atomic result/receipt publication. This is an ownership split, not a
wording or mechanical line-count adjustment.

Current hard-gate evidence: reviewer_worker_runtime.py is 345 tokei Python
code lines and the length gate passes. It remains in the configured advisory
warn band [330, 360], which is recorded as a design smell/non-claim rather
than called clean.

An independent Ruff pass then exposed complexity failures hidden by the
worker's unstaged no-op pre-commit: capability record validation and generic
backend process lifecycle were still combined into high-branch functions.
Per-target preflight validation now has its own helpers, while the existing
reviewer_process.py owner carries bounded subprocess launch, timeout, stream,
and process-group cleanup. Ruff passes without suppressions and the runtime
remains below the hard length limit; the 345-line advisory remains explicit.

## Round-1 Finding Disposition

1. **Capability identity drift — repaired.** The launch capability envelope
   SHA-256 is now bound to the existing delivery attempt and carried through
   its retry/history representation. The receipt, combined report, delivery
   ledger, and installed carrier require the exact launch identity join. No
   second attempt, receipt, ledger, or approval owner was introduced.
2. **External-read policy collapse — repaired.** Every named read target now
   has an exact host-observed effective entry. `deny-all` requires `denied` and
   cannot have preflight; optional unavailable/unproved observations are
   accepted only with a target-specific explicit non-claim; required reads
   still determine fail-closed launch readiness. Duplicate target/policy mixes
   are refused.
3. **Timestamp/freshness gap — narrowed honestly.** The first slice supports
   same-attempt ordering only. `attempt_started_at` is mandatory,
   `observed_at` must not precede it, and `live` is unsupported rather than
   treated as fresh. No wall-clock age heuristic or host-attested freshness
   window was invented; future and ancient `live` observations are refused.
4. **Runner path identity drift — repaired.** The runner resolves each path
   once relative to `--repo-root` and passes those exact resolved identities to
   the child and report writer, including output, receipt, report,
   stdout/stderr, schema, ledger, prompt, and capability files.

## Contract Source

`charness-artifacts/spec/2026-08-24-external-worker-capability-envelope.md`

Supporting context read before implementation:

- `charness-artifacts/debug/2026-08-24-gh-auth-network-misclassification.md`
- `charness-artifacts/ideation/2026-08-24-consumer-friction-and-file-backed-lanes.md`
- the final external-worker capability critique and its repair packets

## Round-2 Accepted-Unreviewed Repair Disposition

1. **Optional non-claim identity — repaired structurally.** Optional
   unavailable targets now carry a capability-envelope-owned record with an
   exact logical target, fixed scope, canonical statement, per-record identity,
   and collective digest. The launch envelope freezes it; the worker result,
   receipt, combined report, delivery ledger join, and installed carrier must
   repeat the exact corresponding identity. Missing, contradictory, rebound,
   or wording/scope-mutated records are ineligible. The existing
   attempt → receipt → ledger → report chain remains the only owner.
2. **Freshness — accepted contract narrowed.** Only same-attempt ordering is
   claimed. `live` is unsupported until a host adapter can attest a freshness
   window, so no broader live/future/stale claim is made.
3. **Valid defer — not silently absorbed.** Retry authorization for active or
   foreign-lineage attempts, and runner ledger mutation before complete
   receipt/report validation, remain separately tracked by the parent. They
   were not changed by this repair.

## Verification

The focused proof fixtures cover ready explicit write/effect denial,
transport-unestablished before backend launch, credential-invalid only after
transport, authorization-insufficient only after identity, provider-unavailable,
malformed/contradictory/missing denial, sandbox-label-does-not-grant,
launch-to-collection drift, and attempt/target/duplicate preflight joins.
Existing reviewer worker, delivery, report, and installed-carrier fixtures cover
stale, missing, duplicated, and mismatched receipt/ledger/report joins.

Prior first-slice proof (before the round-1 repairs; not current closeout evidence):

- `python3 -m pytest -q` over the capability, worker, runner, report, delivery,
  carrier, standalone-import, parity, skill-surface, tier-policy, and critique
  enforcement fixtures — **221 passed**.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`, explicit
  source/plugin `cmp` checks, `py_compile`, and `git diff --check` — **passed**.
- `check_bootstrap_shim_consistency.py`, `validate_packaging.py`, and
  `validate_packaging_committed.py --repo-root . --ref HEAD` — **passed**.
- Surface, skill, handoff, debug, ideation, critique, and current-pointer
  validators — **passed** for their applicable current surfaces.
- `prepush_focused_changed_line_coverage.py --refuse-unestablished` — **status:
  noop**, because the mutation pool does not include the changed
  `skills/shared/**` proof surface; this is not changed-line coverage evidence.
- `bash .githooks/pre-commit` — **ran-pass**, but its predict-commit scope was
  empty because this slice is intentionally unstaged.

Focused proof currently run:

- `python3 -m pytest -q tests/quality_gates/test_reviewer_worker_capability.py
  tests/quality_gates/test_reviewer_capability.py
  tests/quality_gates/test_reviewer_worker.py
  tests/quality_gates/test_reviewer_worker_report.py
  tests/quality_gates/test_reviewer_runner.py
  tests/quality_gates/test_issue_worker_carrier.py
  tests/quality_gates/test_reviewer_delivery_state_machine.py` — **98 passed**.
- `python3 -m pytest -q tests/quality_gates/test_parity_harness.py` — **45
  passed**; direct source/plugin `cmp` parity for every affected shared script
  also passed. The repo parity harness itself reports its 26 changed paths as
  **skipped/uncomparable** because the review snapshot has no baseline for this
  uncommitted/new surface; that is not treated as parity proof.
- Targeted `py_compile`, `validate_packaging.py`,
  `validate_packaging_committed.py --repo-root . --ref HEAD`,
  `check_bootstrap_shim_consistency.py`,
  `validate_packaging_install_surface.py`, and `git diff --check` — **passed**.
- `check_python_lengths.py` — **passed**; the repository-wide run reports
  existing advisory warn-band files, including the now-cohesive
  `reviewer_worker_runtime.py` at 345 code lines. No hard length failure
  remains.

## Ownership and Non-Claims

The normative chain remains `attempt -> worker receipt -> reviewer delivery-ledger
attempt -> combined worker report`; no second attempt, receipt, ledger, or
approval owner was introduced. Charness task/lane semantics were not redesigned.

This slice does not claim live credentials, live network/provider behavior,
installed-machine or Ceal proof, Cautilus evaluation, GitHub mutation, push, or a
bounded fresh-eye review. The mandatory round-2 cap is consumed and these
repairs are accepted-unreviewed; no third review is claimed. The existing r2
packet with `changed_ref: HEAD` did not cover these working-tree repairs; the
parent must regenerate a working-tree-bound packet. No files under `../ceal`
were edited, and lesson-session state was not touched.

## Critique and Next Slice

The mandatory two-round cap has been consumed. The round-2 repairs above are
recorded as accepted-unreviewed; no additional review is implied or claimed.
The parent should regenerate the review packet against the repaired working
tree, separately track the two valid-defer findings, and retain the uncommitted
state until its own closeout decision. This artifact does not claim
installed/Ceal proof, live-read proof, Cautilus evaluation, GitHub mutation,
push, or release.
