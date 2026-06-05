# Achieve Goal: Issues 302-305: gather / setup / release robustness

Status: draft
Created: 2026-06-05
Activation: `/goal @charness-artifacts/goals/2026-06-05-302-305-gather-setup-release-robustness.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slices 1 (#304), 2 (#303), 3 (#302) complete — fixes +
  direct-commit closeouts staged (`Close #304`, `Close #303`, `Close #302`).
  Next: Slice 4 (#305) release publish-flow resilience.
- Next action: implement Slice 4 (#305) — make `publish_release.py`
  resumable/idempotent across a mid-publish failure (detect existing commit+tag
  → continue push/release/verify, re-validating first); installed-cache-safe
  runtime bootstrap; release-time `update_instructions` version-staleness check.
- Verification cadence: cheap deterministic checks (`run_slice_closeout.py`
  aggregate + targeted pytest) at commit boundaries; full targeted test file +
  bounded fresh-eye critique at slice boundaries; broad pytest at final closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.
- Assumed mode: implementation-continuation — slices execute once the user runs
  `/goal`; this Before-phase only shapes and saves, then stops.

## Goal

Resolve four independent robustness issues across the gather (web-fetch), setup
host-doc, and release publish surfaces so each fails visibly instead of
silently, with regression tests, and stage each tracked issue's close via
`Close #N`. #306 (mutation-gate changed-line signal) is split out into its own
design-decision goal per the user.

Per-issue outcome:

- **#304** — the setup host-doc generator's `COMPACT_SUBAGENT_DELEGATION`
  default and the setup inspector (`inspect_repo.py`) agree on the minimal valid
  `## Subagent Delegation` contract, so an agent copying the documented compact
  default does not immediately get flagged as drift.
- **#303** — `setup`-generated / normalized `AGENTS.md` carries an adapter-first
  subagent reviewer rule (follow the adapter's reviewer tier and concrete spawn
  fields, not inherited host defaults), without weakening existing
  standing-delegation language.
- **#302** — `acquire_public_url.py` attempts `agent-browser close` on every
  in-process path, a missing post-close runtime guard is fail-visible (not a
  silent clean success), exported/installed Charness layouts can reach the
  web-fetch impl + cleanup proof, and the runtime guard does not misclassify
  zombie/reparented residue as clean.
- **#305** — `publish_release.py` is resumable/idempotent across a mid-publish
  failure, runs from the installed plugin cache without `ModuleNotFoundError`,
  and a release-time check flags `update_instructions` that omit the target
  version.

## Non-Goals

- **#306 is out of scope.** The mutation-gate changed-line signal becomes its
  own design-decision goal later (user-chosen split). This goal does not pick
  that fix.
- **The Ceal-owned init/reaper fix (#302) is out of scope.** Charness must only
  avoid *misclassifying* zombie/reparented Chromium residue as clean; reaping
  PID-1 zombies belongs to Ceal's container init and is fixed there.
- **No push, no GitHub release, no out-of-band issue close.** `achieve` stages
  `Close #N` only; the maintainer's push performs the actual close.
- **No new charness version / no `marketplace.json` bump.** #305 hardens the
  publish *helper*; it does not cut a release.
- **No scope creep past each issue's acceptance criteria** — e.g. #303 only
  generates the host rule; it does not redesign the reviewer-tier policy.

## Boundaries

- Four issues, three independent surfaces: gather/web-fetch (#302), setup
  host-doc (#303 + #304, shared file), release publish (#305). Only #303/#304
  share a file and are sequenced **#304 → #303**.
- **#303 reviewer tier is adapter/host-varying (axis: adapter/host).** The
  generated rule must NOT hardcode a global `medium`; it says "follow the
  adapter's reviewer tier" and may name medium only as the Codex-critique
  default *unless the adapter says otherwise*. It must not assert every subagent
  is always medium.
- **#302 browser env varies by host/container (axis: host/environment).** Env
  fixes (`HOME`, `XDG_CACHE_HOME`, `XDG_CONFIG_HOME`, cache/profile locations)
  must be instance/workspace-scoped, not a single hardcoded path.
- **#305 checkout layout varies (axis: runtime).** The bootstrap fix must work
  from both the repo-root copy and the installed plugin-cache copy, proven by
  test, not by assuming one layout.
- Each fix lands with a regression test; no fix is "done" on inspection alone.
- The `Close #N` keyword goes in the fix/closeout commit body on the default
  branch and is preserved through squash/rebase/edited-merge bodies.
- Generated/exported surfaces (the `plugins/` mirror) are synced before
  validators, per `mutate → sync → verify → publish`.

## User Acceptance

What the user can do to verify completion directly:

- **#304** — Generate `AGENTS.md` from the setup default
  (`COMPACT_SUBAGENT_DELEGATION` via `normalize_host_docs.py`) in a fresh repo,
  then run
  `python3 skills/public/setup/scripts/inspect_repo.py --repo-root <repo>` and
  see **no** delegated-review drift finding. A fixture/test pins the agreement.
- **#303** — Inspect setup-generated / normalized `AGENTS.md`: it contains an
  adapter-first subagent reviewer rule; the existing standing-delegation
  language is intact; a fixture/test covers the rule.
- **#302** — Run the new/extended tests around
  `skills/support/web-fetch/scripts/acquire_public_url.py`: they prove close is
  attempted across render success/failure, network-recon success/failure,
  classification failure, and in-process timeout paths; a test proves a missing
  post-close guard is fail-visible (`guard_unavailable`-style, not silent
  clean); an exported-surface test proves `gather_public_url.py` reaches the
  web-fetch impl + cleanup proof from an installed/exported layout; a
  runtime-guard test proves zombie/reparented residue is not reported clean.
- **#305** — Re-run `publish_release.py` after a simulated mid-publish failure:
  it detects the existing release commit+tag and continues to push/release/verify
  (resumable/idempotent); the helper imports and runs from the installed
  plugin-cache path without `ModuleNotFoundError`; a release-time check flags
  `update_instructions` that don't mention the target version.
- **Closeout** — Each of #302–#305 has a fix/closeout commit carrying
  `Close #N`; the issues remain **OPEN** until the maintainer pushes (achieve
  does not push).

## Agent Verification Plan

### Low-Cost Checks

- `run_slice_closeout.py` pre-commit aggregate (ruff, `check_python_lengths`,
  `validate_skills`, `check-markdown`, mirror-drift, `check_doc_links`) on the
  changed surface at each commit boundary.
- Targeted pytest for the touched module only (the setup inspector test, the
  web-fetch acquire test, the release publish test).
- For #303/#304: `inspect_repo.py --repo-root <generated>` returns clean.

### High-Confidence Checks

- Full targeted test file(s) for the changed surface, green, at the slice
  boundary.
- Bounded fresh-eye slice critique (with the slice review packet) for any slice
  that introduces a new validator/inspector rule (#304), a prompt/host-doc
  template change (#303), or release-helper control-flow change (#305).
- Exported/installed-layout test executed at the slice boundary for #302
  (gather reach) and #305 (installed-cache bootstrap).

### External Or Live Proof

- **Not claimed:** no live `agent-browser`/Chromium runtime proof on a real
  exported host (#302) — coverage is test-level only; live reaper behavior stays
  Ceal-owned.
- **Not claimed:** no real `git push` / `gh release create` (#305) — resume /
  idempotency is proven by tests with a simulated/failed push, not a real
  publish.
- **Final closeout:** full broad pytest gate (this run adds/expands tests) —
  classify any duplicate/length/pressure-gate failure as new-slice-local vs
  accumulated-suite debt and name the smallest structural cleanup.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 — #304 setup template↔inspector agreement | Make `COMPACT_SUBAGENT_DELEGATION` + `normalize_host_docs.py` output satisfy `inspect_repo.py`'s delegated-review snippet requirements (or relax the inspector to accept the documented compact form), so the two agree on the minimal valid `## Subagent Delegation` contract | Narrowest, most deterministic; shares the delegation-block region with #303 and must agree before #303 adds a rule | Bug-class: record the falsifiable mismatch (template lacks inspector-required snippets) then fix. Fresh repo → generate `AGENTS.md` from the default → `inspect_repo.py` reports no delegation drift; fixture/test pins it | planned |
| 2 — #303 setup adapter-first reviewer rule | Add an adapter-first subagent reviewer rule to setup-generated/normalized `AGENTS.md` (follow adapter tier + concrete spawn fields; Codex critique default medium unless adapter says otherwise; stop+report if tier unappliable) without weakening standing-delegation language | Same setup host-doc surface as #304; builds on the now-agreed template/inspector shape | Feature-class (no debug step). Generated/normalized `AGENTS.md` contains the rule; standing-delegation language intact; `inspect_repo.py` stays clean; fixture/test covers the rule | planned |
| 3 — #302 gather browser close + clean-runtime proof | Ensure `acquire_public_url.py` attempts session close on all in-process paths; missing post-close guard is fail-visible (`guard_unavailable`); exported-surface gather reaches the impl + proof; runtime guard does not misclassify zombie/reparented residue; instance-scoped browser env smoke | Independent surface; ceal-prod runtime-pressure evidence; highest blast radius if a close failure reads as clean | Bug-class: record the falsifiable gap (guard skipped on non-repo-root hosts → silent clean) then fix. Tests across success/failure close paths; missing-guard fail-visible test; exported-layout reach test; zombie-residue not-clean test; env smoke | planned |
| 4 — #305 release publish-flow resilience | Make `publish_release.py` resumable/idempotent across a mid-publish failure (detect existing commit+tag → continue push/release/verify); installed-cache-safe runtime bootstrap; release-time `update_instructions` version-staleness check | Independent surface; v0.21.0 publish surfaced 3 concrete gaps; no new release needed to prove them | Bug-class: record the falsifiable partial-state repro then fix. Resume/idempotency test (simulated failed push); installed-cache import test; `update_instructions` staleness check + test | planned |

Debug coordination: #304, #302, and #305 are bug-class — each slice records a
falsifiable hypothesis / reproduction *before* the fix. Each issue already
documents the mechanism, so `debug` here is confirm-the-hypothesis, not
open-ended root-cause. #303 is feature-class (add a rule): no `debug` step.

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

### Planned At Shaping (to confirm during the run)

- Issue closeout (planned): #302, #303, #304, #305 — carrier `direct-commit`
  with `Close #N` in each fix/closeout commit body on the default branch; issues
  stay OPEN at achieve closeout (achieve never pushes). Bind `Critique #N:` per
  issue at closeout via the `issue` verifier; confirm with
  `issue_tool.py validate-closeout-draft` during the run.
- Note #305 touches the release helper but performs **no** release; the
  `Release:` floor is expected to resolve as a helper-hardening reference or an
  `n/a — <reason>` opt-out, not a version bump.

### Discuss Before Activation

Discuss before activation: resolved — the user approved (1) the bundled
**#302–#305** scope with **#306 split out** into its own design-decision goal;
(2) **staging `Close #N`** on each fix commit (issues stay OPEN until the
maintainer pushes); and (3) **no timebox** (run to macro-outcome). Proof-level
non-claims are accepted: no live `agent-browser`/Chromium runtime proof on a
real exported host (#302) and no real `git push` / `gh release` (#305); the
Ceal-owned zombie/reparented-process reaper is out of scope; and the #303
reviewer-tier rule stays adapter-first, never a global hardcoded `medium`. No
unresolved consequential item remains for `/goal` activation.

## Slice Log

### Slice 1: Slice 1 — #304 setup template↔inspector agreement

- Objective: Make COMPACT_SUBAGENT_DELEGATION and the setup inspector agree on the minimal valid ## Subagent Delegation contract so a copy of the documented compact default is not flagged as fresh_eye_delegation_rule_drift.
- Why this approach: RN1: relax the inspector (whitespace-normalize contract-snippet matching) rather than de-wrap the template — also fixes consumer repos that copied the documented wrapped block.
- Commits:
- What changed: scripts/setup_agent_docs_fresh_eye_lib.py (+mirror): added _normalize_whitespace() and routed _missing_snippets, the same-agent-forbidden check, fresh_eye_policy_gaps, and detect_fresh_eye_normalization haystacks through it. tests/quality_gates/test_setup_inspect_policy.py: new regression test pinning agreement against the actual render_agents_template output (line-wrapped).
- Alternatives rejected: De-wrap the COMPACT_SUBAGENT_DELEGATION template (only fixes future generations, not consumer copies) — rejected per RN1.
- Targeted verification: Confirmed pre-fix repro (compact_contract_present=False, drift finding present, end-to-end via inspect_repo.py). Post-fix: compact_contract_present=True, no drift, same-agent-allowed still rejected. test_setup_inspect_policy.py 32 passed; related fresh-eye suites 75 passed; run_slice_closeout.py deterministic aggregate completed. Bounded fresh-eye slice critique: no blockers, all 4 invariants confirmed.
- Test duplication pressure: 1 new test (test_setup_inspect_accepts_generated_compact_subagent_delegation_block). Distinct from the sibling single-line accept test: this one renders the actual wrapped generator output and asserts the phrases are non-contiguous in raw text, so it exercises the normalization path the sibling never did. No duplicate-coverage pressure.
- Critique: charness-artifacts/critique/2026-06-05-issue-304-template-inspector-agreement.md (fresh-eye, no blockers).
- Off-goal findings: none
- Lessons carried forward: Contract-snippet detection over markdown prose must be whitespace-insensitive; line-wrapping to satisfy length gates otherwise creates false drift against the very default the repo ships.
- Metrics:

### Slice 2: Slice 2 — #303 setup adapter-first reviewer rule

- Objective: Add an adapter-first subagent reviewer rule to setup-generated/normalized AGENTS.md (follow the adapter's tier + concrete spawn fields; Codex critique default medium unless adapter says otherwise; stop+report if unappliable) without weakening standing-delegation language.
- Why this approach: Feature-class: add the rule the #303 issue specifies, framed adapter-first per the canonical reviewer-tier policy (tier-named, concrete values adapter-owned).
- Commits:
- What changed: scripts/setup_host_docs_lib.py (+mirror): added a second adapter-first reviewer bullet to COMPACT_SUBAGENT_DELEGATION. tests/quality_gates/test_setup_inspect_policy.py: test_generated_agents_carries_adapter_first_reviewer_rule.
- Alternatives rejected: Hardcode a global medium tier — rejected (axis adapter/host; would contradict the multi-host reviewer-tier policy). Make the rule host-plural and drop the Codex example — rejected: the #303 issue and goal boundary explicitly want medium named only as the Codex-critique default.
- Targeted verification: Generated AGENTS.md carries the rule; standing-delegation language intact; inspector clean (compact_contract_present True, weakening_caveats []). 50 targeted tests passed; run_slice_closeout.py deterministic aggregate completed. Bounded fresh-eye slice critique: no blockers, all 4 acceptance criteria YES; test confirmed to fail on removed-rule and global-medium regressions.
- Test duplication pressure: 1 new test. Distinct from the #304 generated-template test (which asserts inspector agreement on the wrap); this one asserts the adapter-first rule content + conditional-medium framing. No duplicate-coverage pressure.
- Critique: charness-artifacts/critique/2026-06-05-issue-303-adapter-first-reviewer-rule.md (fresh-eye, no blockers).
- Off-goal findings: none
- Lessons carried forward: Host instruction files (generated AGENTS.md) may name a concrete tier value as a per-adapter default, unlike portable skill prose; keep it adapter-first and explicitly disclaim global application.
- Metrics:

### Slice 3: Slice 3 — #302 gather browser close + clean-runtime proof

- Objective: Guarantee agent-browser close on every in-process path; make a missing post-close guard fail-visible (guard_unavailable); make gather reach the web-fetch impl + cleanup proof from an exported layout; stop the runtime guard misclassifying reparented/zombie residue as clean.
- Why this approach: Bug-class, four confirmed gaps. try/finally for close; ancestor-walk guard resolution for the bundled guard; reparented/zombie residue folded into the runtime health check; markers scoped to agent-browser + headless Chromium to avoid desktop-Chrome/dockerd false positives.
- Commits:
- What changed: NEW skills/support/web-fetch/scripts/agent_browser_session.py (session I/O + resolve_runtime_guard + assert_runtime_clean). acquire_public_url.py: _browser_stage try/finally close+proof. scripts/agent_browser_runtime_guard.py: reparented_residue + zombie_residue + runtime_residue_total in health. Mirrors synced. Tests: test_web_fetch_cleanup.py (+4), test_agent_browser_runtime_guard.py (+4).
- Alternatives rejected: Hardcode a single relative guard offset (fails one of repo-root/export). De-wrap nothing. Bare chrome/chromium markers (rejected: false-positives desktop Chrome at PID 1 on the unconditional closeout gate; tightened to require headless/automation context). Reaping reparented/zombie residue (rejected: Ceal-owned Non-Goal; detect-not-reap).
- Targeted verification: 63 tests green (web-fetch cleanup + runtime guard + support + content + gws). Pre-fix gaps confirmed via git show HEAD. guard_unavailable fail-visible; exported reach proven by failing-bundled-guard test; reparented/zombie not clean; desktop-Chrome + dockerd not flagged; dev host residue 0; deterministic aggregate completed. Bounded fresh-eye critique: no blockers, all 4 gaps YES; folded its chrome-marker false-positive finding in-slice.
- Test duplication pressure: 8 new tests across 2 files. Distinct coverage: close-attempted (success/failure), guard_unavailable fail-visible, exported reach, reparented residue, zombie residue, desktop-Chrome-not-flagged, assert-no-orphans unhealthy. No duplicate-coverage pressure; each pins a distinct gap.
- Critique: charness-artifacts/critique/2026-06-05-issue-302-gather-browser-close-and-clean-runtime.md (fresh-eye, no blockers; chrome-marker finding folded).
- Off-goal findings: none — the reviewer's deeper note (run_slice_closeout runs --assert-no-orphans unconditionally) is mitigated by the tightened markers; the residual (cleanup cannot reap reparented residue) is the intended fail-visible Ceal-owned boundary, not a defect.
- Lessons carried forward: Browser session lifecycle must close in finally; missing proof must be fail-visible, never None; runtime residue detection must be specific (agent-browser + headless) to avoid false-positiving an unconditional, waiver-stripped closeout gate.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- GitHub issues **#302, #303, #304, #305** (this goal) and **#306** (split out
  — separate design-decision goal, see Non-Goals).
- `docs/handoff.md` — prior portable-skill goal complete; open follow-ups #295,
  #296, plus #184/#293/#294 outside this goal.
- `charness-artifacts/retro/recent-lessons.md` — recent repeat traps to honor
  before changing contracts/exports/validation.
- #302 surface: `skills/support/web-fetch/scripts/acquire_public_url.py`,
  `scripts/agent_browser_runtime_guard.py`,
  `skills/public/gather/scripts/gather_public_url.py`.
- #303 / #304 surface: `scripts/setup_host_docs_lib.py`
  (`COMPACT_SUBAGENT_DELEGATION`), `skills/public/setup/scripts/inspect_repo.py`,
  `skills/public/setup/scripts/normalize_host_docs.py`.
- #305 surface: `skills/public/release/scripts/publish_release.py`; related
  **#194** (usage-episodes gate flake that interacts with the #305 resume path).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Scope / chunking** (family: all-5-one-goal | exclude-#306 | setup-pair-only).
  Chosen: **exclude #306** — this goal covers #302–#305; #306 is a separate
  design-decision goal. Rejected: all-5 risked rushing #306's repo-wide
  mutation-gate policy inside a robustness bundle; setup-pair-only deferred too
  much safe, independent work. (axis: single-point — a per-session scoping
  decision, not a system axis.)
- **Issue closeout** (family: stage-`Close #N` | land-work-leave-open). Chosen:
  **stage `Close #N` per fix**. Rejected: leave-open loses the auto-close link
  and risks issues that are resolved-in-code yet still OPEN after push. (axis:
  adapter/host — the closeout carrier is adapter-owned; `direct-commit` here, a
  publish-capable adapter could differ.)
- **Timebox** (family: no-timebox | bounded-run). Chosen: **no timebox** (run to
  macro-outcome). Rejected: bounded-run is unnecessary — no fixed budget was
  given and the work is well-scoped. (axis: single-point — no user budget.)

Anti-anchoring on inherited issue-framing values:

- #303 reviewer tier `medium` → **axis: adapter/host** — must not become a global
  default; the rule stays adapter-first.
- #302 env `HOME` / `XDG_*` paths → **axis: host/environment** — fixes are
  instance/workspace-scoped, never one hardcoded path.
- #305 checkout layout → **axis: runtime** — repo-root vs installed plugin cache;
  both must work.
- #304 one template + one inspector → **single-point** — there is one generator
  and one inspector and they must agree.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Blockers folded:

- **B1 — #304 before #303 ordering.** Adding the new adapter-first rule (#303)
  before the template/inspector agree (#304) risks the new rule itself failing
  the inspector. Folded into the slice order (#304 first).
- **B2 — #302 over-claim risk.** Charness cannot reap Ceal-owned PID-1 zombies.
  Folded into Non-Goals + the External/Live non-claim: the slice only avoids
  *misclassifying* zombie residue as clean.
- **B3 — #305 idempotency hazard.** A buggy resume touching commit/tag/push could
  double-publish. Folded into Boundaries (resume detects existing commit+tag and
  continues only push/release/verify) and verification (test with a simulated
  failed push; no real push).
- **B4 — #303 global-tier anchoring.** Hardcoding `medium` globally would
  contradict the multi-host reviewer-tier policy. Folded into Boundaries
  (adapter-first, axis: host) and the Interview-Decisions anti-anchoring record.
- **B5 — exported-layout test fragility.** #302/#305 installed-layout tests can be
  slow/fragile. Folded into verification: targeted layout tests, not live runs.

Over-worry raised but not folded:

- **OW1 — "all 4 issues will collide."** False: three independent surfaces, only
  #303/#304 share a file and are sequenced. Recorded so a fresh session does not
  re-litigate.
- **OW2 — "#302 needs a live exported-host run to prove clean."** Not for this
  goal: test-level coverage of close-attempt + fail-visible guard is the
  acceptance bar; live runtime is a separate, explicit non-claim.

Reviewer guidance carried into the run (raised by the fresh-eye plan critique,
not folded as blockers):

- **RN1 — #304 fix direction.** Slice 1 leaves open "de-wrap the template" vs
  "relax the inspector to accept the documented compact form". The reviewer
  noted relaxing the inspector is the higher-leverage option: it also fixes any
  consumer repo that copied the documented compact block, whereas de-wrapping
  only fixes future generations. Decide with the falsifiable test in hand during
  the slice; both satisfy the acceptance criterion.
- **RN2 — #305 resume must re-validate, not blindly push.** A naive "detect
  existing commit+tag → push" resume would skip the pre-commit quality / narrative
  / critique gates that ran before the original commit. The resume path should
  re-validate before continuing push/release/verify; B3's simulated-failed-push
  test bounds this for the goal, but the impl slice must not push a stale local
  commit unchecked.

Reviewer provenance: self-critique at the Before-phase (shaping), plus one
**bounded fresh-eye plan critique** (general-purpose subagent, read-only,
shared parent worktree) that verified all four issue mechanisms against live
code and returned **`activate-ready` — zero blockers**. It confirmed: #304's
root cause is `fresh_eye_compact_contract_present()` requiring contiguous
substrings the template line-wraps (`setup_agent_docs_fresh_eye_lib.py:57-61`);
the #304→#303 ordering is correct because that one helper gates both the #304
drift path and the #303 policy-gap path; #302's guard-skip and hardcoded export
path are real and the guard only flags `ppid==1` (matching the Ceal-reaper
boundary); #305's three gaps are genuinely absent in code; and every axis
classification is honest (no disguised singleton). Further bounded fresh-eye
slice/closeout critiques still run during the run per the risk-boundary cadence
(the #304 inspector slice, the #303 rule slice, and the #305 resume-logic slice
each qualify); final closeout review reads across slices for cross-slice drift
and Auto-Retro disposition.

## Off-Goal Findings

None recorded at shaping. #306 is **not** an off-goal finding — it is a
deliberately split-out goal (see Non-Goals).

## Final Verification

Filled at the After-phase closeout: final self-verification against each issue's
acceptance criteria, broad pytest gate result (with new-slice-local vs
accumulated-suite-debt classification if it fails), the `Close #N` staging
ledger per issue, residual risks, and the explicit live/release non-claims.

## User Verification Instructions

Filled at the After-phase closeout: the concrete commands the user runs to
confirm each issue's acceptance criteria (see `## User Acceptance` for the
planned shape), plus which issues are staged-to-close-on-push.

## Auto-Retro

Filled at the After-phase closeout: `retro` skill findings inline (Waste /
Critical Decisions / Next Improvements), a per-improvement disposition
(`applied: <what>` or `issue #N`) or the falsifiable
`Retro dispositions: none — <reason>` line, the bound `Disposition review:`
artifact, and the `Retro:` / `Host log probe:` evidence lines.
