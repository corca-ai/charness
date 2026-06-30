# Debug skill claim-fidelity capture — 2026-06-30

## Verdict

**MISS (cautilus `failed`), informative.** A real `/charness:debug` run
honored the TASK with an exemplary structural RCA but did not open its own
workflow floor references. The capture produced two skill-shape signals and one
floor re-pin. debug stays a HYPOTHESIS.

## What ran

`/charness:debug` (the spec's gitignore-scanner bug-class prompt) on `HEAD`=f827594c,
isolated worktree capture (`--timeout-sec 900`, hit the cap, exit 124). This also
exercised the new empty-hooks fix (confirmed active) and the fae23 debug-planner
change. Tools: Bash=31 Edit=21 Read=11 Write=3 Skill=1 (the 21 Edits were all to
the ONE debug artifact it authored — not code fixes). `cautilus evaluate
observation`: `failed` (1 failed, 0 passed). coverage 2/11.

## The run honored the TASK — and the structural-improvement intent

Not a matcher artifact: the floor refs appear in NO tool input (verified). The run
consulted the planner (1×), read the actual scanner code (`repo_file_listing.py`,
`inventory_gitignore_scan_hygiene.py`, the tests), opened the two topically-right
refs (`detection-gap.md` + `sibling-search.md` = coverage 2/11), and wrote a
high-quality artifact (`captured-debug-artifact.md`) with a complete **Detection
Gap** (4 named gate gaps + proofs, 0 vs 14 findings) and **Sibling Search** (named
the wrong mental model + four-axis scan finding ~15 sibling scanners with
per-sibling decisions + follow-ups). It reached the correct fix (git-aware
`iter_repo_files`). So the structural-improvement / compounding intent was met.

## Two skill-shape signals

1. **Floor mis-pin (RE-PINNED this slice):** `five-whys-causal-chain.md` is routed
   `on_demand` by the planner — one of THREE alternative causal lenses (five-whys /
   disconfirmer-first / invariant-first). The skill never claims it is universal,
   so the floor wrongly required it; this run proves a competent run reaches the
   structural outcome without it. Removed from the floor (now
   `[five-steps.md, debug-memory.md]`). This corrects a static hypothesis to the
   planner's real routing — NOT softening the matcher.
2. **Genuine fidelity miss (debug stays HYPOTHESIS):** the run skipped
   `five-steps.md` + `debug-memory.md`, which the planner emits as UNCONDITIONAL
   required reads. It followed the 5-step STRUCTURE anyway (the scaffold supplies
   it) but did not open the canonical sequence or prior-incident memory — the
   `debug-memory.md` skip is the notable one (lost cross-incident compounding).
   Aggravated by the planner mis-moding to `continue-existing-artifact` (a mature
   repo always has debug history), which buried the two required reads under 5
   stale prior-incident reads the run sensibly skipped.

## Disposition (operator-reviewed)

- five-whys re-pin: APPLIED.
- The structural-improvement INTENT is best protected by a debug OUTCOME ASSERTION
  on the Detection Gap / Sibling Search / Prevention sections (substance, not
  doc-opening — this run nailed the substance without the doc). DEFERRED to next
  session; doc-opening is a weak proxy for the intent.
- Open follow-ups (next session): (a) author the debug outcome-assertion set;
  (b) review whether the debug reference docs are over-built at the current level
  given the scaffold already supplies the structure; (c) the `continue-existing-
  artifact` mode mis-fires for fresh bugs — planner-shape candidate; (d) re-capture
  debug after (a)/(c) to attempt a PASS.
- n=1 caveat.
