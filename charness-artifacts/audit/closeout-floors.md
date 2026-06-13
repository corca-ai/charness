# Closeout-Floor Audit

Direction D of spec
[achieve-efficiency-improvements](../spec/achieve-efficiency-improvements.md):
the teeth-restraint philosophy applied to ourselves. This audits the **standing
deterministic blocking floors** that gate closeout/commit and assigns each a
disposition. **Audit output only — no floor is removed in this slice.** Removal
is a separate, critiqued change.

Dispositions:

- **keep** — genuinely needs to stay a standalone blocking floor; cheap, distinct
  surface, low false-fire risk.
- **absorb** — should be (or now is) surfaced up front by the describe-first
  closeout preflight / an advisory, so it no longer drives serial-rejection churn
  even though it still blocks. The Problem-1 fix is *visibility up front*, not
  deletion.
- **merge** — overlaps a sibling floor checking the same surface; a future
  consolidation could fold them into one gate (tracked, not done here).

Source surfaces audited: the `achieve` goal-closeout evidence floors
([goal_artifact_lib.py](../../skills/public/achieve/scripts/goal_artifact_lib.py),
[goal_artifact_closeout_evidence.py](../../skills/public/achieve/scripts/goal_artifact_closeout_evidence.py)),
and the repo closeout/commit verify chain
([surfaces.json](../../.agents/surfaces.json) verify_commands +
`.githooks/pre-commit`).

## A. `achieve` goal-closeout evidence floors (Problem-1 churn source)

These are the floors A1's describe-first wiring (the dispatcher
`scripts/check_artifact_surface_preflight.py --type goal-closeout`, which reads
[describe_goal_closeout_shape.py](../../skills/public/achieve/scripts/describe_goal_closeout_shape.py),
plus a dry `check_goal_artifact.py` pass) is designed to surface *before*
drafting. **Completeness note:** this is the full set of live `report["ok"]=False`
goal-closeout floors as of this audit (verified against
[goal_artifact_lib.py](../../skills/public/achieve/scripts/goal_artifact_lib.py),
[goal_artifact_disposition.py](../../skills/public/achieve/scripts/goal_artifact_disposition.py),
[goal_artifact_coordination_floors.py](../../skills/public/achieve/scripts/goal_artifact_coordination_floors.py),
[goal_artifact_section_placeholders.py](../../skills/public/achieve/scripts/goal_artifact_section_placeholders.py),
[goal_artifact_closeout_delegation.py](../../skills/public/achieve/scripts/goal_artifact_closeout_delegation.py),
[goal_artifact_timebox.py](../../skills/public/achieve/scripts/goal_artifact_timebox.py),
[goal_artifact_early_close_report.py](../../skills/public/achieve/scripts/goal_artifact_early_close_report.py)),
not a representative subset.

