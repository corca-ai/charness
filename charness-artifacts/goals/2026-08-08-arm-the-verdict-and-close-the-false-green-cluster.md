# Achieve Goal: Arm the verdict, then close the false-green cluster

Status: active
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 1 (`#530`, arm the WARN tier) — built, round-1 reviewed,
  repaired at `f6ead5ea`; round-2 bounded review of the repairs in flight.
- Current slice intent: the WARN tier is ARMED for `unknown` only, across 37
  adapters (18 repo-owned + 19 shipped examples). `reader-elsewhere` and
  `text-asserted` stay reported-but-unarmed on measured evidence.
- Next action: disposition round-2 findings, then decide `#530`'s closability —
  see the OPEN QUESTION below, which the slice measured and did not resolve.
- OPEN QUESTION for `#530`: the gate now warns on the issue's exact
  reproduction, but the RESOLVER (`skills/public/*/scripts/resolve_adapter.py`)
  still returns `valid: true, errors: [], warnings: []` for a typo'd key — the
  literal string in the issue title. Half (b) (unchecked `version`) IS fixed
  (`version: 7` → `errors: ['version must be 1']`). Arming the resolver was
  rejected on measured cost (3.1s reader scan × 16 resolvers, including the 16
  the gate itself spawns). `#530` is therefore NOT claimed closed.
- Tracker recount 2026-08-08 (post-activation): 28 open issues, not the 25 this
  goal was shaped against.
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

### Slice 1: Slice 1 premise check (recorded BEFORE the build)

