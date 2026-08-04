# Trigger And Persistence Rules

`retro` should not be purely opt-in.

## Auto-Retro Trigger

Run a short `session` retro before resuming the main task when all of these are
true:

1. the user correctly points out a missed issue, wrong assumption, or missing
   gate
2. the miss is something the current workflow should plausibly have caught
3. the user did not explicitly ask to skip retrospective cleanup

Examples:

- assuming a checked-in hook was active without checking clone-local git config
- missing an obvious repo-owned validator that should have existed
- treating a repo shape or contract as enforced when it was only documented
- treating a present invariant as absent because no single gate, type, or doc made the invariant easy for a fresh reader to verify

Do not trigger on:

- preference changes
- new context the user had not provided yet
- ordinary product disagreement
- scope changes that are not retrospective misses

## Persistence Rule

Every retro must tell the operator whether it persisted.

Allowed forms:

- `Persisted: yes: charness-artifacts/retro/retro.md`
- `Persisted: no: chat-only quick retro`
- `Persisted: no: user asked to skip durable artifact update`

If a durable home exists, prefer writing or updating it before moving on.

For an achieve closeout, pass `--goal-path` to the persistence helper. The
path must resolve to the owning canonical goal artifact, and the retro must
contain exactly one `Goal:` field in the preamble after its optional document
title, whose trimmed value is that repo-relative path or its filename slug. A
slug is accepted as input for compatibility, but the helper writes the
canonical repo-relative path form. This opt-in check runs before the retro,
summary, lesson index, event, or output-directory writes; omit the flag for
ordinary session or release-trigger retros.
