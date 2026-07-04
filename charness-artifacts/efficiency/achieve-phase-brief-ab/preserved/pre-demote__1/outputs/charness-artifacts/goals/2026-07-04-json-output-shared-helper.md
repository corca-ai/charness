# Achieve Goal: Consistent --json output mode across repo scripts via a shared helper and tests

Status: draft
Created: 2026-07-04
Activation: `/goal @charness-artifacts/goals/2026-07-04-json-output-shared-helper.md`
Timebox: none supplied — scope is bounded by the conformance ratchet, not a clock; slices 1–3 land in the first active session, migration chunks continue under the done-early policy
Activation time: unset — stamped when `/goal` starts the active run
Closeout reserve: final ~20% of any active session reserved for broad-gate proof, retro, and closeout
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: real draft/backlog awaiting activation — shaped this
  session; reshape before activating if the acceptance boundary has changed.
- Current slice: none — draft awaiting operator scope confirmation, then activation.
- Current slice intent: none executing — `achieve` shapes only; no slice runs before
  `/goal`. Once active, this names the reviewable-intent unit in progress and the
  commits it spans; critique and broad proof do not re-fire within one unchanged
  intent — update it when the intent changes, not per commit
  (meaningful-slice-cadence).
- Next action: operator confirms the `Discuss before activation:` summary (scope =
  144 argparse entrypoints via shrinking-baseline ratchet; local-only proof), then
  activate with `/goal @charness-artifacts/goals/2026-07-04-json-output-shared-helper.md`.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- Reporting expectations: one `append_slice_log.py` entry per slice (with
  `--test-pressure` whenever a slice adds or expands tests); this frame stays
  current; the final report separates self-verification, user verification,
  residual risk, non-claims, and the operator decision queue.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Give every Python CLI entrypoint under `scripts/` a consistent `--json` output
mode through one shared helper, with the contract pinned by tests and enforced
by a shrinking-baseline conformance gate — so consistency is machine-checked,
not a prose convention.

Ground truth at shaping time (2026-07-04 scouting): `scripts/` holds 270 Python
files; 79 are `*_lib.py` libraries (78 without a main guard); 144 are
argparse CLI entrypoints; 78 of those already carry an ad-hoc, per-script
`--json` flag; no shared JSON-emission helper exists (no
`emit_json`/`print_json`/`output_json` definition anywhere under `scripts/`).

The shared contract the helper owns (mechanics, not payload schemas):

- one flag registration point (e.g. `add_json_flag(parser)`),
- exactly one JSON document on stdout in `--json` mode (diagnostics to stderr),
- deterministic serialization (stable indent/ordering choices, documented),
- a structured error payload + non-zero exit on failure paths,
- helper adoption checkable by the conformance gate.

Outcome capability: the repo gains a machine-enforced "every entrypoint speaks
consistent `--json`" contract — shared helper + unit tests defining the
contract + a conformance ratchet whose baseline only shrinks — instead of 78
divergent hand-rolled implementations and 66 entrypoints with none.

## Non-Goals

- No payload schema changes. The 78 existing `--json` scripts have consumers
  (tests, gates, other scripts) pinning their shapes; the helper standardizes
  mechanics only. A migration that cannot preserve a consumer-pinned shape
  stops and records the script on the baseline instead.
- Shell scripts (`check-*.sh`) and import-only `*_lib.py` files are out of
  scope; the unit is the argparse CLI entrypoint.
- No CLI framework rewrite (no click/typer); argparse stays.
- No plugin version bump or release surface inside this goal.
- No forced big-bang migration in one session: "all scripts" is achieved by the
  ratchet contract (baseline monotonically shrinks to empty), and migration
  chunks may span sessions under the done-early policy.

## Boundaries

- In scope: a new `scripts/json_output_lib.py` (name per repo `*_lib.py`
  convention), migrated entrypoints under `scripts/`, a conformance gate script
  with a checked-in baseline (precedent:
  `scripts/boundary_bypass_ratchet_lib.py` + `boundary-bypass-baseline.json`),
  and tests under `tests/`.
