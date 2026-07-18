# Quality infrastructure correctness and v2.1.1 release
Date: 2026-07-18

## Execution

- Standalone code critique: two bounded fresh-eye angles, followed by a separate counterweight and a read-only fix-verification pass.
- Packet Consumed: `charness-artifacts/critique/2026-07-18-quality-infrastructure-v2-1-1-packet.md`; fix verification consumed `charness-artifacts/critique/2026-07-18-quality-infrastructure-v2-1-1-fix-verification-packet.md`.
- Target: `skills/public/critique/references/code-critique.md`, with release lock-in checked through the generated export and operator-proof inventory below.

## Decision Under Review

Repair the mutation-coverage producer/consumer false green, move shared Nose executable transport to one owner, reuse immutable test seeds, then publish the compatible repairs as v2.1.1.

## Diff Scope

- changed-line coverage production, authoritative consumption, and closeout reporting;
- Nose binary/version/JSON transport plus source/plugin consumers;
- quality-runner test seed construction and clone isolation.

## Failure Angles

- Problem framing and diagnosis: does the final consumer, rather than the producer exit code, own changed-line proof?
- Boundary ownership: did shared transport move to a domain owner without leaking Markdown or code-report policy into it?
- Operability and test economics: can an operator see a non-claim, and does fixture reuse preserve isolation while reducing setup?

## Counterweight Pass

- Act before ship: expose dirty-range `NOT CHECKED`, reject malformed or range-mismatched consumer verdicts, include untracked eligible files, and sync the plugin export. All four were fixed and the fix-verification reviewer found the slice ship-ready.
- Valid but defer: a runtime-writing clone-isolation scenario has no observed missing branch beyond the direct contamination proof.
- Over-worry: no new mandatory post-commit gate and no loader-unification refactor; the existing pre-push consumer is the irreversible-boundary check, and `nose_tool_lib` is stateless.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/slice_closeout_reporting.py | action: fix | note: dirty precommit coverage non-claims now render reason, excluded files, and the consumer command.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/mutation_coverage_producer.py | action: fix | note: a pass now requires the authoritative clean verdict and exact base/head range.
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/check_changed_line_mutation_coverage.py | action: fix | note: untracked nonignored eligible files now force the honest precommit non-claim.
- F4 | bin: act-before-ship | evidence: strong | ref: plugins/charness/skills/quality/scripts/nose_tool_lib.py | action: fix | note: source and checked-in plugin consumers now receive the shared transport together.
- F5 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_quality_runner.py | action: defer | note: current clone-contamination proof is sufficient until a seed-writing runtime path is observed.
- F6 | bin: over-worry | evidence: weak | ref: skills/public/quality/scripts/nose_report_lib.py | action: defer | note: direct versus path loading has no identity or state consequence for this stateless helper.
- F7 | bin: over-worry | evidence: moderate | ref: scripts/run-quality.sh | action: defer | note: the standing pre-push consumer already owns post-commit range proof, so another gate would add duplicate teeth.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`, `fork_turns=none`.
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested spawn fields; provider application metadata was not exposed.

## Fresh-Eye Satisfaction

parent-delegated; reviewer-boundary fingerprint verification returned `ok: true` with no drift after both angles, the counterweight, and fix verification.

## Boundary Ownership

- Producer: coverage producers emit the report, freshness marker, range metadata, and authoritative consumer command; `nose_tool_lib` emits only executable transport facts.
- Consumer: `check_changed_line_mutation_coverage.py` owns the changed-line verdict; Nose inventory/report modules own their schemas and operator rendering.
- Owning surface: repo-python plus quality skill source, synchronized checked-in-plugin-export.
- Verdict: owned-correctly

## Release Scope

- v2.1.1 / tag `v2.1.1`: compatible correctness, internal ownership, and test-runtime repairs; patch is the lightest honest bump.

## Surface-Lock Inventory

- Generated artifacts: packaging and marketplace versions plus the checked-in plugin export.
- Consumer-visible behavior: closeout text now names changed-line proof that was not checked; existing commands and defaults are unchanged.
- Documentation: release artifact and closeout handoff only; no migration guide is required.
- Adapter/integration state: release adapter, fresh-checkout probes, public readback, and post-publish installed update remain the owning evidence channels.

## Operator Action Required

- None beyond the existing `charness update` path; publication remains provisional until the helper records public HTTPS and installed-version readbacks.

## Upgrade Path

- Run `charness update`; rollback remains installation of v2.1.0 if an operator needs the prior behavior.

## Deliberately Not Doing

- No new blocking floor, post-commit workflow, Nose policy abstraction, or Cautilus run. The slice reuses existing teeth and keeps reversible design choices judgment-led under the north star.

## Next Move

Run synchronized full proof, persist the quality/retro closeout, commit, then let the release helper perform the v2.1.1 irreversible-boundary sequence and distinct-channel readbacks.
