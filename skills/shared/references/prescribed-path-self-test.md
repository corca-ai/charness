# Prescribed Path Self-Test

Use this when a skill package claims that a self-test, smoke test, schedule,
event trigger, or external lookup proves the skill is ready for another agent
to run later.

## Rule

A passing self-test is evidence only when it exercises the path the next agent
will actually have:

- start from the checked or installed `SKILL.md`, not the author's private
  memory of what worked
- run the commands, query templates, selectors, adapter names, event payloads,
  and fallback rules that `SKILL.md` prescribes
- record the raw provider response, checked fixture, or command artifact before
  choosing a stable identification signal
- compare that raw shape against the next-turn instructions field by field
- promote any successful free-form probe into the skill contract before calling
  it proof

The issue is not whether an author can make the external system respond. The
issue is whether a later model, reading only the skill contract and local
artifacts, can reproduce the same retrieval and decision path.

## Common False Pass

The author writes a flexible search or smoke command while developing the skill.
It finds the right source item and the run is marked ready. The checked
`SKILL.md` then describes a narrower or different identification signal. The
first scheduled or delegated run sees only `SKILL.md`, cannot reproduce the
author's search, and silently takes the wrong branch.

This is especially likely when:

- parent or event messages contain opaque ids instead of human-readable team,
  repo, project, or customer names
- a search endpoint returns useful surrounding context that the direct event
  payload does not include
- a workflow-bot, scheduler, or integration owns the parent message text
- a no-op result is a valid output, so `[SILENT]`, empty JSON, or "no changes"
  can hide that the prescribed lookup path was skipped

## Minimum Evidence

Record enough evidence that a reviewer can tell which path was proved:

- skill path or installed export path that the test started from
- exact trigger input, event payload, command, or query template used
- raw external response excerpt or fixture path that contains the fields the
  contract relies on
- the stable field chosen as the source identity or selector
- the branch that proves a no-op result was reached through the prescribed
  path, not by skipping the lookup

When live credentials or the real scheduler are unavailable, mark the seam
unverified instead of replacing it with a producer-composed smoke test.
