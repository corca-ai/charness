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

When a criterion is still vague, keep sharpening until these are clear:

- who experiences the result
- what behavior should happen
- under what conditions
- how the result will be observed
- what failure would look like

## Weak Success Criteria

Weak criteria sound nice but do not guide implementation:

- "Feels intuitive"
- "Works well"
- "Scales"
- "More robust"

These may appear as aspirations, but the spec must translate them into specific
checks.

## Pressure Rules

Do not stop at the first polished sentence.

- if the criterion could pass while users still fail, it is too vague
- if two implementers could build materially different behavior and both claim
  success, it is too vague
- if failure is not named, success is probably under-specified

## Acceptance Checks

Every important success criterion should imply at least one acceptance check:

- a manual verification step
- a scenario
- a testable behavior
- a negative case

If the repo supports executable specifications or established test surfaces,
promote the check into that form when practical.
