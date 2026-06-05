# Retro: inventory_* conversions + nose 0.5 + release 0.21.0

Date: 2026-06-05
Mode: session

## Context

Goal `2026-06-05-inventory-conversions-nose-05-and-release`: three bundled slices
ending in a release — (1) adapt the `quality` clone-family advisory to nose 0.5,
(2) convert the five remaining import-safe `inventory_*` boundary-bypass tests to
in-process, (3) full-publish 0.21.0 (push + tag + GitHub release). All three
landed; the release is live at `releases/tag/v0.21.0`.

## Evidence Summary

- `git log/show`, `git diff`, the regenerated boundary-bypass baseline summary,
  `./scripts/run-quality.sh --read-only` (71/0 twice), the helper `--release`
  gate, `current_release.py`, `gh release view v0.21.0`, three bounded fresh-eye
  subagent critiques (one per slice), and the publish helper dry-run/execute
  payloads.

## Waste

- **The release publish flaked mid-way and left a partial state.** The publish
  helper's pre-push gate hit the #194 usage-episodes test-isolation race (a
  parallel gate phase appended to the gitignored live `usage_episode.jsonl` while
  the round-trip test asserted that tree immutable). The helper had already made
  the local release commit + tag, so the push failure left commit+tag local with
  nothing on origin. Recovery cost real time: diagnosing flake-vs-regression
  (the test passes in isolation), confirming the authoritative `--release` gate
  had passed, then completing push + `gh release create` + verified-record
  finalize by hand because the helper is not resumable.
- **`publish_release.py` from the installed plugin cache fails its runtime
  bootstrap** (`ModuleNotFoundError: skills.public`) — a dead end before I
  switched to the repo-root copy. Small, but it cost one failed attempt.
- **Two inventory scripts surfaced a hidden testability gap only at conversion
  time** — `inventory_public_spec_quality` / `_cli_side_effect_probes` import
  their sibling `*_lib` bare, relying on `__main__` `sys.path[0]`, so in-process
  load failed. Caught immediately by the focused test run; one-line bootstrap fix
  each. Not large waste, but the boundary probe calls them "import-safe" without
  detecting this, so the gap was invisible until exercised.

## Critical Decisions

- **Diagnosed the nose "0 families" as a JSON-schema parse bug, not a clean
  scan.** Reading `nose scan --help` + a live scan revealed the 0.4-array →
  0.5-object change; the parser was silently returning `[]`. This was the load-
  bearing call — refreshing the baseline naively would have frozen a fake-clean
  state. Added a regression test on the exact 0.5 schema.
- **Asked the user about the publish boundary** (branch-push vs full GitHub
  release) rather than defaulting. The goal text said "push to origin" but the
  repo's prior release was a full publish; the user chose full publish. Asking
  prevented either an under-shipped half-state or an unauthorized public release.
- **Fixed the sibling-import gap in the production scripts, not the tests.**
  Honored commit `a7449e8a`'s direction (tests stay path-hack-free) and raised
  real production testability (goal A) — consistent with the peer scripts that
  already carried the bootstrap.

## Expert Counterfactuals

- **Gary Klein (pre-mortem):** a pre-mortem on the release slice would have asked
  "what blocks the push?" and surfaced the #194 flaky pre-push gate before
  running the irreversible publish — letting me run the gate in isolation first
  (or expect the flake) instead of discovering it mid-publish in a partial state.
- **Michael Feathers (legacy testability):** would note that "has `main()` +
  `__main__`" (the boundary probe's import-safe test) is a weak proxy for
  "cleanly callable in-process"; the real signal is a successful in-process
  import. The probe could grow a cheap import-smoke to flag the sibling-bootstrap
  gap before a conversion trips it.

## Next Improvements

- **workflow:** before an irreversible publish whose push runs a flaky/expensive
  pre-push gate, run that gate once in isolation first (or knowingly expect the
  flake) so a partial-publish state is not the discovery mechanism. (issue #N)
- **capability:** `publish_release.py` should run from the installed plugin cache
  (resolve `skills.public` regardless of cache layout), or doctor should flag
  the gap. (issue #N)
- **memory:** persisted here + recent-lessons digest; the nose-schema and
  sibling-bootstrap lessons are captured in the goal slice log and the
  testability doc.

## Sibling Search

- Transferable pattern: a tool's machine-readable output schema changing
  (top-level shape) silently zeroes a parser expecting the old shape. Scanned the
  other `inventory_*` consumers of external-tool JSON: the nose inventory was the
  only one parsing nose's top-level shape; the boundary-bypass and ratchet libs
  parse repo-internal payloads (versioned `schemaVersion`, drift-checked), so they
  are guarded. No additional unguarded external-schema parser found.

## Persisted

Persisted: yes (see path printed by the persistence helper).
