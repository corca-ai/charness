Classification: decision-needed

Jtbd: Decide whether Goal #744 must continue spending its serial critical path on hosted Mutation Tests before the remaining composable-capability issues can close.
Decision: Not planned for this Goal. The operator explicitly removed Mutation Tests from the Goal's proof policy after two hosted attempts failed in the standing baseline before mutation ran. The durable amendment is `charness-artifacts/goal-runs/744/amendments/2026-08-30-ignore-mutation-test-proof.md`; the follow-up diagnosis is `charness-artifacts/debug/2026-08-30-issue-758-mutation-workflow-standing-baseline-followup.md`.
Evidence: Runs `33296181601` and `33297693085` both skipped actual mutation. The second run exposed an authoring-clone versus provider-history referent seam; that seam is diagnosed and deliberately deferred, not represented as repaired.
Non-claims: No successful mutation execution, mutation score, mutation non-regression, or #758 behavioral fix is claimed. Closing the tracker records the operator's scope decision only.
AI-provenance: Agent-authored decision closeout from the operator-approved Goal #744 proof-policy amendment and durable debug record.
