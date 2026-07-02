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

## Scenario review

Proof-posture: `plan_cautilus_proof.py` → next_action none, so deterministic
validation + this scenario review own closeout and a live capture is
contract-refused (eval-only, ask-before-run).

- **Weak-on-cost gate**: green E2E smoke now covered by a cheaper unit proof →
  brief's `weak` definition drives the same `weak`+delete recommendation without
  the mandatory read. At-least-as-smart.
- **Silent-gap repo**: final gate, no pre-push hook → probe DETECTS the gate,
  brief emits the enforcement prompt proactively → gap flagged `missing` without
  the mandatory read (arguably smarter: probe-driven, not reader-primed).
- **Inference-layer inventory** (`inventory_nose_clones`): the tool self-emits
  its interpretation question at run time; the up-front read was redundant.

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
