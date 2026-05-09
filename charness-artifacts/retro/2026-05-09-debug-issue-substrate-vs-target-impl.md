# Debug ↔ Issue Substrate-vs-Target Impl Slice — Session Retro

## Mode

`session`. Closeout for the First Implementation Slice of
`charness-artifacts/spec/debug-issue-substrate-vs-target.md` (commit
`424504e`).

## Context

debug ↔ issue substrate-vs-target First Implementation Slice landed (commit
`424504e`): RCA substrate now owned by `skills/public/debug/references/five-whys-causal-chain.md`,
`issue/references/causal-review.md` Lens 1 compressed to dispatch paragraph,
`issue/SKILL.md` step 4 + close-comment `Debug artifact: <path>` slot wired,
`debug` marked standalone-callable, 9 grep-based anchor citation chain
assertions land. Spec contract land happened in the previous session
(commit `21c348d`); this session executed the spec's 7-step atomic plan in a
single commit and folded 4-subagent code-critique findings (Jackson +
Weinberg + Gawande + counterweight) before commit.

## Evidence Summary

- spec contract: `charness-artifacts/spec/debug-issue-substrate-vs-target.md`
- impl commit: `424504e` (9 files / +270 / -96)
- validators clean: `validate_skills`, `check_doc_links`,
  `validate_public_skill_dogfood`, `check_skill_contracts`, `check-markdown`,
  `markdownlint-cli2`
- quality_gates: 525 passed / 4 skipped
- cautilus eval test: 5/5 passed (recommendation `accept-now`,
  `.cautilus/runs/20260509T140802050Z-run/eval-summary.json`)
- 4 critique subagents returned `parent-delegated`; Act-Before-Ship +
  Bundle-Anyway findings folded into the same commit before push gate

## Waste

- **Bootstrap line-wrap broke a contractual literal phrase**. First pass
  rewrapped "It must not use the current session's last created issue" across
  a newline; `test_issue_skill_records_github_sot_for_omitted_selector` and
  `check_skill_contracts.py` both use literal substring assertions, so the
  broken wrap surfaced as a fail, not a silent drift. Fixed by restructuring
  the bootstrap merge so both contractual phrases ("With no selector,
  `select` queries the newest open GitHub issue", "It must not use the
  current session's last created issue") stay continuous within a single
  line. ~2 retry cycles.
- **MD004 list-style snag on a wrapped Output Shape bullet**. Lines starting
  with `  + ` (two-space indent + plus + space) made markdownlint think
  `+ \`Over-reach check\`` opened a `+`-style sublist. Rewrapped so `+`
  lands mid-line, not at the start of a continuation line. ~1 retry.
- **Ruff I001 phantom error**. First pre-commit run flagged the test file's
  import block as unsorted; `ruff check --fix` reported "1 fixed" without
  changing the file content. Adding/removing the noqa cleared cache; net
  zero file-content delta but ~1 cycle lost. Likely ruff cache/symbol
  state, not a real defect.

## Critical Decisions

- **Atomic single-commit policy held**. Spec required mutate (reference
  file new + Lens 1 body removed) to land in *one* commit so the substrate
  is never duplicated and never absent. The 7-step plan was executed as a
  single staged diff with no intermediate test-fail window.
- **Critique findings folded *before* commit, not as follow-up**. Jackson
  flagged the spawned subagent prompt contract was missing the substrate
  cite requirement (silent overlap could re-grow). Weinberg flagged the
  Output Shape "chain with citations" wording still pulled the reviewer
  back into chain re-derivation. Both Act-Before-Ship items were folded in
  the same commit (`causal-review.md` "Causal review subagent contract"
  bullet + Output Shape Root cause line rewrite + new Debug artifact field
  in Output Shape). Gawande's "Debug artifact slot has no fallback wording
  for trivial-bug" was also Act-Before-Ship; folded as `(or none (trivial
  fix) / cite-only)` inline. Counterweight independently surfaced the same
  two Bundle-Anyway candidates ("For bug" close-comment shape mirror +
  Output Shape consistency), which validated the angle pass.
- **Lens 1 line-budget gate added as the 9th anchor assertion**. Weinberg's
  diagnostic concern was that the negative-grep regex (forbidden phrases)
  is paraphrase-bypass-able. Adding a `≤15 lines` assertion on the Lens 1
  body between `### Lens 1` and `### Lens 2` is a structural gate, not a
  phrase gate — drift that re-bodies RCA into Lens 1 fails on length even
  if no forbidden phrase is re-pasted.