- Objective: Before arming the WARN tier on unreconciled adapter keys (#530), verify the premise the slice is shaped around and measure the fire rate across this repo and every shipped example, per the goal's Boundaries.
- Why this approach: The goal makes premise-check a phase, not a step. It paid 3 for 3 in the predecessor including where the premise held. Here it did NOT hold, and it changed both the arming site and the tier's scope.
- Commits: none yet -- this entry is the pre-build record
- What changed: nothing yet; measurement only
- Alternatives rejected: REJECTED -- arming at each skill's `resolve_adapter.py` payload (the surface where an operator literally sees `valid: true, errors: []`). It is the truer symptom surface, but it is 16 resolvers and would add the reader scan to every resolver invocation, including the 16 subprocess calls `validate_adapters.py` itself makes. Rejected on cost and blast radius; the gate reaches the same operator with one site. REJECTED -- widening `associated_modules` so the 3 residue instances resolve. Explicitly forbidden by this goal's Non-Goals, and measured twice in the predecessor as how the verdict stops meaning anything. REJECTED -- arming `reader-elsewhere` alongside `unknown`. Refuted by the 13% measured false-positive rate and the shipped-example instance above.
- Targeted verification: PREMISE VERDICT: REFUTED IN PART, and the refutation is load-bearing. (1) `scripts/adapter_key_registry.py`'s own module docstring (the `KNOWN DESIGN GAP` paragraph) states: 'this module must not be wired to anything that refuses or warns an operator: it would flag on evidence it does not have.' That paragraph describes resolution being KEY-scoped rather than (FILE, KEY)-scoped. That gap was CLOSED by `f470cd83` / `19189ff1`: `resolve_declared_keys` now takes `adapter_relative`, `associated_modules` scopes the parse list, and `survey` passes the relative path. The docstring is STALE and currently forbids the exact arming this slice exists to do. Repairing it is in-scope for the build, not a follow-up. (2) FIRE-RATE MEASUREMENT (`python3 scripts/adapter_key_registry.py --repo-root .`, 37 adapters, 445 declared keys): - `reader`: 254, `shared-core`: 167, `reader-elsewhere`: 23, `text-asserted`: 1, `unknown`: **0** - 24 gaps total = 5.4% of declared keys, concentrated in 4 files. - `registry_problems`: [] (the anti-rot audit is clean). (3) THE OPEN QUESTION THE GOAL LEFT TO THIS SLICE -- does WARN cover `unknown` only, or `reader-elsewhere` too -- is ANSWERED by classifying all 23 `reader-elsewhere` instances by hand: - 20 of 23 are GENUINE: `.agents/cautilus-adapters/chatbot-benchmark.yaml` (10) and `chatbot-proposals.yaml` (10). `scripts/cautilus_adapter_lib.py` pins `ADAPTER_PATH` to the SINGULAR `.agents/cautilus-adapter.yaml`, so nothing reads those two files at all. Real unreconciled declarations. - 3 of 23 are RESIDUE -- demonstrably FALSE warnings, verified by reading the readers: * `chunk_policy` in `skills/public/handoff/adapter.example.yaml`: `skills/public/handoff/scripts/chunked_routing_agentic_policy.py` line 79-92 does `resolve.load_adapter(repo_root)` then `raw.get("chunk_policy")`. It IS a real reader; the association closure misses it because it loads its sibling by dynamic string (`_load_sibling("resolve_adapter")`), and bare-basename matching was deliberately removed to kill #553. * `session_routing` and `skill_anchor_edit_guard` in `.agents/usage-episodes-adapter.yaml`: `scripts/host_hook_registry.py` lines 48-55 declare both as registry rows and line 82 passes `adapter=adapter` straight into their reconcilers. Real readers, missed via `getattr`/string dispatch. DECISION, from the measured counts: **WARN covers `unknown` ONLY.** Three reasons, in order of force: - `reader-elsewhere` carries a measured 13% false-positive rate (3/23), and 2 of the 4 firing FILES fire on residue alone. - One of those false positives is in a SHIPPED example (`skills/public/handoff/adapter.example.yaml`). Warning on `reader-elsewhere` means every consumer repo that copies the shipped handoff example sees a false warning on day one. That is precisely the wolf-crier the goal's Boundaries forbid. - `find_readers`' own stated bias (lines 183-192) is toward reporting a key as OWNED, so `unknown` UNDER-reports gaps and cannot invent one. The docstring already names this 'the safe direction for a warn tier'. The goal's Non-Goals forbid widening `associated_modules` to make a `reader-elsewhere` disappear, so the residue is NOT repaired by widening -- it is left reported-but-not-warned, which is what the `survey` CLI already does. (4) CONSEQUENCE THE MEASUREMENT FORCES: `unknown` fires ZERO times repo-wide. So the acceptance criterion cannot be met by observing this repo -- the warned input must be CONSTRUCTED, exactly as the goal's High-Confidence Checks require ('Construct the warned input; never infer a warning from a green suite'). (5) ARMING SITE, chosen from the measurement: `scripts/validate_adapters.py`. It is the operator-visible command (`run-quality.sh` line 673 and the commit-time dispatcher via `staged_commit_gate_plan.py` line 322), and its terminal line -- `Validated 16 adapter resolvers and 18 adapter YAML file(s).` -- is today a green that establishes nothing about key reconciliation. Cost probe: the full survey is 4.63s, but `unknown` is reachable only when the parse list is EMPTY, so it needs no association closure at all -- 3.11s, and `associated_modules`/`_reference_edges` can be skipped entirely.
- Test duplication pressure:
- Critique: Deferred to the build's round-1 bounded review; this entry is the premise phase only. Carried forward as a reviewer question: the `unknown` verdict's soundness rests on `find_readers`' quoted-literal match, whose stated limit is that ANY string constant equal to the key counts as a parse -- including one in a docstring or an emitted payload. That bias under-reports gaps, so it cannot manufacture a false warning, but it does mean an armed `unknown` will stay quiet for a typo that happens to collide with an unrelated string constant anywhere in `scripts/` or `skills/`. That is a non-claim to state, not a defect to fix here.
- Off-goal findings:
- Lessons carried forward: The premise check has now paid 4 for 4 across this goal family. This time it inverted a build decision twice over: it found the instrument's own docstring forbidding the arming (stale, repairable), and it turned the goal's explicitly-open warn-scope question into a measured answer rather than a judgment call. Reading the three suspicious readers cost minutes and converted 'reader-elsewhere is noisy residue, probably' into '13%, and one of them ships to consumers'.
- Metrics:

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
