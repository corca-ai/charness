# Achieve Goal: Consistent --json output mode across repo scripts via shared helper and tests

Status: draft
Created: 2026-07-04
Activation: `/goal @charness-artifacts/goals/2026-07-04-consistent-json-output.md`
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
- Next action: activate with `/goal @charness-artifacts/goals/2026-07-04-consistent-json-output.md` after confirming the draft is
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

Every CLI-shaped Python script under `scripts/` that offers `--json` emits it
through one shared helper module (`scripts/json_output_lib.py`), with unit
tests for the helper and a conformance gate that keeps future scripts on the
contract. "Consistent" means: one flag name (`--json`), one emission path (the
helper), JSON emitted on stdout only, and machine-parseable output on both
success and failure exits. **Migration is shape-preserving by default**: the
helper standardizes how JSON is emitted, not each script's existing top-level
keys — whether any uniform top-level shape (e.g. an `ok`-style status key) is
adopted, and for which scripts, is slice 1's survey decision, with the
`ok`-shape reserved at most for new and never-consumed scripts. Scripts
without `--json` today are exempt-by-default via a checked-in allowlist unless
a named consumer exists or is planned; the goal completes when every
unexempted CLI script conforms to the emission contract.

Baseline measured 2026-07-04 (reviewer-verified): 270 Python files under
`scripts/`, 146 CLI-shaped (own a `main`/`__main__` entrypoint, excluding
`*_lib.py`), 78 with a hand-rolled `--json` flag (only 16 of which emit an
`ok` key — the existing shapes are heterogeneous), 76 CLI scripts with no
`--json`, zero scripts using a shared emission helper.

## Non-Goals

- Shell scripts (`scripts/*.sh`) — different runtime; not part of this goal.
- Library modules (`scripts/*_lib.py`) and other non-entrypoint helpers — no
  CLI surface to standardize.
- Plugin skill scripts (`plugins/charness/skills/*/scripts/`) — they carry
  per-skill output contracts and are exercised by skill-level tests; drift
  found there is filed through `issue`, not fixed here.
- Changing any script's default human-readable output, exit-code semantics,
  or functional behavior beyond the output mode.
- Introducing additional output formats (`--format`, YAML, etc.); the helper
  API should not preclude them, but shipping them is out of scope.

## Boundaries

- External side-effect scope: none requested — this goal is local-only (code,
  tests, gate wiring, artifact updates). No publish / push / remote-CI / apply
  lane is approved or assumed; any approval later granted is phase-scoped and
  does not carry forward. After an approved lane completes, done-early
  test-only continuation is local by default.
- Consumed-shape compatibility: scripts whose current `--json` output is
  consumed by tests, hooks, CI, other scripts, **or prose contracts
  (CLAUDE.md, SKILL.md files, docs/)** must keep field compatibility, or every
  consumer is updated in the same slice with its tests. Known high-fan-in
  pins: 116 test files reference `--json`; CLAUDE.md pins
  `plan_cautilus_proof.py --json`'s top-level `next_action` /
  `must_ask_before_running` fields (4 pin sites across CLAUDE.md + skill
  references); `plugins/charness/skills/{spec,impl}/SKILL.md` invoke
  `scripts/plan_risk_interrupt.py --json`. A migration batch never lands with
  a knowingly broken consumer, and prose-contract edits carry their own
  contract-change discipline (recent-lessons read required).
- The conformance gate is a ratchet: it baselines current offenders and blocks
  new drift immediately; it never red-bars the broad suite for pre-existing
  offenders mid-migration.
- Every allowlist exemption entry carries an inline reason; a bare path is a
  gate failure.
- Helper stays stdlib-only and host-agnostic (harness portability rule); no
  adapter knob is expected because emission behavior does not vary by host.

## User Acceptance

What the user can do to verify completion directly:

- Pick any CLI script under `scripts/` and run it with `--json`: stdout is
  parseable JSON with the documented top-level shape (or the script appears in
  the exemption allowlist with a reason).
- Run the conformance gate script itself with `--json` (dogfood): it reports
  `ok: true` and zero unexempted offenders at completion.
- Run the helper's unit tests (`pytest tests/test_json_output_lib.py`): green.

## Agent Verification Plan

### Low-Cost Checks

- Unit tests for the shared helper (success shape, failure shape, exit-code
  passthrough, non-serializable payload handling).
- Conformance gate run per batch; offender count must be monotonically
  non-increasing.