| Floor | What it blocks | Disposition | Note |
|-------|----------------|-------------|------|
| `REQUIRED_SECTIONS` (H2 presence) | A goal missing a required `##` heading | **absorb** | Static catalog — the preflight lists all of them up front; A1 makes the author see the set in one pass instead of failing the flip per missing heading. Keep blocking; churn removed by visibility. |
| `PORTABILITY_SECTIONS` (Context Sources, etc.) | Missing reconstruction-context headings | **absorb** | Static, preflight-surfaceable. |
| Disposition rung 1a (block-the-blank `## Auto-Retro`) | A blank/placeholder Auto-Retro when a cited retro lists improvements | **keep** | Substance floor (block-the-blank); needs runtime evaluation of the cited retro, so it is **not** derivable from the static catalog. The dry `check_goal_artifact.py` pass surfaces it for *this* goal; A2 (goal-conditional describe, deferred) would fold it into the preflight. |
| Disposition rung 1b (`disposition_review` line, in-scope) | In-scope goals missing the review-ran evidence line | **keep** | Conditional (in-scope + grandfather-by-Created); runtime-evaluated, not a static catalog item. |
| Disposition rung 1c (`disposition_form`) | Malformed disposition line shape | **absorb** | The exact "form an author discovers by failing the flip" the describe-first tooling was built for; preflight renders the form. |
| Disposition rung 1d (`recurrence_lineage`) | Missing recurrence-lineage link | **absorb** | Form-shaped; preflight-surfaceable. |
| Disposition rung 1e (`structural_followup`) | Cited transferable-waste retro missing a structural-follow-up *destination* line | **keep** | Conditional on the cited retro's content; runtime-evaluated. |
| Disposition rung 1f (`residual_ledger`) | A `## Residual Ledger` row without a valid disposition | **absorb** | Row-form shaped; the preflight renders the ledger row form. |
| `## Final Verification` evidence (`Retro:`, `Host log probe:`) | Missing closeout evidence lines | **absorb** | Listed by the preflight; A1's whole point. |
| Section-placeholder floor (`final_status_placeholders`, **#359**) | A `complete` goal whose H2 section still holds a seeded closeout placeholder | **keep** | The floor #359 actually shipped (complete-state + pending placeholder must not coexist); needs the live status+body, not a catalog. |
| `## Coordination Cues` `Routing:` (names `find-skills` + routed skill) | Routing line not naming both | **merge** | One of four floors in the same `## Coordination Cues` section — see below. |
| `## Coordination Cues` gather floor | Gather-triggered goal missing the gather coordination line | **merge** | Same section + same opt-out grammar as Routing/release/issue-closeout; strongest consolidation candidate. |
| `## Coordination Cues` release floor | Release-triggered goal missing the release coordination line | **merge** | Same family. |
| `## Coordination Cues` issue-closeout floor | Issue-closeout goal missing the issue coordination line | **merge** | Same family. |
| Closeout-delegation floor | Orchestrator/sub-goal goal missing closeout-proof delegation | **keep** | Conditional on orchestrator/sub-goal shape; no-op for standalone goals; runtime-evaluated. |
| Timebox floor (`check_timebox_closeout`) | A timeboxed goal closing without early-close readiness | **keep** | Conditional on a `Timebox:` marker + clock; cannot be a static catalog item. |
| Early-close-report floor | A skipped or malformed early-close report | **absorb** | Report *shape* is form-shaped (the preflight can render it); the *when-required* trigger is conditional. |

**A-level finding:** of the live goal-closeout floors, the **absorb** class
(static or form-shaped — `REQUIRED_SECTIONS`, `PORTABILITY_SECTIONS`, rungs
1c/1d/1f, Final Verification evidence, early-close report shape) is the
Problem-1 churn source, and A1 (Slice 1) already wired the describe-first
preflight + dry-check that surfaces them up front. The **keep** floors (rungs
1a/1b/1e, section-placeholder/#359, closeout-delegation, timebox) are
*conditional, runtime-evaluated* floors a static catalog structurally cannot
surface — they carry a **residual** reactive-rejection risk that A2
(goal-conditional describe, deferred probe) is what closes, not this slice. The
**merge** finding is now sharper: the four `## Coordination Cues` floors
(routing/gather/release/issue-closeout) share a section and opt-out grammar and
are the strongest single consolidation candidate. No *new* floor is warranted to
fix Problem 1 — visibility (absorb) and A2 (the conditional residual) are the
levers, not more teeth.

## B. Repo closeout/commit verify chain

Grouped; each group is one disposition. None removed.

| Floor group | Examples | Disposition | Note |
|-------------|----------|-------------|------|
| Packaging/mirror integrity | `validate_packaging`, `validate_packaging_committed`, `check_staged_mirror_drift` | **keep** | Distinct hard surface (the mirror-drift barrier is non-negotiable, #257); cheap; no churn class. |
| Skill structure | `validate_skills`, `validate_skill_ergonomics`, `check_skill_contracts`, `check_skill_bootstrap_vars`, `check_skill_ownership_overlap` | **keep** | The structural sweep already runs ergonomics/attention-state FIRST (#332) so they fail at the cheap boundary, not at minute six — this is the describe-first/absorb pattern already applied at the repo level. |
| Markdown/doc | `check_doc_links`, `check-markdown`, `check_command_docs`, `check_title_slug_drift` | **keep** | Cheap, deterministic, distinct surfaces; low false-fire. |
| Python hygiene | `ruff`, `check_python_lengths`, `check_python_filenames`, `inventory_gitignore_scan_hygiene` | **keep** | Length gate is the hard floor; the near-limit advisory already absorbs the *authoring* signal (#256) — the right advisory/floor split is already in place. |
| Prompt/skill policy | `validate_cautilus_proof`, `validate_public_skill_validation`, `validate_public_skill_dogfood` | **keep** | Policy alignment floors; the Cautilus *run* itself is correctly advisory (ask-before-run), so the blocking surface here is only deterministic alignment, not a heavy proof. |
| Attention-state visibility | `validate_attention_state_visibility` | **keep** | Distinct invariant (no silent skip states); cheap. |
| Boundary/repo-copy ratchets | `check_boundary_bypass_ratchet`, `check_test_repo_copy_invariants`, `check_staged_reversion` | **keep** | No-increase ratchets and structural sentinels; cheap, fail at commit boundary by design. |
| Broad pytest + mutation coverage | `pytest`, `--produce-mutation-coverage` consumer | **keep** | Final-bundle proof; the meaningful-slice cadence already restrains *cadence* (run once at the bundle boundary), which is the correct lever, not removing the floor. |

**B-level finding:** the repo verify chain shows the *intended* end state — cheap
structural floors run first (sweep), authoring signals are advisories
(near-limit, over-slice, gate-runtime), and the expensive floor (broad pytest)
is cadence-restrained to the bundle boundary. No repo floor is a Problem-1 churn
source today; the one `merge` candidate is in surface A (routing). The standing
risk is *additive*: the next new floor should pass the
[Floor-Addition Restraint](../../docs/conventions/implementation-discipline.md)
checklist rather than being added by reflex.

## Summary

- **absorb (surface A): 7** static/form floors — `REQUIRED_SECTIONS`,
  `PORTABILITY_SECTIONS`, rungs 1c/1d/1f, Final Verification evidence, early-close
  report shape. Fixed by A1's describe-first *visibility*, not by removal.
- **merge (surface A): 4** — the `## Coordination Cues` family
  (routing/gather/release/issue-closeout), one consolidation candidate.
- **keep (surface A): 6** — rungs 1a/1b/1e, section-placeholder (#359),
  closeout-delegation, timebox: conditional, runtime-evaluated floors a static
  catalog cannot surface; their residual reactive-rejection risk is **A2's** scope
  (deferred), not a regression.
- **Surface B (repo verify chain): keep all** — distinct, cheap, low-false-fire;
  the intended advisory/floor/cadence split is already in place.
- **No floor removed.** Load-bearing conclusion (narrowed for honesty): the
  Problem-1 churn was the *absorb-class* floors, already fixed by A1's
  describe-first visibility, plus cadence (B/C). A residual churn risk remains on
  the *conditional `keep`* floors until A2 lands. So direction D's net new
  contribution is the **restraint checklist** to stop the *next* reflexive floor —
  not remediation of existing ones, and not (yet) closure of the conditional
  residual. Removal of the `merge` family and an enforcement *nudge* for the
  checklist itself are separate changes with reopen triggers (see below).
- **Honest non-claim (updated 2026-06-14):** this audit is output only and the
  restraint checklist was prose. The deterministic, *advisory* (non-blocking)
  floor-addition nudge that gives it teeth — `advise_floor_addition_restraint` in
  `scripts/slice_closeout_advisories.py`, wired into `run_slice_closeout.py` — has
  now **shipped** (`follow-up:floor-addition-restraint-nudge`, resolved). It flags a
  new blocking floor (new `report["ok"] = False` site / new `REQUIRED_*` member)
  added without a recorded restraint call. The audit itself stays output-only. A
  *blocking* enforcement gate is still deliberately rejected: it would be the exact
  reflex D names.
