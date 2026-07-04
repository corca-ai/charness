# Achieve Goal: Consistent --json output mode across repo scripts via a shared helper

Status: draft
Created: 2026-07-04
Activation: `/goal @charness-artifacts/goals/2026-07-04-json-output-shared-helper.md`
Timebox: 8h proposed — no operator work budget was supplied; confirm or adjust at activation
Activation time: to be set when `/goal` starts the run
Closeout reserve: 60m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-07-04-json-output-shared-helper.md` after confirming the draft is
  still intended.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Every Python CLI entrypoint under `scripts/` supports a consistent `--json`
output mode, emitted through one shared repo-owned helper
(`scripts/json_output_lib.py`, name subject to repo filename gates) with its own
unit tests, and a deterministic conformance gate keeps the conversion complete
so new scripts cannot regress to ad hoc JSON printing.

Evidence base at shaping time (2026-07-04, corrected by fresh-eye critique):
`scripts/` holds 147 Python files with a `__main__` block (146 non-lib
entrypoints); 65 non-lib entrypoints actually `add_argument("--json")` (a
grep-literal count says 78, but 12–13 of those only mention `--json` in strings
or subprocess invocations — Slice 2's inventory must count by argparse wiring,
not grep); ~9 entrypoints emit JSON unconditionally with no flag; 3 entrypoints
have no argparse at all; `json.dumps` styles are split (110 `indent=2` vs 45
bare); no shared JSON output helper exists anywhere in `scripts/`.

Consistency contract (exact schema fixed in Slice 1, consuming the `create-cli`
structured-output conventions):

- one shared emit function owns serialization (indentation, key stability,
  stream choice) — scripts never call `json.dumps` directly for `--json` output
- one argparse wiring helper adds the flag uniformly
- errors under `--json` are reported as JSON with defined exit-code semantics,
  not bare tracebacks mixed into the stream — for flags newly added in Wave B;
  Wave A conversions preserve each existing script's error-path output and exit
  codes (changing them is an observable behavior change that rides the
  consumers-first boundary, updated with its consumers in the same slice)
- `--json` output parses with `python3 -m json.tool` for every converted script

## Non-Goals

- Shell scripts (`scripts/*.sh`, 8 files) and Node scripts
  (`scripts/agent-runtime/*.mjs`, 9 files) — a Python helper cannot serve
  them; they keep their current output.
- Import-only modules (~123 `scripts/*.py` files with no `__main__` block —
  note many lack the `_lib` suffix) — no CLI surface, nothing to convert; they
  are in scope only where an entrypoint that wraps them converts. Scope
  classification is by `__main__`-block presence, never by filename.
- Skill-owned scripts — the source surfaces `skills/public/*/scripts/` and
  `skills/support/*/scripts/` (~264 files) and their generated exports under
  `plugins/charness/skills/*/scripts/` — a separate portable surface with its
  own bootstrap contract; converting them is a possible follow-up goal, not
  this one (recorded in Operator Decision Queue).
- Changing what any script *reports* — payload semantics stay identical; only
  the emission path and flag wiring are unified. Behavior-affecting output
  changes found along the way are filed via `issue`, not absorbed.
- Redesigning human-readable (non-`--json`) output.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Local-only goal: no publish, push, remote-CI, or external apply lane is
  requested or required; all proof is local and deterministic.
- Consumers first: 65 scripts already expose an argparse-wired `--json` and other repo surfaces
  (tests, gates, `check_coverage.py` invocations, skill docs) consume that
  output. Converting a script must not change its observable JSON payload
  keys/values unless a test proves the old shape was already broken; when a
  shape must change, the consuming surface updates in the same slice.
- Repo gates own style: the helper and every conversion respect
  `check_python_filenames.py`, `check_python_lengths.py`, export-safe imports,
  and the mutation-score gates; do not add per-script test files when a
  table-driven conformance test covers the same behavior (test-duplication
  pressure, see Slice Plan).
- Wave discipline: one migration wave = one reviewable slice; no cross-wave
  half-converted states left at commit boundaries.
- Always-JSON scripts (~9, e.g. `bootstrap_runtime.py`,
  `check_changed_line_mutation_coverage.py`, `check_mutation_run_proof.py`)
  emit JSON unconditionally today and have live stdout consumers
  (`run_slice_closeout.py` parses the mutation gate). Their conforming state is
  "emits via the shared helper, no flag required"; gating their output behind
  `--json` is a behavior change routed via `issue`, never applied in a wave.
- Changed-line mutation coverage gates ALL of `scripts/*.py`
  (`sample_mutation_files.py` pools every scripts file; subprocess-only
  exercise counts as 0% coverage). Wave conversions must keep changed lines
  in-process-covered: the conformance test imports and exercises the converted
  emit path directly, or the wave records the
  `check_mutation_run_proof.py --claim changed-line` proof lane before commit.

## User Acceptance

- Pick any Python entrypoint in `scripts/` and run it with `--json`; the output
  parses with `python3 -m json.tool` and the script's source shows the shared
  helper, not a bare `json.dumps` print.
- Run the conformance gate (added in Slice 2) and see zero non-conforming
  entrypoints; temporarily add a bare `json.dumps` `--json` script and see the
  gate go red.
- Run the helper's unit tests: `python3 -m pytest tests/test_json_output_lib.py`.

## Agent Verification Plan

### Low-Cost Checks

- Helper unit tests (envelope, error path, exit codes, argparse wiring).
- Conformance gate run over `scripts/` (deterministic, no network).
- Per-converted-script smoke: `<script> --json | python3 -m json.tool` for the
  scripts touched in the wave.
- Targeted pytest for test files that pin the touched scripts' output.

### High-Confidence Checks

- Broad pytest at wave-bundle boundaries and closeout (not per commit).
- Changed-line mutation coverage on every wave's touched scripts (the gate
  pools all of `scripts/*.py`, not just the helper): satisfied by the
  in-process conformance test exercising converted emit paths, with the
  `check_mutation_run_proof.py` lane as the planned fallback per wave.
- Mutation-score gates per standing policy on the helper and gate modules.
- `run_slice_closeout.py --skip-broad-pytest` pre-lock; `--verification-lock`
  at final proof, per the gate cadence in the operating frame.

### External Or Live Proof

- None planned and none claimed: this goal has no provider, network, or host
  side effects. Completion claims are local-proof-level only.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Fix the JSON output contract (spec via `create-cli` conventions) and build `scripts/json_output_lib.py` + unit tests | Everything downstream depends on the contract; cheapest point to critique it | Helper module; `tests/test_json_output_lib.py` green (in-process, mutation-gate-satisfying); contract notes in this artifact | planned |
| 2 | Conformance inventory + ratchet gate. Detection rule: any `scripts/*.py` with a `__main__` block, regardless of filename. Classes: conforming / ad-hoc `--json` (argparse-wired, 65 today) / always-JSON no flag (~9) / no JSON surface / no argparse (3). Proxy check: no `json.dumps` reaching stdout in entrypoint files outside the shared helper, with an exemptions allowlist mirroring `boundary-bypass-exemptions.txt` | Makes "all scripts" enforceable instead of aspirational; catches regressions from wave 1 onward | Gate script + test; shrinking baseline file; gate wired like `check_boundary_bypass_ratchet.py`; known residual recorded (a no-`__main__`-guard top-level script evades detection) | planned |
| 3 | Wave A: migrate the 65 argparse-wired ad hoc `--json` scripts to the helper, table-driven in-process conformance test instead of per-script tests; error-path output and exit codes preserved | Largest consistency win; no new flag semantics, lowest consumer risk | Baseline drops by 65; targeted tests green; payload-shape parity spot-checks; changed-line mutation coverage satisfied | planned |
| 4 | Wave B: add `--json` via the helper to the ~81 remaining entrypoints in domain batches (gates, tool install/update, artifact helpers); named sub-batches for the ~9 always-JSON scripts (helper without flag) and the 3 no-argparse scripts (adopting argparse is an arg-handling change, reviewed per script) | Completes the "all entrypoints" outcome | Baseline reaches zero non-conforming; gate flips to enforce-complete | planned |
| 5 | Closeout: docs touch-up (`docs/development.md` / generated CLI reference if affected), broad pytest + mutation gates, final quality gate, retro | Proof and reflection at bundle boundary per cadence | Final Verification section bound; Auto-Retro dispositioned | planned |

Test-duplication pressure plan: waves add one parametrized conformance test
over the entrypoint inventory, not per-script test files; each test-adding
slice records a `--test-pressure` sample in the Slice Log.

Timebox realism: at plausible throughput, Wave B (~81 scripts plus the
mutation-proof lane) likely overflows the proposed 8h. Wave B is explicitly
splittable — the ratchet baseline preserves partial progress as a valid
stopping state, and the done-early/timebox policy continues from the shrunk
baseline in a follow-on window rather than rushing the tail.

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

Open items:

- Decision: confirm or resize the proposed 8h timebox (no operator budget was
  supplied at shaping).
  - Owner: operator
  - Why deferred: a default timebox lets the draft complete; the value only
    binds at activation.
  - Unblock action: state a timebox (or accept 8h) when running `/goal`. Note:
    critique judged Wave B likely to overflow 8h; the slice plan marks Wave B
    splittable with the ratchet preserving partial progress, so 8h buys the
    helper + gate + Wave A with Wave B partial, while a larger box buys
    completion in one run.
  - Revisit trigger: activation.
- Decision: whether `plugins/charness/skills/*/scripts/` should get a follow-up
  goal adopting the same shared helper contract (out of scope here).
  - Owner: operator
  - Why deferred: separate portable surface with its own bootstrap/release
    boundary; excluding it keeps this goal reviewable.
  - Unblock action: say yes/no after this goal completes; if yes, a new goal is
    shaped from Slice 1's contract.
  - Revisit trigger: this goal's closeout report.

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the find-skills-recommended skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: find-skills -> <skill> — <why this phase needs it>`

