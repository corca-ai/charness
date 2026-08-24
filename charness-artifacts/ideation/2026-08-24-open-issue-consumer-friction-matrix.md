# Open-Issue Consumer-Friction Matrix

Inventory timestamp: 2026-08-24T18:21:43+09:00

Source query: `gh issue list --repo corca-ai/charness --state open --limit 200 --json number,title,updatedAt`

The query returned 46 open issues. Inclusion means the issue body or comments
contain a concrete episode in a repository consuming Charness. Dependency means
the row is required to preserve the correctness of an included consumer behavior.
Exclusion means no current direct consumer episode was found; it does not mean the
issue is invalid or should be closed. Candidate bodies and comments were re-read
with `gh issue view --comments`. Closeout must refresh the affected row because
GitHub remains the source of truth.

| Issue | Updated (UTC) | Class | Current disposition and evidence |
| --- | --- | --- | --- |
| [#713](https://github.com/corca-ai/charness/issues/713) | 2026-08-24 08:45 | include | Live bug: a Ceal test-only lane was stopped by an unrelated global interrupt while a path-bound invocation proceeded. |
| [#712](https://github.com/corca-ai/charness/issues/712) | 2026-08-23 05:02 | exclude | Open release-review obligation for Charness 6.4.0 verdict logic; no consumer episode. |
| [#711](https://github.com/corca-ai/charness/issues/711) | 2026-08-23 05:01 | exclude | Internal dup-ratchet numerator proof gap; current code is correct and no consumer episode is recorded. |
| [#710](https://github.com/corca-ai/charness/issues/710) | 2026-08-23 05:01 | exclude | Live repo-owned advisory normalization defect; no observed consumer episode. |
| [#709](https://github.com/corca-ai/charness/issues/709) | 2026-08-23 05:01 | exclude | Internal nonzero summary-projection test is missing; current code is correct. |
| [#708](https://github.com/corca-ai/charness/issues/708) | 2026-08-23 05:01 | exclude | Charness gate reporting defect and serialized rerun cost; no consumer evidence. |
| [#707](https://github.com/corca-ai/charness/issues/707) | 2026-08-22 23:30 | exclude | Load-dependent flake measured in the Charness release gate. |
| [#706](https://github.com/corca-ai/charness/issues/706) | 2026-08-22 23:19 | exclude | Live internal dup-ratchet summary-truth defect. |
| [#705](https://github.com/corca-ai/charness/issues/705) | 2026-08-22 23:00 | exclude | Live Charness release-record count/claim mismatch. |
| [#704](https://github.com/corca-ai/charness/issues/704) | 2026-08-22 23:00 | exclude | Valid defer; the issue body classifies the surface as repo-owned rather than consumer-installed. |
| [#703](https://github.com/corca-ai/charness/issues/703) | 2026-08-22 22:04 | exclude | Visibility debt in the internal green-run output channel. |
| [#702](https://github.com/corca-ai/charness/issues/702) | 2026-08-22 21:39 | exclude | Charness goal/retro headline citation discipline, without a consumer episode. |
| [#701](https://github.com/corca-ai/charness/issues/701) | 2026-08-22 07:23 | exclude | Charness release claims-loop fixed-point design problem. |
| [#700](https://github.com/corca-ai/charness/issues/700) | 2026-08-22 07:22 | exclude | Charness release-grant narrative revalidation problem. |
| [#699](https://github.com/corca-ai/charness/issues/699) | 2026-08-22 05:19 | exclude | Live Charness publish-authorization bug; no consumer incident is recorded. |
| [#698](https://github.com/corca-ai/charness/issues/698) | 2026-08-22 04:38 | dependency | Live correctness residual of #691: `superseded` can lose Auto-Retro or remainder disposition. |
| [#697](https://github.com/corca-ai/charness/issues/697) | 2026-08-22 02:42 | exclude | Live Charness mutation/changed-line coverage artifact collision. |
| [#696](https://github.com/corca-ai/charness/issues/696) | 2026-08-22 02:04 | exclude | Live Charness gate performance bug measured at 8.22 GB corpus and 20.4 GB RSS. |
| [#695](https://github.com/corca-ai/charness/issues/695) | 2026-08-21 22:49 | exclude | Live Charness closeout-shape bug found in an internal issue program. |
| [#694](https://github.com/corca-ai/charness/issues/694) | 2026-08-22 04:38 | exclude | Main source path repaired; open residual is a second internal blind shape. |
| [#693](https://github.com/corca-ai/charness/issues/693) | 2026-08-21 22:22 | exclude | Live review-contract enforcement gap, but no concrete consumer-friction episode. |
| [#692](https://github.com/corca-ai/charness/issues/692) | 2026-08-21 22:22 | include | Installed 6.2.1 `release` bootstrap failed on a second valid run; only `impl` is currently idempotent. |
| [#691](https://github.com/corca-ai/charness/issues/691) | 2026-08-21 21:53 | include | Ceal uses eight `superseded` goals; current source now has the status and tests, while #698 retains a separate residual. |
| [#690](https://github.com/corca-ai/charness/issues/690) | 2026-08-21 21:59 | include | Repeated Ceal episode; current source now has the hollow-section classifier and tests. |
| [#689](https://github.com/corca-ai/charness/issues/689) | 2026-08-21 21:52 | include | Three Ceal Node repositories cannot use the common harness and reimplemented a repo-local `prove-guard`. |
| [#688](https://github.com/corca-ai/charness/issues/688) | 2026-08-21 22:14 | include | Live and reproducible: malformed ``: strong` output and all three source retros exist in `../ceal`. |
| [#687](https://github.com/corca-ai/charness/issues/687) | 2026-08-20 22:13 | include | Two Ceal reviewers timed out or were interrupted without findings; typed non-delivery is source-proven but host terminal delivery is not. |
| [#680](https://github.com/corca-ai/charness/issues/680) | 2026-08-20 09:14 | include | Ceal's installed plugin assigned reviewed-input identity to a zero-section packet; explicit-path behavior needs current requalification. |
| [#671](https://github.com/corca-ai/charness/issues/671) | 2026-08-18 14:18 | include | A Linux path remained in a macOS Ceal goal; executable-path refusal exists, but the critique portability angle is missing. |
| [#669](https://github.com/corca-ai/charness/issues/669) | 2026-08-18 06:28 | exclude | Live `Popen`/SIGTERM race observed in a Charness release lane. |
| [#668](https://github.com/corca-ai/charness/issues/668) | 2026-08-18 06:48 | exclude | Measured Charness standing-pytest profiling/shrink debt. |
| [#667](https://github.com/corca-ai/charness/issues/667) | 2026-08-18 01:27 | include | Ceal's proven three-repo release lanes are contradicted by the generic planner's `not releasable` answer. |
| [#637](https://github.com/corca-ai/charness/issues/637) | 2026-08-20 13:02 | include | Ceal 6.0.0/6.2.0 installed layouts failed with a `/skills/public/...` ENOENT; current behavior is classified already-satisfied. |
| [#634](https://github.com/corca-ai/charness/issues/634) | 2026-08-15 14:42 | include | A consuming machine hit a PyYAML dependency failure; two export entrypoints are repaired while other self-sufficiency families remain. |
| [#628](https://github.com/corca-ai/charness/issues/628) | 2026-08-18 10:57 | exclude | Dangerous scaffold defect, but the recorded trigger is internal to Charness. |
| [#612](https://github.com/corca-ai/charness/issues/612) | 2026-08-22 12:49 | exclude | Open mutation regression on Charness main. |
| [#605](https://github.com/corca-ai/charness/issues/605) | 2026-08-14 03:20 | exclude | Unproven defer; body/comments could not construct a live trigger. |
| [#601](https://github.com/corca-ai/charness/issues/601) | 2026-08-12 17:43 | include | Ceal release proof takes about 15 minutes; 226 real-binary spawns concentrate 63% of wall time in 2% of files. A generic threshold is still unproven. |
| [#599](https://github.com/corca-ai/charness/issues/599) | 2026-08-12 17:42 | exclude | Deferred capability from seven wrong removals inside Charness; no consumer episode. |
| [#587](https://github.com/corca-ai/charness/issues/587) | 2026-08-12 14:57 | exclude | Original serial-aggregate diagnosis and remedy were refuted by measurement. |
| [#586](https://github.com/corca-ai/charness/issues/586) | 2026-08-12 15:35 | exclude | Deferred without a current reproducer; candidate helper is superseded and consumers were not inspected. |
| [#584](https://github.com/corca-ai/charness/issues/584) | 2026-08-13 00:25 | exclude | Partial umbrella; representative read-cost slice is repaired and the residual is broader planner rollout. |
| [#583](https://github.com/corca-ai/charness/issues/583) | 2026-08-12 15:57 | exclude | Deferred pending a concrete reproducer; known pickup fail-open paths were removed or repaired. |
| [#582](https://github.com/corca-ai/charness/issues/582) | 2026-08-12 16:10 | exclude | Partial umbrella; remaining work is internal schema/ruling debt. |
| [#550](https://github.com/corca-ai/charness/issues/550) | 2026-08-12 17:27 | exclude | Unproven defer; the body records neither consumer inspection nor a wrong verdict. |
| [#546](https://github.com/corca-ai/charness/issues/546) | 2026-08-14 03:21 | exclude | Partial; the body says consumer application is unproven and a conditional schema is still needed. |

## Cohort Accounting

- Included direct consumer friction: 13
- Required correctness dependency: 1
- Excluded from this consumer-friction program: 32
- Total current open issues: 46

This matrix is an inventory and routing artifact, not a close verdict. Every
included or dependency row still requires issue-specific current-source,
installed-consumer, and requested-outcome proof before closure or narrowing.
