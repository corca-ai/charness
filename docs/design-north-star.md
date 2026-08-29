# Charness Design North Star

> Status: current
> Source of truth: this page and its linked executable surfaces

**One idea: the harness briefs a capable judge, and keeps teeth only where a
wrong answer escapes.** Equip judgment; fence only cliffs.

## Purpose (what the one idea serves)

**Charness exists to reduce rework in the repositories that consume it, and to
make agentic development there fast.** The one idea above is the method; this is
the goal it serves, and what *Operating stance* means by "serve the goal first."

- **The consumer is the subject.** A change that improves this checkout while
  breaking or slowing a consuming repo is a regression however green it measures
  here.
- **Rework is the unit, not gate count.** Machinery earns its place by preventing
  work that would otherwise be done twice. Machinery that does not is cost — and
  so are an unread artifact and an unarmed detector.

This is the standard the rest of the harness is measured against. When a skill,
gate, doc, or contract is added or changed, it earns its place against this idea
or it does not belong.

## Diagnosis (back-tested 2026-06-20 — partially confirmed)

The repeated harness failure is not "too many gates." It is **terminal trust at
irreversible boundaries**: a single context — a gate's green, a `CLOSED` state,
a deployment readback, a reviewer's "looks good" — was treated as proof that an
irreversible action was done right. The recurrence cluster
(#359/#363/#376/#381/#382/#385/#386) is one mental model wearing seven masks.

The bloat (≈17.6K lines of reference prose, ≈34.7K lines of gate scripts, skill
bodies pinned at the length cap) is the *cost of meeting that failure with ever
more bespoke gates*. The fix is neither more gates nor blind trust. It is
**non-terminality at the few boundaries that matter, and terse,
concept-separated judgment everywhere else.**

The [#359–#386 back-test](../charness-artifacts/audit/2026-06-20-north-star-phase0-diagnosis-backtest.md)
(2026-06-20) confirmed this on the irreversible-boundary cases (0/7 contradict)
and sharpened it: the failure is terminal trust on a *single evidence channel*,
not gates as such — the remediations that worked were gates that force a check on
a **distinct** channel (P5), and a distinct *observer* that re-reads the same
proxy still rubber-stamps (#359, #386). The operative variable is the channel.

## The five facets of the one idea

**P1 — Default to judgment on reversible work.** Where a mistake stays inside
this session's editable state, the default is a short principle plus the agent's
judgment; a gate/validator/rule here bears the burden of showing why judgment
alone fails. *Because over-encoding reversible work bought bloat, not safety.*

**P2 — One surface, one concept (Raskin).** A skill teaches itself. A body at
the length cap is a signal to *separate a concept or delete* — never to shave
lines or push overflow into `references/`. *Because displaced overflow goes
unread, and unread prose is not a contract.*

**P3 — Principle over rulebook.** Prefer one sharp worked example plus the
principle behind it, so the reader derives the next case. *Because an enumerated
"do not X" list rots and still misses the case it never listed.* (Exception: at
an irreversible boundary, the list of irreducible observables **is** the
contract — see P5.)

**P4 — At irreversible boundaries, success is provisional.** A passing gate, a
`CLOSED` state, a readback, an advisor verdict — each is a *claim*, not a
conclusion. Confirm it by re-examination that uses a **different evidence
channel and a different observer** than the claim under review; never by
re-reading the same proxy. *Because form-passed ≠ content-correct, and at a
cliff the wrong form has already escaped.* (#386's reviewer re-read the same
proxy and rubber-stamped; this is the facet that stops that.)

**P5 — Teeth only for irreversibility and form.** A gate may *force a question*;
it may not *declare completion*. There is no terminal green. At an irreversible
boundary, closeout stops when the **evidence record is populated with captured
observables and a distinct second observer has signed** — the populated record
is the stop condition, not the gate. *Because a terminal green is the exact
thing the cluster abused.*

## The boundary (load-bearing)

P4 and P5 turn on one term, so it is defined by **blast radius of a wrong pass**,
not by literal undo-ability:

- **Irreversible** — a wrong success propagates somewhere you do not control
  before you can correct it: another agent acts on it, it ships to an operator,
  or it enters shared history others build on. **When unsure, classify as
  irreversible.**
- **Reversible** — a wrong success stays inside this session's editable working
  state.

The irreversible set includes: GitHub issue/PR close, release publish, external
state writes (Slack / Notion / provider / apply-to-prod), deletions, and
**authoring or changing a proof surface** — a gate, validator, or evidence floor.
(Reopenable ≠ reversible: a reopened issue was already read as "done".)

That last entry is a reading of the definition above, not an addition to it. A
proof surface that fails open satisfies all three clauses at once: other agents
act on its green, it ships to every consuming repo, and every future session
builds on the history it certified. And a wrong pass here is *silent by
construction* — a fail-open gate emits no failure, no log line, no ticket — so
the elapsed time before anyone notices is unbounded. The 2026-07 evidence-surface
hunt measured that: thirty defects across the repo's proof surfaces, none of them
regressions, most written once and never revised, the oldest sitting green for
three months in a repo with a 5.8K-test suite. One arrived on the very commit
implementing P4 — *applying the principle produced a violation of it*.

So P4 applies here in full: a proof surface's own author and its own tests are
one observer, and a large suite is not many independent observations along this
axis — the author writes the gate and the gate's tests in the same sitting, from
the same mental model, so the blind spot in the code and the blind spot in its
test are the same blind spot. The distinct observer is a fresh-eye review at the
authoring boundary, which in that hunt found defects inside the fix on 6 of 6
slices, several of them the exact class under repair.

What this does **not** license is a gate that checks gates. That is the
anti-pattern named in the diagnosis above — meeting a gate-quality problem with
another bespoke gate — applied to itself. The teeth here are a distinct observer
and a scope a verdict must name, not another green.

## Operating stance

Serve the goal first. When a *reversible* surface fights the goal, fix the
system even at the cost of speed. Irreversible-boundary safeguards are not
"friction to fix" — they are the goal at the boundary. When goal and system
genuinely conflict and the call is unclear, ask.

## Taste (a preference order — not a sixth facet, not a gate)

P1–P5 are each a principle with a measured failure behind it. This section is
different in kind, and it sits apart on purpose. It is **taste**: a preference
order for choosing among options that *all* already satisfy the five facets. It
renders no verdicts and needs no back-test, because it never decides whether
something is correct — only which of several correct things we would rather
ship. Asking it for an observable predicate is a category error; that demand
belongs to gates.

Adopted 2026-08-11 from [Tasteful software](https://wiki.g15e.com/pages/Tasteful%20software.md)
([gathered copy](../charness-artifacts/gather/2026-08-10-wiki-g15e-com-pages-tasteful-software-md-536ebc23.md)),
where taste is explicitly not innate, not finished, and kept useful only by
continual unlearning — and where its whole job is stated as choosing among many
possibilities, "which also means discarding most of them."

> **At equal capability, prefer less.**
>
> 1. At equal **capabilities** (what can be done), fewer **features** is better.
>    Capability is possibility; a feature is one shipped path to it.
> 2. At equal features, less code is better.
> 3. At equal code, a higher share of open source is better.
> 4. At equal code, declarative beats procedural.

**The precondition is the rule.** Every rung opens with *at equal —*. The rung
fires only once that equality is established, and establishing it is work, not
an assumption. On 2026-08-11 a disposition plan asserted equal capability four
times and was wrong four times: it proposed deleting a ratchet arm that was the
only detector of one-for-one substitution, a probe pin that an open operator
decision publishes its figures from, an eval spec that was the only forcer of a
gated reference, and a marker seam whose absent writer was its specification.
Each deletion *reduced* capability while reading as a tie. Taste applied before
the equality check is not taste; it is a license.

This does not contradict the count line below. Count still justifies nothing on
its own — capability does. Count only breaks ties among equals.

## Failure signatures (you are misapplying this if)

- you deleted a gate guarding an irreversible boundary and replaced it with
  nothing — that is a P5 violation, not a P1 application;
- you treated a passing advisor / gate / `CLOSED` state at an irreversible
  boundary as completion — P4 violation;
- you confirmed an irreversible closeout by re-reading the same proxy the gate
  already cited — P4 violation;
- you shortened a body to dodge the cap instead of splitting the concept — P2
  violation;
- you cited "fewer lines / fewer gates" — or, inverted, *more* code / *more*
  gates as "thoroughness" — as success; count is not the metric in either
  direction (escape-closed + concept-clearer is);
- you invoked the taste ladder without establishing the *at equal —*
  precondition it opens with, so a capability reduction read as a tie.

## Deliberately not in this document

Per-surface migration checklists, rollback refs, the diagnosis back-test against
the #359–#386 cluster, and the per-transition observable checklists are the
overhaul *plan's* job; they ship with the surfaces. This document is the
briefing, not the plan.
