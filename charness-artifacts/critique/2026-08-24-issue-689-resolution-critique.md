# Issue #689 Resolution Critique

Date: 2026-08-24

Verdict: `CLOSABLE-WITH-SEPARATE-FOLLOWUP`

## Outcome-to-proof map

| Requested outcome | Executed proof | Judgment |
| --- | --- | --- |
| Node TAP baseline is readable | Current Charness real-Node fixture returns `earned: true`, two passing tests, and exit `0`. | Proven |
| A real mutation receives a typed verdict | The same fixture reports one killed mutant and refuses a module-load failure instead of miscounting it as a kill. | Proven |
| Exact restoration | Source fixture compares bytes; Ceal commit `f65a0b25c` records identical pre/post SHA-256 and Git object hashes plus an empty recovery journal. | Proven |
| Source/plugin/installed parity | Reporter and runner hashes match across source, checked-in plugin, installed 6.4.0 cache, managed checkout, and consumer probe. | Proven |
| External Node consumer use | Ceal runs a real TypeScript source mutation through installed Charness against a 27/27 TAP baseline and receives `killed: 1`. | Proven for Ceal |

## Resolution judgment

The original issue asks for Node test accounting that lets the mutation harness
run against a Node repository. That capability is implemented and has crossed
the final-consumer boundary in Ceal. Requiring deletion of Ceal's fork or sibling
repository adoption before closing this issue would broaden its requested
outcome after the fact.

Closure must not claim tracked Ceal adapter/plan/CI wiring, full guard-manifest
parity, TypeScript call-site analysis, fork retirement, or adoption in
`ceal-cli`/`ceal-agent`. Those are tracked separately in Ceal #732.

The fresh-eye review also found a safe-direction false refusal: the Node reporter
selects the last TAP summary but counts process diagnostics over the entire
transcript. That observer-window mismatch is tracked separately in Charness
#714; it does not invalidate the single-run real-consumer proof for #689.

## Irreversible-boundary evidence

- Distinct Luna xhigh reviewer delivered the resolution verdict.
- Charness and Ceal reviewer-boundary windows both verified `clean` with no
  worktree, index, or HEAD drift before these findings were consumed.
- No issue close, comment, push, release, or hosted mutation was performed.

## Fresh-Eye Satisfaction

parent-delegated — a distinct read-only Luna xhigh
reviewer returned `CLOSABLE-WITH-SEPARATE-FOLLOWUP`, and both repository
fingerprint windows verified clean before the findings were consumed.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-luna`,
  `reasoning_effort=xhigh`, `service_tier=priority`
- Host exposure state: requested_fields_sent
- Application state: spawn accepted; effective model and effort were not
  independently observable
- Delivery state: findings-received

## Boundary Ownership

- Producer: Charness `NodeTestReporter` and `mutate_and_restore.py` produce the
  structured Node mutation verdict and restore evidence.
- Consumer: Ceal's installed-Charness adoption probe is the final external Node
  consumer for this issue's requested capability.
- Owning surface: reporter adapter plus mutation runner contract in Charness;
  tracked fork adoption remains Ceal-owned follow-up #732.
- Verdict: owned-correctly
