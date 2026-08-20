# Consumer Validator Catalog and Quality-Race Debug Review
Date: 2026-08-21

## Problem

The #670 repair slice exposed several failures while adding a packaged
consumer-validator catalog, explicit adoption decisions, source/installed path
handling, and a safer quality-run temporary boundary. The failures included
wrong command paths, a fail-open inventory result, an unowned adoption file, a
cache eviction race, a relative temporary path race, and a dirty-worktree
changed-line mutation refusal.

## Correct Behavior

Every validator or validator-like path must have one explicit catalog decision;
every consumer-facing entry must expose stable metadata and exactly one
`wired: true` or non-empty `opt_out_reason` decision. Source and installed
layouts must resolve their own catalog and package roots. The inventory CLI must
return a non-clean status when the adoption contract is missing or invalid.
Quality subprocesses must receive one absolute temporary base outside the repo,
and changed-line mutation proof must refuse rather than claim coverage over
uncommitted mutation-pool files.

## Observed Facts

- The first quality run failed because `TMPDIR=.charness/tmp` did not exist;
  after creation, xdist workers resolved it from temporary checkouts and failed
  `mktemp`.
- The same repo-local temporary tree was visible to git population scans and
  cleanup, producing transient `Cannot stat` and `FileNotFoundError` failures.
- Seed-cache tests exposed a cross-hash prune/acquire TOCTOU race; a root prune
  lock plus a cross-hash multiprocess regression removed the race class.
- Standing pytest then failed because the new
  `.agents/consumer-validator-adoption.yaml` had no owning `.agents/surfaces.json`
  surface. Registering a dedicated consumer-validator surface made the exact
  closeout readiness test pass.
- Dup-ratchet first found a duplicated source/installed layout branch. A shared
  `_layout_relative` helper removed that structural duplicate; the remaining
  independent CLI lifecycle families were classified with explicit rationale.
- The final read-only quality rerun passed 96 checks, but changed-line mutation
  returned `status: blocked` because five mutation-pool files were uncommitted.
  It listed blocking lines in `scripts/check_consumer_validator_catalog.py`.
- Wrong or unavailable calls included nonexistent critique/debug scaffold paths,
  the wrong mirror checker name, source-layout paths passed to the exported
  checker, a doubled plugin path, a nonexistent attention-state validator
  path, and a positional debug-artifact path passed to a `--paths` CLI. The
  last call was rejected by argparse; the corrected flag form passed. Correct
  paths were found before treating any result as proof.

## Reproduction

Focused catalog and capability tests pass after repair:

`python3 -m pytest -q tests/test_consumer_validator_catalog.py tests/test_capability_catalog.py tests/charness_cli/test_codex_cache_refresh.py tests/quality_gates/test_packaging_validation.py tests/quality_gates/test_staged_commit_gate_plan.py`

The final focused receipt was `161 passed`. The read-only quality command was:

`TMPDIR=/tmp ./scripts/run-quality.sh --read-only`

Its receipt was `96 passed, 1 failed`; the failure was dirty-worktree mutation
refusal, not an analyzed-code verdict.

## Candidate Causes

- Invocation cause: callers inferred paths from skill names or source layout
  instead of resolving the owning root.
- Contract cause: the catalog and adoption declaration were treated as
  descriptive metadata without a fail-closed consumer readback or staged
  ownership check.
- Concurrency cause: workers shared relative temporary paths and cache-prune
  state without serialized ownership.
- Integration cause: a new top-level contract file was added without entering
  the closeout surface registry.
- Proof cause: mutation coverage was requested before the semantic candidate
  was committed, so a clean result would have silently omitted changed files;
  one validator call also used the wrong CLI shape.

## Hypothesis

