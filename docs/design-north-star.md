# Charness Design North Star

**One idea: the harness briefs a capable judge, and keeps teeth only where a
wrong answer escapes.** Equip judgment; fence only cliffs.

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
state writes (Slack / Notion / provider / apply-to-prod), and deletions.
(Reopenable ≠ reversible: a reopened issue was already read as "done".)

## Operating stance

Serve the goal first. When a *reversible* surface fights the goal, fix the
system even at the cost of speed. Irreversible-boundary safeguards are not
"friction to fix" — they are the goal at the boundary. When goal and system
genuinely conflict and the call is unclear, ask.

## Failure signatures (you are misapplying this if)

- you deleted a gate guarding an irreversible boundary and replaced it with
  nothing — that is a P5 violation, not a P1 application;
- you treated a passing advisor / gate / `CLOSED` state at an irreversible
  boundary as completion — P4 violation;
- you confirmed an irreversible closeout by re-reading the same proxy the gate
  already cited — P4 violation;
- you shortened a body to dodge the cap instead of splitting the concept — P2
  violation;
- you cited "fewer lines / fewer gates" as success — count is not a metric.

## Deliberately not in this document

Per-surface migration checklists, rollback refs, the diagnosis back-test against
the #359–#386 cluster, and the per-transition observable checklists are the
overhaul *plan's* job; they ship with the surfaces. This document is the
briefing, not the plan.
