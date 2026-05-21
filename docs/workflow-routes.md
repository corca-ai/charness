# Workflow Routes

This guide owns the route and procedure examples that would make the README too
heavy as a first-touch surface.

## Starting A New Project

1. Start with `ideation`: describe the rough idea, then let the agent help you
   brainstorm, challenge, and clarify it. It can also route to `gather` when
   outside context would sharpen the concept.
2. Once the concept is concrete enough, ask the agent to create a directory and
   use `setup`. It should propose the first repo surface, including
   [AGENTS.md](../AGENTS.md), so future sessions can use `charness` naturally.
3. Start a fresh session in the new directory. Ask the agent to turn the
   direction into a buildable contract. Route: `spec`, with critique-style
   review when the decision is risky enough.
4. Ask for the first implementation slice. Route: `impl`, with verification,
   debugging, and critique review pulled in as needed.
5. If the agent moved in a frustrating direction, or found a pattern future
   sessions should repeat, ask for a retro. Route: `retro`.
6. Once enough code or docs exist, ask for a quality check. Route: `quality`,
   covering repo posture such as missing gates, brittle tests, duplicate code,
   security risks, documentation drift, and skill or script ergonomics.

Retros can trigger automatically when a correction exposes a real workflow miss
or when repo adapter rules require one, but asking explicitly gives the agent a
stronger improvement loop. For prompt- or behavior-affecting changes,
[`cautilus`](https://github.com/corca-ai/cautilus) can provide
evaluator-backed scenario review when installed and configured.

## Working In An Existing Repo

1. If the repo has not been initialized with `charness`, ask the agent to use
   `setup` first. It should normalize [AGENTS.md](../AGENTS.md) and related
   operating surfaces without turning the repo into a generic template.
2. Ask for the concrete work directly: `Implement this`, fix a failing test, or
   `Debug this behavior`. Routes: `impl` or `debug`.
3. If the task is under-specified, ask the agent to shape the contract before
   coding. Route: `spec`, with critique review when the change is risky.
4. When you want to explain progress, rewrite the repo story, or prepare a
   human-facing update, ask for that communication. Routes: `narrative` or
   `announcement`.
5. When the next session needs context, or when you want to review what the
   agent did and why, ask for a handoff or review loop. Routes: `handoff` or
   `hitl`.
6. When the repo needs a stronger quality bar, ask for quality review or
   follow-up gates. Route: `quality`, with `retro` when the lesson should
   persist.

## Direct Invocation

Normal prompts should be enough after setup, but direct invocation is useful
when you already know the workflow.

- Claude Code: `/charness:quality`, `/charness:narrative`, and similar.
- Codex: `$charness:quality`, `$charness:narrative`, and similar.
