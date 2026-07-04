# Achieve Goal: Consistent --json output mode across repo CLI scripts via shared helper and tests

Status: draft
Created: 2026-07-04
Activation: `/goal @charness-artifacts/goals/2026-07-04-script-json-output-mode.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-07-04-script-json-output-mode.md` after confirming the draft is
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

Every operator-facing argparse CLI entrypoint under `scripts/` supports a
`--json` flag that emits one consistent, machine-parseable envelope built on a
single shared helper module, and a checked-in coverage guard keeps that true:

- a shared helper (working name `scripts/json_output_lib.py`) owns the envelope
  shape and the emit path; its contract is decided by a slice-1 survey of the
  72 existing `scripts/` emitters (measured 2026-07-04: `"status"` in 38,
  `"ok"` in 15, `"errors"` in 5, `"warnings"` in 7, none combining all three)
  and absorbs the existing prior art — four near-identical
  `emit_payload(payload, json_mode=...)` helpers in
  `worktree_create_lib.py` / `worktree_cleanup_lib.py` /
  `worktree_audit_lib.py` / `worktree_doctor_lib.py` plus
  `scaffold_artifact_lib.emit_payload_main` — rather than starting greenfield
- the 74 argparse CLIs that currently lack `--json` (measured 2026-07-04:
  144 argparse non-`_lib` CLIs total, 74 without the flag) gain it via the
  helper, in batches
- a coverage/ratchet test pins the compliant set with a checked-in baseline so
  the non-compliant list only shrinks and new CLIs cannot regress
- unit tests cover the helper itself; a parametrized smoke test proves each
  converted script's `--json` output parses and carries the envelope keys

Outcome capability: any consumer (operator, hook, CI, downstream script) can
run `python3 scripts/<cli>.py ... --json` on a covered script and parse a
predictable envelope. Failed capability today: 74 CLIs have no machine-readable
mode at all, and the 72 that do each hand-roll their own shape (only small
pockets of shared emit helpers exist, in the worktree/scaffold lib family).

## Non-Goals

- No change to the existing JSON key shapes of the 72 scripts that already
  emit `--json` output. Consumers (tests, hooks, CI, skill bodies) parse those
  shapes today; convergence onto the helper is per-script opt-in and only when
  the output stays byte-compatible or strictly additive.
- No `--json` flag for `_lib.py` modules (they are imported, not invoked), for
  shell scripts (`scripts/*.sh`), or for skill-owned scripts under
  `plugins/charness/skills/*/scripts/` (exported portable surfaces with their
  own contracts; a follow-up goal may extend the convention there).
- No new CLI framework, no argparse replacement, no output-schema registry
  beyond the one helper and its tests.
- No provider/live/release proof claims: this is local CLI behavior; proof is
  deterministic local test execution.
- No push or release; `achieve` does not push, and no release surface is
  touched unless a slice edits `docs/generated/cli-reference.md` via its
  renderer (doc regeneration, not a version bump).

## Boundaries

- External side-effect scope: none requested and none planned — all slices are
  local mutate/sync/verify work. If a slice unexpectedly needs remote CI or
  publish, that approval is phase-scoped, must be requested explicitly, and
  does not carry forward.
- Backward compatibility is a hard boundary: no existing consumer-visible JSON
  key may change meaning or disappear. Any script where helper adoption cannot
  keep output compatible stays on its current shape and is recorded, not
  forced.
- Smoke-test invocation is **in-process** (import + `main(argv)` / `runpy`),
  never subprocess-per-script: the boundary-bypass ratchet
  (`scripts/check_boundary_bypass_ratchet.py`, no-new-keys policy) flags test
  files combining spawn tokens with `scripts/*.py` path literals, so a
  subprocess smoke over 74 scripts would add up to 74 ratchet keys and fail.
  If in-process invocation proves infeasible for a family, the alternative —
  registering one deliberately-exempted shared script-entrypoint smoke harness
  in `scripts/boundary-bypass-exemptions.txt` (its entries already anticipate
  this) — is a policy decision recorded in the Operator Decision Queue first,
  never stumbled into mid-slice.
- Side-effectful or contract-gated scripts are never blindly executed by the
  smoke: `run_cautilus_eval.py` (cautilus is eval-only, ask-before-run per
  CLAUDE.md), `install_machine_local.py`, `bootstrap_runtime.py`,
  `refresh_current_pointer.py`, `sync_root_plugin_manifests.py`,
  `export_plugin.py`, `migrate_backtick_file_refs.py`, and any others slice 2
  classifies. The smoke harness is driven by a data recipe table with a
  per-script disposition: safe-args in-process run, or `excluded-from-exec`
  with the emit path proven instead by direct unit tests of its `main`/emit
  function. Exclusions are recorded, not silent.
