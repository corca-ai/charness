# Session Retro: portability lens not applied to the premerge-gate

Mode: session (bounded to one user-surfaced miss)

## Context

This session built the changed-line mutation-coverage premerge-gate (spec +
slice 1 consumer + slice 2 producer mechanism) as a **charness-repo-local**
capability. A user correction surfaced the real miss: in a repo whose product
*is* a portable harness, a new reusable mechanism was scoped repo-local without
ever classifying "host-local vs skill-capability" — so the lessons never reached
the `quality` skill and adopting repos get no benefit.

## Waste

- The gate logic lives in repo-root `scripts/check_changed_line_mutation_coverage.py`
  and is wired into charness's `run-quality.sh`; the transferable doctrine
  (stale-coverage freshness guard, the producer-cost lesson) was never written to
  `skills/public/quality/references/mutation-testing.md`. Other repos adopting the
  `quality` skill therefore inherit none of it.
- The miss was caught by the **user**, not by any gate or self-check — the
  portability principle (CLAUDE.md "keep the harness portable") relied on the
  agent remembering it mid-defect-repair, and it did not fire. Unrecorded, the
  lesson would have rotted.

## Critical Decisions

- Pivoting to the forced #320/#321 risk-interrupt was correct. But framing the
  work as *defect repair* ("stop this recurring failure here") locked the
  altitude low: defect-repair never asks "who else needs this?", so the
  product/platform question never got raised.

## Expert Counterfactuals

- **Eric Evans (shared-capability lens).** Would have asked at spec time "is this
  a capability of the product (shared across adopters) or a fix of this repo?"
  and classified the audience before committing repo-local. Changed action: add
  an explicit audience/portability classification to the spec contract for any
  new reusable mechanism.
- **Don Norman (forcing functions; "principles don't scale, checkpoints do").**
  Would convert "keep the harness portable" from a remembered principle into an
  enforced closeout tripwire. Changed action: a portability-classification
  checkpoint at impl/quality closeout when a new reusable script/gate/pattern is
  added repo-local — so it cannot be silently skipped.

## Next Improvements

- **workflow:** at `spec`/`impl` closeout in this harness repo, when a slice adds
  a NEW reusable mechanism (repo-root script, gate, or generalizable pattern),
  require a one-line classification — `host-local` vs `skill-capability` — before
  closeout. Make the portability question a checkpoint, not a principle. Owner:
  `docs/conventions/implementation-discipline.md`.
- **capability:** explore a deterministic nudge — flag a newly-added repo-root
  `scripts/*.py` that implements a generalizable capability and ask whether it
  belongs in a skill. Classification stays judgment, but a prompt-level tripwire
  in the impl/quality contract is feasible and cheap.
- **memory:** this lesson (recorded here + refreshed into recent-lessons). The
  concrete instance follow-up — promote the gate's lessons to
  `quality`'s mutation-testing reference — is already captured as handoff Next
  Session #3 and in the premerge-gate spec "Skill portability".

## Sibling Search

Transferable pattern: **"new reusable mechanism scoped repo-local in a harness
repo without a portability classification."** Immediate sibling = the whole
premerge-gate (this session's instance). A fuller axis — auditing other recent
repo-root `scripts/*.py` for capabilities that should be skill-shipped — is NOT
done here (out of scope for a bounded retro) and is itself the deterministic-nudge
capability above. Follow-up identifier: `follow-up:portability-classification-tripwire`.

## Persisted
