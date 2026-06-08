# Disposition review — #339 portable residual/disposition ledger bundle

Date: 2026-06-09

Fresh-eye satisfaction: satisfied — a fresh-eye reviewer in a separate agent
context reviewed the closeout dispositions, the residual ledger, and the bundle,
and returned SHIP after the one flagged gap was fixed.

## Scope

The four-slice #339 bundle: the `accepted-risk:`/`out-of-scope:` arms + the
`## Residual Ledger` floor; the proof-semantics adapter boundary; the proof-mismatch
floor wired into achieve closeout; the same floor wired into issue closeout. Broad
gate `run-quality.sh --read-only` = 73 passed / 0 failed; changed-line mutation
coverage over `merge-base origin/main..HEAD` = 0 uncovered.

## Verdict

SHIP. The independent fresh-eye review returned REVISE with one required change,
which has been applied:

- **Caught + FIXED — the draft↔verify parity gap.** The proof-mismatch floor was
  first wired only into `issue_validate_closeout_draft.py` (pre-publication).
  `closeout-discipline.md` documents that `verify-closeout` runs the same
  ledger/critique/close-keyword checks as the draft validator (omitting only the
  final GitHub-state check), so an operator running only post-publication
  `verify-closeout` would have missed proof-mismatch — exactly the "closed with a
  proof non-claim" class #339 targets. Resolved by moving the floor into
  `verify_closeout` (the shared core the draft validator reuses), so the
  pre-publication draft and the post-publication verify enforce it identically.

## Disposition honesty (the three Auto-Retro improvements)

- `#N`-in-skill-file guard → `accepted-risk:` — HONEST. The package-level
  `validate_skill_ergonomics` sweep is a real commit-time backstop that caught all
  three occurrences this run; the residual is edit-time friction, not an escape risk.
- in-slice coverage → `applied:` — TRUE. The reviewer re-ran the changed-line
  mutation producer against the merge-base: 0 uncovered, backed by the green suite.
- at-cap module split → `accepted-risk:` — FAIR. The hard length gate is a real,
  active backstop that forced this run's clean factoring; the next at-cap addition
  to this family should escalate to `issue`.

## Residual ledger + doctrine

- The residual ledger honestly discloses the live/release non-claim, the deferred
  retro-surface wiring, the at-cap split, and the held `#339` GitHub-CLOSED push.
- The held push is the right call: the goal pre-commits to default-no-push, and the
  push is an irreversible outward side-effect, so it is scoped to explicit operator
  approval rather than taken autonomously.
- Doctrine clean: the portable core carries no domain token; proof-mismatch is
  presence/form + generic rank comparison only, never a content classifier; the new
  disposition arms are excluded from the #337 destination vocabulary
  (behavior-preserving over the live corpus, 0 verdict changes).
