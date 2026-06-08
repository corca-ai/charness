# Coverage Report: author-time shape preflight across the artifact-authoring family

Status: Slice-3 deliverable of goal
`charness-artifacts/goals/2026-06-08-authoring-preflight-and-disposition-delaunder.md`
Generated: 2026-06-08 (hand-authored audit; the per-row facts are reproducible
with the commands below)

This report makes "we generalized the preflight" **provable, not asserted**. It
enumerates the hand-authored-artifact-shape validator family, and for each
surface records whether author-time shape help existed *before* this goal,
whether it is *now* covered by `scripts/check_artifact_surface_preflight.py`, and
how (scaffold-by-construction + blocking commit-boundary relocation, or
shape-surfaced only).

## In-class family (hand-authored artifact shape)

Definition: a validator that gates the *sections / fields / enums* of a
hand-authored `charness-artifacts/**` (or default `docs/handoff.md`) markdown
artifact. This is the family the goal scopes; infra validators are out of class
(below).

| Surface | Owning validator | Author-time help BEFORE | Covered NOW | How | Commit-boundary blocking |
| --- | --- | --- | --- | --- | --- |
| critique | `scripts/validate_critique_artifacts.py` | no (scaffold existed but **uncited** — the #334 trap) | yes | scaffold cited from `counterweight-triage.md` + dispatcher `--type/--path/--emit-stub` | yes (`--paths`, prefix `charness-artifacts/critique/`) |
| goal-closeout | `check_goal_artifact.py` (closeout-evidence) | partial (template seeds `## Final Verification`, no dispatcher surface) | yes | dispatcher `--type goal-closeout` reads the template block (validator-constants/template source) | n/a — owned by the achieve complete-flip, not the commit gate |
| retro | `scripts/validate_retro_artifact.py` | no | yes | scaffold + dispatcher | yes (`--paths`, prefix `charness-artifacts/retro/`, excludes `recent-lessons.md`/`history/`) |
| ideation | `scripts/validate_ideation_artifact.py` | no | yes | scaffold + dispatcher | yes (`--paths`, prefix `charness-artifacts/ideation/`) |
| debug | `scripts/validate_debug_artifact.py` | no | yes | scaffold + dispatcher | yes (validate-all, default dir `charness-artifacts/debug/`) |
| quality | `scripts/validate_quality_artifact.py` | no | yes | scaffold + dispatcher | yes (validate-all of `latest.md`, default dir `charness-artifacts/quality/`) |
| handoff | `scripts/validate_handoff_artifact.py` | no | yes | scaffold + dispatcher | yes (validate-all, default file `docs/handoff.md`) |

Result: **7/7 in-class surfaces now have author-time shape help** (was 0 fully /
1 partial). The two #334 proving instances (critique, goal-closeout) are
demonstrated: a parent-delegated critique missing `## Reviewer Tier Evidence` is
blocked at the commit boundary (was a late broad-gate failure), and the
goal-closeout shape is surfaced via `--type goal-closeout`.

Reproduce any row:

```bash
python3 scripts/check_artifact_surface_preflight.py --type <surface>          # required shape
python3 scripts/check_artifact_surface_preflight.py --type <surface> --emit-stub
python3 scripts/check_artifact_surface_preflight.py --path <artifact>         # shape + verdict
```

## Known limitation (named, not silent)

The adapter-scoped surfaces (debug/quality/handoff) are matched at the commit
boundary by their **default** output dir/file. A repo whose adapter relocates the
output dir degrades that surface to **broad-gate-only** coverage (the relocated
commit-boundary block won't fire on the moved path). The broad gate remains the
backstop; the commit-boundary arm is additive relocation, never the sole gate.
Resolving the adapter dir at preflight time is a deferred enhancement (recorded in
the goal's deferred decisions).

## Out of class (no hand-authored artifact shape — correctly NOT covered)

Per the goal's Non-Goals, infra validators are out of scope. For the record, the
validators that reference `charness-artifacts/**` or carry `REQUIRED_SECTIONS`
but are **not** hand-authored-artifact-shape validators:

- `validate_current_pointer_freshness.py` — current-pointer freshness, not artifact shape.
- `validate_inventory_consumption.py` / `..._declaration.py` — inventory declarations.
- `validate_quality_closeout_contract.py` — closeout-contract wiring, not an artifact's sections.
- `check_spec_evidence_durability.py` — cited specs exist; no section/field shape.
- `validate_rca_ledger.py` — JSONL ledger, not a hand-authored prose artifact.
- `validate_skill_output_schemas.py` / `validate_skill_t_inventory.py` — skill/inventory schemas.
- `validate_adapters/profiles/presets/packaging/integrations*.py`,
  `validate_cautilus_*` — packaging / supply-chain / adapter / cautilus infra.

`charness-artifacts/` dirs with **no owning shape validator** (announcement,
gather, narrative, issue-drafts, setup, premortem, design-studies, hitl, dogfood,
metrics, spec, probe, release, cautilus, find-skills, skill-t-mechanism): there
is no gate-time shape to fail, so there is nothing to surface — they are correctly
absent from the registry. If a shape validator is later added for one of these,
add a registry row (the generalization point is the registry, not per-surface
code).

## Verification

- `scripts/check_artifact_surface_preflight.py` registry holds all 7 in-class
  surfaces; `surface_for_path` / `surface_for_type` map them (tests in
  `tests/quality_gates/test_check_artifact_surface_preflight.py`).
- Behavior-preserving: every owning validator is unchanged; `--all` runs stay
  green (critique 255, ideation 0, retro 156; debug/quality/handoff exit 0).
- The blocking commit-boundary member (`check-artifact-shape (staged)`) is a
  `STRUCTURAL_SWEEP_LABELS` member; gate-plan tests assert in-family surfaces pull
  it and non-artifact md does not.
