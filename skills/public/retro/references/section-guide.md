# Retro Section Guide

The core retro stays small and repeatable.

## Context

State:

- what unit of work is under review
- why it mattered
- which evidence sources are trustworthy for this retro
- when conclusions mix hard local proof with weaker judgment, tag the claim
  strength inline as `strong`, `moderate`, `weak`, or `contested`

Do not repeat the entire session transcript.

## Waste

Identify where effort was lost:

- unnecessary backtracking
- hidden assumptions
- missing verification
- repeated reconstruction
- slow approval loops
- gate-baseline runtime: a gate that PASSES but is slow by design (pre-push,
  full suite, coverage). A passing slow gate is code-quality debt, not
  "necessary safety cost" — name its measured runtime, route the structural fix
  to the gate-implementation owner, and do not let it sit unflagged in an
  Evidence line. See `phase-aware-efficiency.md` *Gate-Baseline Runtime*.

For efficiency claims, identify the phase before prescribing a fix. Broad
exploration is not waste solely because it was broad; first ask whether it was
user-intended, where the triage lock happened, and whether later work drifted
after that lock. When phase is inferred rather than directly evidenced, reuse
the `strong`, `moderate`, `weak`, or `contested` claim-strength tags from
`Context`.

Prefer causal explanation over complaint.

## Critical Decisions

Capture the decisions that changed outcome.

For each important decision:

- what was chosen
- what alternatives were skipped
- why the choice was made
- what it constrained later

This section explains the past. It is not the place for tool shopping.

## Window, Evidence, And Trends

Add these three bounded sections when they are supported by real evidence:

- `Window`: the span of work being reviewed
- `Evidence Summary`: which artifacts or commands were actually used
- `Trends vs Last Retro`: current delta versus the last durable retro

If there is no prior retro, say so plainly and skip the comparison section
instead of inventing trend data.

## Expert Counterfactuals

Ask:

- what would a strong expert in this domain have done differently?
- what question would they have forced earlier?
- what evidence would they have demanded before acting?
- where would they downgrade a confident story because the available evidence
  is only anecdotal or authority-based?

Prefer named experts with distinct lenses.

## Next Improvements

Every retro needs concrete future changes. Group them by type:

- `workflow`: process or sequencing change
- `capability`: skill, tool, adapter, preset, or automation change
- `memory`: durable note, handoff, checklist, or artifact update

This is where self-growing and self-healing live. Capability recommendations
belong here because they are future improvements, not past decisions.

## Recurrence Class

A `Waste` or `Next Improvements` bullet may carry an explicit concept identity:

```markdown
- re-ran the sync helper after every edit (recurrence-class: derived-surface-batching)
```

Why it exists: the lesson-selection index groups candidates by the first 14 words
of the bullet's surface text, so **re-wording a lesson silently resets its
recurrence count to 1**. Measured on this repo's corpus, 1594 of 1596 candidates
sat at one independent observation, making the recurrence multiplier exactly 1.0
and digest selection pure recency — while one concept held 7+ rows across 6 dates
and never won a slot. The tag is the only identity a re-wording cannot break.

How to use it:

- Reuse an existing slug when this is the same concept biting again, even if you
  describe it in completely different words. That is the entire point; a fresh
  slug for a re-observed trap is the defect, not the fix.
- Coin a new lowercase-hyphenated slug only for a genuinely new concept.
- The tag is stripped from the digest text, so write the bullet to read naturally
  without it.
- It groups across sections and dates: the same class seen as `Waste` in one retro
  and a `Next Improvements` item in another is one recurring class, not two
  one-offs.
- A malformed slug is a gate failure, not a silent fallback — a prefix-matching
  typo like `Bad_Slug!` would otherwise create the wrong class `bad`.

The tag is presence-and-shape only. Whether two bullets really share a concept is
the author's and reviewer's judgment; no gate classifies content.

Untagged bullets keep the historical surface-text grouping, so this is additive —
nothing already written changes meaning.

## No Hidden Snapshot

Do not invent a hidden machine-readable snapshot format. The retro's durable
output is the artifact under `output_dir`; the closeout-telemetry stream it may
read is written by the closeout emitter, never by the retro.

## North Star Alignment

Required in every retro, and enforced by the retro validator.

Read the repo's governing design standard and record what it says about **this**
work — do not recall it from memory. Three things belong here:

- **Which facets held**, with the concrete evidence that they did.
- **Which were mis-applied.** This is the valuable half and the one most often
  skipped: naming a principle you followed is cheap, naming one you inverted is
  what changes the next run. A real example: treating a reversible, low-cost
  action as an irreversible boundary is a judgment-on-reversible-work failure,
  and it cost three rounds of operator attention before anyone said so.
- **Any named failure signature the run walked into**, if the standard
  enumerates them.

The floor is presence-only. It proves the question was asked; whether the answer
is any good is the fresh-eye reviewer's call, and a validator that scored it
would be pretending to a judgment it cannot make.

Why a floor rather than prose: this skill's prose already pointed at the
standard, and two consecutive retros still shipped with no mapping at all. A
recurrence is the bar for teeth, and this cleared it.
