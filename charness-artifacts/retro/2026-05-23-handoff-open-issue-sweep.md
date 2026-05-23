# Session Retro: Handoff Open-Issue Sweep
Date: 2026-05-23
Mode: session

## Context

Closed the handoff's self-fixable open issues (#198, #202-#206) and RCA'd
#207 (by-design) through the design→impl→pattern-scan→RCA→final-critique loop
with five bounded fresh-eye subagent passes. All fixes landed in one commit
(`858da76`) and pushed; #207 closed by-design with the RCA comment.

## Waste

- The commit subject `Fixes #198 #202 #203 #204 #205 #206` auto-closed only
  **#198**. GitHub applies a closing keyword to the FIRST issue number only; a
  list of bare numbers after one keyword are mentions, not closing references.
  The result was 6 unpushed-then-pushed fixes that all stayed OPEN until a
  manual `gh issue close` sweep. The prior session's `a689024`
  (`Fixes #199 #200 #201`) had the same defect — #199 closed, #200/#201 did
  not — so this already recurred once and was not caught.
- The recent-lessons digest already carries the parent trap ("`Add #NNN` does
  not auto-close; use a closing keyword"), but it does not say the keyword must
  be repeated **per issue number**. The refinement is what bit twice.

## Critical Decisions

- Closed #200/#201/#202-#206 manually with commit-ref comments rather than
  amending pushed commit messages (rewriting pushed history is worse than a
  one-time manual close).
- Kept #207 a by-design close, not a code change: a no-mutable-line allowlist
  would weaken the just-hardened fail-closed scope-gap signal. Recorded the
  allowlist as a deferred design decision instead of auto-applying it.

## Expert Counterfactuals

- Jef Raskin lens: the `issue` skill already shows the correct, discoverable
  form — `Close #1. Close #2.` (keyword per issue) in its closeout discipline.
  The waste was deviating from the surface that already teaches the right move
  in an ad hoc commit; following the skill's own example would have prevented
  both occurrences.
- Daniel Kahneman lens: anchoring on "I used a closing keyword, so it will
  auto-close" skipped the verification step. Checking issue state immediately
  after push (cheap) surfaces the gap before it becomes a stale-OPEN cost.

## Next Improvements

- workflow: when one commit resolves multiple issues, repeat the closing
  keyword before EACH number (`Fixes #1, fixes #2, fixes #3`) or use the
  `issue` skill's `Close #1. Close #2.` form. A bare list after one keyword
  closes only the first.
- workflow: after any push that should auto-close issues, verify each issue's
  state (`gh issue view <n> --json state`) before declaring closeout done; the
  check is cheap and catches both this trap and the parent `Add #NNN` trap.
- memory: this refines the existing closing-keyword lesson rather than
  replacing it; the parent ("use a closing keyword at all") still holds.

## Sibling Search

- same layer: prior commit `a689024` `Fixes #199 #200 #201` | decision: same waste, fix now | proof: confirmed #200/#201 stayed OPEN until this session's manual close — same single-keyword defect, already closed out here
- abstraction up: skills/public/issue/SKILL.md:118-119 closeout discipline | decision: intentional boundary | proof: it already prescribes `Close #1. Close #2.` (keyword per issue) — the skill is correct; the deviation was an ad hoc non-skill commit
- specialization down: skills/public/release/ close-issue handling (`--close-issue <number>`) | decision: diagnostic-only | proof: release closes a single number per call, so the multi-issue list trap does not apply
- mental-model siblings: charness-artifacts/retro/recent-lessons.md parent trap (`Add #NNN` does not auto-close) | decision: same waste, fix now | proof: this session's Next Improvements refines that lesson with the per-issue-keyword rule, captured in this artifact

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-23-handoff-open-issue-sweep.md`
