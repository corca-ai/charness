# Achieve Goal: Consistent --json output mode across repo scripts via shared helper and tests

Status: draft
Created: 2026-07-04
Activation: `/goal @charness-artifacts/goals/2026-07-04-json-output-mode.md`
Timebox: none — operator gave no work budget; slice-count stop conditions govern instead
Activation time: set at `/goal` pursuit
Closeout reserve: final slice reserved for docs sync, broad gate, and retro (no wall-clock budget)
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
- Next action: activate with `/goal @charness-artifacts/goals/2026-07-04-json-output-mode.md` after confirming the draft is
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

Every Python CLI entrypoint under repo-root `scripts/` offers a consistent
`--json` output mode backed by one shared helper library, with tests, and the
consistency is held durably by a conformance gate rather than a one-time sweep.

Concretely:

- A shared helper (working name `scripts/json_output_lib.py`) owns the flag
  registration (`add_json_flag(parser)`) and emission
  (`emit(payload, as_json=..., human_renderer=...)`) so flag help text, envelope
  shape, and error/exit-code semantics stop drifting per script.
- The convention is written down once (conventions doc section referencing the
  `create-cli` structured-output contract), not re-invented per script.
- A conformance check with a burn-down baseline (repo ratchet idiom, cf.
  `check_boundary_bypass_ratchet.py`) classifies every `scripts/*.py`
  entrypoint as conforming / baselined / exempt-with-reason, blocks new
  nonconforming entrypoints immediately, and shrinks the baseline as migration
  waves land.
- Migration waves convert existing entrypoints to the helper
  behavior-compatibly (existing JSON consumers — docs, CI, other scripts —
  keep working), highest-traffic operator-facing scripts first.

"모든 repo 스크립트" (all repo scripts) is achieved as: all entrypoints either
migrated or held by the ratchet with an explicit baseline entry, and the
baseline monotonically shrinking — not necessarily every one of ~148 CLIs
hand-converted in this single goal if a stop condition fires first.

## Non-Goals

- Shell scripts (`scripts/*.sh`, 8 files) — the helper is Python; shell
  scripts stay human-output-only (exempt class in the gate). Honest basis:
  these are NOT all thin wrappers — `check-secrets.sh` and `check-shell.sh`
  have no Python equivalent and `run-quality.sh` is a ~550-line orchestrator.
  They are exempted because porting shell gates to Python is a different,
  larger goal, not because a JSON path already exists for them.
  `single-point: language boundary of the Python helper.`
- Plugin skill scripts (`plugins/charness/skills/*/scripts/`,
  `skills/public/*/scripts/`) — portable skill surfaces must not import a
  repo-root lib; forcing the shared helper there breaks the portability
  contract. `axis: surface (repo-root scripts vs portable skill scripts vary
  deliberately).` A follow-up issue may propose a skill-shared equivalent.
- Library modules (`scripts/*_lib.py` and other non-entrypoint files) — no CLI,
  no flag; they are out of the gate's entrypoint classification.
- Changing existing JSON *payload schemas or top-level shapes* — this goal
  standardizes the flag, emission path, and conventions for *new or newly
  converted* output. Precedence rule (settles the envelope-vs-compat tension):
  any standard envelope applies only to human-only entrypoints gaining
  `--json` for the first time; the 78 already-JSON scripts keep their existing
  top-level shape byte-compatible for consumers (only the emission call routes
  through the helper), and the conformance gate checks helper usage, never
  envelope shape. Consumer scale making this non-negotiable: ~232 test files
  call `json.loads` on script output. Schema redesigns are off-goal findings.
- Scripts that are JSON-only by design (always emit JSON with no human mode):
  they adopt the helper's emission path where cheap, but adding a human
  renderer to each is out of scope.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- No external side-effect lane requested or planned: no push, publish, release
  bump, or remote CI trigger inside this goal. All proof is local.
