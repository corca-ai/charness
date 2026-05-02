# HITL Report Mode

Report mode turns a generated artifact into a small human decision queue. The
raw report remains evidence; the primary surface is the set of decisions the
human is being asked to make.

## Packet Shape

The renderer accepts a JSON object with:

- `session_id` or `id`
- `title`
- `summary` or `intro`
- `agent_next_step`
- `items`

Each item may include:

- `id`
- `question` or `review_question`
- `why` or `why_it_matters`
- `explanation` or `plain_language_summary`
- `suggested_decision`, `recommended_decision`, or `suggested_action`
- `agent_next_step`
- `evidence_links` or `evidence`
- `table` or `evidence_table`
- `source_order`
- `priority`
- `depends_on`
- `blocks`
- `tags`
- `why_next`

Adaptive queue packets use explicit item IDs. Fallback `item-N` IDs are only
safe for non-adaptive packets because reprioritization and resume need stable
identity across renders.

`priority` may include:

- `leverage`: `high`, `medium`, or `low`
- `risk`: `high`, `medium`, or `low`
- `uncertainty`: `high`, `medium`, or `low`
- `context_cost`: `low`, `medium`, or `high`
- `rule_seed`: boolean
- `score`: additive base score for local packet builders
- `reason`, `why_next`, or `score_explanation`

Ordering is deterministic:

1. structured queue effects from explicit review input
2. blocking/dependency metadata
3. priority metadata
4. `source_order`
5. item `id`

Review input may include `queue_effects` on reviewed items. Supported effects
are `boost_tag`, `deprioritize_tag`, `supersede_tag`, `supersede_item`, and
`recommend_restart`. Effects are structured state supplied by the agent after
human judgment; report mode does not infer them from free-form comments.

## Review Surface

Decision cards are first-class. Each card should make these visible before raw
details:

- what the human should decide
- why the decision matters
- what the evidence means in plain language
- what the agent will do next
- optional links or expandable raw details
- a comment field

Tables and matrices are not the primary review surface. When a packet includes
table rows, render a short plain-language interpretation first and keep the raw
table inspectable behind details. The goal is to spare the reviewer from
decoding generated structure before they understand the decision.

When `recommend_restart` is present, render a queue-level meta-card before
ordinary cards. The meta-card asks whether to continue or stop, apply accepted
feedback, and restart HITL with a fresh queue. This recommendation is
display-only until the human explicitly records a queue action outside the
ordinary card defaults.

## Saved Decisions

Suggested decisions are metadata only. Defaults stay `unreviewed`, and untouched
`unreviewed` cards are dropped from the saved JSON so a later agent cannot
confuse a recommendation with human approval.

The browser save affordance produces a compact review-input packet that can be
fed back to `render_report.py --review-input`. The CLI output remains the fuller
agent-consumable decisions packet with questions, evidence, and display-only
suggestion metadata.

The saved JSON keeps only explicit human decisions or comments:

- `id`
- `decision`
- `comment`
- `question`
- `explanation`
- `agent_next_step`
- `evidence_links`
- `suggested_decision`
- `suggestion_display_only: true`

Adaptive decisions also include:

- `queue_effects`
- `queue_state`
- `superseded_unreviewed_item_ids`

Superseded items remain unreviewed. They must not be treated as approvals.
