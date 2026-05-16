# Handoff Stale Refresh Critique

- Date: 2026-05-16
- Target: `docs/handoff.md` stale cleanup and current pickup rewrite
- Fresh-Eye Satisfaction: blocked
- Host Signal: active Codex tool contract only permits `spawn_agent` when the current task asks for subagent delegation; this slice used live GitHub/Git state plus deterministic validators.

## Change

`docs/handoff.md` was rewritten from a long historical queue into a short
current-state pickup pointer. Closed or stale historical work moved out of the
active queue; live issue state, local unpublished commits, gather repair
direction, and user-decision items now drive the next session.

## Angles

- State accuracy: checked the handoff against `git status`, local commits ahead
  of `origin/main`, and live GitHub issues #168/#169.
- Decision boundary: separated autonomous local follow-through from user or
  maintainer decisions such as publishing the 7 ahead commits and choosing #168
  scope.
- Gather continuity: preserved the intended support-skill direction while
  honestly recording that `defuddle` is not installed on this machine.
- Counterweight: kept historical issues out of the handoff unless they change
  the next action.

## Counterweight Triage

### Act Before Ship

1. Do not close #169 from the handoff alone.
   - Local commits exist, but GitHub cannot verify them until the branch is
     pushed or a PR lands.

2. Keep #168 as discussion, not implementation.
   - The issue body explicitly frames it as a discussion starter and asks for
     methodology choices before a first experiment.

### Valid But Defer

1. A live `defuddle` dogfood run can wait until the binary is installed or
   exposed through a supported runtime route.

2. Full gather acquisition repair remains blocked on the implementation
   contract requested by the prior gather critique.

### Over-Worry

1. Replaying old mutation/Cautilus history in the handoff would add noise.
   - The owning artifacts and GitHub history are better reload points when a
     fresh signal references that work.

## Proof

- `gh issue list` shows #168 and #169 as the only live open issues.
- `gh issue view 168` confirms #168 is a discussion starter.
- `python3 scripts/plan_cautilus_proof.py --repo-root . --json` reports
  `next_action: none`, `run_mode: ask`, and a truth-surface scenario review
  follow-up for `docs/handoff.md`.
- `python3 scripts/check_doc_links.py --repo-root .`
- `./scripts/check-markdown.sh`
- `python3 scripts/validate_handoff_artifact.py --repo-root .`

## Scenario Review

1. New-session pickup scenario:
   - The prior handoff could route a maintainer into stale closed-issue history
     before live state. The refreshed handoff puts `find-skills`, live Git,
     live GitHub issues, and the unpublished-commit warning first.

2. Gather continuation scenario:
   - The prior handoff buried gather repair under older mutation/Cautilus
     queues. The refreshed handoff points directly to the gather repair
     critique, preserves the support-skill acquisition direction, and records
     that live `defuddle` proof is still absent on this machine.
