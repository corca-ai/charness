# Critique Review
Date: 2026-07-15

## Decision Under Review

Repair the copied global CLI's catalog backend resolution and make session and
generated routing guidance state the direct workflow, exact inventory command,
and command-failure action.

Packet Consumed: charness-artifacts/critique/2026-07-15-022604-packet.md

## Failure Angles

- An installed executable could still import from its bin directory, so source
  tests would pass while a consumer repository cannot run the catalog inventory.
- Routing text could retain a retired-command shape or leave the ordinary-task
  and nonzero-result actions underspecified.
- A brittle semantic detector could accept stale guidance or reject equivalent
  direct-action phrasing.

## Counterweight Pass

- Act before ship: repair the standalone loader and require direct-action,
  nonzero-result, and copied-CLI subprocess proof.
- Bundle the root source, generated setup guidance, and checked-in plugin mirror
  because each is a final consumer of the same replacement contract.
- Defer environment-variable sanitization in the subprocess test: the loader
  prepends the managed checkout and the current test environment has no
  `PYTHONPATH` or `PYTHONHOME`.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/setup_skill_routing_lib.py | action: fix | note: Charness-management detection had to remain distinct from complete direct-action and nonzero-result routing proof
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/setup/references/default-surfaces.md | action: document | note: default-surface guidance had to render the same direct action and command-failure rule as the runtime hook
- F3 | bin: over-worry | evidence: moderate | ref: tests/charness_cli/test_codex_cache_refresh.py | action: defer | note: environment-variable sanitization has no current evidence of affecting the isolated copied-CLI proof
- F4 | bin: bundle-anyway | evidence: strong | ref: docs/handoff.md | action: document | note: the handoff references must include the current retro digest that governs the next session

## Reviewer Tier Evidence

- Requested tier: high-leverage fresh-eye review.
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, fork_turns=none; service_tier=priority was requested by the repo contract but unavailable in the host spawn API.
- Host exposure state: requested_fields_sent
- Application state: unverified-by-host; the host accepted model, reasoning, and fork fields but exposed no provider-application metadata.

## Fresh-Eye Satisfaction

parent-delegated

Independent read-only reviewers covered installed-CLI portability, routing
wording, counterweight disposition, and the final semantic-parser resolution.
Each reviewer boundary fingerprint verified that the shared worktree and index
had no drift.

## Boundary Ownership

- Producer: the CLI loader produces the catalog backend import root; root routing sources produce the session instruction text.
- Consumer: copied global CLIs, SessionStart hooks, and setup-generated AGENTS guidance.
- Owning surface: `charness` loader plus root routing source and checked-in plugin-export sync.
- Verdict: owned-correctly
