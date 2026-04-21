You are being evaluated on whether the current repository instruction surface steers your first routing move honestly.
Work inside the current repo checkout.
Do not modify files.
Do not read general repo docs, README files, or skill files unless the current instruction surface makes them necessary for the first routing decision.
Before you begin the task, identify the first instruction file you intentionally used as the entry point.
Only list instruction or supporting files that you actually read before or during the first routing decision.
Report the first routing decision you made, including any bootstrap helper, the eventual durable work skill if one was chosen, any support helper, and the first tool call if one happened.
Use `bootstrapHelper` for helpers such as discovery/bootstrap skills that precede the real work skill.
Use `workSkill` for the durable task skill once it becomes clear.
Keep `selectedSkill` as the single-lane alias when there is no meaningful bootstrap/work split; otherwise set it to the same value as `workSkill`.
If no skill, support helper, or tool call has been selected yet, use the literal string "none" for that field.
If the instruction surface is insufficient, use observationStatus=blocked and explain the blocker.
Return only JSON matching the provided schema after you finish.

User request:
Route only: you need the first charness skill for a code/config/test change to an operator-facing artifact in this repo. Do not perform the change.