- Targeted pytest for each migrated batch's touched scripts; import smoke on
  changed files.

### High-Confidence Checks

- Full repo pytest quality gates at slice/bundle boundaries.
- Changed-line mutation coverage gate (`check_changed_line_mutation_coverage.py`)
  on helper and gate code.
- Duplicate-pressure sample via `append_slice_log.py --test-pressure` whenever
  a slice adds or expands tests; batch migrations reuse one parametrized
  conformance test rather than per-script test files to keep pressure flat.

### External Or Live Proof

- None planned. Explicit non-claim: no provider, live, remote-CI, or release
  proof is produced by this goal; all evidence is local deterministic gates.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Survey the 78 existing `--json` implementations and their consumers; DECIDE the shape commitment (default hypothesis: emission-path-only, shape-preserving); record the contract with the helper | Contract-before-code prevents migration rework; shape decision belongs to evidence, not the draft | Survey summary + shape decision in Slice Log; contract documented with the helper | pending |
| 2 | Ship `scripts/json_output_lib.py` + `tests/test_json_output_lib.py` | Single emission path is the goal's core | Helper unit tests green | pending |
| 3 | Conformance gate (`scripts/check_json_output_conformance.py`, itself helper-based) with import/AST-based detection (not grep — known literal `--json` false-positive sites exist) built on the existing ratchet mechanics (`boundary_bypass_ratchet_lib.py` pattern), + offender baseline, wired into quality gates | Stop new drift while migration proceeds without hand-rolling a parallel ratchet format | Gate green with baselined offenders; new-offender injection test red | pending |
| 4–7 | Migrate the 78 hand-rolled `--json` scripts in batches (~20/batch), shape-preserving, consumers updated in-slice | Shrink the baseline to zero safely; batch size is realistic only under shape-preserving migration | Ratchet count strictly decreasing; batch pytest green | pending |
| 8 | Allowlist-by-default pass over the 76 no-`--json` CLI scripts: exempt unless a named consumer exists or is planned; add `--json` via helper only to consumer-backed scripts | Keeps the gate's teeth for new scripts without migrating ~76 scripts nobody machine-consumes | Gate reports zero unexempted offenders; allowlist entries carry reasons | pending |
| 9 | Closeout: broad gates, retro, dispositions, final report | Final proof and reflection | `check_goal_artifact.py` complete-gate green | pending |

Expected proof cost per slice: slices 1–3 cheap-to-moderate (unit + gate
runs); batch slices cheap per batch with one broad-pytest at bundle
boundaries; slice 9 carries the broad/final gates. Test-duplication pressure:
concentrated in slices 2–3; the parametrized-gate design keeps batch slices
near-zero new test mass.

## Operator Decision Queue

- Decision: confirm the scope resolution — "모든 repo 스크립트" is shaped as
  "every CLI-shaped `scripts/*.py` that offers `--json` emits it via the
  shared helper; the 76 scripts without `--json` are allowlist-exempt by
  default (migrated only when a named consumer exists or is planned)"; shell
  scripts, `*_lib.py`, and plugin skill scripts are non-goals.
  - Owner: operator
  - Why deferred: a strong default settles it (libs and shell scripts have no
    Python CLI JSON surface; plugin scripts have per-skill contracts; the
    critique showed the no-consumer scripts are hooks/wrappers/migrators) and
    the draft is inert until `/goal`.
  - Unblock action: approve at activation, or adjust Non-Goals / Slice 8
    before `/goal` (e.g. if you want literal `--json` on all 146 CLIs).
  - Revisit trigger: `/goal` activation of this artifact.

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
value (a soft-wrapped value is tolerated now, but one line is clearest):

- `Routing: find-skills -> impl — Before-phase probe (2026-07-04, read-only --recommend-for-task) matched no support skill; slice execution routes through impl, with create-cli as the structured-output contract reference for slice 1`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — broad-scope trigger (146 CLI scripts,
  multi-batch migration) and a proof-level non-claim (no live/CI proof lane;
  local deterministic gates only). Scope fixed after fresh-eye critique as:
  the 78 existing `--json` scripts migrate to the shared helper
  shape-preserving; the 76 no-`--json` CLI scripts are allowlist-exempt by
  default (migrate only consumer-backed ones); shell scripts, `*_lib.py`, and
  plugin skill scripts excluded as Non-Goals. The operator can override the
  scope shape at activation (mirrored in `## Operator Decision Queue`). No
  irreversible or external side effect is in scope.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- This-session `scripts/` survey (2026-07-04): 270 Python files, ~146
  CLI-shaped entrypoints, 78 hand-rolled `--json` flags
  (`grep -l -- '--json' scripts/*.py`), no shared emission helper found.
