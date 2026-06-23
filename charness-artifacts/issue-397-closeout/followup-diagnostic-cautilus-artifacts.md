## Summary

#397 exposed a second, separate problem from the quality skill's runtime
reference bypass: a valid diagnostic Cautilus `reject` finding has no first-class
artifact home.

Today `scripts/validate_cautilus_proof.py` and
`charness-artifacts/cautilus/latest.md` are shaped around passing proof of a
prompt or skill change. That is right for release/proof closeout, but it makes a
negative evaluator verdict awkward even when the evaluator is doing exactly the
right thing.

## Evidence

In #397, the 2026-06-22 quality claim-fidelity run correctly rejected a real
`/charness:quality` execution because it opened `0/39` declared quality
references and exceeded the runtime threshold. The finding was preserved under:

- `charness-artifacts/cautilus/quality-claim-fidelity-2026-06-22/`

That side bundle worked as a preservation tactic, but it did not answer the
artifact-contract question: where should an honest negative Cautilus verdict
live when the desired output is diagnosis, not "latest passing proof"?

## Requested outcome

Add a canonical diagnostic/finding path for evaluator-backed negative results.
Possible shapes:

- a diagnostic `latest` variant that does not pretend to be a passing regression
  proof
- a `goal: diagnose` or equivalent exemption in the validator
- a separate `finding.md` / `observed.v1.json` contract with explicit
  non-claims and follow-up linkage

Success means a future evaluator-backed failure can be preserved, validated, and
linked from issue work without weakening the passing-proof contract used for
release or prompt-change closeout.

## Non-goals

- Do not make failing diagnostic verdicts look like passing proof.
- Do not relax release or prompt-change proof requirements.
- Do not re-open #397's quality runtime-reference fix; this is only the
  diagnostic artifact contract sub-gap.
