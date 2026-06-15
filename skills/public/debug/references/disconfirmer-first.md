# Disconfirmer-First Claims

Use this rung before turning partial evidence into a diagnosis conclusion. It
fires on claim type, not host or repo type.

## Claim Triggers

Before stating one of these as confirmed, name and run the single cheapest check
that would falsify it:

- absence: "nothing does X", "not wired", "doesn't exist", "zero callers"
- attribution: "caused by X", "this came from Y", "scheduled/manual did it"
- liveness: "running", "live", "applied", "delivered", "hook installed"
- frequency: "one-off", "recurring", "first time", "always"

Until that check runs, label the statement `candidate`, `not yet confirmed`, or
`source-inferred`; do not write it as a conclusion.

## Probe Preference

Prefer the probe closest to the claim:

- For liveness, wired/running, applied, or delivered claims, prefer runtime
  state over source inference: process lists, service status, logs, ledgers,
  host settings, generated state files, or provider state. Source code proves
  "could it"; runtime state proves "does it".
- For absence claims, search the source likely to contradict the claim before
  broadening the conclusion: full repo text, generated mirrors, installed
  surfaces, scheduler/service state, or persisted ledgers.
- For attribution claims, look for a timestamp, actor, command, event source, or
  provenance record that would make the plausible cause impossible.
- For frequency claims, inspect the longest cheap time series available before
  calling a recent-window symptom one-off or recurring.

## Output

Record the claim and its falsifier in the debug artifact:

- `Claim type:` absence | attribution | liveness | frequency
- `Candidate claim:`
- `Cheapest falsifier:`
- `Result: confirmed | disconfirmed | still-candidate`

If the falsifier is unavailable, say why and keep the claim candidate. Do not
promote a source-only inference to runtime truth just because the runtime probe
was inconvenient.

## Over-Reach Check

This rung does not require exhaustive proof before every sentence. It applies
when the claim would steer the diagnosis, closeout, or next action. If a cheap
falsifier exists and would change the decision, run it before asserting the
claim.
