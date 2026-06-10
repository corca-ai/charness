# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **[Next-queue goal (lane verification + #346 metric scoping + #348 hotl)](../charness-artifacts/goals/2026-06-10-push-release-verify-346-metric-scope-348-hotl.md) COMPLETE, awaiting push.**
  Slice 1: second 2026-06-10 push + v0.38.0 release lane verified read-only
  (quality-core 27264481707 green on fd3c2c6c; installed plugin 0.38.0 ==
  tag via live probe; scheduled mutation 27261418055 green over 39ff5432 —
  prior carried proof retired; the next slot fired in-goal over fd3c2c6c,
  run id in the goal artifact). Slice 2 (#346, CORRECTED root cause): the
  misattributed measured block was a STALE Codex rollout rendered on a
  Claude-host run — a new
  [Claude session auditor](../scripts/claude_session_jsonl_audit.py), dual-key
  `Host metric window:` grammar (`claude_session_file`), render-path
  freshest-session disambiguation with named provenance, and
  `record_metric_window --claude-session-file` (carrier 84dc1db3,
  `Closes #346` staged; this goal's own closeout dogfooded the scoped
  window end-to-end). Slice 3 (#348): new portable public skill
  `skills/public/hotl/` (human-on-the-loop closure of applied behavior;
  7-status proof ledger vocabulary, proof rules, adapter-owned repo
  specifics; carrier a65a232c, `Closes #348` staged). Bundle: broad 73/0,
  changed-line consumer 0 uncovered, four fresh-eye reviews (activation
  plan, two slice critiques, disposition review ACCEPT).
- Open issues (`gh`): **#184** (product metrics — operator `ideation`
  needed, FIFTH exclusion); **#349** (hitl/hotl boundary one-directional;
  hitl core at its 200-line ceiling — needs a deliberate frozen-contract
  trim; filed by this goal, lineage cross-linked to the detection class).

## Next Session

- **Push the staged closeouts** (maintainer; `achieve` does not push):
  `origin/main..HEAD` carries the slice/closeout commits including the
  `Closes #346` / `Closes #348` carriers — both validated
  `draft_verified`; verify both issues flip CLOSED after the push
  (`issue_tool.py verify-closeout`).
- **Deferred proof to consume:** the scheduled `mutation-tests.yml` run
  over fd3c2c6c (fired 10:40Z in-goal; verdict recorded in the goal
  artifact's Final Verification) and the first scheduled run covering the
  newly pushed carriers' HEAD.
- **#349** — small bounded slice: trim one line from hitl's reviewed core
  (contract-freeze discipline) + the reciprocal `hotl` boundary line.
- **ceal-side consumption of `hotl`** — named in #348 as the consuming
  repo's follow-up (adapter wiring + retiring its repo-local close-loop);
  not charness work, but worth surfacing to the operator.
- **#184** (product metrics) — product-level; needs `ideation`/`spec`, not
  a slice (fifth consecutive deliberate exclusion; should be its own goal).

## Discuss

- (Resolved 2026-06-10) **#346 issue-body mechanism** — falsified by the
  activation critique; the carrier records the corrected root cause
  (stale Codex rollout in the render path).

## References

- [premerge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
  (canonical), [preflight coverage spec](../charness-artifacts/spec/artifact-shape-preflight-coverage.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
