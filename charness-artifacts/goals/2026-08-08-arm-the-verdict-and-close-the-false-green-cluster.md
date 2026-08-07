# Achieve Goal: Arm the verdict, then close the false-green cluster

Status: draft
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed.
- Next action: activate and run Slice 1 (arm the warning tier).
- Verification cadence: cheap deterministic checks at commit boundaries; bounded
  fresh-eye proof at slice boundaries; broad/live proof at closeout.
- Gate cadence: `run_slice_closeout.py --skip-broad-pytest` per slice AND
  `./scripts/run-quality.sh --read-only` at EVERY slice boundary.
- Slice review packet: intent, changed files and owning/generated surfaces,
  expected invariants, tests/proof, non-claims, out-of-scope lines, questions.
- History boundary: keep this frame current; completed detail moves to
  `## Slice Log`.

## Goal

v3.5.0 made adapter declarations answerable: a `version` no reader speaks is
refused, and a declared key resolves to a named reader or a typed gap. But
NOTHING IS ARMED. The registry reports and refuses nothing, so the original
symptom — a typo'd key passing as `valid: true, errors: []` — is still what an
operator sees.

The operator has now decided the tier: **unreconciled keys WARN.**

That decision is the hinge. Arming it finishes `#530`, and it makes the same
question askable of every other surface that currently renders a false green.
This goal arms it, then works the cluster of issues that share exactly one shape:
**a check that reports success it did not establish.**

Ordered by what unlocks the most and what is least likely to be refuted:

1. Arm the warning; finish `#530`.
2. Repair the shaping defect that produced this backlog's waste (`#554`) —
   early, because every later slice's scope depends on it.
3. Surface reconciliation (`#518`), which consumes the armed registry.
4. Absence (`#528`).
5. The evidence-identity cluster (`#535`, `#547`).
6. The false-green gate cluster (`#546`, `#536`, `#537`, `#534`).

## Non-Goals

- Do not arm a REFUSAL. The operator chose WARN. D46's consumer-population
  reasoning still forbids escalating from a repo-local zero.
- Do not widen `associated_modules` to make a `reader-elsewhere` disappear.
  Measured twice: widening is how the verdict stops meaning anything.
- Do not take the prompt-surface cluster (`#519`, `#520`, `#521`, `#523`,
  `#524`, `#525`, `#527`, `#531`, `#532`) in this goal. It is a different
  question — measuring prompt efficacy — and mixing it in is how a goal stops
  being reviewable.
- No release, tag, version bump, or Cautilus run unless separately granted.

## Boundaries

- **Premise check is a phase, not a step.** It paid 3 for 3 in the predecessor
  INCLUDING where the premise held.
- **A slice that changes verdict logic owes round-1 AND round-2 bounded review**,
  and round 2 reads the REPAIRS. Measured twice in the predecessor: round 1's fix
  carried the class it fixed both times.
- **Widening a scope to avoid false positives ships with a measured UPPER bound
  in the same commit.** The predecessor's single most transferable lesson.
- **Run `./scripts/run-quality.sh --read-only` at each slice boundary.** In the
  predecessor it failed first and named four defects that 7,700 tests and two
  review rounds had missed.
- **Recount the tracker before shaping ANY scope, and record what this goal
  claims and does not.** This goal is the first shaped after `#554`; it must not
  reproduce the defect it exists to fix.
- **Arming a warning makes every existing green a claim.** Before arming, measure
  how many warnings fire across this repo and every shipped example. A tier that
  fires everywhere is the wolf-crier the predecessor's Non-Goals forbid, and the
  measurement decides whether to ship it as-is or scope it first.
- Bounded reviewers run read-only in the shared worktree, fingerprinted, and the
  window is CLOSED before the parent starts repairing.

## User Acceptance

- An adapter key that no reader consumes produces an operator-visible WARNING
  through a real command, not just a library return value. The report names how
  many warnings fire repo-wide and across shipped examples.
- `setup-adapter.yaml`'s four multi-reader keys produce NO warning — the
  regression fixture for the refuted approach survives arming.
- Every quality surface the adapter declares resolves to an executable reader or
  a typed gap; no declared-but-unreached surface renders as `clean` (`#518`).
- A repo can declare a sub-key ABSENT and the resolver honors it, distinguishably
  from `defaulted` (`#528`).
- An identity-binding surface has a one-command re-bind, and a re-bind reports
  WHICH identities moved (`#535`, `#547`).
- A budgeted label with no sample no longer reads as protection (`#546`).
- `pytest tests/ -q` reports zero failures AND `./scripts/run-quality.sh
  --read-only` exits 0 at each slice boundary.
- The Slice Log records the premise-check verdict BEFORE each build.

## Agent Verification Plan

### Low-Cost Checks

- `scripts/check_changed_surfaces.py` and the validators it names; root/plugin
  sync before validators; `check_python_lengths.py --headroom` before adding to a
  gated file; `check_dup_ratchet.py --summary` before writing the commit message.
- Do not pipe a gate through `tail`; redirect and grep.

### High-Confidence Checks

- Mutation-check every new verdict path and report the count from a re-run. Two
  mutants SURVIVED first in the predecessor and both exposed real gaps.
- Construct the warned input; never infer a warning from a green suite.
- For any new state, construct an input that reaches it.

