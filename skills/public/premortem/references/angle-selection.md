# Angle Selection

Pick angles that create different failure stories, not five copies of "what if
this breaks."

Good default angles for a non-trivial decision:

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
- widen to four angle subagents only when the decision spans multiple durable
  surfaces, a breaking migration, or a release/install/doc cascade
- if you cannot name four meaningfully different angles, stay at two or three
  instead of inventing filler

The parent review coordinator owns spawning those angle and counterweight
subagents. A delegated angle reviewer should run the assigned lens directly and
should not spawn another reviewer unless the parent explicitly asks for
recursive delegation.

Canonical execution uses subagents. Before a parent reports that path as unavailable, use `../../../shared/references/fresh-eye-subagent-review.md`: attempt the bounded subagent setup, resolve availability uncertainty, and cite the concrete host signal. If the host still cannot provide subagents, say the canonical premortem path is unavailable and leave the host-side contract gap visible. Do not collapse into a same-agent self-review.

Rotate or swap angles when the decision is narrower:

- skill, adapter, bootstrap, or example changes where the main risk is a bad
  first run for the skill's customer
- breaking change boundary
- release-time operator proof
- external consumer migration
- install/update/support behavior
- policy or security posture

Include the `first-reader` angle when the decision changes durable docs, spec
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
