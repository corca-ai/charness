# Achieve Goal: Post-push queue — push/release-lane verification + deleted-checkout settings scan + PR-mirror first execution

Status: draft
Created: 2026-06-10
Activation: `/goal @charness-artifacts/goals/2026-06-10-postpush-verification-deleted-checkout-scan-pr-mirror.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-10-postpush-verification-deleted-checkout-scan-pr-mirror.md`.
- Timebox: 3h
- Activation time: set at `/goal` activation (REPLACE with an ISO timestamp at
  activation — the complete gate parses `Activation time:` as ISO; two prior
  goals carried this exact reminder for a reason).
- Closeout reserve: 30m
- Done-early policy: continue_next_improvement (if a slice closes early,
  continue to the next surfaced improvement rather than stopping).
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Clear the post-push/release-lane queue in three independent per-slice-closed-out
slices, synthesized from the 2026-06-10 next-queue goal's retro and non-claims,
the refreshed handoff, the open-issue state, and recent-lessons: (1)
**PUSH/RELEASE-LANE VERIFICATION (read/verify-first).** The 2026-06-10
push + release lane (executed right after this goal was shaped) produced
deferred proofs this goal consumes read-only: #342, #343, and #344 reach
CLOSED on GitHub via their staged `Closes #N` carriers (verify with
`issue_tool.py verify-closeout --expect-state CLOSED` per issue — never
manually close), the `quality-core.yml` push run on the new HEAD is green
(triage any failure per the CI-only failure-recovery protocol, repair
repo-locally), the release publish verified its installed-surface refresh
(installed version == released tag, per the release-helper contract), and the
next green scheduled `mutation-tests.yml` run over the pushed state stays
green. (2) **DELETED-CHECKOUT SETTINGS SCAN.** Close the honestly-documented
blind spot from #343 (authoring-preflight.md: "a *deleted* checkout's
leftover settings entries are not detectable from a surviving checkout's
state"): extend the existing `hook_liveness` status surface with a
settings-file scan — host settings entries (claude `settings.json`, codex
`hooks.json`, codex `config.toml` charness-marker blocks) whose command
carries a known charness hook-script basename but whose embedded absolute
path no longer exists are reported as dangling-from-any-checkout. Advisory
status surfacing under the existing drift contract, NOT a new hard gate; the
known-basename list derives from the registry/sibling modules' script
constants (single source, no forked list). (3) **PR-MIRROR FIRST EXECUTION +
F4 TEST.** The quality-core PR-mirror job has never executed on a real PR
(every push-event run correctly skips it). Carry the slice-4 critique's
deferred F4 test (an end-to-end seeded-tmp-repo positive for
`advise_new_pool_module`, using the `_seed_repo` pattern from
`tests/quality_gates/test_slice_closeout_base_range.py`) on a branch, open
ONE bounded PR, consume the PR-mirror job's first real verdict (green, or
triaged + repaired locally on the branch), then merge the green PR. Each
slice closes out independently; skill-script changes mirror byte-synced;
deterministic gates own closeout; no `#N` anchors in skill-package files.

## Non-Goals

- Do NOT take on **#184** (product success metrics) — FOURTH consecutive
  deliberate exclusion; it is product-level and needs an operator
  `ideation` session shaped into its own goal. If the operator wants it
  next, that ideation session is the prerequisite, not a slice here.
- Do NOT manually close #342/#343/#344 — their staged carriers own the
  close; slice 1 only verifies the expected CLOSED state and investigates
  (not force-closes) any mismatch.
- Do NOT cut a release in this goal — the 2026-06-10 release lane precedes
  activation; slice 1 verifies it. A repair that would need a new release
  is named as the next operator lane, not executed here.
- Do NOT add consumer-inherited blocking behavior: the settings scan is
  status/doctor surfacing that degrades to silence when settings files are
  absent/unreadable; repos without charness hooks inherit nothing.
- Do NOT fork the known-hook-basename list — derive it from the modules
  that own the script constants (install lib + registry siblings).
- Do NOT open more than the ONE named PR, and do not enable any other
  workflow trigger while consuming the PR-mirror verdict.

## Boundaries

- **Slice 1 — lane verification.** READ/VERIFY-FIRST: `gh issue view` /
  `issue_tool.py verify-closeout --expect-state CLOSED` for #342/#343/#344;
  `gh run list/view` for the post-push quality-core run and the next
  scheduled mutation run; release verification via the release skill's
  recorded proof artifacts (installed == released). Repairs for CI friction
  are local-only; a repair changing workflow behavior re-verifies via the
  slice 3 PR (if it touches the mirror) or the next operator push (named
  deferred if so).
- **Slice 2 — settings scan.** Extends `hook_state_liveness` /
  `--mode status` payload (a `settings_scan` or equivalent section beside
  `hook_liveness`); the known-basename set must be derived from the owning
  modules' constants; per-format readers reuse the existing JSON/TOML
  helpers (no new parsers); flags join the drift list under the existing
  "exit 1 on drift" status contract; tests per format + a
  degrades-to-silence negative (missing/unreadable settings, foreign hooks
  untouched); the docs line in authoring-preflight.md that named this gap
  is updated to claim exactly what now exists.
