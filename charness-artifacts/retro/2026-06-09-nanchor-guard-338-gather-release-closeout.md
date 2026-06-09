# Session Retro — next-queue goal (#N-anchor guard + #338 gather + charness-update closeout)

Mode: session
Goal: charness-artifacts/goals/2026-06-09-nanchor-guard-338-gather-release-update.md

## Context

One `achieve` goal cleared the operator-selected next queue in three
independent, per-slice-closed-out slices: (1) **#N-anchor edit-time guard**
(`scripts/skill_issue_anchor_scan.py` + `check_skill_surface_preflight.py
--scan-issue-anchors`), (2) **#338** gather X/Twitter exact-source
(`twitter_exact_source.py` identity-keyed route + `source_identity` answer-path
verdict, `Closes #338`), (3) **charness-update release-closeout** — verification
that the standing step already shipped (v0.29.0 to v0.30.1) + stale-handoff fix.
Each slice: cheap deterministic checks at commit + a fresh-eye critique (all
SHIP); bundle-boundary broad gate + changed-line mutation producer green
(ok:True, 0 uncovered changed lines, blocking empty).

## Evidence Summary

Commits 7204940d, 40e492ed, 5c20547f, f99e361c over base 81f2e1ab; three
fresh-eye subagent critiques (SHIP); the changed-line mutation producer (full
verify suite PASS, broad pytest green); test_twitter_exact_source.py (19),
test_skill_issue_anchor_scan.py (16), test_release_publish_resilience.py (20).
No host-log metric window was set on the goal, so efficiency below is proxy-based
(gate round-trips), not measured token/time.

## Waste

- **#338 closeout-draft contract discovery (4 round-trips).** The
  `validate-closeout-draft` contract was learned incrementally: missing
  resolution_critique, then a critique artifact missing a `tool signal:`, then a
  wrong carrier-body source (for direct-commit the body is the COMMIT MESSAGE,
  not --body-file), then missing feature ledger fields. An author-time preflight
  listing the required closeout-draft shape would have collapsed these to one pass.
- **Slice-2 commit gate round-trips.** Two aborted commits: attention-state
  vocabulary (`disabled`/`skipped` literals in a new module) and the
  boundary-bypass ratchet (a new gather-subprocess test). Both are the
  authoring-preflight class, surfaced late at the commit boundary.
- **Slice-3 stale-handoff investigation.** The goal was shaped around a handoff
  to-do (make charness update a standing release-closeout step) that had ALREADY
  shipped (v0.29.0 to v0.30.1). Time went to confirming it was done rather than
  building it; the to-do had been carried across sessions without reconciling
  against the implementation.
- **Handoff conciseness floor.** A verbose slice-3 handoff edit pushed the file
  past its 70-line floor, failing the broad gate (one fix round-trip).

## Critical Decisions

- **Slice 1: extract a new module rather than bloat the preflight.** Inlining hit
  471/480 NEAR-LIMIT; extraction kept both files healthy (fresh-eye SHIP).
- **Slice 2: implement the real syndication/oEmbed exact-source route** (not just
  honest-stop) with a hard identity gate, and keep live fetch operator-gated.
  Folded the fresh-eye finding that oEmbed echoes the URL (require a rendered body
  so a deleted post cannot verify) in this slice.
- **Slice 3: refuse to manufacture work.** Recognized the deliverable pre-existed
  and that a deterministic installed==repo check would be redundant (repo HEAD is
  normally ahead of the last release); corrected the stale handoff instead. A
  fresh-eye reviewer independently confirmed this was honest, not a dodge.

## Expert Counterfactuals

- **Gary Klein (pre-mortem / recognition-primed):** before treating a handoff
  to-do as work, run a 60-second "is this already shipped?" check against the
  owning adapter/helper/release notes. For slice 3 that check would have surfaced
  `post_publish_install_refresh` immediately and reframed the slice as
  verification from the start.
- **Authoring-preflight lens (the repo's own #284 to #334 thesis):** the same
  "learn the gated shape at author time, not at the boundary" idea the repo
  applies to critique/retro/goal artifacts is NOT applied to the GitHub issue
  closeout-draft contract, so it was rediscovered by round-trips.

## Next Improvements

- **workflow:** before acting on a handoff Next-Session to-do, reconcile it
  against the actual repo/adapter/release state; a carried-forward to-do can be
  already shipped.
- **capability (recommend to operator, not auto-filed):** an author-time
  issue-closeout-draft preflight (the required resolution_critique + `tool
  signal:` + carrier-body source + classification ledger fields), the sibling of
  `check_artifact_surface_preflight` for the GitHub-issue closeout surface. Same
  authoring-preflight class as #284 to #334.
- **memory:** the #N-anchor recurring trap now has the edit-time surface its prior
  accepted-risk disposition recommended; upgrade the recent-lessons entry from
  accepted-risk to applied.

## Sibling Search

Transferable waste named: **closeout-draft contract learned by round-trips**.

- axis (surface): the GitHub-issue closeout-draft (`validate-closeout-draft`) has
  no author-time shape preflight, unlike the 7 artifact surfaces
  `check_artifact_surface_preflight` already covers.
- axis (workflow): the achieve/issue closeout path surfaces required fields only
  at validation time, not author time.
- decision: **recommend-to-operator** — a genuine recurring-class sibling, but
  outward-facing and out of this goal's non-goal scope (do not take on other
  tracked issues). Recorded here + in handoff for an operator decision; not
  auto-filed.

## Persisted

(stamped by persist helper)
