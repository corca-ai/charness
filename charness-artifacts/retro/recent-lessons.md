# Recent Retro Lessons

## Current Focus

- This session closed GitHub issues #25-#31 after implementing the local fixes, running fresh-eye premortem agents, pushing `main`, and closing the remote issues.

## Repeat Traps

- The first implementation pass worked mostly from issue summaries and local intent, not from a full issue body plus comment acceptance matrix. That meant follow-up comments on #26, #27, and #31 were discovered late.
- Slice closeout was treated as enough evidence after the tree was clean. For a close-readiness decision, the standing gate mattered more than a clean-tree no-op closeout.
- Fresh-eye review happened after the seven issue slices were already committed. It still caught the blockers, but only after we had created extra cleanup and handoff churn.
- The handoff update crossed its own concise limit and was caught only by the push hook. That repeated a known class of artifact-size misses.

## Next-Time Checklist

- workflow: For multi-issue batches, create a compact acceptance matrix from each issue body and all comments before implementation starts. Treat comments as first-class acceptance input.
- workflow: Run fresh-eye premortem before the first "ready to close" claim, not after all slices are committed.
- workflow: Use full `./scripts/run-quality.sh` for close-readiness, even when `run-slice-closeout.py` reports no changed surfaces.
- capability: Add an issue-batch triage helper or checklist that emits issue/comment acceptance rows and closeout commands.
- memory: Keep this as a repeat trap in the retro digest: issue closeout is not ready until issue comments, standing quality, and fresh-eye premortem have all been consumed.

## Sources

- `charness-artifacts/retro/2026-04-16-issue-closeout-premortem.md`
