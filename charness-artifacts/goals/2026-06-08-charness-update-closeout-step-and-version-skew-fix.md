# Achieve Goal: Add the charness-update release-closeout step + fix the scaffold/repo-validator version-skew + goal-activation preflight surface, proven end-to-end by a real push + release + on-machine update (with #335 closing alongside)

Status: complete
Created: 2026-06-08
Activation: `/goal @charness-artifacts/goals/2026-06-08-charness-update-closeout-step-and-version-skew-fix.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: COMPLETE. All 4 slices done; v0.29.0 shipped + pushed + on-machine `charness update` verified (installed == repo).
- Next action: none — goal complete. Carrier-pending external proof: #335 auto-closes on the next green scheduled mutation run after this push. Done-early candidate for a future session: the deferred installed-vs-repo drift detector.
- Timebox: 4h
- Activation time: 2026-06-08T05:12:00Z
- Closeout reserve: 45m
- Done-early policy: continue_next_improvement (re-point to the next release/tooling
  hardening — e.g. the deferred installed-vs-repo drift detector, or the next
  scaffold/host-surface skew — not an unrelated slice).
- Verification cadence: cheap deterministic checks at commit boundaries; the
  touched scripts' tests + fresh-eye critique at slice boundaries; the broad +
  release gates, then the REAL push/release/on-machine update + end-to-end verify
  at the bundle/closeout boundary.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Bundle the three next-session proposals into one shipped change, then PROVE it
works end-to-end with a real release rather than asserting it:

1. **`charness update` as a standing release-closeout step.** Make updating the
   installed charness on this dev machine a required step of release closeout, so
   the installed surface stays `== repo`. This is the operator-requested fix for
   the **version-skew class** this seam exposed (the scaffold-cited *installed*
   `validate_debug_artifact.py` was looser than the repo's own, so a
   scaffold-blessed artifact passed locally but failed the broad gate). Mechanism:
   **closeout step only** (release contract/docs) — NO automated drift detector
   this goal.
2. **Scaffold cites the repo validator, not the installed plugin's.** The deeper
   root: `debug`/`critique` (and sibling) scaffolds emit the *installed* validator
   command; prefer the repo-local `scripts/` validator when present so the cited
   check `==` the gate. This kills the skew even between updates.
3. **`goal-activation-preflight-surface`.** Surface the goal `Activation:` preamble
   line in `check_artifact_surface_preflight.py` (the carried-over deferred
   follow-up; needs preamble extraction, not the `## Heading` template-section
   source).

Then **cut a real release, push `origin/main`, run `charness update` on this
machine, and verify it actually works** — the end-to-end proof the operator asked
for. **#335 rides along**: no separate pre-verification; the post-push scheduled
mutation run is its authoritative verdict and the workflow marker auto-closes it.

## Non-Goals

- Do NOT build the automated installed-vs-repo **drift detector** / `--release`
  gate check this goal — the operator chose closeout-step-only; the drift gate is
  an explicit deferred option (done-early candidate), not in scope.
- Do NOT pre-verify #335 separately — it closes with the push/release; the next
  scheduled mutation run verifies and the marker auto-closes it.
- Do NOT expand beyond the three proposals + the release; no unrelated cleanup.
- Do NOT turn the scaffold fix into a content classifier; it is a presence/path
  resolution (repo-local validator exists → cite it).

## Boundaries

- **This goal performs irreversible external actions** (operator-directed): the
  agent will `git push origin main`, cut a real release (version bump + tag via the
  `release` skill), and run `charness update` on THIS dev machine (mutating the
  installed plugin). Approval is phase-scoped to the final release stage and was
  chosen explicitly at shaping ("Agent runs it all" + "Closeout step only").
- **Override of the standing `achieve` no-push default** is intentional and
  scoped to this goal's final stage only; it does not carry forward.
