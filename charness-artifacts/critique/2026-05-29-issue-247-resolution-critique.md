# Resolution Critique — issue #247

- **Issue**: corca-ai/charness#247 — should `/goal` be strictly pursue, with all
  shaping owned by `/achieve`? **Decision (maintainer): adopt + (b) fail-fast.**
- **Class**: feature (decision made; implementing the agreed contract).
- **Target reference**: code-critique (design critique on a prompt-surface +
  script change).
- **Prepare packet consumed**: `charness-artifacts/critique/2026-05-29-064112-packet.md`.
- **Framing question**: what would let `/goal`'s pursue-only contract silently
  regress, misclassify a real goal, or break the legitimate happy path?

## Design under review

`/goal` = pure pursue (never shapes); shaping owned by the achieve Before-phase
(`/achieve`); `/goal` on an unshaped goal **fail-fasts** and routes to
`/achieve`. Implemented as: `goal_artifact_lib.pursue_readiness` (marker-based
detector) + `check_goal_artifact.py --pursue-ready`; achieve `SKILL.md` +
`references/lifecycle.md` prose (incl. removing the #239 "explicit `/goal`
already happened ⇒ run-mode" clause); contract + detector tests.

## Angles (3 bounded fresh-eye reviewers, parent-delegated)

1. **Contract completeness** — no surface left implying `/goal` shapes; #239
   block stayed coherent after the clause removal; pipeline (#246 chunker →
   `/achieve` → `/goal`) composes. One nit: SKILL.md cited `--pursue-ready`
   without `--goal-path`.
2. **Detector soundness** — flagged false-negative (base-template/empty goals
   pass), false-positive (inline-code/prose quoting the marker; `_mask_fences`
   only masks triple-fence), and stuck-state (no guarantee shaping removes the
   marker).
3. **Regression risk** — verdict clean: #239 intent preserved (mode question
   still fires; auto-execution now structurally impossible), no other consumer
   relied on `/goal` shaping, existing tests still hold.

## Counterweight triage (four bins) — judged against the #247 responsibility model

The model (caller is responsible for handing `/goal` a ready goal; the fail-fast
is a courtesy guard against the known chunker hand-off mistake, not a goal-quality
validator) reframes several findings.

- **Act Before Ship**: SKILL.md `--pursue-ready` command missing `--goal-path`
  (errors as written). **DONE.**
- **Bundle Anyway**: add a Before-phase clause that shaping must overwrite the
  placeholder marker (kills the stuck-state at source). **DONE** (SKILL.md +
  lifecycle.md).
- **Over-Worry**: false-negative on base-template/empty goals (this is the
  responsibility model working — the caller owns pursuing an unshaped goal);
  stuck-state via self-inflicted leftover marker (loud, recoverable, covered by
  the new prose); matching the separate `plan-critique` placeholder variant
  (gold-plating — the auto-draft carries the Before-phase marker 3×).
- **Valid but Defer**: inline-code-span / prose false-positive (narrow — needs
  an author to inline-quote the sentinel phrase); extend `_mask_fences` to inline
  spans and add the regression test **only if it recurs**. Tracked here, not as a
  separate issue.

## Decision and proof

- **Decision**: ship after the Act-Before-Ship doc fix (applied) + the bundled
  marker-overwrite prose (applied); over-worry items dropped; the inline-span
  false-positive deferred.
- **Proof**: deterministic local gates — full repo-python pytest (1668 passed,
  4 skipped, incl. 3 new `pursue_readiness` tests + the contract gate), plus
  validate_skills / packaging / doc-links / check-markdown / check-secrets /
  validate_cautilus_proof (deterministic-owned; planner `next_action: none`) /
  public-skill validation+dogfood / ruff. No live/provider proof applicable to a
  prompt-surface + helper change.

## Fresh-Eye Satisfaction

parent-delegated (3 angle subagents + 1 separate counterweight subagent).
