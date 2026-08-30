## Situation

While running a coarse repository slice in `corca-ai/ceal`, the Charness file-backed review path required a packet, content identity, boundary snapshot, capability envelope, artifact paths, worker carrier, and final delivery readback. The repository had already widened its slice/review policy to avoid per-file reviews, but the execution contract still imposed substantial ceremony for one seam.

## Experience

The operator could not consume partial progress through one stable lifecycle surface. Path and brief mismatches stopped work before the worker started, while a parent interruption left child reviewer processes alive until the repository adapter was repaired. Progress existed in ledger/log files, but determining whether it was useful evidence or an approval-eligible result required reconstructing state across several files and exit signals.

## Evidence

- The affected integration is the file-backed parent runner in `ceal` (`scripts/run-bounded-review.py`) and the installed Charness worker boundary (`run_reviewer_worker.py`).
- Before the local repair, the parent used a blocking subprocess invocation without an explicit process group or descendant cleanup on timeout/interruption. A Ctrl-C during the review left orphaned child reviewer processes; the local adapter now starts a new process group, terminates it on timeout/interruption, preserves progress files, and emits `timed-out` with `not-observed` verdict in commit `ae25fc4dc`.
- The repository contract now documents the intended distinction in `charness-artifacts/spec/lane-execution-and-review.md`: ledger/logs are progress evidence, only a terminal identity-bound report can be approval, and a timeout must terminate the worker group.
- The local regression fixture initially exposed two caller-side mistakes rather than product failures: a 100ms timeout killed the fixture before its PID marker was written, and the fixture incorrectly treated `argv[1]` (`--repo-root`) as a custom path. Both were corrected; the incident still shows how easy it is for a consumer to mis-model the worker invocation contract.
- The current Charness critique contract requires a multi-angle pass plus a counterweight for substantial work, even when the repository has selected one coarse slice and the host cannot expose child terminal carriers. This creates avoidable throughput and approval friction for reversible local seams.

## Impact

Every consumer that wants honest timeout behavior and partial-result handling must reimplement process-tree cleanup and state classification. Operators spend time on path/identity/carrier plumbing instead of the product seam, and a timed-out run can be operationally ambiguous even when useful intermediate findings are present. The extra review choreography also makes large, parallel implementation slices feel serial and approval-heavy.

## Requested outcome

Please provide a lower-friction, risk-adaptive file-backed worker contract:

1. Expose one durable lifecycle/status carrier that distinguishes accepted, running, partial progress, timed-out/interrupted, terminal delivery, and approval eligibility. Partial ledger/log output must remain readable but never imply approval.
2. Make the parent worker boundary own process-group/tree cleanup on timeout and interruption, so repository adapters do not need private subprocess workarounds.
3. Allow a single bounded fresh-eye worker to run several explicitly listed lenses when child terminal carriers are unavailable, and make full multi-angle/counterweight orchestration conditional on a material risk boundary rather than every substantial-looking local change.
4. Provide a canonical preflight/diagnostic command that resolves helper paths, validates the brief/argument contract, and reports the exact next action before worker startup.

## Acceptance shape

- A timed-out or interrupted worker returns a typed non-delivery state, preserves all partial carriers, and leaves no descendant process owned by that run.
- No partial result, process exit code, or non-empty output is approval-eligible without terminal identity and schema validation.
- A repository can select a coarse review unit and one bounded carrier without adding per-file or per-fix approval steps when no material authority, durability, external-write, or security boundary changes.
- The implementation does not require each consumer to fork a custom lifecycle adapter merely to get safe timeout semantics.

## Scope note

The two fixture failures above are explicitly not being reported as Charness product defects. They were fixed locally. The issue is about the upstream contract and default workflow friction that made lifecycle ownership, partial-result consumption, path validation, and review cadence costly to integrate.

Weak direction only: a versioned worker lifecycle envelope plus a risk-tiered cadence setting could provide the needed semantics without weakening identity binding or the rule that partial findings are never approval.

---

<!-- charness-work-item-key: issue-731-reviewer-lifecycle -->
# Work Item #731 — Preserve bounded-review partial progress

## Purpose and premise

After #756 owns backend invocation and normalization, make useful partial reviewer output first-class without weakening timeout, cleanup, identity, or approval eligibility.

## Acceptance and proof

Focused lifecycle tests prove partial-output preservation, process-tree cleanup, terminal delivery, and refusal of exit-code-only or identity-mismatched evidence. A resolution critique binds the behavior verdict.

## Non-claims

No new reviewer backend, dashboard, or success inference from a worker exit code.