- **Release-surface + prompt-surface + public-skill scope.** Touches the `release`
  contract/docs, the `debug`/`critique` scaffolds (public skills), and
  `check_artifact_surface_preflight.py` → prompt-behavior-proof + public-skill
  dogfood + mirror-sync apply; deterministic gates own closeout.
- **Behavior-preserving for existing gates.** The scaffold + preflight changes are
  additive; no existing validator verdict changes on existing artifacts. Prove
  with the touched scripts' tests + a before/after check.
- **Export-safe + length-safe.** Mirror sync (`plugins/charness/...`) after any
  `scripts/**` or `skills/**` change.
- Discuss before activation: RESOLVED at shaping. (a) **Push + release/tag + on-
  machine `charness update`** are operator-directed (activation question "Agent
  runs it all") — real irreversible actions the agent performs in the final stage,
  recorded as executed proof, not claimed. (b) **Mechanism = closeout-step only**
  (no drift detector) — operator-chosen; the drift gate is a named deferred option.
  (c) **#335 closes alongside** with no pre-verification — operator-directed; the
  scheduled run is the authoritative verdict. No unresolved consequential default
  remains.

## User Acceptance

What the user can do to verify completion directly:

- See `charness update` documented as a required release-closeout step in the
  `release` contract/docs, and see it actually RUN in this goal's closeout.
- Author a `debug`/`critique` artifact and confirm the scaffold now cites the
  repo-local `scripts/` validator (matching the broad gate), not the installed one.
- Author into a goal `Activation:` surface and see its required shape surfaced at
  author time via the preflight.
- Confirm a real release was cut (version bumped + tag), `origin/main` pushed, and
  `charness update` succeeded on this machine (installed surface `== repo`,
  re-verified by the scaffold==gate check).
- Confirm #335 auto-closes on the next green scheduled mutation run after push.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths` on touched scripts at each commit.
- The touched scripts' own pytest modules; a before/after verdict-equality check;
  `check_export_safe_imports` + mirror byte-sync.

### High-Confidence Checks

- Dogfood: scaffold emits the repo-local validator command and authoring into the
  goal `Activation:` surface surfaces the shape; the touched gates stay green.
- Broad gate (`run-quality.sh --read-only`) + the release gate
  (`run-quality.sh --release`) at the bundle boundary. Fresh-eye `critique` at the
  scaffold-skew (Slice 2) and preflight (Slice 3) boundaries.

### External Or Live Proof

- **Real release + push + on-machine `charness update`** (operator-authorized; the
  agent performs these): release cut (tag + manifests), `git push origin main`,
  `charness update` on this machine, then `doctor` / a scaffold==gate re-check as
  the end-to-end proof. Recorded as executed, with command output.
- **The next scheduled mutation run** is #335's authoritative verdict (the agent
  cannot trigger a `schedule` event; `workflow_dispatch` is inert for the
  changed-line classifier). Recorded as pending external proof; the marker
  auto-closes #335 on the next green run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Add `charness update` (this machine) as a required release-closeout step in the `release` contract/docs; fold in the v0.27.0 real-host smoke | the operator-requested durable fix for the version-skew class | the release contract/docs name the step; release-skill dogfood | done |
| 2 | Fix the scaffold/repo-validator skew: `debug`/`critique` (+ siblings) scaffolds cite the repo-local `scripts/` validator when present; tests; critique | the deeper root that masks gate failures between updates | scaffold emits the repo validator; before/after verdict unchanged; SHIP critique | done |
| 3 | `goal-activation-preflight-surface`: surface the goal `Activation:` preamble shape in the preflight (preamble extraction); tests; critique | the carried-over deferred follow-up; completes the goal-artifact family | `--type goal-activation` surfaces the shape; verdicts unchanged; SHIP critique | done |
| 4 | Bundle proof + REAL release + push + on-machine `charness update` + end-to-end verify; #335 rides along | the operator-requested end-to-end proof | broad + release gates PASS; tag + push done; `charness update` succeeds; scaffold==gate re-verified; #335 pending the next scheduled run | done |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — planned: Slice 1 → `release` + `impl`; Slice 2 → `create-skill`/
  `impl` + `critique`; Slice 3 → `impl` + `critique`; Slice 4 → `quality` +
  `release` + `retro`. Confirm via `find-skills` and record the returned route at
  completion.