The failures are one recurring class: a boundary accepted a name, path, CLI
shape, or state observation without binding it to the owning root and the
evidence channel that makes the observation complete. Disconfirmer: run the source and
installed checker defaults, fail the CLI on a missing adoption declaration,
run the closeout readiness test, and run mutation proof after a commit that
contains the mutation pool. If any succeeds while the relevant owner is absent,
the hypothesis is false and the responsible boundary remains under-specified.

## Verification

- Source checker default: pass with source catalog/package-root resolution.
- Exported checker default: pass with installed catalog/package-root resolution.
- Catalog readback: 133 packaged validators, 133 decisions, 14 consumer-facing,
  119 excluded, 13 declared wired, and 1 explicit opt-out.
- Missing/invalid repo-root calls now return structured nonzero results rather
  than a traceback or clean status.
- `.agents/surfaces.json` now owns the adoption declaration and its checker,
  catalog, mirror, and focused verification commands.
- Retry boundary fingerprint: `verdict: clean`, `drift: []`.
- Fresh-eye round 1 returned BLOCK and its repairs are recorded. Round 2 and
  its unnamed retry did not deliver a final report; no fresh-eye PASS or BLOCK
  is claimed.

## Root Cause

The implementation lacked one shared ownership pattern: path-bearing contracts
were not consistently resolved through their owning root, and new contract
files were not required to register a closeout owner. A relative temporary base
crossed subprocess cwd boundaries, while mutation proof was invoked before the
commit boundary.

## Invariant Proof

- Invariant: a consumer-validator result is trustworthy only when catalog,
  package root, adoption declaration, and staged ownership agree.
- Producer proof: the checker validates source and installed layouts, exact
  invocation tokens, catalog completeness, adoption cardinality, and optional
  index presence.
- Final-consumer proof: the capability CLI exposes detailed entries and returns
  nonzero for a blocked catalog; the quality runner invokes the required
  adoption check.
- Concurrency proof: the seed-cache cross-hash multiprocess test and absolute
  external TMPDIR boundary cover the two observed race shapes.
- Non-claims: no installed cache update, hosted release, public publication,
  GitHub issue closure, Cautilus evaluation, or runtime proof that every
  declaration marked wired is actually called is established here.

## Detection Gap

The first quality run showed standing pytest, closeout ownership, and mutation
proof observing different parts of one contract. No structural owner tied the
new `.agents` declaration to closeout verification, and mutation could start
against a dirty candidate. The dedicated surface and commit-before-mutation
sequence close those gaps at their owners.

## Sibling Search

- Mental model: a path-bearing command is a typed owner reference, not a string
  that can be copied between source and installed layouts.
- Shared helper axis: `_layout_relative` | source/installed root probe | exact
  checker readback; this is now shared inside the checker rather than repeated
  as two branches.
- Cross-file: catalog, adoption declaration, capability CLI, quality runner,
  staged gate plan, `.agents/surfaces.json`, and plugin export must move as one
  contract family. Independent CLI verdict surfaces remain local because their
  schemas and refusal semantics differ.

## Seam Risk

- Interrupt ID: consumer-validator-catalog-quality-races-2026-08-21
- Risk Class: repeated-symptom
- Seam: source path or temporary base -> child cwd/cache -> verifier verdict
- Disproving Observation: source and installed direct checker readback pass,
  but mutation proof remains blocked until the current changes are committed.
- What Local Reasoning Cannot Prove: fresh-eye correctness (delivery failed),
  installed managed-cache readback, hosted/public release behavior, and runtime
  semantics behind declared wired entries.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: commit the semantic repair candidate, rerun changed-line mutation
  and full quality, then bind a delivered fresh-eye review before release or
  goal closeout.
- Handoff Artifact: `charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md`

## Prevention

Keep a single root-resolution helper for source/installed path contracts, make
every new contract file enter `.agents/surfaces.json` in the same change, reject
relative repo-local TMPDIR at the quality-run boundary, serialize cache prune
ownership, and require commit-before-mutation. Treat wrong paths and unavailable
review calls as first-class failure smells with durable evidence, not as noise
around the eventual green command.
