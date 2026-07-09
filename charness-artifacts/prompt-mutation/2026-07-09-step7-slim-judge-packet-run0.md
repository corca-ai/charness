# Blinded Handoff Quality Packet — Refresh Run 0

Judge each packet against the handoff refresh contract. Prefer a packet only for a material contract-anchored quality reason. A good packet should preserve a useful `docs/handoff.md`, keep only next-action state, avoid diary prose, include honest `Refresh kept:` / `Refresh non-claims:` closeout accounting, and avoid unverified overclaim. Ties are acceptable. Do not infer arm identity; labels are randomized per run.

## Packet A

### Observed Summary

Execution of /handoff: 2177976 total tokens (56126 output, 1888464 cache-read), 430096ms wall. Tool profile: Bash=26 Read=7 Edit=2 Write=1 Agent=1. All declared claims met. Reference coverage: 3/5 DEPTH references opened (missing: adapter-contract.md, continuation-sequence.md). Advisory ref classes: 1 INLINE, 0 DUP (excluded from the coverage ratio). Waste smells: 2 (duplicate_read, repeated_edit).

### Produced `docs/handoff.md`

# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`). This is the
  same no-task trigger as a bare `/handoff`: both run chunked routing over
  handoff + open issues.

## Current State

- **#421 nightly mutation gate went RED again (2026-07-09 01:11 UTC, run
  [28986563107](https://github.com/corca-ai/charness/actions/runs/28986563107),
  head `f84eb223`).** The #422 fix is working — the summary now names the real
  blocker: baseline pytest fails on
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
  (the #423 blinding guard) before any mutants run. That test **passes locally
  at this snapshot**, so the split is CI-environment-specific or the CI head
  predates a fix. Prior #421 root-cause history:
  [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md).
- #410 (handoff pickup floor + capture queue) and #423 (capture eval-identity
  blinding) are both CLOSED; method and per-condition results live in
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Debug the #421 CI-only red (route through `debug`; the issue is
   machine-owned — do not close it manually).** Reproduce the CI-vs-local split
   on the #423 guard test first; the scheduled run (`17 */12 * * *` UTC) stays
   red until the CI run's baseline passes (cause still open: a main-content
   fix, or a CI-environment-specific fix).
2. **81-site argparse-help debt (run LAST, alone).** Trip-wire D33:
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

I'll run the handoff planner first, per the skill bootstrap.

The handoff is in good shape structurally (48 lines, no dated diary sections). Now I'll check the live state that could change the next action — issue statuses and referenced artifacts.

It passes locally but failed in CI — that's the key fact for the next session. Let me quickly check the owning debug artifact so the pointer is accurate.

Now the cheap deterministic gates from the plan:

The reviewer confirmed the next action and ownership boundaries, and flagged two concrete clarity fixes. Applying both:

Refresh done and committed (`a30804fc`). The headline change: the previous handoff expected #421 to auto-close green, but the live check showed the nightly mutation gate went **red again** at 2026-07-09 01:11 UTC — baseline pytest fails in CI on `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view` (the guard test from the #423 fix), while that same test **passes locally** at this snapshot. The next session's first move is now debugging that CI-vs-local split via the `debug` skill; #421 stays machine-owned and must not be closed manually. #423 and #410 are both CLOSED, so their next-action entries were dropped and the session diary was compressed to a pointer at the owning census artifact.

All three deterministic gates pass (shape, pointer freshness, authoring preflight; 49/70 lines). The bounded fresh-eye critique confirmed the next action and ownership boundaries, and produced two clarity fixes I applied: the Workflow Trigger now states that session-start pickup and a bare `/handoff` are the same no-task trigger (both run chunked routing), and the "stays red until…" clause is hedged so an operator doesn't skip CI-environment reproduction by just pushing to main and waiting for green.

Refresh kept: the #421 red evidence (run 28986563107, head `f84eb223`, failing test node id, local-pass observation) because it defines the first debug move; the machine-owned-close boundary; the argparse-help debt item with trip-wire D33; the test-debt rotation baseline `8e1fd200`; and the three Discuss items (RULE_DATE floor practice, D34/D35 declined, `--advisory` pin deferral).

Refresh non-claims: the #410 session narrative was spilled to `charness-artifacts/reference-compaction/slice7-census-reconciliation.md` (already the owning artifact); the closed #423 next-action was dropped; the root cause of the new #421 red is unproven — local pass vs CI fail is observed fact, but whether it's a CI-environment difference or a fix postdating `f84eb223` is explicitly left open for the debug session.

## Packet B

### Observed Summary

Execution of /handoff: 1319507 total tokens (47482 output, 1120509 cache-read), 305167ms wall. Tool profile: Bash=8 Read=4 Edit=3 Write=1 Agent=1. All declared claims met. Reference coverage: 1/5 DEPTH references opened (missing: adapter-contract.md, chunked-routing.md, continuation-sequence.md, workflow-trigger.md). Advisory ref classes: 1 INLINE, 0 DUP (excluded from the coverage ratio). Waste smells: 2 (duplicate_read, repeated_edit).

### Produced `docs/handoff.md`

# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> the session-start hook routes
  straight into **`charness:handoff`** (not `find-skills`), which — given no
  task directive — runs chunked routing over handoff + open issues. A bare
  `/handoff` mid-session is the same no-task flow.