- `scripts/check_python_lengths.py` gate: repo script files cap at 480 lines;
  batch conversions must not push any script over, and the helper stays small.
  Known hot spots in the conversion list: `run_skill_efficiency_ab.py` sits at
  479/480 and `grade_skill_outcome.py` at 448 — these need a prior split or a
  recorded exclusion before their batch, not a mid-edit surprise. The
  parametrized smoke module plans for TEST_FILE_MAX 800 by keeping recipes in
  a data file, not inline code.
- Changed-line mutation coverage: all `scripts/*.py` sit in the core-python
  mutation pool, so edited lines fall under
  `scripts/check_changed_line_mutation_coverage.py`. Executed smokes cover the
  emit path (subprocess/in-process coverage is captured); any
  `excluded-from-exec` script must get its changed lines covered by direct
  unit tests or the gate reds.
- Test-duplication pressure: new tests concentrate in one parametrized module
  per concern (helper unit tests; conversion smoke test) instead of per-script
  test files; every test-adding slice records `--test-pressure` in its slice
  log entry.
- Exit-code semantics are preserved per script: `--json` changes the output
  channel, never the pass/fail contract that gates and hooks depend on.
- Hard phase barriers per repo contract: mutate -> sync -> verify -> publish;
  generated surfaces (`docs/generated/cli-reference.md`) re-render before
  validators run.

## User Acceptance

What the user can do to verify completion directly:

- pick any script from the converted list and run
  `python3 scripts/<cli>.py --json ... | python3 -m json.tool` — it parses and
  shows the documented envelope keys
- run the coverage guard test and see the baseline of non-compliant scripts at
  its final (smaller or empty) state:
  `python3 -m pytest tests/test_script_json_output.py -q`
- read the helper module docstring — it is the canonical envelope contract —
  and inspect the checked-in baseline file for the residual exclusion list
  (note: `docs/generated/cli-reference.md` renders only the `charness` CLI,
  not `scripts/*.py`, so it is deliberately NOT an acceptance surface here)

## Agent Verification Plan

### Low-Cost Checks

- `python3 -m pytest tests/test_json_output_lib.py -q` (helper unit tests)
- per-batch smoke: parametrized in-process invocation (`main(argv)` via the
  recipe table) asserting the output parses as JSON and carries the envelope
  keys; manual spot checks may pipe through `python3 -m json.tool`
- `python3 scripts/check_python_lengths.py` and targeted
  `python3 -m pytest tests/quality_gates -q -k length` where applicable

### High-Confidence Checks

- coverage/ratchet test over the full argparse CLI inventory with the
  checked-in baseline (list of not-yet-converted scripts) — proves the "all
  covered CLIs" claim deterministically instead of by prose
- broad pytest at bundle boundaries via `run_slice_closeout.py` with the
  verification lock at final closeout; duplicate-pressure ratchet consulted
  when test files grow
- changed-line mutation coverage
  (`scripts/check_changed_line_mutation_coverage.py`) over each batch —
  `excluded-from-exec` scripts need direct unit coverage of their changed
  lines, per Boundaries
- boundary-bypass ratchet (`scripts/check_boundary_bypass_ratchet.py`) stays
  green: the smoke design is in-process specifically so no new bypass keys
  appear

### External Or Live Proof

- none planned; explicit non-claim — no provider, host-integration, or release
  proof is made by this goal. Local deterministic checks are the ceiling.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Envelope survey + shared helper `scripts/json_output_lib.py` + unit tests; absorb the worktree/scaffold `emit_payload` prior art | Contract first; everything else builds on it | helper module, `tests/test_json_output_lib.py` green, survey table in slice log | planned |
| 2 | Coverage inventory + ratchet baseline test (`tests/test_script_json_output.py`) + per-script invocation recipe table with exec/excluded dispositions | Makes "all scripts" measurable before mass edits; ratchet prevents regression; recipes settle safe invocation up front | baseline JSON of 74 non-compliant CLIs checked in, recipe table with dispositions, test green | planned |
| 3 | Batch A adoption: `validate_*` CLIs (29) | Largest homogeneous family; validators share output habits | baseline shrinks by 29, parametrized in-process smoke green | planned |
| 4 | Batch B adoption: `check_*` CLIs (18) | Second homogeneous family | baseline shrinks by 18, smoke green | planned |
| 5 | Batch C adoption: remaining CLIs (`run_*`, `render_*`, `build_*`, misc, 27); pre-split or record exclusion for the 480-line hot spots first | Completes the surface | baseline empty or residual list with per-script recorded reason | planned |
| 6 | Docs + closeout: envelope contract documented in the helper docstring (+ a `docs/development.md` note if it fits), final gate | Canonical contract surface; `cli-reference.md` does not cover `scripts/*.py` | doc diff, broad pytest with verification lock, final report | planned |

