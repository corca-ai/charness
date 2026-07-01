# achieve claim-fidelity capture — 2026-07-01 (reference-compaction Slice 7)

## Verdict

**RCF→RSF MOVE — #410's conditional criterion is MET.** The goal-shaping run
opened ZERO reference docs (coverage 0/3) but GENUINELY produced a goal artifact
and emitted its canonical path, so the floor moves from the re-read proxy
`requiredCommandFragments=[lifecycle.md, goal-artifact.md]` to the emitted-token
floor `requiredSummaryFragments=["charness-artifacts/goals"]`. This is the second
clean move of the sweep (after create-cli).

## What ran

`/charness:achieve` shaping a goal to add a consistent `--json` output mode to all
repo scripts via a shared helper + tests. Capture at `HEAD`=4fc6389c, exit 0,
236894ms, 1.96M tokens (Bash=13 Edit=6 Read=1). The run interviewed the intent and
wrote a well-formed goal artifact at
`charness-artifacts/goals/2026-07-01-repo-script-json-output-mode.md` — WITHOUT
opening any of its reference docs.

## Why the move is honest (#410 conditional MET)

#410 scoped achieve CONDITIONALLY: "goal-artifact.md/lifecycle.md RCF→RSF ONLY if a
capture confirms the shaping prompt forces a goal-artifact token; else KEEP in RCF
and record the finding." The capture confirms it BOTH ways:

- **doc-open floor refuted** — coverage 0/3, neither lifecycle.md nor
  goal-artifact.md opened (genuine reads = NONE across parent + subagents).
- **goal-artifact token forced** — the run emitted `charness-artifacts/goals` (the
  canonical goal-artifact path) in its closeout, because it produced the artifact
  there. The goal-artifact path + concept is inlined in achieve/SKILL.md (the
  description, the Bootstrap `ls charness-artifacts/goals/`, and the workflow
  steps), so the run shapes the goal from always-loaded core without opening the
  doc — the exact wasteful-re-read Move C relieves.

`charness-artifacts/goals` is achieve's central-claim path ("interview prose intent
into a reviewable goal artifact under charness-artifacts/goals/") and is NOT in the
prompt (which is about repo `--json` output), so a run emitting it demonstrably
produced a goal artifact — not a prompt echo.

## classTags + substance backstop (fresh-eye critique fix landed)

lifecycle.md + goal-artifact.md stay DECLARED with classTag DEPTH: the full
lifecycle/artifact CONTRACT is a depth read opened on-demand for a complex goal,
not every run.

The fresh-eye bounded critique (SHIP) flagged that, with the doc-open proxy retired
and no substance judge, the spec.json RSF (`charness-artifacts/goals`, a bare-dir
substring) was achieve's WHOLE floor and a run merely NAMING the goals dir could
pass. Fix landed THIS slice: added `evals/cautilus/achieve-claim-fidelity/outcome-assertions.json`
binding the token to a PRODUCED artifact — a deterministic `output_glob`
`**/goals/*.md` (did the run materialize a goal artifact, not just name the path) +
a judge assertion for honest slice/verification/non-claim substance. The output_glob
resolves against the bundle outputs/ dir; achieve capture-side output preservation is
a tracked follow-up (as for hitl), so it fails-closed until preservation is wired —
an honest known-pending floor, never a green. So achieve's floor is now RSF (form,
currently gradable) + output_glob (substance, pending preservation) + judge — no
longer a lone form token. `thresholds.max_duration_ms=475000` from the passing
baseline (236894ms, ~2x).