- Behavior-compatibility boundary: any script whose JSON output is consumed by
  another script, test, doc example, or CI step must keep its consumer contract
  green in the same slice that migrates it (per-branch falsifiable proof in the
  same slice — recent-lessons rule).
- Generated/mirror surfaces: edit sources only; if a migrated script is
  mirrored into a plugin/export surface, run the owning sync step before
  validators (implementation-discipline order).
- Gate additions respect existing broad-gate economics: the conformance check
  must be cheap (static scan, no subprocess-per-script) so it can sit in the
  default gate lane without slowing it.
- Stop conditions: (a) a migration wave surfaces a consumer contract that
  cannot be kept behavior-compatible without a schema change → file the issue,
  leave that script in the baseline with a reason, continue; (b) the dup
  ratchet or another broad gate reds for accumulated suite debt beyond this
  goal's new slices → classify per the After-phase rule, name the smallest
  structural cleanup, and stop the wave rather than force the gate; (c) two
  consecutive waves shrink the baseline by fewer than 5 entries each → close
  early with the ratchet holding the remainder and report the residual count.
- Reporting expectations: slice log per wave with baseline count before/after;
  final report separates migrated-set, baselined-remainder-with-reasons, and
  exempt classes; no completion claim while an unclassified entrypoint exists.

## User Acceptance

- Pick any 2–3 scripts named in the migrated set and run
  `python3 scripts/<script>.py --json | python3 -m json.tool` — valid JSON,
  and `--help` shows the shared, identical flag help text.
- Run the conformance gate (`pytest tests/... -k json_output` or the check
  script directly) and see: zero unclassified entrypoints, baseline count
  strictly below the starting inventory count recorded in slice 1.
- Read the conventions doc section and confirm it matches what the scripts do.

## Agent Verification Plan

### Low-Cost Checks

- Unit tests for the helper (flag registration, JSON vs human path, stdout vs
  stderr emission stream, envelope, exit-code passthrough, non-serializable
  payload error).
- Conformance gate run (static scan) — commit-boundary cheap check.
- `--json | python3 -m json.tool` smoke on each script touched in a slice.
- `run_slice_closeout.py --skip-broad-pytest` at pre-lock commit boundaries.

### High-Confidence Checks

- Broad pytest at slice boundaries (migration waves can break consumer tests).
- Duplicate-pressure sample via `append_slice_log.py --test-pressure` on every
  test-adding slice (helper tests + gate tests will push the dup ratchet; the
  expected pressure is recorded per slice, cf. Test-duplication pressure note
  below).
- Changed-line mutation coverage where the existing gate demands it.
- Fresh-eye bounded slice critique at slice boundaries per the frame's packet.

### External Or Live Proof

- None planned; explicit non-claim: no remote CI, no release, no
  provider/live proof. Local gates and broad pytest are the ceiling for this
  goal.

