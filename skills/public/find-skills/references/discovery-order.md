# Discovery Order

`find-skills` should search in this order:

1. local public skills
2. local support skills
3. local synced support skills
4. local external integration manifests
5. adapter-configured trusted skill roots
6. missing capability classification

Reason:

- users should prefer what already ships in the current harness
- support skills are not the product's public concept layer
- synced support skills are already materialized locally, but still belong below
  the public concept layer
- external integrations may require install/update/doctor flows that are not yet
  active
- trusted skill roots are host-trusted extension surfaces, not local product
  ownership

When more than one match exists:

- prefer the most direct public concept
- prefer local public skills over trusted-root skills unless the host adapter
  says otherwise
- fall back to support or integration layers only when the need is primarily a
  tool-use capability

## Interpreting the recommendation ranking

The recommendation ranking (`tool_/support_/workflow_/public_skill_recommendations`)
is an **inference-layer** proxy, not a verdict: it matches declared trigger
vocabulary, not task semantics. When a ranking is produced it carries a
`recommendation_interpretation` self-declaration per
[advisory-interpretation-contract.md](../../../shared/references/advisory-interpretation-contract.md).
Before routing on it, the consumer must answer its declared interpretation
question first: does the top-ranked route actually fit THIS task and repo state,
or is it a trigger-phrase coincidence — and is a better-fitting skill missing
from the ranking? An empty ranking is not proof that no capability exists. The
capability *inventory* itself (installed skills, paths, triggers) is a verified
fact and stays trusted; only the ranking is re-interpreted.
