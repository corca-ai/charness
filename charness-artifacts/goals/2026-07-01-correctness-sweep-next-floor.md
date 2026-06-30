# Achieve Goal: Capture the next hypothesis-floor skill (`impl`) one at a time via cautilus, reusing the proven outcome-assertion pattern; a floor miss is a skill-shape signal, never a softened matcher.

Status: complete
Created: 2026-07-01
Activation: `/goal @charness-artifacts/goals/2026-07-01-correctness-sweep-next-floor.md`
Activation time: 2026-07-01T03:32:15+09:00

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: COMPLETE (2026-07-01 KST) — all 3 slices executed; impl
  captured (5th sweep skill); floor MISS (0/8) + substance 4/5; finding + assertion
  set + retro committed; harness gaps filed as #409; impl stays HYPOTHESIS (floor
  un-softened). See `## Final Verification`.
- Selected target: `impl` (RCF floor `verification-ladder.md`) — chosen from the 14
  remaining HYPOTHESIS-floor skills as the lowest-risk, highest-value next capture
  (single methodologically-sound engage-always floor, concrete executable subject,
  sandbox-safe, no external writes). Decision rationale in `## Interview Decisions`.
- Next action: none — goal complete. The operator decision (impl closeout-vocabulary
  skill-shape) is in `## Off-Goal Findings`; the next sweep skill is in the handoff.
- Verification cadence: cheap deterministic checks (validators, the grader
  self-test) at commit boundaries; the live cautilus capture + observation score is
  the external proof at the slice boundary. Operator pre-authorized the spend.
- Slice review packet: before fresh-eye slice critique, hand the reviewer intent,
  changed files + owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`, and
  `## Auto-Retro`.

Discuss before activation: CONFIRMED — Slice 1 is a live cautilus capture (a real
headless `claude -p` run, ~15-20 min, multi-M tokens) and Slice 2 runs a live judge
LLM (grade_skill_outcome.py --judge-cmd, additional spend). Both are token-spend /
live-proof consequential defaults under the ask-before-run cautilus contract. The
operator explicitly pre-authorized this autonomous run and the cautilus capture this
session and is asleep, so the run does NOT pause at the capture boundary; it still
consults `plan_cautilus_proof.py`, invokes via `scripts/run_cautilus_eval.py` with an
operator-log `--justification-log` (never bare `cautilus evaluate`), and gates the
judge behind the grader self-test (good>bad). Exact capture params (HEAD ref,
timeout) are runtime confirmations tracked in the Operator Decision Queue, not
unresolved activation blockers.

## Goal

Advance the correctness sweep by one skill: prove (or refute) that a real
`/charness:impl` run honors its central claim — route to `verification-ladder.md`
at the point of need so it can produce an honest categorized closeout (the Lint
Gate status vocabulary + the five completion-report categories that live ONLY in
that doc). Score BOTH axes the proven pattern uses: the deterministic FLOOR
(cautilus matcher: was `verification-ladder.md` opened? declared-reference
coverage) and the advisory SUBSTANCE (judge: did the run actually execute its
verification and emit the honest closeout vocabulary, not merely claim it). A floor
MISS with a substance PASS is the informative "doc-opening is a weak proxy" result,
not a failure to fix by softening the matcher.

**Source handoff entry #1: Correctness sweep**

> Capture the next hypothesis-floor skill one at a time, REUSING the proven
> outcome-assertion pattern per-eval. A miss = skill-shape signal
> (re-pin / re-classify / planner), never soften the matcher. `--justification-log`
> overrides `next_action: none`; mirror hitl/retro/quality/debug.

So far PROVEN (live-capture): retro, hitl, quality, debug (n=2). `impl` is the 5th
skill captured and the first of the remaining 14 hypothesis-floor skills.

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not soften the cautilus matcher, the floor (`requiredCommandFragments`), or any
  substance assertion to force a PASS. A floor miss is a skill-shape signal
  (re-pin / re-classify / planner work in a FUTURE slice), recorded honestly.
- Do not capture more than one skill this goal (`impl` only); the sweep is
  one-at-a-time by contract.
- Do not encode substance assertions keyed on literal phrases from this capture's
  output (over-fit guard); substance assertions stay judge-kind and discriminating.
- Do not modify the `impl` SKILL surface or `verification-ladder.md` this goal
  (the subject is captured read-only at HEAD); any skill change is a separate goal.

## Boundaries

