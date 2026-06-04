# Achieve Goal: Future work efficiency: handoff, closeout, and publication

Status: active
Created: 2026-06-04
Activation: `/goal @charness-artifacts/goals/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 3 - direct-commit closeout carrier rehearsal for #288.
- Next action: inspect `issue_tool.py validate-closeout-draft`, closeout
  carrier parsing, and issue skill instructions; add a pre-push direct-commit
  rehearsal path without claiming post-push remote issue state.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve the work-efficiency bundle surfaced from handoff pickup: make bare handoff routing propose coherent agentic work packages instead of ranked issue lists (#286), stabilize the chunker fixtures that currently hard-pin live issue numbers (#285), add direct-commit closeout rehearsal before push (#288), add an Achieve adapter seam for closeout publication and auto-retro disposition policy (#287), and make announcement dual-output/thread-reply delivery executable or explicitly draft-only (#289).

## Non-Goals

- Do not resolve #293 inside this goal. Treat it as a preflight quality risk:
  inspect whether the current red mutation signal blocks this bundle, then
  either take the smallest enabling action or record why it is independent.
- Do not resolve #184. Product-success metrics need separate product judgment.
- Do not ship a release or version bump unless implementation discovers an
  already-owned release surface. This is a repo maintenance goal, not a release
  goal.
- Do not encode Ceal-specific label semantics in portable Charness source.
  Repo-local issue grouping policy belongs in adapters.
- Do not claim live installed-host proof, GitHub closeout, or delivery posting
  unless the run actually executes and records that proof.

## Boundaries

- Scope is the efficiency bundle the user selected from the handoff pickup:
  #286, #285, #288, #287, and #289.
- Preserve the public workflow split: `handoff` proposes and drafts, `achieve`
  shapes and coordinates, `/goal` pursues, `issue` owns tracked-issue closeout,
  `quality` owns validation posture, and `release` owns release surfaces.
- Prefer deterministic source identity and validation around agentic judgment.
  The agent may propose work packages, but validators must reject unknown source
  IDs, duplicate inclusion, over-large chunks, empty rationale, and broad-label
  only merges unless adapter policy allows them.
- Keep fixture stabilization repo-local where possible; changing portable
  handoff behavior solely to satisfy brittle live issue tests is out of bounds.
- Treat direct-commit closeout rehearsal as pre-publication readiness only. It
  must not claim remote issue state until after push and `verify-closeout`.
- If slice work touches public skill source, support scripts, exports, or
  generated plugin surfaces, follow mutate -> sync -> verify -> publish ordering.

## User Acceptance

- Running a bare `charness:handoff` / `/handoff` pickup over the current open
  backlog presents a small set of coherent work packages, not primarily one
  standalone candidate per issue.
- Closing or changing unrelated live GitHub issue numbers no longer breaks the
  handoff chunker tests that should be fixture-owned.
- A direct-commit closeout can be rehearsed before push against a proposed
  commit message or carrier body, with output that distinguishes pre-push
  readiness from post-push remote verification.
- `achieve` exposes an adapter-owned place for closeout publication and
  auto-retro disposition policy, including audit-only / handoff-only publish
  defaults, without forcing that rule into host-loaded instructions only.
- Announcement dual-output adapters can either pass an executable parent/thread
  delivery-chain contract or be explicitly classified as draft-only before any
  unthreaded `thread_reply` post is attempted.

## Agent Verification Plan

### Low-Cost Checks

- Start by checking `git status --short --branch`, `git log --oneline
  origin/main..HEAD`, the current open issue list, and whether #293 currently
  blocks local proof for touched surfaces.
- For each slice, run focused pytest for touched modules plus `ruff check` on
  changed Python paths.
- Use `python3 scripts/check_changed_surfaces.py --repo-root .` after each
  meaningful mutation to identify generated/export/documentation obligations.
- If public skill prose changes, run
  `python3 scripts/check_skill_surface_preflight.py --repo-root . --path <file>
  --preview-delta <planned-lines>` before editing.
- Use `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  before each slice lock when changes span multiple validator families.

### High-Confidence Checks

- Handoff chunking: targeted tests around parse/source packet/chunk proposal
  validation/rendering/auto-draft, plus an end-to-end fixture that proves package
  synthesis without live issue number coupling.
- Issue closeout rehearsal: tests for direct-commit carrier parsing, close
  keyword/ledger validation, ready-to-push output, unchanged PR/body-file
  behavior, and post-push verification non-claims.
- Achieve adapter seam: adapter resolver tests, missing-adapter fallback tests,
  lifecycle/After-phase policy consumption tests, and goal-artifact validation.
- Announcement delivery: resolver/delivery runner tests covering executable
  parent-handle chaining, draft-only classification, fail-fast before unthreaded
  thread replies, and single-output compatibility.
- Before final closeout, run the locked broad gate:
  `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock`
  and the repo's required read-only quality gate or a recorded justified
  substitute if #293 remains an unrelated scheduled-mutation signal.

### External Or Live Proof

- GitHub issue closeout proof is required only when closing #285/#286/#287/#288/#289:
  rehearse the carrier before push, then run `issue_tool.py verify-closeout`
  after publication and record the result.
