# Achieve Goal: catch authoring/closeout debt at slice time, not push time

Status: COMPLETE (2026-06-07) — #328 resolved + gate-phase coverage closed; see
`## Outcomes` and `## Final Verification`.
Created: 2026-06-07
Activation: `/goal @charness-artifacts/goals/2026-06-08-preflight-gate-phase-coverage.md`

This file is a shaped-but-inactive goal scratchpad. It becomes active only when
the user runs the activation command. It was shaped at the end of the
`2026-06-07-322-advisory-interpretation-rollout` session from that session's
lessons + the handoff + the open issue list, per the operator's request to
prepare the next session's work as an `achieve` goal.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate, then re-confirm the objective against `Discuss Before
  Activation` (the operator may re-point to a candidate objective below).
- Mode: spec-light — small per-check slices; promote to a `spec` only if a shared
  preflight contract/registry emerges.
- Timebox: until objective complete; re-pick the next slice at each boundary.
- Verification cadence: cheap deterministic checks at commit boundaries; targeted
  `pytest` per check; broad `pytest` + one bounded fresh-eye `critique` at the
  bundle boundary.

## Goal (recommended primary objective)

**Close the "debt ships latent because the catching gate only runs at push /
full-quality, not at slice closeout" gap, and resolve #328's cheap upstream
pre-checks** — so the rework class this last session repeatedly hit stops
recurring.

Concretely:

1. **Resolve #328** (https://github.com/corca-ai/charness/issues/328): a
   prose-pin pre-check (given changed `docs/`/`SKILL.md` paths, grep `tests/` for
   literal-string assertions referencing them — catches prose-pin breakage before
   broad pytest) + a lighter authoring-preflight prompt to run
   `check_skill_surface_preflight.py` / skim `authoring-preflight.md` before
   editing a gated surface.
2. **Close the gate-phase coverage gap.** Several hard gates only run in the full
   `run-quality.sh` / pre-push (e.g. `inventory-gitignore-scan-hygiene
   --require-empty`, `validate-retro-lesson-index`), so debt committed during a
   slice ships latent and only surfaces at the next push. Pull the cheap ones
   into the slice-closeout / pre-commit subset (or surface them in
   `run_slice_closeout.py`) so a slice catches them at authoring time.

### Motivating evidence (from the last session — concrete, not hypothetical)

- A new test file written with `subprocess` calls was blocked by
  `check_boundary_bypass_ratchet` only at commit, forcing a full in-process
  rewrite (authoring-preflight class, #308 family).
- #325's `standing_doc_provenance_lib.py` `repo_root.glob` debt
  (`inventory-gitignore-scan-hygiene`) was committed at #325 closeout but only
  surfaced at the v0.27.0 **push**, because that gate is not in the slice-closeout
  subset. Same family as the recent-lessons "deterministic-gate blind spot."
- `validate-retro-lesson-index` staleness after a new retro artifact, also only
  caught at push.
- A length-warn-band / surfacing-prefix near-miss caught by re-reading the filter,
  not by a check.

## Non-Goals

- Do not turn every advisory into a hard pre-commit gate; keep the cheap pre-checks
  proportionate (advisory prompt + the few high-value deterministic ones).
- Do not duplicate gate logic; reuse the existing checkers, just run them at the
  earlier phase.

## User Acceptance

- Editing a gated surface (SKILL.md/docs/new test) surfaces the relevant
  constraint at slice/authoring time, not only at push (demonstrate with the
  boundary-ratchet and gitignore-scan-hygiene cases).
- #328 closed (staged close keyword) with the prose-pin pre-check +
  authoring-preflight prompt landed and tested.

## Candidate Objectives (Discuss Before Activation — operator may re-point)

The last session left these open issues; the recommended primary above is the
strongest tie to that session's lessons, but the operator can re-point at
activation:

- **#330 — meta-validator for the advisory-interpretation contract** (direct
  continuation of #322; enumerate inference-layer surfaces, assert each emits the
  4-field declaration + a paired consumer line; exclude verified facts). Clean,
  bounded; the natural sequel to the just-shipped rollout.
- **#327 — mutation test regression on main** (label `mutation-test`). **Triage
  severity first**: if the mutation gate is actively red on main, this jumps to
  primary (bug-class → route through `debug` before fixing).
- **#329 — retro disposition floor does not reject invalid (prose-only "memory")
  dispositions** (retro tooling hardening; small).
- **#184 — 제품 성공 기준과 핵심 메트릭 정의** (product success criteria / core
  metrics; larger, product-level — needs `ideation`/`spec`, not a quick slice).

## Pending non-goal carryover (not this goal's work)

- **v0.27.0 human real-host smoke** (maintainer-only): the release adapter
  requires a clean-temp-home / second-machine `charness update` + the nose
  tool-doctor/install/sync checklist in
  `charness-artifacts/release/latest.md`. The agent cannot run it; confirm before
  treating the v0.27.0 operator surface as proven.

## Slice Plan (recommended primary)

| Slice | What | Expected evidence | Status |
| --- | --- | --- | --- |
| S1 | Triage #327 severity (is the mutation gate red on main?) | a one-line verdict; if red, re-point primary to #327 | done |
| S2 | Prose-pin pre-check (#328) | checker + test; catches a literal-string test assertion on a renamed doc/SKILL path | done |
| S3 | Authoring-preflight prompt (#328) | prompt/affordance wired where gated surfaces are edited; test | done |
| S4 | Gate-phase coverage: pull cheap full-suite gates into slice closeout | gitignore-scan-hygiene + retro-index caught at slice closeout; test | done |
| S5 | Close #328 + bundle verify + bounded critique + retro | staged close; broad pytest; fresh-eye critique | done |

## Outcomes (this session)

- **S1 verdict (#327): not a hard-red bug-class blocker; primary kept.** The
  mutation *score* passes consistently (88.9%/91.9% vs 80%). The CI FAILs are the
  changed-line *blocking signal* — eligible changed files dropped by selection
  budgets — on *scheduled* main runs, and they are intermittent (last 12 runs
  alternate pass/fail). Scheduled-only + score-green + flaky-selection = real but
  low-severity and non-blocking for development. Not re-pointed.
- **#328 was accidentally closed** by a stray `resolves #328` in the body of the
  handoff commit `12e9d54b` (which only touched the goal file + handoff); the
  actual work had not landed. Reopened, landed the work, closing via the carrier
  commit.
