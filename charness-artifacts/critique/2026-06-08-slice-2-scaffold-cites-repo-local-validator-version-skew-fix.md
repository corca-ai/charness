# Slice 2 — scaffold cites repo-local validator (version-skew fix)
Date: 2026-06-08

## Decision Under Review

Swap the validator-lookup order in all 6 artifact-authoring scaffolds
(`debug`/`critique`/`retro`/`quality`/`handoff`/`ideation` `validator_command`)
to prefer the repo-local `repo_root/scripts/<validator>.py` over the running
script's `__file__`-ancestor (installed/exported plugin) copy, so the cited
check `==` the broad gate and the installed-vs-repo version-skew class is killed.

## Failure Angles

- Repo-local-first could cite a STALE/vendored `scripts/<validator>.py` inside
  `repo_root` over a newer bundled one.
- The swap could regress the consumer-fallback case (a repo with no own
  validator must still cite the installed plugin copy).
- The new test uses an empty stub validator file, so it proves the cited
  command string but not that the cited validator actually runs / differs.
- A consumer of the scaffold payload (e.g. `check_artifact_surface_preflight.py`)
  could break if it depended on the old absolute citation.

## Counterweight Pass

- Stale-vendored-repo-local: NOT a blocker — by design, if a repo owns a
  validator, that file IS the repo's gate; citing the installed copy instead is
  exactly the skew being fixed. The contract is presence/path resolution, not a
  content classifier.
- Consumer fallback: verified preserved — both existing test families pass a
  `repo_root` that does not own the validator, so they still hit the ancestor
  fallback (in-repo → absolute real-repo path; exported → absolute plugin path).
- Stub-only test: faithful enough — the pre-existing exported test already proves
  the cited command RUNS in the fallback case; the actual installed-plugin
  behavioral-difference proof is a stated non-claim deferred to the on-machine
  Slice 4. The new test's precondition asserts the exported tree ships the
  validator, so `str(plugin_root) not in command` is a real regression guard.
- Preflight: verified independent — `check_artifact_surface_preflight.py` builds
  its own command from `surface.validator` and only calls the scaffold for shape
  text, so the swap cannot change preflight citation; its tests stay green.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/public/*/scripts/scaffold_*_artifact.py:validator_command | action: document | note: search-order swap is identical and correct across all 6; verdict-equality on the 15 pre-existing scaffold-test assertions confirmed by the fresh-eye reviewer
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/test_scaffold_repo_local_validator.py | action: defer | note: stub-only citation test does not execute the cited validator; behavioral-difference proof deferred to the on-machine Slice 4 (stated non-claim), and the fallback run-path is already covered by the existing exported tests

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent reviewer (separate agent context), per the goal verification plan's Slice-2 scaffold-skew boundary.
- Requested spawn fields: read-only critique reviewer with the bounded slice packet (intent, changed files + mirrors, expected invariants, non-claims, out-of-scope, reviewer questions); instructed to inspect via git diff/show and read-only test runs only.
- Host exposure state: applied
- Application state: host-confirmed: bounded fresh-eye subagent (general-purpose agent a5ca10ceae751f405) spawned and returned VERDICT: SHIP, no blockers; independently ran the 21-test scaffold suite (pass) + 43 dependent-consumer tests (pass) + the release-only changed-line coverage gate (2 pass).

## Fresh-Eye Satisfaction

SHIP. The fresh-eye reviewer confirmed: the swap fixes the skew and preserves the
consumer fallback; all 6 scaffolds + mirrors are byte-identical with an identical
comment; the regression test's precondition is a genuine guard against the old
ancestor-first behavior; `check_artifact_surface_preflight.py` is independent of
the scaffold's `validator_command` so preflight citation is unaffected. Live
dogfood signal: authoring this very artifact via `scaffold_critique_artifact.py`
emitted the repo-local `python3 scripts/validate_critique_artifacts.py` citation,
demonstrating the fix in the real repo.
