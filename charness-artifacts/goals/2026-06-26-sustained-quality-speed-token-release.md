# Achieve Goal: Sustained quality speed token release

Status: active
Created: 2026-06-26
Activation: `/goal @charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release.md`
Timebox: 3h
Activation time: 2026-06-26T09:34:18+09:00
Closeout reserve: 25m
Done-early policy: continue_next_improvement

This file is the active living goal scratchpad for the current run.

## Active Operating Frame

- Current slice: boundary-bypass/test-runtime cleanup after the prior subprocess
  fanout reductions.
- Current slice intent: reduce remaining nested subprocess tests only where
  ordinary behavior is already reachable in-process, while preserving one real
  CLI smoke for each operator-facing entrypoint that still needs boundary proof.
- Next action: inspect candidate test files, convert low-risk subprocess
  assertions to direct `main()`/library calls, run focused tests plus the
  boundary inventory, then record critique and commit the slice.
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

Run a timeboxed implementation-continuation goal for roughly three hours: keep improving Charness quality across bug fixes, test speed, script execution speed, and token efficiency, then push and prepare or publish the release surface when the release contract allows it.

## Non-Goals

- Do not weaken or remove the standing read-only quality gate.
- Do not publish a release until the release skill's proof contract is read and
  satisfied.
- Do not remove the final real CLI proof for a shipped entrypoint merely to
  lower a boundary-bypass count.
- Do not expand into unrelated product design or issue-closeout work unless a
  local quality finding must be tracked instead of fixed now.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Push/release is approved by the user's request for the final phase only; the
  run still performs local proof, release critique, and a second evidence
  channel before claiming publication.
- Cautilus remains eval-only and disabled unless the repo planner explicitly
  allows the wrapper path with a named failing-log source.
- Generated/plugin/export surfaces must be synced before validators when touched.

## User Acceptance

- Inspect the commits made during this goal and see concrete quality/runtime
  improvements rather than only prose.
- Run `./scripts/run-quality.sh --read-only` successfully after the final bundle.
- Confirm `main` is pushed and the release surface is prepared or published
  according to the repo release contract.

## Agent Verification Plan

### Low-Cost Checks

- Focused pytest for changed test modules.
- Boundary-bypass inventory summary before and after conversion slices.
- `git status --short` and generated-surface sync checks when relevant.

### High-Confidence Checks

- `./scripts/run-quality.sh --read-only` at final closeout and before push.
- Fresh-eye critique on the changed risk boundary before final broad proof.
- Release skill validation before any release publish step.

### External Or Live Proof

- `git push` result plus clean branch status after push.
- Release publish or release-preparation evidence from the release workflow; if
  publication is blocked by contract or credentials, record the concrete blocker.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Reduce more nested subprocess fanout while preserving real CLI smokes | Boundary inventory still shows 84 candidates / 144 keys / 47 convertible after prior improvements | Focused pytest, boundary inventory delta, critique artifact, commit | in-progress |
| 2 | Address the next highest signal quality/runtime/token issue found by inventories | Timebox mode continues improvement if slice 1 completes safely | Focused proof, quality artifact update, commit | queued |
| 3 | Final release and push bundle | User explicitly requested final push/release | Read-only quality gate, release proof, push output, clean status | queued |

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

Current queue: none — the user already authorized the final push/release lane;
credentials or release-tool refusal will be recorded here if encountered.

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

Routing: `find-skills` recommendation for the task returned `quality` for the
quality/runtime work and `release` for final publication.
Gather: n/a — no external URL/source context was provided for this goal.
Release: pending final release phase.
Issue closeout: n/a — this goal is not resolving a tracked GitHub issue.

## Slice Log

### Slice 1: Retro and handoff boundary fanout

- Objective: Reduce nested subprocess fanout in retro and handoff behavior tests while preserving real CLI proof.
- Why this approach: The boundary-bypass inventory still had 84 candidates / 144 keys / 47 convertible files; these tests asserted ordinary JSON and artifact behavior through subprocesses even though import-safe main() seams existed.
- Commits:
- What changed: Converted recent-lessons refresh, retro persistence, and handoff merge-proposal behavior assertions to in-process main() calls; added quality and critique artifacts for the slice.
- Alternatives rejected: Deferred render_report.py and record_metric_window.py because they include unique CLI/argparse proof that should be split before conversion.
- Targeted verification: Focused pytest: 34 passed in 3.18s; ruff passed; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary.
- Test duplication pressure: No tests added; existing tests changed from subprocess to in-process. Raw boundary inventory improved to 81 candidates / 141 keys / 44 convertible files.
- Critique: charness-artifacts/critique/2026-06-26-retro-handoff-boundary.md; fresh-eye reviewer 019f015c-bba6-79b2-9fa2-43135fc21015 found no issues.
- Off-goal findings: none
- Lessons carried forward: Before converting boundary tests, prove retained CLI smoke exists for each entrypoint; direct main() calls should use pytest-scoped monkeypatch/capsys only.
- Metrics: Runtime profile local-linux-x86_64-36cpu; run-quality latest 38.1s / median 65.7s before this slice.

