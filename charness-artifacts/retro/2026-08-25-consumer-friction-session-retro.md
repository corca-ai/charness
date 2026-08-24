# Consumer Friction Structural Closeout Retro
Date: 2026-08-25

## Context

This retro covers the Charness/Ceal consumer-friction work from issue #713
through the #689 requalification, #690/#691 readiness repair, #714 Node TAP
window repair, and the external-worker capability envelope. It also covers the
user correction that a sandbox-local `gh auth status` message cannot establish
invalid credentials when the same credentials continue to work elsewhere.

## Window

From the initial 2026-08-24 consumer-friction design through the fresh
`run-quality.sh --read-only` result on 2026-08-25 and its four structural
repairs. Publication, issue closure, push, release, and Cautilus are outside the
window.

## Evidence Summary

- Ceal's real Node TAP suite passed 27/27; the installed Charness mutation
  roundtrip killed the selected mutation and restored the source exactly.
- The final pre-repair changed-line run passed 11,349 standing tests and reported
  no blocking line for the then-committed range.
- The subsequent broad quality run passed 94 checks and retained four failures:
  three malformed debug interrupt records hidden behind the first error, two
  unclaimed lesson sessions, one uncovered loader refusal, and four duplicate
  fingerprints.
- Focused repairs now pass 99 achieve/reporter tests, 5 debug-index tests, the
  regenerated seam index, and the duplicate ratchet with zero new families.
- Closeout telemetry was read from this repo only. It reports recurring standing
  test runtime and over-slice cost, but does not establish whether those costs are
  justified or describe any consumer repo.

## Packet Consumed

The deterministic prepare packet at
`charness-artifacts/retro/2026-08-24-151441-packet.md` was read. It established
the changed files and owning surfaces; it did not establish release readiness or
a reviewer verdict.

## Waste

The largest trust loss came from accepting a provider-facing phrase before
establishing the observation channel. A read-only worker lacked network access;
its `gh` output was initially summarized as invalid authentication even though
parent and network-capable controls worked with unchanged credentials. The
direct pattern is transport/auth conflation. The higher-order pattern is that
producer version, capability, scope, attempt, and lifecycle identity were not
bound to the consumer that rendered the verdict.

The first broad quality failure also exposed a reporting defect: the seam-index
builder stopped at the first malformed artifact, so one lowercase field hid two
additional enum/handoff violations. Fixing only the named line would have
required repeated unchanged gate runs. The repair now collects every malformed
artifact into one path-bound diagnostic batch.

The duplicate gate separated actual repetition from fingerprint churn. The
same-file Node match collection was factored once. Three portable bootstrap or
cross-package parser families were linked to their prior reviewed rationale
under their new fingerprints instead of distorting package boundaries to chase
a hash.

## Critical Decisions

- Treat `gh auth status` as application text whose credential meaning is valid
  only after same-attempt transport evidence. This led to the typed capability
  envelope instead of an authentication retry.
- Keep #689's direct Node health control separate from wrapper accounting and
  factor the newly exposed run-window defect into #714.
- Refuse terminal, hollow, and duplicate-section goal artifacts at one shared
  readiness producer, while preserving Ceal host activation as a non-claim.
- Run changed-line proof before broad quality, then treat every new failure from
  the broader observer as a new stimulus requiring repair and fresh proof.
- Record both lesson receipts as `presentation-unproven`; emission and subsequent
  commits do not prove the lessons were presented or used.

## North Star Alignment

The work held the north star where the direct Node control, installed wrapper
roundtrip, changed-line producer, and broad quality run observed different
boundaries through different evidence channels. It violated the same standard
when a provider string stood in for a transport observation and when a fail-fast
index message concealed sibling defects. The repairs move teeth to the escape
points: typed capability state before worker launch, complete-run ownership
before mutation accounting, lifecycle-aware readiness before activation, and
batched path-bound diagnostics before index acceptance.

## Trends vs Last Retro

The recent-lessons digest already warned that green tests are not covered lines,
unsupported command forms are not proof, and bars encoded as prose drift. This
window followed the changed-line ordering but still reproduced the broader class
at other boundaries: a provider phrase was treated as a capability verdict, and
hand-authored debug records drifted from executable field grammar. The trend is
not missing prose; it is insufficient end-to-end identity and scaffold use.

## Expert Counterfactuals

- Engelbart's system-improving lens would treat the worker tool, the
  capability vocabulary, and the operating method as one system. It would have
  introduced the transport/auth/effect axes before sending the first external
  worker, rather than repairing the worker's interpretation afterward.
- An evidence-auditor lens would ask, for every verdict, which observer saw
  which attempt and which immutable input. That question would have rejected the
  auth claim, the incomplete TAP candidate, and the unclaimed lesson scores at
  their respective boundaries.

## Sibling Search

- axis: provider/host output interpreted without its capability axis | decision:
  fixed in this slice | proof: typed request/effective/preflight/receipt fields
  now bind transport, identity, authorization, filesystem, and effects |
  follow-up: #715 owns installed adoption
- axis: worker-created ambient coordination state | decision: valid follow-up
  outside the slice | proof: two valid lesson receipts had no owning retro and
  the continuity gate reported both | follow-up: issue #716
- axis: fail-fast corpus validators hiding sibling violations | decision: fixed
  in this slice | proof: a two-invalid-artifact fixture now requires both paths
  and both reasons in one diagnostic | follow-up: none
- axis: fingerprint identity churn losing prior duplicate judgment | decision:
  valid follow-up outside the slice | proof: three already-reviewed families
  reappeared only under new content fingerprints | follow-up: issue #720

## Portable Candidate

- Abstract pattern: bind producer version, capability, scope, attempt, and
  lifecycle identity through the final consumer; retry creates a new record and
  never rewrites the failed one.
- Triggering evidence: the auth/network misclassification, unframed Ceal grep
  records, generated worktree-link noise, and worker lesson-session conflicts.
- Intended consumer shape: repos that delegate bounded work to external model
  CLIs or host workers.
- Destination: create-skill, after installed adoption and Ceal acceptance prove
  the envelope outside this authoring checkout.
- First-prompt acceptance claim: a remote-read task with denied writes/effects
  either launches with same-attempt ready evidence or stops with a typed
  capability non-claim.

## Lesson Evaluation

The receipt proves the list was emitted, and this logical session continued the
work, but the durable repo evidence does not prove the list was presented before
the affected decisions. No scores are appended. `no-effect` would be an equally
unsupported affirmative judgment.

Lesson evaluation: {"reason":"presentation-unproven","score_event_count":0,"session_id":"27605bc2-5cff-4ca0-a1e9-563dee69e9ba","status":"not-evaluated"}

## Next Improvements

- workflow: keep `mutate -> sync -> focused proof -> changed-line proof -> broad
  quality`; any repair after broad quality creates a new proof range rather than
  inheriting the earlier green.
- capability: issue #716 (recurs: session-opened-never-closed) must make one
  parent own lesson state and make workers inherit an immutable session or run
  with lesson writes disabled.
- capability: issue #721 (recurs: debug-artifact-scaffold-shape-guess) must bind
  the debug producer to targeted validation before broad corpus quality.
- memory: recurrence-class: boundary-identity-unbound — a producer's output,
  version, capability, scope, attempt, and lifecycle identity must remain bound
  through the final consumer.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-25-consumer-friction-session-retro.md