### External Or Live Proof

- Remote CI is a non-claim unless separately observed, by a different observer
  AND channel than the push exit code.
- Consumer-repo product behavior remains a standing non-claim.

## Slice Plan

| Slice | Objective | Issues | Why HERE in the sequence | Status |
| --- | --- | --- | --- | --- |
| 1 | Arm the WARN tier on unreconciled adapter keys; measure the fire rate first | #530 | The operator's decision is made; arming is what turns v3.5.0's seam into something an operator sees | planned |
| 2 | Make `achieve` recount the tracker, reusing `handoff`'s backlog seam rather than building a second reader | #554 | Early, because every later slice's scope is shaped by it; this goal is its first test | planned |
| 3 | Reconcile every declared quality surface to a reader or a typed gap | #518 | Expressible only once a declaration resolves to a reader, and useful only once armed | planned |
| 4 | Let a repo declare a sub-key ABSENT | #528 | Needs declared/defaulted/absent as three states | planned |
| 5 | One-command re-bind that reports which identities moved | #535, #547 | Same shape as slice 1: a tool that reports success it did not establish | planned |
| 6 | Close the false-green gate cluster | #546, #536, #537, #534 | Cheapest last: each is local, and slices 1-5 will have exercised the gates that surface them | planned |
| 7 | Bundle proof, goal closeout, successor goal | (none) | Composition can drop what each slice proved alone | planned |

## Operator Decision Queue

- Decision: RESOLVED 2026-08-08 — unreconciled adapter keys WARN (not refuse).
  Owner: operator. Recorded here because slices 1 and 3 both depend on it and a
  future reader will ask why the tier is what it is.
- Decision: whether the prompt-surface cluster becomes its own goal.
  Owner: operator.
  Why deferred: explicitly out of scope here; it is a measurement question, not a
  verdict question.
  Unblock action: operator says whether prompt efficacy is a goal of its own.
  Revisit trigger: any slice here needing a read-cost number it cannot get.

## Coordination Cues

Phase-appropriate routing chosen from installed skill metadata and model
judgment. Fill during the run:

- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

CONFIRMED 2026-08-08 by explicit operator instruction in session: arm the warning
tier, take `achieve`'s backlog reading from `handoff`, and shape a LARGER goal
for an unattended overnight run.

- RESOLVED — the WARN tier is the operator's stated decision, not an inference.
- RESOLVED — scope is the verdict/false-green cluster; the prompt-surface cluster
  is explicitly excluded and recorded in the Decision Queue.
- RESOLVED — no push, release, or Cautilus run is implied by activation. Each is
  per-request, and the operator is asleep, so none may be assumed.

## Slice Log

## Context Sources

1. `charness-artifacts/goals/2026-08-07-repair-declaration-to-verdict-at-root.md`
   — the predecessor that built the seam this goal arms.
2. Live tracker recount 2026-08-08: 25 open issues at shaping time, ordered with
   `handoff`'s chunker (`parse_handoff_entries.py --with-issues`). Staleness
   facts from that run: 10 entries cited closed issues, 21 cited missing paths.
3. `scripts/adapter_key_registry.py` — the seam slices 1 and 3 consume.

## Interview Decisions

- Ordered by unlock value, not by issue number. Arming comes first because it is
  the smallest change that makes the predecessor's work operator-visible, and
  `#554` comes second because it shapes every later scope.
- The prompt-surface cluster is excluded rather than deferred inside. Nine issues
  sharing a theme is a goal, not a slice.
- `#514`/`#515` are NOT claimed. They predate this line of work, carry consumer
  ownership, and the handoff entries citing them are stale.

## Plan Critique Findings

- Corrected while drafting: the first shape put `#518` first, because it is the
  predecessor's next numbered slice. That buries the operator's decision behind a
  large surface and leaves the warning unarmed for most of the run. Reshaped to
  arm first.
- Open risk, not resolved: arming a warning may fire widely. Slice 1 therefore
  MEASURES the fire rate before arming, and the measurement can send the slice
  back to scoping instead of shipping a wolf-crier.
- Open risk, not resolved: `reader-elsewhere` currently includes
  under-association residue, and arming turns that residue into operator-visible
  noise. Slice 1 must decide whether the WARN covers `unknown` only, or
  `reader-elsewhere` too, from the measured counts.

## Closeout Binding Plan

- Reviewed inputs: name semantic goal/issue/quality inputs; retro, packet, reviewer, and lock records are terminal evidence.
- Frozen target: commit the semantic baseline, then bind the packet to that exact commit SHA.
- Fresh-eye: name a distinct reviewer and a different observer/evidence channel.
- Verification lock: name the lock command and evidence location; semantic input edits require rebinding.
- Complete flip: record packet/reviewer/lock evidence, then write terminal status/evidence bookkeeping outside the reviewed identity.

## Off-Goal Findings

- The prompt-surface cluster (`#519`, `#520`, `#521`, `#523`, `#524`, `#525`,
  `#527`, `#531`, `#532`) is unclaimed and recorded as a candidate successor.
- `#549`, `#548`, `#545`, `#542`, `#539`, `#550`, `#552` are unclaimed here.
- `#514`/`#515` carry consumer ownership and are not this goal's to close.

## Final Verification

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