- In scope: `evals/cautilus/impl-claim-fidelity/` (spec + new outcome-assertions),
  a dated capture bundle under `charness-artifacts/cautilus/`, the cautilus
  eval-only contract (`plan_cautilus_proof.py` + `scripts/run_cautilus_eval.py`).
- Portable per implementation-discipline: no host-specific assumption.
- Stop conditions: capture `impl` only; do not guess at a different skill. If the
  capture harness fails at the runtime level (creds/worktree/host block), stop and
  report the concrete signal rather than fabricating a result.

## User Acceptance

The operator accepts this goal as done when:

- A real, isolated, headless `/charness:impl` capture at HEAD exists on disk with
  its full session-log tree, scored on the FLOOR axis via the canonical wrapper
  (`run_cautilus_eval.py --mode observation`), with an explicit pass/fail + declared-
  reference coverage recorded.
- The SUBSTANCE axis is graded with a newly-authored, committed
  `impl` `outcome-assertions.json` (grader self-test good>bad passing first), OR an
  honest explicit non-claim states why the judge step was skipped.
- A `finding.md` records the verdict on both axes and a clear disposition: `impl`
  PROVEN (floor met), or stays HYPOTHESIS with the floor-miss/substance result
  named as a skill-shape signal — never a softened matcher.
- If (and only if) the capture PASSES the floor AND completes naturally (not a
  timeout cap), `evals/cautilus/impl-claim-fidelity/spec.json`
  `thresholds.max_duration_ms` is set to ~2x the passing baseline; otherwise it
  stays unset with the reason recorded.
- Meaningful `charness-artifacts/` + eval changes committed; handoff updated at
  closeout (end-only write) with the sweep state and the next skill.

## Agent Verification Plan

- **Pre-capture gate:** `plan_cautilus_proof.py --repo-root . --json` consulted;
  run authorized via operator-log `--justification-log` (overrides `next_action:
  none` per the handoff + cautilus-on-demand contract). Invoke ONLY through
  `scripts/run_cautilus_eval.py`, never bare `cautilus evaluate`.
- **Floor (deterministic, canonical):** `build-skill-execution-observation.mjs`
  emits `observed.v1.json`; `run_cautilus_eval.py --mode observation` scores the
  `requiredCommandFragments=[verification-ladder.md]` matcher + declared-reference
  coverage → `cautilus-report.json`. This is the correctness signal.
- **Substance (advisory judge):** author `impl` `outcome-assertions.json`
  (deterministic `ran-impl` sanity + judge-kind: executed-verification, honest-
  categorized-closeout). `grade_skill_outcome.py --selftest` MUST rank good>bad
  before any judge spend; then `--judge-cmd` over the preserved bundle →
  `outcome-grade.md`. Advisory, never gates.
- **Closeout gate:** repo quality gate / documented substitute; `check_goal_artifact.py`
  green; finding.md + spec/assertion changes committed; `retro`.
