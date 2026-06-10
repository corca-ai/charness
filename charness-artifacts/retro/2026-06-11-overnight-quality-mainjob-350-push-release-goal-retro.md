# Overnight quality main-job + #350 + push/release goal retro
Date: 2026-06-11

## Mode

session

## Context

Closeout retro for
`charness-artifacts/goals/2026-06-10-overnight-quality-mainjob-350-then-push-release.md`
(6h timebox, operator asleep, Claude host): five quality slices (posture
refresh, #350, C2 bootstrap data-loss fix, C4 commit-time handoff pull, C3
scheduled-mutation capacity-advisory reclassification) then the
pre-authorized single push + v0.40.0 release lane. All slices closed inside
~1.5h of wall clock; the lane verified green end-to-end.

## Evidence Summary

- Posture refreshed at v0.39.0+3 staged commits; broad gates repaired
  71/2 -> 73/0 (empty handoff Discuss from bc70d76a; stale retro index);
  ranked candidates C2/C3/C4 scoped slices 3-5 exactly as planned.
- #350 (31dbe3ad, `Closes #350` draft_verified) and #349 (763653c7 from the
  prior goal) both flipped CLOSED — verify-closeout `verified` for each.
- Live bug found AND fixed in-goal: `quality_bootstrap_lib` allowlist
  rewrite dropped `standing_doc_provenance` + `changed_line_mutation_gate`
  (reverted, then aa8670c8 round-trips unknown fields; no-op path restored).
- Scheduled-lane noise engine diagnosed to mechanism (capacity-blocking +
  vacuous-arm auto-close; 47 auto-issue lifecycles) and resolved by
  completing the premerge spec's deferred follow-up (da6b9a8e), with a
  reviewer-traced no-escape safety argument; workflow JS deliberately
  untouched overnight.
- Five bounded fresh-eye reviews (activation plan, posture, three slices) +
  release critique: every verdict ship/ship-with-nits, all blockers zero,
  all foldable nits folded pre-commit.
- Lane: push 768ded84..a7185616; quality-core green on a7185616, 792ffaaf,
  a7d50604; v0.40.0 published + public-verified; install refresh auto-ran;
  live probe installed SHA == origin/main == a7d50604, plugin 0.40.0 == tag.
- Deferred proof consumed at activation with a CORRECTED disposition: the
  768ded84 red run was real-by-design (budget drop), not flake; greens were
  vacuous on the changed-file arm. That correction BECAME slice 5's fix.
- Off-goal: #353 filed (adapter_lib renderer hygiene, three latent defects).

## Waste

- Wrong oracle for the release adapter edit: validated with pyyaml, which
  rejects the file HEAD already shipped (the repo's own tolerant loader is
  the canonical parser); cost two error rounds before checking
  `git show HEAD | pyyaml`. Lesson: validate a repo-owned format with the
  repo's own loader first.
- Slice-log timestamps were written as estimates and drifted ~2.5h fast;
  corrected in a dedicated bundle-boundary commit. `date` at each boundary
  costs nothing.
- First disposition of the red mutation run was "flake" from same-SHA
  greens; reading the workflow's base/seed mechanism flipped it to
  real-by-design within slice 1. Pattern-matching red->green->flake without
  reading the selection mechanism is the trap.
- verify-closeout invoked again with sketched args (third goal running);
  one usage round. The error is loud and self-documenting; cost stays ~30s.
- validate-quality-artifact's 140-line cap took ~6 trim edit rounds because
  trimming and field-engagement requirements interact; the scaffold prints
  the skeleton but not a per-section line budget.

## Critical Decisions

- Reordered C4 before C3 (smaller, deterministic, fully local) — kept the
  diagnose-first slice last where its scope risk was bounded by everything
  else already being committed.
- Slice 5 scoped to unit-testable Python semantics with the workflow JS
  deliberately untouched: a broken workflow edit overnight would generate
  the exact red-run noise the slice existed to remove. The provable
  safety argument (uncovered arm scans the full changed set pre-selection)
  is what made the reclassification shippable without CI rehearsal.
- Reverted the bootstrap adapter rewrite instead of committing it, turning
  an observed mutation into evidence (git diff) and then into C2's fix and
  regression tests.
- Activation critique's "consume the deferred proof NOW" adjustment
  surfaced the corrected disposition early enough to reshape slice 5 — the
  fold-the-critique-early pattern paid for itself.

## Expert Counterfactuals

- An "oracle choice" lens (which parser/validator is canonical for THIS
  file?) would have skipped both pyyaml error rounds; the repo's
  resolve_adapter was one command away.
- A "read the mechanism before dispositioning" lens on CI flaps: the
  base/seed lines in the workflow were 10 lines of reading that inverted
  the flake verdict.

## Sibling Search

- wrong-validation-oracle axis: pyyaml vs repo `load_yaml` (.agents/release-adapter.yaml); same class as validating generated markdown with a generic linter instead of the owning validator | decision: memory destination | proof: HEAD version of the adapter is pyyaml-invalid yet shipped and parsed by every release helper | follow-up: recent-lessons refresh sourcing this retro (no gate change — the repo loader is already the enforced path; pyyaml was an agent-side verification detour)

## Next Improvements

- memory: refresh `charness-artifacts/retro/recent-lessons.md` sourcing
  this retro (repo-loader-as-oracle; date-at-boundary; read-the-mechanism
  before CI-flap disposition).
- capability: adapter_lib renderer hygiene — filed as issue #353.
- workflow: when a quality artifact must satisfy both a line cap and
  field-engagement minima, draft sections against the cap from the start
  instead of trimming post-hoc.

## Persisted

yes: charness-artifacts/retro/2026-06-11-overnight-quality-mainjob-350-push-release-goal-retro.md
