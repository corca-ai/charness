# Reference paths and one authoring pytest execution

The source change is `30d4c89d5`. The final verification JSON binds the exact integrated commit and files; subsequent changes preserve evidence only.

## Results

- The impl fixture prompt now preserves relative reference paths against the containing document. The same frozen consumer seed, exported skills and unchanged oracle were used. Original test methods and the spec were preserved; only source and tests changed. Eleven consumer tests and four independent oracle tests passed.
- A separate trace observer found neither invented `skills/shared/...` nor `skills/spec/design-lenses.md` paths and no failed reads. Correct shared-reference content is visible; the correct spec design-lenses path appears in a successful guarded command, but its body was truncated. Broad spec/Prove/reference reading remains; no general routing or speed claim is made.
- Development and operating-contract instructions now use explicit export followed by a fresh full read-only lane. That lane already owns the standing runner first and stops on failure. Existing release-only/slow-corpus exclusions and conditional omissions remain; additional gate/test filters cannot stand in for final integration proof.
- Sixty-nine existing runner, selection and mirror controls passed, including stale-mirror refusal and fail-fast behavior. The final lane passed 83 checks with zero failures in 163.2 seconds; its single pytest phase passed in 98.8 seconds. Five checks were not run: browser baseline/hygiene, dead-code advisory and online supply-chain were opt-in; coverage was omitted in read-only mode. The JSON records all omissions and exactly one pytest phase start. Changed-line proof is a no-op because no eligible mutation-pool source changed.

## Evidence and limits

[Consumer acceptance and frozen identities](./2026-09-08-literal-reference-consumer.json), [actual trace excerpts](./2026-09-08-literal-reference-trace.md), [diagnosis and command comparison](./2026-09-08-reference-and-suite-diagnosis.json), and [final verification](./2026-09-08-reference-suite-final-verification.json) preserve observed outputs. Direct and aggregate process environments are not byte-identical; this change chooses the fresh aggregate as owner, with no result cache or cross-run reuse.

The initial two critiques deferred final approval to actual evidence. Their marker-exclusion and export-paragraph corrections were applied. The [bounded evidence follow-up](./2026-09-08-reference-suite-final-review.json) passed with no findings; its matching worker receipt and delivery ledger are approval-eligible. Fresh-Eye Satisfaction: `worker-delivered`. Parent rejected new resolver/cache machinery and prose-pinning tests. The fixture AGENTS file, public skills, exporter, executable gates and external authorization rules are unchanged. No push, release or installation was performed.

An evidence commit first failed on trailing whitespace. Parent mistakenly launched a broad run before inspecting that failure, then stopped both engine and nested runner. The corrected final run is separate; the interrupted attempt is not a passing result or a claimed cost saving.
