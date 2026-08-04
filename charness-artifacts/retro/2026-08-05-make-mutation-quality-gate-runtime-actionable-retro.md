# Make mutation quality gate runtime actionable — session retro
Date: 2026-08-05
Goal: make-mutation-quality-gate-runtime-actionable

## Context

This retro reviews the completed implementation slice that moved focused
changed-line mutation coverage onto the canonical standing pytest runner. The
goal mattered because the mutation producer was the measured local closeout
critical path, while its wrapper duplicated runner policy. Strong evidence is
the six matched local quality receipts, the committed gate result, and the
focused worker-coverage test. Host-session token/cost evidence is unavailable;
those claims are intentionally not made.

Packet Consumed: charness-artifacts/retro/2026-08-04-200900-packet.md

## Window

From activation and the pre-change baseline through implementation commit
`3c241399`, post-change receipts, claims review, and closeout preparation.

## Evidence Summary

- Three baseline `./scripts/run-quality.sh --read-only` runs passed 85/0;
  median total 123.96s and mutation 120.6s.
- The matched post-change three runs passed 85/0; median total 79.97s and
  mutation 76.8s, a measured 43.99s and 43.8s median relief respectively.
- The committed direct mutation gate passed 5/5 changed-pool files in 50.37s;
  the dirty pre-commit attempt correctly remained unestablished.
- Candidate critique, delivery, boundary, and final claims artifacts are
  persisted under `charness-artifacts/critique/`.
- The local closeout-telemetry miner found recurring historical over-budget
  broad-test entries; it reads this repo's stream only and cannot prove host
  identity, exit status, or cross-repo cost.

## Waste

- Gate-baseline runtime (strong, measured): the focused mutation phase still
  costs 76.8s median after the repair. The old 120.6s median was not necessary
  safety cost; it was duplicated scheduling policy in the producer. The
  remaining cost is proof-bearing work and stays routed to #505, not removed.
- Verification (strong, necessary): three-before/three-after receipts, the
  worker-level coverage probe, and the dirty-tree non-claim prevented a fast
  but false conclusion. They are not treated as waste.
- Rework (strong): the first worker probe asserted an xdist output banner that
  quiet mode did not promise, and the first claims review cited a prepare packet
  as completed review evidence. Both were repaired by observable worker files
  and durable review records before closeout.
- Closeout orchestration (moderate): two claims-review attempts had to be
  repeated because the boundary and delivery evidence was not persisted before
  citation. The next closeout should create those records immediately after
  each returned review and before updating the goal.
- The telemetry recurrence is broader than this slice. Existing open #505 is
  the structural destination; no new issue is filed for the same runtime class.

## Critical Decisions

- Chose the canonical standing runner as the execution-policy owner. The
  producer remains the selector and artifact bridge; `run_standing_pytest.py`
  owns xdist compatibility, worker limits, scheduling, affinity, and temp
  isolation.
- Preserved the exact mapped test targets and made `--include-release-only`
  explicit, because the wrapper's old scope otherwise changed under the
  runner's default marker policy.
- Rejected hand-assembled `-n` flags and target pruning. The candidate had to
  preserve changed-line mapping, subprocess coverage, failure visibility,
  focused artifact output, and consumer verdict semantics.
- Kept the fixed ten-second matched full-command bar. The xdist spike selected
  the candidate; only matched full receipts established material relief.

## Trends vs Last Retro

No directly comparable prior retro exists for this goal window. The current
trend is nevertheless clear within the measured window: mutation runtime fell
from a 120.6s median to 76.8s without a proof-floor change. Historical
telemetry remains a recurrence signal, not a claim about this host session.

## North Star Alignment

P1 held for the reversible local candidate: judgment selected one owned change
after mapping, rather than adding a gate for every runtime smell. P4/P5 held at
the proof-surface boundary: bounded fresh-eye reviewers, distinct claims
re-derivation, and durable receipts kept a green command provisional. P3 held
by reusing one canonical runner principle instead of copying worker rules.

The run mis-applied P4 once in its process: the first claims review was treated
as usable before its delivery and boundary evidence had a durable path. The
correction was to persist the observer result before citing it. The named
failure signature was terminal trust in a single green channel; the dirty
pre-commit non-claim and final distinct review specifically prevented it.

## Expert Counterfactuals

- John Ousterhout would have forced the owner question before the first `-n`
  experiment: selector owns what runs, executor owns how it runs. That framing
  produced the smaller durable repair and avoided another policy fork.
- Charity Majors would have demanded a receipt that exposes the failing seam,
  not merely a faster green. The two-worker identity proof, changed-line
  consumer result, and explicit dirty-run refusal are the observables that make
  the speed claim useful under failure.

## Sibling Search

- same layer: `charness-artifacts/critique/*` delivery and boundary records |
  decision: same waste, fix now | proof: `rg` found the existing reviewer
  boundary contract and this run added bound delivery/receipt artifacts.
- abstraction up: `skills/public/achieve/references/lifecycle-after.md` and
  `goal_artifact_closeout_evidence.py` | decision: intentional boundary |
  proof: these already require distinct retro/disposition evidence; no second
  generic gate is warranted.
- specialization down: `skills/public/critique/` packet and reviewer helpers |
  decision: diagnostic-only | proof: packet preparation and boundary fingerprint
  already expose the needed inputs; the observed gap was persistence timing.
- mental-model siblings: `docs/conventions/operating-contract.md` and
  `skills/shared/references/fresh-eye-subagent-review.md` | decision: valid
  follow-up outside the slice | proof: the same durable-observer rule applies
  to other closeouts; follow-up: https://github.com/corca-ai/charness/issues/505.

## Next Improvements

- workflow: applied — persist each bounded review's delivery and boundary
  receipt before citing it in the goal; this run's critique and claims records
  are the model.
- capability: applied — worker-coverage proof now asserts distinct worker
  identities and exported coverage rather than an optional output banner.
- memory: issue #505 (recurs: closeout-critical-path runtime) — retain the
  measured mutation-lane owner and reopen only when a new matched receipt shows
  proof-preserving runtime regression or another safe structural owner.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-05-make-mutation-quality-gate-runtime-actionable-retro.md
