# Success Criteria

Success criteria are the heart of the spec.

## Good Success Criteria

Good criteria are:

- observable
- testable
- bounded
- tied to user or operator value

Examples:

- "User can create a project from the CLI and see it listed immediately."
- "The agent can run the flow without manual file edits after setup."
- "Invalid input returns a clear error instead of partially mutating state."

## Weak Success Criteria

Weak criteria sound nice but do not guide implementation:

- "Feels intuitive"
- "Works well"
- "Scales"
- "More robust"

These may appear as aspirations, but the spec must translate them into specific
checks.

## Acceptance Checks

Every important success criterion should imply at least one acceptance check:

- a manual verification step
- a scenario
- a testable behavior
- a negative case
