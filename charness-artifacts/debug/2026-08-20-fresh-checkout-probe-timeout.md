# Fresh Checkout Probe Timeout Debug Review
Date: 2026-08-20

## Problem

The release planner's declared fresh-checkout proof did not establish a verdict.
`python3 skills/public/release/scripts/check_fresh_checkout_probes.py --repo-root . --run-probes --detail`
returned exit 1 with exactly `release fresh checkout probes timed out after 10s`.

## Correct Behavior

Given a clean release candidate and the five declared fresh-checkout probes, the
checker should run the temporary checkout probes to completion, attribute any
failure to the exact probe and command, and emit an established pass/fail result.
A timeout must identify the timed-out child and preserve enough state to rerun it;
it must not be treated as a successful fresh-checkout proof.

## Observed Facts

- `current_release.py` reported clean version surfaces at 6.2.0 and `git_status: []`.
- The release plan declared these probes: `./charness --help`,
  `./charness goal check --help`, `python3 scripts/doctor.py --repo-root .
  --skip-release-probe`, `python3 scripts/closeout_bundle.py --help`, and
  `python3 scripts/validate_retro_handoff_wiring.py --help`.
- The checker emitted only a wrapper-level 10-second timeout; no child probe,
  clone path, or process diagnostic was rendered.
- Real-host proof returned `evaluation_scope: empty`, which is not evidence that
  release-time host proof is unnecessary; no changed range was supplied.
- The timeout was observed before any release mutation or external side effect.

## Reproduction

- Default invocation on clean HEAD `b744181a5` exits 1 after the exact wrapper
  message `release fresh checkout probes timed out after 10s`.
- The same command with `CHARNESS_SCRIPT_TIMEOUT_SECONDS=420` exits 0 and records
  all five declared probes with return code 0. This changes only the outer
  runtime budget, falsifying the theory that one child probe is intrinsically
  failing.
- Source inspection binds the two timers: `_run` gives git clone 120 seconds and
  `_run_shell` gives each declared probe 300 seconds, while `main` calls
  `arm_cli_timeout` without an override and inherits the global 10-second CLI
  default.

## Candidate Causes

- Confirmed control-flow cause: the checker applies the global 10-second process
  alarm to a workflow whose clone and child commands have independent, longer
  bounds.
- Falsified primary child cause: the 420-second override completed the same clone
  and all five probes with zero return codes.
- Remaining operational risk: a future adapter may declare many probes, so a
  fixed aggregate timeout would recreate the mismatch unless the checker relies
  on the bounded child operations or computes a total from the declared set.

## Hypothesis

Confirmed: diagnostic collapse occurred at the release proof boundary because the
wrapper's default process alarm preempted its own bounded operations. The
different-channel falsifier is the successful 420-second run: the child result
packet contains five completed probes, all with return code 0. No blind fixed
timeout increase is justified; the producer must not impose a shorter default
than the child-operation contract.
disconfirmer: run the exact checker with the 420-second outer override and inspect
all five probe result return codes; a child-specific nonzero result would refute
the wrapper-only attribution.

## Verification

- confirmed — default command failed at the outer 10-second alarm.
- confirmed — `CHARNESS_SCRIPT_TIMEOUT_SECONDS=420` completed the same fresh
  checkout and all five declared probes with return code 0.
- confirmed — source inspection shows the 10-second alarm is inherited at
  `main`, while clone/probe subprocesses have 120/300-second bounds.
- pending — implement the producer-side timeout contract, mirror it, add a
  regression that observes the default passed to `arm_cli_timeout`, and rerun
  the default fresh-checkout proof.

## Root Cause

`check_fresh_checkout_probes.py:217` calls `SKILL_RUNTIME.arm_cli_timeout` with no
`default_seconds`, so `scripts/script_timeout.py` arms the repository-wide
10-second default. That alarm covers clone setup plus five sequential probe
commands. It fires before `_run`'s 120-second clone bound or `_run_shell`'s
300-second child bound can attribute a result. The global default is therefore
not a valid budget for this producer; it is a shared helper contract accidentally
applied across unlike workflows.

## Invariant Proof

- Invariant: a release fresh-checkout claim is established only by an attributed,
  completed probe set, never by a generic timeout exit.
- Producer Proof: source inspection plus the 420-second override bind the generic
  timeout to the producer; the override's established payload has five successful
  probe results.
- Final-Consumer Proof: pending; release planner must consume the established
  packet after the producer-side repair rather than the wrapper timeout.
- Interface-Shape Sibling Scan: `current_release.py` intentionally does not run
  probes; `publish_release_cli.py` invokes this checker and therefore inherits
  the defect. The shared timeout helper remains valid for short scripts; this
  workflow needs an explicit producer contract.
- Non-Claims: no release publication, tag, hosted readback, install refresh, or
  issue closeout is claimed.

## Detection Gap

- Fresh-checkout release gate | reused a global 10-second wrapper budget despite
  declaring 120/300-second child bounds | add a regression pinning the producer's
  explicit timeout policy and run the real default checker in a fresh checkout.

## Sibling Search

- Mental model: a release probe timeout is a single boolean failure rather than a
  producer-to-consumer diagnostic packet.
- timeout/reporting seam: `check_fresh_checkout_probes.py` →
  `scripts/script_timeout.py` | decision: repair producer-specific budget, do not
  widen the global default | proof: source binding plus override payload.
- cross-file: `publish_release_cli.py` is the release consumer; its proof remains
  unestablished until the default producer invocation passes.

## Seam Risk

- Interrupt ID: fresh-checkout-release-proof-timeout-2026-08-20
- Risk Class: host-disproves-local
- Seam: local release planner → temporary checkout → child CLI/doctor probes.
- Disproving Observation: the exact default failure and successful 420-second
  override differ only on the outer timer, confirming the seam.
- What Local Reasoning Cannot Prove: cold fresh-checkout startup and installed or
  host-dependent behavior.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-20-fresh-checkout-probe-timeout.md

## Prevention

Keep the exact child-level evidence and add the smallest structural prevention at
the producer/consumer boundary: the fresh-checkout producer must opt out of the
10-second shared default because every subprocess it owns is already bounded.
Keep timeout failures blocked and attributed; never report an unestablished
fresh-checkout packet as green.
