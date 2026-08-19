# issue 675 resolution critique
Date: 2026-08-19

## Decision Under Review

The resolution of [#675](https://github.com/corca-ai/charness/issues/675): splitting the
census's single `guarded` token into `guarded-all-doors` / `guarded-errors-only` /
`guarded-upstream`, with a witness that checks the LEVEL in both directions — and keying that
level on what the CONSUMER asks rather than on what its resolver reports, against the issue's
own proposal.

## Failure Angles

- **The chosen axis could measure nothing.** The issue proposes keying the level on whether
  the file's resolver routes through the reporting loader. If that axis is real and the
  consumer axis is not, the split reports a distinction that does not exist.
- **A migration of 35 rows can upgrade by hand.** The issue is explicit that nothing may be
  upgraded without a measurement.
- **A token that publishes an ENUMERATED set owes that enumeration the same measurement the
  verdict owes** — and the tempting shortcut is to lift it from prose that already lists
  members.
- **A gate can shape its own input.** If the checker refuses a legitimate shape, the manifest
  bends to the checker rather than to the code.

## Counterweight Pass

REAL BLOCKERS, all folded before close:

- The gate's headline accepted-risk number was inflated by half: five of ten rows already
  carried "every production caller is guarded" in their own reasons and sat in that class
  only because no token existed for them.
- The token named the wrong DIRECTION. `guarded-by-caller` / `covering_callers` publishes a
  call-graph claim, and the only live row is covered by its CALLEE. Renamed to
  `guarded-upstream` / `covering_rows`.
- TWO of the five `covering_rows` lists were wrong — both derived from each row's own PROSE
  rather than the call graph. One was incomplete in both directions; one was a row that
  should never have migrated, because it CAN guard itself and simply does not.
- The gate FORBADE a legitimate two-hop chain, so the manifest omitted a real caller rather
  than recording it — the gate shaping its own input, which is `#675`'s own distortion one
  level up. Chains are followed now, with cycle detection.
- The level witness is CALL PRESENCE, not load-bearing-ness, and the module's blind class did
  not say so; three further limits were missing from that list.

OVER-WORRY, raised and not folded: the consumer axis. `#673` made all sixteen public
resolvers report all three doors, so the resolver axis is uniform across every guarded row —
traced, not assumed. Keyed on the consumer the level is real: 32 rows cover all three doors,
three ask a predicate over `errors` alone and are blind to a silently dropped line.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/adapter-consumer-classification.json | action: fix | note: five rows meeting the new level's criterion sat in accepted-risk, so the gate's headline debt number was false by the manifest's own text
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_adapter_consumer_classification.py | action: fix | note: the token and its field named a caller relationship the gate never checks, and the only live row is covered by its callee
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/adapter-consumer-classification.json | action: fix | note: two of five covering_rows lists were derived from prose and were wrong, one of them a migration that should not have happened at all
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/check_adapter_consumer_classification.py | action: fix | note: forbidding a legitimate two-hop chain produced a manifest that omitted a real caller instead of a refusal
- F5 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/goals/2026-08-19-adapter-debt-tooling-and-remainder.md | action: defer | note: 55 safe-checks-errors rows now carry one token over materially different coverage, exactly as guarded did; staged as an operator decision rather than split here
## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (this repo's read-only typed subagent).
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing name, read-only tools (Read, Grep, Glob), one bounded packet per round naming intent, changed files, invariants, non-claims and out-of-scope lines.
- Host exposure state: applied
- Application state: host-confirmed: two reviewer reports were returned to the parent across two rounds, each naming the tools it actually used and the findings it could not construct.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; each round's packet was authored inline in the spawn prompt and is reproduced in the goal's `## Slice Log` slice 3 critique field. -->

## Boundary Ownership

- Producer: `scripts/check_adapter_consumer_classification.measured_guard_level` — the level a file's own calls establish.
- Consumer: the census manifest's per-row verdict, and the per-level counts an operator reads to answer "how much of this debt is closed".
- Owning surface: adapter-consumer census gate.
- Verdict: owned-correctly
