# Achieve Goal: Make the commit-boundary structural sweep non-discretionary (#332)

Status: active
Created: 2026-06-07
Activation: `/goal @charness-artifacts/goals/2026-06-07-332-commit-boundary-sweep-enforcement.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Mode: implementation-continuation. `/achieve` shaped and saved this goal; it is
inert until `/goal` activates it, at which point the slices below execute. The
mode was a strong default (resolving a tracked GitHub issue), stated rather than
asked.

## Active Operating Frame

- Current slice: Slices 1-3 COMPLETE (root cause + fix + regression test, with
  the fix-boundary fresh-eye critique BLOCKER folded); Slice 4 (closeout) next.
- Next action: Slice 4 — doc sync, full `run_slice_closeout.py` gate, stage
  `Close #332`, `issue` validate-closeout-draft rehearsal, RCA ledger event,
  retro + disposition review.
- Slice 1 root cause (proven, falsifiable): both #329 gates
  (`validate_skill_ergonomics`, `validate_attention_state_visibility`) are fully
  wired into BOTH the cheap predict-commit plan and the full-closeout verify
  phase, and BOTH predate #329 (`a09e6d95` 2026-06-06, `86a905d7` 2026-05-31 vs
  #329 `7f0231e3` 2026-06-07). They reached the slow boundary not from a coverage
  or wiring gap (both FALSIFIED) but because the cheap sweep only *runs* on
  `git commit` / `--predict-commit` / full closeout — and at the #329 slice
  boundary the agent ran a hand-picked manual subset that invoked none. The full
  closeout also runs surface-match + cautilus BEFORE the verify-phase structural
  gates, so even there the cheap verdict is not produced first. Artifact:
  `charness-artifacts/debug/2026-06-07-332-commit-boundary-sweep-latency.md`
  (+ `latest.md`). Staged-index repro: `--predict-commit` blocks a fresh
  undeclared-`skipped` `scripts/*.py` at rc=1 in 0.8s.
- Verification cadence: cheap deterministic checks at commit boundaries
  (`run_slice_closeout.py --predict-commit`); higher-cost or fresh-eye proof at
  slice boundaries; final broad pytest + full `run_slice_closeout.py` at closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.
- Open root-cause lead (for Slice 1, sharpened by the Before-phase fresh-eye
  critique): `core.hooksPath=.githooks`, so the pre-commit hook *was* active
  during #329. Git timing shows the ergonomics fast-gate (`a09e6d95`) and the
  attention-state wiring (`86a905d7`) both predate #329, and both #329 instances
  were under wired, active gates — so "wiring added after #329" is *falsified*
  and a pure coverage gap is largely ruled out. A `pre-push` hook also runs the
  full broad gate, so violations do not actually escape the machine. The likely
  cause is *latency* (the cheap sweep was reached only inside the 7-min broad
  `run_slice_closeout`, not run first as the cheap `--predict-commit` subset)
  and/or a `--no-verify`/hook-not-run bypass. Confirm which, per gate, before
  fixing — do not harden coverage that already exists.

## Goal

Make the cheap commit-boundary structural sweep non-discretionary for the file
classes that trigger it, so a new skill-package or `scripts/*.py` edit cannot
defer `validate_skill_ergonomics` / `validate_attention_state_visibility` / the
authoring-preflight (`check_skill_surface_preflight.py`) to the slow broad gate
instead of the cheap `--predict-commit` subset. Enforce at the **existing**
pre-commit boundary as a single source of truth; root-cause first, then close
whatever lets the #329-class regression reach the slow boundary today (a
`pre-push` broad-gate backstop already prevents true escape from the machine);
keep it presence/structural only — run the existing gates, add no new judgment.
Coverage is per gate, not uniform: ergonomics is skill-package-only,
attention-state covers `scripts/**`+`skills/**` `*.py`, and the preflight check
keys on `SKILL.md` (confirm in Slice 1; do not assume the trio is uniform).

The recurrence this closes (three sessions): #329 `portable_package_issue_anchor`
+ attention-state `skipped` regressions caught only at the 7-minute broad pytest
though both are commit-boundary gates; #325/#308 authoring-preflight skips.
Memory-only reminders have not stopped it — this goal converts the reminder into
teeth.

