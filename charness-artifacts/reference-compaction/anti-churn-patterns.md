# Anti-churn skill patterns + H0 method (locked from 4 captures, 2026-07-03)

Serves [intent.md](./intent.md): north = SMARTER agent; test = "그게 정말 최선인가?"
Four per-skill H0 captures (quality / spec / debug / retro) converged on a small
reusable pattern set. This LOCKS them so the sweep transfers proven design instead
of re-deriving per skill. **`retro` is the exemplar** — ~8× leaner than debug/
quality (20k output, 24 tools, 5.7min, 0 waste smells) precisely because it already
embodies patterns 1–5 below. Per-skill evidence: the sibling `*-h0-*.md` diagnoses.

## Design patterns — transfer targets ("how retro is so good")

Ranked by leverage. Each: exemplar · anti-pattern it removes · where to transfer.

1. **Persist-helper stamps what it computes.** retro `persist_retro_artifact` +
   `stamp_persisted_path`: the helper writes the artifact in ONE pass and fills the
   fields it already knows (durable path, digests) instead of leaving placeholders
   the run hand-edits. *Anti-pattern:* scaffold emits `TODO`/placeholder → run hand-
   fixes (retro's 2-edit micro-churn; the debug path re-derivation). *Transfer:* every
   artifact-writing skill; the STRONGEST anti-churn shape. Today only retro has it —
   all others are scaffold-only hand-edit.
2. **Surface the gate's expectation up front.** debug `size_budget`: when a validator
   enforces an invisible rule (a `MAX_*_LINES` ceiling; a required format), the
   scaffold/planner states it BEFORE the write so the run writes-to-fit, not write-
   then-trim. *Proven:* debug 37→7 edits, 19→0 `wc -l` once surfaced. *Transfer:* the
   shared `size_budget` field (`scaffold_artifact_lib.current_pointer_payload`) + the
   count-reporting `validate_max_lines` already exist — a ceiling-capped skill just
   passes `size_budget` from its scaffold (one small edit, mirror debug).
3. **Validator reports ALL violations + actual counts.** `validate_max_lines`
   ("is N lines … cut ~M"); quality report-all default. One pass names every problem
   + the exact overage → fix once, no re-run / `wc -l` loop. *Anti-pattern:* fail-fast
   + vague message → N re-runs (quality's 6×).
4. **Planner emits a substantive brief (`lens_brief`).** References become trigger-
   gated depth, not mandatory reads (quality pilot; retro origin). *Anti-pattern:* N
   mandatory primer reads the representative run does not need.
5. **Auto-refresh derived surfaces from the durable write.** retro persist auto-
   refreshes the recent-lessons digest + selection index. *Anti-pattern:* hand-
   maintaining a summary that drifts.

## When it is NOT churn (equally important — do not manufacture a fix)

`spec`: pure-prose, no artifact gate → no churn lever; its cost (fresh-eye critique
that caught real defects + repo-truth ingest) is load-bearing. A "fix" here would
fail the intent test. References are almost never the drain (confirmed 4×).

## The churn heuristic (cheap static-check BEFORE spending a capture)

Churn PRESENT ⇐ the skill (a) hand-edits its artifact via `Edit` (no persist helper)
AND (b) the run must iterate to satisfy an **invisible validator-format rule** — a
`MAX_*_LINES` ceiling is one; retro's `Persisted` form was a micro-case with NO
ceiling. Churn ABSENT ⇐ one-pass persist-helper that stamps gated fields (retro), or
no artifact gate / pure-prose (spec). Static-check a candidate's scaffold+validator
for (hand-edit + invisible format rule); it predicts the capture result.

## The H0 method (locked)

1. **Capture-then-diagnose; never assume the lever.** Find the DOMINANT cost
   empirically. Refs are almost never it.
2. **Static-check by the heuristic first; H0 only the hits.** Do not sweep by ref
   count (spec proved ref count ≠ lever) or capture every skill.
3. **Classify the fix:** DETERMINISTIC (the tool computes the value) → a unit test is
   proof, no re-capture (retro's stamp). BEHAVIORAL (a soft hint the run may ignore)
   → controlled A/B, same session/bug, only the fix differs (debug; stronger than n=2
   uncontrolled).
4. **Fresh-eye before commit.** It caught a real defect in 3/4 (spec's Bootstrap-scan
   candidate, debug's honesty scope, retro's micro-lever).

## Eventual home

Once proven across more skills, patterns 1–5 belong in `create-skill`'s authoring
contract (new artifact skills default to persist-helper + brief). Not yet — lock
here, transfer per-skill, promote when the sample is bigger.