- **Slice 3 — PR-mirror + F4.** The branch carries ONLY the F4 test (and
  any slice-3-scoped repair); the PR is opened against main, the PR-mirror
  job verdict is recorded (run id + conclusion), and the PR merges only
  when green (merge = the goal's one authorized remote mutation beyond the
  PR itself). If the mirror job fails for infrastructure reasons, record
  the honest signal, repair locally on the branch, and re-push the branch
  (branch pushes are within the PR lane's authorization).
- **Public-skill + generated-surface scope.** Any skill-script change
  mirror-synced (`plugins/charness/...`); deterministic gates own closeout;
  no `#N` anchors in skill-package files; new-pool-module advisory heeded
  (walk new modules' environment-dependent branches in the introducing
  slice — the trap fired three goals running).
- Discuss before activation: RESOLVED — (a) `production_or_live_proof` +
  remote side-effects: slice 1 is read-only consumption of the
  operator-authorized 2026-06-10 push/release lane's results; slice 3
  creates ONE bounded PR (branch push + PR open + merge-when-green) whose
  sole content is the named F4 test — the operator activating this goal
  with `/goal` authorizes exactly that PR lane, nothing broader; re-open
  this item instead of activating if that scope is wrong. (b) `issue_close`:
  no issue is close-intended by this goal (slice 1 verifies closes the
  push already delivered; slice 2's gap is tracked by this artifact, not an
  issue). (c) No release is cut by this goal.

## User Acceptance

What the user can do to verify completion directly.

- **Slice 1:** `gh issue view 342 343 344` each show CLOSED with the
  carrier commit referenced; the goal artifact's slice log names the
  post-push quality-core run id + verdict and the release-verification
  evidence; #335 stays closed with scheduled runs green.
- **Slice 2:** delete (or rename) a charness hook script path referenced by
  a host settings entry on a scratch HOME and run
  `python3 scripts/reconcile_usage_episodes_host_hooks.py --mode status
  --home <scratch>` — the leftover entry is flagged even though no state
  file knows it; a HOME without settings files reports silence; the
  authoring-preflight.md paragraph no longer names the blind spot as open.
- **Slice 3:** the PR shows the `Changed-line mutation coverage (PR
  mirror)` job EXECUTED (not skipped) with its verdict; the F4 test is on
  main after the green merge; the goal artifact records the run id.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths --headroom` on every touched
  file; mirror byte-sync for any exported-script change; the touched test
  modules per slice (host-hook family for slice 2, the new advisory test
  module for slice 3).
- Slice 2: the new-pool-module advisory's own early producer+consumer
  self-check BEFORE the slice commit when a new pool module is added
  (dogfood the slice-4 advisory; confirm, don't discover).

### High-Confidence Checks

- Full relevant test surface green per slice; broad gate
  (`run-quality.sh --read-only`) + changed-line producer
  (`run_slice_closeout.py --base --verification-lock
  --produce-mutation-coverage`) at the bundle boundary, consumer confirming
  0 uncovered. Fresh-eye `critique` at each mutating slice boundary;
  the goal-closeout disposition review at the end.

### External Or Live Proof

- Slice 1 consumes already-executed remote proofs read-only via `gh`.
- Slice 3's PR is the goal's one authorized remote lane: branch push, PR
  open, PR-mirror verdict consumption, merge-when-green. Any further
  remote re-verification beyond that PR is the next operator lane.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Verify the 2026-06-10 push/release lane: #342/#343/#344 CLOSED via carriers, post-push quality-core green, release installed-surface verified, scheduled mutation green | the lane executes immediately after this goal is shaped; its proofs are this goal's named deferred inputs — consuming them closes the loop the honest way | verify-closeout CLOSED x3; run ids + verdicts in slice log; release proof referenced | planned |
| 2 | Deleted-checkout settings scan in the existing status surface; docs updated to match the new honest claim | #343 shipped with this blind spot explicitly documented as open; the registry + liveness seam from slice 2 of the prior goal makes the extension cheap now | settings-scan section + tests per format + degrade negative; docs paragraph updated; status flags leftover entries from a scratch HOME | planned |
| 3 | PR-mirror first real execution carrying the F4 seeded-repo e2e test; merge when green | the mirror job is the last never-executed CI surface (named non-claim twice); F4 is the only deferred test debt — one bounded PR pays both | PR url + mirror job run id + verdict; F4 test on main post-merge | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out. (Reminder: the summary `Routing:`
  line must be ONE line naming find-skills plus each triggered phase skill —
  wrapped lines fail the floor parser.)
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — no issue is close-intended by this goal: #342/#343/#344
  closes are verify-only (their carriers own them; record the
  `verify-closeout --expect-state CLOSED` proof in slice 1) and #184 is
  context-only (`Issue closeout: n/a` expected for this goal unless a slice
  files something new).

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **The prior goal + its retro:**
   `charness-artifacts/goals/2026-06-10-342-343-adapter-schema-hook-lifecycle-deferred-proofs.md`
   (`## Final Verification` non-claims: carriers land on push; PR-mirror
   never executed on a real PR) and
   `charness-artifacts/retro/2026-06-10-342-343-next-queue-goal-retro.md`
   (W1 trend + the applied advisory this goal must dogfood).
