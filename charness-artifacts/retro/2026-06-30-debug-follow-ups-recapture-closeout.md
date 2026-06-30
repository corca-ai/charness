# Session Retro — debug follow-ups (outcome-assertion set + planner resolved-state guard + live re-capture)

Mode: session

## Context

Achieve goal closeout for
`charness-artifacts/goals/2026-06-30-issue-2-debug-follow-ups-start-here-sharpens-2.md`.
Three legs landed: (a) a substance-keyed debug outcome-assertion set, (c) a
targeted resolved-state planner guard for the `continue-existing-artifact`
mis-fire, (d) an operator-gated live re-capture + judge grade. Commits
c41222f9, 9981d7a2, a3639f11.

## Evidence Summary

Live capture bundle
`charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30-recapture/`
(observed.v1.json, cautilus-report.json, outcome-grade.md, finding.md); the
debug pytest suite; the fresh-eye Slice 2 critique; the host-log probe (claude
session detected — token/duration/tool-call derivable, not fabricated).

## Waste

- **Mis-framed the fix as the cause before proving it.** The plan assumed the
  `continue-existing-artifact` mis-fire CAUSED the floor doc-skip. The live
  re-capture proved otherwise: the fix changed behavior (fresh artifact +
  `Resolution: resolved`) but the run STILL skipped five-steps/debug-memory — the
  mis-fire was only an aggravating factor. The framing was corrected by RUNNING the
  capture, not by reasoning. Cost: low (the plan still landed real value), but the
  "PASS attempt" expectation was set higher than the evidence supported.
- **Trusted a judge FAIL before checking what the judge saw.** The first outcome
  grade FAILed detection-gap + sibling-search; the evidence line said "Output
  truncated at '## Correct Behavior'." The grader excerpted each output at only 500
  chars, so the judge graded substance blind. ~1 extra judge spend to re-grade
  after fixing the window. Caught only because the judge cited its own truncation.
- **Background launch denied → one wasted round-trip.** I stacked the tool's
  `run_in_background` with shell `nohup … &` AND a compound `rm -rf` one-liner —
  three permission triggers at once. The clean single command via the tool's native
  `run_in_background` was accepted.

## Critical Decisions

- **`missing → open` for the resolved-state guard** (vs `missing → resolved`).
  Smallest behavior change: legacy/in-progress fieldless artifacts keep continuing
  (existing test + resume safety preserved); only explicit `Resolution: resolved`
  flips. The live #365 case was fixed by a one-line migration instead of a global
  default flip. This honored the operator's "targeted/minimal" choice.
- **Did NOT soften the floor despite the re-capture miss.** A floor miss is a
  skill-shape signal; the substance set — not the floor — is the right
  discrimination. The set proved it (3 substance PASS + 1 real discipline FAIL).

## Expert Counterfactuals

- **Deming / measurement-system lens:** "trust the measurement only after you've
  validated the measurement system." Checking the judge's actual evidence window
  BEFORE accepting its FAIL would have caught the 500-char truncation on the first
  pass, saving the re-grade. → folded into Next Improvements (verify the grader's
  evidence window covers the claim target).
- **Popper / falsificationist lens:** the run's `falsifiable-hypothesis` FAIL is
  textbook confirmation-bias debugging — it reached the answer by static reads
  without attempting a cheap disconfirmer. The substance assertion caught exactly
  what Popper warns about, which is strong evidence the set measures the right thing.

## Next Improvements

- **workflow:** when an LLM judge returns FAIL, verify the judge's evidence window
  actually contains the claim's target before trusting it (the truncation
  false-negative). APPLIED partially via the excerpt-window fix.
- **capability (APPLIED):** `grade_skill_outcome.py _output_excerpts` per_file
  500→8000 (+40KB total budget) so substance sections (bottom-anchored) are visible
  to the judge. Committed a3639f11 (mirror synced).
- **capability / follow-up (tracked-candidate):** the floor doc-skip — a competent
  run reaches the structural outcome via the scaffold STRUCTURE without opening the
  canonical reference docs — is a debug skill-shape question (are the reference docs
  over-built given the scaffold supplies the structure?). NOT a floor softening; a
  candidate issue for the next correctness-sweep session.
- **memory:** recent-lessons should carry: (1) a "fixable" mis-fire can be only an
  aggravating factor — prove behavior-change SEPARATELY from symptom-fix; (2) verify
  a grader/judge's evidence window before trusting a FAIL.

## Sibling Search

Transferable waste pattern: **an evidence-excerpt window too small to contain the
load-bearing content it grades.** Four-axis scan of the grading/review path:

- same-layer (grade_skill_outcome judge_context): transcript truncated at 8000,
  trace at 80 calls — bounded but those are heads of append-style logs where recent
  content matters less than an artifact's bottom-anchored conclusions; decision:
  no-action (different risk profile; the artifact-substance case was the real gap).
- abstraction-up (build-skill-execution-observation excerpting): reads the session
  tree, not artifact substance for grading; decision: no-action.
- mental-model sibling (any reviewer/judge fed a fixed-size head of a structured
  doc whose verdict-bearing sections are at the end): decision: follow-up —
  `follow-up: audit fixed-size doc excerpts feeding LLM judges/reviewers for
  bottom-anchored-section truncation` (low priority; only grade_skill_outcome was
  confirmed affected this session).

## Persisted

Persisted: yes: charness-artifacts/retro/2026-06-30-debug-follow-ups-recapture-closeout.md