Batch slices are mechanical fan-out over a known work-list; per the repo
Dynamic Workflows standing opt-in, the during-phase may orchestrate a batch
with worktree-isolated agents when a batch is large enough to earn it —
judgment at slice time, evidence in the slice log.

## Operator Decision Queue

- Decision: should the 72 existing ad-hoc `--json` emitters converge onto the
  helper (beyond opt-in byte-compatible cases) in a follow-up goal?
  - Owner: operator
  - Why deferred: convergence risks breaking consumers of current shapes; this
    goal deliberately freezes existing shapes (Non-Goals)
  - Unblock action: operator says whether a follow-up convergence goal is wanted
  - Revisit trigger: closeout of this goal (final report re-surfaces it)
- Decision: if in-process smoke invocation proves infeasible for a script
  family, approve registering one shared script-entrypoint smoke harness as a
  deliberate `scripts/boundary-bypass-exemptions.txt` entry?
  - Owner: operator
  - Why deferred: the default design (in-process invocation) avoids the
    question entirely; the exemption is a ratchet-policy change
  - Unblock action: operator approves the exemption entry text
  - Revisit trigger: slice 2 recipe-table work hits an in-process dead end
- Decision: extend the convention to skill-owned scripts under
  `plugins/charness/skills/*/scripts/`?
  - Owner: operator
  - Why deferred: exported portable surfaces have a separate contract and
    validation path; bundling them would broaden scope past the ratchet
  - Unblock action: operator approves a follow-up goal
  - Revisit trigger: closeout of this goal

## Coordination Cues

- `Routing: find-skills -> impl (slice execution) — task-text probe (2026-07-04, read-only summary) returned no support-skill match; create-cli's structured-output contract references consulted at slice 1 design time; quality routes gate-posture questions.`
- Gather: n/a — no external sources; all context is repo-local scans and repo docs.
- Release: n/a expected — no version bump; add a `Release:` line only if a release surface is unexpectedly touched.
- Issue closeout: n/a — no tracked issue is resolved by this goal; off-goal findings route through `issue` with references recorded below.

## Discuss Before Activation

- Discuss before activation: resolved — broad bundled scope (74 CLIs edited across 3 batch slices) is accepted deliberately: batches are homogeneous families, each batch is one reviewable slice with fresh-eye critique, and the ratchet baseline makes partial progress safe to stop at any slice boundary. Operator confirms scope by activating; shrink by deleting batch rows before `/goal` if unwanted.
- Discuss before activation: resolved — proof-level non-claim: no provider/live proof; the goal's ceiling is local deterministic tests (helper units, parametrized smoke, ratchet, broad pytest). Stated in Agent Verification Plan and repeated in the final report.
- Discuss before activation: resolved — existing `--json` emitters keep their current output shapes (backward-compat hard boundary); convergence is queued as an operator decision, not silently bundled.

## Slice Log

## Context Sources

- repo scan 2026-07-04 (this shaping session + fresh-eye reviewer
  verification): 270 `scripts/*.py`; 144 argparse non-`_lib` CLI entrypoints;
  74 lacking `--json` (validate_* 29, check_* 18, remainder 27); 72 existing
  emitters with heterogeneous envelopes (`"status"` in 38, `"ok"` in 15,
  `"errors"` in 5, `"warnings"` in 7, none combining all three); prior art:
  `emit_payload` helpers in the four `worktree_*_lib.py` modules and
  `scaffold_artifact_lib.emit_payload_main`
- `charness-artifacts/find-skills/latest.md` + read-only
  `--recommend-for-task` probe output (no support-skill match; 2 support
  skills exist but none intent-matched this task text)
- `docs/conventions/implementation-discipline.md` (sync-before-verify,
  generated surfaces) — binding for slices 3-6
- `docs/design-north-star.md` (judgment on reversible work; ratchet gates keep
  teeth where a wrong answer escapes — the coverage baseline is that tooth)
- `plugins/charness/skills/create-cli/SKILL.md` (structured output contract
  guidance for repo-owned CLIs) — design input for slice 1
- `charness-artifacts/retro/recent-lessons.md` (read before this shaping;
  relevant trap: broad-gate/test-packaging pressure from many small test files
  — folded into the one-parametrized-module boundary)
- precedent for ratchet-with-baseline: `scripts/boundary-bypass-baseline.json`
  + `scripts/check_boundary_bypass_ratchet.py`

## Interview Decisions

