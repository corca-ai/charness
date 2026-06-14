# Achieve Goal: Workflow + host-state hardening bundle: agent-browser orphan scoping, close-keyword guard (#363), decaying-habit advisory (#364), through push + release

Status: complete
Created: 2026-06-14
Activation: `/goal @charness-artifacts/goals/2026-06-14-workflow-host-state-hardening-bundle.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: COMPLETE — all four slices landed; release 0.48.0 published and
  verified; #363/#364/#365 CLOSED.
- Current slice intent: goal complete. S1 #365 agent-browser scoping, S2 #363
  close-keyword advisory, S3 #364 decaying-habit advisory (+ module split) all
  shipped in release 0.48.0; the three issues verified CLOSED; off-goal finding
  #366 filed. Retro, host-log probe, and disposition review recorded below.
- Next action: none — goal complete. (Off-goal follow-up #366 tracks the
  author-time-validator-vs-downstream-closeout strictness gap.)
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

Land three additive, **non-blocking** workflow + host-state guards that harden
charness against recurring traps this session exposed, each reusing an existing
surface (no new blocking floor, per Floor-Addition Restraint), then push and cut
a release:

1. **agent-browser orphan scoping (bug-class).** `scripts/agent_browser_runtime_guard.py`
   detects/cleans "orphan" agent-browser daemons **machine-wide and by PPID
   alone**, so `--cleanup-orphans --execute` killed a *concurrent unrelated
   task's* live browser sessions this session (a `parental-interaction-eval`
   job in another checkout — its `agent-browser wait` hung). Scope orphan
   detection + cleanup to **charness-owned / this-checkout** daemons so the guard
   (and the doctor probe / release fresh-checkout gate that calls it) never flags
   or kills a neighbor task's daemon. File the issue, then resolve it.
2. **#363 close-keyword-leakage guard.** A non-blocking pre-commit/pre-push
   advisory flagging a close keyword (`closes/fixes/resolves #N`) in a commit
   whose changed paths are not a plausible fix for `#N` (the trap that
   auto-closed #362 a day before its fix existed).
3. **#364 decaying-habit advisory.** A non-blocking author-time advisory for the
   recurring pre-commit-gate habits whose persisted lessons keep decaying and
   re-violating (proactive plugin-mirror sync; in-process test default for
   import-safe `scripts/*.py`).

Then **push** the bundle and **cut release 0.48.0** (operator-approved this run).

## Non-Goals

- **No new blocking floors.** All three are non-blocking advisories or a scoping
  bug-fix; the existing gates (commit gate, doctor, staged-mirror-drift,
  boundary-bypass-ratchet) stay the enforcement. Per the Floor-Addition Restraint
  checklist — two of these (#363, #364) have a *recorded* recurrence, so an
  advisory (not a blocking gate) is the sanctioned escalation.
- **Not re-implementing existing gates.** The #363/#364 advisories reuse the
  `slice_closeout_advisories` surface and forecast the SAME constraints the real
  gates enforce; the agent-browser fix reuses the existing runtime-guard module,
  it does not fork it.
- **Not a redesign of agent-browser.** Only the orphan-ownership *scoping* is in
  scope — not the browser daemon lifecycle, not the gather/browser-automation
  surface.
- No cross-repo work; no prompt-behavior change requiring live Cautilus.

## Boundaries

- charness-internal only (repo-root `scripts/*.py` + the slice-closeout advisory
  surface + the runtime guard); run the portability classification at closeout
  for any new repo-root script.
- **External side-effect scope (operator pre-authorized this run):** the bundle
  boundary push to `origin/main` AND cutting **release 0.48.0** (version bump +
  `publish_release.py` publish + GitHub release) are approved for THIS goal's
  closeout. Per-slice pushes are NOT assumed — push/release batch at the final
  bundle boundary. The approval is scoped to this goal and does not carry forward.
- This goal **resolves tracked issues #363 and #364, plus a new agent-browser
  issue filed in S1**; the issue-closeout floor applies to all three.
- The agent-browser item is **bug-class** (real-world behavior diverged — the
  guard killed a live concurrent task), so its resolution runs a `debug`-substrate
  causal review before the fix and a resolution critique after, per `issue`.
- agent-browser orphan-cleanup is **destructive to live processes**: any test or
  verification must simulate concurrent daemons (fake PIDs / a temp marker), never
  kill real machine daemons; the guard must default to NOT killing a daemon it
  cannot prove is charness-owned.
- Discuss before activation: resolved. The three consequential signals are
  settled by the operator's explicit choices and the goal design: (1) **push +
  release** were explicitly chosen by the operator ("Build through push +
  release"), so cutting 0.48.0 is the goal's authorized closeout, not a surprise
  side effect; (2) **multi-issue closeout** (#363 + #364 + the new agent-browser
  issue) is the goal's explicit purpose (the operator chose "all"); (3) the
  **bug-class causal review** for the agent-browser fix is the correct default
  for a defect that caused real harm. No floor removal, no irreversible side
  effect beyond the approved release.

## User Acceptance

- **agent-browser:** a simulated agent-browser daemon whose cwd/owner is a
  DIFFERENT checkout is NOT reported as an orphan by
  `agent_browser_runtime_guard.py` and is NOT targeted by `--cleanup-orphans`;
  a genuine charness-owned orphan still is reported and cleaned. A run of the
  charness release fresh-checkout probe does not fail merely because an unrelated
  task's agent-browser daemon is alive on the machine.
- **#363:** a commit whose body says `Resolves #999` but whose changed paths are
  not a plausible fix for #999 (e.g. an artifact-only goal-shaping commit) emits
  the advisory; a real fix commit for #999 stays silent. The commit still
  succeeds either way (non-blocking).
- **#364:** staging a `scripts/*.py` change without the plugin-mirror sync, or a
  test that subprocesses an import-safe `scripts/*.py`, emits the advisory; a
  clean change stays silent. Non-blocking.
- **release:** `charness --version` (and the GitHub release page) shows 0.48.0
  after the run; #363/#364/the new issue show CLOSED.

## Agent Verification Plan

### Low-Cost Checks

- Unit tests per guard: agent-browser ownership scoping (foreign-cwd daemon not
  flagged; charness-owned orphan flagged) with simulated PIDs/markers — never
  real kills; #363 advisory fires on a leak fixture and is silent on a real fix;
  #364 advisory fires on the mirror-skew / subprocess-test fixtures and is silent
  when clean.
- `ruff` / `py_compile` / `check_python_lengths` / `validate_attention_state_visibility`
  / `check_doc_links` / `check-markdown` green for each slice; plugin mirror
  synced for any `scripts/*.py` change.

### High-Confidence Checks

- The agent-browser fix verified against a real `--doctor-check` run with a
  simulated foreign daemon present → guard reports healthy / does not target it.
- `run_slice_closeout.py` bundle boundary green; the boundary-bypass ratchet and
  staged-mirror-drift gates pass.
- Per-issue resolution critique (fresh-eye) for each of the three; the
  agent-browser bug also gets a causal review before the fix.

### External Or Live Proof

- **Release 0.48.0** (operator-approved): `publish_release.py --part minor
  --execute` — push, tag `v0.48.0`, GitHub release verified, install refresh.
  `issue_tool.py validate-closeout-draft` / `verify-closeout --expect-state
  CLOSED` for #363/#364/the new issue. Release critique (fresh-eye) before
  publish. No live Cautilus (no prompt-behavior change).

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | agent-browser orphan scoping (bug-class): file the issue, run a causal review, then scope orphan detection + cleanup to charness-owned/this-checkout daemons so a neighbor task's live daemon is never flagged/killed | highest-leverage + reduces active harm (it already killed a concurrent task); also unblocks the release fresh-checkout probe under concurrent browser activity | foreign-daemon-not-flagged + charness-orphan-flagged unit tests (simulated PIDs, no real kills); causal review + resolution critique; `verify-closeout` for the new issue | planned |
| S2 | #363 close-keyword-leakage guard: a non-blocking pre-commit/pre-push advisory flagging a close keyword in a commit whose changed paths are not a plausible fix for #N | recorded recurrence (premature-closed #362); advisory-first per Floor-Addition Restraint | leak-fixture advisory + real-fix silence unit tests; non-blocking guard test; `verify-closeout` #363 | planned |
| S3 | #364 decaying-habit advisory: a non-blocking author-time advisory for proactive mirror-sync + in-process-test default | recorded recurrence (re-violated this session); advisory-first | mirror-skew/subprocess-test fixtures fire; clean silence; non-blocking guard test; `verify-closeout` #364 | planned |
| S4 | Bundle proof + push + release 0.48.0 | the operator-approved external lane; batch push/release at the bundle boundary | `run_slice_closeout` bundle green; release critique; `publish_release.py --execute`; GitHub release v0.48.0 verified; install refresh | planned |

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

Recorded:

- Routing: find-skills (run once at session start) recommended the achieve goal lifecycle, with impl + debug + quality + issue + release as the routed phase skills.
- Routing detail: S1 routed to `issue` (file #365 + bug-class resolution),
  `debug` (causal-review substrate
  `charness-artifacts/debug/2026-06-14-issue-365-agent-browser-orphan-ownership.md`),
  `impl` (the guard fix), and `critique` (causal + resolution critique, both
  fresh-eye subagents); S2/S3 `impl` on the advisory surface; quality via the
  closeout/run-quality gates; S4 `release`.
- Gather: n/a — no external URL/Slack/Notion/Docs/Drive source; the agent-browser
  harm evidence is this session's transcript, preserved in issue #365.
- Release: published 0.48.0 via `publish_release.py --part minor --execute`;
  release verified (https://github.com/corca-ai/charness/releases/tag/v0.48.0),
  `public_release_verification: verified`, `fresh_checkout_probe_status: passed`,
  `install_refresh` 0.47.0->0.48.0 (`== repo`); proof
  `charness-artifacts/release/latest.md` +
  `charness-artifacts/retro/2026-06-14-v0-48-0-release-auto-retro.md`.
- Issue closeout: #365 (S1, bug), #363 (S2, feature), #364 (S3, feature);
  carrier = direct-commit close keywords with full closeout ledgers in the slice
  commits (c71cd4de / b757e40c / 8a43651e); `validate-closeout-draft`
  draft_verified pre-push; `verify-closeout --expect-state CLOSED` = verified for
  all three post-push. (#366 filed as an off-goal finding; NOT closed by this goal.)

## Slice Log

### Slice 1: S1 — agent-browser orphan scoping (bug-class, #365)

- Objective: Scope agent_browser_runtime_guard orphan/residue detection + cleanup to this-checkout-owned daemons so a concurrent neighbor checkout's live daemon is never flagged or killed; file + resolve the new issue.
- Why this approach: cwd (/proc/<pid>/cwd resolved under repo_root) is the checkout-specific ownership signal; daemon is detached-by-design (ppid==1) and does NOT chdir (empirically confirmed), so cwd is reliable. Fail-closed: unknown cwd never killed/flagged. Reused the existing guard module (no fork); scoped all three selectors uniformly.
- Commits: S1 commit (this slice): scope agent-browser orphan detection to this checkout (#365)
- What changed: scripts/agent_browser_runtime_guard.py (+ plugin mirror); tests/test_agent_browser_runtime_guard.py (pure ownership tests + real-process CLI neighbor-safety tests); charness-artifacts/debug/2026-06-14-issue-365-agent-browser-orphan-ownership.md (causal-review substrate); preserved prior debug latest pointer.
- Alternatives rejected: (a) remove the orphan check — loses real cleanup value; (b) machine-wide allowlist file — brittle/host-specific; (c) AGENT_BROWSER_SESSION env marker — charness-wide not checkout-specific AND would need a launch-path change (out of scope).
- Targeted verification: ruff + py_compile + check_python_lengths (790 files) green; 18/18 guard tests pass; REAL end-to-end: a live agent-browser daemon in a foreign checkout reported healthy (rc=0) by --assert-no-orphans and not a --cleanup-orphans target, neighbor stayed alive.
- Test duplication pressure: New tests reuse existing fake-ps helpers; pure ownership tests (simulated cwd) are distinct from the real-process CLI tests (prove /proc wiring + neighbor safety) — no duplicate coverage; existing single-tenant tests converted to owned-marker form rather than duplicated.
- Critique: Causal review (fresh-eye, parent-delegated): all three lenses PASS close-ledger; flagged zombie-cwd / cwd-heuristic / TOCTOU. Resolution critique (fresh-eye): committed-ready, no Act-Before-Ship; one Bundle-Anyway (path-prefix-collision assertion) folded in.
- Off-goal findings: none
- Lessons carried forward: ppid==1 is detached-by-design for agent-browser daemons (not 'abandoned'); machine-global signals need per-task ownership scoping; proactive plugin-mirror sync done before the commit gate (#364 habit).
- Metrics:

### Slice 2: S2 — #363 close-keyword-leakage advisory

- Objective: Non-blocking pre-push advisory flagging a GitHub close keyword (close/fix/resolve #N) in an unpushed commit whose changed paths are not a plausible fix for #N (artifact-only goal-shaping commit) — the trap that auto-closed #362 before its fix existed.
- Why this approach: Reused the slice_closeout_advisories surface (mirrors advise_floor_addition_restraint / advise_over_slicing) and the SHARED is_artifact_only_commit signal (extracted so over-slice + close-keyword cannot drift). Scans origin/main..HEAD (the pre-push leak window); degrades silently off a git repo / unresolved base. Non-blocking stderr only.
- Commits: S2 commit (this slice): #363 close-keyword-leakage advisory
- What changed: scripts/slice_closeout_advisories.py (parse_close_keyword_refs + _unpushed_commits + advise_close_keyword_leakage + extracted is_artifact_only_commit) + mirror; scripts/run_slice_closeout.py wiring + mirror; tests/quality_gates/test_slice_closeout_close_keyword_advisory.py; debug-artifact risk-interrupt enum fix (operator-visible-recovery / monitor).
- Alternatives rejected: (a) blocking gate — rejected per Floor-Addition Restraint (one recorded recurrence -> advisory); (b) fetch the issue via gh to check changed-paths-vs-issue — rejected (network dependency in a closeout advisory, heavier); (c) hand-rolled artifact-only check — rejected (drift); reused the shared signal instead.
- Targeted verification: ruff + py_compile green; 14 S2 tests (pure keyword parsing incl. URL/owner-repo/dedup/bare-ref/in-word-negatives; artifact-only signal; monkeypatched fire/silent/non-blocking; real-git-repo positive + real-fix silence + unresolved-base degrade); 149-test affected sweep green incl. overslice (shared-helper refactor) + broad_gate + surface_obligations.
- Test duplication pressure: is_artifact_only_commit extracted and reused (no duplicate artifact-only logic); pure parsing tests distinct from real-git-repo plumbing tests; non-blocking + not-wired-into-commit-gate assertions guard the Floor-Addition Restraint invariant.
- Critique: Self-review: regex anchored with \b + [\s:]+ separator so in-word (prefix/affixes) and no-separator (fix#1) cases never match; bare #N (safe shaping form) explicitly silent; reuses shared signal (no drift). Slice-level critique deferred to bundle resolution critique at S4.
- Off-goal findings: Fixed an incidental block: my own S1 debug artifact used Risk Class 'host-state' / prose Generalization Pressure, invalid for the stricter risk_interrupt parser, which blocked run_slice_closeout repo-wide; reclassified to operator-visible-recovery / monitor (non-forced). Not a new issue — a self-inflicted artifact enum error, fixed in this slice.
- Lessons carried forward: The risk_interrupt parser enums (Risk Class, Generalization Pressure) are stricter than validate_debug_artifact; debug artifacts must use the risk_interrupt taxonomy or they block run_slice_closeout repo-wide.
- Metrics:

### Slice 3: S3 — #364 decaying-habit advisory

- Objective: Non-blocking author-time advisory for the two recurring pre-commit-gate habits: (1) a changed scripts/*.py with a stale plugin mirror; (2) a changed test that subprocesses an import-safe scripts/*.py when an in-process main() exists. Fire BEFORE the blocking gates (staged-mirror-drift, boundary-bypass ratchet).
- Why this approach: Reused the REAL signals (no drift): habit 1 maps the mirror path via packaging_lib.checked_in_plugin_root and compares working-tree bytes; habit 2 reuses inventory_boundary_bypass_lib.analyze_test_file + boundary_bypass_ratchet_lib exemptions. Both degrade silently when the manifest/probe can't load.
- Commits: S3 commit (this slice): #364 decaying-habit advisory + module split
- What changed: scripts/slice_closeout_commit_advisories.py (NEW: #363 + #364 advisories moved here to respect the file-length gate) + mirror; scripts/slice_closeout_advisories.py trimmed (kept shared is_artifact_only_commit) + mirror; scripts/run_slice_closeout.py rewired imports + mirror; tests/quality_gates/test_slice_closeout_decaying_habit_advisory.py; S2 test imports repointed to the new module; carried the S1 rca-ledger entry.
- Alternatives rejected: (a) blocking gate — rejected (Floor-Addition Restraint; recorded recurrence -> advisory); (b) hand-rolled mirror-path / boundary detection — rejected (drift); reused packaging + boundary-bypass libs; (c) keep both advisories in slice_closeout_advisories — rejected (530 > 480 code-line gate), split into a cohesive slice_closeout_commit_advisories sibling.
- Targeted verification: ruff + py_compile green; check_python_lengths exit 0 (both modules under 480 after split); 13 S3 tests (mirror drift match/stale/missing/non-scripts/degrade; boundary-bypass fire/in-process-silent/exempted/non-test; orchestration fire/silent/non-blocking/not-wired); 162-test affected sweep green incl. run_slice_closeout integration (subprocess, proves new-module wiring) + plan-only smoke (status=planned).
- Test duplication pressure: Habit-1 tests fake only the packaging import (real temp-file byte compare); habit-2 tests use the real boundary-bypass libs against a seeded repo (no mock of the detection); orchestration tests monkeypatch the two private helpers — distinct layers, no duplicate coverage.
- Critique: Self-review: both advisories reuse real gate signals (no drift); both asserted non-blocking + not-wired-into-staged_commit_gate_plan; module split keeps each file cohesive + under length gate. Slice-level critique deferred to the bundle resolution critique at S4.
- Off-goal findings: Module split (slice_closeout_advisories 530>480 length gate) was forced by S3's additions — handled in-slice, not a deferral.
- Lessons carried forward: Portability: all three guards ship via the plugin mirror (plugins/charness/scripts) -> skill-capability, inherited by consuming repos, already routed (not repo-local). Adding ~110 lines to a near-cap module trips the 480 code-line gate; split into a cohesive sibling early.
- Metrics:

### Slice 4: S4 — bundle proof + push + release 0.48.0

- Objective: Prove the bundle at the boundary, push to origin/main, cut release 0.48.0, and close #363/#364/#365 (operator-approved external lane).
- Why this approach: run-quality.sh --read-only is the authoritative push gate (superset of run_slice_closeout incl. broad pytest + boundary-bypass + plugin-export-drift); validated it green before publish. Reworded the slice commits to carry full closeout ledgers so direct-commit verify-closeout passes (the fix commit is the carrier).
- Commits: S4: release-prep (3f70ea56), Release charness 0.48.0 (2a4378c3), Record release verification (3fe1d4ab); slice commits reworded to c71cd4de/b757e40c/8a43651e.
- What changed: .agents/release-adapter.yaml (0.48.0 update_instructions); charness-artifacts/debug/seam-risk-index.json (rebuilt for #365 seam); charness-artifacts/critique/2026-06-14-charness-0-48-0-release.md; packaging + plugin version surfaces -> 0.48.0; charness-artifacts/release/latest.md + auto-retro (publish).
- Alternatives rejected: (a) --close-issue on publish_release — rejected (the release commit would lack per-issue ledgers; the slice commits are the proper carriers); (b) rely on run_slice_closeout alone — used run-quality --read-only as the authoritative push gate instead.
- Targeted verification: run-quality.sh --read-only: 75 passed, 0 failed (broad pytest included) after the seam-index rebuild; publish_release --execute: release v0.48.0 verified (public_release_verification: verified, fresh_checkout_probe_status: passed, install_refresh 0.47.0->0.48.0 == repo); verify-closeout --expect-state CLOSED verified for #363/#364/#365; charness --version = 0.48.0.
- Test duplication pressure: n/a — S4 is proof + release, no new tests added (the bundle's tests were added in S1-S3).
- Critique: Bundle release + #363/#364 resolution critique (fresh-eye): PUBLISH-WITH-NITS, no blockers (charness-artifacts/critique/2026-06-14-charness-0-48-0-release.md). S1/#365 causal + resolution critiques done in S1.
- Off-goal findings: #366 filed (validate_debug_artifact vs risk_interrupt enum gap; the S2 detour).
- Lessons carried forward: Direct-commit auto-close requires the full closeout ledger in the commit body; author it up front when resolving an issue. The push gate is run-quality.sh --read-only (run it to pre-validate before publish_release).
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- [#363](https://github.com/corca-ai/charness/issues/363) — close-keyword-leakage
  guard (filed this session after #362 was auto-closed prematurely).
- [#364](https://github.com/corca-ai/charness/issues/364) — recurring
  pre-commit-gate author habits decaying despite persisted lessons.
- `charness-artifacts/retro/2026-06-14-general-doc-authoring-preflight.md` — the
  retro whose Sibling Search + disposition review surfaced #363/#364.
- The agent-browser harm evidence is in THIS session's transcript: the
  `parental-interaction-eval` concurrent task whose `agent-browser wait` hung
  after `agent_browser_runtime_guard.py --cleanup-orphans` killed its daemons.
  The new S1 issue will preserve the concrete evidence.
- `scripts/agent_browser_runtime_guard.py` — the runtime guard whose machine-wide
  PPID-based orphan detection is the S1 fix target.
- `scripts/slice_closeout_advisories.py` — the advisory surface S2/S3 extend
  (mirrors `advise_doc_surface_preflight` / `advise_floor_addition_restraint`).

## Interview Decisions

- **Scope (which next-to-do):** operator chose **"all"** — bundle the
  agent-browser orphan scoping + #363 + #364, over (a) one issue only or (b) the
  agent-browser fix alone. Cohesive theme (non-blocking workflow/host-state
  guards), so one goal with three slices, not three goals.
- **Run autonomy:** operator chose **"Build through push + release"**, over
  (a) local-closeout-only or (b) push-without-release. So 0.48.0 is cut at the
  bundle boundary; the push/release approval is recorded in Boundaries.
- **agent-browser fix shape:** scope orphan *ownership* (charness-owned vs
  foreign), over (a) removing the orphan check (loses the real cleanup value) or
  (b) a machine-wide allowlist file (brittle, host-specific). Ownership-scoping
  keeps the cleanup useful while making it neighbor-safe.
- **#363/#364 shape:** non-blocking advisories on the existing
  `slice_closeout_advisories` surface, over new blocking floors (Floor-Addition
  Restraint: recorded recurrence warrants an advisory, not teeth).

## Plan Critique Findings

Pre-activation premortem (additive, charness-internal, but with a destructive
host-state surface). Worth stressing when it runs:

- **(a) destructive-cleanup safety (S1).** The agent-browser fix touches a
  process-killing path. Tests MUST use simulated PIDs / a temp marker and never
  kill real daemons; the guard must FAIL SAFE (do not kill a daemon it cannot
  prove charness-owned). This is the highest-risk slice — fresh-eye + causal
  review required.
- **(b) ownership signal robustness (S1).** "charness-owned" must be a reliable
  signal (cwd of the launching process, a charness env marker, or the daemon's
  working dir) — walk the string/PID-matching edge cases (a foreign daemon under
  a path that contains "charness"; a charness daemon launched from an odd cwd).
  Decide fail-open vs fail-closed deliberately (here: fail-closed = do not kill).
- **(c) advisories stay non-blocking (S2/S3).** Each must be asserted
  non-blocking by a test (a commit still succeeds), guarding against a future
  hand converting an advisory into a precondition.
- **(d) no-drift (S2/S3).** The #363 "plausible fix" heuristic and the #364
  mirror/subprocess detection must reuse real signals (changed paths vs issue,
  the staged-mirror-drift / boundary-bypass logic), not a hand copy that drifts.
- **(e) release under concurrent browser activity.** S1's fix should make the
  release fresh-checkout probe robust to a neighbor's agent-browser daemon — but
  if a concurrent task is active at release time, confirm the probe passes
  without killing anything (the whole point of S1).

## Off-Goal Findings

- [#366](https://github.com/corca-ai/charness/issues/366) — `validate_debug_artifact`
  accepts `Risk Class` / `Generalization Pressure` values the stricter
  `risk_interrupt_lib` parser rejects, so an off-taxonomy debug Seam Risk passes
  the debug validator then blocks `run_slice_closeout` repo-wide at closeout (the
  S2 detour). Filed, not closed by this goal; routed via `issue`.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-14-workflow-host-state-hardening-bundle.md
Host log probe: charness-artifacts/retro/2026-06-14-workflow-host-state-hardening-bundle-host-log.md
Disposition review: charness-artifacts/critique/2026-06-14-workflow-host-state-hardening-bundle-disposition-review.md

## User Verification Instructions

- Confirm `charness --version` reports `0.48.0` (the installed surface was
  auto-refreshed to `== repo` during publish).
- Confirm the GitHub release page shows `v0.48.0`:
  https://github.com/corca-ai/charness/releases/tag/v0.48.0
- Confirm issues #363, #364, #365 show CLOSED on GitHub (auto-closed by the
  slice-commit keywords; `verify-closeout` reported CLOSED for all three).
- Optional (agent-browser fix): with an agent-browser daemon alive in a
  different checkout, run
  `python3 scripts/agent_browser_runtime_guard.py --repo-root . --assert-no-orphans`
  from this checkout and confirm it reports healthy (rc 0) and does not target
  the neighbor daemon.

## Auto-Retro

Retro dispositions: issue #366 (novel: no prior retro records the validate_debug_artifact-vs-risk_interrupt_lib enum gap) — debug Seam Risk write-time hygiene: an off-taxonomy Risk Class / Generalization Pressure passes the debug validator then blocks run_slice_closeout repo-wide at closeout (covers the seam-risk-index proactive-rebuild miss too).
Retro dispositions: issue #366 (recurs: sibling of the 2026-06-01 release-issue-closeout-miss carrier-ledger lesson, re-surfaced this run as a release-time reword) — author the fix commit with its full closeout ledger up front; same author-time-validator-vs-downstream pattern as #366 (the commit-msg hook under-constrains the ledger validate-closeout-draft requires), noted as a sibling on #366.
Structural follow-up: issue #366 (novel: cross-validator strictness gap — an author-time validator under-constrains a field the downstream closeout parser rejects, surfacing only as a repo-wide block; instances: validate_debug_artifact vs risk_interrupt_lib, and commit-msg hook vs validate-closeout-draft)
