# Host Log Probe: Shown-Set Session Records

Goal: charness-artifacts/goals/2026-08-12-shown-set-session-records.md
Date: 2026-08-12

## Command

`python3 skills/public/retro/scripts/probe_host_logs.py --repo-root . --format markdown`

## Result

- Goal metric window: not requested; the probe reports thread-wide pressure,
  not a goal-scoped total.
- Measured thread-wide snapshot: 920 tokens, 183 function calls, 696 custom
  tool calls, 6 context compactions, and delegated-agent activity of spawn=35,
  wait=78, close=0.
- Proxy activity: no repeated broad gates or VCS commands were reported.

## Interpretation

This is a host-log availability check, not a goal-window measurement and not a
claim about cost of this slice. No session-file path or activation/completion
window was available for a retrospective goal-scoped calculation.
