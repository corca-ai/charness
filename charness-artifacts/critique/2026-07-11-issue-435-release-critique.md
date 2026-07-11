# Critique Review
Date: 2026-07-11

## Decision Under Review

Resolve issue #435 and publish patch release v0.66.1. The change removes the
ambiguous `--no-verify` spelling, adds the explicitly mutating
`--skip-readback` spelling, refuses exact placeholder titles `x` and `test`
before any backend call unless intentionally overridden, and synchronizes the
public skill, tests, attention-state declaration, and installed plugin mirror.

## Release Scope

- Current version: 0.66.0.
- Target version: 0.66.1.
- Bump rationale: patch. This is a compatible safety repair to an existing
  issue-create workflow; it adds no new skill, package id, or migration.
- Operator story: update with `charness update`. Existing intentional `x` or
  `test` titles require `--allow-placeholder-title`; callers that deliberately
  skip readback use `--skip-readback`, which still creates the issue.

## Surface-Lock Inventory

- Consumer behavior: `skills/public/issue/scripts/issue_create.py` and its
  checked-in plugin mirror.
- Guidance: the public issue `SKILL.md` and `references/issue-backend.md`, plus
  their plugin mirrors.
- Verification: `tests/quality_gates/test_issue_create.py`.
- Attention state: the issue-create entry in
  `skills/public/quality/references/attention-state-visibility.json` and its
  mirror.
- Release-owned surfaces still to mutate: packaging/plugin marketplace
  versions, release artifact, tag, public GitHub release, issue state, and the
  maintainer install refresh.

## Failure Angles

- Gawande operational: a correct local patch would still be unpublished if the
  release helper did not bump, sync, verify, push, publish, and refresh the
  installed copy.
- Raskin/Minto first use: a renamed flag could remain misleading if help and
  narrative guidance did not say that skipping readback still creates, or if
  verification guidance still suggested a second create.
- Weinberg recurrence: a source-only guard would be weak without zero-backend
  tests for every named placeholder, exact create-then-view proof, synchronized
  mirrors, and an updated attention-state declaration.

## Counterweight Pass

- Act Before Ship: the release helper must create v0.66.1 release state and
  final public/readback proof; pre-critique 0.66.0 manifests are expected input,
  not evidence that v0.66.1 shipped.
- Act Before Ship, resolved in the implementation slice: the focused tests now
  cover both `x` and `test` with zero backend calls and assert a normal verified
  path is exactly `create` then `view`, never a second create.
- Valid but Defer: the removed legacy spelling exits through argparse stderr
  rather than a structured JSON migration error. It cannot mutate, and a hidden
  rejecting alias would add maintenance surface without improving the reported
  safety boundary.
- Over-Worry: copying the exact “never second create” sentence into CLI help,
  broad minimum-title or alias guards, broad CLI inventory, and provider/model
  agent-choice proof are not required for this bounded patch.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: packaging/charness.json:5 | action: fix | note: the release helper must bump and synchronize v0.66.1 before publish.
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/latest.md:1 | action: fix | note: the release helper must persist v0.66.1 public and issue-closeout proof.
- F3 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_issue_create.py | action: defer | note: a structured migration error for removed --no-verify is optional ergonomics, not a safety blocker.
- F4 | bin: over-worry | evidence: moderate | ref: skills/public/issue/scripts/issue_create.py | action: document | note: CLI help already says creation still occurs; narrative docs own the never-second-create explanation.
- F5 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_issue_create.py | action: fix | note: resolved before release by explicit x/test zero-call coverage and exact create-view sequence proof.
- F6 | bin: over-worry | evidence: strong | ref: skills/public/issue/references/issue-backend.md | action: defer | note: broad placeholder aliases or minimum title length would exceed the reporter JTBD and risk false positives.
- F7 | bin: over-worry | evidence: strong | ref: charness-artifacts/critique/2026-07-11-issue-435-release-packet.md | action: defer | note: broad CLI inventory and provider/model proof are outside this patch release boundary.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5; reasoning_effort=medium;
  service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: not claimed; the host returned completed findings but no
  provider-applied tier metadata.

## Fresh-Eye Satisfaction

parent-delegated. Three distinct angle reviewers and one separate counterweight
reviewer completed read-only reviews. Parent-side fingerprint verification
reported `ok: true` with no drift after every reviewer.

## Packet Consumed

`charness-artifacts/critique/2026-07-11-issue-435-release-packet.md`

## Boundary Ownership

- Producer: `issue_tool.py create` produces the external mutation and its
  readback ledger.
- Consumer: the issue skill closeout and downstream operator consume that
  ledger to decide whether creation is verified.
- Owning surface: public issue skill capability, synchronized into the plugin
  export; release publication remains owned by the release helper.
- Verdict: owned-correctly

## Deliberately Not Doing

- No time-window body-hash deduplication cache.
- No broad placeholder-title or minimum-length policy.
- No provider/model agent-choice claim; local fake-backend behavior proof is
  the distinct evidence channel for issue #435.

## Next Move

Run the focused and repo release gates, then publish v0.66.1 through the
repo-owned release helper with `--close-issue 435` and this critique artifact.