## Non-Goals

- Not adding any new structural *judgment*, classifier, or content heuristic; the
  sweep runs the existing gates only (presence/structural).
- Not redesigning the gate framework, the surface manifest model, or the
  `mutate → sync → verify → publish` rhythm.
- Not adding a second, parallel enforcement mechanism that competes with the
  pre-commit boundary (operator chose a single source of truth — see Interview
  Decisions Q1).
- Not switching git-hook managers or introducing a third-party pre-commit
  framework.
- Not touching unrelated commit-boundary gates (ruff, mirror-drift,
  check-markdown, doc-links) beyond what root-cause shows is the actual gap.
- Not a broad-pytest economics / duplicate-pressure refactor (that is its own
  family; this goal only adds a small regression test).
- Not pushing or closing #332 out-of-band; closeout *stages* the close (see
  Discuss Before Activation and Coordination Cues).

## Boundaries

- External side-effect scope: `achieve` does not push or publish. The closeout
  commit lands on the working branch and carries `Close #332`; the maintainer's
  push auto-closes the issue. Any approval for an external side effect is
  phase-scoped and does not carry forward.
- Single enforcement point: harden the existing pre-commit boundary
  (`.githooks/pre-commit` → `run_slice_closeout.py --predict-commit` →
  `staged_commit_gate_plan`). Do not stand up a competing mechanism.
- Known backstop (do not ignore): `.githooks/pre-push` already runs the full
  broad gate (`run-quality.sh --read-only`) on non-docs-only pushes, so a
  `--no-verify`-bypassed commit is still caught before it leaves the machine.
  The problem is *latency* (the cheap gate reached only at the slow boundary),
  not true escape — frame Slice 1 and the fix accordingly.
- Per-gate coverage is not uniform (confirm in Slice 1; do not assume the trio
  covers both file classes): `validate_skill_ergonomics` is skill-package-only
  (it walks `SKILL.md`-bearing packages and fires via the `skill-packages`
  surface — a staged `scripts/*.py` never triggers it);
  `validate_attention_state_visibility` covers staged `scripts/**`+`skills/**`
  `*.py`; `check_skill_surface_preflight` keys on `SKILL.md` headroom.
- Presence/structural only: wire/repair the *existing* gates so they fire on the
  triggering staged file classes. Add no new judgment, no new gate semantics, and
  do not broaden coverage to unrelated paths beyond what root-cause shows is the
  actual gap.
- Hook-install reliability is **in scope**, but `validate_maintainer_setup.py`
  already checks `core.hooksPath` points at `.githooks` and that the hooks exist
  (surface-wired, with tests). Slice 2 *confirms that is sufficient* and extends
  it only if Slice 1 proves a concrete gap — do not rebuild it. Keep any change
  source-repo-scoped (hooks install for maintainer source repos only, by design).
- Root-cause gates the fix: do not assume the issue's example remedy ("add a
  pre-commit hook") — the hook already exists and is active here, and a pure
  coverage gap is largely ruled out (both #329 gates predate #329 and were
  active). Slice 2's fix shape is whatever Slice 1 proves, nothing more.

## Discuss Before Activation

Discuss before activation: resolved — (1) #332 closes via a staged `Close #332`
on the closeout commit in this harness source repo (destination: upstream-harness
= this repo); `achieve` does not push or close out-of-band. (2) Per operator
decision, the fix hardens the existing pre-commit enforcement point only — no
parallel mechanism. (3) Hook-install reliability is in scope. (4) The concrete
fix shape is gated on Slice 1's root-cause and must not be pre-assumed. No
live/prod proof, no irreversible side effect, and no broad multi-issue bundle is
involved — references to #308/#325/#329 are recurrence evidence, not a bundle.

## User Acceptance

After activation completes, the user can verify directly:

1. Stage a deliberate #329-class violation in a new file — e.g. a literal
   `(#332)`-style issue anchor inside a `skills/**` helper, or a bare `skipped`
   attention-state term in a new `scripts/*.py` docstring — and run the
   pre-commit boundary (`git commit` or `python3 scripts/run_slice_closeout.py
   --repo-root . --predict-commit`). It is **blocked at the cheap
   `--predict-commit` boundary**, not deferred to the 7-min broad run.
