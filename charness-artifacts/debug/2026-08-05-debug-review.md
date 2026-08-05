# Issue #506 Reviewer Boundary Stale Default Window Debug
Date: 2026-08-05

## Problem

The reviewer-boundary fingerprint helper can verify an unqualified default
snapshot from an older review window instead of refusing an ambiguous request.
At closeout this can attribute a mismatch to the current review when the helper
compared the wrong baseline.

## Correct Behavior

Verification must identify the snapshot/window it is comparing. A non-canonical
or stale default path must refuse with an actionable message that names the
resolved snapshot and window, while explicit `--before` verification preserves
the existing parent/reviewer drift attribution semantics.

## Observed Facts

- Issue #506 reports a structural closeout window whose unqualified verify read
  an older `retro-goal-design-critique-repair-read-1` snapshot; explicit
  `/tmp/charness-reviewer-boundary-structural-runtime.json` verification was
  clean.
- The issue names `skills/shared/scripts/reviewer_boundary_fingerprint.py` as
  the canonical helper and says no reviewer finding or code mutation escaped.
- The issue is classified as a bug because an existing verification capability
  can compare the wrong review window while returning an ordinary mismatch.
- The debug adapter is absent; the default durable artifact location is used.
- The existing local #506 disposition carrier claims a stale/default refusal
  test, but the current source suite has no such test and the helper still
  accepts an unqualified default verify.

## Reproduction

- Reproduction on the current HEAD: snapshot the repository with
  `--window-id issue-506-stale-default-repro`, then run `verify --repo-root .`
  without `--before` or `--window-id`; it returned `ok: true`, `verdict: clean`,
  and that stale window id. The explicit-window boundary snapshot used for this
  causal review verified clean separately.

## Candidate Causes

- The default snapshot path is treated as a stable identity even when a new
  review window has no matching snapshot metadata.
- Snapshot filenames or stored metadata do not carry enough window identity for
  verify to distinguish a stale default from the requested window.
- Existing boundary tests exercise drift attribution and explicit paths but do
  not assert refusal on stale or ambiguous default resolution.

## Hypothesis

- The helper's default verify path resolves a canonical file without checking
  that its recorded window identity is explicit at the call boundary.
  Disconfirmer: inspect the resolver and tests, then reproduce with a stale
  snapshot; result below would disconfirm this if default verification already
  refused or required an identity.

## Verification

- confirmed — `reviewer_boundary_fingerprint.py:262-265` selects the canonical
  default, while the window mismatch refusal at `:284-298` runs only when
  `--window-id` is supplied; the reproduction returned a normal clean verdict.
- repaired and verified — the default-path refusal, explicit-path compatibility,
  mismatch/parent-attribution behavior, and parity cases pass 26 focused helper
  tests plus the 45-test parity suite. The source and plugin mirror are
  byte-identical. A second bounded review read the repaired verdict logic and
  found no blocker; its documentation minor was corrected before the separate
  resolution critique.
- Resolution critique: `charness-artifacts/critique/2026-08-05-issue-506-resolution-critique.md`
  triaged canonical-path alias detection as over-worry for this slice and kept
  explicit `--before` as the identity-bearing compatibility path.

## Root Cause

The verify contract permits an implicit canonical snapshot identity. Without an
explicit `--window-id`, an unqualified call can compare the default file's old
window and still render a drift/clean verdict. The prevention boundary is the
CLI's default-path selection, before fingerprint comparison.

## Invariant Proof

- Invariant: an accepted boundary verification must compare the requested
  reviewer window, not an unrelated prior snapshot.
- Producer Proof: `reviewer_boundary_fingerprint.py:220-244` writes a window id
  into snapshots; `snapshot --window-id issue-506-stale-default-repro` produced
  one in the reproduction.
- Final-Consumer Proof: `reviewer_boundary_fingerprint.py:262-343` resolves the
  default path and emits the `clean` verdict without a caller identity.
- Interface-Shape Sibling Scan: this is a local proof-boundary identity check,
  not producer-to-final-consumer diagnostic propagation; see Sibling Search.
- Non-Claims: no host-installed behavior, remote CI, or GitHub CLOSED state is
  claimed by this investigation.

## Detection Gap

- Focused boundary tests (`tests/quality_gates/test_reviewer_boundary_fingerprint.py:56-68,322-350`) |
  cover clean default verification and explicit mismatch/legacy cases, but not
  an unqualified default with a stale window | add a refusal assertion for the
  default path and retain explicit-path legacy coverage.
- Human structural closeout review | discarded the ambiguous default result and
  reran with `--before` | make the helper refuse the ambiguous default before a
  boundary verdict can be cited.

## Sibling Search

- Mental model: a proof tool treats a mutable canonical location as authoritative
  identity.
- same layer: `plugins/charness/shared/scripts/reviewer_boundary_fingerprint.py:262-298` |
  decision: same bug, fix now | proof: static scan only; generated mirror must
  stay synchronized.
- abstraction up: `scripts/parity_harness.py:58-60,119-121` reads the same
  implicit location | decision: same class, diagnostic-only for this slice |
  proof: static scan only; its broader semantics need a separate issue/contract.
- specialization down: `tests/quality_gates/test_reviewer_boundary_fingerprint.py:338-350`
  intentionally exercises legacy snapshots without a window | decision: same
  bug, fix now | proof: local payload proof; keep explicit-path compatibility.
- mental-model sibling: `docs/conventions/operating-contract.md:108-114` and
  `skills/shared/references/fresh-eye-subagent-review.md:253-269` require an
  explicit before/window invocation | decision: same class, diagnostic-only
  for this slice | proof: static scan only.
- cross-file: `plugins/charness/shared/scripts/reviewer_boundary_fingerprint.py`
  is the exported mirror of the subject helper.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: reviewer-boundary helper to snapshot files and closeout callers
- Disproving Observation: none
- What Local Reasoning Cannot Prove: host-specific invocation behavior outside
  the checked-in helper and tests
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Diagnosis and implementation are complete; resolution critique and remote
  issue closeout are recorded separately below.
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this dated debug record

## Prevention

Require an identity-bearing invocation for the canonical default path: accept a
matching `--window-id`, or require an explicit `--before` path. Preserve the
existing explicit-path, legacy-snapshot, and parent-attributed verdict behavior;
pin all three in focused tests and synchronize the plugin mirror.
