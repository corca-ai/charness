# Adversarial Evidence Review

Use this reference only when a critique input contains an observed failure or a
review finding that is already being treated as evidence. The purpose is to
separate a report that sounds plausible from a failure that the final consumer
actually exhibits.

## Routing

Use `critique` first when the request is review approval, before-merge judgment,
or evidence disposition. Use `debug` when it asks for root cause, Five Whys, or
recurrence analysis. When both are requested, critique produces the typed
dispositions and debug consumes the reproduced findings.

The normal critique scaffold remains mode-neutral. Add the two evidence-led
sections only when this mode is selected; their presence activates the shared
validator. Run the emitted critique/debug validator with `--evidence-led` in
this mode; that explicit binding fails closed when both sections are omitted.
Historical artifacts without the flag remain shape-compatible and cannot claim
evidence review merely by passing the ordinary validator.

## Claim Record

Carry one record per reported finding:

```text
- Finding: <stable id> | source: <review, issue, log, or artifact path> | expected: <given/when/then behavior> | stimulus: <smallest input that could disconfirm the claim> | disposition: reproduced | disconfirmed | unproven | not-applicable | observed: <final-consumer output, refusal, or missing observation> | proof: static scan only | local payload proof | executable fixture | runtime/provider roundtrip | handoff: <debug artifact or `none` when not reproduced> | next move: <named next move or `none` when not reproduced> | receipt: <repo-relative JSON receipt or `none` for a non-claim> | receipt sha256: <64 lowercase hex or `none`>
```

The containing artifact also records `Report Identity`, `Reported Findings`,
`Dispositioned Findings`, `Missing Findings`, `Report Source`, and
`Report Source SHA256`. Dispositioned plus missing IDs must cover the reported
count. Use an identity such as `review:2026-08-25#sha256:<64 lowercase hex>`;
its SHA256 must equal `Report Source SHA256`, so a changed source packet needs a
new identity. `Report Source` is a repo-relative
packet/fixture path and its SHA is recomputed by the canonical validator when a
repo root is available; an external source without a local packet is `unproven`.
Add `Evidence Digest: sha256:<64 lowercase hex>`; it is the canonical digest of
the typed record lines and catches stale/copy-pasted edits.

For `reproduced` or `disconfirmed`, the receipt is mandatory and must be a
repo-relative JSON file whose SHA is recomputed by the canonical validator. It
must use schema `charness.adversarial-evidence.receipt.v1`, bind the record's
finding/source/expected/stimulus/disposition/observed fields exactly, and carry
the executed command, fixture identity, final-consumer identity,
`executed: true`, `final_consumer_observed: true`, and an integer return code.
This is a receipt binding, not an independent claim that a provider was live;
without the channel, record `unproven` with `receipt: none`.

Do not collapse `missing`, `empty`, `unavailable`, `skipped`, `stale`, and
`passed` into one boolean. If the report cannot be exercised, preserve
`unproven` and name the missing evidence channel.

## Stimulus Selection

Choose the cheapest stimulus that can make a false approval visible:

- delete or corrupt a required input to test degraded readiness
- skip, xfail, xpass, or zero a fixture to test executable proof
- mutate a helper, schema, or transitive dependency to test trigger closure
- remove or traverse an exported anchor to test package proof
- replay a stale receipt or copied count to test artifact binding

The stimulus must reach the final consumer that decides success, refusal, or
readiness. A producer log or subprocess exit code alone is not final proof.
`reproduced` requires `executable fixture` or `runtime/provider roundtrip` plus
the receipt binding above; `static scan only` and local payload proof are never
reproduced. Run
deletion, corruption, or mutation stimuli in a temporary fixture or isolated
worktree, never the shared parent checkout, index, or tracked artifact. If
isolation is unavailable, record `unproven` and the host signal.

## Decision Rules

- `reproduced`: the expected failure or false-green path is observed; hand it to
  `debug` for invariant-first analysis and Five Whys.
- `disconfirmed`: the stimulus reaches the consumer and the claim does not
  occur; retain the observation without inventing a new bug. This also needs
  consumer-capable proof; a static scan cannot disconfirm runtime behavior.
- `unproven`: the required consumer or host channel is unavailable; this is a
  non-claim and cannot support approval.
- `not-applicable`: the report names a surface outside the change boundary;
  cite the boundary rather than silently dropping it.

## Handoff And Repair Loop

After the disposition pass, `debug` owns the causal record. A reproduced record
must name that handoff and its next move; a non-reproduced record may use
`none` for both. Its `Pattern
Ladder` should connect the concrete failure to interface-shape siblings and a
testable structural cause. After a repair, run one separate adversarial read of
the repaired verdict surface only when the repair materially changes the
reviewed risk. When it does not, the existing disposition remains sufficient;
do not require a repeated review or a second durable artifact.

## Stop Conditions

Stop the adversarial pass when every report has a typed disposition and either:

- every `reproduced` finding has a debug handoff and a named next move, or
- every non-reproduced finding has a concrete non-claim or boundary reason.

Do not expand a single report into a system-wide redesign unless the pattern
ladder finds a sibling with the same producer/consumer interface shape or an
external seam disproves local reasoning.
