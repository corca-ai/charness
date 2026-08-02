# Charness Handoff

## Workflow Trigger

- **No shaped goal is waiting.** The 2026-08-03 three-lane goal completed
  (#475 / #473 / #474 all closed). Start from `## Next Session` below, or shape a
  new goal with `/achieve <outcome>`.

## Continuation Capability

- **The round that reads the REPAIRS is where the class comes back.** Twice this
  run a round-1 repair on a proof surface shipped the defect it was repairing:
  a `delegation signal:` heading that could not fire on the record the contract
  prescribes, and a `blocked_kind` field the operator-facing advisory never read.
  Neither was visible to round 1 — it was reviewing code that did not exist yet.
- **Build test inputs from the source constant, never by retyping.** A fixture
  that spells a string the way the matcher wants is how the whole class hides.
  Two instances this run: a decline-record test that hand-built a two-line form
  appearing nowhere in the contract, and a `#473` probe that re-implemented
  `main`'s exit line and would have passed with `main` deleted.
- **Adversarial verification refuted 11 of 14 sweep findings.** Surveyor agents
  asked to find inert rules will find them. Without a refute-by-default verify
  stage, that sweep would have checked in a confident wrong measurement.

## Current State

- `main` is at the commit below, local backlog empty. Re-check remote CI state
  rather than trusting this line: `gh run list --limit 3`.
- **The delegation authorization ladder is LIVE** (#475 closed). `AGENTS.md`,
  else `.agents/subagent-delegation.json`, else ask once and persist. Anything
  unreadable resolves to `ask`, never `granted`. Both shipped adoption detectors
  walk it, so a rung-2 grant is not read as never-adopted. Resolve it with
  `python3 skills/shared/scripts/resolve_subagent_delegation.py resolve --repo-root .`
- **The dup ratchet now warns at the edit** (#474 closed), once per file per HEAD,
  on `hookSpecificOutput.additionalContext`. It caught its own author.
- **#473 closed as an armed tripwire**, not deleted — a forced-scope probe drives
  the real `main`, mutation-checked.
- **The sweep is checked in** (197 units assigned, 172 read, 25 unread and
  counted, 1 confirmed `cannot-fire` repaired). Still open and untouched: the
  **E-cluster**, D41–D49, `parse_created_date`'s uncorroborated consumers.

## Next Session

1. **#475's behavioural half is an OPEN operator decision.** The mechanism is
   proven; nobody has yet seen an agent in a block-less repo ask-and-spawn. The
   command and expected output are in the completed goal's
   `## User Verification Instructions`. Reopen #475 if the re-run does not ask.
2. **#476 is the same class one rung up.** The shipped compact `AGENTS.md`
   template carries the section marker but not the contract sentence, so a repo
   that DID run `setup` can read as never-adopted. Not repaired because both
   directions newly APPLY floors to repos previously outside them — it needs a
   measured count and a recorded disposition first (D49).
3. **The sweep's consuming-repo reading is under-measured** — refuted claims were
   "inert where installed", answered from the AUTHORING repo. Needs a consuming
   repo, unreachable from this tree.
4. **A `completed` closeout gate is still not broad proof.** This run's gate
   reported `completed` while a test was failing; the explicit
   `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only` found
   it (1 failed, 6675 passed). Run it and record the number.

## Discuss

- **Settled (#475): who grants the standing delegation request.** The three-rung
  ladder shipped. Reopen only if the per-repo question proves more friction than
  the never-ran-`setup` refusal it replaced.
- **Open (#476): which spelling of the delegation contract wins** — the template
  gains the marker sentence, or the markers widen to accept the standing-request
  spelling. Both newly hold repos to floors they were outside; measure first.
- **A read-only check and an irreversible boundary deserve different teeth** — D48
  left `drift` alone and refused at publish; still open for other gates.

## References

- [completed goal](../charness-artifacts/goals/2026-08-03-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md) · [retro](../charness-artifacts/retro/2026-08-02-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md) · [the sweep](../charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md)
- critiques: [Lane A ladder](../charness-artifacts/critique/2026-08-02-lane-a-the-delegation-authorization-ladder.md) · [Lanes B and C](../charness-artifacts/critique/2026-08-02-lanes-b-and-c-sweep-and-edit-time-advisory.md)
- [deferred decisions](./deferred-decisions.md) (D45–D49) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
