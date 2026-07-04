# Quality Review
Date: 2026-07-03

## Scope

Target boundary: the 0.59.0 release surface — the gather credentialless-by-default
boundary change plus the `--release` gate readiness of accumulated post-0.58.0 main.

Ambient repo findings: the `./scripts/run-quality.sh --release` gate surfaced three
release-only failures that normal pre-commit does not catch, all pre-existing
accumulated debt rather than the gather change; repaired this session.

## Current Gates

- `./scripts/run-quality.sh --release`: green after the three repairs below (was
  78 passed / 3 failed).
- Standing pytest suite: 3980 passed.
- Pre-commit battery (skill-contracts, staged-mirror-drift, ergonomics, evals): green.

## Runtime Signals

- runtime source: structured runtime-signals timing capture is unavailable this session
  (not refreshed via `render_runtime_summary.py`).
- runtime hot spots: the `pytest` and `check-coverage` gates dominate the release gate
  wall-clock; every other gate is individually cheap.
- coverage gate: run-quality `check-coverage` PASS; changed-line mutation teeth skipped
  non-blocking (stale coverage fingerprint, `command:` suggest_mutation_coverage_command.py).
- evaluator depth: deterministic gates only this session, plus the advisory gather
  claim-fidelity substance floor (`outcome-assertions.json`); no new live Cautilus run.

## Healthy

- Gather boundary change fresh-eye reviewed AND release-critique reviewed (4 angle
  subagents + counterweight); RCF claim-fidelity floors untouched.
- No consumer-facing skill renames/deletes in the release delta; public shape intact.

## Weak

- dup-ratchet baseline drifted: 11 clone `family_id`s rotated by the batched edits
  across 46 commits (the #395 rotation class, deferred-decision D30) — re-baselined.
- One prior quality artifact sat at `latest.md` in a non-`# Quality Review` shape
  (this review replaces it; the audit is retained as a dated artifact).

## Missing

- No repo-owned concept-boundary/ownership checkpoint yet (#414/#416/#408) — folded
  into the reference-compaction sweep plan rather than a standalone spike.

## Deferred

- reference-compaction Slice 7 / #410 (per-skill RCF→RSF sweep) — uncommitted, not in
  this release.
- gather Notion default-`none` has no `advise_notion_path.py`/redirect (declarative
  only); tracked as a follow-up, no regression.

## Advisory

- structural review result: the release-only gate set (`run-quality --release`) is the
  right teeth here because it caught real accumulated debt that pre-commit did not; no
  structural gate change needed.
- prose review result: `skills/public/gather/SKILL.md` + ownership-doc credentialless
  framing corrected to stop over-claiming Google Workspace/Drive (artifact:
  `charness-artifacts/critique/2026-07-03-release-0-59-0.md` F2), because the primary
  operator surface had contradicted the shipped default.
- clone/doc duplication advisories (`command:` inventory-nose-clones) are intentional
  per-skill portability boilerplate (resolve_adapter/scaffold copies) confirmed by family
  membership, accepted into baseline rather than refactored.

## Delegated Review

- Delegated Review: executed — 5 bounded fresh-eye subagents for the release critique
  (Gawande/Minto/Raskin/Weinberg + counterweight), verdict SHIP-after-fixes; artifact
  `charness-artifacts/critique/2026-07-03-release-0-59-0.md`.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not
  re-delegated — no slow-gate scope change this session.

## Commands Run

- `./scripts/run-quality.sh --release`; `pytest -q`; `validate_cautilus_diagnostics.py --all`;
  `validate_quality_artifact.py`; `check_dup_ratchet.py`; `validate_packaging_committed.py`.

## Recommended Next Quality Moves

- active dup-ratchet residual churn — capability_needed=stop conflating D30 (RESOLVED
  2026-06-27, Slice 4) with its still-open residuals; next_center=D30's named residual
  reopen triggers S4-Defer-1 (in-place comment/whitespace edits inside a duplicated
  span still rotate the v1 rstrip-only fingerprint) and S4-Defer-3 (a membership-shrink
  still forces a full re-baseline instead of a reduction diff), plus the accepted-corpus
  shrink lever (refactor down the accepted clone-family baseline count instead of only
  re-accepting more into it); transformation=token/comment-aware normalization for
  S4-Defer-1, a subset-aware reduction diff for S4-Defer-3, or a corpus-reduction pass
  on the largest accepted families; proof_boundary=an in-place comment edit or a
  membership-shrink edit inside a duplicated span no longer forces `--write-baseline`;
  enforcement_posture=advisory.
- passive concept-boundary checkpoint (#414/#416/#408) — no gate yet because it is not
  yet designed; capability_needed=repo-owned producer/consumer boundary discipline;
  next_center=reference-compaction sweep; transformation=extend the existing portability
  checkpoint; proof_boundary=a sample ownership-boundary-violating patch is flagged;
  enforcement_posture=no-gate.

## History

- [test-value audit that drove this suite state](history/2026-07-03-pytest-suite-test-value-audit.md)
