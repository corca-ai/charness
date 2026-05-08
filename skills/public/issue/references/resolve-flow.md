# Resolve Flow

`issue resolve` turns GitHub issues into implementation work.

GitHub owns issue identity and freshness:

- omitted selector means newest open GitHub issue in the target repo by created
  date
- local artifacts and session memory may provide context, but never select the
  issue
- issue body, comments, labels, state, and linked PR state should be read from
  GitHub before design

Resolution order should reduce uncertainty. Start with issues that clarify
shared contracts, unblock later issues, or remove failing gates that would make
the rest hard to verify.

Discuss with the user before implementation when the issue asks for a decision
outside the agent's authority, such as product direction, policy, scope cuts,
secret access, external billing, or irreversible publication.
