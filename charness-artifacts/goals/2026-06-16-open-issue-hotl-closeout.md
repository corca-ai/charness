# Achieve Goal: Open issue HOTL closeout

Status: draft
Created: 2026-06-16
Activation: `/goal @charness-artifacts/goals/2026-06-16-open-issue-hotl-closeout.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: draft/backlog awaiting activation.
- Current slice intent: implement the repo changes, proof, and issue closeout
  carrier needed to close every currently open `corca-ai/charness` issue.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-16-open-issue-hotl-closeout.md`.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Implement the repo changes, proof artifacts, and GitHub closeout carrier needed
to close every open `corca-ai/charness` issue visible at activation time, using
HOTL proof where the acceptance surface involves applied/live behavior.

The shaped open queue at draft time is:

- #378 `Surface duplicate-discovery and broad-scanner waste in quality`.
- #377 `Audit latest.md current-pointer handling across skills`.
- #376 `Require agentic re-judgment after deterministic helper outputs`.
- #375 `achieve scaffold should allow adapter-controlled draft current-frame disposition`.
- #371 `agent-browser leaves orphaned chromium trees + profile dirs after the invoking turn ends`.

The intended successful outcome is that #378, #377, #376, #375, and #371 are
all verified `CLOSED` through the issue backend. Leaving one open is not a
successful completion unless implementation discovers a new external blocker
that cannot be resolved locally; in that case the goal blocks or records a
separate user-visible stop condition instead of silently counting the issue as
done.

## Non-Goals

- Do not claim Charness fixed upstream `agent-browser` invocation-bound teardown
  unless controlled lifecycle proof exists for normal completion, cancellation,
  provider failure, timeout, and matching profile-dir cleanup.
- Do not stop at planning, triage, or issue classification. The active run owns
  implementation, verification, carrier publication, and issue closeout.
- Do not leave #371 open merely because the upstream tool still needs its own
  fix. Charness can close its issue after verifying local mitigation, documenting
  the ownership split, linking the upstream tracker, and recording the residual
  upstream lifecycle work as a HOTL non-claim.
- Do not publish, push, release, or manually close issues before the relevant
  implementation and proof exist. During activation, remote side effects are
  expected once the carrier is ready; name the phase-scoped carrier before
  executing it.
- Do not treat CodeRabbit-generated issue-plan comments as acceptance
  authority. They are context only.
- Do not turn #378 into a blocking quality gate by default; the issue asks for
  advisory structural signal first.
- Do not resolve current-pointer policy by forcing every `latest.md` layout to
  become a symlink.

## Boundaries

- Discuss before activation: RESOLVED for draft shaping by the user's request to
  create a goal that implements the work necessary to close all open issues and,
  where applicable, proves it with HOTL. The #371 closure interpretation is
  resolved in-thread: close is allowed as a Charness-local ownership/disposition
  closeout, not as a claim that upstream `agent-browser` lifecycle teardown is
  fixed.
- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward. After an approved publish/CI/apply lane completes,
  done-early test-only quality continuation is local by default. Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Source of truth: GitHub issue state via `issue_tool.py read` / `gh issue`
  remains authoritative over handoff snapshots.
- HOTL adapter state: no `.agents/hotl-adapter.yaml` exists at shaping time.
  Live proof commands are therefore undeclared; any live proof that needs a
  repo-owned command must either implement/declaratively register that command
  or record `blocked-needs-capability`.
- Branch state at shaping: `main...origin/main [ahead 9]` with the runtime
  optimization branch locally committed and unpublished.
- Existing uncommitted test changes in
  `tests/quality_gates/test_mutation_coverage_producer.py` and
  `tests/quality_gates/test_standing_pytest_runner.py` predate this goal
  shaping in the working tree; do not revert or mix them into this artifact-only
  closeout unless the active run claims them.

## User Acceptance

- Run the activation command, then verify #378, #377, #376, #375, and #371 are
  closed on GitHub.
- Inspect the closeout carrier and confirm it contains the required close
  keywords or verified manual fallback for all five issues.
- Confirm the implementation artifacts and tests cover each issue's acceptance
  sketch rather than only adding close comments.
- For #371, verify the close comment says Charness local mitigation/ownership is
  closed while upstream invocation-bound lifecycle teardown remains tracked
  externally. The closeout must not claim provider lifecycle proof unless it was
  actually run.

