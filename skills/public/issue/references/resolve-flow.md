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
critique before close. See `causal-review.md` for the lenses, the subagent
contract, and the close-comment shape that carries the analysis forward.

Feature-class and deferred-work issues run a **pre-mutation resolution brief**
between ordering and design. The brief makes the proposed product or workflow
boundary visible in the transcript before any file or state mutation begins,
so scope and tradeoff disagreements can be caught while they are still cheap.
See `resolution-brief.md` for the brief template, the pause-vs-continue
rules, and the trivial-feature short-circuit.

Discuss with the user before implementation when the issue asks for a decision
outside the agent's authority, such as product direction, policy, scope cuts,
secret access, external billing, or irreversible publication. For
feature-class and deferred-work issues, the resolution brief is the place
where this surfaces; for `question` and `decision-needed`, this is the
primary routing.

Target repo is durable workflow state. Once named or first-resolved, retries
within the same session reuse it; if the prior target becomes unreachable,
surface `target_unavailable: <full_name>` and stop. Closeout for `issue new`
must render only from the verified `{repo, number, url}` ledger. See
`closeout-discipline.md` for the full contract.

For `issue resolve`, make GitHub auto-close the normal closeout path when the
backend supports it. In PR-based work, put explicit close keywords and the
classification-specific closeout summary in the PR body so merge closes the
issue. In direct-to-default work, put the same keywords and summary in the
commit body before push. If the repository squashes or rewrites merge commits,
verify the final merge body still contains the close keywords before treating
the issue as closable. Manual close-with-comment is reserved for cases where
auto-close is unsupported or did not close after the remote state was verified.
If direct work is bundled into a release helper run, pass the resolved issue
numbers to the helper and require its post-push issue verification payload
before reporting the issue resolved.

Use `issue_tool.py verify-closeout` as the ordinary issue-resolution final gate.
Without `--expect-state`, the verifier can only report `carrier_verified` for a
pre-push or pre-merge carrier audit. Final handoff requires
`--expect-state CLOSED` and `status: verified`; otherwise the issue lifecycle is
not closed.
