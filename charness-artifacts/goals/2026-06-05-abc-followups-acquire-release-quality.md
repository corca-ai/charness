# Achieve Goal: A~C parallel follow-ups: acquire signal fidelity (#310/#309), release resilience (#312), quality-gate economics (#307/#308)

Status: draft
Created: 2026-06-05
Activation: `/goal @charness-artifacts/goals/2026-06-05-abc-followups-acquire-release-quality.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command. No timebox: run to completion of all three chunks
and the shared final gate (user chose no work-budget).

## Active Operating Frame

- Current slice: chunk A landed (#310 `75f30584`, #309 `618bca29`); chunk B in
  progress (B1 resume-before-push, B2 read-only-safe closeout).
- Next action: implement B1+B2 (serialize C1 after B2 on the shared
  usage-episode / `run_slice_closeout.py` surface), then C1+C2, then batch the
  three per-chunk fresh-eye reviews before the shared `--release` gate.
- Quality route (B2 + C1): `quality` consulted. B2 cut = read-only-safe closeout
  (gate live usage-episode emission on `CHARNESS_QUALITY_MODE`, the signal
  `run-quality.sh` already exports). C1 = add the fast standalone
  `check_test_repo_copy_invariants.py` to the `repo-python` surface verify
  commands (named checker only; honor the issue's latency caution).
- Execution model (at `/goal`, dynamic workflow approved): pursue via a Workflow
  that fans out the three chunks as **independent slice-chains** running in
  parallel, then a single barrier before the shared final
  `./scripts/run-quality.sh --release` gate.
  - **Chunk A** (web-fetch acquisition signal fidelity): #310 → #309. Fully
    independent surface; runs unimpeded.
  - **Chunk B** (release publish-flow resilience): #312 parts 1+2.
  - **Chunk C** (quality-gate economics): #307 → #308.
  - **Shared-surface guard:** B2 (#312 part 2) and C1 (#307) both touch
    `scripts/run_slice_closeout.py`. Serialize those two edits (land B2, rebase
    C1) **or** worktree-isolate B and C and merge B before C. A needs no
    isolation.
- Verification cadence: cheap deterministic checks (targeted pytest + the owning
  `check_*.py` + `check_python_lengths`) at commit boundaries; per-chunk
  fresh-eye bounded critique + reproduce-then-fixed at slice boundaries; one
  `./scripts/run-quality.sh --release` on a clean tree at the bundle boundary.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve chunks A–C in parallel and close #307/#308/#309/#310/#312 with verified
fixes, leaving main's gather/release/quality surfaces with honest operator
signals and cheap-checks-at-the-commit-boundary discipline.

Per chunk:

- **A — gather/web-fetch acquisition error-signal fidelity**
  - **#310** (`skills/support/web-fetch/scripts/acquire_public_url.py`): on a
    cleanup error, stop clobbering the last attempt's real acquisition `.error`
    (status/confidence). Append the cleanup error to details so both the
    "why the fetch failed" signal and the cleanup error survive.
  - **#309** (`scripts/agent_browser_runtime_guard.py`): when only
    reparented/zombie residue remains, `next_step` must distinguish a
    *reap-able orphan tree* (the `--cleanup-orphans --execute` path actually
    helps) from *container-init residue* (needs an init reap / fresh container,
    not the cleanup command) so the operator is not stuck in a humane no-exit
    loop.
- **B — release publish-flow resilience (#312)**
  - **B1:** `publish_release_resume.py` should commit the refreshed
    `charness-artifacts/release/latest.md` *before* `git push` (mirroring the
    normal flow) so `.githooks/pre-push` does not block on a dirty
    `charness-artifacts/`, and must not regress the retro-trigger block to a
    dry-run (`would_write`/`release_content_paths`) payload on resume.
  - **B2:** the closeout-wrapped quality run (`publish_release.py --execute` via
    `run_slice_closeout`) must not write live `usage_episode.jsonl` episodes
    during the suite (the #194 state-bleed class that races
    `tests/test_usage_episodes_host_hooks.py`). Preferred direction (handoff
    Discuss): make the closeout-wrapped quality run read-only-safe; route the
    cut through `quality`.
- **C — quality-gate economics**
  - **#307:** run the fast standalone structural checkers
    (`scripts/check_test_repo_copy_invariants.py` and peers of the same shape)
    in the `repo-python` surface of the per-slice / pre-commit aggregate
    (`scripts/run_slice_closeout.py`) so test-fixture drift fails at the commit
    boundary, not 172s into the broad pytest gate. Weigh the fast-aggregate
    latency cost; route through `quality`.
  - **#308 (lightweight + headroom tool):** add a short, discoverable
    authoring-preflight reference (attention-state banned-vocabulary list +
    regex/string-matching edge checklist) and surface `check_python_lengths`
    per-file headroom before editing a near-limit file (add a `--headroom`-style
    mode if one does not already exist). No new gate, no active edit-time hook.

## Non-Goals

- **Chunk D / #306** (scheduled mutation gate's self-healing auto-issues) — a
  separate, larger design decision; out of scope here.
- **#311** (setup adapter-first reviewer rule greenfield-only backfill) — the
  rider item; carries its own small scoping decision and a different surface
  (`setup` / AGENTS.md). Not in this goal.
- **Cutting a new release.** B fixes the publish flow; this goal does **not**
  bump a version, edit install manifests, or publish v0.23.0.
- **#308 active tooling.** No edit-time preflight script/hook and no new gate —
  the user chose the lightweight+headroom level deliberately (the issue itself
  warns against the process overhead).
- **No live/prod proof.** The only external write is GitHub issue close via
  `gh`; no provider/live product proof is claimed.

## Boundaries

- Work in the shared parent worktree on `main` (or a single working branch);
  one commit per landed sub-slice, each carrying `Close #N` for its issue.