## Agent Verification Plan

### Low-Cost Checks

- Refresh live issue list before mutation:
  `gh issue list --repo corca-ai/charness --state open --limit 50`.
- Read every selected issue and comments through the issue backend before
  design: `issue_tool.py read --repo corca-ai/charness --number <n>`.
- Run focused tests for changed helper, skill, or quality surfaces before each
  commit.
- Run `python3 scripts/check_changed_surfaces.py --repo-root .` after mutation
  to identify generated/export obligations.
- Validate closeout carrier drafts with `issue_tool.py validate-closeout-draft`
  before publishing any `Close #N` keywords.

### High-Confidence Checks

- Run a slice closeout rehearsal with `python3 scripts/run_slice_closeout.py
  --repo-root . --skip-broad-pytest` after coupled artifact/code changes.
- For the final bundle, lock the diff and run the repo-required final closeout
  gate. If the worktree is clean and verification-lock no-ops, follow the recent
  lesson: run and record the broad gate directly rather than manufacturing a
  fake diff.
- For bug-class issue fixes, run the `issue` causal-review path before design
  and the resolution critique before closeout. If the host cannot spawn the
  required bounded reviewer, stop and record the host signal.
- Verify every issue closeout after push/merge or manual fallback with
  `issue_tool.py verify-closeout --expect-state CLOSED`.

### External Or Live Proof

- HOTL proof packet:
  `charness-artifacts/hotl/2026-06-16-open-issue-hotl-closeout-proof-packet.md`.
- External mutation proof for issue closure requires before/after GitHub
  readback: open issue state before carrier, carrier/push evidence, closed
  issue state after, and any fallback comment evidence.
- #371 has two proof classes:
  - Charness-local mitigation/ownership closeout: prove repair/doctor behavior,
    existing release notes or comments, upstream tracker links, and GitHub
    before/after closeout readback.
  - Upstream lifecycle fix: only claim verified if invocation start/end or
    abort-mode readback proves browser process-tree and profile-dir teardown.
- If the active run closes #371 without upstream lifecycle proof, record the
  residual as `issue` with the upstream tracker as owner, not as `verified`.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Refresh issue SoT and lock closeout contract | GitHub state can change; implementation must target live issues, not stale handoff prose | Fresh issue list, per-issue reads with `comments_read: true`, issue classification, route recommendation recorded | planned |
| 1 | Implement #375 achieve scaffold adapter control | This is a concrete helper/API change with focused tests and low dependency on other issues | Adapter contract update, scaffold implementation, idempotence tests, fixture proving custom draft frame | planned |
| 2 | Implement #376 deterministic-helper re-judgment contract | This cross-skill rule affects how helper output is presented before operator decisions | Handoff chunking guidance/output update, cross-skill audit note, tests or validator proving visible re-judgment where practical | planned |
| 3 | Implement #377 current-pointer audit tightening | Current-pointer handling is a repo-wide artifact policy issue and may affect validators/resolvers | Audit artifact, resolver/instruction updates, symlink/current-pointer guard proof, focused tests | planned |
| 4 | Implement #378 quality advisory inventory | Quality needs a non-blocking signal for duplicated discovery and broad scanner waste | Advisory inventory/report surface, quality docs update, tests against duplicate discovery and prefilter examples | planned |
| 5 | Close #371 as Charness-local ownership disposition | Local mitigation has shipped; remaining lifecycle fix belongs upstream but must be closed honestly here | Repair/doctor/readback proof, upstream tracker refs, HOTL non-claim, close comment draft | planned |
| 6 | Final gate, publish carrier, verify all issue closures | GitHub closure requires a pushed/merged or verified manual carrier | Final closeout gate, validated closeout draft, push/release decision executed, `verify-closeout --expect-state CLOSED` for #378/#377/#376/#375/#371 | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) - never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns which skill answers a boundary.

- Routing: `find-skills --recommend-for-task` on 2026-06-16 recommended
  `handoff` and `hotl`; GitHub issue access route was `issue` with ready
  `github-gh`.
- Gather: n/a - the external source is the GitHub issue tracker, read through
  the `issue` backend as source of truth rather than arbitrary web context.
