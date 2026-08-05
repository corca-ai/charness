# Hook Failure Visibility

Use this reference when `setup` detects a Lefthook configuration, or
when a consumer repo asks how hook failures should survive truncated output.
This is guidance for the consumer's hook configuration; Charness does not
invent or rewrite a consumer's lefthook file.

## Capability

After a commit or push hook fails, an operator must be able to identify the
blocking gate and the next evidence path from the hook's final visible message.
When a failure needs diagnostics, the full stdout/stderr must remain available
in a stable log for diagnosis.

## Contract

For every `pre-commit.commands.<id>` and `pre-push.commands.<id>` entry in a
lefthook configuration:

- declare `fail_text` with the hook stage, the blocking command or gate, and the
  next action; use `read <path>` for retained diagnostics, or the complete
  fallback `read output above; do not retry blind` when the failure is fully
  explained by the message itself;
- for every gate whose failure needs diagnostics, including long-running gates,
  provision a stable stage-specific log directory before the hook runs and
  redirect both stdout and stderr to a path such as
  `logs/pre-push-quality-failure.log`; do not use a temporary path that
  disappears when the hook exits;
- never make a truncated operator depend on normal output or on a log path that
  may not exist. If log provisioning can fail, the `fail_text` fallback must
  name the gate and say `read output above; do not retry blind` rather than point
  at a nonexistent file;
- treat the final visible ordering as a consumer acceptance check: confirm that
  the hook runner leaves the `fail_text` pointer visible after its summary, or
  provide an equivalent final pointer to the retained log.

Example:

```yaml
pre-push:
  commands:
    quality:
      run: ./scripts/run-quality.sh --read-only > logs/pre-push-quality-failure.log 2>&1
      fail_text: "PUSH BLOCKED by quality; read logs/pre-push-quality-failure.log before retrying"
```

Provision `logs/` during repo setup or installation before this hook runs; do
not combine directory creation with the gate command, because a directory
creation failure would leave the advertised log path absent. Use the same shape
for `pre-commit`, changing both the stage and the stable log name. A short
command may omit a log only when its `fail_text` is self-contained and does not
send the operator to normal output that truncation can hide.

## Pipeline and filter rule

Do not pipe a state-changing hook or gate through `tail`, `head`, or another
output filter. In a shell pipeline, the exit status can be the final filter's
status; a successful filter can hide a failed gate. Redirect the raw output to
the stable failure log and let `fail_text` identify it. If a consumer has a
documented reason to filter output, it must preserve the gate's non-zero status
with an appropriate `pipefail` policy and still retain the unfiltered log.

## Setup boundary

`setup` may detect a Lefthook configuration and point the operator here. It does
not assume a universal log directory, alter a consumer's gate thresholds, or
claim that Charness has observed the consumer's real failing hook. Husky and
simple-git-hooks have different configuration surfaces; this Lefthook reference
does not claim to configure them. A consumer-facing test or an intentional
failing hook run is the evidence that its configured `fail_text`, final visible
pointer, and log path work end to end.