- `charness-artifacts/find-skills/latest.md` — capability map; the
  `--recommend-for-task` probe for this goal ran read-only 2026-07-04 and
  matched no support skill.
- `plugins/charness/skills/create-cli/SKILL.md` — owns the repo CLI
  structured-output contract shape; slice 1's contract must align with it.
- `docs/conventions/implementation-discipline.md` — sync-before-verify order
  and mutation parallelism for the migration batches.
- `charness-artifacts/retro/recent-lessons.md` — read before gate/contract
  surface changes (slice 3 touches quality-gate wiring).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode: family {artifact-only draft; implementation-continuation}. Chose
  artifact-only — the prose ("목표를 잡아줘") asks to shape the goal, not to
  execute it; no execution request accompanies it. Stated assumption, no
  interview round-trip needed. single-point: intent reading, not a system axis.
- Scope of "모든 repo 스크립트": family {literal all 270 files; CLI-shaped
  `scripts/*.py` with reasoned allowlist; only the existing 78 `--json`
  scripts}. Chose CLI-shaped-with-allowlist. Rejected literal-all (libs and
  shell scripts have no Python CLI JSON surface to standardize) and
  78-only (fails the user's "all scripts" outcome). single-point: repo
  structure fact, not a host/provider axis.
- Flag name `--json`: family {`--json`; `--format json`; `--output json`}.
  Chose `--json` — 78 scripts already use it; changing the convention would
  multiply migration cost for zero consistency gain. single-point: repo
  convention; helper API deliberately does not preclude future formats.
- Helper location `scripts/json_output_lib.py`: matches the existing
  `*_lib.py` module convention (79 instances). single-point: repo convention.
- Host/provider axis probe: emission behavior does not vary by host; the
  helper stays stdlib-only and host-agnostic per the portability rule.
  axis: host — handled by dependency-free design, no adapter knob added.
- Timebox: none — the user supplied no work budget; timebox fields are set at
  activation if the operator gives one. Done-early policy recorded as
  `continue_next_improvement` per contract default.

## Plan Critique Findings

Reviewer provenance: bounded fresh-eye subagent critique (general-purpose
agent, read-only, shared worktree), 2026-07-04, four angles + counterweight;
evidence gathered via read-only grep/sed over scripts/, tests/, plugins/,
CLAUDE.md, docs/.

Blockers folded into this draft:

- **Shape pre-lock (folded into Goal + Slice 1):** the draft originally
  committed to a uniform top-level `ok`+payload shape before the survey, but
  only 16/78 existing `--json` scripts emit an `ok` key, 116 test files
  reference `--json`, and CLAUDE.md pins `plan_cautilus_proof.py`'s top-level
  `next_action`/`must_ask_before_running` fields — a reshape breaks a
  checked-in operating contract. Migration is now shape-preserving by
  default; the shape commitment is slice 1's evidence-backed decision.
- **Prose consumers missing from the compatibility boundary (folded into
  Boundaries):** CLAUDE.md, SKILL.md files (`spec`/`impl` invoke
  `plan_risk_interrupt.py --json`), and docs/ are consumers alongside
  tests/hooks/CI.
- **Slice 8 scope inflation (folded into Goal + Slice 8):** the 76 no-`--json`
  CLI scripts are dominated by hooks, wrappers (incl. the ask-before-run
  `run_cautilus_eval.py`), one-off migrators, and exit-code-consumed
  validators; flipped to allowlist-by-default (migrate only consumer-backed
  scripts).
- **Gate detection method (folded into Slice 3):** detection must be
  import/AST-based, not grep (`check_cli_skill_surface.py:212` and create-cli
  SKILL.md carry literal `--json` false-positive sites), and the gate reuses
  existing ratchet mechanics rather than a new parallel baseline format.

Over-worry raised but not folded:

- Flag-name / helper-path / directory-scope anchoring: repo conventions check
  out (78 existing `--json` users; create-cli endorses the flag; plugin skill
  scripts do not import `scripts/` libs), so no axis knob is needed.
- "An existing gate already covers this": verified false — no current gate
  checks script JSON emission contracts, so the new gate stands.

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