Shaping-time routing evidence (fill run-phase lines during the run):

- Routing: find-skills -> achieve — goal shaping; task-text probe (read-only)
  returned no overriding support skill. Slice 1 consumes `create-cli`
  structured-output conventions; slices route through `impl`, verification
  cadence through `quality`, plan/slice review through `critique`, off-goal
  findings through `issue`, closeout reflection through `retro`.
- Gather: n/a — no external sources; the goal is shaped entirely from local
  repo evidence (`scripts/` inventory, existing gates, repo conventions).

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — broad scope ("모든 repo 스크립트",
  146 entrypoints) was the trigger; settled by bounding scope in Non-Goals to
  Python CLI entrypoints under `scripts/` only (shell scripts, pure libs, and
  plugin skill scripts excluded) and by making completeness a shrinking-baseline
  ratchet with wave slices instead of a big-bang sweep. No live/prod proof,
  issue close, or irreversible side effect is in scope. Two deliberately
  deferrable operator choices (timebox size; whether skill-plugin scripts get a
  follow-up goal) sit in the Operator Decision Queue and do not block
  activation. Operator can veto the scope interpretation before running
  `/goal`.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- Operator request (2026-07-04, session prompt): "모든 repo 스크립트에 일관된
  --json 출력 모드를 공유 헬퍼와 테스트로 추가하는 목표를 잡아줘".
