# Blinded Handoff Quality Packet — Refresh Run 1

Judge each packet against the handoff refresh contract. Prefer a packet only for a material contract-anchored quality reason. A good packet should preserve a useful `docs/handoff.md`, keep only next-action state, avoid diary prose, include honest `Refresh kept:` / `Refresh non-claims:` closeout accounting, and avoid unverified overclaim. Ties are acceptable. Do not infer arm identity; labels are randomized per run.

## Packet A

### Observed Summary

Execution of /handoff: 2508626 total tokens (75689 output, 2214703 cache-read), 438811ms wall. Tool profile: Bash=19 Read=5 Edit=4 Write=1 Agent=1. All declared claims met. Reference coverage: 1/5 DEPTH references opened (missing: adapter-contract.md, chunked-routing.md, continuation-sequence.md, workflow-trigger.md). Advisory ref classes: 1 INLINE, 0 DUP (excluded from the coverage ratio). Waste smells: 3 (duplicate_read, repeated_edit, repeated_bash).

### Produced `docs/handoff.md`

# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 went RED on the 2026-07-09 01:11 UTC scheduled run** (run
  [28986563107](https://github.com/corca-ai/charness/actions/runs/28986563107),
  head `f84eb223`): the coverage-baseline pytest failed before any mutants ran
  — `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`;
  the StrykerJS missing-report FAIL is collateral. The failing nodeid **passes
  in isolation locally at both the current tree and `f84eb223`** (verified
  2026-07-09), so suspect full-suite interaction (CI runs the whole coverage
  baseline) or CI-env divergence — not a plain unit regression at that commit.
- **#423 CLOSED (2026-07-08).** Its prompt-mutation pilot left two open
  harness issues: **#426** (mutant-arm captures unblind themselves via
  `git show`/`git diff` on the neutral snapshot commit) and **#427** (scorer
  `stream.jsonl` fallback matches marker mentions anywhere, not only
  command-bearing `tool_use` events). Both issues cite the 2026-07-09
  prompt-mutation pilot report; that artifact is not in this checkout, so
  treat the issue bodies as the working source.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Unblock #421 (machine-owned close; do not close manually)**: the single
   nodeid already passes locally at `f84eb223`, so start with the full
   coverage-baseline pytest at `f84eb223` in a throwaway worktree
   (suite-interaction suspect); if that is green too, read the workflow run
   logs for CI-env divergence. Land the fix and let the scheduled run
   (`17 */12 * * *` UTC) judge and auto-close.
2. **Resolve #426 and #427** (prompt-mutation capture self-unblinding; scorer
   stream fallback over-matching). Issue bodies are the spec; fix shape goes
   through the issue workflow — phrasings here are symptoms, not designs.
3. **81-site argparse-help debt (run LAST, alone).** Trip-wire D33:
   `run_skill_efficiency_ab.py` at 479/480.

## Discuss

- **RULE_DATE floor practice (retro 2026-07-08)**: on a grandfathered-floor's
  landing day, run the suite as-of tomorrow's enforcement date so truncating
  consumers detonate before push; promote to a gate only on recurrence.
- **D34/D35 DECLINED** (2026-07-04); reopen only if the recorded failure
  materializes. See [deferred-decisions.md](./deferred-decisions.md).
- Deferred from #420 close: nothing pins the `--advisory` flag at
  `run-quality.sh:505`; add a pin only if the hard-block posture regresses.

## References

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md)
  (prior 2026-07-06..08 red, resolved — reuse its worktree-bisect method, not
  its conclusion; the 2026-07-09 red is a new baseline failure, see Current
  State) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)


### Assistant Closing Text

Running the three cheap deterministic gates the planner named.

Worktree removed. Now applying the critique fixes to the handoff.

Gates green at 58/70 lines. Committing the refresh.

Handoff refresh is done and committed (`6aad3f1d`), all three deterministic gates green at 58/70 lines. The live state had moved substantially since the last write, and the rewrite reorders the pickup around it:

- **#421 went red, not green.** The 2026-07-09 01:11 UTC scheduled run failed its coverage-baseline pytest before any mutants ran (`test_capture_script_behavioral_no_identity_in_run_view` at head `f84eb223`); the StrykerJS failure is collateral. I verified the failing test **passes in isolation locally at both the current tree and `f84eb223`**, so the handoff now points the next operator at full-suite interaction or CI-env divergence first, not at a unit regression — and keeps the do-not-close-manually boundary.
- **#423 is closed**; its slot is replaced by the two open follow-ups **#426** (captures unblind via diffing the snapshot commit) and **#427** (scorer stream fallback matches mentions, not executions), with issue bodies named as the spec since the cited pilot artifact isn't in this checkout.
- The completed **#410 diary paragraph was dropped** — its detail already lives in the census-reconciliation artifact.

A fresh-eye subagent critique ran on the material change and produced two clarity fixes I applied: the #421 first move is now a concrete throwaway-worktree suite run instead of vague "CI conditions", and the prior-red debug artifact link is annotated so its resolved conclusion (a different failing test) isn't mistaken for a diagnosis of the new red. One reviewer claim ("local main ahead 9") didn't survive verification — this checkout is ahead of `origin/main` by exactly one commit, and I excluded the commit-difference hypothesis by direct test instead of recording it.

