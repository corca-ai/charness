# Critique Review
Date: 2026-08-09

## Decision Under Review

Whether issue #563's advisory title/slug checker behavior and live wiring can be
retired without leaving a shipped consumer asking for its output, weakening
unrelated document reachability, or breaking the installed command path in the
planned minor release.

## Execution

Two bounded read-only reviewers inspected the shared worktree. Round 1 reviewed
the deletion and found three stale consumer instructions. Round 2 read those
repairs and the full surface, then found one live-linked standing-floor audit
that still classified the deleted checker as `keep`. Parent-side reviewer
fingerprints verified clean before either repair. The final audit correction is
accepted-unreviewed under the two-round cap. A later release-safety critique
caught a distinct semver blocker: v4.0.0 installed four callable paths, so their
complete absence would make v4.1.0 incompatible. Deprecated compatibility
copies now preserve those paths and legacy strict/JSON semantics while the
standing gate and public recommendation remain removed.

## Failure Angles

- Completeness: executable, shim, plugin, hook, gate-plan, registry, test, and
  shipped command references.
- Contract: whether the replacement judgment tells a reviewer what to inspect
  without inventing a deterministic clean result.
- History versus live policy: whether dated evidence stays honest while a live
  audit can still direct future work toward the retired mechanism.
- Counterweight: whether another doc-link or graph surface already owns the
  mechanical parts that must remain.

## Findings

- Round 1 found `rename-critique.md` still proposed future pre-push wiring and
  required `Slug Drift Result`; `critique/SKILL.md` still named slug-drift
  evidence. They now require inspected paths, H1/filename comparison,
  incoming-link/generated-index evidence, first-reader friction, and no
  aggregate clean verdict.
- Round 2 confirmed all active checker and plugin copies were absent, the
  docs-only set was exactly 13, and mirrors were byte-identical. It found
  `closeout-floors.md`, linked from the implementation discipline, still saying
  the checker was a low-false-fire `keep`. The row now records #563 as its
  superseding correction without erasing the historical decision.
- Dedicated heuristic tests were deleted; unrelated portable-path, doc-link,
  docs-graph, staged-plan, packaging, and critique-contract coverage remains.
- Release critique found that deleting the installed invocation paths changed
  existing automation expectations and therefore required either a major bump
  or compatibility. The four restored entrypoints accept the former CLI shape,
  preserve advisory exit 0 and strict 0/1 behavior, and keep the legacy
  `checked`/`drift` JSON fields while labeling the surface `deprecated`. The
  issue's scope defect is repaired by including `charness-artifacts/goals` in
  the default population. They are not wired back into any gate or public
  recommendation; a later major release owns complete removal.

## Counterweight Pass

- Act Before Ship: stale executable-output instructions and the live `keep`
  classification contradicted the deletion and could cause reintroduction.
- Bundle Anyway: the focused output-shape assertion was added beside the public
  contract repair.
- Over-Worry: a permanent repo-wide ban on the deleted token would add a new
  meta-gate for a one-time deletion; residual search plus current contract tests
  are proportionate.
- Keep: title/slug coherence remains a bounded first-reader judgment, while link
  validity and graph reachability stay owned by their existing gates.
- Keep: the deprecated compatibility copies preserve a minor-release invocation
  surface without restoring standing execution or public recommendation.

## Deliberately Not Doing

No replacement word-overlap heuristic, transliteration rule, new blocking floor,
scheduler change, or Cautilus evaluation is included. Historical artifacts may
name the old checker when they are clearly records rather than live directions.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/critique/references/rename-critique.md | action: fix | note: retired deterministic output and future wiring removed
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/critique/SKILL.md | action: fix | note: output contract now names title/slug coherence review evidence
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/audit/closeout-floors.md | action: fix | note: live keep call superseded by #563; accepted-unreviewed under cap
- F4 | bin: over-worry | evidence: moderate | ref: repo-wide deleted-token floor | action: defer | note: active wiring is absent; compatibility paths are intentional
- F5 | bin: act-before-ship | evidence: strong | ref: release version policy and v4.0.0 installed tree | action: fix | note: retain deprecated direct-call compatibility with corrected goal-record scope so v4.1.0 does not remove or silently neuter an installed command

## Reviewer Tier Evidence

- Requested tier: host default for bounded fresh-eye review.
- Requested spawn fields: existing agent context; no model override requested.
- Host exposure state: host-defaulted
- Application state: findings delivered to the parent; provider-side model
  metadata was not exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. Both bounded reviewer results were delivered, and both
parent-side reviewer-boundary fingerprints returned `verdict: clean`.

## Boundary Ownership

- Producer: critique references produce the rename-review questions.
- Consumer: installed agents read those references and render per-concept
  evidence.
- Owning surface: link gates own mechanical resolution/reachability; critique
  owns semantic title/slug coherence judgment.
- Verdict: owned-correctly

## Next Move

Validate active-wiring absence, deprecated compatibility CLI behavior,
packaging parity, and the release critique repair before publication. The repair is
release-boundary review, not a third verdict-logic round over the deleted
heuristic.
