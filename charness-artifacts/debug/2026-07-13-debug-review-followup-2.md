# Issue Resolve Invalid-Target Preflight Ordering Debug
Date: 2026-07-13

## Problem

`issue_tool.py plan --intent resolve --target ...` is an invalid invocation, but
it probes GitHub authentication before returning the deterministic usage error.
The standing regression therefore pays variable remote latency and can fail at
the wrong boundary.

## Correct Behavior

Given a valid issue adapter and `intent=resolve` with forbidden `--target`, when
the plan command runs, then it returns the existing rc=2 JSON usage error before
backend resolution or preflight. Invalid-adapter errors retain precedence.

## Observed Facts

- The standing test took 5.48s in one suite run and is the only neighboring plan
  test that omits the fake-GitHub environment.
- `command_plan` loads the adapter, resolves the backend, and builds its
  preflight payload before checking `args.target`.
- Host CLI proof took about 0.48s outside pytest; immediate fake GitHub took
  0.07s; a fake two-second auth probe made the same invalid command take 2.10s.
- The preflight result is discarded on this usage-error path, so the remote
  observation cannot affect the intended rc/payload.

## Reproduction

- Run `python3 skills/public/issue/scripts/issue_tool.py plan --repo-root
  <fixture> --intent resolve --target corca-ai/other -- 42` with a fake `gh`
  whose `auth status` sleeps two seconds. It returns rc=2 only after 2.10s.

## Candidate Causes

- `command_plan` orders backend readiness before local argument validation.
- The test accidentally uses the host GitHub binary because it omits the shared
  fake-GitHub fixture.
- Backend preflight owns a required normalization side effect needed before the
  target check.

## Hypothesis

- Falsifiable claim: the target misuse guard is below the only remote preflight,
  and moving it after invalid-adapter handling but before `resolve_backend`
  preserves the exact rc/payload while preventing any backend call.
- disconfirmer: find target-error output derived from preflight or observe a
  required backend call in an in-process regression.

## Verification

- resolved — source order and fake-GitHub timing confirmed the diagnosis. After
  repair, 48 focused issue tests passed; the in-process regression proves exact
  rc/payload while backend resolution, preflight, and invocation sentinels would
  fail if called. The public subprocess test uses fake GitHub, and source/plugin
  parity, ruff, pycompile, and packaging validators passed.

## Root Cause

Local usage validation was treated as downstream of backend readiness. That
mental model makes a malformed command depend on remote authentication even
though its outcome is fully determined by parsed arguments and adapter validity.

## Invariant Proof

- Invariant: once a valid adapter plus forbidden resolve target determines a
  usage error, the issue-plan consumer must emit that error before any backend
  or provider preflight can run.
- Producer Proof: parsed `intent=resolve` and non-empty `target` are sufficient
  local inputs.
- Final-Consumer Proof: the in-process consumer returned exact rc=2/payload with
  three no-call sentinels; the subprocess consumer returned rc=2 through the
  public CLI path under an immediate fake GitHub environment.
- Interface-Shape Sibling Scan: inspect other issue-plan local usage guards for
  readiness-before-validation ordering.
- Non-Claims: no claim that all valid issue-plan paths can skip backend
  preflight; only this deterministic invalid-input path is in scope.

## Detection Gap

- existing subprocess regression | asserted final rc/text but not that remote
  preflight was skipped | add an in-process no-backend-call assertion and make
  the subprocess test host-independent.

## Sibling Search

- Mental model: backend readiness was considered prerequisite to deciding a
  local parse/usage error.
- same layer: other `issue_plan.command_plan` local guards | decision: same
  class, diagnostic-only for this slice | proof: static scan found no sibling
  local misuse guard below the same backend boundary.
- abstraction up: issue CLI parse-to-provider ordering | decision: same class,
  diagnostic-only for this slice | proof: local payload and timing proof.
- specialization down: invalid-adapter precedence | decision: intentional
  plain-text or non-rendering boundary | proof: existing contract requires
  adapter repair before usage classification.
- cross-file: `skills/public/issue/scripts/issue_tool.py` dispatch and
  `tests/quality_gates/test_issue_skill.py` final CLI consumer.

## Seam Risk

- Interrupt ID: issue-invalid-target-preflight-order
- Risk Class: none
- Seam: parsed CLI arguments to GitHub backend preflight
- Disproving Observation: a fake slow GitHub binary delays a deterministic
  local error by the fake delay.
- What Local Reasoning Cannot Prove: provider latency outside the bounded fake;
  provider behavior is irrelevant once the call is correctly absent.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Validate deterministic local misuse after adapter-shape validity but before
backend readiness. Prove ordering with a backend that fails loudly if invoked;
keep one subprocess assertion for the public rc/JSON contract.
