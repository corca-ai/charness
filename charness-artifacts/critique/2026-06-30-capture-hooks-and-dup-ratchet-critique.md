# Critique — capture-skill-run hook neutralization + dup-ratchet resolution

## Execution

Bounded fresh-eye subagent review (1 reviewer, adversarial gaming-audit), parent-delegated.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

n/a (no adapter sections re-rendered for this follow-up slice)

## Target

references/code-critique.md (two follow-up fixes from the quality-capture finding).

## Change

1. `scripts/agent-runtime/capture-skill-run.sh`: neutralize the captured
   subprocess's `core.hooksPath` to an EMPTY dir (was the worktree's `.githooks`),
   so a captured skill stops burning turns fighting charness's dev hooks; more
   faithful (a real plugin user runs none of charness's maintainer hooks).
2. dup-ratchet gate (was hard-block, 17 code + 2 doc new families) → GREEN via ONE
   extraction (`eventContent` helper in `build-skill-execution-observation.mjs`,
   removing the `ddae` internal message/content-unwrap dup) + 19 `intentional`
   classifications in `charness-artifacts/quality/dup-review.json`; baseline file
   untouched (no silent re-baseline).

## Capability at Stake

Capture-harness fidelity, and the integrity of the dup-ratchet gate — the risk is
mass-classifying real extractable debt as "intentional" to force the gate green
(gaming), or neutralizing hooks in a way that hides a signal the capture needs.

## Angles

Single bounded reviewer covering: hook-change safety/fidelity; dup classification
honesty (adversarial spot-check of the biggest families against real member spans);
`eventContent` behavior-neutrality + whether the extraction created new debt.

## Findings

- Hook change SOUND: the original derail (inheriting the main clone's absolute
  hooksPath) is still avoided (empty dir also overrides via process-scoped
  GIT_CONFIG_*); no main-repo config pollution; `.githooks` stay readable; more
  faithful. One stale header comment (now fixed).
- dup classifications HONEST, not gaming: reviewer spot-checked `aed52` (two
  standalone .mjs CLI parsers — only 12/66 lines shared), `fae23`/`1029` (planner
  call-site + adapter marshaling; shared logic already in run_plan_envelope.py per
  the locked item-2 spec), `322d067a` (the `## Bootstrap` phrasing whose uniformity
  IS the planner-uniformity north star), `94430` (trivial guard idioms),
  `735b` (hand-spelled test fixtures). None should have been extracted instead.
- `eventContent` extraction is behavior-neutral (52/52 tests) and REDUCED
  duplication: it removed `ddae`; `b84a` is a pre-existing jsonl-parse clone
  re-fingerprinted by the helper landing in its span (not new debt) — classifying
  it intentional is honest.

## Structured Findings

- stale-header-comment | bin: bundle-anyway | evidence: strong | ref: scripts/agent-runtime/capture-skill-run.sh:13 | action: fix | note: file-header still said "pins core.hooksPath to the worktree's own .githooks"; reworded to the empty-dir neutralization (done this slice).

## Deliberately Not Doing

- Extract a shared argv-parser (`aed52`) or jsonl-parse util (`b84a`) across the two
  standalone agent-runtime .mjs tools — rejected: they are independently executable
  by design and share only schema constants; a util module couples them for a small
  stdlib-shaped loop. Classified intentional, revisit if a 3rd consumer appears.
- Extract the per-planner envelope call-site marshaling into run_plan_envelope.py —
  rejected: skill-local portability is the locked item-2 design; the shared builders
  already live in the envelope lib.

## Next Move

Commit both fixes with the synced plugin mirror and the dup-review classifications.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority (per .agents/critique-adapter.yaml)
- Host exposure state: host-defaulted
- Application state: requested high-leverage fields are not available in this host runtime; spawned a host-default general-purpose subagent (Claude) for the bounded adversarial review.
