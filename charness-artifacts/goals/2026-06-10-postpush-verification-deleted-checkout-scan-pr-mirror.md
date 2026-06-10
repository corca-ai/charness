# Achieve Goal: Post-push queue — push/release-lane verification + deleted-checkout settings scan + PR-mirror first execution

Status: complete
Created: 2026-06-10
Activation: `/goal @charness-artifacts/goals/2026-06-10-postpush-verification-deleted-checkout-scan-pr-mirror.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- All three slices complete; goal in closeout. Slice 2's commit is
  011a931f after the post-merge rebase onto origin/main (originally
  authored as 868181ef — historical SHA, rewritten by the rebase).
- Bundle proof: locked producer closeout PASS (broad pytest green,
  coverage produced), consumer ok=true / 0 uncovered over the three slice
  2 pool files, `run-quality.sh --read-only` 73 passed / 0 failed.
- Remaining deferred proof: the next scheduled `mutation-tests.yml` run
  over merged main 39ff5432 (cron 17 */3; recheck recorded below).
- No safe next slice: all three slices are complete with bundle proof;
  the only open item is the scheduled mutation run, which cannot progress
  before the 10:17Z cron slot (outside the timebox), and the next
  surfaced improvement (#346, a retro/achieve skill-script capability
  change touching exported plugin surfaces) is its own lane, not a safe
  tail slice inside this goal's closeout reserve.
- Timebox: 3h
- Activation time: 2026-06-10T15:14:07+09:00
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
Filled at completion:

Routing: find-skills (session bootstrap + task-text recommendation probe, no skill-specific route returned) -> achieve (goal lifecycle), impl (slice 2/3 mutation work under achieve's coordination, implementation-discipline contract consulted before mutation), quality (deterministic gate cadence: rehearsal + locked producer closeout + consumer + run-quality broad gate), critique (three bounded fresh-eye reviews: activation plan, slice 2, slice 3 post-hoc), issue (slice 1 verify-closeout proofs + #346 filing via issue_tool), retro (session retro + persistence).

Gather: n/a — every context source is repo-internal (goal/critique/retro artifacts, docs, scripts); remote state was consumed via `gh` reads, not external documents.

Release: n/a — no version bump or install-manifest edit; slice 1 verified the PRE-EXISTING v0.37.0 release lane read-only (installed 0.37.0 == released tag), and the plugin-mirror byte-sync is generated-surface sync, not a release surface.

Issue closeout: n/a — no issue close-intended: #342/#343/#344 verify-only (CLOSED via their carriers; `verify-closeout --expect-state CLOSED` proofs in the Slice Log); #184 context-only (fourth deliberate exclusion); #346 newly FILED (not closed) from the retro's sibling search; #347 closed only as an accidental duplicate of #346 created by the same filing action.

- **Issue closeout step** — no issue is close-intended by this goal: #342/#343/#344
  closes are verify-only (their carriers own them; record the
  `verify-closeout --expect-state CLOSED` proof in slice 1) and #184 is
  context-only (`Issue closeout: n/a` expected for this goal unless a slice
  files something new).

## Slice Log

### Slice 1: Slice 1 — push/release-lane verification (read-only)

- Objective: Consume the 2026-06-10 push + release lane's deferred proofs read-only: issue closes, post-push CI, release installed-surface, scheduled mutation run.
- Why this approach: Verify-first per the goal: carriers own the closes; gh + issue_tool verify-closeout are the read-only consumption surfaces; no remote mutation.
- Commits: none (read-only slice; goal-artifact log update committed with activation bookkeeping)
- What changed: Goal artifact only (activation stamp + this slice log).
- Alternatives rejected: Manual gh issue close on mismatch (pre-rejected non-goal); re-running release verification instead of consuming recorded proof (over-worry, rejected at shaping).
- Targeted verification: issue_tool.py verify-closeout --expect-state CLOSED: #342 via 76909cc8, #343 via 7f835610, #344 via cd2618d1 — all status=verified, state=CLOSED. quality-core.yml push run 27254637832 on HEAD 3310b28b: success (3e735cad run 27254628529 also success; sibling 27254628519 cancelled by concurrency, superseded). Release: charness-artifacts/release/latest.md records v0.37.0 publish + verification; installed plugin ~/.agents/src/charness at version 0.37.0, checkout v0.37.0-1-g3310b28b == repo HEAD (installed == released tag). mutation-tests.yml: latest scheduled run 27253892006 (58cc749a, 04:47:58Z) success — fired pre-push; post-push scheduled run not yet fired at activation; named deferred proof with recheck at closeout per the activation-timing interview decision.
- Test duplication pressure:
- Critique: Activation-time fresh-eye plan critique running in parallel (bounded reviewer); slice 1 itself is non-mutating so no slice-boundary critique owed.
- Off-goal findings: none
- Lessons carried forward: Two push runs can appear for one lane (branch+tag); the concurrency-cancelled twin is expected, record the surviving green run id.
- Metrics:

### Slice 2: Slice 2 — deleted-checkout settings scan

- Objective: Close the #343-documented blind spot: flag host-settings hook entries left behind by a DELETED checkout (invisible to state-driven hook_liveness) via a direct settings-file scan in the existing status surface.
- Why this approach: Extend host_hook_registry in place (no new pool module, plenty of length headroom): known-basename set derived from the owning modules' script constants via a new script_relative_attr registry-row field (activation-critique adjustment 5); per-format readers reuse the existing JSON helpers and the TOML lib's line parser (made public: toml_command_value); settings_scan joins the pre-existing exit-1-on-drift status contract.
- Commits: 011a931f (post-rebase rewrite of the originally-authored 868181ef; rebased onto origin/main 39ff5432 after the slice 3 merge)
- What changed: scripts/host_hook_registry.py (script_relative_attr field, known_hook_script_basenames, _json_settings_commands, _toml_settings_commands, settings_file_scan, docstring no longer defers the scan); scripts/host_hook_codex_toml_lib.py (toml_command_value made public); scripts/reconcile_usage_episodes_host_hooks.py (settings_scan payload section + drift join); tests/test_host_hook_registry.py (+10 tests); docs/conventions/authoring-preflight.md (blind-spot paragraph now claims exactly the shipped behavior); plugins/charness/scripts/ mirrors byte-synced.
- Alternatives rejected: Forked literal basename list (pre-rejected non-goal); marker-block TOML identification (shipped basename filter is strictly broader and safe — recorded as critique F3); module-attribute introspection for derivation (critique preferred the explicit registry-row field).
- Targeted verification: 21/21 module tests, 64/64 host-hook family; ruff + py_compile + length headroom green (registry 216/480); registry line coverage 96% with every slice-changed line executed in-process (degrade branches walked deliberately: malformed JSON shapes, PermissionError, unparseable command — the W1 confirm-not-discover lesson applied); live scratch-HOME acceptance: leftover entry flagged with NO state file knowing it, exit 1; e2e subprocess test pins the same case.
- Test duplication pressure: New tests reuse the module's existing _fake_home/_seed_state helpers plus one new _claude_settings_payload helper; the two status-mode subprocess tests share shape with the pre-existing dangling-hook test (acceptable duplication: each pins a distinct detection source — state vs settings).
- Critique: Fresh-eye bounded reviewer (slice2-critique): SHIP-WITH-NITS, no blockers — charness-artifacts/critique/2026-06-10-settings-scan-slice-critique.md; F2 (intents passthrough) folded before commit, F1 (direct-exec loud-over-silent edge) and F3 (basename-not-marker TOML decision) documented.
- Off-goal findings: none
- Lessons carried forward: Non-claims: scan covers the three default settings paths only (no custom/project-level settings locations); a hand-written interpreter-less entry with a known basename reports loudly even when live (inherited posture); scan reports, never removes.
- Metrics:

### Slice 3: Slice 3 — PR-mirror first execution + F4

- Objective: Land the deferred F4 seeded-repo e2e test for advise_new_pool_module via ONE bounded PR and consume the quality-core PR-mirror job's first real verdict.
- Why this approach: Branch pr-mirror-f4-seeded-e2e cut from origin/main (activation-critique adjustment 2 — local main carried unpushed slice 1/2 commits). The mirror JOB executes on any PR, but a test-only diff short-circuits the gate green (tests/ is not a mutation pool), so per the interview decision's pre-authorized minimal adjustment the branch also carries a docstring amendment to scripts/slice_closeout_advisories.py (eligible pool file) noting the e2e pin — making the gate run its full real path (coverage probe + changed-line classification). Decision recorded in Plan Critique Findings before the branch was cut.
- Commits: 43476ae6 on the branch; squash-merged to origin/main as 39ff5432 (PR https://github.com/corca-ai/charness/pull/345); branch deleted after merge.
- What changed: tests/quality_gates/test_slice_closeout_new_pool_advisory.py (+1 e2e test: seeded tmp repo with local origin/main anchor, real eligibility glob, no mocks); scripts/slice_closeout_advisories.py docstring (+plugins mirror byte-synced).
- Alternatives rejected: Test-only PR accepting the gate-internal skip-green (rejected: equivalent to the trivial-doc PR the goal pre-rejected — exercises the trigger, not the gate's real path); a behavior-bearing pool change (rejected: scope creep; the docstring touch is zero-behavior-risk and still puts an eligible file in the range).
- Targeted verification: PR-mirror job EXECUTED on PR 345: run 27258023056, job 80496728903 'Changed-line mutation coverage (PR mirror)', conclusion success, 9m51s; gate payload: ok=true, blocking=[], changed_pool_files=[scripts/slice_closeout_advisories.py] — the eligible-file analysis path, not the no-eligible-files skip. Core deterministic gates job 80496728922 success. Local: 8/8 advisory module tests, ruff, length headroom, mirror cmp. Merged only after green; merge commit 39ff5432 verified on origin/main.
- Test duplication pressure: The e2e test seeds its own tmp repo inline rather than importing the base-range module's _seed_repo (cross-test-module imports avoided); duplication is one ~10-line git seed block shared as a PATTERN across two modules — acceptable, each module stays self-contained.
- Critique: Slice design was pre-reviewed in depth by the activation plan critique (mirror path-filter analysis, branch-base contamination, ONLY-F4 boundary tension — all folded); a post-hoc fresh-eye pass runs with the goal-closeout disposition review.
- Off-goal findings: none
- Lessons carried forward: Non-claim: the PR carried no mutable changed line (docstring only), so the blocking arm classified an empty changed-mutable-line set; blocking-arm-on-real-uncovered-lines remains proven by local/unit tests and the scheduled mutation suite, not by this PR. Residual: local main diverged from remote during the lane (rebased after merge); slice 1/2 work reaches remote CI on the next operator push.
- Metrics:

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

- **Provenance:** self-critique by the shaping session; fresh-eye activation
  critique by a bounded reviewer subagent at 2026-06-10 activation — verdict
  PROCEED-WITH-ADJUSTMENTS, adjustments folded below.
- **Activation critique adjustments (folded):** (1) the mirror JOB executes on
  any PR (no path filter; `if: github.event_name == 'pull_request'` only), but
  the gate inside short-circuits skip-green for a test-only diff (`tests/` is
  not in `MUTATION_POOLS`) — slice 3 resolves this via the interview decision's
  pre-authorized minimal pool-file touch, recorded at slice time. (2) Cut the
  slice 3 branch from **origin/main**, never local main — local main carries
  unpushed slice 1/2 commits that must not ride the PR; named residual: local
  and remote main diverge until the next operator push (slice 2's work reaches
  remote CI only then). (3) `verify-closeout` requires the full argparse set
  (`--repo/--number/--classification/--carrier[/--commit-ref]`); slice 1 used
  exactly that. (4) `latest.md` carries no `install_refresh` line (ephemeral
  publish payload only) — slice 1's installed==released claim rests on the
  live local probe (installed plugin version 0.37.0, checkout == repo HEAD),
  not a recorded artifact line. (5) Slice 2's basename derivation gets an
  explicit `script_relative_attr` registry-row field resolved against the
  owning module's constant (keeps "a fourth intent is a table row" true; no
  forked list). Over-worry (raised, not folded): post-merge push-run flake on
  main — merge-when-green already CI-verifies the merged content; an infra
  flake is the next operator lane.
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

No safe next slice: all three slices complete with bundle proof; the only open item (the scheduled mutation run over 39ff5432) cannot progress before the 10:17Z cron slot, outside the timebox, and the next surfaced improvement (#346, a skill-script capability change on exported plugin surfaces) is its own lane, not a tail slice inside the closeout reserve.

Retro: charness-artifacts/retro/2026-06-10-postpush-goal-retro.md
Host log probe: charness-artifacts/retro/2026-06-10-postpush-goal-host-log-probe.md
Disposition review: charness-artifacts/critique/2026-06-10-postpush-goal-disposition-review.md
Early-close report: charness-artifacts/goals/2026-06-10-postpush-verification-deleted-checkout-scan-pr-mirror-early-close-report.md

Self-verification (executed):

- Slice gates: per-slice cheap checks green (py_compile/ruff/lengths,
  module + family tests); fresh-eye bounded reviews at every mutating
  boundary — activation plan critique PROCEED-WITH-ADJUSTMENTS (all five
  adjustments folded), slice 2 SHIP-WITH-NITS (nits folded/documented,
  charness-artifacts/critique/2026-06-10-settings-scan-slice-critique.md),
  slice 3 post-hoc SHIP-CONFIRMED (no defects).
- Bundle gates: `run_slice_closeout.py --base --verification-lock
  --produce-mutation-coverage` PASS (broad pytest green, instrumented);
  consumer `check_changed_line_mutation_coverage --base-sha origin/main
  --reuse-coverage` ok=true, blocking=[], over the three slice 2 pool
  files (confirm-not-discover achieved); `run-quality.sh --read-only`
  73 passed / 0 failed.
- Live/remote proof consumed: #342/#343/#344 `verify-closeout
  --expect-state CLOSED` status=verified; quality-core push runs green on
  3310b28b (27254637832) and post-merge 39ff5432 (27258478736); PR-mirror
  job 80496728903 (run 27258023056) EXECUTED on PR 345 with conclusion
  success in 9m51s, gate payload ok=true with
  changed_pool_files=[scripts/slice_closeout_advisories.py]; installed
  plugin 0.37.0 == released tag v0.37.0 (live local probe).

Residual risks and non-claims:

- The PR-mirror's blocking arm classified an EMPTY changed-mutable-line
  set (docstring-only pool change); blocking-on-real-uncovered-lines
  remains proven by unit tests and the scheduled mutation suite, not by
  PR 345.
- Slice 1/2 work exists only on LOCAL main (rebased onto 39ff5432); it
  reaches remote CI on the next operator push — the next operator lane,
  not this goal's.
- The scheduled `mutation-tests.yml` run over merged main 39ff5432 had
  not fired by closeout: the 07:17Z cron slot was actively awaited until
  07:48Z (31 min past the slot; GitHub cron delay/skip) and the next slot
  (10:17Z) falls outside the timebox. Latest green: 27253892006 over
  pre-push 58cc749a, 04:47Z. Named deferred proof per the
  activation-timing decision; verify with the next `gh run list
  --workflow mutation-tests.yml` showing a green schedule run on
  39ff5432 or later.
- The settings scan covers the three default host settings paths only;
  a hand-written interpreter-less entry with a known basename reports
  loudly even when live (inherited liveness posture); the scan reports,
  never removes.
- Per-goal token/time metrics are NOT claimed: the host probe's
  project-dir aggregate is unattributable to this goal (recorded honestly
  in the host log probe artifact; capability gap filed as issue 346).

## User Verification Instructions

- `gh issue view 342 343 344 --repo corca-ai/charness` — each CLOSED,
  closed-by the carrier commits (76909cc8 / 7f835610 / cd2618d1).
- `gh pr view 345 --repo corca-ai/charness` — MERGED as 39ff5432; its
  checks page shows `Changed-line mutation coverage (PR mirror)` EXECUTED
  with conclusion success (run 27258023056, job 80496728903).
- Deleted-checkout scan demo: on a scratch HOME, write a claude
  `settings.json` hook entry whose command names
  `usage_episode_session_start.py` at a nonexistent absolute path, then
  `python3 scripts/reconcile_usage_episodes_host_hooks.py --repo-root .
  --home <scratch> --mode status` — the `settings_scan` section flags it
  and the command exits 1; an empty scratch HOME reports silence.
- `docs/conventions/authoring-preflight.md` multi-checkout paragraph no
  longer names the deleted-checkout blind spot as open.
- `pytest tests/quality_gates/test_slice_closeout_new_pool_advisory.py
  tests/test_host_hook_registry.py -q` — green (F4 e2e + scan tests).

## Auto-Retro

Retro dispositions: issue #346 (recurs: second consecutive Claude-host goal closeout hand-wrote the same attribution caveat — see the prior goal's probe artifact) — per-goal metric scoping for the host-log probe on Claude hosts (probe aggregates the project dir; metric-window recorder is Codex-only); accepted-risk: shaping-time reading of CI workflow + gate source for CI-behavior-dependent slices stays a judgment habit — the activation fresh-eye plan critique is the standing gate that caught it at zero rework cost this run, and a hard shaping rule would duplicate that gate.
Structural follow-up: issue #346 (recurs: the prior goal's host-log probe artifact carries the identical thread-wide attribution caveat; the fix is a capability change in the retro/achieve helper scripts, not a repo-local guard)