- Local scout evidence: `ls scripts/` (286 entries; ~144 `__main__`
  entrypoints; 79 `*_lib.py`; 8 `.sh`), `grep -l -- '--json' scripts/*.py`
  (78 hits), `grep 'json.dumps' scripts/*.py` (~110 `indent=2` vs ~45 bare),
  no `emit_json`/`json_output`/`print_json` helper anywhere in `scripts/`.
- Conventions: `plugins/charness/skills/create-cli` (structured-output
  contract), `scripts/check_boundary_bypass_ratchet.py` +
  `scripts/boundary-bypass-baseline.json` (existing ratchet idiom to mirror),
  `docs/conventions/implementation-discipline.md`.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Path (artifact-only vs implementation-continuation): artifact-only Before
  phase. The request says "목표를 잡아줘" (shape the goal) — a strong default;
  no execution before `/goal`. Rejected: starting the helper now (violates
  inert-until-activation).
- Meaning of "모든 repo 스크립트": Python CLI entrypoints under `scripts/`.
  Rejected: including `plugins/charness/skills/*/scripts/` (different portable
  bootstrap surface; would triple scope and cross the plugin release boundary);
  including `.sh` scripts (wrong toolchain for a Python helper).
- Completeness mechanism: shrinking-baseline conformance ratchet + wave slices.
  Rejected: single big-bang conversion commit (unreviewable, high consumer
  risk); prose-only "please use the helper" convention (no teeth — exactly what
  the north star says to avoid for regressions that escape).
