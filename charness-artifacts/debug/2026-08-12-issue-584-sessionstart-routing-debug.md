# Issue 584 SessionStart Routing Debug
Date: 2026-08-12

## Problem

The SessionStart routing hook receives a repository `cwd` but emits one constant
handoff instruction, so a consumer whose handoff adapter moves the artifact can
be told to inspect the wrong path.

## Correct Behavior

Given a SessionStart payload containing a repository cwd, when the installed
handoff adapter resolves its artifact path, then the hook must inject the
configured path only when that file exists; otherwise it must explicitly skip
the pickup branch. The hook remains exit-0 on resolver failure.

## Observed Facts

- GitHub #584 is open; its #531 member records this as a live consumer-facing
  defect and requires adapter resolution rather than `docs/handoff.md` probing.
- `scripts/session_start_routing.py` reads `cwd` only for debug output and
  `build_additional_context()` returns the `DIRECTIVE` constant unchanged.
- `skills/public/handoff/scripts/resolve_adapter.py` produces the authoritative
  relative `artifact_path`; its default is `docs/handoff.md` but adapters may
  override it.
- `main()` already encloses hook work in a broad `try/except` and returns 0.

## Reproduction

- Feed a payload with a cwd containing `.agents/handoff-adapter.yaml` that sets
  `output_dir` to a non-default directory. The pre-fix emitted directive still
  names `docs/handoff.md`, regardless of that adapter or file's existence.

## Candidate Causes

- The directive predates adapter-configurable artifact locations.
- The payload's cwd was treated as debug-only host metadata.
- The existing tests assert a constant directive and never exercise an adapter
  fixture with present and absent handoff files.

## Hypothesis

- Confirmed if a helper invokes the installed handoff resolver against payload
  cwd and tests observe configured-present, configured-missing, and resolver-
  failure branches without changing the hook's exit-0 behavior; disconfirmer: the
  resolver cannot be located from either source or shipped-plugin layout.

## Verification

- Result: resolved. `python3 -m pytest tests/test_session_start_routing.py -q`
  passes 19 tests, including source and shipped-plugin nested-cwd paths plus
  entrypoint-level missing, timeout, and nonzero resolver output. Packaging and
  debug artifact validators pass. A local hook run measured about 0.14 seconds.

## Root Cause

The hook's runtime contract had no adapter-to-directive seam: it kept a default
path literal in a global string while the authoritative adapter path was
available only to handoff workflow planners.

## Invariant Proof

- Invariant: when the handoff adapter emits an artifact path, the SessionStart
  final consumer must act on that configured path before offering pickup routing.
- Producer Proof: resolver fixture emits a non-default `artifact_path`.
- Final-Consumer Proof: SessionStart subprocess output contains the configured
  present path or the explicit skip state.
- Interface-Shape Sibling Scan: source script and shipped plugin projection
  share this hook contract; `plan_handoff_run.py` already consumes the adapter.
- Non-Claims: no real Claude or Codex host roundtrip is run; local hook payload
  proof does not establish host injection behavior.

## Detection Gap

- SessionStart routing tests | only default constant assertions fired | add
  adapter-backed present/missing and resolver-failure payload tests.

## Sibling Search

- Mental model: a default path in contextual prose is safe even when a runtime
  adapter owns the artifact location.
- same layer: `plugins/charness/scripts/session_start_routing.py` | decision:
  same bug, fix now | proof: generated projection equality test.
- abstraction up: handoff planner | decision: same class, diagnostic-only for
  this slice | proof: local payload proof; it already resolves the adapter.
- specialization down: missing configured handoff | decision: same bug, fix
  now | proof: local payload test.
- cross-file: `skills/public/handoff/scripts/resolve_adapter.py` | decision:
  intentional adapter owner | proof: static scan only.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: host payload cwd to installed resolver to contextual directive.
- Disproving Observation: resolver location cannot be derived from the hook's
  source/plugin layout, or it emits an unusable path.
- What Local Reasoning Cannot Prove: host timing and host treatment of emitted
  `additionalContext`.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Critique Scope: host-safe adapter resolution and configured-path disclosure.
- Next Step: impl
- Handoff Artifact: this record.

## Prevention

Treat runtime-visible artifact locations as adapter-owned data. Pin both source
and generated-plugin paths with fixtures so a default literal cannot reappear.