Test-duplication pressure: helper tests are new-surface (low dup risk); the
conformance gate test and per-wave consumer-contract tests risk near-duplicate
shapes across waves — waves reuse one parametrized test table instead of
copying test functions per script, and each wave slice records a
`--test-pressure` sample.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Inventory & contract: classify every `scripts/*.py` as entrypoint/lib; record current output behavior on FOUR dimensions — json-always / `--json` flag / human-only, output stream (stdout vs stderr; ~36 of the 78 `--json` scripts touch stderr, and e.g. `check_github_actions.py` emits its JSON report to stderr with rc=1, asserted by `tests/quality_gates/test_python_and_security_gates.py`), exit-code semantics, and known consumers; write the convention section referencing the `create-cli` structured-output contract | Everything downstream keys off the classification and the written contract; stream/exit semantics are the hardest compat constraint and must shape the helper API before it ships | Checked-in inventory (JSON artifact) + conventions doc section; counts: ~148 argparse CLIs, ≤78 with ad-hoc `--json` today (raw grep upper bound; slice 1 produces the exact number) | planned |
| 2 | Shared helper `scripts/json_output_lib.py` + unit tests; API must carry stream and exit-code semantics (not stdout-only), per the slice-1 inventory | The contract needs one owning implementation before any migration | Helper + green unit tests covering stdout and stderr emission paths and exit-code passthrough; pressure sample | planned |
| 3 | Conformance gate with burn-down baseline (ratchet idiom) + red/green demo; the static scan must detect the helper *emission call*, not merely flag registration, so a script cannot conform by registering the flag and printing ad hoc | Locks "all scripts" durably; blocks new nonconforming entrypoints from slice 3 onward | Gate script/test, baseline file seeded from slice-1 inventory, demonstrated red on a synthetic script that registers the flag but bypasses the emit path | planned |
| 4 | Migration wave 1: highest-traffic operator-facing scripts (gate/validator scripts named in CLAUDE.md and conventions docs) | Highest operator value; exercises the helper against the hardest consumer contracts early | Wave converted, consumer tests green, baseline count shrinks; pressure sample | planned |
| 5..N | Migration waves 2..N in batches of ~15–25, ordered by consumer-contract risk (low-risk batched, risky ones individually) | Burn down the baseline monotonically | Per-wave: broad pytest green, baseline shrink recorded in slice log | planned |
| final | Closeout: docs sync, full gate lane, `describe_goal_closeout_shape.py` preflight, retro | Prove-and-reflect phase | Final verification section bound; retro artifact | planned |

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

Seeded at draft (During-phase fills the rest): the Before-phase
`find-skills --recommend-for-task` probe returned no support-skill match
(note recorded in Context Sources); expected During-phase routes are `impl`
for migration slices, `quality` for the conformance-gate design slice, and
`create-cli` as the owning contract reference for structured output — confirm
each with a phase-boundary `find-skills` probe when the slice starts.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — broad-scope trigger ("모든 repo 스크립트" over a 286-file `scripts/` surface, ~148 argparse CLIs). Settled by reshaping "all" as helper + conformance ratchet + prioritized migration waves with an explicit stop condition, instead of one big-bang sweep; scope excludes shell scripts, libs, and portable plugin-skill scripts (see Non-Goals). Surfaced verbatim in the Before-phase final report so the operator reads this scope definition before running `/goal`; overriding it (e.g. demanding 100% hand-migration of all ~148 CLIs in this goal, or including skill scripts) means reshaping via `/achieve @...` first. Run length is bounded despite `Timebox: none`: expected ~4–9 wave slices, and stop condition (c) (two consecutive waves shrinking the baseline by <5 entries) forces an early close with the ratchet holding the remainder. No live/prod proof, issue close, or irreversible side effect is in scope.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- Operator prompt (2026-07-04, Korean): "모든 repo 스크립트에 일관된 --json
  출력 모드를 공유 헬퍼와 테스트로 추가하는 목표를 잡아줘" — the sole external
  intent source; no URL/issue named. Gather: n/a — no external source.
- Before-phase repo scout (this session, reproducible): `ls scripts/ | wc -l`
  → 286 files; `grep -ln argparse scripts/*.py | wc -l` → ~148;
  `grep -ln -- --json scripts/*.py | wc -l` → 78; only ad-hoc prior art is
  `emit_json` in `scripts/rename_allowlist_scan_lib.py:154`.
- `find-skills` task-text probe (read-only, `--summary`): no support-skill or
  public-skill recommendation matched; inventory counts 20 public / 2 support
  skills. Probe left no artifact by design.
- `plugins/charness/skills/create-cli/SKILL.md` — owning contract for
  repo-owned CLI structured output; slice 1 must reference, not duplicate, it.
- `scripts/check_boundary_bypass_ratchet.py` + `scripts/boundary-bypass-baseline.json`
  — the repo's existing burn-down-ratchet idiom the conformance gate copies.
- `charness-artifacts/retro/recent-lessons.md` (read 2026-07-04): per-branch
  falsifiable proof in the same slice; edit sources not generated mirrors.
