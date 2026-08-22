# Critique Review

Date: 2026-08-23

## Decision Under Review

Publishing charness `6.3.0` → `6.4.0` (minor): four gates that now name their
uncovered set as a number, a position-independent consumer-validator discovery
predicate, and mutation summaries that report `UNMEASURED` where nothing was
scored. Four of the changed files install into consuming repos through the
`quality` skill.

## Failure Angles

- Consumer blast radius: a changed refusal or exit code in the dup ratchet would
  turn a consuming repo's CI red, or worse, silently green.
- New required config: a previously-optional adapter key becoming mandatory, or a
  previously-tolerated adapter shape now failing, breaks consumers on upgrade.
- Payload contract: consumers may parse these gates' YAML; a removed key or a
  changed meaning breaks them, while additive keys do not.
- `UNMEASURED` is a THIRD value in a field that held `PASS`/`FAIL`. Anything
  matching those two exhaustively sees a new value.
- Bump level: most of this delta is repair, which argues `patch`; new exported
  functions on a consumer-installed module argue `minor`.
- Shipping over known-open items: the mutation lane has not been observed green
  on CI since its repair, and a live unallowlisted cross-namespace mention exists
  in the tree that the ownership gate reports `ok` over.

## Counterweight Pass

Real, and folded before shipping: the `inert` / `adapter-invalid` early-return
paths published `did_not_judge: []` — an empty "what I did not judge" over a gate
that judged nothing, on the default state of every repo still working through the
documented adoption procedure. Fixed to withhold, matching the two sibling gates
in this same release. Verified by planting the pre-fix defaulting and observing
`did_not_judge: []` return.

Real, and recorded rather than fixed: the `grep 'Status: **FAIL**'` red→green
class, the pinned-catalog `CatalogError`, the `int | str` union on
`link_only_lines_slack`, and the fourth `UNMEASURED` transition
(`reachable == 0` precedes `exec_timed_out`, so a timed-out run with nothing
scored moves from `FAIL-incomplete`). Each belongs in the release notes.

Over-worry, checked and dismissed on evidence rather than judgement: the
empty-`scope_paths` degrade is NOT new — it is present at the `v6.3.0` tag, so
the feared silent red→green on that path does not exist. The catalog widening
adds no consumer obligation: every `consumer_facing: true` entry was already
discoverable under the old prefix predicate, so no adoption file needs an edit.
No key was removed from `summarize()`; the diff against the tag is three
additions.

Correction the critique forced on a record I had already filed: issue #703's
first item overstated its trigger. The ownership gate IS wired, as a surface
`verify_command` in `.agents/surfaces.json`; what holds is only that it is absent
from `run-quality.sh`'s broad lane. Corrected on the issue.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/check_dup_ratchet.py | action: fix | note: inert and adapter-invalid paths published did_not_judge as an empty list over a gate that judged nothing; withheld instead, matching the sibling gates
- F2 | bin: bundle-anyway | evidence: strong | ref: scripts/check_mutation_score.py | action: document | note: an external CI grep for `Status: **FAIL**` on a baseline abort now goes green; exit code is unchanged and the surface is documented non-portable, so this is a release-note item rather than a major bump
- F3 | bin: bundle-anyway | evidence: moderate | ref: skills/public/quality/references/consumer-validator-catalog.yaml | action: document | note: a consumer pinning the 6.3.0 catalog against a 6.4.0 checker gets a hard CatalogError from the candidate_patterns equality check
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_docs_graph.py | action: file-issue | note: link_only_lines_slack is typed int-or-str and returns a sentence on the not-computable path, which is a parser trap for any consumer reading the field | follow-up: deferred handoff-anchor release-6-4-0-open-risks
- F5 | bin: over-worry | evidence: strong | ref: skills/public/quality/scripts/check_dup_ratchet.py | action: defer | note: the feared silent red-green from an empty scope_paths does not exist; that degrade predates v6.3.0 and was verified against the tag

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (read-only; Read/Grep/Glob only)
- Requested spawn fields: subagent_type bounded-reviewer, unnamed one-shot spawn, release-critique packet naming the shipped surfaces, the six failure angles, and the known-open items
- Host exposure state: applied
- Application state: host-confirmed: the reviewer returned a verdict and reported its own envelope as bound, seeing only Read/Grep/Glob with no Bash, Edit, Write, or Agent tool
- Delivery state: findings-received
- Worker report: n/a
- Worker report identity: n/a
- Worker report approval: n/a
- Worker report delivery: n/a
- Worker report packet identity: n/a
- Worker report input identity: n/a
- Worker report parent receipt identity: n/a
- Worker report findings identity: n/a

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewer was given an inline
release packet naming the shipped surfaces, the substance of the change, and the
known-open items. The reviewed tree is the pushed commit `907e190b5`. -->

## Boundary Ownership

- Producer: the four gates themselves, each computing its own uncovered-set count from its own scan
- Consumer: a maintainer or consuming repo reading the gate's YAML payload or its phase log
- Owning surface: each gate that owns the list; no surface reads another gate's verdict
- Verdict: owned-correctly