2. **The slice-4 critique's deferred F4:**
   `charness-artifacts/critique/2026-06-10-344-new-pool-module-advisory-critique.md`
   (F4 valid-but-defer: seeded-repo e2e positive via the
   `tests/quality_gates/test_slice_closeout_base_range.py` `_seed_repo`
   pattern).
3. **The #343 documented blind spot:**
   `docs/conventions/authoring-preflight.md` (multi-checkout posture
   paragraph: deleted-checkout leftovers undetectable from state; "a
   settings-file scan stays deferred") and
   `charness-artifacts/critique/2026-06-10-343-host-hook-lifecycle-critique.md`
   (the reviewer's honest-scope analysis that shaped the non-claim).
4. **Handoff + open issues:** `docs/handoff.md` (Next Session: push lane,
   PR-mirror deferred proof, #184 exclusion); open issues #342/#343/#344
   (carrier-staged) + #184 (excluded).
5. **Recent lessons:** `charness-artifacts/retro/recent-lessons.md` (the
   confirm-not-discover repeat trap + the release-helper persistence note
   that slice 1's release verification leans on).
6. **Surfaces to touch:** `scripts/host_hook_registry.py` +
   `scripts/host_hook_install_lib.py` + `scripts/host_hook_codex_toml_lib.py`
   + `scripts/reconcile_usage_episodes_host_hooks.py` +
   `tests/test_host_hook_registry.py` (slice 2);
   `tests/quality_gates/test_slice_closeout_new_pool_advisory.py` +
   `.github/workflows/quality-core.yml` (slice 3, read-only unless repair);
   `gh run list/view`, `gh pr` (slices 1 and 3).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

- **Which next work (operator-directed: "이번 세션 교훈, handoff, 열린 이슈,
  최근 레슨 포함해서 다음 할 일", followed by an operator-ordered push +
  release lane).** Family: {post-lane verification; deleted-checkout
  settings scan; PR-mirror first execution + F4; #184; idle until lane
  lands}. Chosen: **verification + settings scan + PR-mirror/F4** — the
  first consumes the lane the operator just ordered (the same
  deferred-proof pattern the prior goal proved out), the second closes the
  only honesty gap #343 left documented-but-open, the third retires the
  last never-executed CI surface and the only deferred test debt in one
  bounded PR. Rejected: #184 (fourth consecutive exclusion — product-level,
  needs operator ideation as its own goal; bundling it would repeat the
  mistake three prior goals deliberately avoided); idle-until-lane (slices
  2–3's mutating work has no ordering dependency on slice 1's reads).
- **Slice 2 scan scope (probe, not fixed).** Family: {scan all three
  settings formats; JSON-only first; fold into hook_liveness vs a sibling
  section}. Deferred to slice 2 verify-first — but a forked basename list
  is pre-rejected (derive from owning modules), and silence-on-absent is
  fixed (consumer repos inherit nothing).
- **Slice 3 PR mechanics (probe, not fixed).** Family: {PR from an
  in-repo branch; PR from a worktree; synthetic PR with a trivial doc
  change instead of F4}. Chosen direction: in-repo branch carrying F4 (a
  PR must change a mutation-pool-relevant path for the mirror job to have
  real work; F4 is test-only — verify at slice time whether the mirror's
  path filter needs a pool file touched and adjust the branch content
  minimally if so, recording the decision). Trivial-doc PR rejected: it
  would exercise the trigger but not the gate's real path.
- **Activation timing.** Activate AFTER the 2026-06-10 push + release lane
  completes (the lane runs in the same session this goal is shaped); if the
  scheduled mutation run hasn't fired by activation, slice 1 records the
  latest available run and the next-run check becomes a named deferred
  proof rather than a blocker.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. A fresh-eye plan critique runs at
activation per the verification cadence.

- **Provenance:** self-critique by the shaping session.
- **Slice 3 could quietly expand remote side-effects (extra PRs, workflow
  edits re-running CI).** Folded: ONE bounded PR named in Non-Goals +
  Boundaries; merge-when-green is the only remote mutation beyond it; the
  Discuss item makes `/goal` activation the explicit authorization.
- **Slice 2 could fork the hook-basename list or break consumer repos.**
  Folded: single-source derivation + degrade-to-silence are Boundaries;
  the per-format negative tests are named evidence.
- **Slice 1 could drift into manually closing issues on mismatch.**
  Folded: verify-only posture in Non-Goals (investigate, never force-close).
- **The mirror job might not run on a test-only PR (path filter).**
  Folded into Interview Decisions: verify the filter at slice time and
  adjust branch content minimally, recording the decision.
- **Over-worry (raised, not folded):** that slice 1 duplicates the release
  skill's own verification — it consumes the recorded proofs rather than
  re-running them; read-only consumption is cheap and closes the loop.

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
