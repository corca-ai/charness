# Charness Handoff

## Workflow Trigger

- **A shaped goal is READY TO RUN.** Both activation items are settled — external
  side effects approved for that goal, and Lane C decided as a non-blocking
  advisory. Activate it directly:
  `/goal @charness-artifacts/goals/2026-08-03-repair-the-commands-the-skills-tell-agents-to-run.md`

## Continuation Capability

- **The round that reads the REPAIRS is where the class comes back.** Twice last
  run a round-1 repair on a proof surface shipped the defect it was repairing.
  Round 1 could not see either — it was reviewing code that did not exist yet.
- **Build test inputs from the source constant, never by retyping.** A fixture
  spelled the way the matcher wants is how this whole class hides. Three
  instances so far: #471's synthetic `AGENTS.md`, a decline-record test, and a
  probe that re-implemented the exit line it was supposed to prove.
- **Adversarial verification, defaulting to refuted, killed 11 of 14 findings.**
  Surveyors asked to find inert rules will find them.
- **Cover new failure branches as you write them.** The pre-push mutation lane
  refused four times last run, always correctly.

## Current State

- `main` is at the commit below, local backlog empty. Re-check remote CI rather
  than trusting this line: `gh run list --limit 3`.
- **#471 / #473 / #474 / #475 / #476 all CLOSED.** The delegation authorization
  ladder is live (`AGENTS.md`, else `.agents/subagent-delegation.json`, else ask
  once); the dup ratchet warns at the edit; `--fail-on-pre-rule-refusal` is an
  armed, mutation-checked tripwire; the `setup` template now satisfies both
  readers of the contract.
- **The 2026-08-02 sweep is checked in** — 197 units assigned, 172 read, 25
  unread, 1 confirmed `cannot-fire` repaired. It HAD the 13 above and lost them:
  verifiers refuted "inert" by exhibiting a DIFFERENT working path, which proves
  nothing about the path the document told the agent to run.
- Still open and untouched: the **E-cluster** (most expensive lane), D41–D49,
  `parse_created_date`'s uncorroborated consumers.

## Next Session

1. **13 shipped commands cannot run.** A skill reference says
   `<repo-root>/scripts/X.py` while the file is at
   `skills/public/<skill>/scripts/X.py`; an agent following the instruction gets
   "No such file". Measured 2026-08-02 over every shipped skill `.md`: 91
   `$SKILL_DIR` refs resolve cleanly, 13 are broken here AND everywhere, 9 point
   at charness scripts absent in a consuming repo, 0 reference a missing file.
   That is the waiting goal.
2. **#475's behavioural half is still an OPEN operator decision.** Nobody has
   observed an agent ask-and-spawn in a repo that never ran `setup`. The command
   is in the completed goal's `## User Verification Instructions`. Reopen #475 if
   the re-run does not ask.
3. **#476 was fixed non-retroactively.** Consuming repos already set up from the
   old template still read as not-adopted. That is the deliberate cost; the
   marker-widening option is the follow-up if one reports an inert floor.
4. **A `completed` closeout gate is not broad proof.** Last run's gate said
   `completed` while a test was failing. Run
   `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only` and
   record the number.

## Discuss

- **Settled for the waiting goal only**: push, issue-filing, and issue-closing
  are approved there, and Lane C ships an advisory rather than a gate. Neither
  decision carries past that goal.
- **Open: which spelling of the delegation contract wins for EXISTING consumers.**
  Widening the markers would flip every already-set-up repo at once, against a
  population that cannot be counted from this tree — which is what D49 forbids.
  Reopen only with a real observation to measure against.
- **A read-only check and an irreversible boundary deserve different teeth** — D48
  left `drift` alone and refused at publish; still open for other gates.

## References

- [waiting goal](../charness-artifacts/goals/2026-08-03-repair-the-commands-the-skills-tell-agents-to-run.md) · [completed goal](../charness-artifacts/goals/2026-08-03-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md) · [retro](../charness-artifacts/retro/2026-08-02-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md) · [the sweep](../charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md)
- critiques: [Lane A ladder](../charness-artifacts/critique/2026-08-02-lane-a-the-delegation-authorization-ladder.md) · [Lanes B and C](../charness-artifacts/critique/2026-08-02-lanes-b-and-c-sweep-and-edit-time-advisory.md)
- [deferred decisions](./deferred-decisions.md) (D45–D49) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
