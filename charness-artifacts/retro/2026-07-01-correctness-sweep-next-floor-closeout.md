# Retro — correctness sweep: impl claim-fidelity capture (closeout)

Mode: session

## Context

Autonomous `achieve` run of `charness-artifacts/goals/2026-07-01-correctness-sweep-next-floor.md`
— the 5th skill in the correctness sweep (after retro, hitl, quality, debug).
Picked `impl` via handoff chunked-routing, shaped+activated the goal with a
fresh-eye plan critique, ran one live cautilus capture of `/charness:impl`, scored
the floor + substance, and filed the harness gaps it surfaced. What matters next:
the operator's skill-shape decision on `impl`'s closeout vocabulary, and the harness
fixes in #409 that unblock the rest of the sweep.

## Evidence Summary

- Capture bundle `charness-artifacts/cautilus/impl-claim-fidelity-2026-07-01/`
  (`observed.v1.json`, `cautilus-report.json` = 1 failed/0 passed, `outcome-grade.md`
  = 4/5, `finding.md`).
- The run's own metrics from the capture packet: exit 0 (natural completion),
  123821ms wall, 1.28M tokens, 17 tool calls. These are the captured SUBPROCESS's
  metrics, not a host-exposed log of THIS operating session.

## Waste

- **Real, but it was discovery, not avoidable waste:** ~3 recovery cycles diagnosing
  why `git status` was empty in the worktree (the run committed → HEAD moved) and why
  the tree transcript was short (final block unflushed). Phase-aware (per
  `references/phase-aware-efficiency.md`): this was investigation that SURFACED two
  genuine harness bugs (#409), not churn — the triage locked quickly once the commit
  and the stream/tree block-count divergence were seen.
- **Avoidable-in-hindsight:** the first goal draft omitted output preservation
  entirely. The fresh-eye plan critique caught it pre-capture, so the cost was paid in
  review, not in a blind grade — the critique earned its cost. The residual gap (a
  *committing* run defeats even a wired `preserve_outputs`) was NOT predictable from
  the plan alone; it needed the live run.
- The captured run's own duplicate reads (claim_fidelity_lib.py 2x, the registry test
  2x) are advisory smells about the SUBJECT run, not this session.

## Critical Decisions

- **Target = `impl`** (single methodologically-sound floor, concrete executable
  subject, sandbox-safe, no external surface) over riskier multi-floor / external /
  conversational skills. Vindicated: a clean, fast, faithful capture.
- **Did not soften the floor or any assertion** on a MISS + partial-substance result.
  The floor MISS (0/8) and the `honest-categorized-closeout` FAIL are recorded as a
  skill-shape signal, not engineered away. This is the sweep's core discipline.
- **Rebuilt the judge transcript from `stream.jsonl`** (authoritative, complete) once
  the tree was found truncated — so the substance grade read the real closeout, not a
  blind one.
- **Threshold left unset** (floor not passed; policy derives the budget from a PASSING
  capture). Recorded the 123821ms natural-completion baseline for a future PASS.

## Expert Counterfactuals

- **Measurement-instrument lens (Michael Feathers / "trust the harness before the
  verdict"):** a skeptic of the test *instrument* would dry-run the capture→grade
  EVIDENCE pipeline on a cheap or synthetic run first — assert `outputs/` is non-empty
  and the transcript contains the closeout — BEFORE spending an expensive live capture.
  That would have caught both #409 gaps up front instead of mid-grade. The plan
  critique caught the *shape* of gap #1 (no preservation step) but not that a
  committing run defeats even a correct `preserve_outputs`; only running the pipeline
  reveals that. Changed action: add a one-line evidence-pipeline preflight to the
  capture workflow.
- **Definition/semantics lens (Hillel Wayne / "is the vocabulary load-bearing?"):**
  the `honest-categorized-closeout` verdict turns entirely on canonical enum tokens vs
  a semantic equivalent. A spec-clarity skeptic would have forced the
  load-bearing-vs-house-style question up front, which is exactly the operator decision
  this capture surfaces — so the lens confirms the finding rather than changing the
  grade. The assertion stays defensibly strict (impl's Output Shape literally requires
  the `verification-ladder.md` Lint Gate vocabulary).

## Next Improvements

- **workflow:** before an expensive live capture, run a cheap evidence-pipeline
  preflight — confirm the bundle will get a non-empty `outputs/` and a closeout-bearing
  `transcript.txt` (especially for skills that commit or complete cleanly). Prevents a
  blind substance grade.
- **capability:** issue #409 — fix `preserve_outputs` to diff against the capture ref
  (not HEAD) and build the transcript from `stream.jsonl` (not the possibly-truncated
  tree).
- **memory:** recent-lessons digest gets two transferable lessons (below).
- **decision (operator):** `impl` skill-shape — internalize the Lint Gate /
  completion-report enum into `impl/SKILL.md` (debug-Plan-A-style, makes the floor a
  weak proxy and the substance pass) vs keep the floor load-bearing (the MISS is a real
  closeout-vocabulary gap). Candidate issue; recorded in the goal's Off-Goal Findings.

## Sibling Search

Transferable waste pattern: **outcome-grader evidence derived from a source a faithful
run can silently invalidate.** Four-axis scan for siblings:

- `preserve_outputs` / `_changed_files` (`run_skill_efficiency_ab.py:220-266`) — diffs
  vs HEAD; a committing run invalidates it. **CONFIRMED site → #409.**
- `_write_transcript` (`run_skill_efficiency_ab.py:269-289`) — reads the tree jsonl,
  which can miss the final assistant block. **CONFIRMED site → #409.**
- `build-skill-execution-observation.mjs` `finalAssistantText` (reads the tree for the
  SUMMARY used by `requiredSummaryFragments`) — same tree-truncation exposure. **Possible
  third sibling**; benign for impl (no required summary fragments) but a skill with
  summary-fragment floors could be bitten. **Follow-up:** noted in #409 as a related
  surface to check when fixing gap 2; not separately filed (same fix locus).
- Cautilus floor matcher (reads the command log) — NOT exposed: tool calls are complete
  in the tree even when the final text block is unflushed (verified: the 0/8 coverage is
  reliable). Decision: no action.

Destination split for #409 (`../../shared/references/retro-issue-destination-split.md`):
Structural pattern = "grader evidence derived from a run-invalidatable source";
Triggering instances = preserve-vs-HEAD on a committing impl run + tree transcript
missing the final closeout block; Destination = charness repo (the capture/grade
harness is repo-owned), one issue (#409) covering both confirmed sites.

## Next Improvements — disposition (mirrored into the goal Auto-Retro)

- workflow preflight → tracked in #409's "possible direction" (the preflight is the
  operator-facing complement of the harness fix); also a candidate to add to the
  capture workflow doc when #409 lands.
- harness fixes → issue #409.
- memory lessons → applied this run (recent-lessons digest refresh on persist).
- impl skill-shape → operator decision, candidate issue (Off-Goal Findings).

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-01-correctness-sweep-next-floor-closeout.md