- External side-effect scope: none — this is a local-only goal; no
  publish / push / remote-CI / apply lane is requested or approved by this
  goal. `achieve` itself does not push.
- Portable per implementation-discipline. The plugin export mirror
  (`plugins/charness/scripts/` via `scripts/export_plugin.py`) mirrors ALL of
  `scripts/`, so EVERY slice touches the export surface: sync it
  unconditionally per slice before validators (`mutate -> sync -> verify`),
  not only when "gate wiring" changes (plan-critique blocker 1).
- Ratchet policy for new and renamed scripts (plan-critique blocker 2): after
  slice 1 the helper exists, so a NEW argparse entrypoint must adopt the
  helper from day one — the baseline never grows; renames move the baseline
  entry, never add one. Genuinely exempt cases go in an exemptions file with a
  mandatory `# why:` rationale, mirroring `boundary-bypass-exemptions.txt`
  parsed by `load_exemptions()` in `scripts/boundary_bypass_ratchet_lib.py`.
- Proof cost: cheap — targeted pytest per slice, broad pytest at bundle
  boundaries; no external spend.
- Stop conditions: (1) a consumer pins byte-exact output the helper cannot
  reproduce → leave that script on the baseline, file an off-goal finding via
  `issue`, continue with the next chunk; (2) the new gate conflicts with an
  existing quality gate or slows the suite meaningfully → route through
  `quality` before wiring; (3) the bounded fresh-eye reviewer is blocked at the
  runtime level → stop and report the concrete host signal; (4) no safe next
  slice → `No safe next slice:` closeout with the boundary matrix.

## User Acceptance

What the user can do to verify completion directly:

- Run any migrated script with `--json` and pipe to
  `python3 -c "import json,sys; json.load(sys.stdin)"` — exactly one parseable
  JSON document on stdout.
- Run the helper's unit tests (`pytest tests/test_json_output_lib.py` — exact
  name fixed in slice 1) — green, and the test file reads as the contract.
- Run the conformance gate — it lists zero non-baseline entrypoints off the
  helper, and the committed baseline is visibly smaller than its seeded size
  (empty at full completion).
- `grep -l json_output_lib scripts/*.py` shows the migrated set.

## Agent Verification Plan

### Low-Cost Checks

