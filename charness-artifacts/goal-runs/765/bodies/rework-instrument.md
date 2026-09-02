<!-- charness-work-item-key: rework-instrument -->

## Objective

Let the repo observe consumer rework through the operator's own issue filing, without a new gate.

## Owned scope

- Add a `rework` label convention and a `Causing skill:` line to the issue skill's filing shape (`skills/public/issue/references/issue-shaping.md` and the create template).
- Teach `retro` to read `gh issue list --label rework` for the period and attribute per skill in its packet.
- The operator files at least one real rework issue against this Goal Run to prove the path end to end. #773 (Goal Run binding rigidity, causing skills achieve and issue) is the first instance; apply the label to it once it exists.

## Acceptance

- A retro packet shows the per-skill rework attribution for a period containing the operator's instance.
- No new gate, validator, or artifact schema.

## Focused verification

One retro run on the current period.

## Dependencies

None. First Work Item: instrument before the work so the run observes its own rework.

## Non-claims

No claim that this measures rework completely; it is the operator-side fact the usage-episode instrument could not provide.
