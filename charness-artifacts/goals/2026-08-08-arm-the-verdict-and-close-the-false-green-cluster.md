# Achieve Goal: Arm the verdict, then close the false-green cluster

Status: complete
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Status: CLOSED EARLY at 2 of 7 slices by operator instruction, not by a blocker.
  Slices 1 (`#530`, WARN tier armed) and 2 (`#554` part 1, backlog-recount floor)
  are complete and proven; both ran round-1 AND round-2 bounded review.
- Successor: `charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md`
  (draft, pursue-ready). The remaining claims — `#518`, `#528`, `#547`, `#546`,
  `#536`, `#537` — are re-homed there. `#535` is released for a decision and
  `#534` is deliberately NOT re-homed: a prior goal built, refuted and reverted it.
- Open operator decisions carried to the successor: whether the GATE discharges
  `#530`, and whether `#535` is worth claiming.
- Final gate: 86 passed, 0 failed, 0 UNPROVEN. 13 commits, all local; nothing
  pushed.
- No further action belongs to this artifact. Read `## Final Verification` for the
  proof and non-claims, `## Slice Log` for what each slice measured.

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
| 1 | Arm the WARN tier on unreconciled adapter keys; measure the fire rate first | #530 | The operator's decision is made; arming is what turns v3.5.0's seam into something an operator sees | done (`ebc483dc`) — armed for `unknown` only; `#530` NOT closed, see Decision Queue |
| 2 | Make `achieve` recount the tracker | #554 | Early, because every later slice's scope is shaped by it; this goal is its first test | part 1 done (`50407fab`) — the FLOOR ships; the automated helper does not, and the named seam was refuted (see `#555`). `#554` NOT closed |
| 3 | Reconcile every declared quality surface to a reader or a typed gap | #518 | Expressible only once a declaration resolves to a reader, and useful only once armed | planned |
| 4 | Let a repo declare a sub-key ABSENT | #528 | Needs declared/defaulted/absent as three states | planned |
| 5 | One-command re-bind that reports which identities moved | #535, #547 | Same shape as slice 1: a tool that reports success it did not establish | planned |
| 6 | Close the false-green gate cluster | #546, #536, #537, #534 | Cheapest last: each is local, and slices 1-5 will have exercised the gates that surface them | planned |
| 7 | Bundle proof, goal closeout, successor goal | (none) | Composition can drop what each slice proved alone | planned |

## Backlog Recount

- Counted: 28 open issues on 2026-08-08 via `gh issue list --repo corca-ai/charness --state open`, recounted AFTER activation. The goal was shaped against 25, so the shaping number was already stale — which is the defect this section exists to expose, found by the floor's own first use.
- Claims: `#530` (slice 1, armed but NOT closed — see the Operator Decision Queue), `#554` (slice 2, this floor), `#518`, `#528`, `#535`, `#547`, `#546`, `#536`, `#537`, `#534` (slices 3-6, planned and not yet started).
- Not claimed: the prompt-surface cluster (`#519`, `#520`, `#521`, `#523`, `#524`, `#525`, `#527`, `#531`, `#532`) — a different question, measuring prompt efficacy, and mixing it in is how a goal stops being reviewable. `#514`/`#515` — they predate this line of work and carry consumer ownership. `#549`, `#548`, `#545`, `#542`, `#539`, `#550`, `#552` — unclaimed, no reason beyond scope. `#555` — filed BY this run during slice 2's premise check and deliberately left for a successor, because consolidating two tracker backends is a cross-skill change that would swallow the slice that found it. Arithmetic, so a reader does not have to reconstruct it: 10 claimed + 19 not claimed = 29, one more than the 28 counted, because `#555` did not exist when the count was taken.

## Operator Decision Queue

- Decision: RESOLVED 2026-08-08 — unreconciled adapter keys WARN (not refuse).
  Owner: operator. Recorded here because slices 1 and 3 both depend on it and a
  future reader will ask why the tier is what it is.