- Helper placement: new `scripts/json_output_lib.py` following the existing
  `*_lib.py` idiom. Rejected: `tests/`-side helper (runtime scripts cannot
  import it); embedding in an existing lib (no natural owner).
- Payload compatibility: preserve existing JSON shapes during Wave A; shape
  changes are their own reviewed decision per script, filed via `issue` if
  behavior-affecting. Rejected: normalizing all payloads to one envelope in the
  same pass (silently breaks 78 scripts' consumers).
- Timebox: 8h proposed with 60m closeout reserve; the operator supplied no
  budget, so the value is a default to confirm at activation, not a claim.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Reviewer provenance: bounded fresh-eye subagent (read-only, shared worktree),
2026-07-04, Before-phase plan critique across feasibility / scope-honesty /
verification-teeth angles with a counterweight pass.

Folded (1 blocker, 8 should-fix):

- BLOCKER — changed-line mutation gate pools ALL `scripts/*.py`
  (`sample_mutation_files.py`; subprocess-only exercise counts as 0%): folded
  into Boundaries + High-Confidence Checks + Slice 1/3 rows (in-process
  conformance test; `check_mutation_run_proof.py` lane as fallback).
- Count corrections: 147 `__main__` files / 146 non-lib entrypoints; 65 real
  argparse-wired `--json` (78 was grep-literal); Wave B ≈ 81 not ~66. Folded
  into Goal evidence base + Slice 3/4 rows; Slice 2 counts by argparse wiring.
- ~9 always-JSON no-flag scripts with live stdout consumers: folded as a
  Boundaries bullet + Slice 2 class + Wave B sub-batch (helper without flag;
  flag-gating is a behavior change via `issue`).
- 3 no-argparse entrypoints: folded as a named Wave B sub-batch.
- Detection dodgeability (45 import-only files lack `_lib` suffix; one
  `_lib.py` has `__main__`): folded — classification by `__main__` presence
  regardless of name; no-guard evasion recorded as accepted residual in
  Slice 2.
- `json.dumps` conformance not mechanically checkable as prose: folded — Slice
  2 pins the stdout-flow proxy + exemptions allowlist mirroring the
  boundary-bypass ratchet.
- Error-envelope vs payload-compat tension: folded — error contract applies to
  Wave B's new flags; Wave A preserves existing error output/exit codes.
- Scope wording named only the generated export path: folded — Non-Goals now
  name `skills/{public,support}/*/scripts/` source surfaces and exclude
  `scripts/agent-runtime/*.mjs`.
- Timebox realism (Wave B overflows 8h): folded into Slice Plan note + the
  Operator Decision Queue timebox item.

Over-worry raised, not folded: byte-level output compatibility (sampled
consumers `json.loads` rather than string-compare; parity spot-checks are
right-sized); `check_python_lengths`/filename-gate risk for the new helper
(idiom well-established, 480-line budget ample); export-safe import mechanics
(mechanical `import_repo_module` idiom, not a plan defect); 144-vs-147
entrypoint rounding (the wave-math error was the real defect and is fixed).

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
