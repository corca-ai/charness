# Achieve Goal: Enforce recent lessons at broad-gate boundaries

Status: draft
Created: 2026-06-02
Activation: `/goal @charness-artifacts/goals/2026-06-02-enforce-recent-lessons-broad-gate-lock.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-02-enforce-recent-lessons-broad-gate-lock.md`.
- Verification cadence: cheap deterministic checks first. Do not run broad
  pytest or a broad `run_slice_closeout.py` path until the mutation set is
  explicitly locked; use a pre-lock rehearsal path for docs/sync/artifact proof.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files, expected invariants, tests/proof, non-claims, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Turn the recent broad-pytest waste lesson into an enforceable repo workflow:
repo-owned broad closeout paths must either run in an explicit pre-lock/no-broad
mode or require an explicit verification-lock acknowledgment before launching
the broad pytest phase.

The concrete outcome is that future agents cannot accidentally use
`scripts/run_slice_closeout.py` as readiness discovery while docs, artifacts,
fresh-eye disposition, or goal evidence are still moving. The intended workflow
should be visible in script behavior, tests, and operator docs:

- pre-lock: run focused checks and a no-broad rehearsal path;
- lock: record that the mutation set is locked and only failing-gate fixes may
  change files;
- post-lock: run broad pytest/closeout once, with any new scope breaking the
  lock and forcing focused replay before another broad run.

## Non-Goals

- Do not try to intercept every manually typed `pytest` command in arbitrary
  shells. This goal covers repo-owned gates and documented operator workflow.
- Do not solve unrelated open issues such as #184 or #261.
- Do not replace `recent-lessons.md` or the lesson-selection index machinery.
  This goal consumes the lesson and turns the relevant part into a gate.
- Do not run a full pytest suite merely to set up or shape this goal.
- Do not claim live CI/provider proof unless it is actually run during the
  activated goal.

## Boundaries

- The first implementation target is `scripts/run_slice_closeout.py` and its
  mirrored/plugin or documented surfaces if the script is exported there.
- The lock contract should be explicit in CLI flags/help and pinned by tests.
  A plausible shape is `--skip-broad-pytest` for pre-lock rehearsal and a
  positive broad-run acknowledgment such as `--verification-lock` or an existing
  equivalent if one already fits local CLI style.
- The gate should fail closed for repo-owned broad closeout when neither a
  pre-lock skip flag nor a broad-run lock acknowledgment is present.
- The implementation must preserve existing deterministic sync/package/doc
  checks in the pre-lock path; only the broad pytest phase should be skipped or
  gated.
- If `run_slice_closeout.py` currently has callers, update their tests/docs
  rather than silently changing behavior underneath them.
- Direct manual pytest remains outside the enforceable boundary; final reporting
  must name that non-claim.
- Discuss before activation: the exact CLI flag names and whether to fail closed
  by default are consequential compatibility choices. The strong default is
  fail closed for broad pytest in `run_slice_closeout.py`, with an explicit
  no-broad rehearsal path for pre-lock use.

## User Acceptance

The user can verify completion directly by running the documented commands:

- A pre-lock rehearsal command completes deterministic closeout checks without
  launching broad pytest.
- A broad closeout command without the verification-lock acknowledgment refuses
  before pytest starts and explains the required lock.
- A broad closeout command with the explicit lock acknowledgment reaches the
  broad pytest phase.
- The docs or help text state that reading `recent-lessons.md` is not the gate;
  the gate is the broad-run lock decision.

## Agent Verification Plan

### Low-Cost Checks

- Focused tests for `run_slice_closeout.py` argument parsing, fail-closed
  behavior, skip-broad behavior, and lock-ack behavior.
- Focused tests for any docs/generated CLI reference or packaging mirror touched
  by the new flags.
- `ruff` / `py_compile` only on touched Python files.
- `python3 scripts/check_doc_links.py --repo-root .` if docs are touched.
- `./scripts/check-markdown.sh` if markdown contract/docs are touched.

