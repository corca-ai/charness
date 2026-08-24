# External Worker Capability Envelope — Fresh-Eye Rereview

Date: 2026-08-24
Decision before repair: block
Initial reviewer backend: direct read-only `codex exec`, Luna, xhigh; its findings
caused the repair over the r2 packet, but its noncanonical carrier is not claimed
as approval.
Final reviewer carrier: parent-delegated bounded reviewer over the repaired r4
commit-bound packet. It confirmed the same reviewed-input identity as the passing
r3 read and re-ran the r4 verifier as current.
Fresh-eye satisfaction: parent-delegated

## Findings And Disposition

1. Act before implementation: an empty write/effect list did not prove effective
   denial. Repaired by requiring explicit policy plus host-observed per-axis
   `denied`; missing, unproved, or contradictory evidence fails closed.
2. Act before implementation: the generic receipt was not normatively joined to
   the existing reviewer delivery chain. Repaired by fixing the chain as attempt
   -> worker receipt -> delivery ledger -> combined report, binding all identities,
   and reserving `approval_eligible` to the combined report.
3. Bundle: authentication verdicts lacked same-attempt logical target and reached
   layer. Repaired in the preflight record and state-transition criteria.
4. Bundle: sandbox mode could be mistaken for authority. Repaired by making it
   provenance only and adding negative acceptance fixtures.

Per-domain allowlists, credential rotation, provider-specific mutation probes,
and universal host sandbox semantics remain valid deferred work. A generic network
policy engine and parsing every `gh` diagnostic string were rejected as over-worry.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: `model=gpt-5.6-luna`, `reasoning_effort=xhigh`
- Host exposure state: requested_fields_sent
- Application state: n/a — the host accepted the fields but exposes no provider-applied metadata
- Delivery state: findings-received

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r4-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r4-packet.json`
- Packet SHA256: `d2e8c9f34218c91e5f04a11ec6e6f85130b135cc46ea49e5286a1663ac5b1624`
- Identity SHA256: `4e7fb4fb9faffe6b3b22e67844db91a59d81d7b96a101aa3213ef7f4f982879a`
- Packet verification: `ok: true`, `status: current`; reviewer re-ran the exact command before judgment

## Boundary Ownership

- Producer: invocation freezes requested logical capability and policy
- Consumer: host adapter and receipt validator observe/refuse; combined report alone renders review approval
- Owning surface: external-worker invocation/receipt contract plus existing reviewer delivery chain
- Verdict: owned-correctly

The invocation producer owns requested logical capability; the host adapter owns
observed transport/auth/sandbox facts; the receipt validator owns impossible-state
refusal; and only the existing combined reviewer report owns `approval_eligible`.
The repair made those producer/consumer joins normative instead of creating a
second generic approval owner.

## Non-Claims

This review and repair approve only the first-slice design contract. They do not
prove implementation, installed packaging, Ceal adoption, live denial enforcement,
or reviewer approval of the future verdict-rendering code. That code still owes
focused negative proof and the required bounded review round(s).