- No release proof is expected unless release surfaces are touched.
- Installed-host or real delivery posting proof is optional and must be recorded
  as a non-claim if not run.

Discuss before activation: resolved by the user's 2026-06-04 selection of
`chunk A achieve`. The broad bundle is intentional; #293 and #184 are excluded;
tracked issue closeout is allowed only after the goal's issue-closeout rehearsal
and verification steps prove the carrier.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Preflight the quality/routing baseline and inspect #293 impact | Avoid building efficiency work on an unknown red proof surface | Status/open-issue snapshot, #293 independence or blocker note, changed-surface obligations | done |
| 2 | Implement agentic handoff work-package proposal and stable fixture policy for #286/#285 | This fixes the entry point that chooses future work and removes live issue churn from tests | Source packet/proposal validator tests, fixture-owned issue data, handoff e2e package rendering | done |
| 3 | Add direct-commit closeout carrier rehearsal for #288 | Safer closeout reduces push/recommit/CI-watch waste for the rest of the bundle | Carrier rehearsal command/tests, unchanged existing validation behavior, issue skill instruction update | planned |
| 4 | Add Achieve closeout publication / auto-retro disposition adapter seam for #287 | The broader policy should consume the concrete closeout rehearsal contract | Adapter contract/resolver/tests, lifecycle wording, missing-adapter fallback, goal validation | planned |
| 5 | Make announcement dual-output delivery chaining executable or draft-only for #289 | Delivery claims should fail fast or stay draft-only instead of surprising operators late | Adapter example/runner or resolver updates, thread-reply tests, single-output compatibility | planned |
| 6 | Sync, broad verify, critique, issue closeout, retro, and handoff refresh | Bundle completion needs generated surfaces, proof, and tracked issue closure aligned | Synced exports, broad gate, critique, closeout verification, retro dispositions, updated handoff | planned |

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
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Gather: n/a — current context is local repo state plus GitHub issues fetched via
`gh issue view/list` during shaping; no external URL or Slack/Docs source is in
scope for this goal.
Release: n/a — no release surface is planned.
Issue closeout: planned for #285, #286, #287, #288, and #289 only after
direct-commit/PR carrier rehearsal and post-publication verification; #293 and
#184 are context/exclusions, not close-intended issues.

## Slice Log

### Slice 1: Preflight quality and routing baseline

- Objective: Activate the goal, inspect repo/open-issue state, and decide whether #293 blocks the efficiency bundle.
- Why this approach: The bundle should not start implementation on an unknown red proof surface, but #293 must remain outside this goal unless it directly blocks touched work.
- Commits: current HEAD before slice record: dff7bbfa; artifact status changed to active in working tree.
- What changed: Goal artifact status moved to active. Preflight found open issues #293/#289/#288/#287/#286/#285/#184; local branch is ahead of origin/main by the goal-shaping commit; changed surface is only the goal artifact.
- Alternatives rejected: Rejected resolving #293 first inside this goal: its issue body points at earlier quality/testability files and scheduled mutation proof, not the first handoff/fixture implementation surface. It remains a final-proof risk to revisit if broad gates fail.
- Targeted verification: check_goal_artifact.py --pursue-ready passed; gh issue list/view captured current #293 state; check_changed_surfaces.py identified repo-markdown only; run_slice_closeout.py --skip-broad-pytest passed doc links, command docs, markdown, secrets, and agent-browser orphan guard.
- Test duplication pressure: n/a - no tests added or expanded in Slice 1.
- Critique: Same-agent preflight critique: the main possible misread is treating #293 as solved or irrelevant. Folded outcome: record it as independent for Slice 2 start but preserve it as final broad-proof risk.
- Off-goal findings: #293 remains open and out of scope; #184 remains open and out of scope.
- Lessons carried forward: Start Slice 2 with handoff package synthesis plus fixture stability, and keep deterministic source-ID validation as the guardrail around agentic grouping.
- Metrics: Host/thread goal tracker active; no provider-safe per-slice token window recorded for this short preflight.

### Slice 2: Agentic handoff packages and stable fixtures