2. Read the Slice 1 debug artifact under `charness-artifacts/debug/` and confirm
   the recorded root cause is falsifiable and matches the fix in Slice 2.
3. Run the new regression test (`pytest tests/quality_gates/...`) and see it pin
   the blocked-at-commit behavior (and, if in scope, flag an inactive hook).
4. Confirm `#332` is staged for close on the closeout commit
   (`git log` shows `Close #332`) and that `issue` validate-closeout-draft passed.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/run_slice_closeout.py --repo-root . --predict-commit` at each
  commit boundary (the pre-commit aggregate — the commit-ready surface, not
  `pytest`).
- Targeted `pytest tests/quality_gates/test_staged_commit_gate_plan.py` (and the
  new regression test) for the changed gate plan.
- `python3 "$ACHIEVE_SKILL_DIR/scripts/check_goal_artifact.py" --repo-root .
  --goal-path <this file>` after each artifact update.

### High-Confidence Checks

- A reproduction fixture (staged index, not `base..HEAD`) proving the
  #329-class violation is blocked at the predict-commit plan. This guards against
  the recent-lessons false-green dry-run trap (a `--head-sha HEAD`-at-parent
  dry-run that excluded the changes and read "blocking: []").
- Fresh-eye slice critique at the Slice 2 fix boundary (new validator/gate-wiring
  risk) with the bounded slice packet.

### External Or Live Proof

- None required. This is a local gate-hardening change. No live/prod proof, no
  deploy, no remote CI watch is claimed; the closeout names the broad pytest +
  full `run_slice_closeout.py` result as the proof, and explicitly does not claim
  provider/live proof.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Root-cause (debug) why the #329-class regressions reached the slow broad gate despite active pre-commit + pre-push hooks | A bug-class issue gets a falsifiable root cause before any fix; coverage largely exists already, so a wrong fix is the main risk | `charness-artifacts/debug/` artifact that (a) pins each #329 instance to its owning gate, (b) proves via `git log -p`/reflog whether the commit ran pre-commit at all (`--no-verify`/hook-not-run) or the cheap subset was skipped for the 7-min broad run, (c) records the *falsified* "post-#329 wiring" hypothesis, + a failing repro | done — `2026-06-07-332-commit-boundary-sweep-latency.md`: each gate pinned to its surface, "post-#329 wiring" + "pure coverage gap" FALSIFIED by git timing + cheap-plan repro (rc=1, 0.8s); root cause = latency/ordering + slice-boundary discretion |
| 2 | Close the confirmed gap at the pre-commit boundary (likely: run the cheap structural subset first / non-skippably, or surface a bypass) — extend coverage/install only if Slice 1 proves it | Single source of truth; presence/structural only; do not rebuild existing affordances | `staged_commit_gate_plan` change blocking the reproduced violation at the cheap boundary; no duplicate of `validate_maintainer_setup` | done — `staged_commit_gate_plan.py` gains the `STRUCTURAL_SWEEP_LABELS` subset + `block_on_structural_sweep`; `run_slice_closeout.py` full path runs it FIRST (before surface-match/cautilus/broad pytest). No new judgment, no parallel mechanism, no `validate_maintainer_setup` duplicate. Fresh-eye critique: BLOCKER (main() over function limit) folded |
| 3 | Add a regression test that pins the blocked-at-commit behavior | Memory-only reminders failed across three sessions; convert to teeth | `tests/quality_gates/...` test green on fix, red without it (staged-index based) | done — 5 tests in `test_staged_commit_gate_plan.py`; the e2e `test_full_closeout_blocks_329_class_violation_at_structural_sweep` verified red-without-fix / green-with-fix; 26/26 file + 122 closeout-touching tests green |
| 4 | Closeout: doc sync, full gate, stage `Close #332`, retro + disposition review | Make the change auditable and self-applying next run | full `run_slice_closeout.py` PASS; `Close #332` staged; retro + disposition-review artifacts | planned |

