# Churn sweep — COMPLETE + the two open items dispositioned (2026-07-04)

Serves [intent.md](./intent.md): north = SMARTER agent; test = "그게 정말 최선인가?"
(no proxy). Closes the churn-sweep line of [anti-churn-patterns.md](./anti-churn-patterns.md).
This session extended the cold static-confirm to every artifact skill carrying the
churn PRECONDITION (scaffold-hand-edit + a validator gate), each with a bounded
adversarial fresh-eye reviewer tasked to REFUTE. The remaining skills (gather, hitl,
announcement, find-skills, impl, create-*) are ABSENT-by-construction — a one-pass
writer or no artifact gate, so no scaffold-hand-edit-vs-ceiling loop can exist (grep:
`MAX_*_LINES`/`size_budget` hits ONLY debug/handoff/quality). Honest result:
**no new warranted fix — churn is genuinely rare, and every real instance is
already fixed.**

## Full sweep picture (precondition skills reviewed; pure-writers ABSENT-by-construction)

| real churn — FIXED | no lever — ABSENT (why) |
| --- | --- |
| quality (trim-loop → report-all+scaffold-first) | issue · critique · ideation — surfaced format + irreducible judgment |
| debug (invisible ceiling → surfaced `size_budget`) | hotl · hitl · setup · narrative — no artifact gate / pure-prose (hitl one-pass render/sync) |
| retro (`Persisted` micro-lever → stamp) | release · retro · gather · find-skills · announcement — one-pass writer / persist-helper, no hand-edit loop |
| **achieve (false-green → surface `invalid_early_close_reports`, v0.60.0)** | handoff — ceiling surfaced 3 ways (prose + live planner count + prune route) |
| | spec — pure-prose, load-bearing critique |

## This session's additions (all ABSENT, earned)

- **handoff** — the strongest ceiling candidate (`MAX_ARTIFACT_LINES=70` + scaffold-only
  hand-edit), yet ABSENT: unlike pre-fix debug (ceiling invisible everywhere), handoff
  surfaces 70 in the always-read SKILL.md Bootstrap, the planner reports a LIVE
  `line_count` + status (`over_limit`/`near_limit`/`diary_smell`), AND routes overshoot
  to `repair_or_prune_handoff` BEFORE writing. It is a COMPRESSION skill (prunes a ~58-line
  doc down), the inverse of debug's author-rich-then-overshoot. The pattern-2 `size_budget`
  transfer is also structurally wrong here (payload doesn't use `current_pointer_payload`;
  the planner never consumes `size_budget`) → it would land where the run doesn't look.
- **critique / setup / release / narrative** — ABSENT. critique = ideation-shape (full
  enums inline + describe-first + preflight, no computable placeholder); setup/narrative =
  no artifact format gate (prose note); **release = the persist-helper exemplar**
  (`write_release_artifact()` stamps every computed field in one pass — the retro shape).

## The two open handoff items — dispositioned, NOT executed (would fail the one test)

- **persist-helper transfer → NOT WARRANTED.** No un-fixed churn skill needs it: the only
  remaining *ceiling-churn* skills a persist-helper would touch (quality/debug) are already
  fixed, debug's surfaced-budget fix is "PROVEN and sufficient" (retro-h0), retro's stamp
  already IS a persist-helper, and release already IS a one-pass persist-helper.
  Converting debug to a persist-helper is the noted "larger change to weigh later" — an
  optional upgrade on a solved problem, i.e. over-build. Promote patterns 1–5 to
  `create-skill` "when the sample is bigger" (anti-churn-patterns §Eventual home), not now.
- **debug-memory RCF → DEFERRED (not a live-agent lever).** [apparatus-floor-audit.md](./apparatus-floor-audit.md)
  already adjudicated the debug-memory floor: the mechanical RCF→RSF token swap is DEAD
  (`none related` is a trivially-green escape hatch → softening the matcher, forbidden),
  and the floor is MEASUREMENT-VALIDITY, not a runtime tax (faithful runs ignore it). The
  one genuine sub-lever inside it — runs skip prior-incident-memory CONSUMPTION (lost
  cross-incident compounding) — is a real smarter-agent gap, but its honest fix is a
  behavior internalization (planner surfaces near-match priors + a substance assertion,
  the five-steps precedent) that needs an ask-before-run behavioral capture. Kept as a
  deliberate future slice, per the audit's own recommendation.

## Method note

Static-check predicted every remaining skill ABSENT; captures spent = 0 (all predicted
non-hits, and the achieve fix was deterministic). The fresh-eye refutation — not a
capture — is the mechanism throughout: it caught the achieve false-green and it earned
every ABSENT here (each reviewer's strongest counter-angle failed on real files). Two
sub-threshold niceties recorded and deliberately unshipped (handoff cold-start template
comment; setup SKILL.md:152 doc-precision nit).

## Next frontier (the genuine remaining lever)

Per intent.md §"Held open" + the apparatus audit: the churn sweep and per-ref redundancy
are now exhausted; the live-agent lever that remains is the **systemic context-tax**
question — how a skill's overhead taxes reasoning across a WHOLE session (the original
symptom "에이전트가 더 멍청해진 것 같다"), which single-run capture cannot see. Measuring
it directly is still open. That is the next session's frontier, not more per-artifact churn.
