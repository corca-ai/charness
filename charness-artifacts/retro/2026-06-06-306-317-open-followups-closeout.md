# Session Retro: 306–317 open-followups dynamic-workflow goal

Mode: session

## Context

Closeout review of the `2026-06-06-306-316-open-followups` achieve goal: resolve
six open follow-ups (#306, #311, #314, #315, #316, #317) via a sequential dynamic
workflow, then a release. All operator decisions were front-loaded via
`AskUserQuestion` before the goal was shaped; #317 was added mid-shaping by
operator request. Implementation ran as a single dynamic workflow (6 sequential
committed slices + a 4-dimension fresh-eye review + adversarial verify); release
and closeout stayed in the main loop. What matters next: cut the release and
flip the goal complete.

## Evidence Summary

- Workflow result `wdtjjap10`: 6/6 slices landed, `stoppedAt: null`, 0 confirmed
  review findings; commits `a09e6d95`/`ba48808e`/`c688e66c`/`309f7a21`/`4f1adc50`/`bb0ca089`.
- Broad gate runs: first `./scripts/run-quality.sh --release` = 71 pass / 1 fail
  (`test_achieve_root_uses_reference_index_with_core_headroom`); after fix
  `54e1b6b1` = 72 pass / 0 fail.
- Host-log probe (`charness-artifacts/probe/2026-06-06-306-316-open-followups.json`):
  Claude host; token snapshots present, duration/tool-calls derivable; goal
  metric window absent (no ISO `Host metric window:` stamped — thread-wide scope).

## Waste

- **The single real defect slipped past the in-workflow review and was caught
  only by the main-loop broad gate.** The 4-dimension fresh-eye review returned 0
  findings, yet `--release` immediately failed: #316's slice compressed
  `achieve/SKILL.md` to *exactly* the 160 core-nonempty hard limit (0 headroom),
  which `test_achieve_root_uses_reference_index_with_core_headroom` rejects
  (requires ≥4 buffer). The per-slice gate (`run_slice_closeout --predict-commit`)
  excludes broad pytest by design, and the review agents did not run the broad
  suite either — so a deterministic, already-existing test caught a regression
  that no slice-boundary check did. The bundle gate is the *correct* safety net
  and it worked, but the authoring agent satisfied the hard length gate while
  missing the separate headroom-buffer test. This is the #308 authoring-preflight
  lesson recurring on a *different* length surface (SKILL.md core headroom, not
  `check_python_lengths`).
- **Minor:** the #314 slice-spec gotcha I wrote ("scripts/ needs no mirror sync")
  was wrong — `scripts/staged_commit_gate_plan.py` is mirrored to
  `plugins/charness/scripts/`, so the agent had to run the sync. The agent caught
  it and recorded the correction as a non-claim. My recon-derived gotcha was
  repo-inaccurate; the agent's re-verify instruction saved it.

## Critical Decisions

- **Front-loading every decision via `AskUserQuestion` before shaping the goal**
  (the operator's explicit ask) produced a clean autonomous run: zero mid-run
  blockers, `stoppedAt: null`. The decisions also made #317 fold in by
  consistency with the already-made #311 decision, needing no new question.
- **Sequential slice execution (not parallel)** — chosen because #311↔#317 share
  setup files and #315↔#316 share the achieve template. All 6 landed with no
  cross-slice contamination; the stop-on-first-blocker guard never had to fire.
- **Keeping release + closeout in the main loop, not the workflow**, and treating
  the 0-findings review skeptically by running the broad gate myself — this is
  exactly what caught the #316 headroom failure before any irreversible push.

## Expert Counterfactuals

- **Gary Klein (pre-mortem / recognition-primed):** would have asked up front
  "what does the broad gate check that the per-slice gate does not?" — and seeded
  every slice touching a length-gated surface with the matching *buffer* test,
  not just the hard limit. The fix: slices that edit SKILL.md should pre-check
  the headroom-buffer test, since the hard 160 gate and the ≥4 buffer test are
  two different thresholds on the same surface.
- **Don Reinertsen (queue/batch economics):** would note the broad gate is the
  right batch-boundary catch and resist pushing *every* broad test to the commit
  boundary (latency). The targeted improvement is narrow: surface the specific
  per-surface headroom-buffer test at the slice boundary for the handful of
  length-gated authored surfaces, not the whole suite.

## Next Improvements

- **workflow / capability:** the SKILL.md `core_nonempty` headroom-buffer test
  (`remaining ≥ 4`) runs only in the broad gate, not at the commit boundary, so
  authoring a SKILL.md to the hard 160 limit passes the per-slice gate and fails
  late. Generalizes #308 (authoring preflight) and #314 (cheap structural gates
  at the commit boundary) to the SKILL.md core-headroom surface. Disposition:
  filed as a tracked issue (larger than this goal's scope; needs the
  per-slice-cost design the #314/#307 caution flags). → see Auto-Retro
  disposition for the issue number.
- **memory:** recon-derived "gotchas" about which paths are mirrored can be
  repo-inaccurate — `scripts/` is mirrored to `plugins/charness/scripts/`, not
  only `skills/`. The standing "re-verify the brief against real files"
  instruction already absorbed this; no separate gate needed.

## Sibling Search

Transferable pattern: "a per-surface *buffer/headroom* test (distinct from the
hard limit) runs only in the broad gate, so near-limit authoring is caught at the
bundle boundary, not the commit boundary." Four-axis scan:

- **other skills/docs:** every public skill SKILL.md is governed by the same
  `core_nonempty` ≤160 limit + the per-skill headroom-buffer tests — the same
  late-catch applies to any near-limit SKILL.md edit, not just achieve. (the
  filed issue is framed at this general surface, not achieve-specific)
- **other scripts:** `check_python_lengths` warn-bands (advisory) vs hard limits
  are the analogous two-threshold shape for `.py` files; #308's preflight already
  surfaces that headroom — the gap is specifically the SKILL.md core-headroom
  *test* not being in the commit-boundary set.
- **workflow:** the per-slice gate intentionally excludes broad pytest; the fix
  is selective (route the specific cheap headroom-buffer assertion), not "run the
  broad suite per slice."
- **memory/docs:** the authoring-preflight reference (#308) is the natural home
  to note the SKILL.md core-headroom buffer alongside `check_python_lengths`.

Decision: file one tracked issue at the general SKILL.md-headroom surface (not a
trivial local fix; real siblings across all public skills).

## Persisted
