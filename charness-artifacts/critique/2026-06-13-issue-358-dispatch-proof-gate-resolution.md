# Critique Review
Date: 2026-06-13

## Decision Under Review

Resolution of corca-ai/charness#358 (falsified conversion:
`mutation-dispatch-no-base-sha-false-proof` recurred after its retro_lesson
conversion). The fix upgrades the class's durable artifact from prose to a
gate: new claim-time refusal script `scripts/check_mutation_run_proof.py`, a
loud machine-readable no-base-sha verdict in
`scripts/check_changed_line_mutation_coverage.py`, a schedule-only condition on
the mutation workflow's auto-close step (repo workflow + shipped template), the
`conversion_upgrade` ledger mechanism (schema field, recorder flag, aggregator
semantics, falsified-entry annotation), gate wiring in the quality
`mutation-testing.md` reference and the slice-closeout new-pool advisory, and
rubric/spec sync. Classification: `bug` (the converted artifact failed its
implied recurrence-prevention contract).

Framing question: what would let this class (citing a dispatch-green mutation
run as changed-line proof), and the causal-review siblings, come back.

## Failure Angles

- Recurrence/bypass: is the new gate actually in the citation path, or
  prose-reachable only (the original failure mode re-shaped)? Can it be
  satisfied misleadingly?
- Metric integrity: can `conversion_upgrade` launder recurrences, leak into
  rates, or break existing falsified-conversion invariants and pinned tests?
- Classifier correctness: does the verdict matrix match the real workflow
  (PR dry-run, dispatch full-mode-no-base, schedule-with/without-previous-run),
  manifest parsing, `gh run view` fields, CLI ergonomics?

## Counterweight Pass

- Act-before-ship (folded): the mutation workflow's "Close recovered mutation
  issue" step auto-closed on any green full-mode run including
  `workflow_dispatch` — the #358 false-proof move performed by machine,
  outside any agent claim gate. Folded: `github.event_name == 'schedule'`
  condition in `.github/workflows/mutation-tests.yml` and the shipped quality
  template.
- Act-before-ship (folded at closeout): the motivating `conversion_upgrade`
  ledger event for this class is appended in the same commit.
- Bundled (folded): gate pointer added to the slice-closeout new-pool
  advisory (`scripts/slice_closeout_advisories.py`), next to the coverage
  self-check it already names.
- Bundled (folded): anti-laundering operational rule added to the rubric
  (`docs/product-success-metrics.md`) and spec: an actual recurrence is
  recorded as a plain event first; the upgrade never substitutes for it.
- Bundled (folded): `record_rca_event.py --conversion-upgrade` now refuses a
  missing `--ref` (the ref is the upgrade's idempotency identity; a ref-less
  second upgrade would silently drop as a duplicate), with a test.
- Over-worry (not folded): facts-mode trust hardening (tying `--base-sha` to
  the cited run, requiring conclusion for score claims, forensic
  cross-checks). A claim gate is a checklist the agent runs against facts it
  asserts, not a forensics system; deliberate fabrication defeats any local
  script and is outside the JTBD.
- Over-worry (not folded): exit-code split for diagnostics vs refusal, and a
  machine consumer for the new `changed_line_proof` payload bit — no consumer
  branches on these today; both exit-1 paths mean "do not cite".
- Over-worry (not folded): an upgrade for a never-converted class mints a
  conversion stamp — direction is conservative (a later recurrence trips
  rather than hides).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: .github/workflows/mutation-tests.yml; skills/public/quality/scripts/templates/mutation-tests.yml | action: fix | note: schedule-only auto-close — folded this session.
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/metrics/rca-ledger.jsonl | action: fix | note: append the `conversion_upgrade` event for this class in the closeout commit — folded.
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/slice_closeout_advisories.py; docs/product-success-metrics.md; scripts/record_rca_event.py | action: fix | note: advisory gate pointer, anti-laundering rule, ref-required upgrade — all folded.
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_mutation_run_proof.py | action: document | note: run-id mode on a genuine schedule run refuses with the dispatch class key because base_sha is unknowable from run metadata; fails closed, so the class cannot recur through it. Smallest follow-up: a distinct refusal reason (no class-key attribution) for non-dispatch events in run-id mode, directing to --sample-manifest.
- F5 | bin: valid-but-defer | evidence: moderate | ref: skills/public/issue (generic), scripts/slice_closeout_advisories.py | action: document | note: deeper citation-path wiring (an advisory that fires specifically when a mutation auto-issue is being closed) stays deferred; the advisory + reference + machine-close fix cover the observed recurrence paths.
- F6 | bin: over-worry | evidence: strong | ref: scripts/check_mutation_run_proof.py | action: defer | note: facts-mode forensics, exit-code split, payload-bit consumer — raised and rejected, recorded above.

## Deliberately Not Doing

- No forensic binding of hand-supplied facts to a concrete run; the gate's
  threat model is honest-agent claim-time error, not deliberate deception.
- No structural detector for upgrade-laundering; the recorder cannot know
  about an unrecorded recurrence. The rubric rule plus the tripwire's
  detection of the *next* recurrence is the honest guard.

## Reviewer Tier Evidence

- Requested tier: high-leverage (issue-closeout review class).
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium,
  service_tier=priority (from `.agents/critique-adapter.yaml`).
- Host exposure state: host-defaulted
- Host exposure note: the Claude Code host has no gpt-5.5 reviewer surface;
  the tier resolved to the host's default strong reviewer model and the
  requested fields were not sent.
- Application state: host-defaulted, not applied (no host confirmation of the
  requested fields).

## Execution

- Execution: completed via bounded fresh-eye subagents.
- Fresh-Eye Satisfaction: parent-delegated (3 angle reviewers + 1 separate
  counterweight reviewer; causal review ran earlier as its own
  parent-delegated subagent).
- Packet Consumed: charness-artifacts/critique/2026-06-12-161102-packet.md

## Next Move

Append the ledger upgrade event, run the locked producer closeout, commit with
`Close #358`, push, verify GitHub state CLOSED, then cut the release.
