# Achieve Goal: Add the charness-update release-closeout step + fix the scaffold/repo-validator version-skew + goal-activation preflight surface, proven end-to-end by a real push + release + on-machine update (with #335 closing alongside)

Status: active
Created: 2026-06-08
Activation: `/goal @charness-artifacts/goals/2026-06-08-charness-update-closeout-step-and-version-skew-fix.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 3 — `goal-activation-preflight-surface`. Slices 1 & 2 DONE (committed; Slice 2 fresh-eye critique SHIP).
- Next action: surface the goal `Activation:` preamble shape in `check_artifact_surface_preflight.py` (preamble extraction, not the `## Heading` template-section source); tests; verdict-equality; fresh-eye critique at the boundary. Note: the preflight builds its OWN validator command from `surface.validator` (independent of the Slice-2 scaffold citation path).
- Timebox: 4h
- Activation time: TBD (set at `/goal`)
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
| 3 | `goal-activation-preflight-surface`: surface the goal `Activation:` preamble shape in the preflight (preamble extraction); tests; critique | the carried-over deferred follow-up; completes the goal-artifact family | `--type goal-activation` surfaces the shape; verdicts unchanged; SHIP critique | planned |
| 4 | Bundle proof + REAL release + push + on-machine `charness update` + end-to-end verify; #335 rides along | the operator-requested end-to-end proof | broad + release gates PASS; tag + push done; `charness update` succeeds; scaffold==gate re-verified; #335 pending the next scheduled run | planned |

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

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

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

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
