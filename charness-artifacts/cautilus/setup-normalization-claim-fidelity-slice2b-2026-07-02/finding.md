# setup (normalization) claim-fidelity floor RE-BASELINE — 2026-07-02 (reference-compaction Slice 7, #413 / #410)

## Verdict

**CAPTURE-GATED MOVE DONE — the refuted RCF doc-open floor is replaced by an
OBSERVED emitted-token RSF floor.** A faithful `/charness:setup` NORMALIZE run
does not open the reference docs, but it DOES emit a canonical per-surface
closeout; the floor now proves that emission instead of a redundant doc-open.

## What ran

Operator-authorized ask-before-run capture (`capture-skill-run.sh`, `claude -p`,
abs out-dir outside the repo) at commit `74c639cf` — the commit that added setup's
`## Closeout Vocabulary`. Same prompt as `normalization.spec.json`. Base commit
recorded in the bundle; the run detected `NORMALIZE`, realigned one AGENTS.md
commit-discipline drift, left the other surfaces already-aligned, and committed clean.

## The re-baseline (old floor FAILED → new floor PASSED)

Both grades are retained in this bundle:

- `observed.old-spec-FAILED.v1.json` — the OLD RCF doc-open floor:
  **outcome=failed, coverage 1/9** (missing `agent-docs-policy.md`,
  `default-surfaces.md` — the run opened neither). Confirms the RCF is still refuted.
- `observed.flipped-PASSED.v1.json` — the NEW RSF emitted-token floor:
  **outcome=passed**, all declared claims met. The 3 INLINE refs drop out of the
  DEPTH-only coverage denominator.

## The flip (evals/cautilus/setup-claim-fidelity/normalization.spec.json)

- `requiredCommandFragments`: `[normalization-flow.md, agent-docs-policy.md, default-surfaces.md]` → `[]`.
- `requiredSummaryFragments`: `[]` → `["Repo mode:", "Normalization non-claims:"]`
  — both OBSERVED verbatim in the run's CLOSEOUT (see `transcript-closeout.txt`;
  RSF matches the final parent assistant text, so a mid-run mention would not satisfy it).
- The 3 census-INLINE refuted docs get `classTag: INLINE` (legal once off the RCF).
- Substance is separately protected by `evals/cautilus/setup-claim-fidelity/outcome-assertions.json`
  (advisory judge; `grade_skill_outcome.py --grade` selftest PASSED, `ran-setup` deterministic PASS).

## Why this is not a #410 softening

`Normalization non-claims:` requires an honest per-surface CHANGED-vs-LEFT + not-proven
accounting (SKILL.md steps 6-7 + Closeout Vocabulary); a shallow "done" run cannot fill
it. `Repo mode:` forces mode detection to surface. Neither is a trivial token pinned to
force green — the floor moved to where honest substance surfaces. Escalation rule if a
future capture ever shows a hollow pass: re-pin `Normalization non-claims:` to a stronger
per-surface phrase or promote the outcome-assertions judge to gating — NEVER soften.

## Scope

`normalization.spec.json` only (in-repo capturable). `greenfield.spec.json` stays
RCF-pinned/deferred (not in-repo capturable, #410). Fresh-eye Slice-2b critique: HONEST +
LOAD-BEARING, no blockers.

## Non-Claims

- n=1 capture: the RSF emitted-token floor is proven at a single sample, not a
  stability proof.
- Scope is `normalization.spec.json` only; `greenfield.spec.json` stays
  RCF-pinned/deferred and is not closed here.
- Not a softening: the escalation rule (re-pin a stronger per-surface phrase or
  promote the outcome-assertions judge to gating, never soften) governs any future
  hollow pass.

## Bundle

- `observed.flipped-PASSED.v1.json` — the passing grade under the new floor.
- `observed.old-spec-FAILED.v1.json` — the failing grade under the old RCF floor.
- `transcript-closeout.txt` — the closeout emitting `Repo mode:` + `Normalization non-claims:`.
- `justification.md` — the operator authorization + purpose.