## Current State

- **#421 is RED with a new cause (not the #422 regression)**: the 2026-07-09
  01:11 UTC run on `f84eb223` failed baseline pytest before any mutants ran —
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`.
  That test is the behavioral proof for the #423 capture-blinding fix; #423
  itself is CLOSED (2026-07-08 18:28), so the fix landed but its test fails in
  CI. The test **passes locally** (re-proven 2026-07-09 on this checkout), so
  suspect CI-environment sensitivity, not a plain logic break.
- **2026-07-09 prompt-mutation pilot filed two harness bugs**: #426 (mutant-arm
  captures unblind themselves via `git show`/`git diff` of the neutral
  `chore: snapshot` mutant commit; m-workflow NO-OBSERVED-EFFECT attribution is
  confounded, m-closeout stayed clean) and #427 (scorer `stream.jsonl` fallback
  matches marker mentions anywhere in the stream, not command-bearing tool_use
  events; one stream-based fire already withdrawn). Evidence and verdicts live
  in the pilot artifact both issues cite — it may not exist in your checkout;
  read it via `gh issue view 426` / `427`, not by path.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Diagnose the #421 baseline red (CI-only failure).** Read the failing run
   (<https://github.com/corca-ai/charness/actions/runs/28986563107>), then find
   why `test_capture_script_behavioral_no_identity_in_run_view` fails in CI
   while passing locally. #421 stays machine-owned — do not close manually; the
   next scheduled run (`17 */12 * * *` UTC) is the green observer.
2. **#426 capture-unblinding fix**: make the mutant snapshot commit
   non-disclosing from inside the captured run (no readable removed-diff one
   `git show` away); this gates blinding validity for every future
   prompt-mutation run.
3. **#427 scorer fix**: constrain the `stream.jsonl` trace-marker fallback to
   command-bearing (tool_use) events.
4. **81-site argparse-help debt (run LAST, alone).** Trip-wire D33:
   `run_skill_efficiency_ab.py` at 479/480 (counts as of 2026-07-09; re-verify
   before acting since items 1-3 land first).

## Discuss

- **RULE_DATE floor practice (retro 2026-07-08)**: on a grandfathered-floor's
  landing day, run the suite as-of tomorrow's enforcement date so truncating
  consumers detonate before push; promote to a gate only on recurrence.
- **D34/D35 DECLINED** (2026-07-04); reopen only if the recorded failure
  materializes. See [deferred-decisions.md](./deferred-decisions.md).
- Deferred from #420 close: nothing pins the `--advisory` flag at
  `run-quality.sh:505`; add a pin only if the hard-block posture regresses.

## References

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md) (prior #421 red — different cause; read to avoid conflating) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)


### Assistant Closing Text

I'll start by running the handoff planner to scope this refresh pass.

Now writing the refreshed handoff:

Now running the cheap deterministic gates the planner named:

No blockers, three clarity nits — all concrete, so I'll incorporate them:

Handoff refresh complete — `docs/handoff.md` rewritten (59/70 lines, all three deterministic gates green), fresh-eye critique run, and committed as `1b3bcfff` (this checkout is a detached-HEAD snapshot, so the commit sits on top of `36636b8f chore: snapshot`).

**What changed and why.** Live state had moved out from under the old handoff:

- **#421 went red, not green.** The 2026-07-09 01:11 UTC scheduled run failed baseline pytest on `f84eb223` — the failing test is `test_capture_script_behavioral_no_identity_in_run_view`, the behavioral proof of the #423 capture-blinding fix. #423 itself closed 2026-07-08, and the test passes locally in this checkout (I re-proved it: 1 passed in 0.56s), so the new pickup is a CI-only diagnosis, not the old #422 story. Next-action 1 flipped from "watch expected-green" to "diagnose the red"; the machine-owned/do-not-close-manually boundary is kept.
- **Two new pilot-filed issues added** as actions 2–3: #426 (mutant-arm captures unblind themselves by diffing the `chore: snapshot` mutant commit) and #427 (scorer `stream.jsonl` fallback matches marker *mentions*, not command-bearing tool_use events). Their evidence artifact isn't in this checkout, so the handoff points readers at the issues rather than a dead path.
- **Spilled/dropped:** the closed #410 session paragraph (owned by the slice7 census-reconciliation artifact) and the closed-#423 filing entry.

The bounded fresh-eye critique (parent-delegated, medium tier) found no blockers and three clarity nits — trigger-section ambiguity, missing access note for the pilot artifact, over-literalizable 479/480 count — all incorporated before commit.

Refresh kept: the #421 red diagnosis pickup (cause, failing test, passes-locally fact, run URL, machine-owned close boundary), the #426/#427 next actions with issue-based evidence access, the test-debt rotation baseline `8e1fd200`, the argparse-debt run-LAST item with D33 trip-wire, and the three open Discuss decisions.

Refresh non-claims: #410 session detail dropped (spilled to the slice7 census-reconciliation artifact), the closed #423 filing entry dropped, no root cause claimed for the CI-only test failure (unproven — passes locally, failed on `f84eb223` in CI), and the pilot artifact's content not restated (not present in this checkout; owned by #426/#427).

