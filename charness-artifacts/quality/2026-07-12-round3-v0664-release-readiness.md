# Quality Review
Date: 2026-07-12
Title: Round 3 v0.66.4 Release Readiness

## Scope

Target boundary: the `v0.66.3..HEAD` release candidate: sync/verify phase
ownership, mutation-coverage producer-to-consumer handoff, aggregate quality
runtime observability, and test-module ownership.

Ambient repo findings: Python warn bands, skill host-reference heuristics, and
stale noncritical timing labels were reviewed as advisories. They do not
describe regressions in the target delta.

## Current Gates

- Focused behavior: 69 sync/coverage contract tests, seven quality-runner
  aggregate regressions, and five moved coverage-selection scenarios passed.
- Surface integrity: source/plugin byte parity, packaging, surface, skill,
  bootstrap-shim, upstream-drift, secret, and supply-chain checks passed.
- Repo quality: `./scripts/run-quality.sh --read-only` passed 81/81 emitted
  packets before the final clean-HEAD verification lock.
- Maintainer-Local Enforcement: healthy — `.githooks/pre-push` runs the
  repo-owned quality gate and `validate_maintainer_setup.py` proves this clone
  uses the checked-in hooks path.

## Runtime Signals

- runtime source: structured metrics from
  `.charness/quality/runtime-signals.json`, rendered by
  `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: read-only aggregate 61.9s latest / 63.8s median against
  90s; pytest 42.4s / 36.8s against 140s; coverage 6.8s / 7.4s against 55s.
- coverage gate: the prior read-only run passed with a nonblocking stale-source
  advisory; exact-base production and strict reuse are reserved for the final
  clean-HEAD verification lock.
- evaluator depth: deterministic gates only. No public prompt/skill behavior
  changed, Cautilus reported not-required, and execution is ask-before-run.

## Healthy

- Concept: the manifest owns phase assignment, the mutation producer owns
  resolved facts, and the existing consumer retains verdict semantics.
- Behavior: dirty sync cannot start verification; successful production emits
  exact base/path plus a copyable strict-reuse command whose test proves the
  coverage source is neither recollected nor rewritten.
- Operability: unfiltered quality runs now emit mode-specific aggregate timing
  best-effort without replacing the primary gate exit status.
- Portability/security: source and installed plugin mirrors are identical; the
  consumer command separates executable install root from target repo root;
  secret and supply-chain checks passed.

## Weak

- Thirteen ambient Python files remain in advisory length bands after the
  cohesive quality-runner test split removed that touched module from the band.
  This is navigation pressure, not a release correctness failure.
- Several noncritical component timing labels are 23–51 days stale. The newly
  added aggregate signal is current; no release decision depends on the stale
  labels.

## Missing

- none for the local release candidate. Public visibility, fresh-checkout
  behavior, install refresh, and unauthenticated HTTPS readback are owned by
  the publication boundary and remain provisional until executed.

## Deferred

- Issue #436 stays open for an exhaustive all-writer audit; this release claims
  only the observed SLOC writer was moved to sync ownership.
- Issue #433 stays open by user boundary even though the carrier preflight
  behavior was already fixed in `041aa380`; tracker lifecycle is not bundled.

## Advisory

- structural review result: command: `plan_quality_run.py` — the needed
  capability is cheaper exact-bundle
  confidence. Existing manifest, producer, consumer, and quality-runner centers
  were strengthened at their owning seams; no new floor or public CLI is
  recommended.
- prose review result: command: `inventory_skill_ergonomics.py --summary`
  scanned 22
  packages and found 17 host-reference heuristics (85 references), with zero
  core overfill, mode pressure, path ambiguity, issue/date anchors, or missing
  references. No skill changed; the hits are intentional adapter/integration
  vocabulary, not evidence of target portability failure.
- artifact: the round-three goal Slice 6 records three independent read-only
  probes that found no additional code candidate in
  portability or proof economics; the operator probe found only stale handoff
  semantics, scheduled for closeout refresh.
- artifact: commit `0d130dd1` intentionally regenerated
  `retro/lesson-selection-index.json` after adding two round-two retro sources
  (311→313 sources, 1394→1401 candidates, date-weight recomputation). Its large
  diff is generated lifecycle state already present on `origin/main`, not an
  unreviewed runtime or release mutation from this campaign.

## Delegated Review

- Delegated Review: executed — bounded reviewers approved the code slices and
  test move after concrete HOLDs were fixed; reviewer-boundary fingerprints
  reported zero drift. Invalid nested/unauthorized attempts were quarantined.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): executed — a separate proof-economics probe found no
  redundant standing cost; the final broad proof remains necessary.

## Commands Run

- focused pytest packets — 69 sync/coverage tests, seven aggregate regressions,
  and five coverage-selection scenarios passed.
- `./scripts/run-quality.sh --read-only` — 81 passed, zero failed, 61.9s.
- `render_runtime_summary.py --repo-root . --json` — current aggregate/component
  timings and six excluded stale labels.
- `inventory_skill_ergonomics.py --repo-root . --summary` — 22 packages,
  17 ambient host-reference findings; prose-reviewed above.
- `validate_maintainer_setup.py --repo-root .` — checked-in hook setup validated.

## Recommended Next Quality Moves

- active final-release-proof — capability_needed=bind confidence to the exact
  published bytes; next_center=verification lock; transformation=reuse existing
  mutation, broad pytest, release, fresh-checkout, and public readback paths;
  proof_boundary=clean HEAD plus unauthenticated HTTPS/install readback;
  enforcement_posture=existing-gate-reuse.
- passive ambient-warn-band review because no target escape or imminent hard
  limit remains — capability_needed=maintain navigable ownership;
  next_center=the next changed warn-band file; transformation=defer-watch;
  proof_boundary=observed cohesion failure or touched-file pressure;
  enforcement_posture=no-gate because the current advisory already surfaces it.

## History

- [prior pytest test-value audit](history/2026-07-03-pytest-suite-test-value-audit.md)
