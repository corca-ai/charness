# Named-Target Verification

Operator-supplied target names — instance, service, branch, ref, env-var alias,
config profile, channel ID, room ID, deploy environment — are *references*,
not facts. The named target may not be the live one, may be in a broken state,
or may be bound to a different workspace than the operator means. Acting on
the name without verifying the runtime state silently swallows operator
commands and turns one bug into a multi-round retry loop.

Use this reference when the slice runs an operator command framed by a target
name, or frames a debug hypothesis around a named target.

## Verify Before Acting

Before running the operator command or anchoring the hypothesis, run the
cheapest available probe of the runtime state behind the name:

- service or instance: ask the host's process supervisor which unit is
  actually running, using whatever supervisor the host uses (`systemctl`,
  `launchctl`, `pm2`, `docker`, `kubectl`, or similar). Confirm the
  unit is in a healthy running state, not restarting, crashing, or absent.
- branch or ref: `git rev-parse <name>` and `git rev-parse origin/<name>`,
  and the SHA of whichever ref the deploy or runtime actually consumes.
  Confirm the local name, the remote-tracking name, and the deployed name
  all point at the SHA the operator means.
- env var or alias: read the actual `.env`, secrets file, or credential
  resolver output the runtime would consume. Do not assume the documented
  default applies, and do not assume an alias resolves to the same value
  across instances.
- channel, room, or workspace ID: check the bot's membership and which
  workspace, project, or instance is bound to that ID. The same human-readable
  name often exists in more than one workspace.

The probe should usually take 5 seconds. If it takes longer, that is a signal
that the runtime supervisor or resolver itself is unhealthy, and the slice
should pause to record that before continuing.

## When To Use This

- `impl` operator commands that target a named instance, service, profile,
  branch, or environment. Verify the named target is the live one before the
  mutation runs, not after the first failed retry.
- `debug` hypotheses that blame a specific named target ("the `prod` instance
  is broken", "the `main` branch is out of date", "the bot is in `#channel`").
  Verify the runtime state of the name before reasoning further; otherwise the
  next several hypotheses inherit the wrong premise.
- any handoff that includes a named target. State the verified runtime fact
  ("`<service>-active` is the running unit; `<service>-prod` is in a
  restart loop") so the next slice cannot quietly act on the wrong one.

## Recording The Result

When the probe disconfirms the operator's mental model, treat that as the
first finding:

- record what the operator named, what the live runtime state actually is,
  and which target the next move should act on
- if the named-but-not-live target swallowed prior commands, note the
  resulting retry loop in the debug artifact's `Observed Facts` so the same
  trap is recognizable next time
- if the named target is bound to credentials, scopes, or membership the
  operator did not realize, surface that as a follow-up rather than burying
  it in the fix

## Anti-Patterns

- treating the operator's name as ground truth and skipping the probe because
  "the command worked yesterday"
- running the operator command first and using its failure as the probe; a
  successful-looking command against the wrong target is silent damage, not
  diagnosis
- swapping a runtime probe for code inspection when the live runtime is
  reachable
- reporting "I ran apply against `prod`" without naming which runtime unit,
  branch SHA, or workspace ID that resolved to
