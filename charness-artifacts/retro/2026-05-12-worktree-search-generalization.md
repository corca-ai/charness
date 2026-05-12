# Worktree Search Generalization Retro

## Mode

session

## Context

Issue 146/148 work found the immediate worktree readiness and cleanup gaps, but the first sibling search stayed too close to the `worktree` noun and nearby CLI surfaces. The user correctly pointed out that the miss should be generalized by mental model, not only by keyword.

## Waste

The search treated the bug as a domain-local discoverability problem. That found `worktree doctor/prepare/audit`, `impl`/`hitl` versus `spec`, and cleanup as a lifecycle sibling, but it underweighted the structural pattern: lifecycle state exists, readiness is checked only locally, aggregate surfaces do not compose the check, and destructive actions may evaluate safety from the wrong root.

## Critical Decisions

The useful abstraction is lifecycle invariant coverage, not `worktree` coverage. Search should move from noun matching to state-machine questions: create/prepare, inspect/audit, verify/doctor, close/cleanup; then ask whether every mutation phase and renderer carries the same invariant.

## Expert Counterfactuals

Gary Klein premortem: assume another issue of the same class is still open, then ask where an operator believes a lifecycle is safe because one command checks it locally while another command summarizes or acts without composing that check.

Daniel Kahneman bias check: challenge the availability bias from the issue title. The visible word `worktree` made the local keyword search feel complete even though the causal model was broader.

## Next Improvements

- workflow: before closing issue-class work, run one structural sibling pass in addition to keyword sibling search.
- workflow: phrase the pass as mental-model prompts: missing lifecycle endpoint, local check not included in aggregate, mutation skill without readiness probe, renderer hiding failing details, current-working-directory used as authority for safety checks.
- capability: consider a lightweight reviewer checklist for issue resolution that records the structural pattern searched, not just matched files.
- memory: preserve this as a current retro lesson so future issue slices do not stop at noun-neighbor search.

## Persisted

yes: charness-artifacts/retro/2026-05-12-worktree-search-generalization.md
