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

- **v0.27.0 shipped** (tag `v0.27.0`, release verified; `origin/main` even).
- **CLOSED this cycle:** #322 (advisory-interpretation contract), #328 (preflight
  phase coverage), #331 (closeout matcher idiom), #330 (interpretation
  meta-validator), #329 (retro disposition-form floor) — detail in their
  critiques/retros under `charness-artifacts/`.
- **#332 done, awaiting push** (commit-boundary sweep non-discretionary): the full
  closeout now runs the cheap structural sweep FIRST (before
  surface-match/cautilus/broad pytest); `Close #332` staged on `9f2b9005`; a
  follow-up `applied` added function-length headroom to `--headroom`. Closeout:
  [critique](../charness-artifacts/critique/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md),
  [retro](../charness-artifacts/retro/2026-06-07-issue-332-commit-boundary-sweep-enforcement.md).
- **run_slice_closeout split done, awaiting push** (behavior-preserving): the
  reporting/printing block moved to a new
  [slice_closeout_reporting](../scripts/slice_closeout_reporting.py) module;
  `run_slice_closeout.py` 474→370/480 (110 headroom). Mirror byte-synced. Proof:
  byte-identical move + old-vs-new renderer equivalence battery + 73/0 read-only
  gate. Closeout:
  [goal](../charness-artifacts/goals/2026-06-08-run-slice-closeout-module-split.md),
  [critique](../charness-artifacts/critique/2026-06-08-run-slice-closeout-reporting-extraction.md).
- Open issues (`gh`): **#184** (product metrics); **#332** OPEN until push.

## Next Session

- **Push the staged #332 closeout** (maintainer; `achieve` does not push): 5
  commits in `origin/main..HEAD` carry `Close #332`, auto-closing it; the pre-push
  broad gate is the attestation. Optional pre-push: run the mutation-coverage
  producer (`--verification-lock --produce-mutation-coverage`) so the changed-line
  gate activates on the touched mutation-pool files.
- ~~`follow-up:run-slice-closeout-module-split`~~ — **DONE** (2026-06-08): reporting
  block extracted to `slice_closeout_reporting.py`; file now 370/480. Awaiting push.
- **#184** (product metrics) — product-level; needs `ideation`/`spec`, not a slice.
- **v0.27.0 human real-host smoke** (release left open; agent cannot do):
  `charness update` on a clean temp-home + the nose checklist in
  [release latest](../charness-artifacts/release/latest.md).

## Discuss

- **No push/tag CI.** The local `--release` gate is the bundle proof. Open: add
  light push/tag CI and/or mirror the changed-line gate into a CI-PR check (spec
  "Deferred Decisions").

## References

- [premerge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
  (canonical; Slice 2 delivered, freshness identity, portability follow-up),
  [release v0.25.0 critique](../charness-artifacts/critique/2026-06-07-release-v0-25-0.md)
- [nose-clone interpretation (#322)](../charness-artifacts/quality/2026-06-06-nose-clone-interpretation.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
