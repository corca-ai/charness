# Session retro: prompt-mutation-pilot goal
Date: 2026-07-09

## Mode

session

## Context

The operator asked for creative autonomous-improvement directions, challenged
the prompt-mutation idea on false negatives and A+B interaction effects,
approved the resulting design (UNTESTED vs NO-OBSERVED-EFFECT, demote-never-
delete, ship-configuration rerun, batch ratchet), and delegated full design
and execution. The achieve goal
(charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md) ran end to
end: S1 mutant generator, S2 witness coverage + refresh witness map, S3 live
8-capture pilot, S4 report + policy doc, plus a closeout honesty pass.

## Evidence Summary

- Report: charness-artifacts/prompt-mutation/2026-07-09-handoff-refresh-pilot.md
  (verdicts bootstrap DETECTED 0/2; workflow and closeout-vocabulary
  NO-OBSERVED-EFFECT 2/2; 30-unit UNTESTED debt; one ranked demotion
  candidate, not applied).
- Policy: docs/prompt-mutation-policy.md.
- Three fresh-eye critiques with folded fixes: plan critique (F1
  plugin-mirror blocker — mutants would have silently tested the unmutated
  skill), S1+S2 bundle critique (baseline blueprint contamination — pinned
  to pre-S1 f84eb223; missing scorer; identity channels), final closeout
  critique (report over-claim from deleted stream evidence; mutant-diff
  unblinding disclosure).
- Issues filed: #426 (commit-diff unblinding; symmetric parentless
  snapshots), #427 (scorer stream fallback matches mentions).
- Budget: 8/12 captures, 0 failures, ~52 min matrix wall-clock.

## Waste

- The report's first draft claimed a causal story ("planner ran in mutant
  run 0") from stream-sourced evidence, and the streams were deleted before
  the report's claims were re-verified against the committed bundles; the
  closeout reviewer caught the contradiction and one honesty-pass commit
  repaired it. Deleting scoring inputs before re-scoring the committed state
  is the reusable trap.
- Blinding was designed three times (neutral commit message → digest-only
  refs + baseline dates → still diff-readable via `git show` on the snapshot
  commit). One exhaustive "what can the captured agent observe?" enumeration
  at S1 design time would have caught the diffable-parent channel that 4/6
  mutant runs actually used.
- The scorer's stream fallback matched a prose mention as a marker fire
  (#427); the fixture tests covered truncation but not mention-vs-execution.

## Critical Decisions

- Demote-never-delete with the UNTESTED debt list as the primary product —
  this framing survived contact with the data (the debt list, not the single
  demotion candidate, is the larger deliverable).
- Baseline pinned to pre-S1 f84eb223 after the bundle critique showed HEAD
  carries the experiment's own blueprint into every captured worktree.
- workflow NOT proposed for demotion despite 2/2 survival: under-witnessed
  broad owner with observational behavior-change signals; filed as coverage
  debt instead. NO-OBSERVED-EFFECT on a broad unit reads as
  "under-witnessed", not "dead".
- Stream-only marker fire withdrawn rather than defended once the committed
  trace-digest contradicted it.

## Expert Counterfactuals

- A red-team-the-observer lens applied once at S1 design ("enumerate every
  channel the captured agent can read: cwd, env, git log, git diff, refs,
  reflog, sibling files") would have replaced three incremental blinding
  iterations with one design pass — the diff channel was derivable from
  "handoff runs do git ops" which was already known.
- A "chain of custody" evidence rule (no claim survives its evidence's
  deletion without a re-verification) would have made the honesty pass
  unnecessary; that rule is now in the policy doc.

## Sibling Search

- Mention-vs-execution substring matching is a class defect: any grep-based
  scorer over transcripts (trace markers here, waste smells, future tripwire
  probes) can count prose that talks about a command as the command. #427 is
  the instance; the class is worth checking when the next transcript scorer
  is written.
- Evidence-deleted-after-scoring is a class trap for every capture pipeline
  that prunes large artifacts (efficiency A/B bundles already drop worktrees
  and configs): the policy rule (re-score committed state before relying on
  it) generalizes beyond prompt mutation.

## Next Improvements

- applied: docs/prompt-mutation-policy.md stream-drop re-score rule and
  commit-diff blinding caveat (commit 5ce78e9d).
- issue #426 (novel: mutant snapshot commits are diffable against their
  baseline parent; symmetric parentless snapshots for all arms).
- issue #427 (novel: constrain scorer stream fallback to command-bearing
  events; add mention-only negative fixture).
- none further — the 30-unit UNTESTED debt list is recorded in the pilot
  report as the input for future witness-authoring work, owned by the
  report artifact rather than a new tracked issue now.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-09-session-retro-prompt-mutation-pilot-goal.md

- Goal: charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md
- Host log probe: charness-artifacts/goals/2026-07-09-prompt-mutation-pilot-host-log-probe.json
