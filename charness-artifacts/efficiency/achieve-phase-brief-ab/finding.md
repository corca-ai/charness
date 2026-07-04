# achieve phase-brief demote A/B — pre (d14ec985~1) vs post (d14ec985), 2026-07-04

Real `claude -p` spend (operator-authorized, items 1-2 of the 2026-07-04
efficiency plan), judge wired (`--judge-cmd python3 scripts/outcome_judge_cmd.py`).
Same `/charness:achieve` shaping prompt both arms (spec default), so
find-skills/CLAUDE.md routing cancels; the delta is the demote commit.

## Metrics (n=3 per arm, mean [min–max])

| metric | pre-demote | post-demote | delta |
| --- | --- | --- | --- |
| matcher pass_rate | 1.0 | 1.0 | — |
| outcome grade (judge, 0 skipped/0 errors) | 1.0 [1–1] | 1.0 [1–1] | **parity** |
| total_tokens | 4.31M [3.67–4.66M] | 4.82M [3.90–6.22M] | +11.8% (overlapping; one 6.22M outlier) |
| output_tokens | 87.6k [71.1–114.3k] | 77.9k [64.3–86.6k] | **-11.1%** (nearly disjoint ranges) |
| duration_ms | 696k [626–737k] | 623k [545–732k] | -10.5% |
| tool_count | 48 [40–55] | 50.7 [42–66] | +5.6% |

## The behavioral finding (stronger than the means)

Trace digests show the demote changed HOW runs engage the reference, exactly
as designed:

- **pre-demote: 0/3 runs opened lifecycle.md at all** — silently non-compliant
  with their own "read the full contract" routing (re-confirms the Slice-7
  capture).
- **post-demote: 3/3 runs did section-scoped reads** — e.g.
  `awk '/^## Before$/,/^## During$/' .../lifecycle.md` plus the
  `## Honest Proof Discipline` coda (`sed -n '854,920p'`): the exact
  phase-scoped read the `phase_brief` names, ~11KB instead of the 51KB
  full-doc mandate.

So the demote converted silent non-compliance into cheap compliance: runs now
actually follow their own routing, engage the phase depth, and still show
judge-graded outcome parity with slightly lower output tokens and wall time.

## Proves

- No capability loss: matcher AND judge outcome parity 3/3 on both arms
  (`auditable-goal-substance` graded live, never skipped).
- The phase-scoped routing is followed in practice (3/3 section-scoped reads),
  not just emitted.

## Honest non-claims

- n=3; total_tokens ranges overlap heavily (one post-demote 6.22M outlier) —
  no claim of total-token reduction. The pre-registered expectation in
  config.json (near-null efficiency delta because faithful runs already
  skipped the docs) is what the means show.
- The delta is the whole demote commit, not one line within it.
- output_tokens -11.1% has nearly disjoint ranges but n=3 — suggestive, not
  conclusive.
- The measured shaping prompt exercises the Before phase; During/After-phase
  economics (closeout still reads ~40KB: ## During + closeout_handoff →
  ## After) are analyzed in the code critique, not measured here.