- Objective: Implement the #286/#285 handoff package proposal stage so pickup can group work into coherent packages and tests stop depending on live issue numbers.
- Why this approach: This is the entry point for future work selection; package synthesis must happen before ranking, with deterministic validation around agent judgment.
- Commits: pending commit for Slice 2.
- What changed: Added chunked_routing_agentic.py and chunked_routing_agentic_policy.py for source packets, adapter chunk policy, response validation, and materialization; added prepare_chunk_packet.py CLI; re-exported the API from chunked_routing_lib.py; updated chunked-routing references, adapter contract/example, CLI contract, e2e tests, dogfood registry, and plugin mirror.
- Alternatives rejected: Rejected replacing propose_merges outright because existing scripts/tests depend on it and overlap clusters remain useful deterministic hints. Rejected pinning current live issue numbers in tests; new coverage uses synthetic source IDs and current-live smoke only as non-pinned validation evidence.
- Targeted verification: Focused tests: pytest -q tests/test_handoff_chunker_agentic_packages.py tests/test_handoff_chunker_cli_contract.py tests/test_handoff_chunker_ranker_packet.py tests/test_handoff_chunker_end_to_end.py tests/test_handoff_chunker_parse.py tests/test_handoff_chunker_issue_source.py tests/test_handoff_chunker_merge_proposer.py -> 110 passed. Ruff full target passed. run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review passed sync, packaging, docs, cautilus proof validator, skill validators, dogfood, ruff, length, attention visibility, and orphan guard. Current live backlog package response validated ok and materialized packages for #286/#285 and #288/#287 without pinning tests to issue numbers.
- Test duplication pressure: Added tests/test_handoff_chunker_agentic_packages.py and expanded CLI/e2e tests; length gate passes after splitting policy into chunked_routing_agentic_policy.py. Broad pytest intentionally skipped at slice closeout per run_slice_closeout --skip-broad-pytest; final goal closeout still owns broad proof.
- Critique: Slice critique folded: agentic grouping can hallucinate, so validation requires source coverage, no duplicates, max package size, non-empty rationale/unlock, and broad-label-only rejection unless adapter policy allows it. Public-skill dogfood review recorded no Cautilus scenario change because existing handoff-adapter-bootstrap evaluates routing/bootstrap, while deterministic tests cover package synthesis.
- Off-goal findings: #293 remains open; this slice did not touch its quality/testability files. #184 remained out of implementation scope and only appeared as a validated standalone package in live backlog smoke.
- Lessons carried forward: Keep work-package synthesis before ranking; use adapter policy for repo-specific broad labels; do not promote live issue numbers into deterministic tests.
- Metrics: Usage episode emitted by slice closeout: slice-closeout-5c9334d6c2c748a790fc5d5368bc9873.

## Context Sources

- `docs/handoff.md` as read on 2026-06-04: current pickup recommended #293
  first, then #286/#285, while the user chose to optimize for future work
  efficiency instead.
- GitHub issues: #286, #285, #288, #287, #289 are in scope; #293 is preflight
  context only; #184 is explicitly out of scope.
- `charness-artifacts/quality/latest.md` for the current quality posture and
  standing mutation/testability context.
- `charness-artifacts/retro/recent-lessons.md` for current repeat traps:
  broad-gate structure, live issue fixture brittleness, activation/closeout
  evidence floors, and closeout publication waste.
- `docs/conventions/implementation-discipline.md` and
  `docs/conventions/operating-contract.md` for sync-before-verify, critique,
  closeout, and handoff timing policy.

## Interview Decisions

- Mode: implementation-continuation after activation. Chosen because the user
  said "청크 A achieve" after asking to bundle efficiency work. Rejected
  artifact-only because the request was to turn the chosen chunk into the
  operating goal, not only preserve a note.
- Bundle scope: include #286/#285/#288/#287/#289. Chosen because all five reduce
  future operator waste across pickup, fixture stability, closeout, publication,
  or delivery. Rejected including #293 because it is a quality regression
  preflight, and rejected #184 because it is product-success synthesis.
- Sequence: handoff package synthesis first, fixture stability with it, then
  closeout rehearsal, Achieve policy seam, announcement delivery, final closeout.
  Rejected starting with #289 because delivery chaining is valuable but does not
  unblock the core handoff -> goal -> closeout path.
- Proof policy: deterministic local proof plus broad final closeout by default;
  live installed-host/release proof only if touched. Rejected unconditional live
  proof because the selected bundle is source/workflow behavior, not a release.
- Axis check: host/provider/repo policy varies by adapter. Chosen design keeps
  repo-local label semantics, publication policy, and delivery backend behavior
  in adapters; rejected hardcoding current GitHub/Ceal label meanings into
  portable Charness source.

## Plan Critique Findings

- Folded blocker: #293 may make final quality noisy. The plan starts with a
  preflight slice and treats #293 as context unless it directly blocks touched
  surfaces.
- Folded blocker: the bundle is broad. The slice plan keeps risk boundaries
  separate and requires slice closeout plus final broad verification rather than
  one large unreviewed implementation pass.
- Folded blocker: agentic chunking can hallucinate or over-merge. The boundary
  requires deterministic source IDs and validation before rendering or drafting.
- Folded blocker: issue closeout/publication can cause extra push/CI cycles. The
  plan puts carrier rehearsal before close keywords and records post-push
  verification separately.
- Over-worry not folded: splitting #287/#289 into separate goals could be
  cleaner, but the user's explicit efficiency-bundle request makes one goal
  acceptable as long as slices remain independently verifiable.
- Reviewer provenance: same-session achieve shaping critique; fresh-eye critique
  required before substantial slice closeout and final bundle closeout per repo
  operating contract.

## Off-Goal Findings

N/A — none discovered during shaping.

## Final Verification

Pending activation and implementation.

## User Verification Instructions

After completion, run a bare handoff pickup and inspect that it proposes
coherent work packages; inspect direct-commit closeout rehearsal output before a
close-keyword push; and review the Achieve/announcement adapter examples for
draft-only versus executable publication behavior.

## Auto-Retro

Pending completion.
