# Rename Critique

Critique a rename, deletion, or slug churn before the cite churn lands. The
substrate (multi-angle review with one counterweight pass and four-bin
triage) is shared with other `critique` targets; this reference shapes the
angle distribution and output for *rename/deletion lock-in*.

## When This Lens Fires

Pick this reference when the pending change moves, renames, or removes a
named concept across multiple cite sites. Trigger phrases:

- `rename critique`, `rename premortem`, deletion review
- skill rename, directory rename, module rename, validator rename
- spec slug rename, doc title rename, anchor concept rename
- plugin export rename, capability id rename, integration rename
- removal of a named concept the repo has been citing

If the change is a single-file diff with no cross-file cite churn, route to
`code-critique.md`. If the question is whether to rename at all (not how to
land the rename), route to `premortem-decision.md`.

## Anchor Angle Distribution

For rename/deletion lock-in, anchor weighting emphasizes the first-time
reader and the cite cascade:

- **Jef Raskin (humane interface / first-reader)** — strong default. What
  does a first-time reader hit when they search for the old name? Does
  the new name actually teach the concept faster, or does it just churn?
- **Barbara Minto (structure / communication)** — strong default. Do
  filenames, slugs, compact keys, link labels, and H1 titles still match
  the new name? Will the reader's mental top-down chain hold?
- **Michael Jackson (problem framing)** — moderate. Was the old name
  framed against the wrong problem (which is *why* the rename), or was the
  framing fine and only the surface moves?
- **Atul Gawande (checklist / operational)** — moderate. Did the cite
  churn step run? Did the validator allowlist stay tight? Did the plugin
  manifest sync run before the validator?
- **Gerald Weinberg (diagnostic)** — light. Useful only when the rename is
  a symptom of a deeper concept-confusion problem and the reviewer should
  push back on whether rename alone resolves it.

Default slate: Raskin + Minto + Gawande. Swap in Jackson when the rename
is conceptually motivated, not just cosmetic.

## Counterweight Bins

The four bins from `counterweight-triage.md` apply directly. Rename-
specific tightening:

- **Act Before Ship** — concerns that require holding the rename PR: a
  cite site outside the allowlist, a validator that does not actually
  fail-closed, a plugin manifest still pointing at the old path, a
  generated surface (CLI reference, install manifest) not regenerated.
- **Bundle Anyway** — cheap fixes touchable in the same churn: a stale
  comment that mentions the old name in a way the new reader will misread,
  a deprecated cite advisory that should remain N releases for consumer
  migration, or an incoming-link/index update discovered by the bounded review.
- **Over-Worry** — concerns that imagine consumers who have never been
  observed, aesthetic objections to the new name when the contract
  semantics are unchanged, or "search will be slightly worse" without
  evidence.
- **Valid but Defer** — concerns that are real but belong in a later
  slice: a follow-up rename of an adjacent concept, a documentation
  rewrite that depends on dogfood, a deferred allowlist tightening once
  consumer migration data lands.

## First-Reader Probe

Every rename critique records a first-reader probe: does a reader who
knows only the new name, with no chat or prior-version context, hit a
coherent mental model on first read? Concretely:

- read the SKILL.md or top-level surface using only the new name
- check that filenames, slugs, link labels, and H1 titles agree
- check that legacy-coupled negative phrasing (defining the new concept
  against the removed one) is gone or explicit lineage cite

A first-reader probe that fails routes the concern to `Act Before Ship`
unless the reviewer can show the friction is bounded and worth the slice.

## Title-Slug Coherence Review

Compare each affected filename/slug with its H1 and first-reader description.
Inspect incoming links and generated indexes separately so a polished title does
not hide a stale route. This is reviewer judgment: record the paths inspected and
do not render an aggregate clean verdict from word overlap.

## Per-Removed-Concept Verdict (deletion is an irreversible boundary)

Deleting a cited concept is irreversible: consumers that depended on it lose it,
and the removal enters shared history others build on. So per *P4* of the
authoring-repo-internal `<authoring-repo>/docs/design-north-star.md`, a title/slug
comparison and "I updated the cites" are *claims* the cite sites were found —
not proof each consumer still behaves without the removed concept.

For **each** removed or renamed concept, render a verdict that its dependents
resolve, confirmed through a channel **distinct from** your own edit pass: the
rename validator allowlist, an incoming-link inventory, and an actual first-read
of a consumer that knows only the new name (the First-Reader Probe
above) — **or** record an explicit disposition (a deprecation cite kept N releases
for consumer migration, an `Act Before Ship` hold, a deferred allowlist
tightening). An inventory or first-reader probe you do not actually read back
is not this verdict. This is a per-concept **question to render, never a
"cites look updated, ship it" aggregate sign-off to declare**; it adds no gate.

## Output Shape

In addition to the substrate `Output Shape` from `SKILL.md`, rename
critique records:

- `Rename Scope` — old name → new name, plus the cite count snapshot at
  critique time
- `Allowlist Inventory` — paths kept on the rename validator allowlist
  with the reason for each (lineage, history, validator self, release
  notes, etc.)
- `First-Reader Probe Result` — pass/fail summary plus the concrete
  friction observed
- `Title-Slug Coherence Review` — paths inspected; H1/filename comparison;
  incoming-link/generated-index result; and any first-reader friction, without
  an aggregate clean verdict
- `Pre-Merge Action` — for each `Act Before Ship` concern, the concrete
  cite update, manifest sync, or generated-surface regen required