- Release: pending activation decision - the current handoff asks whether to
  publish/release the already-committed runtime optimization branch first.
- Issue closeout: planned close for #378/#377/#376/#375/#371; carrier and
  `validate-closeout-draft` / `verify-closeout --expect-state CLOSED` proof
  must be recorded during the active run.

## Slice Log

No slices have run. This artifact is draft-only until activation.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `docs/handoff.md` read on 2026-06-16. It reported open issues #377, #376,
  #375, #371 and a local unpublished runtime optimization branch.
- `gh issue list --repo corca-ai/charness --state open --limit 50 --json ...`
  read on 2026-06-16. It showed #378, #377, #376, #375, #371 open.
- `issue_tool.py read --repo corca-ai/charness --number 378`: feature/deferred
  quality advisory for duplicate discovery and broad scanner waste.
- `issue_tool.py read --repo corca-ai/charness --number 377`: repo-wide audit of
  `latest.md` current-pointer handling and `write_artifact_path` discipline.
- `issue_tool.py read --repo corca-ai/charness --number 376`: cross-skill
  deterministic helper output must be re-judged by agent synthesis before
  presentation, mutation, closeout, or next-action selection.
- `issue_tool.py read --repo corca-ai/charness --number 375`: `achieve`
  scaffold needs adapter-controlled draft Active Operating Frame disposition.
- `issue_tool.py read --repo corca-ai/charness --number 371`: remains open
  after v0.50.1 downstream mitigation; it can close locally if residual
  invocation-bound lifecycle ownership is explicitly transferred/dispositioned
  and not misrepresented as fixed.
- `charness-artifacts/retro/recent-lessons.md`: keep #371 lifecycle proof
  boundary visible; local healthcheck/reaper is only drift mitigation.
- HOTL adapter resolution on 2026-06-16: no adapter found; live proof commands
  are undeclared.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Scope: chose all live open GitHub issues instead of the handoff's four-issue
  snapshot because `gh issue list` showed #378 was created after the handoff.
- Execution posture: chose an activation-ready implementation goal, not a
  triage-only goal. The active run is expected to mutate code/docs/tests,
  publish the closeout carrier, and close issues after proof.
- Proof posture: chose HOTL ledger/disposition for any applied/live behavior,
  but local deterministic tests for code/docs-only acceptance classes.
- #371 posture: chose closeable local disposition rather than false non-closure.
  Charness can close its issue if it proves local mitigation/repair ownership,
  links the upstream lifecycle tracker, and states the residual upstream
  lifecycle proof as a non-claim.
- Bundle posture: keep the current unpublished runtime optimization branch in
  scope as a publish/release decision because the handoff names it as the first
  sequencing decision and issue closeout may need a carrier.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Same-agent shaping critique, 2026-06-16: the main false-close risk is #371.
  Folded response: #371 closure is allowed only as local ownership/disposition
  closeout and must not claim upstream lifecycle proof.
- Same-agent shaping critique, 2026-06-16: the handoff issue list was stale.
  Folded response: Slice 0 starts with live GitHub refresh and #378 is in scope.
- Same-agent shaping critique, 2026-06-16: broad issue bundling could collapse
  into planning instead of implementation. Folded response: the slice plan names
  the implementation target and expected proof for each issue, with a final
  publish/verify slice.
- Fresh-eye critique: not yet run; required before material mutation or final
  closeout during activation.

## Off-Goal Findings

None at shaping.

## Final Verification

Not run. Required before completion:

- Retro: create or explicitly skip with an allowed reason before complete.
- Host log probe: record unavailable or create the provider-safe metrics block
  before complete.
- Disposition review: run the required critique/disposition review before
  complete.
- Issue closeout verification: verify closed issues through the issue backend
  and record explicit HOTL dispositions for non-closed issues.

## User Verification Instructions

After activation and closeout, run:

- `gh issue list --repo corca-ai/charness --state open --limit 50`.
- `issue_tool.py read --repo corca-ai/charness --number <n>` for each issue
  claimed closed or dispositioned.
- Inspect the final HOTL ledger/proof packet and confirm each issue has exactly
  one verified or explicitly dispositioned status.

## Auto-Retro

Not run. At completion, disposition every surfaced improvement as
`applied: <what>`, `issue #N`, `repo-local guard: <path>`, or
`none - <reason>`.
