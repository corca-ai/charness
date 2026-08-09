# Critique Review
Date: 2026-08-09

## Decision Under Review

Whether adapter-declared skill paths can be reconciled against the files a
consumer actually owns without resolving ignored files, escaping the declared
root, leaking a configured support directory, or changing trust scope through
a symlink.

## Execution

The slice closeout's Git-ignore hygiene gate first caught the main-repo glob
bug. Two bounded read-only rounds then reviewed the repaired verdict surface;
round 2 read round 1's repairs. Parent-side worktree/index fingerprints verified
both windows clean. The final external-support provenance repair is
accepted-unreviewed under the two-round cap.

## Failure Angles

- File population: exact and wildcard declarations must use tracked and
  non-ignored candidates where Git can establish that population.
- Containment: absolute paths, `..`, and symlink escapes must never earn a
  resolved target.
- Trust scope: a candidate discovered from external support must not become a
  repo-owned result after canonicalization.
- Privacy: external host paths must not appear in the rendered plan.

## Findings

- Closeout found that `Path.glob` resolved ignored main-repo skills. The reader
  now uses the shared Git-aware file-listing seam for exact and wildcard paths.
- Round 1 found non-Git `..` declarations could reach outside the repo,
  absolute patterns could crash, and configured external support had no
  explicit scope policy. Absolute and parent-bearing declarations now carry a
  typed error; canonical containment refuses escapes; valid external support is
  virtualized as `skills/support/...` without an absolute host path.
- Round 2 found external support still bypassed its own Git ignore rules and an
  external-support symlink into an ignored main-repo file could switch scope to
  `repo`. Candidate provenance is now fixed before matching: an external
  support declaration is listed from that support root and can resolve only
  inside its canonical support boundary.
- Exact and wildcard ignored paths in both populations remain unreachable;
  repo and external-support symlink escapes remain partial with an excluded
  match count rather than resolving.

## Counterweight Pass

- Act Before Ship: all three finding classes could render `resolved` for a file
  outside the established population or crash the planner; all were repaired.
- Bundle Anyway: final tests cover ignored exact/wildcard support paths,
  external-support-to-repo laundering, and ordinary repo symlink escape.
- Keep: valid configured support remains a supported, virtualized scope; the
  repair does not ban external support or expose its host path.
- Over-Worry: a general cross-repository provenance framework is unnecessary
  for this one declared-skill-path consumer.

## Deliberately Not Doing

No filesystem-wide scanner, new adapter key space, scheduler change, Cautilus
evaluation, or terminal quality verdict is added.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: quality_declaration_lifecycle.py Git-aware matching | action: fix | note: ignored main-repo exact and wildcard paths stay unreachable
- F2 | bin: act-before-ship | evidence: strong | ref: quality_declaration_lifecycle.py canonical containment | action: fix | note: absolute, parent, and symlink escapes cannot resolve
- F3 | bin: act-before-ship | evidence: strong | ref: quality_declaration_lifecycle.py external-support provenance | action: fix | note: external support obeys its own Git listing and cannot launder a repo result; accepted-unreviewed under cap
- F4 | bin: bundle-anyway | evidence: strong | ref: test_quality_declaration_path_resolution.py | action: document | note: exact, wildcard, provenance, privacy, and symlink counterexamples are pinned in their cohesive owner module

## Reviewer Tier Evidence

- Requested tier: host default for bounded fresh-eye review.
- Requested spawn fields: existing agent context; no model override requested.
- Host exposure state: host-defaulted
- Application state: findings delivered; provider-side model metadata not exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. Both results were delivered and both parent-side boundary
fingerprints returned `verdict: clean`.

Fresh-eye pass: skills/public/quality/scripts/quality_declaration_lifecycle.py —
two bounded rounds found ignored-path, containment, and external-support
provenance false verdicts; all findings were repaired, with the capped round-2
repair accepted-unreviewed.

## Boundary Ownership

- Producer: adapter-declared skill path patterns and the repo/support file
  populations they name.
- Consumer: the quality planner renders resolved, unreachable, or partial rows.
- Owning surface: quality declaration lifecycle owns path reconciliation;
  repo-file listing owns Git-aware population discovery.
- Verdict: owned-correctly

## Next Move

Run the final focused cohort and the full slice closeout, then commit this P2
slice. The path-boundary cases live in a cohesive module instead of pushing the
general planner suite above its code-line limit. No third review is claimed.
