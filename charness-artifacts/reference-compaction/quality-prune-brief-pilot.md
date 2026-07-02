# Quality prune+brief pilot — result + reusable pattern (2026-07-02)

Serves [intent.md](./intent.md): the north is a SMARTER agent; the test is
"그게 정말 최선인가?" (no proxy). This is the first executed instance of the
prune+brief pattern the rest of the sweep follows.

## The pattern (reusable across the 24 skills)

A mandatory `required-primer` read earns its keep only if its load-bearing
residue cannot be **briefed**. The lever is not "delete the ref" or "flip role to
on-demand" — a naive flip strands capability. It is: **upgrade the planner stdout
from a read-list into a substantive briefer, then the primer safely becomes
trigger-gated depth.** (intent step 5: 게이트 stdout으로 지능을 채널링.)

Mechanism (mirrors retro's `lens_brief`): `plan_quality_run.py` emits a `brief`
extension carrying the demoted primers' always-relevant residue inline; each
brief block keeps a `detail_ref` + a catalog `trigger` so the full doc is one
open away when depth is actually needed.

## What shipped

Demoted 3 of the 9 mandatory primer reads (required_reads 9→6; −479 lines of
forced reading), each adversarially verified before the demotion:

- **gate-classification.md** — brief carries the 4 closeout states
  {healthy/weak/missing/deferred} *with* the non-obvious rule "a green,
  non-shallow gate is still WEAK if a cheaper proof now covers the same seam"
  (a bare enum label was proven insufficient).
- **automation-promotion.md** — brief carries the AUTO_* 3-case + the
  inference-layer interpretation rule; per-surface questions stay on-demand
  because each inventory self-emits them at run time.
- **maintainer-local-enforcement.md** — brief carries a pre-push-enforcement
  prompt (sharpened by a cheap `_detect_final_gate` file probe) + the
  "Unclear→default `missing`" field discipline; the probe makes the prompt
  *proactive* so the silent-gap repo (final gate, no hook) is still caught.

## Capture (H0) — empirical, not predicted

The capture harness (`capture-skill-run.sh` + `build-skill-execution-observation.mjs`)
is host-owned and ungated; only `cautilus evaluate` scoring is ask-before-run
(`plan_cautilus_proof.py` → next_action none). So a real `/charness:quality` run
on HEAD was captured. Result:

- **Pilot confirmed:** the run read references with one for-loop over **exactly
  the 6 remaining primers** and opened **0 of the 3 demoted docs**, fidelity
  passed (RCF `quality-lenses.md`). The mandatory reads were genuinely droppable.
- **2 residues confirmed without their docs:** it proactively probed pre-push
  enforcement, **found + classified WEAK + fixed** a real `.githooks/pre-push`
  gap (maintainer-local residue), and wrote proper `## Healthy/Weak/Missing/
  Deferred` sections (gate-classification residue) — neither doc opened.
- **Cost OBSERVED corrected the assumption:** 168k output tokens / 18.9M cache /
  19.5min / 103 tools. The dominant cost was **not** reference reads (already
  lean) but artifact **closeout churn** — see follow-up.

## Capture-driven follow-up: closeout churn fix (SHIPPED)

The capture showed the run hand-wrote the quality artifact and re-ran the
fail-fast `validate_quality_artifact.py` **6×** (one format error per run),
skipping the scaffold. Fixed (intent step 5 — template + gate stdout):

- validator CLI default flipped fail-fast → **report-all** (all violations in one
  pass; `--fail-fast` opt-out kept). SKILL.md step 8 → **scaffold-first** (the
  scaffold emits a validator-passing skeleton). Fresh-eye critique SOUND.
- **Method lesson for the sweep:** capture-then-diagnose, don't assume the lever.
  Observation found a bigger lever (closeout churn) than the reference pruning.
- `cautilus improve` (optimize surface) is **disabled by repo policy**
  (`cautilus-on-demand.md`) — not the path; the H0 capture + diagnosis was.

## Verification

- deterministic: `tests/quality_gates` 2475 passed; catalog/index parity + claim-
  fidelity specs green; plugin mirror re-synced.
- adversarial verify (4 skeptics) reshaped the plan: refuted the naive flip for
  3/4 candidates → the brief-upgrade design.
- fresh-eye critique: SOUND (ship it); confirmed KEEP-inventory-dispatch.

## Deferred (documented, not dropped)

- **inventory-dispatch.md** kept required: ~19 inventory scripts live only there
  and the planner emits no script names. Next instance needs a machine-readable
  `scripts:` routing layer in catalog.yaml so the planner can brief the routing;
  then it demotes safely. Biggest remaining always-loaded item (297 lines).
- **proposal-flow / operability-signals / skill-quality / skill-ergonomics**:
  softer candidates, not yet adversarially verified — verify before demoting.
- **quality-lenses.md** stays the one `required-primer` + RCF floor.
