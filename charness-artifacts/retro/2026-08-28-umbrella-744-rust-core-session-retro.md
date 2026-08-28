# Session Retro — umbrella #744: Rust core spike, topology core, distribution

Date: 2026-08-28

## Context

One session drove umbrella #744 from a standing start through three closed
children: #745 (spike, ratified go), #746 (typed topology core), #747
(native distribution, typed-disposition close), plus #753 filed (test-corpus
pruning, next session) and the standing gate battery brought from
32-failures-then-8 to 78/0. Operating shape was operator-mandated:
investigation via sonnet dynamic workflows, implementation via Codex xhigh
lanes, opus bounded reviewers for plan critique; the parent owned design,
adversarial verification, and integration only. What matters next: #748
(first validator-family migration, wired to `classify`) and #753, both
picking up after compaction from the plan/evidence records under
`charness-artifacts/design-studies/`.

## Window

`533f24dad..` (the local v8.0.0 prep head) through the #746/#747 closeouts —
roughly 30 parent commits, 10 Codex lanes, 2 dynamic workflows, 7 bounded
reviewers, all local (nothing pushed).

## Evidence Summary

Task-run receipts under the external runtime root; plan revisions and
critique records in `charness-artifacts/design-studies/` and
`charness-artifacts/critique/2026-08-28-*`; parity/bench JSON and the
parity ledger under `design-studies/issue-745/`; evidence records under
`design-studies/issue-746-747/`; the retro prepare packet
(2026-08-28-095036, clean tree, no owning-surface deltas); quality failure
logs from the two full-battery runs. Narrative claims below cite those;
no adapter metrics command was run beyond the packet.

## Waste

- **Focused-only lane verification.** Every lane ran only its named
  checks; the first full battery then surfaced 32 standing regressions and
  8 full-only gate failures, costing a dedicated repair lane plus a parent
  repair pass. The proof floor existed — it was just run too late.
- **Serial pytest, twice.** The parent invoked bare `python3 -m pytest`
  (~14.5 min) instead of the canonical xdist runner
  (`scripts/run_standing_pytest.py`, ~86 s), and baked the same serial
  command into the repair-lane brief, spending lane wall-time on it too.
- **Parent-authored format misses.** A multi-line YAML checklist entry
  broke the line-based adapter readers (8 cascade failures); six critique
  records were written without the repo's required tier/boundary floor
  blocks and had to be rewritten against the validator grammar.
- **Model-policy miss.** Two bounded reviewers were spawned without a
  model override and silently inherited the parent model (Fable) against
  the operator's sonnet/opus-only intent.
- **Lane scope omissions.** The 747-install scope list omitted the two
  repo-root shims its own brief ordered edited (candidate invalidated,
  manual integration), and the 747-artifact lane could not write
  `.agents/` (parent had to apply the adapter wiring).
- **Workflow structured-output placeholders.** Three of five schema-forced
  workflow agents returned literal "test" dummies; the reruns as
  final-message-report agents all succeeded.
- Not waste: the broad five-agent investigation sweeps and the four-angle
  opus critique were exploration/verification phases that directly removed
  six plan blockers before any lane launched.

## Critical Decisions

- Ratifying the amended #745 3x criterion on structural grounds (operator
  sign-off, recorded in the verdict) instead of a sunk-cost no-go or a
  silent relaxation.
- Cutting `what_reads_this` CLI parity, the rollback subcommand, the
  crate-version sync, and `--version` — each removed a whole failure
  family the reviews had identified.
- The `native_core` declaration switch: landing distribution fully inert
  decoupled lane F from release timing and kept every existing install
  test network-free.
- Fixing the exit-class collision (3 = unestablished) before any lane
  wrote code.
- Treating pre-existing gate debt as in-scope on operator instruction and
  clearing all eight failures rather than fencing them off.

## Trends vs Last Retro

2026-08-22's retro closed on proof cost and cadence for a release that
kept returning `unproven`. This session's analogue improved: every closed
child carried parent-executed proof in the integrated tree, and the one
criterion that could not be met literally (3x on a fixed-cost comparison)
was renegotiated explicitly rather than re-run until green. The recurring
line both retros share: verification that exists but runs later than the
work it should have gated.

## North Star Alignment

The session moved the repo toward the design north star's single-owner
principle concretely: one typed graph now owns derivable topology, with
duplicated projections scheduled for deletion (#748) rather than layered
over. The deletion-over-layering preference was exercised for real (gate
pins declared stale were deleted; ceremony was not re-added). The main
tension surfaced honestly: the meta-verification layer itself is now the
largest unowned cost center (#753).

## Expert Counterfactuals

- **Engelbart (system-improving-itself):** the session used H+LAM well but
  designed T reactively — every lane brief was written fresh, and three of
  the misses (scope omission, serial pytest, single-line YAML) were
  T-knowledge the system already had in scattered form. The improvement
  loop closed only at the end (claude-host.md). Counterfactual: treat the
  lane brief itself as a versioned instrument — a checked-in brief
  template that carries the scope-must-cover-instructed-paths rule, the
  canonical verification commands, and the format constraints — so each
  lane inherits the last lane's lessons structurally, not through the
  orchestrator's memory.
- **Charity Majors (operate what you ship):** the standing battery is
  production for this repo; a change is not integrated until the full
  battery says so. Counterfactual: run `run-quality.sh --full` after the
  FIRST production-surface integration (747-F), not after five — the 32
  regressions would have arrived in two digestible waves, each attributable
  to one lane.

## Next Improvements

- workflow: after integrating any lane that touches production surfaces,
  run the full battery before launching the next dependent lane; keep
  focused checks for `native/**`-only lanes.
- workflow: lane briefs must name the canonical runners
  (`run_standing_pytest.py`, `run-quality.sh` labels) instead of raw tool
  invocations.
- capability: a lane-brief template (checked in beside the host notes)
  carrying the standing constraints: scope covers every instructed path,
  single-line adapter entries, canonical runners, no-descendant-agents,
  result shape. (Candidate for #748 prep.)
- capability: prefer final-message-report subagents over schema-forced
  StructuredOutput for prose-shaped investigation results; keep schemas
  for genuinely tabular returns.
- memory: `.agents/claude-host.md` (written this session) carries the
  model policy and the three paid-for lane lessons; this retro is the
  durable narrative record; #753 carries the test-corpus measurements so
  they are never re-measured.

## Sibling Search

Transferable pattern: "parent-authored artifacts must satisfy repo
validator grammars the parent has not read" (adapter YAML entries,
critique records). Scan: the other hand-edited `.agents/*-adapter.yaml`
entries were already single-line (checked during the fix); the six
2026-08-28 critique records were all rewritten against the validator in
one pass; no other parent-authored artifact classes were produced this
session. Decision: fixed-in-place; follow-up identifier: none needed —
the lane-brief/host-notes capability above is the structural carrier.

## Portable Candidate

not portable — the misses are bindings to this repo's specific validator
grammars and runner topology; the abstract lesson ("run the owning repo's
canonical runner, not the underlying tool") is already the consuming
hosts' documented default.

## Packet Consumed

2026-08-28-095036 packet: clean working tree, no owning-surface deltas —
consistent with an all-committed closeout point; it constrained nothing
further.
