# Critique Review
Date: 2026-06-15

## Decision Under Review

Remove `gws-cli` as a repo-owned integration and make external-tool
healthchecks optional when `detect`, readiness, or consumer probes own the real
contract.

## Failure Angles

- Problem framing: removing the manifest is incomplete if repo scaffolds still
  teach new repos to bind `gws-cli`.
- Diagnostic: structured JSON visibility is not enough if the default
  operator-facing doctor/update output collapses an omitted healthcheck into a
  plain `ok`.
- Operational checklist: generated/current artifacts must not keep advertising
  `gws-cli` as a live external integration.

## Counterweight Pass

- The scaffold leak and human-output silence were real blockers and were fixed
  in this slice.
- Making help-prose healthcheck detection fatal is overreach for this slice:
  the known brittle `nose`, `pry`, and `specdown` checks are removed, optional
  healthchecks are explicit, and future policy hardening can be done separately.
- Historical debug/quality artifacts that mention `gws-cli` remain historical
  records rather than current operator contracts.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness:558 | action: fix | note: capability init still scaffolded `gws.default` and provider `gws-cli`; fixed by removing the Google Workspace placeholder and asserting Slack/GitHub-only defaults
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/doctor.py:162 | action: fix | note: non-JSON doctor/update output hid omitted healthchecks; fixed by rendering `healthcheck=not-configured`
- F3 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/design-studies/issue-57/capability-spectrum.md:43 | action: fix | note: current generated/narrative artifacts still advertised `gws-cli`; regenerated/updated current surfaces
- F4 | bin: over-worry | evidence: moderate | ref: scripts/validate_integrations.py:184 | action: document | note: making help-prose healthcheck advisory fatal now would broaden this removal into a separate validator-hardening policy slice

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: host returned spawned reviewer ids and completed reviewer messages; provider-side application of requested fields is not exposed.

## Fresh-Eye Satisfaction

parent-delegated. The host exposed `multi_agent_v1.spawn_agent`; three angle
reviewers and one separate counterweight reviewer completed read-only reviews
against `charness-artifacts/critique/2026-06-15-104956-packet.md`.
