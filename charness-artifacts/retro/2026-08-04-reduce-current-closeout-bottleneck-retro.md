# Reduce current closeout bottleneck — session retro
Date: 2026-08-04
Goal: charness-artifacts/goals/2026-08-04-reduce-current-closeout-bottleneck.md

## Context

This retro covers the current-host closeout optimization experiment: baseline
selection, a focused changed-line coverage worker-cap candidate, its matched
falsification, final local proof, and the no-safe-change disposition. The goal
was to reduce elapsed time without weakening a proof surface. Measured command
results are strong; host-wide token and tool totals are unavailable.

## Window

The window runs from goal activation commit `e1f0f88b` through the final quality
gate at the committed no-change state `ab0e4ad8`. It includes Slice A baseline,
Slice B matched timing, candidate critique, and final closeout evidence.

## Evidence Summary

- The goal artifact records three full `run-quality.sh --read-only` baselines
  at 122.35s, 122.71s, and 123.33s, with the focused changed-line mutation
  phase at 119.1s, 119.3s, and 120.1s; all three had 85 passed and 0 failed.
- Six matched focused producer runs kept base SHA `827a77f`, the same four
  changed pool files, mapped corpus, host, and clean consumer verdict. Uncapped
  mean was 114.70s; cap-4 mean was 114.81s. The fixed 5s threshold was not met.
- The separate producer/consumer correctness channel passed 43 tests in 4.68s.
  The final local quality gate passed 85 checks with 0 failures in 122.7s;
  its changed-line phase was 119.6s.
- The candidate critique at
  `charness-artifacts/critique/2026-08-04-reduce-closeout-bottleneck-worker-cap-candidate-critique.md`
  contains three delegated read-only findings and clean worktree-boundary
  verifies. The retro prepare packet was
  `charness-artifacts/retro/2026-08-04-120755-packet.md`.
- Closeout telemetry was read from the local stream only: 1,345 records,
  including recurring historical gate-runtime and over-slice signals. Those
  signals selected the area but do not prove current relief or permission to
  weaken proof.

## Waste

- `candidate-protocol-rework` — the first critique artifact used the packet's
  markdown path while carrying the JSON digest, so the binding validator caught
  the mismatch. This was necessary recovery at a proof boundary; the avoidable
  waste was not copying the canonical JSON packet path from the prepare-packet
  contract on the first draft. The artifact was repaired and validated before
  commit.
- `gate-baseline-runtime` — the final gate still costs 122.7s and the focused
  coverage phase 119.6s. This is measured quality debt, not a reason to weaken
  floors or shrink proof. The worker-cap candidate produced no material saving;
  D51 remains the named owner/reopen anchor for a future safe optimization.
- `safety-cost` — the three baseline runs, six matched candidate runs, separate
  correctness tests, delegated critique, and final quality gate were necessary
  safety cost for a proof-adjacent timing experiment, not reducible waste.
- Host metric window and per-goal token/tool/turn totals were unavailable; no
  waste conclusion is inferred from cached input or broad transcript shape.

## Critical Decisions

- Selected the focused changed-line coverage producer because it dominated the
  current serial quality path while the standalone 7,087-test path was much
  shorter; kept the proof question fixed.
- Fixed a 5s materiality threshold before the intervention and required three
  comparable samples per side. The cap was 0.11s slower on mean, so no code or
  runner change shipped.
- Kept the global standing runner, xdist/no-xdist fallback, mapped corpus,
  coverage export, success marker, consumer verdict, and separate correctness
  channel unchanged.
- Treated the passing final gate as evidence, not terminal completion; the
  closeout still requires this durable retro and a distinct claims review.

## Trends vs Last Retro

The most recent durable retro is for a different goal and has no comparable
goal-scoped host metric window. Qualitatively, this run repeats the positive
pattern of preserving a gate when a speed candidate fails its falsifier. It also
repeats the known need to bind evidence to the exact artifact and command shape.

## North Star Alignment

- P1 held: this reversible local experiment used judgment and measurement rather
  than adding a new permanent gate or weakening an existing one.
- P4/P5 held at the proof-surface boundary: timing, correctness, delegated
  review, and final quality were separate evidence channels; no green run was
  treated as permission to change the gate.
- The run avoided the named failure signature “terminal green is not proof” by
  retaining the pre-change behavior after the cap failed its materiality test.
- The one process miss was packet-path copying, not semantic proof loss; the
  binding validator exposed it before the artifact was committed.

## Expert Counterfactuals

- An Ousterhout lens would have made the producer/consumer boundary and the
  focused-only worker option explicit in the first candidate packet. That would
  have prevented the initial packet-path mismatch and made the global-runner
  non-goal immediately executable.
- A Klein/Kahneman decision-quality lens would have locked the 5s threshold and
  matched sample protocol before looking at cap timings. The actual run did so;
  the useful counterfactual is to keep this precommitment as the default for
  future runtime experiments rather than letting a single fast observation
  create optimism.

## Sibling Search

- same layer: focused changed-line producer, mutation coverage exporter, and
  changed-line consumer | decision: valid follow-up outside the slice | proof:
  same command, corpus, marker, and consumer invariants were inspected and
  preserved; follow-up: deferred docs/deferred-decisions.md#d51
- abstraction up: quality routing and the local closeout contract | decision:
  intentional boundary | proof: the goal keeps CI relocation, release changes,
  and cross-host promises outside scope.
- specialization down: `run_standing_pytest.py` worker selection and xdist
  fallback | decision: diagnostic-only | proof: three delegated reviewers and
  the focused correctness channel found no current repair to ship.
- mental-model siblings: global worker defaults, broad coverage replacement,
  cache reuse, and standing-suite pruning | decision: valid follow-up outside
  the slice | proof: each would change proof scope or command shape; follow-up:
  deferred docs/deferred-decisions.md#d51

## Next Improvements

- workflow: Keep the fixed-threshold, matched-sample, separate-correctness
  protocol for future closeout timing candidates; this was applied to the goal
  and candidate critique in this run.
- capability: If a future candidate exceeds 5s relief, add only a focused
  producer-owned option subordinate to xdist detection, with regression checks;
  no current implementation is justified.
- memory: Preserve the no-safe-change result, exact reopen trigger, and packet
  identity in the goal/retro artifacts so a future session does not retry the
  falsified global-cap intuition.

## Packet Consumed

Packet Consumed: `charness-artifacts/retro/2026-08-04-120755-packet.md`

## Host Metrics

Host metric window: absent. The host-log probe is not exposed for this goal, so
per-goal token, turn, tool, and cost totals remain unavailable. Explicit local
command timing is the measured efficiency evidence.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-04-reduce-current-closeout-bottleneck-retro.md