- **Gather** — likely n/a — no external URL/Slack/Notion/Docs/Drive source; shaped
  from this session's handoff + retro. Confirm at completion.
- **Release** — IN SCOPE: this goal cuts a real release (version bump + tag) and
  pushes; record the `Release:` proof (the release artifact + tag + push) at
  completion.
- **Issue closeout** — #335 rides along (no pre-verification): carrier = the
  scheduled mutation-workflow marker (auto-close on the next green run after push);
  record the `Issue closeout:` line at completion. #184 is tracked context only.

Completion record (confirmed via `find-skills` at session start):

- Routing: `find-skills` task-recommendation returned `release` as the matched public skill; the goal used `achieve` (owner) coordinating `release` + `impl` (Slice 1), `impl` + `critique` (Slices 2-3), `quality` + `release` + `retro` (Slice 4). No inline phase→skill map baked here.
- Gather: n/a — no external URL/Slack/Notion/Docs/Drive source; shaped from this session's handoff + retro (`find-skills` returned no gather route).
- Release: v0.29.0 cut and verified — release artifact `charness-artifacts/release/latest.md`, tag `v0.29.0` (commit 4ddd9334) pushed to `origin/main`, GitHub release verified (https://github.com/corca-ai/charness/releases/tag/v0.29.0, isDraft:false); release critique `charness-artifacts/critique/2026-06-08-v0-29-0-release-version-skew-bundle-closeout-step-scaffold-fix-preflight-surface.md` (SHIP).
- Issue closeout: #335 rides along — NOT closed by this release; carrier is the scheduled changed-line mutation-workflow marker, which auto-closes #335 on the next green scheduled run after this push (the agent cannot trigger a `schedule` event). Pending external proof. #184 (product metrics) is tracked context only, not in scope.

## Slice Log

_No slices yet. Activation (`/goal`) flips status to `active` and begins Slice 1._

### Slice 1: Slice 1 — charness update as required release-closeout step

- Objective: Make refreshing the maintainer/authoring machine's own managed install (charness update) a REQUIRED release-closeout step so the installed surface stays == repo, killing the installed-vs-repo version-skew class. Fold the open v0.27.0/0.28.0 real-host smoke into the standing checklist.
- Why this approach: Closeout-step-only mechanism (operator-chosen; NO drift detector). Portable release/SKILL.md states the rule generically via the adapter's declared update path; the concrete charness update command lives in the charness-specific install-surface.md reference + the adapter real_host_checklist + docs/host-packaging.md.
- Commits:
- What changed: release/SKILL.md (step 8 fold + Output Shape entry + guardrail clause; net core 160->158, headroom restored 0->2); release/references/install-surface.md (new Maintainer Dev-Machine Install Refresh section + rationale); .agents/release-adapter.yaml (prepended dev-machine charness update item to real_host_checklist); docs/host-packaging.md (closeout-step note); plugins/charness mirror byte-synced.
- Alternatives rejected:
- Targeted verification: 46 release tests PASS (test_release_real_host/publish/publish_real_host_delta/backend); skill-contracts PASS; phase-barrier+Critique pinned phrases preserved; commit-boundary core-headroom ratchet ok (2 left, was 0 — improved, not regressed); staged mirror matches sources; check_real_host_proof.py surfaces the new dev-machine step first when docs/host-packaging.md changes; adapter resolves clean.
- Test duplication pressure: n/a — no tests added/expanded this slice (docs/contract + adapter only); existing release tests reused.
- Critique: Slice-level scoped self-check; fresh-eye critique is scheduled at the Slice-2 (scaffold-skew) and Slice-3 (preflight) boundaries per the verification plan. No compatibility/visibility change here (additive contract + meaning-preserving compression).
- Off-goal findings:
- Lessons carried forward: release SKILL.md was at the 160 core cap; additive contract work must offset with meaning-preserving compression to satisfy the #319 commit-boundary headroom ratchet.
- Metrics:

### Slice 2: Slice 2 — scaffold cites the repo-local scripts/ validator (skew root)

- Objective: Kill the installed-vs-repo version-skew at its root: the 6 artifact-authoring scaffolds (debug/critique/retro/quality/handoff/ideation) cited the *installed* plugin validator (via __file__-ancestor search) before the repo-local one, so an installed validator looser than the repo's shadowed it. Swap to repo-local-first.
- Why this approach: Pure presence/path resolution (NOT a content classifier): if repo_root/scripts/<validator>.py exists, cite it (repo-relative == the gate); else fall back to the __file__-ancestor installed copy for consumer repos with no own validator. Identical swap across all 6 (kept self-contained per-skill for portability/export — the existing accepted clone family stays identical).
- Commits:
- What changed: 6 scaffolds: validator_command repo-local-first swap + explanatory comment; plugins/charness mirror byte-synced; NEW tests/test_scaffold_repo_local_validator.py (parametrized x6: exported scaffold + consumer repo owning the validator -> asserts repo-relative citation, plugin root absent).
- Alternatives rejected:
- Targeted verification: py_compile+ruff clean; check_python_lengths ok (7 files); new regression test 6/6 PASS; existing 15 scaffold-test assertions PASS unchanged (verdict-equality); 29 artifact-surface-preflight tests PASS; live dogfood: scaffold_critique_artifact.py emitted repo-local 'python3 scripts/validate_critique_artifacts.py' citation; critique artifact validates.
- Test duplication pressure: One parametrized test (6 ids) instead of 6 near-identical test funcs; reuses the run_script subprocess helper idiom shared with existing scaffold tests; no new bespoke fixtures beyond a module-scoped single export. Existing per-scaffold tests retained for fallback/run coverage — no duplication of their assertions.
- Critique: Fresh-eye bounded subagent (general-purpose a5ca10ceae751f405): VERDICT SHIP, no blockers. Artifact: charness-artifacts/critique/2026-06-08-slice-2-scaffold-cites-repo-local-validator-version-skew-fix.md. Independently confirmed verdict-equality, mirror byte-identity, regression-test precondition as a real guard, and that check_artifact_surface_preflight.py is independent of the scaffold validator_command.
- Off-goal findings:
- Lessons carried forward: check_artifact_surface_preflight.py builds its OWN validator command from surface.validator and only calls scaffolds for shape text — relevant to Slice 3 (preflight surface) which is independent of this scaffold citation path.
- Metrics:

### Slice 3: Slice 3 — goal-activation preflight surface (Activation preamble)

- Objective: Complete author-time shape coverage of the goal-artifact family: surface the goal Activation: preamble line shape via check_artifact_surface_preflight.py --type goal-activation. The Activation: line is a PREAMBLE line (pre-first ## ), so it needs preamble extraction, not the ## Heading template-section source.
- Why this approach: New template_preamble shape source + _extract_preamble (lines up to the first ## ). Author-time-only: validator=None, commit_boundary=False, with an owner override naming the real enforcer. Additive optional Surface fields (template_preamble, owner) defaulted AFTER paths_arg so existing positional instantiations/replace tests are untouched.
- Commits:
- What changed: scripts/check_artifact_surface_preflight.py (+ byte-identical plugins/charness mirror): goal-activation surface, _extract_preamble, _shape_text/emit_stub/describe wiring, docstring; tests/quality_gates/test_check_artifact_surface_preflight.py (+4 tests); charness-artifacts/spec/artifact-shape-preflight-coverage.md (deferred follow-up flipped to DONE).
- Alternatives rejected:
- Targeted verification: 33 preflight tests PASS (29 baseline verdict-equality + 4 new); py_compile+ruff clean; lengths ok; mirror byte-identical; --type goal-activation surfaces the Activation: preamble; no commit-boundary/blocking behavior added (surface_for_path None for goal files, commit_boundary=False).
- Test duplication pressure: 4 new tests, each a distinct assertion (preamble unit / surface describe / emit_stub / live-template single-source); no duplication of the existing goal-* surface tests — they exercise the new preamble code path and the owner-override branch specifically.
- Critique: Fresh-eye bounded subagent (general-purpose a9dc870c3281165bd): round-1 HOLD (real blocker: owner message misattributed enforcement to --pursue-ready, which SKIPS the Activation check; default check_goal is the enforcer) -> fixed -> round-2 SHIP. Artifact: charness-artifacts/critique/2026-06-08-slice-3-goal-activation-preflight-surface-activation-preamble.md.
- Off-goal findings:
- Lessons carried forward: When a preflight surface NAMES an enforcement command, verify the command actually enforces the surfaced shape — --pursue-ready and the default check_goal_artifact.py check different things; the fresh-eye empirical run caught the misattribution that a string-only self-check would have missed.
- Metrics:

### Slice 4: Slice 4 — bundle proof + REAL release v0.29.0 + push + on-machine charness update + end-to-end verify

- Objective: Prove the bundle end-to-end with a real release rather than asserting it: broad + release gates, cut v0.29.0 (push/tag/GitHub release), run charness update on THIS machine, re-verify installed == repo + scaffold==gate. #335 rides along.
- Why this approach: Operator-authorized irreversible lane (agent runs it all), scoped to this final stage. Refreshed changed-line mutation coverage first so the push is clean (not a new #335 instance). Fresh-eye release critique (HOLD->fix->SHIP) before the irreversible publish.
- Commits:
- What changed: Release commits 4ddd9334 (Release charness 0.29.0: bump + manifests + latest.md) + 360d81c7 (Record release verification); retro auto-trigger charness-artifacts/retro/2026-06-08-v0-29-0-release-auto-retro.md; release adapter update_instructions (0.29.0) + release critique committed at 59c05315.
- Alternatives rejected:
- Targeted verification: EXECUTED PROOF: broad read-only gate 73/0; release-mode gate 73/0 (incl. release_only lifecycle tests); changed-line mutation coverage ok over merge-base origin/main..HEAD (all 9 changed pool files covered, fresh fingerprint). Release: v0.29.0 pushed (origin/main 0/0 synced), tag v0.29.0 on remote (4ddd9334), GitHub release verified (isDraft:false, https://github.com/corca-ai/charness/releases/tag/v0.29.0), all 5 surfaces at 0.29.0 no drift. On-machine: charness update 0.28.0->0.29.0; installed managed-checkout HEAD 360d81c7 == repo HEAD; installed plugin.json 0.29.0; doctor exit 0 (16 checks, none not-ok). Scaffold==gate dogfood: installed debug scaffold cites repo-local 'python3 scripts/validate_debug_artifact.py'; installed validate_debug_artifact.py byte-identical to repo's (skew closed).
- Test duplication pressure:
- Critique: Fresh-eye release critique (general-purpose a371a7a57279a2dd4): round-1 HOLD (stale update_instructions) -> fixed -> round-2 SHIP. Artifact: charness-artifacts/critique/2026-06-08-v0-29-0-release-version-skew-bundle-closeout-step-scaffold-fix-preflight-surface.md.
- Off-goal findings: Non-blocking (release reviewer): stock PyYAML chokes on unquoted backticks in adapter update_instructions; publish path uses the repo's own load_yaml and pre-existing entries already carry backticks — pre-existing property, awareness-only, not filed.
- Lessons carried forward: New commits over a mutation-pool range invalidate the prior coverage fingerprint; refresh the producer (check_changed_line_mutation_coverage --write-fresh-marker over merge-base origin/main..HEAD) before pushing so changed lines are verified and the next scheduled run does not flag a new #335 instance.
- Metrics:

## Context Sources

Follow these in order to reconstruct the goal from a cold start:

1. **This session's handoff** `docs/handoff.md` (`## Next Session` — the
   `charness update` standing-step item + the scaffold/version-skew Discuss note).
2. **The originating lesson:** the #335 goal's debug + retro
   (`charness-artifacts/debug/2026-06-08-issue-335-changed-line-mutation-recurrence.md`,
   `charness-artifacts/retro/2026-06-08-issue-335-gate-recurrence-and-closeout-preflight.md`)
   — the version-skew miss (installed-plugin validator looser than the repo's).
3. **The preflight follow-up:**
   `charness-artifacts/spec/artifact-shape-preflight-coverage.md`
   (`goal-activation-preflight-surface`, deferred).
4. **Release + host surfaces:** `docs/host-packaging.md`, `scripts/doctor.py`,
   `scripts/install_machine_local.py`, the `release` skill,
   `charness-artifacts/release/latest.md` (the v0.27.0 real-host smoke).

## Interview Decisions

- **Mechanism (asked 2026-06-08).** Family: {drift-gate + closeout step; closeout
  step only; drift-gate only}. Chosen: *closeout step only* (no automated drift
  detector — the drift gate is a named deferred option).
- **Irreversible lane executor (asked 2026-06-08).** Family: {agent runs it all;
  agent preps, user runs}. Chosen: *agent runs it all* — the agent pushes, cuts the
  release/tag, and runs `charness update` on this machine, then verifies. Explicit
  override of `achieve`'s no-push default, scoped to this goal's final stage.
- **#335 (operator-directed, not asked).** Closes alongside the push/release with
  no pre-verification; the scheduled run is the authoritative verdict.

## Plan Critique Findings

Self-critique (Before-phase). Fresh-eye critiques run at the Slice-2 scaffold-skew
boundary and the Slice-3 preflight boundary per the verification plan.

- **Irreversible release performed by the agent is the central risk.** Folded:
  Boundaries scope the approval to the final stage; the release/broad gates run
  first; the agent records command output as executed proof; the override is
  explicit and non-carrying.
- **"Closeout step only" can be skipped (no enforcement).** Accepted trade per the
  operator choice; the drift detector is the named done-early/deferred escalation
  if the step proves skip-prone. The scaffold fix (Slice 2) removes the skew root
  even without an update, reducing reliance on the step.
- **Release while many prior goals are unpushed.** The push ships ALL of
  `origin/main..HEAD` (this + prior complete goals); the release/broad gate over
  the final bundle is the attestation. Folded into Slice 4.
- **Over-worry, not folded:** rebuilding the host install/update machinery, or
  adding push/tag CI — out of class (the latter is a separate handoff Discuss item).

## Off-Goal Findings

_None yet. File off-goal findings through `issue`; record only the reference and
reason here — and, per the recurrence discipline, check the seam lineage before
filing a fresh narrow issue._

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md
Host log probe: skipped: host-log-not-exposed: no goal-scoped Host metric window line was recorded for this goal so a goal-scoped host-log probe cannot be bound; session efficiency was reviewed inline in the retro Waste section (the coverage round-trip and the headroom/boundary-bypass ratchet rework passes)
Disposition review: charness-artifacts/critique/2026-06-08-version-skew-bundle-goal-v0-29-0-disposition-review.md
Early close report: charness-artifacts/goals/2026-06-08-charness-update-closeout-step-and-version-skew-fix-early-close-report.md

(The release-trigger retro `charness-artifacts/retro/2026-06-08-v0-29-0-release-auto-retro.md` was also written by the publish helper.)

Early close rationale: the goal completed every planned slice plus the irreversible release and the on-machine end-to-end proof in roughly 1.5h, well before the 4h timebox; the done-early candidate (the installed-vs-repo drift detector) is an explicit Non-Goal this goal, and the operator-approved release/push/update lane does not carry forward to a new feature slice, so continuing would violate scope rather than add safe value. Closing now is the correct move, not a forced early stop.

### Self-verification summary

- All three proposals shipped and PROVEN end-to-end, not asserted: (1) `charness update` is a required maintainer install-refresh release-closeout step in the `release` contract/docs and RAN in this closeout (0.28.0->0.29.0); (2) the six scaffolds cite the repo-local validator — proven by the INSTALLED debug scaffold citing `python3 scripts/validate_debug_artifact.py` after update; (3) `--type goal-activation` surfaces the `Activation:` preamble shape.
- Release v0.29.0 verified: pushed (origin/main 0/0), tag on remote, GitHub release not-draft, 5 surfaces at 0.29.0 no drift; installed surface == repo (HEAD 360d81c7, validator byte-identical); doctor 16/16.
- Gates: broad read-only 73/0; release-mode 73/0; changed-line coverage ok (fresh fingerprint). Three fresh-eye critiques (Slice 2 SHIP; Slice 3 HOLD->SHIP; release HOLD->SHIP).

### Residual risk / non-claims

- NON-CLAIM: #335 is NOT verified closed by this goal — its authoritative verdict is the next green scheduled changed-line mutation run after this push (the agent cannot trigger a `schedule` event). Pending external proof; the workflow marker auto-closes it.
- NON-CLAIM: the second-machine/clean-temp-home fresh-host smoke + the nose checklist in the release real-host checklist were NOT run this goal (single dev machine); the dev-machine install-refresh + dogfood is the executed proof, the fresh-host smoke remains the standing checklist item.
- No drift detector was built (out of scope by operator choice); the closeout-step mechanism relies on the maintainer running it — mitigated structurally by the Slice-2 scaffold fix, which removes the skew even between updates.

## User Verification Instructions

After the run reports complete, the user can independently verify:

1. Read the `release` contract/docs and confirm `charness update` (this machine) is
   a required closeout step; confirm it ran in this goal's closeout (command output).
2. Author a `debug`/`critique` artifact and confirm the scaffold cites the
   repo-local `scripts/` validator (matching the broad gate).
3. Author into the goal `Activation:` surface and confirm the shape is surfaced.
4. Confirm a real release/tag was cut, `origin/main` pushed, and `charness update`
   succeeded on this machine (`doctor` clean; scaffold==gate re-verified).
5. Confirm #335 auto-closes on the next green scheduled mutation run.

## Auto-Retro

Cited retro: `charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md` (it surfaced three actionable workflow improvements; the 3rd — critique-authoring enums — was added as a post-review self-correction after the operator asked whether recent-lessons was fully applied). Disposition review: `charness-artifacts/critique/2026-06-08-version-skew-bundle-goal-v0-29-0-disposition-review.md` (verdict `dispositions-genuine`, covering the original two; the 3rd is the same `applied` form).

Retro dispositions: applied: all three surfaced workflow improvements (1: run the changed-line coverage producer over `merge-base origin/main..HEAD` as the FIRST bundle-boundary step when the session added mutation-pool commits; 2: anticipate the no-increase ratchets — core-headroom and boundary-bypass — on additive contract work; 3: keep the critique scaffold's example enum tokens / check `validate_critique_artifacts`'s allowed `bin`/`action` + `applied`<->`host-confirmed:` set before substituting) were persisted to `charness-artifacts/retro/recent-lessons.md` this run as next-time-checklist / pre-commit-design / critique-authoring signals (real working-tree adds, not prose-only memory). No `issue #N` this goal — the ratchets fired at the correct pre-merge boundary, the fresh-eye critiques caught the two real defects pre-ship, and the critique-enum friction self-corrected within-session, so the gaps are workflow-anticipation, not a missing gate or recurring code-defect class; the deferred installed-vs-repo drift detector stays a named done-early/next-session candidate, not filed.
