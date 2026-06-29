# Spec — Skill Planner Uniformity (locked intent)

Status: locked intent 2026-06-29; build sequence below. Flows from the
claim-fidelity methodology
([2026-06-23-skill-claim-fidelity-doc-philosophy.md](./2026-06-23-skill-claim-fidelity-doc-philosophy.md))
and the retro live-capture pilot (commits `a7e49790`..`a758df0c`).

## North Star

A well-formed skill encodes HOW TO USE IT in code (a deterministic planner /
briefing surface), not prose. Uniform structure across all skills means an agent
(and plugin user) learns ONE protocol, not 20 bespoke bootstraps — fewer
concepts/terms to know. This operationalizes the design north-star (brief a
capable judge via a deterministic surface) uniformly across the skill set.

## Locked Intent (3 items, scoped)

1. **Matcher: count file reads, not just Read tool-calls.** — LANDED (2026-06-29).
   `build-skill-execution-observation.mjs` `collectOpenedBasenames` counted only
   `file_path`/`notebook_path` keys, missing Bash `sed`/`cat`/`head` reads, so
   coverage under-reported. Fix shipped: `parseReadCommandBasenames` parses
   `cat|sed|head|tail|less|nl|rg|grep|awk` + path operands, dropping the
   pattern/script operand of grep/rg/awk/sed so a reference NAMED in a search
   pattern never miscounts as opened (coverage must not inherit the floor matcher's
   "named anywhere in the command log" blur). A live re-tally over the surviving
   raw capture trees (`/tmp/charness-retro-*`, ephemeral — the committed
   `observed.v1.json` packets still record the pre-fix 0/9 and 4/9, so the figures
   below are a re-tally observation, not re-derivable from committed artifacts)
   verified the property: the FAILED capture rose 0/9 → 1/9 (recovered its
   `sed`-read of `waste-sibling-scan.md`) yet `expert-lens.md` stayed missing and
   the outcome stayed `failed` — a sharper metric does not rescue a real floor
   miss; the PASSED re-capture held at 4/9 (it read via the Read tool, no
   regression). The floor (`requiredCommandFragments`) is unaffected by design.

2. **Planner envelope unification BEFORE any rollout.** The existing 6 planners
   (debug/gather/handoff/issue/quality/release) have divergent schemas; adding 14
   more bespoke ones multiplies concepts instead of reducing them. So: unify the 6
   + retro into ONE canonical envelope + shared lib; minimal common vocabulary =
   `{required_reads, next_action, gate_packets}` (skill-specific fields stay
   extensions). Linear skills get a minimal required_reads emitter — no fake
   branches (Floor-Addition Restraint). Once the envelope is fixed, bake "a new
   skill ships a planner" into `create-skill` as the well-formedness standard.

3. **More fixtures ONLY where the default prompt can't evaluate the skill.** Add a
   scenario fixture only when a single representative/bare prompt cannot honestly
   exercise the skill's claim (a genuinely branching workflow), and only for a
   branch with a UNIQUE floor. Each new fixture is a static hypothesis → it needs a
   live capture (live-capture-before-assert). Not completeness for its own sake.

## Build Sequence (post-compaction pickup)

1. Item 1 (matcher fix) — smallest, foundational (it is the measurement
   instrument); re-tally the two retro captures to verify the new count.
2. Item 2 *foundation* — unify the planner envelope + shared lib + minimal
   vocabulary. This is the real structural work and precedes any rollout.
3. On that envelope: capture `hitl` → if a passive-pointer shape is confirmed, fix
   with the unified planner; fold in item 3 (a branch fixture) only if hitl
   branches. Then capture-prioritized rollout for the rest.

## Guardrails (honest caveats, locked)

- Envelope BEFORE more planners. Mechanically adding planners to 14 skills without
  one canonical envelope is debt, not unification — stop that path if proposed.
- Don't cargo-cult: a planner on a skill with no real briefing decision is
  boilerplate that ADDS concepts. Minimal emitter for linear skills.
- Rollout order is capture-driven (where a floor actually fails), reconciling the
  proactive envelope (design up front) with the reactive methodology (lens 9 /
  live-capture-before-assert): design the envelope first, let captures pick the
  order.
