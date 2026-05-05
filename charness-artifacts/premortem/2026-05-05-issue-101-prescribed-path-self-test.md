# Premortem: Issue #101 Prescribed-Path Self-Test
Date: 2026-05-05

## Decision

Close issue #101 after tightening `create-skill` and `impl` so skill self-tests,
scheduled workflows, delegated workflows, and external lookup contracts must
prove the path prescribed by checked or installed `SKILL.md`, not an author's
free-form smoke probe.

## Likely Misreads

- Treating the incident as Slack-specific instead of a general prescribed-path
  verification failure.
- Letting `create-skill` own authoring guidance while leaving `impl`
  verification able to accept producer-composed smoke tests.
- Adding a reference under `skills/public/` but forgetting checked-in plugin
  export sync.
- Treating a valid no-op result as proof even when the lookup path was skipped.

## Counterweight Triage

- Act before ship: none after delegated review. The cheap `impl` wording
  improvement for external lookup contracts was applied.
- Bundle anyway: include untracked reference, test, and plugin export files in
  the commit.
- Over-worry: broader redesign of skill validation is not needed for this
  incident slice.
- Valid but defer: executable scheduled-run reproduction can wait for Cautilus
  re-enable or a later scenario-registry slice.

## Proof

- Fresh-eye review: three parent-delegated reviewers found no content blocker.
- Deterministic gates passed for skill validation, public skill dogfood,
  public skill validation, packaging validation, packaging committed parity,
  markdown lint, doc links, command docs, secrets, ruff, py_compile, and focused
  pytest coverage.
- Wider pytest run before final wording fixes reported 550 passed, 4 skipped,
  with 2 wording-sensitive failures; focused reruns for those failures passed.
- Cautilus eval/proof was omitted from parent closeout per operator request;
  the repo adapter remains `run_mode: disabled`.

## Next Move

Commit, push to `main`, comment on issue #101 with the proof summary, and close
the issue.
