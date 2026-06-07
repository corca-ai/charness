# Session Retro — #325 provenance policy + handoff-3 gate capability

## Mode

session

## Context

Pursued the merged `/goal`
(`2026-06-07-325-provenance-policy-handoff3-gate-capability`): #325
(provenance-placement policy + portable standing-doc check + dogfood sweep +
closeout-checkpoint broadening) and handoff-3 (changed-line mutation gate as a
portable `quality` capability + adapter). Six slices, two commits
(`7e931999` Close #325 staged, `0f97effb` handoff-3), two bounded fresh-eye
critiques. Next: maintainer push (issue stays OPEN); release surfaces untouched.

## Evidence Summary

- Host-log probe (`probe_host_logs.py --format markdown`): 429 function calls,
  149 custom tool calls, 139 patch applications, 4 subagent spawn / 3 wait,
  git status x26. Thread-wide (no per-goal window configured).
- Two `run_slice_closeout.py --verification-lock` broad runs (one per bundle),
  both green; two critique artifacts under `charness-artifacts/critique/`.

## Waste

- **Serial validator discovery behind the broad closeout (dominant).** After the
  cheap aggregate passed, the `--verification-lock` closeout surfaced
  portable-surface validator failures ONE AT A TIME across ~7 fix then re-run
  cycles: `check_doc_links` (bare path to markdown link), `check-markdown`
  (wrapped inline code span), `validate_skills` (author-repo cite),
  `check_skill_ownership_overlap` (`retro/` token in a docstring),
  `validate_attention_state_visibility` (`skipped` term undeclared),
  `validate_skill_ergonomics` (issue anchors in package scripts), then `ruff`
  (import sort). This is the recent-lessons repeat trap "serial discovery behind
  a gate" — each discovery cheap, but paid serially. Most were predictable from
  the skill-package authoring constraints.
- **Authoring-preflight skip for new skill-package files.** I authored new
  `skills/public/quality/scripts/*.py` + `references/*.md` without first running
  `check_skill_surface_preflight.py` / skimming `authoring-preflight.md`, so the
  issue-anchor / dated-incident / author-cite / attention-state-declaration
  constraints bit after the fact — the #308-class trap already in recent-lessons.

## Critical Decisions

- **Enforcement surface = `quality` capability via the adapter** (vs a repo-root
  linter). Made BOTH #325's check and handoff-3's gate genuinely inheritable
  (the portability mandate), reusing the seam consuming repos already install.
- **Masking sanctioned placements** (inline-code, markdown link targets, slash
  path tokens) in the standing-doc check. Turned a 20-finding over-firing check
  into a precise one with 0 false positives on the swept corpus — exactly the
  plan-critique "over/under-fire" seed.
- **Two commits, not one** (#325 issue-close boundary vs handoff-3 internal),
  each with its own fresh-eye critique. Kept the `Close #325` closeout clean.

## Expert Counterfactuals

- **Gary Klein (pre-mortem / recognition-primed decision).** Before authoring a
  new skill-package surface, run a 2-minute pre-mortem: "which known gates will
  this trip?" The skill-package gate set (ergonomics anchors/dates, author-cite
  portability, attention-state declaration, ownership-overlap, doc-links
  pathy/wrapped, markdown) is a KNOWN, enumerable set. Recognizing the pattern
  up front would have batched ~7 serial discoveries into one preflight pass.
- **Counterweight.** Not all serial discovery was avoidable: `ruff` import-sort
  and the mirror sync only exist post-edit, and broad pytest genuinely must run
  last. The avoidable share is the skill-package-specific gates, which a
  preflight batch covers.

## Next Improvements

- **workflow:** When a slice adds NEW skill-package files (`skills/public/*/scripts`
  or `references/*`), run the portable-surface validator BATCH upfront — before
  the first broad closeout — in one pass: `validate_skills`,
  `validate_skill_ergonomics`, `check_skill_ownership_overlap`,
  `validate_attention_state_visibility`, `check_doc_links`, `check-markdown`,
  `ruff`. Collapses the serial fix/re-run loop into one detection round.
- **capability:** Extend `check_skill_surface_preflight.py` (or a sibling) to
  run the portable-package gate set as a single pre-author/pre-closeout tripwire
  that reports ALL findings at once — its current scope missed attention-state
  declaration coverage, ownership-overlap, and author-repo cites together.
  Disposition: scope-extension comment posted to the existing `issue #328`
  (authoring-preflight prose-pin pre-check) recording these additional gates on
  the destination, so a future build covers the whole set.
- **memory:** this retro + the recent-lessons digest carry the recurrence.

## Sibling Search

- Pattern: **serial discovery behind a gate** for slices adding gated surfaces.
  Transferable (recurs for any skill-package / docs / export slice). Four-axis
  scan: it already recurs across the producer-rerun retro (mutation gate) and now
  the skill-package surface; the general fix is "batch the relevant validators
  upfront, keyed off the changed-surface class." Decision: **recurrence of an
  existing tracked lesson** (recent-lessons "serial discovery behind a 6-min
  gate" + "authoring-preflight skip"); boost, do not file a new issue. The
  concrete capability gap is tracked under `issue #328`.

## Persisted

yes — `charness-artifacts/retro/2026-06-07-325-h3-provenance-gate-capability.md`
(recent-lessons digest + lesson-selection-index refreshed; committed in the goal
closeout commit).
