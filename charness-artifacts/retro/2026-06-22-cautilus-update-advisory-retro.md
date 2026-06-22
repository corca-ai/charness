# Retro — cautilus manual/staleness -> behind-latest advisory (2026-06-22)

Mode: session

## Context

Operator asked why `cautilus version` stayed 0.15.4 after `charness update all`,
then "why is cautilus manual? auto seems right." Traced the mechanism (manual
lifecycle + version-pinned wrapper), surfaced a real defect (advisory-policy tools
record `latest_tag` but never compare it -> silent staleness), shipped a
generalizable behind-latest advisory, upgraded cautilus to 0.17.1, re-verified the
claim-fidelity harness eval contract on 0.17.1, and fixed a latent js-mutation red.

## Waste

- **Lock-schema strictness misread (one debug cycle).** A quick `additionalProperties`
  probe reported the lock `doctor` block as permissive; it is actually
  `additionalProperties: False` with a required list. I designed `update_advisory`
  persistence assuming permissive -> doctor.py raised a jsonschema ValidationError
  under `--write-locks` -> CLI exit 1, caught by the CLI lifecycle tests. Root: a
  one-shot probe of the schema instead of reading the actual schema node / running
  the validator before persisting a new field into a schema-validated artifact.
- **Prior-session incomplete green (latent red surfaced).** `tests/quality_gates/
  test_js_mutation_tooling.py` had a stale hardcoded pool/sample list since
  build-skill-execution-observation.mjs landed (4f46230a); `node --test` passed but
  the standing pytest was never run, so the red shipped. Not this turn's change, but
  this turn's thorough verification caught it.

## Critical Decisions

- Kept cautilus update **manual** (eval-surface stability + deliberate v0.14.2 pin +
  operator-gated contract) and fixed the actual defect (silent advisory)
  generalizably, instead of flipping the evaluator to auto-update. Matched the
  operator reframe; auto-swapping the scorer mid-workflow was the wrong default.
- **Before/after proof** of the advisory (fired on the real 0.15.4 gap; clean
  `current` after upgrade) rather than asserting it works.
- Re-verified the harness contract on 0.17.1 by **re-scoring the existing packet**
  (cheap, no new capture); reject verdict + schemas reproduced.
- Fresh-eye critique with a **negative control** on the lock-leak path (leaked ->
  ValidationError; stripped -> PASS), proving the strip is load-bearing.

## Expert Counterfactuals

- Chesterton's-fence / archivist lens: before recommending "make it auto," retrieve
  the prior decision on why it is manual. The manifest's deliberate `v0.14.2` support
  pin + "main not stable across the promise-spec/HITL rewrite" note + the eval-only
  contract are the fence. The fence stood (manual is right for the *evaluator*), so
  the fix correctly landed on the silent-advisory axis, not the mode. This is the
  same lens the prior retro flagged (mis-attributing to a settled-decision layer) —
  applied correctly this time.

## Next Improvements

- **workflow:** before persisting a new field into a schema-validated artifact,
  confirm the target block's `additionalProperties` by reading the schema node or
  running the validator on a sample — not a one-shot probe. (applied: caught + fixed
  via lock_safe_doctor_payload pop this run.)
- **workflow:** when touching `scripts/agent-runtime/*` (mutation-pooled) or adding
  files there, run the standing pytest (not just `node --test`) before claiming
  green. (applied: js-mutation expected lists refreshed this run.)
- **capability:** behind-latest advisory now exists for every advisory-policy tool
  via the shared `attach_release_metadata` chokepoint + doctor. (applied, committed.)
- **memory:** "advisory-policy tool version was silent (recorded latest_tag, never
  compared); the fix is a behind-latest advisory in the release chokepoint, not
  auto-update of the evaluator." Recorded here.

## Sibling Search

Transferable pattern A — "records upstream state but never surfaces the gap": the
version_expectation:advisory silence was the instance; the shared-chokepoint fix
now covers ALL advisory tools, so no per-tool sibling remains. Pattern B —
"new field persisted into a strict-schema artifact without checking strictness":
the only new persisted field this session was update_advisory (now popped from the
lock); no other sibling this session. scripts/gates: none introduced.

## Persisted

(set by persist helper)