Refresh kept: the #421 red signal with its reproduce-fork (passes in isolation at both trees → suite-interaction or CI-env), the machine-owned-close boundary, #426/#427 as the queued harness work, the test-debt rotation baseline `8e1fd200`, the argparse-debt run-LAST rule with trip-wire D33, and the three Discuss decisions (RULE_DATE floor practice stays — the 2026-07-08 retro explicitly defers it to this section).

Refresh non-claims: the #410 execution narrative (spilled to `charness-artifacts/reference-compaction/slice7-census-reconciliation.md`), the closed #423 entry, the missing pilot-report path as a link target (issues are the working source), and any root cause for the new #421 red — only the isolation-pass facts are proven; the suite-interaction/CI-env fork is a hypothesis, not a diagnosis.

## Packet B

### Observed Summary

Execution of /handoff: 2560533 total tokens (54498 output, 2285732 cache-read), 501517ms wall. Tool profile: Bash=31 Read=3 Edit=2 Write=1 Agent=1 ReportFindings=1. All declared claims met. Reference coverage: 1/5 DEPTH references opened (missing: adapter-contract.md, chunked-routing.md, continuation-sequence.md, workflow-trigger.md). Advisory ref classes: 1 INLINE, 0 DUP (excluded from the coverage ratio). Waste smells: 3 (duplicate_read, repeated_edit, repeated_bash).

### Produced `docs/handoff.md`

# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 went RED on the 2026-07-09 01:11 UTC scheduled run** (commit
  `f84eb223`): the coverage baseline pytest failed before any mutants ran —
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
  (the #423 blinding fix's behavioral test). That test passes at this
  checkout's snapshot, so suspect commit- or CI-env-specific breakage.
  Summary + workflow-run link live in the issue comment.
- **#423 CLOSED** (2026-07-08): capture eval-identity blinding fix landed with
  the behavioral test above.
- **Prompt-mutation pilot (2026-07-09) filed two harness follow-ups**: #426
  (mutant-arm captures unblind themselves by diffing the neutral snapshot
  commit) and #427 (scorer `stream.jsonl` fallback matches marker mentions,
  not command executions). The issue bodies carry the evidence pointers.
- **This checkout is a stale squashed snapshot**: `f84eb223` is not an
  ancestor of local HEAD, and the whole prompt-mutation harness the issues
  reference is absent here. Sync to current main before any code work.
- #410 queue executed end-to-end and closed; method + results:
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
- Test-debt rotation baseline stays `8e1fd200` (method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Debug the #421 red** (machine-owned issue; do not close manually): read
   the 2026-07-09 01:11 UTC comment + linked workflow run, then reproduce the
   failing baseline test at `f84eb223` **in a disposable worktree** (it is not
   an ancestor of this snapshot). Treat this as a fresh diagnosis: #421 has
   now carried three unrelated baseline failures, and
   [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md)
   covers an earlier, already-fixed one (RULE_DATE floor).
2. **#426 + #427 prompt-mutation harness fixes** (on a synced checkout —
   the harness is absent from this snapshot): blind mutant-arm captures to
   the snapshot-commit diff; constrain the scorer stream fallback to
   command-bearing (tool_use) events.
3. **81-site argparse-help debt (run LAST, alone).** Trip-wire D33:
   `run_skill_efficiency_ab.py` at 479/480.

## Discuss

- **RULE_DATE floor practice (retro 2026-07-08)**: on a grandfathered-floor's
  landing day, run the suite as-of tomorrow's enforcement date so truncating
  consumers detonate before push; promote to a gate only on recurrence.
- **D34/D35 DECLINED** (2026-07-04); reopen only if the recorded failure
  materializes. See [deferred-decisions.md](./deferred-decisions.md).
- Deferred from #420 close: nothing pins the `--advisory` flag at
  `run-quality.sh:505`; add a pin only if the hard-block posture regresses.

## References

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)


### Assistant Closing Text

I'll run the handoff planner first to scope this refresh pass.

Now inspecting live repo state that could change the next action.

Now running the deterministic gates the planner named.

Handoff refresh complete — `docs/handoff.md` rewritten, all three deterministic gates green (59/70 lines), fresh-eye critique run and its fixes incorporated, and the change committed as `a076ca53` (note: this checkout is on a detached squashed snapshot, so the commit lives here, not on a branch).

The material change: the next session's first move is no longer "watch #421, expected green." The scheduled run went **red** at 2026-07-09 01:11 UTC on `f84eb223` — the coverage baseline pytest failed before any mutants ran, on `test_capture_script_behavioral_no_identity_in_run_view` (the #423 blinding fix's test, and #423 itself is now closed). That test passes at this checkout, so the handoff directs a fresh diagnosis at `f84eb223` in a disposable worktree. Two new prompt-mutation harness issues (#426 capture unblinding, #427 scorer stream-fallback false fires) are queued second, with an explicit warning that this snapshot predates that harness entirely and code work needs a synced checkout. The critique also caught that the prior #421 debug artifact covers a different, already-fixed failure, so the handoff no longer implies continuity between the reds.

Refresh kept: #421 red signal + failing test name + machine-owned/do-not-close rule, #423 closed, #426/#427 as next fixes, the stale-snapshot fact (it changes every code-work first move), test-debt baseline `8e1fd200`, and the three standing Discuss items.

Refresh non-claims: the #410 census detail stays spilled to `slice7-census-reconciliation.md`; no root cause is claimed for the new #421 red (only the observed signal and that it differs from the two prior failures); the prompt-mutation pilot report is referenced only via the issues since it doesn't exist in this snapshot; and per #426 I did not diff the snapshot commit to inspect its provenance.