- **Bug-class issues (#309, #310, #312) get a `debug` root-cause step before the
  fix slice** (per the issue resolution contract), even though the issues
  already carry strong evidence — confirm the falsifiable cause, then fix.
- **#310 and #312-B2 are pre-existing / cross-cutting**, not regressions from
  #302–#305 — fix at the source, do not reopen the #302–#305 goal.
- **Chunk C routes through `quality` before impl** (both #307 and #308 are
  quality-contract / discoverability changes).
- **Shared surface `scripts/run_slice_closeout.py`** (B2 + C1): serialize the two
  edits or worktree-isolate and merge B before C; never let parallel chains race
  the same file.
- Each chunk gets a **bounded fresh-eye review in a different agent context**;
  reviewers inspect prior versions read-only (`git show <ref>:<path>`) and run no
  index- or worktree-mutating git ops in the shared parent worktree.
- Final proof is one `./scripts/run-quality.sh --release` on a **clean tree**,
  recorded as a broad-gate attestation result (gate id, PASS, clean-tree SHA) —
  not a re-embedded provider command string.
- Auto-close #307/#308/#309/#310/#312 via `Close #N` on the owning fix/closeout
  commit (user-approved); validate the closeout draft before relying on the
  keyword.

## User Acceptance

What the user can do to verify completion directly:

- `gh issue list --state closed --limit 20` shows **#307, #308, #309, #310, #312**
  closed, each referenced by a landed commit.
- **#310:** induce a cleanup error on a real acquisition failure and confirm the
  operator still sees the original acquisition `.error` (cleanup error appended,
  not overwriting).
- **#309:** with only reparented/zombie residue present, the guard's `next_step`
  tells the operator this needs an init reap / fresh container — not
  `--cleanup-orphans` — instead of a dead-end loop.
- **#312-B1:** a `publish_release_resume.py` resume leaves `charness-artifacts/`
  clean at push time (commit before push) and keeps the `written`/
  `final_release_paths` retro-trigger payload (no dry-run regression).
- **#312-B2:** the closeout-wrapped quality run no longer writes a live
  `usage_episode.jsonl` episode mid-suite;
  `tests/test_usage_episodes_host_hooks.py::test_session_capture_cli_install_and_uninstall_round_trip`
  passes inside the full suite, not only standalone.
- **#307:** introducing inline `shutil.ignore_patterns(...)` (instead of
  `REPO_COPY_IGNORE`) in a fixture test now fails the per-slice / pre-commit
  aggregate, not only the 172s broad gate.
- **#308:** a discoverable authoring-preflight reference exists and
  `check_python_lengths` reports per-file headroom.
- `./scripts/run-quality.sh --release` passes on a clean tree.

## Agent Verification Plan

### Low-Cost Checks

