# Issue Resolution Critique — #498, #495

Date: 2026-08-07

## Decision Under Review

Two prose corrections on shipped surfaces: the `achieve` goal template's garbled
`Routing` bullet (#498), and two claims in `docs/handoff-chunked-routing.md` naming a
call path `draft_goal_from_chunk.py` does not take (#495). No logic changed.

The bar this round had to clear is specific: **this run had already shipped one doc
correction that was itself false.** So the only question that mattered was whether the
new sentences are TRUE.

## Failure Angles

- The repaired template bullet parses but MISDESCRIBES the floor it explains — worse
  than a garbled bullet, because it reads as authoritative.
- The deleted fragment contained a clause worth restoring rather than dropping.
- The new `#495` sentences repeat the class they fix by naming another wrong path.
- The edited section contradicts itself after a partial correction.
- Existing goal artifacts carrying the garbled copy are read by something.

## Counterweight Pass

Three blockers were real and all three were the SAME class as the defect being fixed —
a claim about a call path or a record that does not exist. The two "is the repair
adequate" angles came back clean and were verified rather than assumed: the repaired
bullet matches what `goal_artifact_phase_routing.py` actually enforces (`impl`/`debug`/
`quality`/`issue` trigger, `n/a — <reason>` opt-out), and the deleted fragment held
only the retired `find-skills` call the newer sentence replaced. Leaving historical
artifacts garbled is correct: the floors parse the `Routing:` STEP LINE, not the
bullet prose, and no test reads that prose from an artifact.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: docs/handoff-chunked-routing.md:316 | action: file-issue | note: my new sentence said the guard question was "tracked separately", but #495 WAS that tracking and this change closes it — the claim would be false the moment it shipped | follow-up: https://github.com/corca-ai/charness/issues/500
- F2 | bin: act-before-ship | evidence: strong | ref: docs/handoff-chunked-routing.md:328 | action: fix | note: the Title bullet still pointed at `goal_artifact_lib._TEMPLATE`, which this path never reads (it templates from `templates/auto_draft_goal.md`), contradicting the new sentence twelve lines above
- F3 | bin: act-before-ship | evidence: strong | ref: docs/handoff-chunked-routing.md:378 | action: fix | note: the portability-headings bullet had the same wrong path and implied the achieve template is a single source that propagates; it is a COPY that can drift
- F4 | bin: bundle-anyway | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_auto_draft.py:52 | action: fix | note: the same wrong path in a docstring, and the likely ORIGIN the doc error was copied from — fixed with the reason recorded so it cannot be copied back
- F5 | bin: over-worry | evidence: moderate | ref: docs/handoff-chunked-routing.md:316 | action: document | note: "TWO goal-artifact writers" is true only under a creator reading (three more helpers write EXISTING artifacts); reworded to CREATORS, one word

## Reviewer Tier Evidence

- Requested tier: this host's typed `bounded-reviewer` subagent (read-only Read/Grep/Glob).
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing or team name (per the repo spawn-shape rule), session-model inheritance.
- Host exposure state: applied
- Application state: host-confirmed: the Agent tool was exposed, the spawn returned findings inline, and the reviewer self-reported `envelope-bound`. Per the per-host subagent split the Codex model/effort request does not apply on a Claude Code host.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepared packet was consumed; the reviewer was given an inline packet naming both fixes, the issues, and the specific "is this sentence true" questions, and read the repo directly. -->

## Boundary Ownership

- Producer: the `achieve` goal template and the `handoff` chunked-routing doc
- Consumer: every goal artifact scaffolded from the template, and any reader deciding whether a guard reaches both goal-artifact creators
- Owning surface: `achieve` (template) and `handoff` (doc + drafter docstring)
- Verdict: escalated-to-issue-spec

The cross-surface question the round surfaced — whether the second goal-artifact
CREATOR should get `upsert_goal.py`'s value guards — belongs to neither doc and was
escalated to #500 rather than folded into a prose fix. The doc now names that number
instead of an unverifiable "tracked separately", because an unnamed tracking claim is
how the original false claim survived.
