# Retro: Reviewer Tier, #275, and #276 Closeout

Mode: session
Date: 2026-06-01
Persisted: yes `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`

## Context

This session continued the reviewer-tier closeout goal, added #276 at the
operator's request, fixed the #275 installed plugin layout regression, and added
an achieve activation-discussion gate for #276.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-01-reviewer-tier-closeout-and-issue-275.md`
- Issue closeout carrier:
  `charness-artifacts/issue/2026-06-01-reviewer-tier-275-276-closeout.md`
- Resolution critique:
  `charness-artifacts/critique/2026-06-01-reviewer-tier-275-276-resolution.md`
- Final broad pytest: `1973 passed, 4 skipped in 270.06s`
- Changed-surface validators all passed after final sync.

## Waste

- Broad pytest was rerun before a later metadata change was mirrored into the
  plugin export, producing avoidable packaging-drift failures in installed-CLI
  tests.
- #276 was added mid-closeout after #275 broad verification had already passed,
  forcing another full verification cycle. This was correct for scope, but it
  made the late-stage verification cost explicit.

## Critical Decisions

- Treat #276 as a true second bug-class issue, not a note under #275.
- Keep #275's fix local to handoff issue/achieve sibling resolution rather than
  designing a broad cross-skill resolver in the same carrier.
- Add `goal_artifact_discussion.py` as a leaf helper so
  `goal_artifact_lib.py` stayed under the hard length limit.
- Honor the goal's no-push boundary: prepare a local closeout carrier with
  close keywords, but do not claim GitHub issue closure.

## Expert Counterfactuals

- Gary Klein premortem: would have asked "what final gate can still invalidate a
  green broad run?" and forced plugin-sync validation after every metadata edit,
  not only after source skill edits.
- Jef Raskin discoverability lens: would have separated "structurally shaped"
  from "operator-ready" in the first #276 design sketch, avoiding any wording
  that implied hidden defaults were acceptable if markdown headings existed.

## Next Improvements

- workflow: after any metadata file under `skills/public/quality/references/`
  changes, run `sync_root_plugin_manifests.py` before broad pytest, even if the
  change appears unrelated to packaging.
- capability: add a small changed-surface note or validator hint for
  attention-state metadata edits that says plugin export sync is required.

## Sibling Search

Transferable pattern: source/runtime topology and structural-readiness checks can
look green while the operator-visible contract is wrong.

- Same-class fixed now: handoff-to-issue installed layout, handoff-to-achieve
  installed layout, and achieve `--pursue-ready` operator discussion readiness.
- Same-class deferred: broader cross-skill resolver unification and support-skill
  topology helpers. These were outside #275/#276's acceptance boundary.

## Persisted

yes `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`