## Coordination Cues

Phase routing is deferred to `find-skills` (`--recommend-for-task` /
`--recommendation-role <runtime|validation> --next-skill-id <skill>`); the routes
below are the *plan*, confirmed via `find-skills` during the run. `achieve` owns
this slot and the closeout floors; `find-skills` owns which skill answers a
boundary.

- **Routing (planned)**: Slice 1 → `debug` (root cause); Slice 2 → `impl`
  (gate-plan / install wiring); Slice 3 → `quality` + `impl` (regression test);
  Slice 4 → `quality` (final gate) + `issue` (closeout). Confirm via `find-skills`
  and record the returned route at completion.
- **Gather: n/a — no external URL/Slack/Notion/Docs/Drive source; shaped from
  GitHub issue #332 (via `gh issue view 332`) and local repo files only.**
- **Release: n/a — gate hardening with no version bump or install-manifest edit
  expected. Revisit only if a release is later cut to ship the gate.**
- **Issue closeout (planned)**: `#332` via `direct-commit` carrier (`Close #332`
  on the Slice 4 commit), validated with the `issue` skill's
  `validate-closeout-draft --carrier direct-commit --commit-message-file ...`
  rehearsal before commit.
- **RCA ledger (planned)**: record ONE converted event at Slice 4 closeout
  (`--source debug --event-kind repeated_correction --converted --durable-kind
  test --class-key commit-boundary-structural-sweep-discretionary --caught-by
  human --ref #332`); the recurrence-preventing durable artifact is the Slice 3
  regression test. Not recorded at Slice 1 (work unit not yet closed/converted).

## Slice Log

- **Slice 1 (root-cause debug), 2026-06-07.** Routed via `find-skills` → `debug`.
  - Pinned each #329 gate to its owning surface: `validate_skill_ergonomics`
    (`skill-packages`, skill-package-only), `validate_attention_state_visibility`
    (`repo-python`, `scripts/**`+`skills/**` `*.py`). Both run in BOTH the cheap
    predict-commit plan AND the full-closeout verify phase (verify cmds #7/#12,
    before broad pytest — not broad-pytest-only).
  - FALSIFIED "post-#329 wiring": ergonomics `a09e6d95` (2026-06-06) and
    attention-state `86a905d7` (2026-05-31) both predate #329 `7f0231e3`
    (2026-06-07). FALSIFIED "pure coverage gap": the cheap plan blocks the
    violation. `--no-verify`/inactive-hook ruled out (`core.hooksPath`=.githooks
    active; pre-push backstop; #329 was caught pre-commit at the agent's
    voluntary full-closeout, never escaped).
  - Root cause: latency/ordering + slice-boundary discretion — the cheap sweep
    only *runs* on `git commit` / `--predict-commit` / full closeout, and at the
    #329 slice boundary the agent ran a hand-picked manual subset that invoked
    none; the full closeout also runs surface-match + cautilus before the
    verify-phase structural gates, so the cheap verdict is not produced first.
  - Repro (staged index, NOT `base..HEAD`): a fresh undeclared-`skipped`
    `scripts/*.py`, staged, blocked by `--predict-commit` at rc=1 in 0.8s; tree
    cleaned. Artifact: `charness-artifacts/debug/2026-06-07-332-commit-boundary-sweep-latency.md`
    (+ `latest.md`), `validate_debug_artifact` green.
  - Slice 2 fix shape (proven, for fresh-eye critique at the fix boundary):
    prepend the cheap `staged_commit_gate_plan` structural subset to
    `run_slice_closeout.py`'s full path, fail-fast, reusing the predict-commit
    plan — single source of truth, no new judgment, no parallel mechanism.
    Follow-up `follow-up:slice-2-path-resolution-parity`: the cheap path keys on
    the staged index, the full path on the working-tree diff; feed the cheap
    subset the closeout's resolved changed paths.

