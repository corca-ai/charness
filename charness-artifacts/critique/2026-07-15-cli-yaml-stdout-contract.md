# CLI YAML stdout contract
Date: 2026-07-15

## Decision Under Review

Make every operational root `charness` stdout payload a single YAML document.
Remove `--json` from the public root CLI surface, while silently ignoring the
legacy flag wherever it is supplied.

Packet consumed: `charness-artifacts/critique/cli-yaml-stdout-contract-packet.md`

## Failure Angles

- A per-handler conversion could leave one human or JSON root-output branch
  reachable, particularly in failure, update-progress, or nested-command paths.
- Guidance, generated references, evaluator fixtures, and plugin mirrors could
  keep teaching `--json` after the parser stops advertising it.
- Treating private helper JSON protocols as public root CLI behavior could break
  internal subprocess boundaries without advancing the YAML contract.

## Counterweight Pass

- Independent counterweight review found no reachable root-output escape: the
  argv filter removes exact legacy flags before argparse and root handlers emit
  payloads via `emit_yaml`.
- The documentation/export reviewer confirmed the generated reference now covers
  catalog and session-capture, and the remaining JSON flags name private scripts.
- Exhaustive legacy-flag tests for every subcommand are over-worry: central
  stripping plus version/task compatibility tests cover the distinct behavior.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness; evals/cautilus/whole-repo-routing.fixture.json | action: fix | note: Central YAML emission needed matching legacy-flag stripping and stale evaluator guidance removal before this contract could ship.
- F2 | bin: bundle-anyway | evidence: strong | ref: scripts/render_cli_reference.py; docs/generated/cli-reference.md | action: fix | note: Generated reference wording and omitted catalog/session-capture help surfaces needed correction to make the public contract discoverable.
- F3 | bin: over-worry | evidence: moderate | ref: tests/charness_cli/test_task_envelope.py; charness | action: defer | note: Per-subcommand legacy-flag matrix adds no independent proof beyond the global argv filter and focused compatibility tests.
- F4 | bin: valid-but-defer | evidence: strong | ref: scripts/doctor.py; skills/public/setup/scripts/render_skill_routing.py | action: document | note: Private helper JSON remains an intentional subprocess protocol and is outside the root `charness` stdout contract.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: host metadata-hidden; independent reviewers completed and returned read-only findings.

## Fresh-Eye Satisfaction

parent-delegated. Documentation/export and counterweight reviewers ran from
separate contexts; parent fingerprint verification reported no drift for both
post-review snapshots.

## Boundary Ownership

- Producer: root `charness` CLI operation handlers.
- Consumer: operators and agents parsing root command stdout.
- Owning surface: root CLI entrypoint and its generated public command reference.
- Verdict: owned-correctly.