- **Cautilus eval test run for prompt-affecting public-skill change**.
  Adapter is `ask` mode (eval-only per corca-ai/cautilus#32) so
  deterministic gates own closeout, but the routing fixture is the closest
  evaluator-backed regression check available. 5/5 passed confirms no
  routing drift on `debug` / `issue` / `causal-review.md` body changes.

## Dogfood Evidence

The new close-comment shape rendered against an actual incident from this
session — the bootstrap line-wrap fail. Synthetic close-comment rendered
following the new `bug` bullet structure:

```
- `bug`:
  - JTBD: maintainer wants the `issue resolve` bootstrap docs to keep two
    contractual phrases ("With no selector, `select` queries the newest
    open GitHub issue", "It must not use the current session's last
    created issue") literal-grep-able from
    `test_issue_skill.py:579` and `check_skill_contracts.py`.
  - root cause (one line): bootstrap rewrite split the two contractual
    phrases across newlines, breaking Python `str in str` checks even
    though the words were semantically preserved.
  - `Debug artifact: cite-only` (chat-only diagnosis; no
    `charness-artifacts/debug/` artifact written for a 1-cycle fix).
  - siblings (bundled/deferred+location): same trap class as
    recent-lessons.md `MAX_SKILL_MD_LINES=200` repeat trap (compress
    *before* additions); none deferred this slice.
  - prevention: contractual literal-phrase tests are the existing gate;
    Lens 1 line-budget assertion (added in this slice) generalizes the
    structural-gate pattern. No new gate added for line-wrap of literal
    phrases — single occurrence so far, capability change deferred per
    recent-lessons heuristic ("한 번 패턴이라 capability 변경은 미루고
    다음 회 같은 트랩이 반복되면 그때 짓는다").
```

Confirms: `Debug artifact:` slot lands directly below the root cause line
within the `bug` bullet structure as the spec's Fixed Decision required;
the `cite-only` fallback wording from the impl-slice critique fold is
operator-consumable for the trivial-bug short-circuit case.

## Expert Counterfactuals

- **Weinberg lens, applied retroactively**. Without the impl-slice
  critique pass, the Output Shape "Root cause (chain with citations)"
  surface would have shipped as-is. The Lens 1 body was removed but the
  *contract surface that drives the spawned subagent prompt* still asked
  for chain output — silent overlap could regrow as soon as a subagent
  prompt was instantiated from the unchanged Output Shape. Counterfactual
  changed action: catch contract-driving surfaces (Output Shape,
  subagent prompt requirements) as cite targets when the lens-body is
  compressed, not just the lens-body itself. Folded into the impl
  commit; no separate slice needed.
- **Klein pre-mortem lens for the Debug artifact slot fallback**. Without
  Gawande's pass, the `Debug artifact: <path>` slot would have shipped as
  a hard sub-bullet with no wording for the trivial-bug short-circuit
  path (which skips step 4 entirely, so no debug artifact exists).
  Operator under load would either (a) skip the slot silently, (b) write
  unconventional fallbacks ("`Debug artifact: chat memory only`",
  "`Debug artifact: n/a`") that the grep test passes literally but that
  drift across operators. Adding `(or none (trivial fix) / cite-only)`
  to the slot wording standardizes the fallback. Counterfactual changed
  action: when expanding a single-line bullet into a multi-line shape,
  enumerate explicit fallbacks for short-circuit branches in the same
  edit.

## Next Improvements

- **memory**: spec-critique 4-bin triage Act-Before-Ship items applied at
  *contract-driving surfaces* (Output Shape, subagent prompt contract,
  validator gates), not only at the lens body, when the slice compresses
  a lens. surface in recent-lessons.
- **memory**: when expanding a single-line bullet to a multi-line shape
  in close-comment / output-shape contracts, name explicit fallbacks for
  short-circuit branches inline (here: trivial-bug → `cite-only` /
  `none (trivial fix)`). Apply to next contract that introduces
  multi-line shape.
- **workflow**: contractual literal-phrase tests in `test_issue_skill.py`
  + `check_skill_contracts.py` already catch line-wrap drift; no new
  gate needed (this is the *intended* surface). Confirmed by this
  session's repro. No capability change.
- **capability** (deferred, single occurrence): markdownlint MD004 trap
  on wrapped continuation lines beginning with `  + ` (literal text). If
  this trap repeats, a pre-commit hint that names continuation-line
  bullet-style ambiguity would cut the cycle. One occurrence — defer
  per recent-lessons "한 번 패턴" heuristic.
- **memory** (active deferred follow-up — close): the
  Compact-AGENTS.md routing discriminator follow-up surfaced in the
  v0.5.20 cautilus refresh batch is *not* triggered by this slice
  (cautilus eval 5/5 pass). Stays as the next-after-this slice when a
  natural surface change arrives.
- **memory** (next slice candidate): P4 sequencing decision (debug-call
  as `prior_context` vs cite-only consume) needs first dogfood retro
  observation from a *real* bug-class issue resolved through the new
  contract. Today's synthetic dogfood confirmed the close-comment shape
  but not the (a)/(b) sequencing question. Defer until first real
  bug-class `issue resolve` lands.

## Persisted

`Persisted: yes charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-impl.md`