- Decision: is the GATE the right surface for `#530`, or must the RESOLVER warn too?
  Owner: operator.
  Why deferred: slice 1 armed `scripts/validate_adapters.py`, which catches the
  issue's exact reproduction and reaches an operator at commit time and in
  `run-quality.sh`. But `#530`'s TITLE names the resolver payload, and
  `skills/public/*/scripts/resolve_adapter.py` still returns
  `valid: true, errors: [], warnings: []` for a typo'd key. Half (b) (unchecked
  `version`) IS fixed and verified. Arming the resolver was rejected on measured
  cost: a 3.1s reader scan on every resolver invocation, including the 16
  subprocesses the gate itself spawns.
  Unblock action: operator says whether the commit-time gate discharges `#530`,
  or the resolver owes a `warnings` entry too.
  Revisit trigger: any consumer report of a typo'd key surviving to runtime.
  Until resolved, `#530` stays OPEN and no closeout is staged.

- Decision: whether the prompt-surface cluster becomes its own goal.
  Owner: operator.
  Why deferred: explicitly out of scope here; it is a measurement question, not a
  verdict question.
  Unblock action: operator says whether prompt efficacy is a goal of its own.
  Revisit trigger: any slice here needing a read-cost number it cannot get.

## Coordination Cues

Phase-appropriate routing chosen from installed skill metadata and model
judgment.

- Routing: achieve — goal operator for the whole run; owns the slice log, the operating frame, and the closeout floors
- Routing: impl — slice 1 and slice 2 builds, both loading prove at their stop gate
- Routing: quality — the slice-boundary gate cadence, dup-ratchet dispositions, and the mutation/coverage reads
- Routing: issue — filed #555 under the standing issue-filing approval during slice 2's premise check
- Routing: critique — two bounded review rounds per slice, four rounds total
- Routing: retro — the closing efficiency review that produced this goal's successor scope
- Gather: n/a — no external URL or published source became working context in this run; every input was repo-local or the live tracker
- Release: n/a — no release, tag, or version bump was requested or performed; the plugin mirror sync is not a release surface
- Issue closeout: n/a — no issue was closed. #530 and #554 both remain open by design, each with an operator decision recorded in the queue above
- Successor goal: charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md — designed from THIS run's measured mechanisms (one rule with two owners, a refusal that cannot say its own name, a label that reads as protection), carrying twelve tracker issues that share that class plus the four waste habits this run measured

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

### Slice 2: Slice 1 complete — the WARN tier is armed (#530)

