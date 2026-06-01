# Critique: Issue #277 Closeout Binding Resolution

Date: 2026-06-02
Issue: #277
Fresh-Eye Satisfaction: parent-delegated
Target: issue closeout verifier, goal close-intent cue, handoff active-goal routing

## Change

Issue #277 reported that a goal-run issue closeout can miss the actual
auto-close carrier and can over-satisfy bundled issue critique evidence. The
fix splits resolution-critique verification into a dedicated helper and makes
multi-issue carriers bind critique evidence to each selected issue number.

This slice also keeps the current goal and handoff honest while the user asked
to resolve #277 alongside the active workflow-improvement goal.

## Fresh-Eye Review

### Causal Review

Mendel classified #277 as a bug. The root mental model was that closeout
evidence belonged to the carrier as a whole; `issue_verify_closeout` accepted
repeated `--number` selectors but checked one global `Critique:` line. The
recommended prevention was per-issue or explicit-bundle critique binding, plus a
close-intent ledger on active goals when a goal resolves tracked issues.

### Post-Implementation Review

Lorentz, Peirce, and Dirac reviewed the implementation read-only.

Act-before-ship findings folded:

- Include the new `issue_resolution_critique.py` helper in both source and
  plugin export surfaces.
- Update stale `Critique: full <path>` public issue docs so operators do not
  write a carrier value the verifier treats as a filename.
- Sync the setup renderer so generated Skill Routing prose matches `AGENTS.md`.
- Record the active goal's #277 close-intent cue.
- Sync handoff chunked-routing reference prose to the new active-goal filter.

Regression coverage folded:

- Multi-issue carriers with unqualified `Critique: <path>` no longer satisfy
  all selected issues.
- Explicit bundle critique evidence must bind to every selected issue number.
- Fenced `Critique:` examples do not count as proof.

## Counterweight

Over-worry not folded:

- Enforcing trackedness or a strict `charness-artifacts/critique/` path for
  critique evidence is broader than #277's per-issue binding failure.
- A deterministic `Issue closeout:` goal floor is valid follow-up territory,
  but this slice records the cue and lets the issue verifier enforce the actual
  closeout carrier.
- More fence syntaxes can wait; the verifier and existing body parser both use
  triple-backtick fences today.

## Result

The #277 issue evidence is bound to this artifact by filename and content. The
commit carrier should use:

`Critique #277: charness-artifacts/critique/2026-06-02-277-closeout-binding-resolution.md`
