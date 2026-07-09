# Achieve Goal: Autonomous repo improvement issues

Status: complete
Created: 2026-07-09
Activation: `/goal @charness-artifacts/goals/2026-07-09-autonomous-repo-improvement-issues.md`

This file is the living goal scratchpad. The user explicitly activated this
implementation-continuation run with "모든 문제를 자율적으로 해결하세요".

## Active Operating Frame

- Current slice: S1 #427 proof-honesty repair and current-state reconciliation.
- Current slice: complete local closeout for the #427 repair bundle.
- Current slice intent: bind the code fix, handoff reconciliation, critique,
  retro, and verification evidence into one auditable local closeout.
- Next action: create the validated direct-commit carrier and leave remote issue
  closure as an explicit push/verify boundary.
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

Resolve the current actionable Charness repo problem set autonomously: open tracked issues that are locally actionable, stale handoff/current-state drift, and directly provable quality risks discovered during the run.

## Non-Goals

- Do not claim every deferred product idea in `docs/deferred-decisions.md` is
  resolved; only locally actionable current problems are in scope.
- Do not publish a release or push to GitHub as part of the local repair unless
  final closeout identifies that as the only remaining safe proof lane.
- Do not physically delete prompt-surface content based on mutation survival;
  the current policy permits demotion proposals only.