### High-Confidence Checks

- Run the pre-lock/no-broad rehearsal path on the real repo and prove it does
  not invoke broad pytest.
- Run the lock-required negative path on the real repo and prove it exits before
  pytest.
- After implementation is stable and the mutation set is locked, run the normal
  broad closeout path with the explicit acknowledgment once.
- Use a slice-level fresh-eye critique before final completion because this goal
  changes operator workflow and verification economics.

### External Or Live Proof

- No external source is required for shaping this goal.
- CI/live provider proof is optional; if skipped, final verification must state
  that only local deterministic proof ran.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Map current broad-closeout behavior and callers | Avoid designing a flag that conflicts with existing local contracts | Notes in Slice Log naming current broad pytest trigger, callers, and docs/export surfaces | planned |
| 2 | Implement the no-broad rehearsal and lock-required broad path | Convert the retro lesson from prose memory into executable behavior | Focused tests plus real negative/pre-lock command output | planned |
| 3 | Sync docs/export/plugin surfaces | Keep operator and generated surfaces consistent with the new gate | CLI docs/help/plugin mirrors updated and validators green | planned |
| 4 | Critique, focused verification, and final broad proof after lock | Prove the gate without repeating the same pre-lock broad pytest waste | Fresh-eye critique disposition, focused checks, then one post-lock broad closeout if warranted | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- Gather: n/a - all shaping context is local repo state and conversation
  summarized into this artifact.
- Release: n/a pending activation - no version or install-manifest change is
  planned by default.

## Slice Log

- 2026-06-02 Before-phase setup: user challenged why `recent-lessons` was read
  but the broad pytest waste still recurred. The working conclusion is that
  reading lessons is insufficient unless a repo-owned broad-gate path turns the
  lesson into an actionable lock decision or refuses without an explicit lock.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `docs/handoff.md`
- `charness-artifacts/retro/recent-lessons.md`
- `charness-artifacts/retro/2026-06-02-hard-waste-full-pytest-reruns.md`
- `charness-artifacts/metrics/rca-ledger.jsonl`
- `scripts/run_slice_closeout.py`
- User discussion on 2026-06-02: full pytest was run too often; the lesson was
  read but not converted into a gate.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Scope family considered: artifact-only retro memory, operator doc reminder,
  or executable gate. Chosen: executable repo-owned broad-gate behavior because
  the prior memory-only lesson recurred.
- Enforcement family considered: block all pytest commands, gate only
  `run_slice_closeout.py`, or only add a no-broad mode. Chosen: gate the
  repo-owned broad closeout path and add a pre-lock no-broad path; arbitrary
  shell interception is out of scope and brittle.
- Compatibility family considered: preserve current default and add optional
  flags, or fail closed before broad pytest without an explicit lock. Chosen
  default for activation: fail closed for broad pytest, pending user review of
  exact flag names, because optional-only flags would not prevent recurrence.
- Proof family considered: broad pytest at every slice, focused tests only, or
  focused tests until lock followed by one broad closeout. Chosen: focused tests
  and real negative/pre-lock commands during slices; one broad proof only after
  mutation lock.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Self-critique blocker folded: a no-broad mode alone could become another
  optional affordance that agents ignore. The broad path itself must require an
  explicit lock acknowledgment.
- Self-critique blocker folded: "read recent lessons" is not a sufficient
  success criterion. Acceptance must be command behavior, not memory behavior.
- Self-critique over-worry not folded: direct manual pytest cannot be fully
  prevented without hostile shell wrappers. This is recorded as a non-claim
  rather than expanded into scope.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- None before activation.

## Final Verification

- Not run. Goal is draft and inert until activation.

## User Verification Instructions

After activation and implementation, run the commands named in `## User
Acceptance` and inspect `scripts/run_slice_closeout.py --help` or the generated
CLI reference for the lock/no-broad contract.

## Auto-Retro

- Not run. Goal is draft and inert until activation.