- Objective: Arm the operator-visible WARN tier on unreconciled adapter keys, after measuring the fire rate, and carry it through the two bounded review rounds a verdict-logic change on a proof surface owes.
- Why this approach: The operator's WARN decision was made; arming is the smallest change that turns v3.5.0's seam into something an operator sees. Ordered first because every later slice's value depends on the registry being consumed rather than merely correct.
- Commits: b8453c02 (arm) -> f6ead5ea (round-1 repairs) -> ebc483dc (round-2 repairs). Base 58be4025.
- What changed: scripts/adapter_key_registry.py (WARN_STATES, unreconciled_keys, three docstrings rewritten); scripts/validate_adapters.py (iter_warn_scope_adapters, report_unreconciled_keys, summary line, early-return condition); tests/quality_gates/test_adapter_key_warn_tier.py (new, 10 tests); tests/quality_gates/test_adapter_key_registry.py (stale count corrected); scripts/boundary-bypass-baseline.json (deliberate +1); docs/handoff.md; plugins/ mirror synced.
- Alternatives rejected: REJECTED -- arming each skill's `resolve_adapter.py`, the surface where an operator literally reads `valid: true, errors: []`. It is the truer symptom surface but costs a 3.1s reader scan on every resolver invocation, including the 16 subprocesses the gate itself spawns. This is the reason #530 is NOT claimed closed; see Off-goal. REJECTED -- arming `reader-elsewhere`: measured 13% false-positive rate (3 of 23 are association residue where the reader genuinely reads the file through dynamic dispatch), one of them inside a SHIPPED example, so arming it would greet every new consumer with a wrong warning. REJECTED -- widening `associated_modules` to absorb that residue: forbidden by this goal's Non-Goals and the mechanism by which #553 happened. REJECTED -- arming a REFUSAL: the operator chose WARN and D46 forbids escalating from a repo-local zero.
- Targeted verification: ARMED SURFACE: `python3 scripts/validate_adapters.py --repo-root .` prints `Validated 16 adapter resolvers and 18 adapter YAML file(s); 0 unreconciled declared key(s) across 37 declaring file(s).` and exits 0. FIRE RATE (the Boundaries' precondition, measured BEFORE arming and re-pinned after): 37 adapters / 445 declared keys; `unknown` 0 REPO-WIDE and 0 ACROSS SHIPPED EXAMPLES (18 repo-owned/227 keys, 19 shipped examples/218 keys). ACCEPTANCE: the warned input is CONSTRUCTED, not observed -- `unknown` fires zero times here, so a green suite proves nothing; three subprocess tests drive the real CLI over constructed trees (a typo in `.agents/`, a typo in a `skills/public/` shipped example, and a typo in the FLATTENED `skills/<id>/` installed layout). REGRESSION FIXTURE: `setup-adapter.yaml`'s four multi-reader keys warn about nothing, asserted at the arming layer rather than trusting the resolver. MUTATION: 14 mutants across three rounds, 13 killed. Survivors were dispositioned rather than tolerated -- two were unreachable branches DELETED (a `relative_to` fallback and an `isinstance(key, str)` guard, both provably unreachable), one was killed by asserting the warning's REASON text, one by proving the call site rather than the helper, one by naming both example families separately. M14 (require_git not threaded) SURVIVES and is disclosed: `iter_matching_repo_files` already applies the git listing whenever the repo is a git repo, so the flag only changes strictness when git is unavailable. GATES: `run_slice_closeout.py --skip-broad-pytest` completed at every commit; `./scripts/run-quality.sh --read-only` 85 passed / 0 failed at both slice boundaries; changed-line mutation coverage clean (analyzed 2, blocking []) -- it first refused a verdict on a dirty worktree, which is the gate behaving correctly. 42 tests green.
- Test duplication pressure: `check_dup_ratchet.py --repo-root . --summary`: OK, no new fixable-eligible families; fixable_ceiling=0 <= floor_F=0. Advisory nose families 1-5 are pre-existing resolver/portability boilerplate, unchanged by this slice.
- Critique: TWO ROUNDS, as the contract requires for verdict logic on a proof surface, and round 2 earned its cost again. ROUND 1 (2 blockers): (a) the gate armed `iter_adapter_yaml`'s 18 `.agents/` files while reporting the 37-adapter measurement's zero -- a check claiming a scope it never read, reproduced before repair as a typo in a shipped example passing with `0 unreconciled` and 40 green tests; (b) three live claims still said `no tier is armed`, in `find_readers`, in `survey`'s docstring (which misread D46 as forbidding what shipped -- D46 forbids escalating a REFUSAL), and in `docs/handoff.md`, the surface a next session reads first. Plus a MODERATE: the module docstring justified arming with (FILE, KEY) scoping while the armed path is deliberately KEY-scoped, sound only because `unknown` is scope-invariant. ROUND 2, reading the repairs (2 moderates): (a) the warn scope listed through a bare `root.glob`, silently abandoning the `git ls-files` filter every other listing in the validator uses, so `--require-git-file-listing` no longer governed the whole command -- a SECOND, undisclosed scope difference riding inside the fix for the first; (b) the widening never reached the flattened `skills/<id>/` layout the export produces, so it found zero shipped examples in exactly the layout consumers receive. It also caught the scope test being too loose to notice a deleted glob family (`>= 15` against 16+3) and two stale prose counts, one of which disagreed with the 23 that is the sole justification for not arming `reader-elsewhere`. Round 2 has now caught real defects in every measured slice that ran it.
- Off-goal findings: #530 is NOT claimed closed and no closeout was staged. The gate now warns on the issue's exact reproduction and half (b) (unchecked `version`) is genuinely fixed (`version: 7` -> `errors: ['version must be 1']`, verified at the resolver). But the issue's TITLE names the resolver payload, and `resolve_adapter.py` still returns `valid: true, errors: [], warnings: []` for a typo'd key. Whether the gate is the right surface for that symptom is an operator decision, recorded in the Operator Decision Queue rather than resolved by fiat.
- Lessons carried forward: PROCESS ERROR to carry forward: for round 2 the reviewer-boundary window was verified AFTER committing the repairs, not before starting them. The contract says the window closes before the parent repairs. The verdict was recoverable -- `--parent-head-moved` resolved it to `parent-attributed` with zero reviewer-attributable drift -- but the ordering discipline slipped and a real reviewer-side write would have been indistinguishable from my own commit at that point. Round 1 was done correctly; the difference was momentum. SUBSTANTIVE: a mutation that survives at the CALL SITE while every test passes is the signature of tests proving a helper rather than the wiring, and it is the same defect as a check claiming a scope it never read, one level up. Both appeared in this slice, and the second appeared inside the fix for the first.
- Metrics:

### Slice 3: Slice 2 premise check (#554) — recorded BEFORE the build

- Objective: Verify the remedy the Slice Plan names for `#554` ("make `achieve` recount the tracker, reusing `handoff`'s backlog seam") before shaping any code around it, per the Work Phase Map's design-time premise rule.
- Why this approach: The Work Phase Map fires one phase earlier than the rest of implementation discipline: before SHAPING a slice around a remedy a durable record already names. `#554`'s own text names a direction, and this goal's Slice Plan copied it. That is exactly the input the rule exists to check.
- Commits: none yet — this entry is the pre-build record. Off-goal finding filed as #555.
- What changed: nothing yet; reading only
- Alternatives rejected: REJECTED — `achieve` imports `chunked_routing_issue_source`: inherits handoff's adapter gating and closes a dependency cycle. REJECTED — `achieve` builds its own backlog reader: the exact repair `#554` forbids, and would be the third implementation. CONSIDERED, NOT CHOSEN — extract the issue-listing seam to `skills/shared/scripts/`: it resolves the duplication but moves a surface AWAY from its contractual owner, and it enlarges slice 2 from "achieve gains a recount" into "three skills change". Recorded in #555 as the open alternative rather than decided here.
- Targeted verification: PREMISE VERDICT: REFUTED. The named remedy is wrong in its object, and the direction it implies is wrong in its target. FOUR ESTABLISHED FACTS. (1) `parse_handoff_entries.py --with-issues` is a handoff-ARTIFACT parser: it parses a handoff's `## Next Session` entries and merely UNIONS tracker issues into them. `achieve` shaping a goal has no handoff artifact to parse, so the flag is not the seam — the seam it calls is `chunked_routing_issue_source.build_issue_entries`. (2) That seam is GATED behind the handoff adapter: `load_issue_source_config` reads the handoff adapter's optional `issue_source:` block, and a host that sets `issue_source: {enabled: false}` would silently disable `achieve`'s goal-shaping recount too. A backlog floor that a DIFFERENT skill's adapter can switch off is not a floor. (3) The naive direction is a CYCLE: `skills/public/handoff/scripts/draft_goal_from_chunk.py:55` already loads `achieve`'s `goal_artifact_lib`, so `handoff -> achieve` exists; adding `achieve -> handoff` closes it. (4) THE DECISIVE FACT, and it inverts the target: `handoff` does NOT own tracker access. `skills/public/handoff/scripts/chunked_routing_issue_backend.py` is a SECOND implementation of backend resolution — same `{"id": "gh", "binary": "gh", "commands": None}` default and the same `backend.get("binary") or backend.get("id") or "gh"` line as `skills/public/issue/scripts/issue_runtime.py`, and its own docstring says so ("exactly as `issue_runtime` already does"). The `issue` skill is the contractual owner per CLAUDE.md. So `#554`'s warning that "building a second backlog reader inside `achieve` would be the wrong repair" describes something that ALREADY HAPPENED once, between `handoff` and `issue` — and following the Slice Plan literally would have made `achieve` the third consumer of the duplicate rather than the first consumer of the owner. REVISED TARGET: `achieve` consumes the `issue` skill's backend, mirroring the dual-layout `_load_issue_module` route `chunked_routing_issue_backend` ALREADY uses to import from `issue`. This keeps the graph acyclic (`issue` imports neither `achieve` nor `handoff`; it is a leaf), puts the dependency on the contractual owner, inherits no handoff adapter gating, and adds no third backend. CROSS-SKILL IMPORT IS NOT A NEW PATTERN HERE: it is established, deliberate, dual-layout-aware, and documented as "route reuse".
- Test duplication pressure:
- Critique: Reviewer question to carry into the build: `#554` also asks that `--pursue-ready` refuse a goal with no record of which open issues it claims and does not. That is VERDICT LOGIC on a proof surface (`check_goal_artifact.py` is what decides a goal may activate), so the slice owes round-1 AND round-2 bounded review. The presence-only shape matters: the judgement of WHICH issues to claim is the operator's, and a floor that tried to check correctness rather than presence would be a new false-verdict surface inside the tool built to stop them.
- Off-goal findings: #555 filed: two tracker-backend implementations already exist (`handoff` and `issue`) with parallel default templates and refusal paths, and nothing prevents them diverging. Filed under the standing issue-filing approval. Its non-claims are explicit: no evidence the two currently DISAGREE, and no non-`gh` backend exercised.
- Lessons carried forward: The premise check has now paid 5 for 5 in this goal family, and this is its largest single save: the Slice Plan's remedy would have shipped a working feature wired to the wrong owner, inheriting a foreign adapter's kill switch and closing a dependency cycle — none of which is visible from the issue text or the plan row. The tell was cheap: read what the named script actually parses, then ask who OWNS the capability rather than who currently HAS it.
- Metrics:

### Slice 4: Slice 2 complete — the backlog-recount floor (#554 part 1)

- Objective: Make `achieve` reconcile a goal's scope against the tracker before activation: a draft needs `## Backlog Recount` (`Counted:`/`Claims:`/`Not claimed:`) or `--pursue-ready` refuses it.
- Why this approach: `--pursue-ready` decides a goal may activate and validated only headings, placeholders and closeout-plan fields, so a goal contradicting the tracker activated cleanly. Chosen second because every later slice's scope is shaped by it, and this goal is its first test.
- Commits: cfc1035f (floor) -> 06a1b773 (wiring proof) -> 265fe90f (round-1 repairs) -> 17ce9bfd (coverage + surfaces) -> e48e44ff (mutation-gate mapping) -> 50407fab (round-2 repairs).
- What changed: NEW skills/public/achieve/scripts/goal_artifact_backlog.py; goal_artifact_pursue.py (wiring, `is_shaping_status`, three-state PASS clause, shared `_SUBSTANTIVE`); goal_artifact_lib.py (sibling gate); goal_artifact_template.md; handoff/scripts/templates/auto_draft_goal.md; achieve SKILL.md + references/lifecycle-before.md + references/goal-artifact.md; NEW tests/quality_gates/test_goal_artifact_backlog.py (17 tests); test_goal_artifact_producers.py; test_goal_artifact_pursue.py; tests/charness_cli/test_goal_helpers.py; tests/fixtures/handoff-auto-draft-rendered.txt; .agents/surfaces.json; quality/attention-state-visibility.json; dup-review.json; docs/public-skill-dogfood.json; plugins/ mirror.
- Alternatives rejected: REJECTED -- grading WHICH issues a goal claims. That judgement is the operator's, and a floor grading it would be a new false-verdict surface inside the tool built to stop them; pinned by a test passing two goals with contradictory splits over the same tracker. REJECTED -- an unconditional floor: 153 of 156 goal artifacts predate the rule, and a floor that reddens the corpus is one that gets disarmed rather than obeyed. REJECTED -- suppressing the first dup-ratchet family: it was my own redundant `main()` CLI shim, no sibling floor module ships one, so it was DELETED rather than classified.
- Targeted verification: SCOPE DELIVERED: `#554` part 1 (the floor) ONLY. Part 2 (an automated recount helper consuming the tracker) is NOT built -- the premise check showed the seam belongs to `issue` while `handoff` holds a duplicate implementation, filed as `#555`, and wiring it is a cross-skill change that would have swallowed the slice. `#554` is therefore NOT claimed closed. PROOF: 17 floor tests + 56 across the achieve/goal/producer surface; full suite 7816 passed at an earlier commit; `run-quality.sh --read-only` 86 passed / 0 failed / 0 UNPROVEN at the final boundary -- the first fully clean gate of this goal. MUTATION: 6 mutants on the floor, 6 killed (fail-open on missing `Created:`, empty-value acceptance, dropped required field, the newline-greedy regex the floor shipped with, a rule date pushed past this goal's artifact, and the activation wiring). Plus two hand-mutants on the repairs: reverting the sibling closeout gate FAILS, and removing the section from the handoff template FAILS. DOGFOOD: this goal's own artifact is in scope of the floor it ships and satisfies it.
- Test duplication pressure: Three dup-ratchet families surfaced. One removed (the `main()` shim). Two classified `intentional` with written reasons: per-floor `RULE_DATE` bindings (collapsing them forces one shared date across floors that landed on different days) and the 13-member `spec_from_file_location` preamble, twelve of whose members are untouched. A doc family had its reducible half removed -- both templates carried the same four-line explanation, now a one-line pointer -- and the irreducible remainder classified, because two producers must each literally contain the section they scaffold.
- Critique: BOTH ROUNDS RUN, and round 2 found three blockers including two INTRODUCED BY the round-1 fix. ROUND 1: (a) the floor shipped into `achieve`'s template but not `handoff`'s, so every pickup-generated goal was refused with no heading to fill -- and the parity test built to catch exactly that was blind, because it checks the section TUPLES and a conditional floor is in none of them; (b) the docstring said 'nineteen goal artifacts predate this rule', a number carried from the PRECEDING slice's unrelated count of 19 shipped example adapters; (c) the floor was removable by deleting the `Status:` line while two docstrings claimed otherwise; (d) `Claims: **` satisfied it. ROUND 2, reading the repairs: (a) I closed only HALF of (c) -- the sibling gate in `goal_artifact_lib` stayed on `== "draft"`, and because the closeout-plan field check is gated on the section being required, one edit still disarmed both; the repair made that path REACHABLE, and my own regression test named the hole in its docstring and asserted nothing about it; (b) collapsing two skip reasons into one boolean made the PASS sentence assert 'this artifact is not a draft' about pre-rule DRAFTS, which are 7 of the 8 live ones -- the majority draft path; (c) 'nineteen' survived verbatim into the test module's docstring. Round 2 also found the em-dash defect the floor DIAGNOSED still live in the sibling it copied from, a stale operator-facing reference, a dogfood citation naming a file the rename deleted, a `>`-quoted example line that could satisfy the floor from another artifact's recount, and a producer test proving strings rather than the refusal.
- Off-goal findings: `#555` filed during the premise check: `handoff` and `issue` each carry a tracker-backend implementation with parallel `gh` defaults and refusal paths. Not claimed here. Two FALSE-RED findings repaired as part of the slice: `tests/fixtures/` had NO owning surface in `.agents/surfaces.json` (pre-existing, both files, surfaced by touching a golden render and reported as five broken bundle tests rather than its own message), and the mutation gate's target selector maps modules to tests by quoted path or dotted module -- a bare `import` after a `sys.path` insert left the floor's own tests out of the focused selection, so exercised lines read as UNCOVERED.
- Lessons carried forward: HARDENING ONE OF TWO SIBLING GATES MAKES THE OTHER REACHABLE. Round 1 named a bypass; I fixed the floor it pointed at and left the gate beside it, which converted a shared bypass into a live one-gate bypass. When a finding is 'this predicate is wrong', grep for every caller of that predicate before repairing one. Both gates now share a named function so they cannot drift again. A DERIVED NUMBER IS NOT A MEASURED ONE: the same sentence carried a wrong number twice -- first borrowed from an adjacent slice, then computed as 176 minus 3 without checking that 20 of the 176 were not goal artifacts at all. Both looked authoritative. THE WIRING-VS-HELPER GAP APPEARED THREE TIMES in this goal (slice 1's call site, this floor's activation conjunct, this floor's producer test), which is enough to call it the house failure mode rather than a coincidence.
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
- `#555` FILED this run (slice 2 premise check): `handoff` and `issue` each carry
  a tracker-backend implementation with parallel `gh` defaults and refusal paths.
  Not claimed by this goal — slice 2 routes around it by consuming the owner
  (`issue`) rather than consolidating the duplicate.
- `#514`/`#515` carry consumer ownership and are not this goal's to close.

## Final Verification

Retro: charness-artifacts/retro/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster-retro.md
Host log probe: skipped: host-log-not-exposed: this host surfaces no per-turn token, wall-clock, or tool-call ledger to the session, so any efficiency figure here would be fabricated rather than measured; the gate timings quoted in the Slice Log come from the gate's own output and are the only real timing evidence this run has.
Disposition review: charness-artifacts/critique/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster-disposition-review.md

Early close: this goal is closing at 2 of 7 slices by explicit operator
instruction, not because the remaining work is unsafe. The operator asked for the
structural class the run surfaced to become the center of gravity and to be taken
LARGER, absorbing related tracker issues. Slices 1 and 2 are complete and proven;
the remaining claims (`#518`, `#528`, `#547`, `#546`, `#536`, `#537`, `#534`) are
re-homed in the successor rather than abandoned, and `#535` is explicitly released
for a decision rather than inherited silently.

Self-verification: `./scripts/run-quality.sh --read-only` 86 passed / 0 failed /
0 UNPROVEN at the final boundary; changed-line mutation coverage clean at HEAD.
The full-suite figure (7816 passed) was measured at an EARLIER commit, before the
last four landed — the qualifier is carried here deliberately, because dropping it
exactly where the number is used as closeout proof is this goal's own house
failure mode.

Mutation ledger: 20 mutants across both slices, 19 resolved. Two of those were
resolved by DELETING the unreachable branch they exposed, not by a test killing
them — "19 killed" reads stronger than the evidence, so it is stated as resolved.
The one survivor (`require_git` not threaded) is disclosed in the Slice Log with
its reason.

Non-claims: nothing was pushed, so remote CI is unobserved. No issue was closed.
`#530` and `#554` are NOT resolved. Consumer-repo behavior is unobserved. The
mutant ledger covers the verdict paths this goal added, not the surfaces they sit
in. The four bounded review rounds left NO checked-in packet or fingerprint
artifact, so their occurrence is supported only by this artifact's own prose — a
delegated reviewer flagged that and it is recorded rather than argued away. Slice
2's round-2 boundary window was verified AFTER its repairs were committed and
resolved to `parent-attributed` via `--parent-head-moved`; that is a degraded
verify, not a clean one.

## User Verification Instructions

## Auto-Retro

Retro dispositions: applied: five repairs committed this run — the warn-scope widening, the shared `is_shaping_status` predicate, two wiring-level tests, `tests/fixtures/*` surface coverage, and the mutation-selector test mapping — with two tracked issues, one accepted risk and one out-of-scope deferral itemised below.

- `applied: the WARN tier now reads iter_warn_scope_adapters' 37 adapters plus the flattened installed layout, with the scope stated in the summary line` — the gate claiming a scope it never read.
- `applied: is_shaping_status is now shared by the backlog floor and the closeout-plan section gate, so the two cannot drift again` — sibling-predicate drift.
- `applied: test_the_floor_actually_gates_activation_not_just_reports and test_the_real_command_warns_on_a_typo_in_a_shipped_example assert through the composed verdict, not the computing module` — the wiring-vs-helper gap, guarded for these two instances.
- `applied: tests/fixtures/* given an owning surface in .agents/surfaces.json` — a pre-existing coverage gap that surfaced as five unrelated broken tests.
- `applied: the floor's tests are loaded by quoted path so the mutation gate's target selector can map them` — exercised lines reading as uncovered.
- `issue #555` — two tracker-backend implementations; filed this run, claimed by the successor.
- `issue #537` — a correct refusal surfacing as unrelated broken tests; hit live this run, already open, now claimed by the successor rather than worked around again.
- `applied: docs/handoff.md's Next Session now names sync-before-verify, the aggregate-after-first-rejection habit, and the premise-check record, and the successor goal's Boundaries carry all four measured waste habits as activation-time constraints` — the sync-ordering false red, the serial gate rediscovery, the `-k`-filter-as-suite error, and the two derived numbers.
- `applied: the successor's Verification Plan requires a mutant at the CALL SITE, not only inside the helper, and requires each caller of a repaired predicate to be mutated independently` — the wiring-vs-helper and sibling-drift habits turned into a per-slice obligation rather than a remembered lesson.
- `accepted-risk: a commit was allowed past a blocked closeout because it was not chained to the gate's exit status; every pre-commit check passed and the closeout is green at that commit, so nothing shipped unverified, but no gate prevents the same ordering next time and none is added here` — recorded rather than dropped, which is what the first draft of this section did to it.
- `out-of-scope: a portable gate for the wiring-vs-helper and sibling-drift mechanisms needs evidence across several unrelated surfaces before it can be generalized without becoming a wolf-crier; the successor goal exists to produce exactly that evidence, and slice 9 is where generalization is decided`

Structural follow-up: `issue #537 (recurs: hit live in this run and independently
present in the tracker; the predecessor's #554 evidence shows the same
work-around-without-linking pattern, so this is a recurring class rather than a
novel one)`