- `docs/handoff.md` (2026-07-04): no competing mandatory work; brittle-file
  warning (`tests/test_handoff_plan.py` reds broad pytest on ≥60-line
  handoff) — this goal does not touch the handoff beyond normal closeout.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode (artifact-only vs implementation-continuation): chosen artifact-only
  draft. The prose "목표를 잡아줘" names goal-shaping explicitly — strong
  default, stated instead of asked. `/goal` remains the operator's pursue
  action; nothing executes from this draft.
- Meaning of "all scripts" (family: literal 286 files / all ~148 Python CLIs
  hand-migrated in-goal / helper+ratchet with prioritized waves): chosen
  helper+ratchet+waves. Literal-all includes libs and shell with no CLI
  surface; hand-migrating 148 CLIs in one goal has slice-count and
  consumer-breakage risk out of proportion to value, and the ratchet is the
  repo's proven idiom for durable "all". `axis: script-surface (repo-root
  scripts vs portable skill scripts vs shell)` — recorded per surface in
  Non-Goals.
- Flag surface (family: `--json` boolean / `--format=json|text` /
  JSON-by-default): chosen `--json` boolean. It is the operator's literal
  request, matches 78 existing scripts and repo docs (`sync_support.py
  --json`), so migration is additive; `--format` would rename a widely
  documented flag for no operator-visible gain. `single-point: repo-internal
  CLI convention, no host/provider axis varies on it.`
- Helper location (family: `scripts/json_output_lib.py` / shared package under
  `scripts/lib/` / duplicate into skill scripts): chosen repo-root
  `scripts/json_output_lib.py`, matching the sibling `*_lib.py` convention and
  the existing test loader (`tests/script_loader.py`). Skill-script duplication
  rejected — portability boundary, see Non-Goals.
- Enforcement (family: one-time sweep / conformance gate with baseline /
  convention doc only): chosen gate-with-baseline; doc-only rots and a
  one-time sweep regresses on the next new script — north-star prefers
  validators over prose rituals.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Provenance: bounded fresh-eye subagent (fresh context, shared worktree,
read-only), 2026-07-04, reviewing this draft against live repo facts before
the operator report. All three blockers folded; four non-blocking items
folded or dispositioned.

Blockers folded:

1. Shell-script Non-Goals bullet stated a false repo fact ("~4 wrappers, all
   delegating to Python equivalents"; reality: 8 `.sh` files, two with no
   Python equivalent, one ~550-line orchestrator). Rewritten with the honest
   exemption basis (language boundary, porting is a different goal).
2. Slice-1 inventory and the helper API omitted output-stream and exit-code
   semantics — the hardest real compat constraint (`check_github_actions.py`
   emits JSON to stderr with rc=1 and a quality-gate test asserts
   `json.loads(result.stderr)`; ~36 of 78 `--json` scripts touch stderr).
   Folded into slice 1 (four inventory dimensions), slice 2 (API carries
   stream/exit semantics), and Low-Cost Checks.
3. Goal ("helper owns envelope shape") contradicted Non-Goals ("no payload
   schema changes") for the 78 already-JSON scripts (~232 test files parse
   script JSON). Settled with an explicit precedence rule in Non-Goals:
   envelope only for newly converted human-only entrypoints; already-JSON
   scripts stay byte-compatible; the gate checks helper usage, never envelope
   shape.

Non-blocking folded: gate must statically detect the emit call, not just flag
registration (slice 3); "78" marked as a raw-grep upper bound (slice 1);
misleading `upsert_goal.py` example removed from Non-Goals (it lives in skill
scripts, an excluded surface); open-ended run length named in the Discuss
line (expected ~4–9 waves + stop condition (c) early close).

Over-worry raised but not folded (reviewer's own dismissals, kept for the
record): wave batch size 15–25 (bounded by stop conditions and per-wave broad
pytest); no CI workflow parses script `--json` today (consumer boundary kept
as precaution); entrypoint classification tractability (147 `__main__` guards
≈ 148 argparse hits, so slice 1 is tractable as planned).

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
