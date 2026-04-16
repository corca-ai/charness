# Issue Closeout Premortem Retro

## Context

This session closed GitHub issues #25-#31 after implementing the local fixes,
running fresh-eye premortem agents, pushing `main`, and closing the remote
issues. The user asked how we could have learned about those issue risks earlier
while working in this repo.

## Evidence Summary

- GitHub issues and comments #25-#31 fetched before final closeout.
- Commits `17efb07` through `04dcf01` on `main`.
- Fresh-eye premortem agents found real gaps in #27 and #31 before close.
- `./scripts/run-quality.sh` and the pre-push hook both passed with
  `37 passed, 0 failed`.
- Earlier retro memory already named the same pattern: run premortem before
  assuming a slice is close-ready.

## Waste

- The first implementation pass worked mostly from issue summaries and local
  intent, not from a full issue body plus comment acceptance matrix. That meant
  follow-up comments on #26, #27, and #31 were discovered late.
- Slice closeout was treated as enough evidence after the tree was clean. For a
  close-readiness decision, the standing gate mattered more than a clean-tree
  no-op closeout.
- Fresh-eye review happened after the seven issue slices were already committed.
  It still caught the blockers, but only after we had created extra cleanup and
  handoff churn.
- The handoff update crossed its own concise limit and was caught only by the
  push hook. That repeated a known class of artifact-size misses.

## Critical Decisions

- Asking for subagent premortem before remote close was the decisive recovery
  point. It found #27's missing init-repo prevention half and #31's runtime/test
  gaps before the issues were closed.
- Running full `./scripts/run-quality.sh` instead of relying on focused tests
  exposed length, plugin import, ruff, and handoff-size failures that would have
  made the closeout untrustworthy.
- Closing only after push-time pre-push passed kept the remote issue state honest:
  the comments reference code that is actually on `main`.

## Expert Counterfactuals

- Gary Klein's premortem lens would have started the issue batch with: "If a
  maintainer reopens this issue after close, which exact acceptance sentence or
  comment did we fail to satisfy?" That would have forced issue comments into
  the acceptance matrix before implementation.
- Atul Gawande's checklist lens would have used a short closeout checklist for
  every issue batch: fetch body and comments, write acceptance rows, run standing
  quality, run fresh-eye premortem, then push and close. The missed steps here
  were checklist-class misses, not deep design uncertainty.

## Next Improvements

- workflow: For multi-issue batches, create a compact acceptance matrix from
  each issue body and all comments before implementation starts. Treat comments
  as first-class acceptance input.
- workflow: Run fresh-eye premortem before the first "ready to close" claim, not
  after all slices are committed.
- workflow: Use full `./scripts/run-quality.sh` for close-readiness, even when
  `run-slice-closeout.py` reports no changed surfaces.
- capability: Add an issue-batch triage helper or checklist that emits
  issue/comment acceptance rows and closeout commands.
- memory: Keep this as a repeat trap in the retro digest: issue closeout is not
  ready until issue comments, standing quality, and fresh-eye premortem have all
  been consumed.

## Persisted

yes: `charness-artifacts/retro/2026-04-16-issue-closeout-premortem.md`