- Per-sub-slice targeted pytest for the touched surface (e.g.
  `tests/test_web_fetch_cleanup.py`, the runtime-guard test, the
  publish/resume tests, `tests/quality_gates/test_repo_copy_invariants.py`,
  `tests/test_usage_episodes_host_hooks.py`).
- The owning standalone `check_*.py` for the change
  (`check_test_repo_copy_invariants.py`, `check_python_lengths`).
- `git status --short` clean after each commit; `check_python_lengths` headroom
  on any near-limit file touched (notably `acquire_public_url.py`).
- `check_goal_artifact.py` on this artifact before flip-to-complete.

### High-Confidence Checks

- **Reproduce-then-fixed** for each bug (#309, #310, #312-B1, #312-B2): a failing
  observation before the fix, the same probe green after.
- **Bounded fresh-eye critique per chunk** in a separate agent context (slice
  packet handed over per the Active Operating Frame).
- Full repo pytest at the bundle boundary before the `--release` gate.

### External Or Live Proof

- `./scripts/run-quality.sh --release` on a clean tree → recorded as a broad-gate
  attestation result (gate id / PASS / clean-tree SHA).
- GitHub issue close via `gh` (issue-closeout proof, **not** live product proof).
- No provider/live/prod proof is in scope; named as skipped here so closeout
  does not over-claim.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A1 (#310) | Preserve original acquisition `.error`; append cleanup error to details | Quick win, independent surface, no design decision | debug root-cause note; reproduce-then-fixed; cleanup test green; `Close #310` | planned |
| A2 (#309) | `next_step` distinguishes reap-able orphan tree vs container-init residue | Same review lens as A1; clears 2nd `bug` | debug root-cause; reparented/zombie-only probe green; guard test; `Close #309` | planned |
| B1 (#312.1) | Resume commits `latest.md` before push; no retro-trigger dry-run regression | Recurs every resume; pre-push false-block | reproduce-then-fixed; resume/publish tests; clean tree at push; `Close #312` (with B2) | planned |
| B2 (#312.2) | Closeout-wrapped quality run is read-only-safe re: live usage episodes | #194 state-bleed class; route via `quality` | full-suite `test_usage_episodes_host_hooks` green; no mid-suite episode write | planned |
| C1 (#307) | Run fast structural checkers in `repo-python` aggregate surface | Shift cheap deterministic checks to commit boundary; via `quality` | inline-`ignore_patterns` fails the aggregate; aggregate latency delta noted; `Close #307` | planned |
| C2 (#308) | Lightweight authoring-preflight reference + `check_python_lengths` headroom | Knowing constraint before authoring; sibling to C1 | discoverable reference + pointers; headroom mode works; `Close #308` | planned |
| Z (gate) | Bundle barrier: full pytest + `--release` gate + per-chunk closeout critique | Final proof + honest closeout | `--release` PASS on clean tree (attestation); 5 issues closed; critique + retro | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary.

Execution-model note (dynamic workflow approved): at `/goal`, fan out A / B / C
as parallel slice-chains, barrier before the shared `--release` gate; isolate
B and C on the shared `run_slice_closeout.py` surface (see Active Operating
Frame). Fill the floors below during/at the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary (expected: `debug` before bug fixes, `impl` for slices, `quality` for
  chunk C and B2's quality-run cut, `issue` for closeout, `critique` per chunk),
  and record the route it returns. `Routing:` evidence required at completion or
  a `Routing: n/a — <reason>` opt-out.
- **Gather step** — `Gather: n/a — <reason>` expected; `## Context Sources` are
  local artifacts/issues, no external URL/Slack/Notion/Docs/Drive fetch.
- **Release step** — this goal touches release *tooling* (`publish_release*.py`)
  but does **not** cut a release; expected `Release: n/a — publish-flow fix
  only, no version bump or manifest edit`. If the run ends up editing an install
  manifest, replace with a real `Release:` proof line.
- **Issue closeout step** — resolves **#307, #308, #309, #310, #312**; carrier
  `direct-commit` (`Close #N`); proof via
  `issue_tool.py validate-closeout-draft` / `verify-closeout`. #311 and #306 are
  out of scope (Non-Goals), not closed here.

## Discuss Before Activation

Discuss before activation: APPROVED — issue auto-close (#307/#308/#309/#310/#312),
the broad 5-issue/3-chunk parallel bundle, the #312-B2 read-only-safe-closeout
default, and the no-live-proof scope were all surfaced and resolved/approved in
the Before-phase interview; the only external write is GitHub issue close via `gh`.

Consequential defaults surfaced for review before `/goal` — all resolved/approved
in the Before-phase interview:

- **Issue auto-close of #307/#308/#309/#310/#312** — **APPROVED** (user chose
  "해결 시 자동 close"). GitHub is the source of truth; close via `Close #N` on the
  owning commit after verification.
- **Broad bundled scope** (5 issues, 3 chunks, one goal, executed in parallel) —
  **APPROVED** (user explicitly requested A~C in one parallel goal). Chunks
  commit and close independently so one chunk's failure does not force-close
  another; the `--release` gate is the only shared barrier.
- **#312-B2 behavior change** (make the closeout-wrapped quality run
  read-only-safe so it stops writing live usage episodes during the suite) —
  **RESOLVED with recommended default** per the handoff Discuss; routed through
  `quality` during impl. Reversible; confirm the exact cut (read-only-safe
  closeout vs. test-robustness) when `quality` weighs in.
- **No live/prod proof** — only external write is GitHub issue close via `gh`;
  named as skipped so closeout does not over-claim.

Resolved/approved — activation-ready.

## Slice Log

(empty until activation)

### Slice 1: A1 (#310) — preserve acquisition .error on cleanup failure

- Objective: Stop the agent-browser cleanup error from clobbering the last attempt's real acquisition .error/status/confidence; append cleanup error to details instead.
- Why this approach: Minimal, source-located fix at acquire_public_url.py:_browser_stage; preserve original error when present, only promote cleanup error to .error when the attempt had none (degraded close stays non-silent).
- Commits: 75f30584
- What changed: skills/support/web-fetch/scripts/acquire_public_url.py (+ synced plugin mirror); tests/test_web_fetch_cleanup.py reproduce test.
- Alternatives rejected:
- Targeted verification: reproduce-then-fixed: test_acquire_preserves_render_error_when_cleanup_also_fails (red before, green after); full tests/test_web_fetch_cleanup.py 7 passed; ruff + check_python_lengths headroom 44 left; pre-commit gate green.
- Test duplication pressure:
- Critique: Debug root-cause confirmed falsifiably: the unconditional 3-tuple assignment overwrote .error; reproduce test proved it. Bounded fresh-eye review batched at chunk boundary before --release.
- Off-goal findings:
- Lessons carried forward: Existing cleanup tests all used render-SUCCESS, masking the render-FAILURE clobber path; the new test closes that gap.
- Metrics:

### Slice 2: A2 (#309) — runtime guard next_step distinguishes residue class

- Objective: next_step must tell apart a reap-able orphan daemon tree (--cleanup-orphans helps) from container-init residue (reparented/zombie only -> needs init reap / fresh container).
- Why this approach: Add runtime_next_step() returning (next_step, next_step_kind); init_reap guidance printed verbatim, cleanup_command printed as a runnable command. Also corrects helpcheck-only failures to stop suggesting cleanup.
- Commits: 618bca29
- What changed: scripts/agent_browser_runtime_guard.py (+ synced plugin mirror); tests/test_agent_browser_runtime_guard.py (2 reproduce tests).
- Alternatives rejected:
- Targeted verification: reproduce-then-fixed: test_runtime_next_step_distinguishes_residue_class + test_assert_no_orphans_init_reap_guidance_for_reparented_only (red before, green after); full guard suite 11 passed; ruff + attention-state + lengths green.
- Test duplication pressure:
- Critique: Debug root-cause: cleanup_orphans targets only orphan_tree_pids while runtime_residue_total also counts reparented+zombie; reproduce test confirmed the no-op loop. Fresh-eye review batched at chunk boundary.
- Off-goal findings:
- Lessons carried forward: next_step is operator-facing UX; a single string field needed a kind discriminator so prose guidance isn't wrapped in a Run-this-command phrasing.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order:

1. GitHub issues **#310, #309** (chunk A), **#312** (chunk B), **#307, #308**
   (chunk C) — primary specs with evidence and file/line pointers.
2. `docs/handoff.md` → "Next Session" #309–#312 routing + "Discuss" (#312 before
   next release; closeout should be read-only-safe).
3. `charness-artifacts/critique/2026-06-05-v0.22.0-release-critique.md` —
   findings E (#309), F (#310), G (#311, out of scope) and the Release Outcome
   that motivated #312.
4. `charness-artifacts/goals/2026-06-05-302-305-gather-setup-release-robustness.md`
   — the originating robustness goal whose closeout surfaced #307/#308 (and
   whose work the #309/#310/#312 fixes sit adjacent to). Do not reopen it.
5. `docs/conventions/implementation-discipline.md` — "cheap deterministic checks
   at commit boundaries, expensive proof at bundle boundary" cadence that #307
   restores and #308 supports.

## Interview Decisions

For each Before-phase question: family considered, chosen value, rejected
alternatives, and an anti-anchoring axis note.

1. **Timebox** — family {6h, 3h, no timebox}. **Chosen: no timebox** — run to
   completion of all of A~C + the shared gate. Rejected 6h/3h because the user
   wants the full bundle done, not a time-bounded slice. _Axis:_ `single-point:
   this goal is scope-bounded by 5 named issues, not a time budget`; no timebox
   fields are written.
2. **Issue closeout** — family {auto-close on resolve, resolve+leave-open}.
   **Chosen: auto-close.** Rejected leave-open: repo treats GitHub as source of
   truth and the issues are concrete bug/enhancement items with verifiable fixes.
   _Axis:_ `single-point: repo issue-closeout policy, not host-varying`.
3. **#308 scope** — family {lightweight+headroom tool, pointer-only, active
   tooling}. **Chosen: lightweight + headroom.** Rejected pointer-only as
   under-delivering the one real code win (length headroom surfacing); rejected
   active tooling as the process overhead the issue itself warns against.
   _Axis:_ `single-point: authoring-discipline affordance, not host/provider
   varying`.

Anti-anchoring on inherited values: the `./scripts/run-quality.sh --release`
gate and `run_slice_closeout` aggregate are repo-owned surfaces
(`single-point: repo-local quality tooling`), not host/provider axes; no
confirmed model/host value was locked into this plan.

## Plan Critique Findings

Provenance: `achieve` Before-phase self-critique. Per-slice bounded fresh-eye
critique (different agent context) is deferred to the During phase per chunk
(slice packet in the Active Operating Frame).

Blockers folded into Boundaries / Verification / Slice Plan:

- **Shared `run_slice_closeout.py` between B2 and C1** → folded into Boundaries +
  Active Operating Frame as a serialize-or-isolate rule (land B2, rebase C1; or
  worktree-isolate B and C, merge B first).
- **#312-B2 has two valid cuts** (read-only-safe closeout vs. robust test) →
  folded: default to read-only-safe per handoff, routed through `quality`,
  flagged in Discuss as confirm-during-impl.
- **#307 could regress fast-aggregate latency** (the issue's own caution) →
  folded into C1 expected evidence: keep the checkers path-scoped/fast and record
  the aggregate latency delta; back out if it materially slows the commit path.
- **Parallel close of 5 issues risks one failing chunk blocking others** →
  folded: chunks commit/close independently; only the `--release` gate is shared.

Over-worry raised but not folded:

- "Workflow parallelism causes merge chaos" — mitigated by isolating only the
  overlapping surface (B, C on `run_slice_closeout.py`); A is independent. Not a
  blocker, so no isolation is forced on A.
- "Bug issues already have evidence, so `debug` is ceremony" — kept the
  root-cause step anyway (cheap, and the issues are the resolution contract), but
  scoped it to a falsifiable cause confirmation, not a full investigation.

## Off-Goal Findings

(none yet — file via `issue` during the run and record only the reference + reason here)

## Final Verification

Pending — populated at closeout: per-bug reproduce-then-fixed results, full
pytest, the `./scripts/run-quality.sh --release` broad-gate attestation (gate id
/ PASS / clean-tree SHA), and the five issue-close proofs. No live/prod proof in
scope.

## User Verification Instructions

After the run completes, verify directly:

1. `gh issue list --state closed --limit 20` → confirm #307, #308, #309, #310,
   #312 closed with referencing commits.
2. Re-run the per-bug reproduce checks listed under `## User Acceptance`.
3. `./scripts/run-quality.sh --release` → expect PASS on a clean tree.
4. Confirm the #308 authoring-preflight reference is discoverable and
   `check_python_lengths` reports per-file headroom.

## Auto-Retro

Pending — runs at the After phase via `retro`; each surfaced improvement gets an
explicit `applied: <what>` or `issue #N` disposition (or one falsifiable
`Retro dispositions: none — <reason>` line).
