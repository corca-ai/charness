# Session Retro

Date: 2026-08-09

## Context

The `make-proof-surfaces-report-what-they-observed` goal, all eight slices, ending
in the `v4.0.0` release and push. The premise: a proof surface should say what it
observed and stay silent about what it did not. Four surfaces broke that in two
directions — one observed nothing and reported clean, three reported verdicts
they never observed.

## Evidence Summary

- Deleted `--invocation-text` and `should_fire_chunker`; routing is declared.
- `docs/README.md` links all 40 pages: `orphans=0 islands=0 ratio=1.0000` at 42
  documents, negative test observed red first.
- New `docs-graph` lane with PASS / FAIL / UNPROVEN all observed through the real
  runner, not just the script.
- Routing floor corpus replay over 185 goals: 156 quality + 47 debug triggers
  dropped, ZERO gained, `impl`/`issue` unchanged.
- Attention-state gate: 31 prose-only declarations retired, 2 REAL states caught
  that a substring scan could not see.
- Pre-push battery green by its own strength before publish: `87 passed, 0 failed`
  under `CHARNESS_PRE_PUSH=1`.
- Remote CI `success` on the pushed SHA, read from GitHub's API through two
  surfaces.

## Waste

- **Building on a stated premise before checking it, twice.** Slice 2's plan said
  linking the orphans makes awiki exit 0; it does not, because link-only lines
  also fail it. Slice 4's plan said to tighten the doctor policies; measuring
  showed that makes any machine without awiki a blocking failure. Both were caught
  by checking, but only after the slice was shaped around them.
- **Inventing fixtures instead of capturing them.** Twice: the passing awiki
  summary and the `// island=1` block header were both my belief written as a
  test. Both were right, and being right is not the point — a bounded reviewer had
  to catch each one, and one of them hid a live fail-open (a clean `ok` line omits
  the counts entirely, so a healthy repo would have reported UNPROVEN forever).
- **Hand-bumping the version.** The publish helper owns bump + pointer + tag +
  push together; the hand bump was refused at commit and had to be reverted.

## Critical Decisions

- **Fix the push gate rather than bypass it.** `--no-verify` was available and
  would have revoked the grant. The blocking set turned out to be 11 refusal
  branches plus one module with no standing test — bounded, and covering it made
  the push legitimate instead of merely permitted.
- **Override the plan on measured evidence.** Slice 4's "tighten the advisory
  policies" step was not done, because measurement showed it would break ordinary
  machines while adding no safety the consumption point does not already provide.
- **Take the operator's amendment rather than force the original criterion.** Exit
  0 was unreachable without a docs-wide reflow the goal forbade; the gate asks the
  connectivity question and says out loud what it does not judge.

## North Star Alignment

P3 named this goal before it existed: an enumerated list *"rots and still misses
the case it never listed."* Three of the four surfaces were exactly that, and the
measurement made it concrete — the quality keyword guess fired on 157 of 185
goals, mostly on the word "gate".

P5 held where it mattered: the routing floor now FORCES a question (`Phases:`) and
refuses to declare the answer. The counter-warning — *"what this does not license
is a gate that checks gates"* — was respected; no slice added a gate on top of a
gate, and the one new gate replaced no existing verdict.

The failure signature the run walked into is the one the boundary section warns
about: authoring a proof surface is irreversible because a fail-open is silent by
construction. I shipped a fail-open (no `documents` floor) and a silent-naming bug
(the orphan block parser) into surfaces I had just written about reporting
honestly. Both were caught by delegated review, which is the safeguard working —
and is why the second round exists.

## Expert Counterfactuals

- **A tester's lens (capture, never assert from memory) would have changed the
  next move twice.** Both invented fixtures would have been captures from the
  start, and the `ok`-line fail-open would have surfaced in slice 4 rather than in
  its review round.
- **A release engineer's lens would have run the pre-push simulation FIRST.** The
  push refusal was fully determined by files in the tree and could have been known
  before slice 8 began, instead of being discovered by the release critique.

## Sibling Search

- axis: invented-instead-of-captured test fixtures | location: tests asserting external tool output shapes | decision: valid follow-up outside the slice | proof: two caught this run (`awiki` passing summary, `// island=1` header), both by bounded review rather than by a gate | follow-up: deferred handoff-anchor `capture-external-tool-fixtures`

## Next Improvements

- workflow: run the pre-push simulation (`CHARNESS_PRE_PUSH=1 run-quality.sh --read-only`) at the START of a release slice, not after the publish helper refuses.
- capability: a check that flags a test asserting an external tool's output shape from a hand-written string when no captured fixture for that tool exists.
- memory: the premise-check rule already exists and fired correctly twice; what is new is that BOTH failures were in plan text written by a previous session, so the rule belongs at slice-shaping time, not only at remedy time.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-09-make-proof-surfaces-report-what-they-observed.md
