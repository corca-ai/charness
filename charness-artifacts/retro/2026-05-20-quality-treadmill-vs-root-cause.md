# Session Retro
Date: 2026-05-20

## Mode

session

## Context

Reviewing the 2026-05-20 quality session that landed depth-bounded
`_pytest_temp_footprint`, `release_only` routing, `## References` link
inventory, and the seed-fixture budget gate. The user explicitly asked why I
needed to be prompted to find (a) the `release_only` marker that was already
documented in `pyproject.toml:3-4`, (b) the xdist × session-scope fan-out
diagnostic with real measurements, and (c) the "do these tests still need to
exist" audit. They later landed the seed cache and orphan teardown in a
separate session as commit `8742673`. This retro is bounded to that miss
pattern, not the whole session.

## Waste

- **Quoted "~1.4 GiB per seed" from a mental model, not measurement.** Real
  per-seed is 26-54 MB; the cost is fan-out, not seed size. Multiple commits
  carried imprecise numbers before the user pushed (`왜 아직도 seed
  materialization이 필요한가?`) and I ran `du`. The diagnostic landed in
  commit `2c6f873` only after that push.
- **Added `check-seed-fixture-budget` before asking root-cause questions.**
  First instinct was to bound the 9.78 GiB advisory finding. The structural
  fix (`release_only` routing) was already declared in `pyproject.toml:3-4`
  and saved 70% pytest time once routed; it was waiting to be honored, not
  invented.
- **Treadmill bias in `Recommended Next Gates`.** Quality skill ended each
  turn with "add more gates" (budget gate, references link inventory,
  advisory-only scope classifiers, attention-state declarations). I produced
  three new gates before the user prompted me to look for an existing
  convention being violated. The 2026-05-17 empty-policy lesson warns about
  invisible advisory state but I did not extend it to "advisory cost."
- **Audit only happened on user push.** "그 테스트들이 뭘 하는 거죠? 예전에는
  가치있었지만 이제 필요없을 것 같은." This was the right first question for
  any expensive test fixture; I should have asked it myself before
  recommending a fixture refactor.

## Critical Decisions

- ✓ Cleaning agent-browser orphans via the runtime guard's prescribed
  remediation — correct path, user-approved.
- ✓ Routing `release_only` out of standing pytest via `--release` flag —
  correct structural fix, but only reached after explicit user push.
- ⚠ Adding `check-seed-fixture-budget` first — correct as a regression
  guard but not as the headline move. Should have been "after the
  root-cause fix."
- ⚠ Adding `scope_classification=advisory_only_*` for unconfigured
  inventories — useful but framed as a new gate rather than as a question
  about whether quality should ever recommend empty-scope inventories as
  `Healthy`.

## Expert Counterfactuals

- **Gary Klein (pre-mortem)**: before recommending the budget gate, ask
  "what if the cost is intentional and already marked?" A 60-second
  pre-mortem on each `Recommended Next Gates` candidate would have pointed
  at `grep -rn release_only` and `git log -S 'release_only'`. Both produce
  the answer in one command. Changed action: pre-mortem each next-gate
  candidate against "existing convention?" before drafting it.
- **A profiler-minded engineer (e.g., Brendan Gregg)**: measure where the
  cost lives before fencing it. `du -sh pytest-of-*/popen-gw0/*` is one
  command; per-seed is then obviously small and fan-out is the cost. That
  framing changes the next move from "budget gate" to "share materialization
  across workers." Changed action: measurement is the first step of any
  cost-architecture proposal, not a follow-up.

## Next Improvements

### workflow

- **Measurement-before-claim rule.** When the quality skill (or any skill)
  writes a number for a size, runtime, or cost, the number must come from a
  command run this turn. Estimates must be labeled "estimate" with the
  reason measurement was skipped.
- **Anti-need before need in `Recommended Next Gates`.** Before proposing a
  new enforcement gate for an advisory cost, the workflow must check (a)
  `git log -S <subject>` for origin context, (b) `grep -rn <subject>` for
  existing markers and conventions, (c) `rg -tpython "<subject>"
  pyproject.toml` for existing routing. Add a new gate only after confirming
  no existing convention is being violated; otherwise the recommendation is
  a routing fix.

### capability

- **Quality skill `Recommended Next Gates` proposal flow.** Extend
  `skills/public/quality/references/proposal-flow.md` to require a one-line
  "existing convention check" beside each recommendation, with the format
  "no existing marker/comment/policy already governs this cost; gate is
  additive, not duplicative." If a marker exists, the recommendation must
  be the routing fix instead.

### memory

- Promote into `recent-lessons.md` (via summary refresh):
  - "Measure before quoting a size/runtime number; estimates must be
    labeled and justified."
  - "Before adding an enforcement gate for an advisory cost, grep for
    existing markers, policies, and `git log -S` for prior owner intent.
    A routing fix is often higher ROI than a new gate."
  - "Quality `Recommended Next Gates` has a treadmill bias toward additive
    enforcement; explicitly ask whether an existing convention is being
    violated before adding."

## Persisted

yes — written via `persist_retro_artifact.py` to
`charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`
with `recent-lessons.md` summary refreshed.
