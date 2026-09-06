# Goal 798 impl evidence reuse brief

- Artifact: public skill, one canonical implementation at skills/public/impl/SKILL.md; generated host registrations remain placements, not forks.
- Audience/trigger: agents implementing an agreed consumer change; trigger unchanged.
- Current center: focused verification and conditional references. Next center: reuse applicable guidance and checks until their inputs or the decision change.
- Capability failure: baseline CLI trace contains 11 strict duplicate operations after usable same-input evidence. Counts exclude changed-input tests and independent review.
- Portable intake: consumer implementation with an existing contract, stdlib CLI and tests; not a Charness-only ceremony. No new external dependency, adapter, state ledger, planner, or permission.
- Adjacent ownership: create-cli defines acceptance axes and delegates implementation proof to impl; spec defines handoff readiness. Neither needs a copied reuse rule. No trigger collision or durable-write ownership change.
- Contract: preserve frozen consumer acceptance; improve redundant-operation behavior only if the candidate trace supports it. Revision 3 protocol and freeze manifest remain immutable.
- Success criteria review (inline, narrow edit): actor retains required checks but avoids rereading unchanged guidance or repeating unaffected passing checks. Acceptance is the frozen independent A/B checks plus configured trace review. Tripwire: stale evidence reused despite changed code, test, environment, or external state; a required independent/release check skipped. No claim of statistical speedup.
- Cold start: read needed owners and establish evidence. Warm start: reuse still-applicable evidence. Error recovery: changed input or unresolved contradictory result justifies targeted rerun and existing debug route. Failure cases: indiscriminate reference sweep; treating a README-only patch as invalidating pure API tests; treating unchanged filenames as unchanged external state.
- Counterweight: limit reuse to still-applicable evidence and preserve owner-required fresh checks. No mechanical cache or freshness framework.
- Proposed change: one paragraph in impl Verify. No new reference or phrase-pinning test.
- Proof boundary: canonical exported package; identical frozen prompts/seeds, separate producer contexts and parent black-box checks. One paired sample, then separate semantic observer; preserve success is not an improvement claim.

## Baseline trace audit

Trace: CLI baseline codex.stderr.log, committed candidate 5cf9b39fb50ef0a77c245a569c4bcf92bbb95f4f. Independent parent-delegated read-only audit by journey_design:
- Four create-cli references read at lines 521–522 and again 696–697.
- install-update tail read again at 8918.
- Four shared references read in sweep 9041–10947 then again 11442–11449.
- At 14591, nine-test suite and compile repeat the usable checks at 13213 after only README changed at 13685–13687.
- Strict total 11. Inapplicable first reads excluded. Lines 3688, 8449 and 13213 tests follow code/test changes and are excluded. Independent review and diff/status checks excluded.

## Execution-setting observation

All three baseline task receipts report the carrier default timeout 3600 seconds, despite the protocol's intended 1800. None timed out. Preserve the frozen protocol and record this deviation; candidate uses explicit 3600 to match actual baseline settings. Model Luna, effort xhigh, sandbox workspace-write remain identical. This timeout mismatch cannot support a speed or reliability claim.