- Do not close a GitHub issue from a same-channel local green alone; issue
  closeout needs the repo's distinct-observer / distinct-channel safeguard.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Scope boundary: "all problems" is interpreted as the current actionable set:
  live open GitHub issues visible at start (#421, #427), stale handoff state
  that can misroute a next session, and defects discovered while repairing those
  surfaces. Historical closed decisions and broad wishlist items remain out of
  scope unless they become blocking evidence.
- Axis check: host axis = Claude/Codex dual support; this run changes repo-local
  Python scoring and docs only, so no host-specific behavior should be added.
- Axis check: evidence channel axis = trace digest vs stream JSONL vs GitHub
  issue state; the fix must avoid treating arbitrary transcript text as the same
  evidence channel as command execution.

## User Acceptance

- Run the focused prompt-mutation scorer tests and see prose-only marker
  mentions rejected while command/tool-use marker events still fire.
- Read `docs/handoff.md` and see the next-session queue match live actionable
  issue state instead of pointing at already-closed #423 as next work.
- Inspect the final commit(s), goal artifact, and closeout evidence for explicit
  non-claims about push/remote issue closure/release.

## Agent Verification Plan

### Low-Cost Checks

- `python3 -m pytest -q <focused prompt mutation scorer tests>`
- `python3 scripts/check_doc_authoring_preflight.py --path docs/handoff.md`
- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.63.0/skills/achieve/scripts/check_goal_artifact.py --repo-root . --slug autonomous-repo-improvement-issues --date 2026-07-09`

### High-Confidence Checks

- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
- Final locked closeout if the diff remains code-bearing and local runtime cost
  is acceptable for the completed bundle.

### External Or Live Proof

- GitHub issue closeout is a separate irreversible boundary. Local commits may
  prepare closeout evidence, but remote closure is not claimed unless verified
  by the repo issue workflow with a distinct channel.
## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | Fix #427 scorer false positive and reconcile handoff state | Open issue and current handoff drift directly affect proof honesty and next-session routing | Focused tests, handoff preflight, slice closeout | complete |
| S2 | Check #421/current mutation-regression posture after S1 | #421 is still open but may be machine-owned; avoid manual closure without current proof | GitHub issue readback, local quality command or explicit non-claim | complete |
| S3 | Closeout critique/retro/commit | Task-completing repo work requires critique, durable evidence, and commit discipline | Critique artifact or bounded reviewer result, goal check, commit | complete |

## Operator Decision Queue

- Decision: whether to push and let GitHub issue auto-close after local closeout.
- Owner: operator
- Why deferred: safe local repair, tests, critique, and commit can proceed
  without crossing the remote irreversible boundary.
- Unblock action: authorize push / remote issue closeout, or handle manually.
- Revisit trigger: local closeout green and commit ready.

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

- Routing: find-skills recommended issue, quality, critique, retro, and handoff for this multi-skill closeout; used issue for #427 closeout validation, quality for gates, critique for fresh-eye review, retro for lessons, handoff for next-session state, and achieve for the goal artifact
- Gather: n/a — no external source URLs were introduced; GitHub issue state was read live through gh for current tracker context
- Release: n/a — this run does not touch release/version/publish surfaces
- Issue closeout: #427 close-intended through a direct-commit carrier; issue_tool.py validate-closeout-draft returned ready_to_commit_push; remote CLOSED verification is pending push because local terminal green alone is not remote issue closure; #421 remains machine-owned/watch

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — user explicitly requested autonomous
  implementation-continuation; local commits are in scope, while push/release
  and remote issue closure remain separate irreversible boundaries unless final
  closeout proves and authorizes them.

## Slice Log

- S1 complete: #427 scorer proof-honesty repair landed in commits
  `87963dab`, `9e97902f`, and `2f988fff`; the final semantics require Bash
  command-bearing evidence for both trace-digest and stream fallback marker
  fires, with regression coverage for prose-only mentions, non-command tool
  inputs, non-Bash trace args, and non-Bash stream `input.command`.
- S1 proof: `python3 -m pytest -q tests/test_score_prompt_mutation_survival.py`
  returned 29 passed; `docs/prompt-mutation-policy.md` records the Bash-only
  evidence caveat.
- S2 complete: #421 remains open and machine-owned/watch rather than manually
  closed; local spot check
  `python3 -m pytest -q tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view tests/quality_gates/test_mutation_baseline_abort.py`
  returned 26 passed.
- S3 complete: bounded fresh-eye critique found the remaining non-Bash stream
  split-brain before closeout; commit `2f988fff` fixed it, and
  `charness-artifacts/critique/2026-07-09-critique-review.md` records the
  disposition.
- S3 proof: `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  completed after artifact-shape repair; structural sweep, current-pointer
  freshness, retro index sync/check, doc links, command docs, markdown,
  secrets, critique validation, and browser runtime guard all passed.

## Context Sources

- `docs/design-north-star.md` — governing evidence/non-terminality standard.
- `docs/handoff.md` — current queue at run start.
- `charness-artifacts/retro/recent-lessons.md` — current prompt-mutation and
  stream-fallback repeat traps.
- GitHub issues read live with `gh issue view`: #421, #427, #423.
- `docs/prompt-mutation-policy.md` — scorer/verdict semantics and stream
  fallback caveats.

## Interview Decisions

- Mode family considered: artifact-only draft vs implementation-continuation.
  Chosen: implementation-continuation, because the user said "자율적으로
  해결하세요". Rejected: artifact-only would not satisfy the directive.
- Scope family considered: all historical deferred decisions vs current
  actionable problem set. Chosen: current actionable set plus defects discovered
  during repair. Rejected: solving every historical deferral would be
  unbounded and would cross product decisions not implied by this prompt.
- External side-effect family considered: local repair only vs push/remote close.
  Chosen: local repair/commit first, remote closure only after closeout proof.
  Rejected: closing issues from same-channel local evidence would violate the
  north-star boundary.

## Plan Critique Findings

- Same-agent shaping critique: broad "all problems" wording is unsafe unless
  bounded to current actionable evidence; folded into Boundaries and Slice Plan.
- Same-agent shaping critique: #427 is a bug-class false-proof issue, so the
  first slice must be root-cause/test-first rather than a prose-only handoff
  cleanup; folded into S1.
- Over-worry not folded: full release proof is unnecessary unless final diff
  touches release/export surfaces.

## Off-Goal Findings

- `prompt_mutation_bundle_lib.stream_command_blob` still has broad helper naming
  and extraction semantics. Counterweight classified this as valid cleanup debt
  but not a #427 blocker because survival scoring no longer imports that helper;
  the retro records deferred follow-up `prompt-mutation-helper-contract`.
- #421 is not manually closable from this run. The local regression spot check
  passed, but its scheduled/machine-owned closeout remains a watch item.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-07-09-autonomous-repo-improvement-issues-retro.md
Host log probe: skipped: host-log-not-exposed: no host session JSONL or goal-window metric file was exposed to this run
Disposition review: charness-artifacts/critique/2026-07-09-critique-review.md

- Focused #427 proof: `python3 -m pytest -q tests/test_score_prompt_mutation_survival.py` = 29 passed.
- #421 spot check: `python3 -m pytest -q tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view tests/quality_gates/test_mutation_baseline_abort.py` = 26 passed.
- Doc preflight: `python3 scripts/check_doc_authoring_preflight.py --path docs/handoff.md` and `--path docs/prompt-mutation-policy.md` passed.
- Critique validator: `python3 scripts/validate_critique_artifacts.py --repo-root . --paths charness-artifacts/critique/2026-07-09-critique-review.md` passed.
- Retro validator: `python3 scripts/validate_retro_artifact.py --repo-root . --paths charness-artifacts/retro/2026-07-09-autonomous-repo-improvement-issues-retro.md` passed.
- Issue closeout draft: `python3 .../issue/scripts/issue_tool.py validate-closeout-draft --repo corca-ai/charness --number 427 --classification bug --carrier direct-commit --commit-message-file <draft> --repo-root .` returned `ready_to_commit_push`.
- Slice closeout: `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest` completed with all listed local gates passing.

## User Verification Instructions

- Re-run `python3 -m pytest -q tests/test_score_prompt_mutation_survival.py`
  to verify the #427 scorer contract.
- Inspect the closeout commit message for `Close #427` plus JTBD, root cause,
  siblings, prevention, behavior proof, critique, boundary, and AI-provenance
  ledger lines.
- After pushing the local closeout commit, verify remote issue state through
  `issue_tool.py verify-closeout --repo corca-ai/charness --number 427 --classification bug --carrier direct-commit --commit-ref <sha> --expect-state CLOSED --repo-root .`.
- Treat #421 as watch-only unless the scheduled owning workflow supplies remote
  closure evidence.

## Auto-Retro

Retro dispositions: applied: Bash-only marker scorer/tests, prompt-mutation
policy update, handoff reconciliation, fresh-eye critique artifact, and session
retro artifact; accepted-risk: broad helper rename deferred until a future
execution-proof consumer appears.
Structural follow-up: applied: scorer contract and regression tests now require
Bash command-bearing evidence for marker fires; repo-local guard:
`docs/prompt-mutation-policy.md`; deferred follow-up:
`prompt-mutation-helper-contract` for helper naming cleanup.