- Named proof level: a local floor score is NOT a provider/live claim beyond what
  the capture observed; the substance grade is advisory; both recorded as such.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Floor capture of `/charness:impl` at HEAD; **preserve produced files + transcript into the bundle BEFORE worktree cleanup** (plan-critique blocker #1); build observation; score the `verification-ladder.md` floor + coverage via the wrapper | The literal "capture the next hypothesis-floor skill"; deterministic + free to score once captured | `justification.md`, `outputs/` + `outputs-manifest.json`, `transcript.txt`, `observed.v1.json`, `trace-digest.jsonl`, `cautilus-report.json`, floor verdict + coverage | pending |
| 2 | Author `impl` `outcome-assertions.json` (deterministic `ran-impl` + `output_glob tests/**/*.py`; judge `executed-verification` + `honest-categorized-closeout`); grade substance (self-test gate → judge over the preserved bundle) | Reuses the proven outcome-assertion pattern; substance is the real signal when the floor is a weak proxy | committed `outcome-assertions.json`, `grade.selftest.txt` (good>bad), `outcome-grade.md` | pending |
| 3 | Write `finding.md` (timeout cap ≠ capture failure — partial tree is usable, threshold stays unset); set spec threshold iff PASS+natural-complete; commit; closeout | Durable disposition + sweep state; closeout discipline | `finding.md`, spec diff (or "unset, reason"), commit, retro, handoff update | pending |

## Operator Decision Queue

- Decision: capture runtime params (HEAD ref, `--timeout-sec`). Owner: agent
  (operator pre-authorized). RESOLVED: ran `--ref HEAD --timeout-sec 1200`; exit 0
  natural completion at 123821ms. No operator action needed.
- Decision: judge LLM spend for the substance grade. Owner: operator (pre-authorized
  via "you can run cautilus" + the proven pattern). RESOLVED: grader `--selftest`
  PASSED (good=1.0/bad=0.0) first, then 3 judge calls ran. No operator action needed.
- Decision (OPEN, operator): impl closeout-vocabulary skill-shape fork — internalize
  the enum into `impl/SKILL.md` vs keep `verification-ladder.md` load-bearing. Owner:
  operator. Why deferred: a skill-design call, not a blocker; the capture stands as
  evidence either way. Unblock action: pick a direction; then file/route the change.
  Revisit trigger: next time the impl floor or the correctness sweep is touched.

## Slice Log

- **Slice 1 — floor capture (DONE).** Authored `justification.md` (operator-log);
  ran `capture-skill-run.sh --invocation "<spec pinned prompt>" --ref HEAD
  --timeout-sec 1200`; exit 0 (natural completion, 123821ms). Discovered the run
  COMMITTED its slice (`2ab1f891`), so `preserve_outputs`' diff-vs-HEAD was empty —
  preserved the changed set vs the capture ref (d5e222a6) instead; rebuilt
  `transcript.txt` from the complete `stream.jsonl` (tree was missing the final
  block). Built `observed.v1.json`; scored floor via `run_cautilus_eval.py --mode
  observation` → **MISS, coverage 0/8** (`verification-ladder.md` not opened).
  Test-pressure: n/a (no repo test added this slice; the capture's SUBJECT added
  tests, graded under Slice 2).
- **Slice 2 — substance (DONE).** Authored
  `evals/cautilus/impl-claim-fidelity/outcome-assertions.json` (2 deterministic + 3
  judge); `validate_outcome_assertions.py` OK; grader `--selftest` PASSED
  (good=1.0/bad=0.0). Graded with `--judge-cmd outcome_judge_cmd.py` →
  **pass_rate 0.714 (4/5)**: executed-verification PASS, smallest-non-overlapping-slice
  PASS, wrote-tests + ran-impl PASS, `honest-categorized-closeout` FAIL (prose, not
  canonical enum). Test-pressure (the new assertion set): additive companion to the
  spec; `validate_outcome_assertions.py` covers it; no duplicate of an existing set.
- **Slice 3 — finding + closeout (DONE).** Wrote `finding.md`; threshold left UNSET
  (floor not passed; 123821ms recorded as future baseline); filed #409 for the two
  harness gaps; ran + persisted retro; committed; flipped to complete.

## Context Sources

- Source: handoff entry #1 (Correctness sweep) — see [docs/handoff.md](../../docs/handoff.md).
- Cautilus current pointer + last passing proof: [charness-artifacts/cautilus/latest.md](../cautilus/latest.md).
- Proven pattern to reuse: debug Plan-C capture2 finding + debug `outcome-assertions.json`
  (`evals/cautilus/debug-claim-fidelity/outcome-assertions.json`).
- Eval-only contract: [skills/public/quality/references/cautilus-on-demand.md](../../skills/public/quality/references/cautilus-on-demand.md).
- `impl` floor analysis: `evals/cautilus/impl-claim-fidelity/spec.json` `_comment`.

## Interview Decisions

This is an autonomous run (operator asleep, pre-authorized); high-leverage
decisions were settled by judgment and recorded here rather than asked.

- **Which skill is next? → `impl`.** The 14 remaining HYPOTHESIS-floor skills are
  achieve, announcement, create-cli, create-skill, critique, find-skills, gather,
  handoff, hotl, ideation, impl, narrative, release, spec. `impl` selected because:
  (1) single, methodologically-sound engage-always floor (`verification-ladder.md` —
  the Lint Gate vocab + 5 completion-report categories live ONLY there, so an honest
  closeout is genuinely forced to open it; this is a substance assertion, not a
  doc-open proxy); (2) the spec's pinned prompt is a concrete, deterministic,
  executable repo-honest subject (add + run unit tests for `claim_fidelity_lib.py`
  helpers); (3) fully local, sandbox-safe, no external network / credentials /
  human-in-loop / publish — the safest headless capture; (4) `impl` is the most-run
  public skill, so proving its floor is high value.
- **Reject alternatives:** gather/release/hotl/issue need external/network/human
  surfaces (headless-risky); create-cli/create-skill/critique/spec/gather carry
  2-4 floors (heavier scoring); ideation is conversational (thin one-shot risk);
  handoff/find-skills floors are likely script-resolved (higher MISS-by-design risk,
  fine later but a weaker first proof).
- **Both axes, not just the floor.** The handoff says "REUSING the proven
  outcome-assertion pattern"; the debug n=2 thesis is that the floor (doc-opening)
  is a weak proxy and substance is the real signal. So author `impl` substance
  assertions and grade them, not only the floor matcher.
- **One skill only.** The sweep is one-at-a-time by contract; not batching.

## Plan Critique Findings

Bounded fresh-eye plan critique ran pre-activation (separate agent context). Verdict:
plan sound, one real blocker fixed, two worth-fixing folded in, three over-worries
dismissed.

- **BLOCKER (fixed) — output preservation was missing from the pipeline.**
  `capture-skill-run.sh` leaves only the session tree, NOT a bundle `outputs/` dir;
  `build-skill-execution-observation.mjs` doesn't preserve either. The substance judge
  (the plan's own "real signal") reads `outputs/` + `transcript.txt`, so without
  preservation it grades `impl` BLIND to the tests the run wrote, and any
  `output_glob`/`output_file_*` assertion FAILs "no outputs/ dir". impl's substance
  lives in FILES (did it write real, runnable, non-overlapping tests?), so this bites
  harder than it did for debug. **Fix folded into Slice 1:** reuse
  `preserve_outputs()` + `_write_transcript()` from `scripts/run_skill_efficiency_ab.py`
  to copy the worktree's changed set into `<bundle>/outputs/` and render
  `<bundle>/transcript.txt` BEFORE the worktree is removed (capture-skill-run.sh says
  the caller owns cleanup, so the worktree persists for preservation — ordering trap
  noted).
- **WORTH-FIXING (folded) — deterministic-assertion shape.** impl has no fixed durable
  output dir (writes `tests/**`, may touch a contract), so debug's `**/debug/*.md` glob
  has no analog. Decision recorded in Slice 2: deterministic = `ran-impl`
  (summary_contains) + `output_glob tests/**/*.py` (meaningful once preservation lands);
  file-substance otherwise rides on the judge reading `outputs/`.
- **WORTH-FIXING (folded) — author `justification.md` as a genuine operator-log, not a
  pretend failing-log.** First capture, no prior failing run; the honest basis is the
  standing sweep mandate + this session's explicit authorization. Authored as Slice-1
  step 1 (was listed as evidence, now an ordered action).
- **NOTED — likely exit 124 (timeout cap).** Prior proven debug + quality captures both
  hit the 1200s cap; an impl run that writes+runs tests+stop-gate is plausibly as long.
  A timeout is NOT a capture failure (partial tree is usable); the finding must say
  "natural-complete not reached, threshold unset," mirrored in Slice 3.
- **OVER-WORRY (dismissed):** wrong-target (`impl` rationale is sound; the spec `_comment`
  is rigorous and the floor content genuinely exists nowhere else); over-fit/soften
  (guarded by judge-kind assertions + the no-literal-phrase rule + the standing
  no-soften contract); authorization (capture is explicitly authorized; the judge spend
  is gated behind the free offline self-test, so it only runs after a free trust check).

## Off-Goal Findings

- **#409 (filed) — capture→grade pipeline loses outcome-grader evidence for
  clean/committing runs.** Two gaps surfaced this run (preserve_outputs diffs vs HEAD
  but a faithful impl run commits; the session-tree transcript missed the final
  closeout block while stream.jsonl was complete). Worked around manually; filed as
  https://github.com/corca-ai/charness/issues/409. Reason: blocks the sweep's reuse on
  any committing/clean-completing skill.
- **Candidate issue (operator decision) — impl closeout-vocabulary skill-shape.** The
  `honest-categorized-closeout` FAIL is a clean fork: (A) internalize the Lint Gate /
  completion-report enum into `impl/SKILL.md` (debug-Plan-A-style → floor becomes a
  weak proxy, substance passes), or (B) keep `verification-ladder.md` load-bearing (the
  MISS is a real canonical-closeout gap; nudge the planner/skill to route the doc).
  Not filed: needs the operator to pick the direction first. Reason for deferral: it is
  a skill-design decision, not a bug.

## Final Verification

The capture executed and was scored on both axes; nothing was softened to move a
verdict. Honest result (n=1 for impl):

- **FLOOR: MISS** — `cautilus evaluate observation` (via the wrapper): 1 failed / 0
  passed; declared-reference coverage **0/8**; `verification-ladder.md` not opened.
  impl stays a HYPOTHESIS on the floor; `requiredCommandFragments` unchanged.
- **SUBSTANCE: 0.714 (4/5)** — `executed-verification` PASS (real pytest, 17 passed,
  reviewer re-ran → 6), `smallest-non-overlapping-slice` PASS, `ran-impl`/`wrote-tests`
  PASS; `honest-categorized-closeout` FAIL because the run produced the closeout in
  PROSE, not the canonical `verification-ladder.md` enum tokens (which live only in
  that doc and are NOT inlined in SKILL.md). The floor MISS and this FAIL are coherent
  and mutually reinforcing — the doc owns the vocabulary, the run skipped the doc.
- **Threshold:** UNSET (floor not passed; policy derives the budget from a PASSING
  capture). Natural-completion 123821ms recorded for a future PASS.
- **Capability landed:** `evals/cautilus/impl-claim-fidelity/outcome-assertions.json`
  (new, validated). **Harness gaps:** filed as #409.

Non-claims: impl is NOT PROVEN (floor miss stands; n=1). The substance grade is
advisory, not a pass/fail commit verdict. No SKILL surface, planner, matcher, floor, or
assertion was changed to flip any verdict. The capture's metrics are the SUBPROCESS's,
not a host-exposed session log.

Retro: charness-artifacts/retro/2026-07-01-correctness-sweep-next-floor-closeout.md
Host log probe: skipped: host-log-not-exposed: this autonomous CLI achieve session exposes no host-side per-session token/turn log; the capture subprocess metrics (123821ms, 1.28M tokens) live in observed.v1.json, not a session log.
Disposition review: charness-artifacts/retro/2026-07-01-correctness-sweep-next-floor-closeout.md

## User Verification Instructions

- `python3 scripts/validate_outcome_assertions.py` → the new impl set passes.
- Read `charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/finding.md` for the
  honest verdict and `outcome-grade.md` for the per-assertion substance table.
- `python3 scripts/run_cautilus_eval.py --repo-root . --mode observation
  --justification-log charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/justification.md
  --dry-run` → confirms the eval-only gate path (no live run).
- `gh issue view 409` → the two capture-harness gaps, problem-first.
- Decide the impl closeout-vocabulary fork (Off-Goal Findings) — internalize vs
  load-bearing floor.

## Auto-Retro

Retro: charness-artifacts/retro/2026-07-01-correctness-sweep-next-floor-closeout.md

Per-improvement dispositions, mirroring the cited retro's `## Next Improvements`:

- Retro dispositions: issue #409 (novel: first capture of a committing/clean-completing
  skill to expose that grader evidence is derived from a run-invalidatable source —
  diff-vs-HEAD and the tree transcript; no prior recurring class — earlier captures
  (debug/quality/retro/hitl) neither committed nor relied on the preserved outputs the
  same way). Both confirmed sites filed in one issue (the capture→grade evidence
  pipeline is repo-owned).
- Retro dispositions: applied: recent-lessons digest refreshed (on retro persist) with
  "a faithful impl run COMMITS, so diff-vs-HEAD preservation captures nothing — build
  judge evidence from the authoritative stream + diff vs the capture ref" and "validate
  the grader's evidence pipeline before trusting a substance verdict."
- Retro dispositions: out-of-scope: the impl closeout-vocabulary skill-shape fork is an
  operator design decision recorded in Off-Goal Findings, not this goal's capture scope.
- Structural follow-up: issue #409 (novel: first time a committing skill capture exposed
  that grader evidence is derived from a run-invalidatable source — diff-vs-HEAD and the
  tree transcript; a possible third sibling, build-observation's summary-from-tree, is
  noted in #409 for the same fix locus, not separately filed).

## Coordination Cues

Phase→skill routing defers to `find-skills` (no inline map).

- Routing: find-skills (session-start) recommended handoff for the pickup, which
  chunk-routed to achieve for the goal lifecycle; `impl` was the routed work skill
  captured, and critique/retro ran as the achieve plan-critique + after-action review.
- Routing: n/a — no debug or quality phase work ran this goal; those words appear only
  as incidental references (the debug-Plan-A internalization analogy and the planned
  quality-gate substitute), not executed phases, so there is no phase route to record.
- Gather: n/a — no external source; the capture subject is repo-internal at HEAD.
- Release: n/a — no version bump or publication surface touched.
- Issue closeout: n/a — #409 is a newly-FILED off-goal finding (creation), not the
  closeout of an existing tracked issue.
