# Critique Review
Date: 2026-07-23

## Decision Under Review

Resolve #452 by adding a "Named Option Semantics" baseline to
`skills/public/create-cli/references/command-conventions.md` (named options
are order-independent by default, distinguished from positional arguments
and option values, with required duplicate/unknown/missing-value rejection,
and a pointer to testing the parser contract over enumerating permutations),
plus a cross-reference bullet in `skills/public/create-cli/references/quality-gates.md`.
Doc-only change; checked-in plugin mirror and two related `SKILL.md` digest
lines synced.

## Failure Angles

- Michael Jackson (problem framing): does the new section solve the
  reported gap without scope creep into prescribing a parser library?
- Barbara Minto (structure/communication): is the new section legible and
  correctly placed for a reader with no chat context?
- Atul Gawande (checklist/operational): is the new rule checkable rather
  than aspirational prose, and is doc-only scoping appropriate?

## Counterweight Pass

- Act Before Ship: none.
- Bundle Anyway: the "Quality review should ask" checklist in
  `quality-gates.md` did not mirror the new gate bullet — fixed in the final
  diff. `SKILL.md`'s two digest references to `command-conventions.md` and
  `quality-gates.md` were also stale relative to the new content — fixed in
  the final diff.
- Over-Worry: demanding an automated enforcement check now (issue's own
  "Desired outcome" explicitly scopes this to a documented baseline, leaving
  helper API/test technique to the consuming repo); a claim that this
  doc-only change is insufficient because "nobody enforces it" (the doc sits
  alongside an already-identical-shaped, already-accepted unenforced pattern
  in the same file); a claim that skipping the resolution-brief pause was
  risky (additive prose, no open decision, no behavior change).
- Valid but Defer: the real consumer CLI (`ceal call`) that motivated this
  issue still has its positional-order parser bug — fixing that external
  repo is out of scope for this issue.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/public/create-cli/references/command-conventions.md:40 | action: fix | note: register inconsistency — issue asked to "require" rejection but doc said parser "should" reject, softer than the "must" used elsewhere on the same page; changed to "must"
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/create-cli/references/command-conventions.md:53 | action: fix | note: "Read-only probe surface:" lacked its own heading, so it visually nested under the new "## Named Option Semantics" heading (MECE violation); promoted to its own "## Read-only Probe Surface" heading
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/create-cli/references/quality-gates.md:63-67 | action: fix | note: "Quality review should ask" checklist did not mirror the new gate-list bullet; added a matching question
- F4 | bin: bundle-anyway | evidence: moderate | ref: skills/public/create-cli/SKILL.md:49,128 | action: fix | note: SKILL.md's digest references to command-conventions.md and quality-gates.md went stale relative to the new content; updated both pointers
- F5 | bin: over-worry | evidence: weak | ref: skills/public/create-cli/references/command-conventions.md:27-30 | action: defer | note: the "documented product reason" / "explicitly documents" escape hatches have no specified documentation location or adjudicator, but this mirrors an already-accepted pattern earlier in the same file (line 20-21) rather than a new gap introduced by this change
- F6 | bin: valid-but-defer | evidence: moderate | ref: n/a (external repo) | action: document | note: the real consumer CLI's positional-order parser bug that motivated this issue is unfixed; out of scope for this doc-only slice

## Reviewer Tier Evidence

- Requested tier: high-leverage (angles) / high-leverage (counterweight).
- Requested spawn fields: session-model inheritance (Claude Code host; the
  repo's Codex-only override fields do not apply on this host).
- Host exposure state: host-defaulted
- Application state: host-confirmed: bounded-reviewer subagent spawned via
  the Agent tool with Read/Grep/Glob-only envelope for all four reviewers.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

n/a (no adapter `packet_sections` declared; reviewers were pointed at the
live source tree directly).

## Boundary Ownership

- Producer: `skills/public/create-cli/references/command-conventions.md`
  and `quality-gates.md` (canonical skill-authoring guidance).
- Consumer: any repo (including this one) creating or reviewing a
  repo-owned CLI, plus the checked-in `plugins/charness/` mirror for
  installed consumers.
- Owning surface: the `create-cli` skill's reference docs plus their
  generated plugin mirror.
- Verdict: single-surface

## Deliberately Not Doing

- Not prescribing a specific parser library/helper API or test technique —
  the issue explicitly leaves that to the consuming repo.
- Not adding a new automated gate/script that checks any CLI's parser
  actually satisfies this baseline — out of scope per the issue's own
  "Desired outcome," which asked only for a documented baseline.
- Not fixing the real external consumer CLI (`ceal call`) that motivated
  this issue (F6) — a separate repo, separate slice.