### Slice 2: HITL report subprocess fanout

- Objective: Reduce repeated render_report.py subprocess calls while retaining real CLI proof.
- Why this approach: The report-mode test file launched render_report.py for ordinary report behavior 14 times; most assertions can use the import-safe main() seam.
- Commits:
- What changed: Converted report behavior tests to run_render_report(monkeypatch, capsys, ...); kept stdout indent and argparse required-argument tests as real subprocess smokes.
- Alternatives rejected: Did not remove the last four run_script calls because they prove delivery-boundary stdout formatting, argparse behavior, and handled-error process exit behavior.
- Targeted verification: ruff passed; focused pytest: 12 passed in 2.64s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 14 to 4.
- Test duplication pressure: No tests added; existing tests switched execution layer. File-level boundary count unchanged by design because retained CLI smokes remain in the same file.
- Critique: charness-artifacts/critique/2026-06-26-hitl-report-runtime.md; fresh-eye reviewer 019f0163-21e9-7c40-9fff-21702c8405cf found one Medium handled-error CLI proof issue, fixed before commit.
- Off-goal findings: Potential future inventory improvement: count within-file subprocess call reductions separately from file-level candidates.
- Lessons carried forward: File-level ratchets can hide meaningful runtime wins inside a retained-boundary test file; record direct call-count evidence.
- Metrics: render_report.py run_script calls in test_hitl_report_mode.py: base 14, current 4.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User request on 2026-06-26: run a three-hour sustained quality improvement
  goal and finish with push/release.
- `docs/design-north-star.md`
- `docs/conventions/implementation-discipline.md`
- `docs/conventions/operating-contract.md`
- `charness-artifacts/retro/recent-lessons.md`
- `charness-artifacts/quality/2026-06-26-five-pass-boundary-quality-review.md`
- `charness-artifacts/critique/2026-06-26-five-pass-boundary.md`

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode family: artifact-only draft vs implementation-continuation. Chosen:
  implementation-continuation because the user explicitly requested a sustained
  goal and final push/release. Rejected: artifact-only would fail the request.
- Quality axis: broad refactor vs measured slice sequence. Chosen: measured
  slices with focused proof and final broad gate because repo contracts require
  evidence before publication. Rejected: one large speculative sweep would make
  critique and rollback harder.
- Runtime axis: remove subprocess boundaries everywhere vs preserve boundary
  smokes. Chosen: convert ordinary behavior assertions only when a real
  boundary proof remains. Rejected: eliminating unique CLI proof repeats the
  prior-session failure class.
- Release axis: publish unconditionally vs release-contract-gated publication.
  Chosen: release skill decides whether to publish, prepare, or block. Rejected:
  direct publish without release proof violates the north-star irreversible
  boundary rule.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Folded blocker: converting subprocess tests can erase the only shipped CLI
  smoke for an entrypoint; the slice explicitly checks for remaining real-boundary
  proof before conversion.
- Folded blocker: push/release is irreversible enough that final success cannot
  be claimed from terminal green alone; final phase uses the release skill and a
  second evidence channel.
- Over-worry not folded: avoiding all test conversion because subprocess smokes
  can be valuable. Counterweight: the boundary-bypass ratchet already separates
  likely keep-boundary rows; ordinary behavior assertions should move lower when
  safe.
- Reviewer provenance: same-agent plan critique at activation; bounded
  fresh-eye critique is planned before final broad proof.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

None yet.

## Final Verification

Closeout pending until the final release/push phase.

## User Verification Instructions

- Run `./scripts/run-quality.sh --read-only`.
- Inspect `git log --oneline origin/main..HEAD` before push, or the pushed tag /
  release evidence after publication.

## Auto-Retro

Retro pending final closeout.
Retro dispositions: pending final closeout.
Structural follow-up: pending final closeout.