- **Slices 2-3 (fix + regression test), 2026-06-07.** Routed via `find-skills`
  → `impl` + `quality`.
  - `scripts/staged_commit_gate_plan.py`: added `STRUCTURAL_SWEEP_LABELS`
    (attention-state, ergonomics, SKILL.md core-headroom preflight — exactly the
    #329-class gates), `structural_sweep_gates` (label-filtered SUBSET of
    `staged_commit_gate_plan`, single source of truth), `structural_sweep_planned_commands`,
    `run_structural_sweep_preflight` (fail-fast), and `block_on_structural_sweep`
    (mirrors the `_maybe_block_on_*` shape).
  - `scripts/run_slice_closeout.py`: `main()` now runs the sweep FIRST via a new
    `_run_preexecution_blocks` helper (sweep → advise → unmatched → cautilus →
    risk), before surface-match/cautilus/broad pytest. `--plan-only` lists the
    sweep first. Path-resolution parity (`follow-up:slice-2-path-resolution-parity`)
    resolved: the sweep is fed the full closeout's resolved `changed_paths`.
  - `tests/quality_gates/test_staged_commit_gate_plan.py`: +5 tests; the e2e
    `test_full_closeout_blocks_329_class_violation_at_structural_sweep` drives
    real `main()` over a tmp repo, verified red-without-fix / green-with-fix.
  - Fresh-eye slice critique (bounded subagent `a0c76fcd06b21618b`, read-only,
    shared parent worktree): **BLOCKER** — `main()` exceeded the 100-line
    function limit (the exact gate this PR hardens). Folded: extracted
    `_run_preexecution_blocks`; `main()` back under limit, behavior unchanged.
    File-length now 474/480 (advisory; the file was already in the warn band
    pre-#332). Recorded `follow-up:run-slice-closeout-module-split` (god-module
    split is a #332 Non-Goal). Reviewer's own `git checkout` slip verified
    non-corrupting (source==mirror sha256, all changes intact).
  - Proof: 26/26 gate-plan + 122 closeout-touching tests green; ruff /
    py_compile / lengths (function gate passes) / mirror byte-synced.

## Context Sources

Follow these in order to reconstruct the goal from a cold start:

1. GitHub issue **#332** (`gh issue view 332`) — the originating retro-issue:
   structural pattern, triggering instances (#329/#325/#308), proposed outcome,
   `Destination: upstream-harness`.
2. `charness-artifacts/retro/recent-lessons.md` — the "Authoring-preflight skip
   for new skill-package files" repeat trap (#308-class), and the false-green
   pre-commit dry-run lesson.
3. `charness-artifacts/goals/2026-06-07-329-disposition-form-floor.md` — the
   session where #332 was filed; records the two self-introduced regressions.
4. Infrastructure (read-only map): `.githooks/pre-commit`,
   `scripts/run_slice_closeout.py`, `scripts/staged_commit_gate_plan.py`,
   `.agents/surfaces.json`, `scripts/install-git-hooks.sh`,
   `scripts/validate_maintainer_setup.py`.
5. The three gates: `scripts/validate_skill_ergonomics.py` (→
   `skills/public/quality/scripts/validate_skill_ergonomics.py`),
   `scripts/validate_attention_state_visibility.py`,
   `scripts/check_skill_surface_preflight.py`.
6. Existing pins: `tests/quality_gates/test_staged_commit_gate_plan.py`,
   `tests/quality_gates/test_closeout_headroom_and_mirror_gate.py`.

## Interview Decisions

- **Q1 — Where should enforcement live?** Family considered: {harden the existing
  pre-commit path; add a mandatory `run_slice_closeout` step; both}. Chosen:
  *harden the existing pre-commit path* (single source of truth). Rejected: a
  separate mandatory step duplicates enforcement and drifts from the pre-commit
  boundary; "both" is unnecessary belt-and-suspenders for one commit boundary.
  Anti-anchoring: `axis: repo-role (source vs consumer)` — the git pre-commit
  boundary is intentionally scoped to maintainer source repos
  (`install-git-hooks.sh` gates on `packaging/charness.json` + `plugins/charness/`);
  this is the correct scope, not over-anchoring.
- **Q2 — Is hook-install reliability in scope?** Family: {in scope; out of scope}.
  Chosen: *in scope*. Reason: a checked-in hook that is not active is the leading
  alternate root cause; fixing coverage while leaving activation silent could
  leave the real gap open on another machine. Anti-anchoring: `axis: repo-role` —
  install applies only to maintainer source repos.
- **Mode** (not asked; strong default): implementation-continuation — resolving a
  tracked issue. `single-point: /achieve always shapes-and-saves and /goal always
  pursues, so the mode only records intent for the run`.

## Plan Critique Findings

Self-critique (Before-phase). A second fresh-eye plan/slice critique runs at the
Slice 2 fix boundary per the verification plan.

- **Confirmed-input over-anchoring (folded).** The issue's example remedy ("add a
  pre-commit hook") is already present and active (`core.hooksPath=.githooks`).
  Folded: Slice 1 root-causes before Slice 2 fixes; Boundaries forbid assuming
  the remedy.
- **Latency/noise risk (folded).** Running the authoring-preflight on every staged
  script could slow commits. Folded: presence/structural only; scope to the named
  file classes; keep within the existing fast-surface set rather than adding a new
  heavy gate.
- **False-green dry-run trap (folded).** Recent-lessons: a `--head-sha HEAD`
  dry-run at a parent commit read "blocking: []". Folded: the regression test and
  the repro fixture assert against the **staged index**, not `base..HEAD`.
- **Over-scoping risk (folded).** Keep to the three named gates + named file
  classes. Folded into Non-Goals and Boundaries.
- **Over-worry, not folded.** Whether to add light push/tag CI (handoff "Discuss"
  item) is out of scope here; it is a separate enforcement layer.

Fresh-eye Before-phase critique (general-purpose subagent `a79fcad39f14b6d2f`,
file-verified, read-only). Four BLOCKERS folded:

- **B1 — pre-push backstop reframes "escape" as latency (folded).**
  `.githooks/pre-push` runs the full broad gate on non-docs-only pushes, so a
  `--no-verify` commit is still caught before leaving the machine. Folded into
  the Goal wording, a Boundaries "Known backstop" line, the Active Operating
  Frame lead, and User Acceptance #1.
- **B2 — per-gate coverage is not uniform (folded).** `validate_skill_ergonomics`
  is skill-package-only (never fires on `scripts/**`); only attention-state
  covers `scripts/**`. Folded into the Goal note and a Boundaries per-gate line.
- **B3 — "wiring added after #329" is falsified (folded).** Git timing shows the
  ergonomics fast-gate (`a09e6d95`) and attention-state wiring (`86a905d7`)
  predate #329, and both instances were under active gates. Folded into the Slice
  1 expected-evidence (pin each instance to its gate; prove `--no-verify`/hook-
  not-run via reflog; record the falsified hypothesis) and the Frame lead.
- **B4 — `validate_maintainer_setup` already checks hooksPath (folded).** Slice 2
  must confirm-not-rebuild. Folded into the Boundaries hook-install line and the
  Slice 2 row.
- Over-worries raised, not folded (verified accurate, no action): test home/shape
  already correct — extend `tests/quality_gates/test_staged_commit_gate_plan.py`
  (O1); plugin mirror-drift is self-enforcing (O2); no in-tree ergonomics
  violations to grandfather (O3); `--no-verify` is bounded by the pre-push
  backstop (O4); anti-anchoring on the "pre-commit hook" value is handled — the
  issue's "(or a mandatory run_slice_closeout step)" alternative is the *same*
  boundary the hook already calls (O5).

## Off-Goal Findings

_None yet. File off-goal findings through `issue`; record only the reference and
reason here._

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

After the run reports complete, the user can independently verify:

1. `git log --oneline origin/main..HEAD` — see the Slice 4 closeout commit
   carrying `Close #332`.
2. Stage a `#329-class` violation in a fresh `skills/**` or `scripts/*.py` file
   and run `python3 scripts/run_slice_closeout.py --repo-root . --predict-commit`
   — confirm it blocks at the commit boundary.
3. `pytest tests/quality_gates/<new test>` — green on the fix.
4. Read the Slice 1 debug artifact and confirm the root cause is falsifiable and
   matches the landed fix.
5. Confirm no provider/live proof is claimed — only local gate proof.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