- Targeted pytest for the helper and the gate at every commit boundary.
- Consumer reverse-dependency check per migrated script (plan-critique
  blocker 3): grep the script's filename across `scripts/`, `tests/`,
  `.githooks/`, and `*.sh`; run the CONSUMER tests (not just the script's own)
  in the commit-boundary targeted set. Known consumers include
  `scripts/check_coverage.py` (invokes `doctor.py`/`update_tools.py`/
  `install_tools.py --json`), `scripts/eval_setup.py`, and
  `.githooks/pre-push` (parses `classify_push_diff.py` stdout — shell logic
  outside pytest). Hook-consumed scripts count as gate-critical and migrate
  last in slice 4+.
- Unconditional per-slice plugin export sync (`scripts/export_plugin.py`)
  before validators — every slice touches the mirror (plan-critique blocker 1).
- Gate self-demonstration: run the conformance gate red (a deliberately
  non-conforming fixture or pre-migration script) then green.
- Import smoke on touched scripts (they remain importable / runnable).
- Test-duplication pressure: the conformance gate is ONE parametrized
  test + baseline file, never per-script test copies; slices that add tests
  carry a `--test-pressure` sample in the slice log; existing
  `tests/quality_gates/` output-pinning tests are reused, not duplicated.

### High-Confidence Checks

- Broad pytest at bundle boundaries via `run_slice_closeout.py` with the
  verification lock at final proof.
- Repo quality gates already wired (coverage / mutation where applicable) stay
  green over the migration chunks.
- Bounded fresh-eye slice critique per repo contract at slice boundaries.

### External Or Live Proof

- None required, stated as an explicit non-claim: the changed surface is local
  CLI stdout behavior; no provider or live-environment claim is made and no
  live lane exists for this goal. Remote CI runs once over the final bundled
  state only if the operator separately approves a push, which is outside this
  goal.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | `scripts/json_output_lib.py` shared helper + contract unit tests | Foundation every later slice depends on | New tests green; contract documented in module docstring | pending |
| 2 | Entrypoint inventory + conformance gate with shrinking baseline seeded at all 144 entrypoints, plus the new-script/rename/exemptions policy (`# why:` rationale file) | Makes "all scripts" machine-enforceable before any mass edit | Gate red/green demo; baseline committed; ratchet refuses baseline growth; new-entrypoint policy test | pending |
| 3 | Pilot migration of ~8 representative scripts (≥1 existing ad-hoc `--json` script, ≥1 error-path-heavy script, ≥1 no-JSON script) | Validates the helper against real consumers before batch work | Targeted pytest green; baseline shrinks by pilot count; consumer-pinned outputs unchanged | pending |
| 4+ | Batch migration chunks (~15–25 scripts per slice, consumer-risk-ordered: hook-consumed and gate-critical scripts last) | Converge the repo; ratchet guarantees monotonic progress across sessions | Baseline shrink per chunk; per-script reverse-dependency check; broad pytest at bundle boundary | pending |
| final | Closeout: broad gate with verification lock, duplicate-pressure classification, retro, dispositions | Prove and reflect | `run_slice_closeout.py --verification-lock`; retro artifact; Auto-Retro dispositions | pending |

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

Current queue: empty — the one pre-activation decision lives in
`## Discuss Before Activation`, not here.

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary.

- Routing: find-skills -> achieve — Before-phase shaping probe (2026-07-04, `--recommend-for-task "add consistent --json output mode to all repo scripts via shared helper and tests"`; no support-skill or public-skill override matched). Slice-time boundaries re-query find-skills per phase; `create-cli` is the likely structured-output reference surface for slice 1, and gate wiring routes through `quality` first.
- Gather: n/a — no external URL/source; the goal was shaped entirely from repo-local scouting (counts and precedents recorded in `## Context Sources`).
- Release: n/a — no release surface (version bump / install manifest) is touched by this goal; re-evaluate at closeout if that changes.
- Issue closeout: n/a — no tracked issue is resolved by this goal; off-goal findings route through `issue` during the run and are recorded by reference only.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`.

- Discuss before activation: PENDING OPERATOR CONFIRMATION — two consequential defaults were settled by assumption, not by the operator. (1) Scope: "모든 repo 스크립트" is read as the 144 argparse CLI entrypoints under `scripts/` (shell scripts and import-only `*_lib.py` excluded), with "all" enforced by a shrinking-baseline conformance gate, so full migration may span multiple active sessions instead of one big-bang edit. (2) Proof level: local-only goal with an explicit no-live-proof non-claim (no publish/push/remote-CI lane requested or approved). Confirm both — reply, or edit this line to start with `CONFIRMED — ...` — before `/goal`; `--pursue-ready` intentionally fails until then.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- Operator prose request (this session, 2026-07-04): "모든 repo 스크립트에
  일관된 --json 출력 모드를 공유 헬퍼와 테스트로 추가하는 목표를 잡아줘".
- Scouting evidence (2026-07-04, repo-local): 270 `.py` under `scripts/`;
  145 with `__main__`; 144 argparse entrypoints excluding `*_lib.py`; 78 with
  ad-hoc `--json`; zero `emit_json`/`print_json`/`output_json` shared helpers.
- `docs/handoff.md` (2026-07-04): reference-compaction frontier closed; no
  mandatory work conflicts with picking up this goal.
- Ratchet precedent: `scripts/boundary_bypass_ratchet_lib.py`,
  `scripts/check_boundary_bypass_ratchet.py`, `boundary-bypass-baseline.json`.
- find-skills probe output (read-only, 2026-07-04): no support-skill match for
  the task text; 20 public skills, 2 support skills inventoried.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

- Request path — options: artifact-only Before-phase draft vs
  implementation-continuation (start slices now). Chosen: artifact-only draft.
  "목표를 잡아줘" asks for goal shaping; `achieve` does not execute before
  `/goal` activation, and the operator was not present to authorize more.
- Meaning of "모든 repo 스크립트" — options: (a) literal 270 `.py` files
  including import-only libs; (b) the 144 argparse CLI entrypoints; (c) only
  the 78 scripts that already expose `--json`. Chosen: (b), with "all"
  enforced by the ratchet baseline rather than one hand-edited big-bang.
  Rejected: (a) libs have no CLI surface to flag; (c) leaves 66 entrypoints
  and every future script inconsistent, which defeats "일관된".
- Consistency mechanism — options: prose convention in docs; shared helper
  only; shared helper + conformance gate with shrinking baseline. Chosen:
  helper + gate. The repo standard prefers validators over prose rituals, and
  the boundary-bypass ratchet is the proven in-repo pattern for "converge a
  large surface monotonically".
- Compatibility posture — options: standardize full payload schemas vs
  standardize mechanics only (flag, single-document stdout, deterministic
  serialization, structured error + exit semantics). Chosen: mechanics only.
  78 existing `--json` scripts have consumers pinning shapes; schema changes
  would be a silent breaking wave across tests and gates.
- Helper shape — options: adopt a CLI framework; decorator/metaclass magic; a
  small argparse-native `*_lib.py` module. Chosen: small argparse-native lib
  matching the repo's existing `*_lib.py` convention; `create-cli`'s
  structured-output guidance is consulted at slice time via find-skills
  routing.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance.

Reviewer provenance: bounded fresh-eye subagent (2026-07-04, shared parent
worktree, read-only), reviewing the draft artifact against the live repo before
activation. All four blockers folded:

- Blocker 1 (folded → Boundaries, Low-Cost Checks): plugin export mirror
  `plugins/charness/scripts/` mirrors ALL of `scripts/`, so export sync is an
  unconditional per-slice step, not conditional on "gate wiring".
- Blocker 2 (folded → Boundaries, Slice 2): explicit ratchet policy for new
  scripts (must adopt the helper from day one; baseline never grows), renames
  (move, never add), and an exemptions file with `# why:` rationale mirroring
  the boundary-bypass precedent.
- Blocker 3 (folded → Low-Cost Checks, Slice 4+): per-migrated-script consumer
  reverse-dependency check (grep across `scripts/`, `tests/`, `.githooks/`,
  `*.sh`) and consumer tests in the commit-boundary set; hook-consumed scripts
  (e.g. `classify_push_diff.py` parsed by `.githooks/pre-push`) migrate last.
- Blocker 4 (folded → Goal): lib count corrected from ~90 to 79 `*_lib.py`
  (78 without a main guard); all other scouting counts verified exactly.

Over-worry raised, not folded:

- Slice ordering is sound; the gate's helper-adoption detection (slice 2) may
  need a cheap tweak if the pilot (slice 3) forces a helper API change —
  accepted rework, not a reorder.
- Tension between "baseline shrinks to empty" and stop condition (1) (a
  byte-exact-pinned consumer parks a script on the baseline): User Acceptance
  already hedges with "empty at full completion" and the stop condition files
  an issue, so the gap self-documents.
- stdout-composition risk for the 78 ad-hoc scripts is covered by the
  mechanics-only Non-Goal plus the folded reverse-dependency check.

Reviewer verdict: "solid, well-scouted draft — hold activation for four cheap
folds; no structural rework of the slice plan or scope needed." Folds applied.

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
