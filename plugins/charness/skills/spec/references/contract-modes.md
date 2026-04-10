# Contract Shapes

`spec` may need different contract shapes during execution.

These are shaping heuristics for the skill designer and operator. They are not
meant to become a mandatory user-facing mode menu in every invocation.

## Bias Toward Upfront Stabilization

Use when implementation churn would be expensive and the key behavior should be
explicit before coding starts.

Typical signals:

- schema or storage changes
- migrations
- API contracts
- changes to legacy systems with costly rollback

Default posture:

- define the slice clearly before implementation
- reduce ambiguity aggressively up front
- leave only safe deferred decisions visible

## Bias Toward Braided Work

Use when part of the contract will emerge while building.

Typical signals:

- prompts and agent workflows
- interaction or UX shaping
- new integrations
- uncertain operator workflows

Default posture:

- write a thin but explicit contract for the current slice
- label unresolved items as probes
- update the spec as implementation resolves those probes

## Bias Toward Executable Checks

Use when the repo already treats executable checks as part of the contract.

Typical signals:

- specdown
- behavior specs
- acceptance tests written before or alongside code

Default posture:

- keep prose and executable checks synchronized
- promote important acceptance checks into executable form when practical
- do not assume every repo needs this mode
