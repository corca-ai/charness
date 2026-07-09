# Critique Review
Date: 2026-07-09

## Decision Under Review

Issue #427 resolution: commits `87963dab`, `9e97902f`, and `2f988fff`
change `trace_command_marker` scoring so marker fires require Bash
command-bearing evidence in both `trace-digest.jsonl` and `stream.jsonl`.
The resolution also updates `docs/prompt-mutation-policy.md` and
`docs/handoff.md`.

Goal binding: `autonomous-repo-improvement-issues`.

Packet Consumed: `charness-artifacts/critique/2026-07-09-124539-packet.md`
(prepare packet generated before doc closeout edits; code diff was supplied by
commit refs in the reviewer prompts).

## Failure Angles

- Michael Jackson / problem framing: the first two commits solved most of the
  JTBD but left stream fallback accepting any `input.command`, not only Bash.
  This was fixed in `2f988fff`, with a non-Bash stream regression test.
- Gerald Weinberg / diagnostic boundary: the first two commits split trace
  semantics from stream semantics. This was fixed in `2f988fff`; sentinel
  scoring inherits `evaluate_witness`, so no separate sentinel matcher remained.
- Shared helper naming: `prompt_mutation_bundle_lib.stream_command_blob` still
  returns broad tool input strings. Counterweight classified this as real
  cleanup debt but not a #427 blocker because survival scoring no longer imports
  that helper.

## Counterweight Pass

- Act Before Ship: none after `2f988fff`; source and plugin mirror both require
  `Bash` for stream and trace marker fires.
- Bundle Anyway: policy caveat updated so stream fallback evidence is Bash
  command-bearing only, excluding prose, non-Bash inputs, paths, patterns, task
  descriptions, and mention text.
- Over-Worry: broadening the advisory blinding scanner into execution-proof
  scoring is scope creep; it is a taint detector, not a marker-fire oracle.
- Valid but Defer: rename/split the broad `stream_command_blob` helper when a
  future consumer needs execution-proof semantics from it.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/score_prompt_mutation_survival_lib.py:133 | action: fix | note: stream fallback had to require Bash; fixed in commit 2f988fff
- F2 | bin: bundle-anyway | evidence: strong | ref: docs/prompt-mutation-policy.md:152 | action: fix | note: policy caveat updated to record Bash command-bearing marker evidence only
- F3 | bin: over-worry | evidence: moderate | ref: scripts/check_prompt_mutation_blinding.py:39 | action: document | note: advisory blinding scanner may stay broader because it is not execution-proof scoring
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/prompt_mutation_bundle_lib.py:44 | action: defer | note: helper naming remains broad cleanup debt, not a #427 close blocker

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: subagent tool accepted spawn fields; provider application not independently confirmed.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: `score_prompt_mutation_survival_lib.evaluate_witness` produces
  deterministic marker-fire verdicts.
- Consumer: prompt-mutation survival reports and sentinel scoring consume the
  verdicts to classify `DETECTED` / `NO-OBSERVED-EFFECT` / baseline validity.
- Owning surface: scoring consumer owns execution-proof semantics; broad bundle
  helpers and blinding scans may keep broader advisory extraction semantics.
- Verdict: owned-correctly
