# Subagent Delegation Salience Debug
Date: 2026-04-24

## Problem

After README/handoff alignment review, I described delegated review as blocked
by a generic host-level policy instead of treating this repo's checked-in
`AGENTS.md` subagent rule as the explicit delegation request it was meant to be.

## Correct Behavior

Given a task-completing `quality`, `init-repo`, or required premortem/fresh-eye
review in this repo, when the initial `find-skills` inventory is complete, then
the agent should spawn the bounded reviewers without asking for another user
message. If the host actually blocks `spawn_agent`, the final report should
include the concrete host/tool signal.

## Observed Facts

- Current `AGENTS.md` has a `Subagent Delegation` section that says required
  bounded review is already delegated and should not be replaced with a
  same-agent pass.
- The same session could successfully call `spawn_agent`, so this was not an
  actual host/tool block.
- Commit `e17b1b2` moved the subagent rule out of all-caps Operating Stance
  bullets into a separate prose section. The meaning stayed correct, but the
  salience as an explicit user delegation request weakened.
- Prior commits `159859e`, `31e239a`, `8c1642a`, and `2c1f8bd` progressively
  tightened delegated-review policy and drift detection.

## Reproduction

1. Read current `AGENTS.md` and `skills/public/quality/SKILL.md`.
2. Run a task-completing quality review.
3. Observe whether the agent spawns bounded reviewers after initial inventory
   or instead reports a vague host-policy limitation.

## Candidate Causes

- The current `AGENTS.md` wording did not explicitly say the section itself is
  the user's delegation request for the bounded scope.
- The move from all-caps Operating Stance bullets to a prose section lowered
  salience for an agent trying to reconcile generic host guidance.
- The local validator checked for "already delegated" and "second user
  message" but not for the stronger "explicit delegation request" wording.

## Hypothesis

If `AGENTS.md`, init-repo policy references, and the inspector required snippets
all include `explicit delegation request`, future agents and validators will
classify the repo rule as a concrete delegation instruction rather than a
background preference.

## Verification

- `python3 -m pytest tests/quality_gates/test_docs_and_misc.py tests/quality_gates/test_init_repo_inspect_policy.py -q`
  passed: `45 passed`.
- `python3 scripts/validate_skills.py` passed.
- `python3 scripts/run_evals.py` passed: `20` scenarios.
- `python3 scripts/check_doc_links.py --repo-root .` passed.

## Root Cause

The recent AGENTS change did not remove the delegation rule, but it made the
authorization signal less explicit. I then misread the active instruction stack
and treated a generic host rule as a blocker even though the repo-supplied
instructions already contained the user's explicit delegation request and
`spawn_agent` was available.

## Seam Risk

- Interrupt ID: subagent-delegation-salience
- Risk Class: contract-freeze-risk
- Seam: repo instruction contract vs host subagent tool policy
- Disproving Observation: a bounded `spawn_agent` call succeeded in the same session.
- What Local Reasoning Cannot Prove: whether every future host will treat
  repo-local AGENTS wording as sufficient delegation without a stronger phrase.
- Generalization Pressure: monitor

## Interrupt Decision

- Premortem Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

- Restore high-salience wording in `AGENTS.md`: the subagent section is an
  explicit user delegation request for the named bounded scopes.
- Propagate that phrase into init-repo generated policy references.
- Make `scripts/init_repo_agent_docs_lib.py` require
  `explicit delegation request` so future init-repo inspection catches drift.
