# Resolve Flow

`issue resolve` turns GitHub issues into implementation work.

GitHub owns issue identity and freshness:

- omitted selector means newest open GitHub issue in the target repo by created
  date
- local artifacts and session memory may provide context, but never select the
  issue
- issue body, comments, labels, state, and linked PR state should be read from
  GitHub before design

Resolution order is a generative sequence in Christopher Alexander's sense:
each move should create the conditions that make the next move cheaper and
more correct. Start with issues that clarify shared contracts, unblock later
issues, or remove failing gates that would make the rest hard to verify.

Bug-class issues run a causal review subagent before design and a resolution
premortem before close. See `causal-review.md` for the lenses, the subagent
contract, and the close-comment shape that carries the analysis forward.

Discuss with the user before implementation when the issue asks for a decision
outside the agent's authority, such as product direction, policy, scope cuts,
secret access, external billing, or irreversible publication.

Target repo is durable workflow state. Once named or first-resolved, retries
within the same session reuse it; if the prior target becomes unreachable,
surface `target_unavailable: <full_name>` and stop. Closeout for `issue new`
must render only from the verified `{repo, number, url}` ledger. See
`closeout-discipline.md` for the full contract.