- Mode (artifact-only vs implementation-continuation): family {shape-and-save
  draft; shape-then-execute}. Chosen: artifact-only draft. Reason: prose
  "목표를 잡아줘" asks to *set* the goal; `/goal` activation stays the
  operator's explicit action. single-point: request wording settles it.
- Scope of "모든 repo 스크립트" (all repo scripts): family {argparse CLIs in
  `scripts/` only; + `_lib` modules; + shell scripts; + skill-owned scripts;
  literally every file}. Chosen: argparse non-`_lib` CLI entrypoints under
  `scripts/`. Reason: `_lib` modules are imported not invoked; shell scripts
  need a different mechanism; skill scripts are exported portable surfaces
  with a separate contract (queued as operator decision). axis: surface tier
  (repo-internal scripts vs exported plugin surfaces) — the repo already
  varies on this axis via the export/packaging boundary, so the goal pins the
  repo-internal tier only.
- Envelope shape: family {invent a new canonical envelope; adopt a measured
  dominant convention; per-family envelopes}. Chosen: decide from the slice-1
  survey of the 72 existing `scripts/` emitters before the helper is frozen —
  there is NO single dominant convention today (`"status"` 38, `"ok"` 15,
  `"errors"` 5, `"warnings"` 7, none combining all three; an earlier draft's
  "`resolve_adapter.py`-style dominant convention" anchor was wrong — that
  script lives only under skill trees, out of this goal's scope — and was
  corrected by the plan critique). Reason: existing emitters and their
  consumers anchor whatever the helper picks; the survey makes the pick
  evidence-based instead of anchored. axis: none — output envelope is the
  very axis this goal collapses; single-point by design after slice 1.
- Existing ad-hoc `--json` emitters: family {force-migrate to helper; opt-in
  byte-compatible migration; freeze}. Chosen: freeze shapes, opt-in
  migration. Reason: consumer breakage risk outweighs uniformity; convergence
  is a queued operator decision. single-point: consumer-compat reasoning.
- Timebox: none — the user gave no time budget, so timebox fields are omitted
  per lifecycle (`Timebox:` only when a budget is given). single-point:
  request wording.
- Host/provider anchoring probe: the helper and flag are host-neutral
  `python3` CLI surface; no host, provider, or profile axis varies the design.
  single-point: python3 CLI behavior is identical across the hosts this repo
  supports.

## Plan Critique Findings

Reviewer provenance: bounded fresh-eye subagent (read-only, shared worktree),
2026-07-04, spawned by the shaping session per the repo standing delegation
contract; 4 blockers + 5 concerns returned, all folded.

Blockers folded:

1. Boundary-bypass ratchet collision — a subprocess smoke over 74 scripts
   would add up to 74 new ratchet keys. Folded: smoke is in-process
   (`main(argv)`/runpy) by design (Boundaries); the exemption-harness
   alternative is an explicit Operator Decision Queue item, not a mid-slice
   stumble.
2. False envelope anchor — `resolve_adapter.py` is not in `scripts/`, and no
   `ok`/`errors`/`warnings` dominant convention exists (measured: `status` 38,
   `ok` 15, `errors` 5, `warnings` 7). Folded: Goal, Context Sources, and
   Interview Decisions now carry the measured distribution; slice 1 decides
   from the survey.
3. Wrong acceptance surface — `docs/generated/cli-reference.md` renders only
   the `charness` CLI. Folded: acceptance/doc surface is the helper docstring
   + checked-in baseline; slice 6 rewritten; the cli-reference non-claim is
   stated in User Acceptance.
4. Unsafe smoke execution — `run_cautilus_eval.py` (eval-only ask-before-run)
   and six machine/worktree mutators must never be blindly executed. Folded:
   recipe table with per-script exec/`excluded-from-exec` dispositions
   (Boundaries, slice 2), with excluded scripts proven via direct unit tests.

Concerns folded: batch counts corrected to 29/18/27; 480-line hot spots named
(`run_skill_efficiency_ab.py` 479/480, `grade_skill_outcome.py` 448);
changed-line mutation coverage gate added to High-Confidence Checks; prior-art
`emit_payload` helpers named as slice-1 absorption input; smoke recipes live in
a data file to respect TEST_FILE_MAX 800.

Over-worry raised but not folded (reviewer's own counterweight): hidden stdout
consumers (default output and exit codes are frozen, so current parsers are
untouched); batch sizes too large (homogeneous mechanical batches with a
ratchet safe-stop are more reviewable than fragmenting); ratchet-baseline
design doubts (matches `boundary-bypass-baseline.json` precedent; copy its
schema-version pinning); scope exclusions as dishonesty (explicitly queued
operator decisions with revisit triggers).

## Off-Goal Findings

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
