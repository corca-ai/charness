# Gather: Ceal #113 Judgment Boundary

Source: https://github.com/corca-ai/ceal/issues/113
Related commit: https://github.com/corca-ai/ceal/commit/7910984d06fe2819bdcf79434b286833fb59e0fb
Access mode: GitHub `gh` authenticated direct-cli
Freshness: fetched 2026-05-19 during Charness #177 resolution

## Requested Scope

Capture the Ceal source context that Charness #177 cites so implementation guidance can be grounded in the upstream observed workflow gap rather than a transient issue summary.

## Source Facts

Ceal #113 reports that a daily-scrum-sharing workflow produced a weak semantic cross-team recommendation by connecting `Paymentwall 입금/계약` with broad `paywall/매출 정합성` context. The first attempted fix moved toward keyword/category rules, but the issue says that was the wrong boundary: the workflow should keep simple safety gates and preserve agent judgment for semantic relevance.

The desired Ceal behavior is to first identify whether a user correction reveals a missing hard invariant or a poor judgment call. Deterministic rules should be reserved for true invariants, safety limits, source-of-truth constraints, or externally mandated policy. Semantic quality failures should prefer prompt or skill guidance that preserves judgment, allows zero recommendations when uncertain, and avoids incident-specific keywords or categories unless the user explicitly asks for that rule.

Ceal commit `7910984d06fe2819bdcf79434b286833fb59e0fb` added one base-prompt sentence in `packages/agent-runtime/prompts/base.md` telling the agent to preserve the judgment boundary before encoding a fix. It also added a prompt test asserting that wording is present.

## Relevance To Charness #177

Charness #177 asks upstream Charness implementation guidance to recognize "preserve judgment boundary / no repo change yet" as a valid outcome after user correction. The Charness side should keep wording sparse and general, avoid an incident-specific taxonomy, and report validation honestly: source/guidance coverage can be proved locally, but future semantic quality is not proven without a targeted behavior replay.

## Open Gaps

The original Slack thread referenced by Ceal #113 was not fetched here. The GitHub issue and commit were enough for Charness #177's acceptance sketch; fetch the Slack source only if future work needs to evaluate the original semantic recommendation itself.
