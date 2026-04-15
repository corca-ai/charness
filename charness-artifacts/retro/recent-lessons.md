# Recent Retro Lessons

## Current Focus

- This slice implemented all quality dogfood follow-ups from `temp-log.txt`: focused upstream release coverage, an advisory unfloored-file coverage inventory, an advisory HITL handoff inventory for `NON_AUTOMATABLE` quality recommendations, and refreshed quality/handoff state.

## Repeat Traps

- The first full review was run before `latest.md` had the new HITL fields, so `inventory-quality-handoff` correctly reported an advisory finding that was already known.
- The first full review also hit a transient runtime-budget failure. Re-running was the right answer, but the quality artifact briefly captured the failed state and then needed another update.

## Next-Time Checklist

- workflow: when adding an advisory inventory, run it directly against the artifact before paying for the full quality review.
- capability: keep `inventory-quality-handoff` advisory through at least one more `NON_AUTOMATABLE` dogfood example before considering a hard gate.
- memory: next quality slice should start from the unfloored-file inventory rather than rediscovering weak coverage files.

## Sources

- `charness-artifacts/retro/2026-04-15-quality-handoff-inventory.md`