- **S2 — prose-pin pre-check:** `scripts/check_prose_pin.py` (advisory; flags
  tests/ string literals that pin prose removed from a changed doc, and tests/
  references to renamed/deleted doc/SKILL paths). Wired as a slice-closeout
  advisory (`scripts/slice_closeout_advisories.py`). Test:
  `tests/quality_gates/test_check_prose_pin.py`.
- **S3 — authoring-preflight prompt:** extended
  `check_skill_surface_preflight.py --run-checks` to the full portable-package
  gate set (validate_skill_ergonomics, check_skill_ownership_overlap,
  validate_attention_state_visibility) so it reports ALL findings in one pass
  (per the #328 scope-extension comment); added the one-shot-preflight +
  prose-pin sections to `authoring-preflight.md`; added a closeout `ADVISORY:`
  pointer when a gated skill surface is edited. Tests + drift guards added.
- **S4 — gate-phase coverage:** added a dedicated `python-scan-hygiene` surface
  to `.agents/surfaces.json` so `inventory-gitignore-scan-hygiene` runs at slice
  closeout for top-level scripts, nested scripts, and skill scripts (the #325
  class). Confirmed `validate-retro-lesson-index` was already reachable at slice
  closeout via the `retro-lesson-selection-index` surface. Tests in
  `test_surface_obligations.py` cover gitignore-scan, retro-index, and the
  boundary-ratchet acceptance cases.
- **Follow-up filed (#331):** the `repo-python` surface's `scripts/**/*.py`
  pattern does not match top-level `scripts/<file>.py` under fnmatch, so that
  surface's whole verify set (boundary-ratchet, ruff, lengths, attention-state,
  broad pytest) skips top-level scripts at slice closeout. Bigger blast radius
  (closeout cost) — deferred to its own critique/slice.

## Coordination Cues

- **Routing** — query `find-skills --recommend-for-task` per phase; #327 is
  bug-class (`debug` before fix); #328/gate-phase are `impl` + `quality`.
- **Gather** — `n/a unless an issue body cites an external source.`
- **Release** — only if a shipped capability warrants it; otherwise n/a.
- **Issue closeout** — #328 (and #327 if taken); direct-commit carrier, staged
  close keyword, `validate-closeout-draft` proof.

## Context Sources

A fresh session can reconstruct context from, in order:

- **Last session's retro** (the lessons this goal operationalizes):
  `charness-artifacts/retro/2026-06-07-322-advisory-interpretation-rollout.md`.
- **Recent lessons digest:** `charness-artifacts/retro/recent-lessons.md`.
- **Handoff:** `docs/handoff.md` (updated with v0.27.0 state + this goal).
- **Open issues:** `gh issue list --state open` (#330, #329, #328, #327, #184).
- **#328 body:** the prose-pin pre-check + authoring-preflight prompt scope.
- **The gate-phase gap instances:** the v0.27.0 release commit history (the
  #325 gitignore debt + retro-index staleness caught only at push).

## Final Verification

Status: COMPLETE. #328 CLOSED (COMPLETED); carrier commit `1e7dd613` pushed to
`origin/main`; `verify-closeout --expect-state CLOSED` returns ok with no state
mismatches; full `run-quality.sh --read-only` 72 passed / 0 failed.

Retro: done — `charness-artifacts/retro/2026-06-07-issue-328-preflight-gate-phase-coverage.md`.
Host log probe: skipped — allowed reason: a clean, fully-instrumented code session
(git + targeted/broad pytest + full quality gate output all captured); no host
anomaly or refusal to investigate, so a host-log probe would add no signal.
Disposition review: done — all surfaced improvements dispositioned in the retro
`Next Improvements` (workflow -> recent-lessons; capability -> issue #331; memory
-> recent-lessons digest refreshed this session).

## Auto-Retro

Retro dispositions: complete — three improvements surfaced and each given a
concrete destination (verify-issue-state-first habit -> recent-lessons;
top-level-scripts closeout coverage -> #331; non-recursive-fnmatch surface trap
-> recent-lessons digest). No no-improvement opt-out needed.
