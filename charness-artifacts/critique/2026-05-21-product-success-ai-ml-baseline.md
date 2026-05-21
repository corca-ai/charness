# Product Success And AI/ML Baseline Critique

## Execution

Fresh-eye critique ran through three parent-delegated bounded subagents:

- product-contract overclaim angle
- implementation and repo-contract angle
- counterweight triage angle

Packet consumed:
[2026-05-21-114402 packet](./2026-05-21-114402-packet.md).

## Change

Add a Charness product success and metrics baseline, an AI/ML engineering
patterns baseline, refresh the handoff, and split runtime usage-episode
emission into follow-up issue
[#188](https://github.com/corca-ai/charness/issues/188).

## Act Before Ship

- Replace the stronger "source of truth" phrasing for the unavailable Slack
  source with "available working evidence." Done in
  [product-success-metrics.md](../../docs/product-success-metrics.md).
- Do not close #184 as fully resolved by this documentation slice. The docs now
  preserve the human-agreement caveat for numeric targets, product priority,
  and runtime capture activation.
- Keep handoff truth accurate by committing and pushing this slice before
  claiming local `main` is clean with `origin/main`.
- Verify critique artifacts explicitly because the prepare packet itself is a
  checked-in closeout surface.

## Bundle Anyway

- Link follow-up #188 from the handoff. Done.
- Add `outcome_status` and `t_status` to the vocabulary table as schema-owned
  closed enums. Done.

## Over-Worry

- Blocking the documentation slice because Slack could not be re-fetched is too
  strict; the docs disclose the missing access and avoid final agreement
  claims.
- Blocking because telemetry remains disabled is too strict; this slice
  intentionally keeps the adapter disabled until an emitter exists.
- Blocking on numeric targets is out of scope for this baseline; targets need
  product agreement and observed usage data.

## Valid But Defer

- External AI/ML source gathering can be made durable later if these docs become
  a polished external-facing rationale.
- Full issue-resolution closeout ledgers for #184 and #185 belong to the actual
  issue-close step, not this baseline artifact.

## Verification Notes

- `./scripts/run-quality.sh --read-only` passed before the final critique
  wording patch.
- Final targeted checks passed after the patch:
  `check_doc_links`, `check_command_docs`, `check-markdown.sh`,
  `check-secrets.sh`, `validate_usage_episodes.py`, and
  `validate_critique_artifacts.py --all`.
