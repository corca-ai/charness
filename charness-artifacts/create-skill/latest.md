# Impl startup with an optional documentation index

Date: 2026-09-08. Scope: local autonomous consumer-workflow improvement; not goal-bound, released, or installed.

## Retained change

The consumer's `docs/index.md` is read **when present**. Its absence no longer instructs an implementer to perform a failing content read before reaching the current contract. Present indexes, explicit `AGENTS.md` requirements, the next step's contract read, and all verification/authorization rules remain intact. The canonical implementation is `skills/public/impl/SKILL.md`; exported host placements remain generated copies. No dependency, adapter, planner, gate, test framework, or new reference was added.

Source base: `c3b5557db8969fe3ee55d88989107e05ddf03756`. Retained source: `dc7a0a74a69512fe3504ebc67719a672d39683d6`. Relative to the base, the only skill change is the clause `when present` in Start item 1.

The capability failure was observed in two consumer traces: an unguarded `sed docs/index.md` failed, and `&&` prevented the same command from reaching the user-named spec/source/tests. The fixture had no index requirement. The inline success criterion was to reach the exact existing contract without an absent-index content-read failure, while preserving canonical lookup, alias acceptance, original tests, and scope. The tripwire was skipping an existing index or a repository's explicit documentation requirement. Independent pre-edit review found no regression in the absent, present, or explicitly-required cases.

Cold start without an index uses the current contract already required by Start item 2. With an index, its owners remain discoverable. Warm continuation and changed-acceptance handling retain the original core rules. Adjacent spec/quality ownership and all public triggers are unchanged.

## Consumer evidence

The [observations](2026-09-08-impl-optional-doc-index.json) retain frozen input/export identities, executed acceptance output, consumer patches, protocol scopes, discarded trials, and limitations. [Command excerpts](../probe/2026-09-08-impl-start-trace-excerpts.md) illustrate the observed failure and repaired start. The existing alias fixture, implementation prompt, previously produced spec, and independent oracle were reused without editing them.

- Absent-index implementation: the consumer read the exact exported skill and named contract without attempting a missing-index content read. Independent alias acceptance passed 4/4; the consumer suite passed 11/11. Original setup/test methods and the spec were unchanged; only the requested source/tests changed. A separate read-only observer inspected the full trace and output.
- Present-index plan: a separate task read `docs/index.md` and the linked exact contract, produced a scoped implementation/verification plan, and changed no files. This is a first-action observation, not executed implementation proof. An earlier host-subagent probe read an installed skill before the export and was excluded from pure-candidate attribution.
- Unresolved: two unrelated exported-reference resolution commands still failed in the absent-index run. This repair does not claim to fix those paths, blanket reference reading, or automatic skill routing.

No speed improvement is claimed. These are individual observations with requested Luna settings, not independent backend attestation or a statistical comparison. Producer timing/token fields exclude parent preparation, review, archival work and authoring gates; total lifecycle net benefit was not measured.

## Discarded hypothesis

The initial trial made four impl reference entries conditional. It was plausible from older traces, but the fixture's instruction to resolve every reference was a competing cause. Initial observations did not establish a stable reduction; the reviewed final trial read all impl/spec references and repeated five impl references. The reference changes were restored completely instead of being kept as an unproved optimization.

Independent review improved that trial's optional-adapter discovery condition and rejected an overly broad requirement to read generic handoff guidance after every acceptance change. Those trial edits are not part of the retained source. The resulting narrower finding was the absent-index startup failure above.

The first acceptance helper also compared `setUp` while labeling its result as original-test preservation. Raw false flags are retained. Independent review confirmed both original `test_*` methods/assertions were unchanged and the setup refactor preserved semantics. The retained run preserves all original methods without that distinction.

## Authoring verification

Focused skill preflight, package/link/contract checks and 25 standing-runner tests passed for the retained source. Changed-line proof reported `noop`: no mutation-pool source changed. Final integrated proof on the retained source passed: standing 9,266 tests; full read-only 83 passed, 0 failed, 5 not run. The omitted checks were agent-browser runtime baseline/hygiene, dead-code advisory and online supply chain (opt-in unmet), plus coverage (read-only). The receipt is retained in the observation JSON. Evidence-only archival changes after this source proof receive focused checks.

The parent started broad verification before one review finished and later before the reference trial was rejected. Interrupted runs are not passes; the 9,266-test pass on the discarded reference trial is not retained-source proof. This was avoidable sequencing cost, not evidence for adding another validator.

No push, release, version change, installed-host mutation, or external tracker action is claimed.

The full lane also reported runtime-budget advisories for plugin import smoke and the recent release read-only lane. These remain advisory follow-ups; this slice did not change those producers or claim to improve their runtime.

Evidence-only archival checks passed: Markdown, document links, artifact referents, JSON parsing, secret scan and diff whitespace. The retained skill bytes still match the full-verified source.
