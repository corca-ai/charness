# retro H0 — anti-DOMINANT-churn exemplar + one micro-lever FIXED (2026-07-03)

Serves [intent.md](./intent.md): north = SMARTER agent; test = "그게 정말 최선인가?"
Fourth H0 (churn-class hunt). Verdict (fresh-eye SOUND-WITH-DEFECTS, incorporated):
**no *dominant* churn lever — retro already ships every anti-churn property the
debug/quality fixes ADD** (it is the reference implementation they converge
toward) — **plus one small residual `Persisted`-stamp micro-lever, now FIXED.**
Scope: `session` mode (weekly mode adds telemetry mining, a heavier unmeasured
profile — substantive work, not churn).

## Capture (fresh, current HEAD)

Real `/charness:retro` via the ungated harness, fixture prompt, **outcome passed**
(RCF `expert-lens.md` met). The leanest, cleanest capture of any skill:

| skill | output | tools | wall | verdict |
|---|---|---|---|---|
| quality | 168k | 103 | 19.5m | churn FIXED |
| debug | 175k | 108 | 18.1m | churn FIXED+PROVEN |
| spec | 88k | 39 | 11.2m | no lever (refs load-bearing) |
| **retro** | **20k** | **24** | **5.7m** | **no dominant lever; micro-lever fixed** |

- **Edits=2, `wc -l`=0, waste smells: NONE** (24 tool calls traced). No trim loop,
  no repeated scan, no ritual doc-open. The artifact (128 lines, 9 sections,
  complete) was written in one persist + 2 edits (the `Persisted`-stamp micro-lever,
  now fixed — see below).

## Why retro has no DOMINANT churn lever (the structural reasons ARE the fix target)

The debug/quality dominant churn lever is the combination **hand-edited artifact +
invisible line ceiling**: the run hand-writes, overshoots a `MAX_*_LINES` it cannot
see, then trim-loops (`Edit→wc -l→Edit`). retro is immune to THAT because it has:

1. **`persist_retro_artifact.py`** — SKILL.md routes artifact writing through the
   persist helper ("instead of ad hoc file writes"), so the artifact lands in ONE
   pass (capture: Write=1, Edit=2), not an iterative Edit loop.
2. **No line ceiling** — `validate_retro_artifact.py` has no `MAX_ARTIFACT_LINES`;
   its floor is recurrence-lineage, not length. Nothing to trim-fight.
3. **`lens_brief`** (planner) — the reference residue is briefed inline (the origin
   pattern the quality pilot mirrored), so refs are handled; only 3 briefed
   required_reads, no ritual doc-open churn.

## The one micro-lever — `Persisted`-stamp hand-fix (FOUND + FIXED)

The capture's `Edits=2` were NOT benign touch-ups (as an earlier draft claimed):
they were two byte-identical hand-edits + a verifying Read (trace steps 19-21)
setting the `## Persisted` line to the real durable path. `persist_retro_artifact`
already *computes and returns* that path (`retro_persistence_lib.py:69`) but wrote
the body verbatim with the placeholder, leaving the run to re-derive it. This is
the retro-shaped analog of the debug fix: **stamp what the tool computes instead
of making the agent re-type it.**

**Fix (shipped):** `stamp_persisted_path` in `retro_persistence_lib.py` regex-fills
the first `Persisted:` line with `Persisted: yes: <relpath>` before writing (no-op
if absent, so a hand-authored `Persisted: no: <reason>` without a persist call is
untouched); SKILL.md tells the run not to hand-edit it. Unit-tested; deterministic,
so the 2→0 edit reduction follows by construction (the placeholder is gone from
the written file) — unlike debug's soft hint, no behavioral uncertainty.

## The predictive HEURISTIC (leverage for the sweep; generalized per fresh-eye D2)

Four H0s separate cleanly — **do not capture every skill; TARGET by this heuristic**
(a heuristic induced from 4 points, not a law):

- **Churn PRESENT** ⇐ the skill (a) hand-edits its artifact via `Edit` (no persist
  helper) AND (b) the run must iterate to satisfy an **invisible validator-format
  rule** — a `MAX_*_LINES` ceiling (debug/quality) is one such rule, but so is any
  format the author re-edits to pass (retro's `Persisted` form was a micro-case even
  with NO ceiling). Fix: surface what the gate wants, or stamp it via a persist helper.
- **Churn ABSENT** ⇐ the artifact is written in one pass by a helper that stamps the
  gated fields (retro), or there is no artifact gate / pure-prose (spec).

Cheap STATIC check of a candidate's scaffold+validator for that combination predicts
the capture result before spending one. (Condition (b) was narrowly `MAX_*_LINES` in
an earlier draft — the `Persisted` micro-lever proved that overfit; generalized here.)

## Bonus: retro validates the debug fix direction

retro empirically shows that persist-helper + no-ceiling + brief = the leanest
run. The debug fix (surface the ceiling) moves debug toward this; the stronger
long-run move for any churn skill is retro's persist-helper shape. Noted, not
acted on (debug's surfaced-budget fix is PROVEN and sufficient; converting debug
to a persist helper is a larger change to weigh later).
