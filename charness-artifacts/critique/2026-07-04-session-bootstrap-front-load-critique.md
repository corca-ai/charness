# Session Bootstrap Front-Load Code Critique

## Execution

Fresh-Eye Satisfaction: `parent-delegated`.
Packet Consumed: `charness-artifacts/critique/2026-07-04-022919-packet.md`.
Target: `code-critique.md`.

## Reviewer Tier Evidence

- requested tier: `high-leverage`
- requested spawn fields: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
- host exposure state: unsupported
- application state: host exposes `model` only; angle + counterweight
  reviewers spawned as bounded fresh-eye subagents on `sonnet` (operator
  standing instruction: lower-power models for delegated work)

## Diff Scope

Session-start contract inversion: the SessionStart hook directive now
front-loads 3-branch routing (pickup → handoff-named workflow; capability
discovery → `find-skills`; otherwise → matching skill; `latest.*` as the
capability map), replacing the mandatory every-session `find-skills`
invocation. Touches the hook script, find-skills SKILL.md + session-start
reference, the AGENTS.md Start Here bullet + generated Skill Routing block,
render_skill_routing.py, eval_setup.py, host_hook_find_skills.py docstring,
plugin mirrors, and three pinning test files (inverted, not deleted).

## Capability at Stake

Removing a ~2.5k-token skill invocation most sessions paid to re-confirm a
cached inventory, WITHOUT regressing the issue-240 routing-miss class
("find-skills ran; handoff did not") the old mandate existed to prevent.

## Angles

- Michael Jackson (framing), Atul Gawande (operational), Jef Raskin
  (first-time-use across five simulated session openings) — bounded
  fresh-eye subagents; separate counterweight pass.

## Findings

### Act Before Ship (applied pre-commit)

- `docs/handoff.md:5` still encoded the OLD two-hop route
  ("Pickup = `find-skills` -> `handoff`") in the exact file branch 1 tells
  every agent to consult — found independently by two reviewers. Reworded to
  the one-hop route.

### Bundle Anyway (applied)

- Branch-1 wording ambiguity (mention+task message could read as pickup):
  added "(if the message also names a concrete task, the task governs)".
- No fallback for absent `docs/handoff.md` in non-charness repos (hook is
  user-level/global): added "skip this branch if the file doesn't exist".
- Savings claim was asserted with no arithmetic: added the token arithmetic
  (~+85 tokens/session directive vs ~2.5k-token skill invocation) to
  session-start-routing.md, honestly noting no traffic-mix dataset is cited.
- Staleness honesty: added a Boundary note that map staleness is
  judgment-only, the old de-facto refresher is gone, and the named follow-up
  (extend the `validate_find_skills_integration_claims` pattern) fires on
  recurrence, not first sight — per Floor-Addition Restraint.

### Over-Worry

- AGENTS.md/render drift test: verified byte-identical today; the existing
  `setup` inspect advisory (`review_existing_skill_routing`) already detects
  this class on demand — a standing pytest would duplicate it on first sight.

### Valid but Defer

- resume/clear matcher re-fires the directive mid-task: pre-existing (old
  directive used the identical matcher), self-correcting via preserved
  context; touch only on an observed incident.
- Deterministic staleness validator for `latest.*`: named follow-up on
  recurrence (see Bundle note above).
- `evals/cautilus/whole-repo-routing.fixture.json` still embeds the old
  phrasing as a synthetic demo case — eval-only, ask-before-run, zero live
  risk; add a new-shape case in a later eval pass.

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` Repeat Traps: mirror-vs-source
edit trap avoided (all edits on `skills/public`/`scripts/`, mirrors via
`sync_root_plugin_manifests.py`, verified byte-identical).

## Capability Gap

None new; the deliberately-rejected-then-adopted front-load is recorded with
its issue-240 lineage and three carried-over protections in
`session-start-routing.md`.

## Pre-Merge Action

All Act-Before-Ship + Bundle edits applied; hook e2e emits the corrected
directive; 39 focused tests green; handoff validator green. Deployment-lag
honesty: the LIVE hook runs from the managed checkout at v0.60.0 — this
change has no live effect until a release ships and `charness update` runs;
stated in the commit message and handoff.

## Next Move

Commit slice C after the achieve A/B finishes (its scratch config makes the
unique-basename doc-links check transiently red); then the full-gate
verification runs clean on the final tree.
