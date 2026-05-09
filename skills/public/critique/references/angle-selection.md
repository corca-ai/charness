# Angle Selection

Pick angles that create different failure stories, not five copies of "what if
this breaks."

## Anchor Lineup

The named anchors below shape angle distribution across all `critique` target
references and the `retro` `Expert Counterfactuals` lens. Each entry carries an
`applies_when:` scope tag drawn from a closed value set
(`lam-critique`, `system-improving-itself`) so a target reference or retro
session knows which anchors are eligible for the surface it is reviewing.

The substrate matters more than the persona voice. If a real-person name does
not sharpen the next move, write the lens directly. The lineup is the agreed
shorthand, not a required cast.

- `anchor_id: jackson` — Michael Jackson (problem framing).
  `applies_when: lam-critique`. Trigger: is the change framed against the
  user's actual problem, or against the most convenient implementation slice?
- `anchor_id: weinberg` — Gerald Weinberg (diagnostic).
  `applies_when: lam-critique`. Trigger: is the cause located where the
  change puts the fix, or only the symptom?
- `anchor_id: gawande` — Atul Gawande (checklist / operational).
  `applies_when: lam-critique`. Trigger: which concrete operator step is
  added, removed, or silently broken by this change?
- `anchor_id: raskin` — Jef Raskin (humane interface / first-time-use).
  `applies_when: lam-critique`. Trigger: what does the first real reader,
  user, or downstream agent hit on first contact with this change?
- `anchor_id: minto` — Barbara Minto (structure / communication).
  `applies_when: lam-critique`. Trigger: when this change is read later
  with no chat context, will the why/what/how chain still hold?
- `anchor_id: engelbart` — Douglas Engelbart (co-evolution of human, tool,
  and training). `applies_when: system-improving-itself`. Trigger:
  *treat (H + LAM + T) as one unit; design T alongside LAM.* Fires when the
  pending change designs the system that designs work — T-loop wiring,
  skill self-evolution mechanism, retro contract change, anchor lineup
  metadata, capability discovery surface — not when the change is an
  ordinary code/PR/release/rename/spec critique.
  - Falsifier: if this anchor is observed to fire on a `lam-critique`
    surface in dogfood and distorts the verdict at least once, escalate to
    option B (separate lineup). Escalation cost is bounded — change the
    lineup metadata format inside `skills/public/critique/references/` and
    keep `applies_when:` as the routing seam. This is not a second rename
    event.

A target reference or retro session selects from this lineup using its own
weighting; it does not redefine the lineup. The `applies_when:` scope is the
contract: a `lam-critique` surface (code/PR critique, release critique,
rename critique, decision premortem, spec critique, ordinary retro lessons)
draws from the five `lam-critique` anchors. A `system-improving-itself`
surface (designing a T-loop, changing how skills self-evolve, changing the
retro/critique substrate itself) draws Engelbart in addition.

When a `critique` or `retro` run actually selects an anchor from this lineup,
the `anchor_invoked` t-event (see `<repo-root>/integrations/t-events/event.schema.json`)
captures `anchor_id` and `applies_when` so Tier C evidence in
`charness-artifacts/skill-t-mechanism/inventory.{md,json}` can show which
anchors fire on which surfaces over time. New `applies_when:` values require
both this spec update and at least one positive dogfood case before landing.

Good default angles for a non-trivial change:

- `customer-of-this-capability`: what the user or downstream agent experiences
  on the first real use, including missing setup, stale adapters, thin defaults,
  confusing next actions, and silent fallback behavior
- `blast-radius`: what breaks for current users, operators, or consumers
- `implementation integrity`: what hidden coupling or duplicate logic makes the
  plan less safe than it looks
- `future maintainer`: what a new reader will misread, reopen, or delete
- `doc and source-of-truth cascade`: what named docs, examples, or packaged
  mirrors become misleading after the change
- `first-reader`: for durable docs, spec indexes, public skill prose,
  README-like surfaces, and source-of-truth narrative, what the plain-language
  first-time reader will hit before any taxonomy lands. Lenses to include:
  plain-language reading path (does the structure teach the product before the
  document architecture); legacy-coupled negative phrasing (does the doc still
  define itself against a removed concept); product-story-before-taxonomy
  (does the first heading path lead with reader tasks instead of model,
  projection, or proof-view labels); title-slug coherence after rename-heavy
  edits (do filenames, slugs, compact keys, and link labels still match the
  new H1 titles, and is any concept-home page duplicated)
- `devil's advocate`: strongest argument for keeping the current design

Subagent sizing:

- minimum: two contrasting angle subagents plus one separate counterweight
  subagent
- default: three angle subagents plus one counterweight subagent
- widen to four angle subagents only when the change spans multiple durable
  surfaces, a breaking migration, or a release/install/doc cascade
- if you cannot name four meaningfully different angles, stay at two or three
  instead of inventing filler

The parent review coordinator owns spawning those angle and counterweight
subagents. A delegated angle reviewer should run the assigned lens directly and
should not spawn another reviewer unless the parent explicitly asks for
recursive delegation.

Canonical execution uses subagents. Before a parent reports that path as unavailable, use `../../../shared/references/fresh-eye-subagent-review.md`: attempt the bounded subagent setup, resolve availability uncertainty, and cite the concrete host signal. If the host still cannot provide subagents, say the canonical critique path is unavailable and leave the host-side contract gap visible. Do not collapse into a same-agent self-review.

Rotate or swap angles when the change is narrower:

- skill, adapter, bootstrap, or example changes where the main risk is a bad
  first run for the skill's customer
- breaking change boundary
- release-time operator proof
- external consumer migration
- install/update/support behavior
- policy or security posture

Include the `first-reader` angle when the change touches durable docs, spec
indexes, public skill prose, README-like surfaces, or source-of-truth
narrative. For rename-heavy edits, the title-slug coherence lens belongs in
the same angle so structural rewrites do not hide stale slugs, links, or
duplicated concept-home pages behind a polished outline. Run
`<repo-root>/scripts/check_title_slug_drift.py` against the affected spec or
docs roots as deterministic evidence for the title-slug lens before relying
on prose judgment alone.

Keep the angle set bounded.
Three strong angles plus one counterweight pass is usually better than six weak
angles and no triage.
