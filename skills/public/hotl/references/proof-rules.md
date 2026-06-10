# Proof Rules

Proof classes are not interchangeable. Each rule below names a substitution
that looks like proof but is not, and what the honest claim would be.

## The rules

1. **A normalized text match is not exact rendering proof.** Comparing
   normalized or trimmed text proves content equivalence, not how the provider
   renders spacing, markup, or layout. If the acceptance is "renders exactly
   like X", the proof is a readback of the rendered surface, not a string
   compare.
2. **A direct post is not scheduled-workflow proof.** Invoking the posting
   path by hand proves the posting path. It does not prove the scheduler
   fires, the schedule is registered, or the workflow's own config resolves.
   Prove the scheduled run itself, or record the gap.
3. **Bot-authored smoke is not human-ingress proof.** A bot sending itself a
   message exercises bot-to-surface delivery. It does not prove a human's
   message reaches the listener (identity, permission, and routing differ).
   If the acceptance is human ingress, a human (or a faithfully human-shaped
   identity) must send the probe.
4. **External mutation proof needs before/after readback.** For any proof that
   mutates provider state, capture the provider state before, the mutation
   evidence, the provider state after, and the cleanup or restoration result.
   A mutation without readback proves only that a command exited zero.
5. **Sender/listener identity must be proven first.** If a proof depends on
   one provider identity being heard by another listener, prove or fix that
   relationship before spending the roundtrip — it is the most common silent
   pre-roundtrip failure.
6. **Local tests prove local classes only.** Deterministic local tests prove
   guards, target resolution, and command behavior. They do not prove live
   provider behavior unless the acceptance class is explicitly local-only.
   Name the acceptance class in the proof packet so the local/live boundary
   is a recorded decision.

## Proof packet discipline

The packet exists so live budget is spent once, deliberately:

- success criteria name the observable result, not the intention
- pre-roundtrip failure checks run first (config, credentials, listener
  reachability, command support, disposable target, artifact path, known
  policy suppressions)
- feasibility is stated as one of: adapter-declared command exists / a
  repo-owned command must be implemented / manual-or-operator action
- human intervention is an exact action packet (what to click or send, where,
  when, and what evidence to capture), not "have someone check"
- non-claims are written before execution, so the proof cannot quietly expand
  into claims it never tested

## Proof levels

When the proof depends on an external or runtime capability, classify which
level the evidence actually reaches per
`../../../shared/references/external-capability-proof-ladder.md` (`surface`,
`worker_queued`, `host_decision`, `provider_roundtrip`, `agent_choice`). A
lower level honestly recorded beats a higher level claimed.
