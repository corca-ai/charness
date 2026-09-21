# Release critique A — charness 8.9.4 patch (closeout-draft readiness)

Reviewer: release-critique-reviewer-a
Verdict: **PASS** — include this change in 8.9.4.
Date (UTC): 2026-09-21
Scope: commit `4e24ed9ee`'s change to
`skills/public/issue/scripts/issue_validate_closeout_draft.py`, plus its
regression test in `tests/quality_gates/test_issue_closeout_draft_validation.py`.
(Nothing else in the commit or release is in scope for this critique.)

Fresh-eye satisfaction: parent-delegated — the spawned subagent reviewer ran the scoped diff, the regression test, and an extra edge case beyond the suite, and delivered this packet with verdict PASS; no same-agent substitution.

## Reviewer Tier Evidence

- **Requested tier**: `n/a` (no tier requested; host-defaulted)
- **Requested spawn fields**: `n/a` (subagent defaults; no explicit model/effort ask)
- **Host exposure state**: `host-defaulted`
- **Application state**: `spawned subagent reviewer delivered; verdict PASS received, approval not inferred`
- **Delivery state**: `findings-received`
- **Execution mode**: `typed-subagent`

## Boundary Ownership

- **Producer:** the issue skill owns closeout-draft readiness
  (`skills/public/issue/scripts/issue_validate_closeout_draft.py`).
- **Consumer:** operators relying on ready/draft_blocked closeout status.
- **Verdict:** `single-surface` — one script's readiness mapping plus its
  regression test; no other surface semantics move with this change.

## What the change actually is

The delegation brief paraphrases this as "refuses ready when new_closeout_data
contains failed checks". The diff I actually ran contains no `new_closeout_data`
symbol. What it does, in 4 changed lines
([issue_validate_closeout_draft.py](/home/hwidong/codes/charness/skills/public/issue/scripts/issue_validate_closeout_draft.py:91)):

- Before: `publication_status` was unconditionally `ready_to_commit_push`
  (direct-commit) / `ready_to_publish` — even when `ok` was `False`.
- After: `publication_status` is the ready value only `if result["ok"]`,
  else `"draft_blocked"`.

The gating expression sits after both failure sources (the reused
`verify_closeout` verdict and the authorization fold that can flip `ok` to
`False`), so every `ok=False` path is covered, not just one failure kind.
The exit-code mapping (`0 if ok else 2`) is unchanged.

## Evidence

### Verified (ran it myself this session)

1. Diff inspected: `git diff v8.9.3..HEAD` and
   `git diff 4e24ed9ee^..4e24ed9ee` on both in-scope files. The production
   delta is exactly the 4-line gating change plus a 2-line comment; the test
   delta is exactly the new
   `test_validate_closeout_draft_failed_draft_never_reports_ready` body.
2. Pre-fix bug reproduced: the `4e24ed9ee^` version of the validator, driven
   with a stub verifier returning `ok=False` over the direct-commit carrier,
   reports `publication_status: ready_to_commit_push`. The stale-ready failure
   mode is real, not hypothetical.
3. Regression suite green: `python3 -m pytest
   tests/quality_gates/test_issue_closeout_draft_validation.py -q` →
   **10 passed**, including the new failed-draft test (failed draft →
   returncode 2, `status: draft_failed`, `publication_status: draft_blocked`,
   no `ready_` prefix) and the two pre-existing happy-path tests that pin
   `ready_to_publish` / `ready_to_commit_push` when `ok` is true.
4. Extra edge cases beyond the cited suite, exercised live against
   `validate_closeout_draft` with stub verifiers (scratch scripts under
   `/tmp`, not committed):
   - failed `pr-body` draft → `draft_blocked` (the suite's new test only
     covers the direct-commit carrier);
   - failed `manual-fallback` draft → `draft_blocked` (third carrier value,
     previously untested on the failure path);
   - `ok` verifier + refused authorization → `ok` flipped `False`,
     `status: draft_failed`, `publication_status: draft_blocked` (proves the
     gating covers the auth-flip path because it is evaluated after the flip);
   - `ok` `pr-body` draft → still `ready_to_publish` (happy path unbroken).
   All four hold.

### Corroborated (consistent with code/tests, not independently observed)

- The commit message's operator story (an author greps the readiness line
  before committing) is consistent with the code shape — `publication_status`
  is a single greppable string distinct from the full verdict — but I did not
  observe an operator workflow; it is the author's rationale, not my finding.

### Degraded (capped claims)

- The brief's "new_closeout_data contains failed checks" wording matches no
  symbol in the diff I ran; I review the gating change as it exists, and cap
  any claim about `new_closeout_data` semantics at "not present in this diff".
- Commit `4e24ed9ee` also touches `scripts/run_quality_engine.py`,
  `scripts/run_quality_engine_output.py`, and two other test files (stale-log
  sweep). Those are **out of scope** and unreviewed here; this PASS covers
  only the two in-scope files. Any release-level verdict must conjoin the
  sibling reviewers' findings on those files.

## Risks / residual notes

- Minimal: the new `draft_blocked` string is a fresh consumer-visible value;
  anyone matching on `publication_status == ready_*` as a boolean is fine,
  but an exact-match consumer expecting only the two ready values would need
  updating. No such consumer was found in the searched tree, and the failing
  exit code (2) already signalled failure before this change.
- No production code was edited, nothing was pushed or committed; probes live
  in `/tmp/edge_closeout_draft.py`, `/tmp/edge_auth_refusal.py`, and
  `/tmp/old_validator.py` for re-runs.

## Verdict

**PASS** for including this change in 8.9.4. Small, correctly ordered,
regression-tested fix for a confirmed stale-ready bug, with all three
carriers and both failure sources verified blocked and both happy paths
verified still ready.
