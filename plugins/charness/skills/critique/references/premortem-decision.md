# Premortem (Decision)

Decision pre-mortem in the Gary Klein lineage. Imagine the decision shipped
and failed; ask what made it fail; convert that into pre-lock-in changes to
the decision contract.

This is one target of `critique`. The substrate (multi-angle review with one
counterweight pass and four-bin triage) is shared across targets; this
reference shapes the angle distribution and output for *decision lock-in*.
The word `premortem` is preserved here because it names the Klein-lineage
target; the skill itself is named `critique` because the same substrate
applies to code, release, rename, and spec lock-in too.

## When This Lens Fires

Pick this reference when the pending change is a decision lock-in that has
not yet committed code, release, or rename. Trigger phrases:

- `decision premortem`, `pre-mortem`
- design lock-in, architecture choice, capability boundary lock-in
- "before we lock this", "before we commit to this approach"
- workflow contract change that affects future operator behavior
- compatibility, install/update, host-proof, prompt-surface, public-skill,
  validator, or export decisions when the *decision shape* is what is
  locking, not a concrete diff or release artifact

If the change is already a diff, release artifact, rename plan, or spec
draft, route to `code-critique.md`, `release-critique.md`,
`rename-critique.md`, or `spec-critique.md` instead.

## Anchor Angle Distribution

For decision lock-in, all five anchors fire usefully; the default three-angle
slate samples *contrasting* anchors instead of three near-duplicates.

- **Michael Jackson (problem framing)**: is the decision framed against the
  right problem? Does it conflate the user's pain with the implementation's
  convenience? `framing` lens is the strongest default angle.
- **Gerald Weinberg (diagnostic)**: is the *current* situation actually the
  problem the decision is solving, or is the perceived problem somewhere
  else? Pulls speculative future-consumer arguments back to current evidence.
- **Atul Gawande (checklist / operational)**: what concrete operator step is
  about to be added or removed? What checklist gap creates silent failure
  later?
- **Jef Raskin (humane interface / first-time-use)**: what does the first
  real user or downstream agent experience? Is the next-action friction
  visible before lock-in?
- **Barbara Minto (structure / communication)**: when this decision is
  written down for future readers, will the why/what/how chain still hold,
  or will the rationale rot into folklore?

Default slate for a non-trivial decision: Jackson + Weinberg + one of
{Gawande, Raskin, Minto} chosen by the decision's surface. Add a fourth
angle only when the decision spans cross-surface, breaking, migration-heavy,
or release plus doc cascade scope.

## Counterweight Bins

The four bins from `counterweight-triage.md` apply directly. Decision-
specific tightening:

- **Act Before Ship** — concerns that change the decision contract,
  acceptance criteria, or success line. A concern qualifies only if naming
  the change is concrete (not "tighten the rationale", but "swap fixed-
  decision X for probe Y").
- **Bundle Anyway** — cheap fixes touchable in the same lock-in: a missing
  Deferred Decision entry, a Probe Question that surfaces a fixed-decision
  ambiguity, an out-of-scope line that is still implicit.
- **Over-Worry** — speculative consumers, "free oracle" arguments that
  silently require maintaining two decision paths forever, aesthetic
  concerns about wording when the contract semantics are clear.
- **Valid but Defer** — a real concern, but the honest tradeoff is shipping
  this decision and reopening when concrete evidence shows the deferred
  cost is higher than predicted.

## Output Shape

In addition to the substrate `Output Shape` from `SKILL.md`, decision
critique records:

- `Decision` — one or two lines naming what is locking
- `Klein Lineage Cite` — when the decision has lineage to a prior premortem
  artifact, name the path so the rationale chain is traceable
- `Acceptance Tightening` — for each `Act Before Ship` concern, the concrete
  acceptance line or fixed-decision edit that resolves it
- `Deferred Decisions` — concerns triaged as `Valid but Defer`, written into
  the decision artifact so they are not silently dropped

## Klein Lineage

The premortem technique here is named for Gary Klein's pre-mortem ("imagine
the project has failed; explain why"). The substrate is older — devil's
advocate review, design crit, structured pessimism — but the Klein framing
is the one most repos cite when they say "premortem". This reference
preserves the word so search and historical cites stay legible.
