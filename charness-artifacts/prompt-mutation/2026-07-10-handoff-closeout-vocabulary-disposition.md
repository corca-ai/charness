# Prompt-Mutation Disposition: handoff closeout vocabulary

Date: 2026-07-10
Candidate: `#handoff/closeout-vocabulary`
Source evidence: [handoff refresh pilot](./2026-07-09-handoff-refresh-pilot.md)

## Decision

**Defer the proposed demotion.** Keep the section in `skills/public/handoff/SKILL.md`
and its plugin export unchanged.

The pilot ranked this narrow section first because both mutant runs preserved
the registered refresh tokens while Workflow step 7 still spelled those tokens
verbatim. That is useful candidate evidence, but the policy proposal itself
requires proof of the combined post-demotion ship configuration plus a
real-usage tripwire window. Neither proof exists in the checked-in evidence.

## Evidence Boundary

- The candidate survived 2/2 deterministic refresh captures and, unlike the
  workflow arm, those runs were not unblinded by reading the removed body.
- The battery covered one refresh scenario on one Claude host. It did not prove
  pickup, chunked routing, Codex, other repositories, or prose-reading quality.
- The pilot explicitly says any demotion batch touching workflow or closeout
  vocabulary must run the integrated post-demotion configuration because the
  two sections are mutually redundant for the observed token floor.
- This goal authorizes local deterministic edits and tests, but not a live
  capture/evaluator spend. Cautilus also remains ask-before-run and is not needed
  to decide that the currently required proof is absent.

## Reopen Conditions

Reopen the demotion only when all of the following can be run as one bounded
experiment:

1. explicit approval for the live capture lane;
2. a blinded snapshot construction that does not expose a mutant-only diff;
3. the closeout-vocabulary demotion applied in the actual ship configuration;
4. deterministic refresh witnesses still firing in repeated captures; and
5. a bounded real-usage tripwire window with rollback to the reference text.

Pickup or chunked-routing coverage would improve confidence, but absence of that
coverage must remain visible rather than being converted into a global claim.

## Non-Claims

- The section is not proven necessary.
- The section is not proven dead.
- The 2/2 survival result is a ranking signal, not a stability estimate.
- Deferral does not reject the candidate; it preserves a reversible proposal
  until its own stated ship-configuration proof can be executed.
